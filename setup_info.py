#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速设置个人信息的脚本
运行此脚本来自动替换项目中的占位符
"""

import os
import re


def replace_in_file(filepath, replacements):
    """在文件中替换文本"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                modified = True
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"处理文件 {filepath} 时出错: {e}")
    return False


def main():
    print("=" * 60)
    print("🚀 LangChain RAG Agent - 个人信息设置")
    print("=" * 60)
    print()
    print("此脚本将帮助你替换项目中的占位符信息")
    print()
    
    # 收集信息
    github_username = input("请输入你的 GitHub 用户名: ").strip()
    repo_name = input("请输入仓库名称 [langchain-rag-agent]: ").strip() or "langchain-rag-agent"
    your_name = input("请输入你的名字: ").strip()
    your_email = input("请输入你的邮箱: ").strip()
    
    print()
    print("确认信息：")
    print(f"  GitHub 用户名: {github_username}")
    print(f"  仓库名称: {repo_name}")
    print(f"  名字: {your_name}")
    print(f"  邮箱: {your_email}")
    print()
    
    confirm = input("确认无误？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 定义替换规则
    replacements = {
        'yourusername': github_username,
        'yourrepo': repo_name,
        'your.email@example.com': your_email,
        'Your Name': your_name,
        '[Your Name]': your_name,
    }
    
    # 需要处理的文件
    files_to_process = [
        'README.md',
        'setup.py',
        'LICENSE',
        'CONTRIBUTING.md',
        'PUBLISH_GUIDE.md',
    ]
    
    print()
    print("开始替换...")
    print()
    
    modified_count = 0
    for filepath in files_to_process:
        if os.path.exists(filepath):
            if replace_in_file(filepath, replacements):
                print(f"✅ {filepath}")
                modified_count += 1
            else:
                print(f"⏭️  {filepath} (无需修改)")
        else:
            print(f"⚠️  {filepath} (文件不存在)")
    
    print()
    print("=" * 60)
    print(f"✨ 完成！共修改了 {modified_count} 个文件")
    print("=" * 60)
    print()
    print("下一步：")
    print("1. 检查修改的文件是否正确")
    print("2. 配置 .env 文件（复制 .env.example）")
    print("3. 按照 PUBLISH_GUIDE.md 发布到 GitHub")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n错误: {e}")
