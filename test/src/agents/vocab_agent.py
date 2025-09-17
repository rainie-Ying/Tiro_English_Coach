from langchain_core.messages import HumanMessage
from .session_history import get_session_history  # 只导入已存在的get_session_history
from .agent_base import AgentBase
from utils.logger import LOG

class VocabAgent(AgentBase):
    """词汇学习代理类，负责生成单词和管理情景对话"""
    
    def __init__(self, session_id=None):
        super().__init__(
            name="vocab_study",
            prompt_file="prompts/vocab_study_prompt.txt",
            session_id=session_id
        )
        self.word_count = 5  # 默认生成5个单词
        self.current_words = []  # 当前生成的单词列表
        self.words_generated = False  # 标记是否已生成单词
        self.in_conversation = False  # 标记是否在情景对话中

    def set_word_count(self, count):
        """设置要生成的单词数量"""
        self.word_count = count
        LOG.info(f"已设置单词数量: {self.word_count}")

    def generate_vocabulary(self, count=None):
        """生成指定数量的英语单词"""
        if count is not None:
            self.word_count = count
        LOG.info(f"开始生成{self.word_count}个单词")
        
        # 构建生成单词的提示
        prompt = (f"请生成{self.word_count}个常用英语单词，每个单词应包含以下信息：\n"
                 f"1. 单词拼写\n"
                 f"2. 音标\n"
                 f"3. 词性\n"
                 f"4. 中文释义\n"
                 f"5. 英文例句\n"
                 f"6. 例句中文翻译\n\n"
                 f"请使用以下格式输出：\n"
                 f"[单词1] - [音标] - 词性 - 中文释义 - 例句：英文例句 - 中文翻译\n"
                 f"[单词2] - [音标] - 词性 - 中文释义 - 例句：英文例句 - 中文翻译\n"
                 f"...")
        
        response = self.chat_with_history(prompt)
        
        # 提取单词列表（优化格式匹配）
        self.current_words = []
        for line in response.split('\n'):
            line = line.strip()
            if not line or ' - ' not in line:
                continue
            word = line.split(' - ')[0].strip()
            self.current_words.append(word)
        
        self.words_generated = len(self.current_words) > 0
        LOG.info(f"成功生成{len(self.current_words)}个单词")
        
        return response

    def start_situation_chat(self):
        """开始情景对话"""
        if not self.words_generated:
            return "--请先生成单词，在学会新单词后再进行对话！--"
            
        self.in_conversation = True
        
        # 构建情景对话提示（使用全部生成的单词）
        prompt = (f"我们将进行一个情景对话练习。请设计一个日常生活场景，例如在餐厅点餐、在商店购物等，"
                 f"并自然地融入以下单词：{', '.join(self.current_words)}。\n\n"
                 f"请首先描述场景，然后以对话的形式发起第一句话。")
        
        return self.chat_with_history(prompt)

    def evaluate_conversation(self):
        """评估对话中单词使用情况并给出评分（保留方法备用）"""
        if not self.in_conversation:
            return "请先开始情景对话！"
            
        # 获取对话历史
        history = get_session_history(self.session_id)
        user_messages = [msg.content for msg in history.messages if isinstance(msg, HumanMessage)]
        conversation_text = " ".join(user_messages).lower()
        
        # 检查每个单词的使用情况
        used_words = []
        unused_words = []
        for word in self.current_words:
            if word.lower() in conversation_text:
                used_words.append(word)
            else:
                unused_words.append(word)
        
        # 计算评分
        score = len(used_words) / len(self.current_words) * 100 if self.current_words else 0
        
        # 构建反馈信息
        feedback = f"### 对话评分：{score:.1f}分\n\n"
        feedback += f"✅ 你使用了以下单词：{', '.join(used_words)}\n\n"
        if unused_words:
            feedback += f"❌ 你还没有使用这些单词：{', '.join(unused_words)}\n\n"
        feedback += "💡 建议：尝试在后续对话中使用未掌握的单词，或者重新开始对话练习！"
        
        self.in_conversation = False  # 结束对话状态
        return feedback

    def chat_with_history(self, user_input, session_id=None):
        """处理用户输入并生成回复"""
        if not isinstance(user_input, str):
            user_input = str(user_input)
        
        if self.in_conversation and not self.words_generated:
            return "--请先生成单词，在学会新单词后再进行对话！--"
        
        return super().chat_with_history(user_input, session_id or self.session_id)

    def restart_session(self, session_id=None):
        """重置会话状态（不依赖clear_session_history）"""
        # 重置会话ID（如果传入新ID）
        if session_id is not None:
            self.session_id = session_id
        
        # 直接清空父类或历史存储的消息（通过获取历史后清空）
        history = get_session_history(self.session_id)
        if hasattr(history, 'clear'):  # 检查历史对象是否有clear方法
            history.clear()
        else:  # 兼容没有clear方法的情况
            history.messages = []  # 直接清空消息列表
        
        # 重置所有状态变量
        self.word_count = 5
        self.current_words = []
        self.words_generated = False
        self.in_conversation = False
        
        LOG.info(f"会话{self.session_id}已重置")
        return "会话已重置。请重新生成单词开始学习。"

