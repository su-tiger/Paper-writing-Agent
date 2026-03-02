#!/bin/bash

echo "========================================"
echo "LangChain RAG Agent 项目安装脚本"
echo "========================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python，请先安装 Python 3.8+"
    exit 1
fi

echo "[1/4] 检测到 Python 版本:"
python3 --version
echo ""

echo "[2/4] 创建虚拟环境..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[错误] 创建虚拟环境失败"
    exit 1
fi
echo "[成功] 虚拟环境创建完成"
echo ""

echo "[3/4] 激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi
echo "[成功] 依赖安装完成"
echo ""

echo "[4/4] 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[提示] 已创建 .env 文件，请编辑并填入你的 API Key"
else
    echo "[提示] .env 文件已存在，跳过创建"
fi
echo ""

echo "========================================"
echo "安装完成！"
echo "========================================"
echo ""
echo "下一步操作："
echo "1. 编辑 .env 文件，填入你的 DEEPSEEK_API_KEY"
echo "2. 将 PDF 文档放入 data/pdf/ 目录"
echo "3. 运行: source venv/bin/activate"
echo "4. 运行: python main.py --help"
echo ""
