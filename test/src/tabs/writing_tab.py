import os
import gradio as gr
from tempfile import NamedTemporaryFile
from langchain_core.messages import HumanMessage
from agents.writing_agent import WritingAgent
from agents.reflection_agent import ReflectionAgent
from utils.logger import LOG

# 初始化写作与反思 Agent
writing_agent = WritingAgent()
reflection_agent = ReflectionAgent()

# ==== 核心工具函数 ====
def get_topic_with_difficulty(difficulty: str) -> str:
    """根据难度生成作文题目"""
    prompt = f"请生成一个{difficulty}难度的英语作文题目，只返回题目文本，不要额外内容。"
    topic = writing_agent.stream_response_text([HumanMessage(content=prompt)])
    return topic.strip()

def reflect_with_difficulty(article: str, difficulty: str) -> str:
    """结合难度进行作文反思点评"""
    reflection_prompt = (
        f"请基于{difficulty}难度标准，从4个维度点评以下作文：\n"
        f"1. 评分（内容契合30%，结构完整50%，语法20%）\n"
        f"2. 优点\n"
        f"3. 不足\n"
        f"4. 整体建议\n\n作文内容：\n{article}"
    )
    return reflection_agent.stream_response_text([HumanMessage(content=reflection_prompt)])

def generate_suggestion_with_difficulty(topic: str, difficulty: str) -> str:
    """结合难度生成写作建议"""
    suggestion_prompt = (
        f"请针对以下{difficulty}难度的英文作文题目，给出对应难度的详细写作建议，"
        f"包括写作要点、结构、适配词汇和语法建议。\n\n题目：{topic}"
    )
    return reflection_agent.stream_response_text([HumanMessage(content=suggestion_prompt)])


# ==== 模式一：Tiro出题模式核心逻辑 ====
def mode1_process(topic: str, user_essay: str, difficulty: str, rounds: int) -> tuple:
    """模式一处理流程"""
    all_output = f"## 📌 Tiro出题（{difficulty}难度）\n{topic}\n\n"
    
    # 检查用户作文
    if not user_essay.strip():
        all_output += "### ⚠️ 提示：未检测到用户作文，仅生成写作建议\n"
        suggestion = generate_suggestion_with_difficulty(topic, difficulty)
        all_output += f"### 💡 写作建议（{difficulty}适配）\n{suggestion}\n"
    else:
        all_output += f"### 📝 用户提交作文\n{user_essay}\n\n"
        current_essay = user_essay
        
        # 多轮精进流程
        for i in range(1, rounds + 1):
            # 反思智能体评分评价
            reflection = reflect_with_difficulty(current_essay, difficulty)
            all_output += f"### 第{i}轮 💬 反思点评（{difficulty}标准）\n{reflection}\n\n"
            
            # 写作智能体生成范文
            write_prompt = (
                f"基于以下{difficulty}难度题目和反思建议，生成一篇范文：\n"
                f"题目：{topic}\n"
                f"反思建议：{reflection}\n"
                f"要求符合{difficulty}水平，内容契合题目"
            )
            model_essay = writing_agent.stream_response_text([HumanMessage(content=write_prompt)])
            all_output += f"### 第{i}轮 ✍️ AI 范文\n{model_essay}\n\n"
            
            # 更新当前作文为范文（用于下一轮精进）
            current_essay = model_essay
    
    # 生成下载文件
    with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.txt') as tmp_file:
        tmp_file.write(all_output)
        download_path = tmp_file.name
    
    return all_output, download_path


# ==== 模式二：用户出题模式核心逻辑 ====
def mode2_process(user_topic: str, difficulty: str, rounds: int) -> tuple:
    """模式二处理流程"""
    if not user_topic.strip():
        return "⚠️ 请先输入作文题目", None
    
    all_output = f"## 📌 用户自定义题目（{difficulty}难度）\n{user_topic}\n\n"
    
    # 生成对应难度的写作建议
    suggestion = generate_suggestion_with_difficulty(user_topic, difficulty)
    all_output += f"### 💡 写作建议（{difficulty}适配）\n{suggestion}\n\n"
    
    # 初始写作
    initial_prompt = (
        f"根据以下{difficulty}难度题目和写作建议，生成初始作文：\n"
        f"题目：{user_topic}\n"
        f"建议：{suggestion}"
    )
    current_essay = writing_agent.stream_response_text([HumanMessage(content=initial_prompt)])
    all_output += f"### 初始 ✍️ AI 作文\n{current_essay}\n\n"
    
    # 多轮精进流程
    for i in range(1, rounds + 1):
        # 反思智能体评价
        reflection = reflect_with_difficulty(current_essay, difficulty)
        all_output += f"### 第{i}轮 💬 反思点评（{difficulty}标准）\n{reflection}\n\n"
        
        # 写作智能体重写优化
        rewrite_prompt = (
            f"基于以下{difficulty}难度题目和反思建议，优化作文：\n"
            f"题目：{user_topic}\n"
            f"当前作文：{current_essay}\n"
            f"反思建议：{reflection}\n"
            f"要求符合{difficulty}水平，针对性优化"
        )
        current_essay = writing_agent.stream_response_text([HumanMessage(content=rewrite_prompt)])
        all_output += f"### 第{i}轮 ✍️ 优化作文\n{current_essay}\n\n"
    
    # 生成下载文件
    with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.txt') as tmp_file:
        tmp_file.write(all_output)
        download_path = tmp_file.name
    
    return all_output, download_path


