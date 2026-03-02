# 贡献指南

感谢你考虑为本项目做出贡献！

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请创建一个 Issue 并包含以下信息：

- Bug 的详细描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python 版本、操作系统等）
- 相关日志或截图

### 提出新功能

如果你有新功能的想法：

1. 先创建一个 Issue 讨论这个功能
2. 说明为什么需要这个功能
3. 描述你期望的实现方式

### 提交代码

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 确保代码符合项目规范
4. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
5. 推送到分支 (`git push origin feature/AmazingFeature`)
6. 开启一个 Pull Request

### 代码规范

- 使用 Python 3.8+ 语法
- 遵循 PEP 8 代码风格
- 添加必要的注释和文档字符串
- 确保代码可以正常运行
- 如果添加新功能，请更新相关文档

### 提交信息规范

提交信息应该清晰明了：

- `feat: 添加新功能`
- `fix: 修复 Bug`
- `docs: 更新文档`
- `style: 代码格式调整`
- `refactor: 代码重构`
- `test: 添加测试`
- `chore: 其他修改`

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/su-tiger/AgentFlow.git
cd AgentFlow

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

## 测试

在提交 PR 之前，请确保：

- 代码可以正常运行
- 没有引入新的错误
- 相关功能已经测试

## 问题？

如有任何问题，欢迎在 Issue 中提问！
