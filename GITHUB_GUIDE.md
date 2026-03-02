# 📘 GitHub 开源完整指南

这是一份详细的 GitHub 开源指南，帮助你一步步将项目发布到 GitHub。

## 🎯 准备工作

### 1. 注册 GitHub 账号

如果还没有 GitHub 账号：

1. 访问 https://github.com
2. 点击右上角 "Sign up"
3. 填写邮箱、密码、用户名
4. 验证邮箱

### 2. 安装 Git

**Windows:**
- 下载：https://git-scm.com/download/win
- 双击安装，一路 Next

**验证安装：**
```bash
git --version
```

### 3. 配置 Git

```bash
# 设置用户名（会显示在提交记录中）
git config --global user.name "你的名字"

# 设置邮箱（建议使用 GitHub 邮箱）
git config --global user.email "your.email@example.com"

# 查看配置
git config --list
```

## 📤 发布到 GitHub

### 方法一：通过 GitHub 网页创建（推荐新手）

#### 步骤 1：在 GitHub 创建仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `langchain-rag-agent`（或你喜欢的名字）
   - Description: `LangChain RAG & Agent 实战项目`
   - 选择 Public（公开）
   - ❌ 不要勾选 "Initialize this repository with a README"（因为我们已经有了）
4. 点击 "Create repository"

#### 步骤 2：在本地初始化 Git

在项目根目录打开命令行：

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 完整的 LangChain RAG & Agent 项目"

# 添加远程仓库（替换成你的 GitHub 用户名和仓库名）
git remote add origin https://github.com/你的用户名/langchain-rag-agent.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

#### 步骤 3：输入 GitHub 凭证

第一次推送时会要求输入凭证：

**方法 A：使用 Personal Access Token（推荐）**

1. 在 GitHub 上：Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成并复制 token
5. 在命令行输入用户名和 token（作为密码）

**方法 B：使用 GitHub Desktop（更简单）**

1. 下载 GitHub Desktop: https://desktop.github.com/
2. 登录 GitHub 账号
3. File → Add Local Repository → 选择项目文件夹
4. 点击 "Publish repository"

### 方法二：使用 GitHub CLI（适合熟悉命令行的用户）

```bash
# 安装 GitHub CLI
# Windows: 从 https://cli.github.com/ 下载安装

# 登录
gh auth login

# 创建仓库并推送
gh repo create langchain-rag-agent --public --source=. --remote=origin --push
```

## ✅ 验证发布成功

1. 访问 `https://github.com/你的用户名/langchain-rag-agent`
2. 应该能看到所有文件和 README

## 🎨 美化你的 GitHub 仓库

### 1. 添加 Topics（标签）

在仓库页面：
- 点击右侧 "About" 旁边的齿轮图标
- 添加 topics: `langchain`, `rag`, `agent`, `llm`, `python`, `ai`

### 2. 添加项目描述

在 "About" 设置中：
- Description: `🚀 LangChain RAG & Agent 实战项目 - 包含知识库问答、多Agent协作、评估体系`
- Website: 如果有文档网站的话

### 3. 创建 Release

```bash
# 打标签
git tag -a v1.0.0 -m "首次发布"
git push origin v1.0.0
```

然后在 GitHub 上：
- 进入 "Releases" → "Create a new release"
- 选择刚才的 tag
- 填写 Release notes

## 📝 日常维护

### 更新代码

```bash
# 查看修改
git status

# 添加修改的文件
git add .

# 提交
git commit -m "feat: 添加新功能"

# 推送
git push
```

### 常用 Git 命令

```bash
# 查看状态
git status

# 查看提交历史
git log --oneline

# 创建分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/new-feature

# 拉取最新代码
git pull

# 查看远程仓库
git remote -v
```

## 🔧 常见问题

### 问题 1：推送时提示 "Permission denied"

**解决方案：**
- 使用 Personal Access Token 而不是密码
- 或使用 SSH 密钥（需要额外配置）

### 问题 2：文件太大无法推送

**解决方案：**
```bash
# 查看大文件
git ls-files --others --ignored --exclude-standard

# 确保 .gitignore 包含了大文件
# 如果已经提交了大文件，需要从历史中删除
git filter-branch --tree-filter 'rm -f 大文件路径' HEAD
```

### 问题 3：想要撤销某次提交

**解决方案：**
```bash
# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD~1
```

### 问题 4：中文文件名显示乱码

**解决方案：**
```bash
git config --global core.quotepath false
```

## 📢 推广你的项目

1. **写好 README**：清晰的说明和示例
2. **添加 Badge**：显示项目状态
3. **分享到社区**：
   - Reddit: r/Python, r/MachineLearning
   - Twitter/X
   - 知乎、掘金等中文社区
4. **持续更新**：定期添加新功能
5. **回复 Issue**：积极与用户互动

## 🎓 学习资源

- Git 官方文档：https://git-scm.com/doc
- GitHub 官方指南：https://guides.github.com/
- Git 可视化学习：https://learngitbranching.js.org/
- GitHub Skills：https://skills.github.com/

## 💡 下一步

- [ ] 设置 GitHub Actions（自动化测试）
- [ ] 添加 Code of Conduct
- [ ] 创建 Wiki 文档
- [ ] 设置 Issue 模板
- [ ] 添加 PR 模板

祝你开源顺利！🎉