# ==== 界面封装：模式一（Tiro出题） ====
def create_mode1_tab():
    with gr.Tab("模式一：Tiro出题"):
        gr.Markdown("## 📌 Tiro出题模式")
        gr.Markdown("1. 选择难度（初中/高中/大学）\n2. 生成题目并提交你的作文\n3. 选择精进轮次获取AI点评与范文")
        
        # 状态变量
        difficulty_state = gr.State("初中")
        
        # 界面布局
        with gr.Row():
            # 左侧输入区
            with gr.Column(scale=2):
                # 难度选择
                gr.Markdown("### 选择难度")
                difficulty_buttons = gr.Radio(
                    ["初中", "高中", "大学"], 
                    value="初中", 
                    label="难度等级",
                    interactive=True
                )
                
                # 题目相关
                topic_display = gr.Textbox(lines=2, label="当前题目", interactive=False)
                gen_topic_btn = gr.Button("🧠 Tiro生成题目")
                change_topic_btn = gr.Button("🔁 更换题目")
                
                # 用户输入
                user_essay = gr.Textbox(lines=6, label="你的英语作文", placeholder="请根据题目写作文...")
                
                # 轮次设置
                rounds_slider = gr.Slider(
                    minimum=1, maximum=5, value=2, step=1, 
                    label="AI精进轮次", info="1-5轮"
                )
                
                # 操作按钮
                start_btn = gr.Button("🚀 开始精进")
                export_btn = gr.Button("📄 导出结果", visible=False)
            
            # 右侧输出区
            with gr.Column(scale=3):
                output_display = gr.Markdown(label="处理结果")
                export_file = gr.File(label="下载链接", visible=False)
        
        # 事件绑定：难度选择
        def set_difficulty(diff):
            difficulty_state.value = diff
            return f"已选择：{diff}难度"
        
        difficulty_buttons.change(
            fn=set_difficulty,
            inputs=difficulty_buttons,
            outputs=gr.Textbox(label="状态提示", visible=False)  # 隐藏状态提示
        )
        
        # 事件绑定：生成/更换题目
        def generate_topic(diff):
            return get_topic_with_difficulty(diff)
        
        gen_topic_btn.click(
            fn=generate_topic,
            inputs=difficulty_buttons,
            outputs=topic_display
        )
        
        change_topic_btn.click(
            fn=generate_topic,
            inputs=difficulty_buttons,
            outputs=topic_display
        )
        
        # 事件绑定：开始精进
        def start_mode1(topic, essay, diff, rounds):
            if not topic.strip():
                return "⚠️ 请先生成题目", None
            return mode1_process(topic, essay, diff, rounds)
        
        start_btn.click(
            fn=start_mode1,
            inputs=[topic_display, user_essay, difficulty_buttons, rounds_slider],
            outputs=[output_display, export_file]
        ).then(
            fn=lambda: (gr.update(visible=True), gr.update(visible=True)),
            outputs=[export_btn, export_file]
        )
        
        # 事件绑定：导出结果
        export_btn.click(
            fn=lambda x: x,
            inputs=export_file,
            outputs=export_file
        )


# ==== 界面封装：模式二（用户出题） ====
def create_mode2_tab():
    with gr.Tab("模式二：用户出题"):
        gr.Markdown("## 📌 用户出题模式")
        gr.Markdown("1. 输入你的题目并选择难度\n2. 选择精进轮次\n3. 获取AI写作、点评与优化")
        
        # 界面布局
        with gr.Row():
            # 左侧输入区
            with gr.Column(scale=2):
                # 难度选择
                gr.Markdown("### 选择难度")
                difficulty_buttons = gr.Radio(
                    ["初中", "高中", "大学"], 
                    value="初中", 
                    label="难度等级",
                    interactive=True
                )
                
                # 题目相关
                user_topic_input = gr.Textbox(lines=2, label="你的题目", placeholder="请输入作文题目...")
                confirm_topic_btn = gr.Button("✅ 确认题目")
                reset_topic_btn = gr.Button("🔄 重置题目")
                
                # 轮次设置
                rounds_slider = gr.Slider(
                    minimum=1, maximum=5, value=2, step=1, 
                    label="AI精进轮次", info="1-5轮"
                )
                
                # 操作按钮
                start_btn = gr.Button("🚀 开始处理")
                export_btn = gr.Button("📄 导出结果", visible=False)
            
            # 右侧输出区
            with gr.Column(scale=3):
                output_display = gr.Markdown(label="处理结果")
                topic_confirm_display = gr.Textbox(label="已确认题目", interactive=False, visible=False)
                export_file = gr.File(label="下载链接", visible=False)
        
        # 事件绑定：确认/重置题目
        def confirm_topic(topic):
            if not topic.strip():
                return "⚠️ 题目不能为空", gr.update(visible=False)
            return f"已确认：{topic}", gr.update(visible=True, value=topic)
        
        confirm_topic_btn.click(
            fn=confirm_topic,
            inputs=user_topic_input,
            outputs=[gr.Textbox(label="提示", visible=False), topic_confirm_display]
        )
        
        reset_topic_btn.click(
            fn=lambda: ("", gr.update(visible=False)),
            outputs=[user_topic_input, topic_confirm_display]
        )
        
        # 事件绑定：开始处理
        def start_mode2(topic, diff, rounds):
            if not topic.strip():
                return "⚠️ 请先确认题目", None
            return mode2_process(topic, diff, rounds)
        
        start_btn.click(
            fn=start_mode2,
            inputs=[topic_confirm_display, difficulty_buttons, rounds_slider],
            outputs=[output_display, export_file]
        ).then(
            fn=lambda: (gr.update(visible=True), gr.update(visible=True)),
            outputs=[export_btn, export_file]
        )
        
        # 事件绑定：导出结果
        export_btn.click(
            fn=lambda x: x,
            inputs=export_file,
            outputs=export_file
        )




