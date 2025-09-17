import gradio as gr
from tabs.conversation_tab import create_conversation_tab
from tabs.vocab_tab import create_vocab_tab
from tabs.writing_tab import create_mode1_tab,create_mode2_tab
from utils.logger import LOG

def main():
    with gr.Blocks(title="Oral English Coach 英语私教") as language_mentor_app:
        create_conversation_tab()
        create_vocab_tab()
        create_mode1_tab()
        create_mode2_tab()
    
    # 启动应用
    language_mentor_app.launch(share=True, server_name="0.0.0.0")

if __name__ == "__main__":
    main()


