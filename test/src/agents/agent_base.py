import json
from abc import ABC, abstractmethod

from langchain_ollama.chat_models import ChatOllama  # 导入 ChatOllama 模型
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # 导入提示模板相关类
from langchain_core.messages import HumanMessage  # 导入消息类
from langchain_core.runnables.history import RunnableWithMessageHistory  # 导入带有消息历史的可运行类

from .session_history import get_session_history  # 导入会话历史相关方法
from utils.logger import LOG  # 导入日志工具

class AgentBase(ABC):
    """
    抽象基类，提供代理的共有功能。
    """
    def __init__(self, name, prompt_file,  session_id=None):
        self.name = name
        self.prompt_file = prompt_file
        self.session_id = session_id if session_id else self.name
        self.prompt = self.load_prompt()
        self.create_chatbot()

    def load_prompt(self):
        """
        从文件加载系统提示语。
        """
        try:
            with open(self.prompt_file, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到提示文件 {self.prompt_file}!")

    def create_chatbot(self):
        """
        初始化聊天机器人，包括系统提示和消息历史记录。
        """
        # 创建聊天提示模板，包括系统提示和消息占位符
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt),  # 系统提示部分
            MessagesPlaceholder(variable_name="messages"),  # 消息占位符
        ])

        # 初始化 ChatOllama 模型，配置参数
        self.chatbot = system_prompt | ChatOllama(
            model="qwen3:latest",  # 使用的模型名称
            max_tokens=8192,  # 最大生成的 token 数
            temperature=0.8,  # 随机性配置
        )

        # 将聊天机器人与消息历史记录关联
        self.chatbot_with_history = RunnableWithMessageHistory(self.chatbot, get_session_history)

    def chat_with_history(self, user_input, session_id=None):
        """
        处理用户输入，生成包含聊天历史的回复。
        参数:
            user_input (str): 用户输入的消息
            session_id (str, optional): 会话的唯一标识符

        返回:
            str: AI 生成的回复
        """
        if session_id is None:
            session_id = self.session_id
        

        response = self.chatbot_with_history.invoke(
            [HumanMessage(content=user_input)],  # 将用户输入封装为 HumanMessage
            {"configurable": {"session_id": session_id}, # 传入配置，包括会话ID
             "hide_chain_of_thought": True  # 强制隐藏思维链
            }, 
        )

        LOG.debug(f"[ChatBot][{self.name}] {response.content}")  # 记录调试日志
        return response.content  # 返回生成的回复内容


    def stream_with_history(self, messages: list, session_id: str = None):
        """
        以流式方式处理用户输入，返回生成器形式的逐步输出。
        """

        if session_id is None:
            session_id = self.session_id

        # 生成器返回逐块结果
        stream = self.chatbot_with_history.stream(
            messages,
            {
                "configurable": {"session_id": session_id},
                "hide_chain_of_thought": True
            }
        )

        for chunk in stream:
            yield chunk


    def stream_response_text(self, messages: list, session_id: str = None) -> str:
        """
        调用 stream 接口，并返回拼接后的完整文本内容。
        """
        if session_id is None:
            session_id = self.session_id

        output = ""
        for chunk in self.stream_with_history(messages, session_id):
            output += chunk.content
        return output


    def stream_to_markdown(self, messages: list, title: str, session_id: str = None) -> str:
        """
        调用 stream 接口并包装为 Markdown 结果块。
        """
        text = self.stream_response_text(messages, session_id)
        return f"### {title}\n{text.strip()}"

    def multi_round_response_text(
        self,
        user_input: str,
        reflection_agent,
        max_rounds: int = 3
        ) -> str:
        """
        多轮生成 + 反思（文本），作为 stream_response_text 的多轮版本。
        """

        current_input = user_input
        all_output = ""

        for i in range(1, max_rounds + 1):
            # 写作生成
            article = self.stream_response_text([HumanMessage(content=current_input)])

            # 反思反馈
            reflection = reflection_agent.stream_response_text([
                HumanMessage(content=user_input),
                HumanMessage(content=article)
            ])

            # 收集内容
            all_output += f"[第{i}轮 写作]\n{article.strip()}\n\n[第{i}轮 反思]\n{reflection.strip()}\n\n"

            # 生成下一轮输入
            current_input = f"{user_input}\n\nAI 改进稿：\n{article}\n\n请根据上面的反思优化文章。"

        return all_output.strip()


    def multi_round_to_markdown(
        self,
        user_input: str,
        reflection_agent,
        max_rounds: int = 3
        ) -> str:
        """
        多轮生成 + 反思（Markdown），作为 stream_to_markdown 的多轮版本。
        """

        current_input = user_input
        all_md = ""

        for i in range(1, max_rounds + 1):
            # 写作 Markdown
            article = self.stream_response_text([HumanMessage(content=current_input)])
            article_md = f"### 第{i}轮 ✍️ 写作生成\n{article.strip()}"

            # 反思 Markdown
            reflection = reflection_agent.stream_response_text([
                HumanMessage(content=user_input),
                HumanMessage(content=article)
            ])
            reflection_md = f"### 第{i}轮 💬 反思点评\n{reflection.strip()}"

            # 合并
            all_md += f"{article_md}\n\n{reflection_md}\n\n"

            # 生成下一轮输入
            current_input = f"{user_input}\n\nAI 改进稿：\n{article}\n\n请根据上面的反思优化文章。"

        return all_md.strip()
