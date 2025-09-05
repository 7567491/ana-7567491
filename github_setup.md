# GitHub推送设置说明

## 1. 如果您已有GitHub仓库

```bash
# 添加远程仓库（替换为您的实际仓库地址）
git remote add origin https://github.com/yourusername/your-repo.git

# 或者使用SSH（推荐，需要配置SSH密钥）
git remote add origin git@github.com:yourusername/your-repo.git

# 推送到GitHub
git push -u origin main
```

## 2. 如果需要创建新的GitHub仓库

1. 访问 https://github.com
2. 点击右上角 "+" -> "New repository"
3. 填写仓库名称，如: `6page-webhook-system`
4. 选择 Public 或 Private
5. 不要勾选 "Initialize this repository with a README"
6. 点击 "Create repository"

然后运行：
```bash
git remote add origin https://github.com/yourusername/6page-webhook-system.git
git push -u origin main
```

## 3. 当前Git状态

✅ 仓库已初始化：`/home/ana/.git`
✅ 主分支：`main`
✅ 用户配置：`ana <ana@6page.cn>`
✅ 初始提交已完成：包含webhook系统所有文件

## 4. 包含的文件

### Webhook系统核心文件
- `webhook.py` - 主脚本（用户活动日报生成和发送）
- `test_webhook.py` - 测试脚本（单元测试+集成测试）
- `webhook_monitor.py` - 系统监控脚本
- `start_webhook.sh` - 生产级启动脚本
- `README_webhook.md` - 详细使用说明
- `webhook.md` - 企业微信发送配置

### 系统配置文件
- `CLAUDE.md` - Claude Code工作指导文档（已更新）
- `.gitignore` - Git忽略规则
- 其他用户配置文件

## 5. 下次推送

当您修改文件后，可以这样提交：

```bash
# 查看修改状态
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "更新描述"

# 推送到GitHub
git push origin main
```

## 6. SSH密钥配置（推荐）

如果使用SSH方式推送，需要配置SSH密钥：

```bash
# 生成SSH密钥（如果没有）
ssh-keygen -t rsa -b 4096 -C "ana@6page.cn"

# 显示公钥内容，复制到GitHub设置中
cat ~/.ssh/id_rsa.pub
```

然后到GitHub -> Settings -> SSH and GPG keys -> New SSH key 添加公钥。

---

请根据您的具体情况选择合适的方式来推送到GitHub！