from langchain_core.messages import AIMessage  # 导入消息类

from .session_history import get_session_history  # 导入会话历史相关方法
from .agent_base import AgentBase
from utils.logger import LOG

class WritingAgent(AgentBase):
    """
    对话代理类，负责处理与用户的对话。
    """
    def __init__(self, session_id=None):
        super().__init__(
            name="writing",
            prompt_file="prompts/writing_prompt.txt",
            session_id=session_id
        )

    def generate_response(self,user_input):
        """
        生成写作建议响应
        参数：
            user_input (str): 用户输入内容
        返回:
            str: 生成的写作建议
        """
        return self.chat_with_history(user_input,self.session_id)

    def stream(self, messages: list):
        return self.stream_with_history(messages, self.session_id)  
