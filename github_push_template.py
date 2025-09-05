#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub推送模板脚本
使用前请设置环境变量: export GITHUB_TOKEN="your_token_here"
"""

import requests
import json
import os
import subprocess
import sys

def get_github_token():
    """从环境变量获取GitHub token"""
    token = os.getenv('GITHUB_TOKEN') or os.getenv('Github_Token')
    if not token:
        print("❌ 错误: 请先设置环境变量 GITHUB_TOKEN")
        print("   export GITHUB_TOKEN='your_github_token'")
        sys.exit(1)
    return token

def create_and_push_repo(repo_name, description):
    """创建GitHub仓库并推送代码"""
    token = get_github_token()
    
    # GitHub API配置
    GITHUB_API_BASE = "https://api.github.com"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 获取用户信息
    response = requests.get(f"{GITHUB_API_BASE}/user", headers=headers)
    if response.status_code != 200:
        print("❌ GitHub认证失败")
        sys.exit(1)
    
    user_data = response.json()
    print(f"✅ 认证成功! 用户: {user_data['login']}")
    
    # 创建仓库
    data = {
        "name": repo_name,
        "description": description,
        "private": False,
        "auto_init": False
    }
    
    response = requests.post(f"{GITHUB_API_BASE}/user/repos", headers=headers, json=data)
    
    if response.status_code == 201:
        repo_data = response.json()
        print(f"✅ 仓库创建成功: {repo_data['html_url']}")
    elif response.status_code == 422:
        print("⚠️  仓库已存在，继续推送...")
        user_login = user_data['login']
        repo_response = requests.get(f"{GITHUB_API_BASE}/repos/{user_login}/{repo_name}", headers=headers)
        if repo_response.status_code == 200:
            repo_data = repo_response.json()
        else:
            print("❌ 无法获取仓库信息")
            sys.exit(1)
    else:
        print(f"❌ 仓库创建失败: {response.status_code}")
        sys.exit(1)
    
    # 设置git远程仓库并推送
    authenticated_url = repo_data['clone_url'].replace('https://', f'https://{token}@')
    
    try:
        # 删除现有的origin（如果存在）
        subprocess.run(['git', 'remote', 'remove', 'origin'], cwd="/home/ana", capture_output=True)
    except:
        pass
    
    # 添加远程仓库
    result = subprocess.run(['git', 'remote', 'add', 'origin', authenticated_url], cwd="/home/ana", capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 远程仓库配置成功")
        
        # 推送代码
        result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], cwd="/home/ana", capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 代码推送成功!")
            print(f"🎉 仓库地址: {repo_data['html_url']}")
        else:
            print(f"❌ 推送失败: {result.stderr}")
    else:
        print(f"❌ 远程仓库配置失败: {result.stderr}")

if __name__ == "__main__":
    # 使用示例
    REPO_NAME = "ana-7567491"
    REPO_DESCRIPTION = "Ana项目 #7567491 - 6页网用户活动日报系统和数据分析工具"
    
    create_and_push_repo(REPO_NAME, REPO_DESCRIPTION)