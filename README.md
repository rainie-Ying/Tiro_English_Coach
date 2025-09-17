# Tiro English Coach

Tiro English Coach 是一款基于AI的英语学习辅助工具，专注于提升用户的英语写作、词汇和对话能力。通过交互式界面和智能反馈，为用户提供个性化的英语学习体验。本项目在Linux系统下开发，采用本地化部署方案，通过Docker容器运行Ollama实现大模型集成，默认使用 **qwen3:latest**（阿里云通义千问3系列）模型适配英语学习场景。


## 项目功能

### 1. 写作训练模块
提供两种出题模式，支持多轮作文精进与结果导出，覆盖不同学习需求：
- **模式一（Tiro出题）**：
  - 按难度（初中/高中/大学）自动生成英语作文题目
  - 支持1-5轮精进，每轮从「内容契合度、结构完整性、语言表达」三维度点评
  - 生成优化范文，对比展示改进方向
- **模式二（用户出题）**：
  - 支持用户自定义作文题目并选择难度
  - 先输出针对性写作建议（含要点、结构、词汇、语法指导）
  - 生成初始作文后，经多轮反思优化生成多版改进稿
  - 支持将「题目+用户作文+点评+范文」导出为txt文件


### 2. 词汇学习模块
采用「热身-呈现-练习」三步教学法，强化词汇理解与应用：
1. **热身与情境提问**：通过日常话题互动，建立学习舒适度
2. **词汇详细呈现**：按「中文含义+词性+英文定义+例句」格式展示，动词额外补充时态变化
3. **练习与反馈**：用户造句后获得评分、错误纠正及地道表达建议，学习结束生成总结报告


### 3. 对话练习模块
模拟真实场景角色扮演，提升口语对话能力：
- 支持多场景选择（酒店接待、面试、航班代理等）
- 系统以对应角色输出流利英语回应，并提供中英文对话提示
- 当用户偏离主题时，自动引导回场景流程
- 对话结束后，生成「优点+改进建议+鼓励」的中英文综合反馈


## 技术栈

| 分类                | 技术/工具                          | 作用说明                                                                 |
|---------------------|-----------------------------------|--------------------------------------------------------------------------|
| 核心开发语言        | Python 3.8+                       | 实现项目核心逻辑、AI交互与接口开发                                       |
| 前端与交互          | Gradio                             | 快速构建可视化交互式网页界面，支持输入输出交互                           |
|                     | HTML/CSS                          | 辅助定制界面样式，优化前端展示效果                                       |
| AI与自然语言处理    | LangChain                         | 构建`WritingAgent`（写作智能体）、`ReflectionAgent`（反思智能体），管理提示词工程 |
|                     | Ollama                            | 本地大模型管理工具，负责部署和运行开源大模型                             |
|                     | Docker                            | 容器化部署Ollama与大模型，避免环境依赖冲突                               |
| 工具与辅助库        | python-dotenv                     | 管理环境变量（如Ollama地址、模型名称）                                   |
|                     | logging                           | 记录系统运行日志，便于调试与问题定位                                     |
|                     | requests                          | 与Ollama API交互，实现模型调用                                          |
|                     | os.path/json                      | 处理文件路径与数据序列化（如作文导出、配置读取）                         |


## 部署与运行环境

### 前置要求
- 操作系统：Linux（推荐Ubuntu 20.04+ 或 Debian 11+）
- 基础工具：Python 3.8+、pip（Python包管理器）、Docker（容器化工具）
- 硬件建议：内存≥8GB（运行qwen3:latest模型最低要求，≥16GB体验更流畅）


### 安装步骤

#### 1. 安装Docker（首次部署需执行）
```bash
# 1. 更新软件包索引
sudo apt-get update

# 2. 安装Docker依赖包
sudo apt-get install ca-certificates curl gnupg lsb-release

# 3. 添加Docker官方GPG密钥（验证包完整性）
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 4. 配置Docker稳定版仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 安装Docker引擎
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# 6. 配置用户权限（避免每次执行docker命令用sudo）
sudo usermod -aG docker $USER
newgrp docker  # 应用权限（需重新登录生效，若临时测试可跳过）
```

#### 2. 用Docker 部署 Ollama
```bash
# 1. 拉取Ollama镜像并启动容器（映射11434端口，挂载数据卷保存模型）
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# 2. 验证容器是否正常运行（出现"ollama"容器名即成功）
docker ps | grep ollama
```

#### 3. 在 Ollama 中安装默认模型（qwen3:latest）
```bash
# 1. 进入Ollama容器内部
docker exec -it ollama /bin/bash

# 2. 安装默认模型qwen3:latest（约4.5GB，需耐心等待）
ollama pull qwen3:latest

# 3. 验证模型安装（出现qwen3:latest即成功）
ollama list

# 4. 退出容器
exit
```

#### 4. 部署 Tiro English Coach 应用
```bash
# 1. 克隆项目仓库（替换yourusername为实际GitHub用户名）
git clone https://github.com/yourusername/tiro-english-coach.git
cd tiro-english-coach
```

