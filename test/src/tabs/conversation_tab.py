import gradio as gr
from agents.conversation_agent import ConversationAgent
from utils.logger import LOG
from langchain_core.messages import HumanMessage

# 初始化对话代理
conversation_agent = ConversationAgent()

# 全局变量存储场景设定和对话轮数计数
conversation_context = {
    "scenario": None,
    "process": None,
    "rounds": 0,
    "max_rounds": 10
}

def reset_context():
    conversation_context.update({
        "scenario": None,
        "process": None,
        "rounds": 0
    })

def handle_conversation(user_input, chat_history):
    if not conversation_context["scenario"] or not conversation_context["process"]:
        return "Please set both <specific scenario> and <specific process> before starting the conversation."

    conversation_context["rounds"] += 1

    bot_message = conversation_agent.chat_with_history(user_input)
    LOG.info(f"[Conversation ChatBot]: {bot_message}")

    if conversation_context["rounds"] >= conversation_context["max_rounds"]:
        feedback = (
            "\n\n✅ **Feedback:**\n"
            "**English**: Great job reaching the end of the conversation session.\n"
            "**中文**: 太棒了，你完成了本轮对话训练！继续加油！"
        )
        bot_message += feedback

    return bot_message

def create_conversation_tab():
    with gr.Tab("对话"):
        gr.Markdown("## 🎭 场景演绎练习 - Tiro 英语私教")

        with gr.Row():
            scenario_input = gr.Textbox(label="场景 (e.g., Hotel Check-in)")
            process_input = gr.Textbox(label="过程 (e.g., Reservation confirmation)")

        with gr.Row():
            set_button = gr.Button("确定场景")
            reset_button = gr.Button("重置场景")

        status_display = gr.Markdown("**未设定场景，请先设定。**")

        with gr.Row():
            round_slider = gr.Slider(5, 20, value=10, step=1, label="最大对话轮数")
            round_counter = gr.Number(label="当前对话轮数", value=0, interactive=False)

        conversation_chatbot = gr.Chatbot(
            placeholder="<strong>你的英语私教Tiro </strong><br><br>设定场景后开始对话吧，记得用英语哦！",
            height=800,
        )

        user_input_box = gr.Textbox(label="输入你的英文对话")
        send_button = gr.Button("发送")
        round_state = gr.State(0)

        def set_scenario(scenario, process, max_rounds):
            if not scenario or not process:
                return "❗ 请填写完整的场景和过程信息。", 0, []

            conversation_context.update({
                "scenario": scenario,
                "process": process,
                "rounds": 0,
                "max_rounds": max_rounds
            })

            intro_prompt = (
                f"The user has selected the following practice setting:\n"
                f"Scenario: {scenario}\n"
                f"Process: {process}\n"
                f"Please provide a brief bilingual (English and Chinese) overview of this role-play scene, then begin the first sentence of the conversation as Tiro."
            )

            overview = conversation_agent.stream_response_text([
                HumanMessage(content=intro_prompt)
            ])

            LOG.info(f"[Scene Overview & Intro] {overview}")

            return (
                f"✅ **场景设定成功：{scenario} / {process}**",
                0,
                [["Tiro", overview.strip()]]
            )

        def reset_scenario():
            reset_context()
            return "🔄 场景已重置，请重新设定。", 0, []

        def chat_fn(user_input, history, round_val):
            bot_message = handle_conversation(user_input, history)
            history.append([user_input, bot_message])
            round_val = conversation_context["rounds"]
            return history, round_val

        set_button.click(
            set_scenario,
            inputs=[scenario_input, process_input, round_slider],
            outputs=[status_display, round_counter, conversation_chatbot]
        )

        reset_button.click(
            reset_scenario,
            outputs=[status_display, round_counter, conversation_chatbot]
        )

        send_button.click(
            chat_fn,
            inputs=[user_input_box, conversation_chatbot, round_state],
            outputs=[conversation_chatbot, round_counter]
        )
