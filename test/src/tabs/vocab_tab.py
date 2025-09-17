# tabs/vocab_tab.py

import gradio as gr
from agents.vocab_agent import VocabAgent
from utils.logger import LOG

# 初始化词汇代理
vocab_agent = VocabAgent()

def generate_words(word_count):
    """生成指定数量的单词并展示"""
    # 调用代理生成单词（修复原代码参数传递问题）
    response = vocab_agent.generate_vocabulary(word_count)
    return [("生成单词", response)], response  # 第二个返回值用于更新单词展示区

def start_situation_chat(word_display):
    """开始情景对话，保持单词展示区不变"""
    response = vocab_agent.start_situation_chat()
    return [("开始情景对话", response)], word_display  # 不改变单词展示内容

def handle_user_message(user_message, chat_history, current_word_display):
    """处理用户输入，更新聊天记录并标记已使用的单词"""
    if isinstance(user_message, tuple):
        user_message = user_message[0] if user_message else ""
    
    # 获取机器人回复
    bot_response = vocab_agent.chat_with_history(user_message)
    chat_history.append((user_message, bot_response))
    
    # 检查用户输入中是否包含当前单词，动态更新单词展示区
    current_words = vocab_agent.current_words
    word_lines = current_word_display.split('\n')  # 按行分割单词展示内容
    updated_lines = []
    
    for line in word_lines:
        line_strip = line.strip()
        if not line_strip:
            updated_lines.append(line)
            continue
        
        # 提取单词（基于生成格式：[单词] - [音标] - ...）
        word = line_strip.split(' - ')[0] if ' - ' in line_strip else line_strip
        
        # 检查该单词是否在当前学习列表中
        if any(word == target_word for target_word in current_words):
            # 不区分大小写检查用户是否使用了该单词
            if word.lower() in user_message.lower():
                # 避免重复添加勾选符号
                updated_line = line + " ✓" if '✓' not in line_strip else line
            else:
                updated_line = line
        else:
            updated_line = line
        
        updated_lines.append(updated_line)
    
    # 合并更新后的单词展示内容
    updated_word_display = '\n'.join(updated_lines)
    return chat_history, updated_word_display

def clear_chat():
    """清空聊天记录，重置单词展示提示"""
    return [], "请生成单词以展示"

def reset_session():
    """重置会话状态（清空单词和聊天记录）"""
    vocab_agent.restart_session()
    return [], "请生成单词以展示"

def create_vocab_tab():
    """创建词汇学习标签页"""
    with gr.Tab("单词"):
        gr.Markdown("## 智能单词学习助手")
        
        with gr.Row():
            # 单词数量选择器
            word_count_slider = gr.Slider(
                minimum=3,
                maximum=10,
                value=5,
                step=1,
                label="选择单词数量",
                interactive=True
            )
            # 生成单词按钮
            generate_btn = gr.Button("生成单词", variant="primary")
            # 开始情景对话按钮
            chat_btn = gr.Button("开始情景对话", variant="secondary")
            # 重置会话按钮
            reset_btn = gr.Button("重置会话", variant="destructive")
        
        # 单词展示区域（替代原操作状态区域）
        word_display = gr.Textbox(
            label="单词展示",
            value="请生成单词以展示",
            interactive=False,
            lines=10  # 增加行数，方便展示多个单词
        )
        
        # 聊天历史展示区
        chatbot = gr.Chatbot(
            placeholder="生成单词后，点击开始情景对话按钮开始练习...",
            height=400
        )
        
        with gr.Row():
            user_input = gr.Textbox(label="输入消息", placeholder="请输入你的回复...")
            submit_btn = gr.Button("发送", variant="primary")
            clear_btn = gr.Button("清空聊天", variant="secondary")
        
        # 绑定按钮事件
        generate_btn.click(
            fn=generate_words,
            inputs=[word_count_slider],
            outputs=[chatbot, word_display]  # 生成后同时更新聊天记录和单词展示
        )
        
        chat_btn.click(
            fn=start_situation_chat,
            inputs=[word_display],
            outputs=[chatbot, word_display]  # 开始对话时保持单词展示不变
        )
        
        submit_btn.click(
            fn=handle_user_message,
            inputs=[user_input, chatbot, word_display],  # 传入当前单词展示内容
            outputs=[chatbot, word_display]  # 同时更新聊天记录和单词展示
        )
        
        clear_btn.click(
            fn=clear_chat,
            inputs=[],
            outputs=[chatbot, word_display]  # 清空聊天和单词展示提示
        )
        
        reset_btn.click(
            fn=reset_session,
            inputs=[],
            outputs=[chatbot, word_display]  # 重置会话后清空内容
        )

