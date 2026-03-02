# 🚀 快速开始指南

这是一份面向零基础用户的快速开始指南。

## 📋 前置要求

- Python 3.8 或更高版本
- 一个 DeepSeek API Key（免费注册：https://platform.deepseek.com/）

## 🔧 安装步骤

### Windows 用户

1. **下载项目**
   ```bash
   # 如果已经从 GitHub 克隆
   cd langchain-rag-agent
   
   # 或者下载 ZIP 并解压
   ```

2. **运行安装脚本**
   ```bash
   # 双击运行 install.bat
   # 或在命令行中运行：
   install.bat
   ```

3. **配置 API Key**
   - 打开 `.env` 文件
   - 将 `your_api_key_here` 替换为你的 DeepSeek API Key
   - 保存文件

### Mac/Linux 用户

1. **下载项目**
   ```bash
   cd langchain-rag-agent
   ```

2. **运行安装脚本**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **配置 API Key**
   ```bash
   # 编辑 .env 文件
   nano .env
   # 或使用你喜欢的编辑器
   ```

### 手动安装（如果脚本失败）

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
# 然后编辑 .env 文件
```

## 🎯 第一次运行

### 1. 准备 PDF 文档

将你的 PDF 文档放入 `data/pdf/` 目录：

```bash
# 创建目录（如果不存在）
mkdir -p data/pdf

# 复制你的 PDF 文件
# 例如：将 paper.pdf 复制到 data/pdf/
```

### 2. 构建向量索引

```bash
# 激活虚拟环境（如果还没激活）
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 构建索引
python scripts/build_index.py --pdf data/pdf/你的文件.pdf
```

### 3. 运行问答系统

```bash
# 单次查询
python scripts/run_qa.py --query "你的问题"

# 交互模式（推荐）
python scripts/run_qa.py --interactive
```

### 4. 运行 RAG 写作系统

```bash
# 简化版（推荐新手）
python scripts/run_rag_writing_simple.py

# 完整版（需要安装 langgraph）
python scripts/run_rag_writing.py
```

## 📚 使用示例

### 示例 1：学术论文问答

```bash
# 1. 准备论文
# 将 CLIP.pdf 放入 data/pdf/

# 2. 构建索引
python scripts/build_index.py --pdf data/pdf/CLIP.pdf

# 3. 提问
python scripts/run_qa.py --query "What is CLIP?"
```

### 示例 2：生成学术综述

```bash
# 运行 RAG 写作系统
python scripts/run_rag_writing_simple.py

# 输入主题，例如：
# "深度学习在计算机视觉中的应用"
```

### 示例 3：评估系统性能

```bash
# 评估 RAG 系统
python scripts/run_evaluation.py --type rag

# 评估所有系统
python scripts/run_evaluation.py --type all
```

## 🔍 常见问题

### Q1: 提示 "ModuleNotFoundError"

**原因：** 虚拟环境未激活或依赖未安装

**解决：**
```bash
# 激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 重新安装依赖
pip install -r requirements.txt
```

### Q2: 提示 "API Key 错误"

**原因：** API Key 未配置或配置错误

**解决：**
1. 检查 `.env` 文件是否存在
2. 确认 `DEEPSEEK_API_KEY` 已正确填写
3. 确认 API Key 有效（登录 DeepSeek 平台查看）

### Q3: 索引构建很慢

**原因：** 首次下载嵌入模型需要时间

**解决：**
- 耐心等待，模型只需下载一次
- 下载完成后会自动缓存
- 如果网络不好，可以使用代理

### Q4: 内存不足

**原因：** 文档太大或嵌入模型占用内存

**解决：**
1. 减小文档大小
2. 调整 `CHUNK_SIZE` 参数（在 `.env` 中）
3. 使用更小的嵌入模型

### Q5: 中文支持问题

**解决：**
- 确保文件编码为 UTF-8
- 在 `.env` 中可以设置中文嵌入模型
- 推荐使用 `BAAI/bge-base-zh-v1.5` 处理中文

## 📖 进阶使用

### 自定义配置

编辑 `.env` 文件：

```bash
# 修改嵌入模型
EMBEDDING_MODEL=BAAI/bge-base-zh-v1.5  # 中文模型

# 调整文档切分大小
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# 修改检索数量
RETRIEVAL_K=5
```

### 使用统一 CLI

```bash
# 查看所有命令
python main.py --help

# 构建索引
python main.py build --pdf data/pdf/paper.pdf

# 运行问答
python main.py qa --interactive

# 运行写作
python main.py write --topic "AI的未来"
```

## 🎓 学习路径

1. **第一天**：安装配置，运行基础示例
2. **第二天**：理解 RAG 原理，尝试不同查询
3. **第三天**：探索多 Agent 写作工作流
4. **第四天**：学习评估系统，优化性能
5. **第五天**：阅读源码，尝试自定义功能

## 📚 相关文档

- [完整 README](README.md)
- [架构文档](docs/architecture_rag.md)
- [RAG 教程](docs/rag_agent_tutorial.md)
- [评估指南](docs/evaluation_guide.md)
- [GitHub 开源指南](GITHUB_GUIDE.md)

## 💬 获取帮助

- 查看 [Issues](https://github.com/yourusername/yourrepo/issues)
- 阅读 [文档](docs/)
- 提交新的 Issue

祝你使用愉快！🎉