# 2. 创建并激活Python虚拟环境（避免依赖冲突）
```bash
python -m venv venv
source venv/bin/activate  # Linux环境激活命令
```

# 3. 安装项目依赖包
```bash
pip install -r requirements.txt
```

# 4. 配置环境变量（关联Ollama与模型）
# 方式1：直接创建.env文件（推荐）
```bash
echo "OLLAMA_API_BASE_URL=http://localhost:11434" > .env
echo "OLLAMA_MODEL=qwen3:latest" >> .env

# 方式2：若有.env.example示例文件，可复制后修改
# cp .env.example .env
```

#### 5.启动应用
```bash
# 在虚拟环境中运行（确保venv已激活）
python main.py
```
启动成功后，终端会输出访问链接（默认：`http://localhost:7860`），打开浏览器即可使用。

### *如何更换其他模型*  
若需替换为 Ollama 支持的其他模型（如 llama3、gemma 等），按以下步骤操作：

#### *1.查看可用模型*
访问 Ollama 官方模型库：https://ollama.com/library，选择适配英语场景的模型（推荐 7B 参数级模型，平衡性能与速度）。

#### *2. 安装新模型*
```bash
# 1. 进入Ollama容器
docker exec -it ollama /bin/bash

# 2. 拉取目标模型（以llama3为例）
ollama pull llama3

# 3. 验证安装（确认模型名正确）
ollama list

# 4. 退出容器
exit
```

#### *3. 修改项目配置*
```bash
# 编辑.env文件（使用nano编辑器）
nano .env

# 将OLLAMA_MODEL值改为新模型名，例如：
OLLAMA_MODEL=llama3

# 保存并退出（nano操作：按Ctrl+O → 回车确认 → Ctrl+X）
```
#### *4. 重启应用*
```bash
# 1. 先停止当前应用（按Ctrl+C）
# 2. 重新启动
python main.py
```
### *Tiro English Coach - 常见问题解决指南*
| 分类          | 问题现象                                | 解决方案                                                                                                                                                                                                                                                                                                          |
| ----------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Docker 相关问题 | Docker 命令权限错误（提示 Permission denied） | 1. 执行权限配置命令：`sudo usermod -aG docker $USER`（将当前用户添加到 docker 用户组）2. 必须重新登录系统（权限修改需重新登录生效）3. 临时方案：在 Docker 命令前加`sudo`（如`sudo docker ps`）                                                                                                                                                                        |
| Ollama 服务问题 | Ollama 连接失败（应用提示无法连接模型服务）           | 1. 检查容器状态：执行 \`docker ps                                                                                                                                                                                                                                                                                      |
| 模型运行问题      | 模型运行缓慢（响应时间超 10 秒）                  | 1. 更换轻量模型：将`OLLAMA_MODEL`改为`gemma-2b`/`mistral-7b-instruct`（按更换模型流程操作）2. 释放资源：关闭高内存占用程序（用`htop`查看）3. 硬件要求：确保内存≥8GB，推荐 16GB 以上                                                                                                                                                                                 |
| 应用启动问题      | 应用无法启动（执行 python main.py 报错）        | 1. 检查依赖：执行`pip list`，确认`gradio`/`langchain`/`requests`等已安装，缺失则重新执行`pip install -r requirements.txt`2. 核对.env 配置：确保`OLLAMA_API_BASE_URL=http://localhost:11434`，`OLLAMA_MODEL`与已安装模型名一致（用`docker exec -it ollama ollama list`查看）3. 解决端口冲突：若提示 Address already in use，修改代码指定新端口（如`gr.launch(server_port=7861)`） |
| 功能使用问题      | 作文导出功能失效（无文件生成）                     | 1. 检查目录权限：执行`ls -l ./tiro-english-coach`，确保有写入权限，无则执行`chmod 755 ./tiro-english-coach`2. 关闭文件占用：确保之前导出的同名.txt 文件未被打开3. 确认导出路径：若自定义路径，需提前创建（如`mkdir -p ./exports`）                                                                                                                                              |
| 功能使用问题      | 对话练习偏离场景（回应无关）                      | 1. 重启应用：按`Ctrl+C`停止后重新执行`python main.py`，清除会话缓存2. 切换推荐模型：优先使用`qwen3:latest`或`llama3`3. 优化输入：贴合场景主题，避免无关话题                                                                                                                                                                                                     |
| Ollama 服务问题 | Ollama 容器重启后模型丢失                    | 1. 检查数据卷挂载：确认部署时加`-v ollama:/root/.ollama`参数，无则重新创建容器并拉取模型2. 恢复数据卷：执行`docker volume inspect ollama`查看路径，确认模型文件存在则重新关联3. 设置自启：执行`docker update --restart=always ollama`                                                                                                                                        |
| 功能使用问题      | 词汇学习模块无反馈（输入造句无响应）                  | 1. 检查 Ollama 连接：参考 Ollama 连接失败解决方案确认服务正常2. 增加等待时间：低配置设备建议等待 15-30 秒3. 简化输入：造句控制在 20 词以内，减少模型压力

### *许可证*
本项目基于 MIT License 开源，允许个人或商业用途的修改与分发，需保留原许可证声明。
