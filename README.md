Tiro English Coach
Tiro English Coach 是一款基于 AI 的英语学习辅助工具，专注于提升用户的英语写作、词汇和对话能力。通过交互式界面和智能反馈，为用户提供个性化的英语学习体验。
项目功能
1. 写作训练模块
模式一（Tiro 出题）：
系统根据选择的难度（初中 / 高中 / 大学）生成作文题目
支持 1-5 轮的作文精进，每轮提供专业点评
从内容契合度、结构完整性、语言表达等多维度评估
生成优化后的范文，帮助用户逐步提升
模式二（用户出题）：
支持用户自定义作文题目并选择难度
提供针对性的写作建议（要点、结构、词汇和语法）
生成初始作文并经过多轮优化
支持将写作过程和结果导出为 txt 文件
2. 词汇学习模块
三步教学计划：
热身与情境提问，建立学习舒适度
词汇详细详细呈现（中文含义、词性、英文定义及例句）
练习与反馈，用户造句后获得评分和改进建议
动词包含各种时态变化展示
学习结束提供总结反馈
3. 对话练习模块
基于选定场景进行角色扮演对话（酒店接待、面试、航班代理等）
系统模拟对应角色用流利英语回应
提供中英文对话提示，帮助用户回应
当用户偏离主题时给予引导
对话完成后提供中英文综合反馈
技术栈
核心开发语言
Python 3.8+：项目主要开发语言，用于实现核心逻辑和算法
前端与交互
Gradio：用于构建交互式网页界面，实现用户友好的可视化交互
HTML/CSS：用于界面样式定制和前端展示优化
AI 与自然语言处理
LangChain：用于构建 AI 智能体和管理提示词工程
实现WritingAgent（写作智能体）
实现ReflectionAgent（反思智能体）
大语言模型集成：支持与主流 LLM 模型对接（如 GPT 系列等）
工具与辅助库
python-dotenv：用于环境变量管理
logging：系统日志记录与调试
os.path：文件路径处理与管理
json：数据序列化与处理
部署与运行环境
前置要求
Python 3.8+
pip（Python 包管理工具）
安装步骤
克隆仓库

bash
git clone https://github.com/yourusername/tiro-english-coach.git
cd tiro-english-coach

创建并激活虚拟环境（可选但推荐）

bash
# 创建虚拟环境
python -m venv venv

# 在Windows上激活
venv\Scripts\activate

# 在Mac/Linux上激活
source venv/bin/activate

安装依赖包

bash
pip install -r requirements.txt

配置环境变量
创建.env文件，添加必要的环境变量（如 API 密钥等）：

plaintext
OPENAI_API_KEY=your_api_key_here
# 其他必要的配置...
运行应用
bash
python main.py

应用启动后，会自动在浏览器中打开 Gradio 界面，或在终端显示访问链接（通常为 http://localhost:7860）
贡献
欢迎提交 issue 和 pull request 来帮助改进这个项目。
许可证
MIT
