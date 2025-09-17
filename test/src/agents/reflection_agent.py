from langchain_core.messages import AIMessage  # 导入消息类
from .session_history import get_session_history  # 导入会话历史相关方法
from .agent_base import AgentBase
from utils.logger import LOG

class ReflectionAgent(AgentBase):
    """
    对话代理类，负责处理与用户的对话。
    """
    def __init__(self, session_id=None):
        super().__init__(
            name="reflection",
            prompt_file="prompts/reflection_prompt.txt",
            session_id=session_id
        )
    
    def provide_feedback(self,article_content):
        """
        提供文章评审反馈
        参数:
            article_content (str): 待评审的文章内容
        返回:
            str: 生成的评审意见
        """
        return self.chat_with_history(article_content,self.session_id,)

    def stream(self, messages: list):
        return self.stream_with_history(messages, self.session_id)  
