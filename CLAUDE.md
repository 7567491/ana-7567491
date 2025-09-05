# CLAUDE.md

请用中文和我对话

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 系统概述

这是一个运行在Linux上的多服务器环境，包含以下几个关键组件：

- **Web应用程序**：托管在 `/www/wwwroot/` 下的多个基于PHP的网站
- **主要应用程序**：位于 `/www/wwwroot/www.6page.cn/` 的 ThinkPHP 5.0 框架应用
- **数据分析系统**：位于 `/www/wwwroot/ana/` 的 Flask 数据分析应用
- **用户活动日报系统**：自动化webhook日报系统，每日10:00和22:00发送活动统计
- **数据库**：MySQL 5.7，数据存储在 `/www/server/data/`
- **Web服务器**：Nginx 配置位于 `/www/server/nginx/`
- **面板管理**：用于服务器管理的宝塔(BT)面板，位于 `/www/server/panel/`

## 架构说明

### 主应用程序 (`/www/wwwroot/www.6page.cn/`)
- **框架**：ThinkPHP 5.0
- **结构**：采用MVC模式，包含不同接口的模块
- **模块**：
  - `admin/` - 后台管理系统
  - `wap/` - 移动端/WAP接口  
  - `web/` - Web前端
  - `wechat/` - 微信集成
  - `callback/` - 支付/API回调
  - `push/` - WebSocket/推送通知

### 数据分析系统 (`/www/wwwroot/ana/`)
- **框架**：Flask (Python)
- **功能**：6页网数据分析和可视化
- **端口**：127.0.0.1:8080
- **数据库**：使用主数据库6page，用户: 6page，密码: 5NsFLLBFFsnZb3fh
- **主要组件**：
  - `app.py` - Flask主应用
  - `database.py` - 数据库查询模块
  - `config.py` - 配置文件
  - `templates/` - HTML模板
  - `static/` - 静态资源（CSS/JS）

### 数据库配置
- **类型**：MySQL
- **数据库名**：`6page`
- **表前缀**：`wy_`
- **连接**：localhost:3306
- **字符集**：utf8mb4

### 主要功能
- 教育平台，包含课程、直播、文章功能
- 多支付系统（支付宝、微信支付）
- 用户管理，支持会员等级
- 内容管理（文章、课程、下载资料）
- 直播功能
- 移动端和Web端界面

## 开发命令

### PHP/Composer
```bash
# 安装依赖
composer install

# 更新依赖
composer update

# 使用PHP内置服务器运行（用于测试）
cd /www/wwwroot/www.6page.cn/public
php -S localhost:8888 router.php
```

### Ana数据分析系统
```bash
# 进入ana项目目录
cd /www/wwwroot/ana

# 启动Flask应用
python3 app.py

# 后台运行
nohup python3 app.py > app.log 2>&1 &

# 检查进程状态
ps aux | grep "python3 app.py"

# 访问应用
curl http://127.0.0.1:8080
```

### Webhook用户活动日报系统
```bash
# 进入ana项目目录
cd /www/wwwroot/ana

# 手动运行webhook脚本
python3 webhook.py

# 使用启动脚本（推荐）
./start_webhook.sh run

# 健康检查
./start_webhook.sh health

# 运行测试
./start_webhook.sh test
python3 test_webhook.py

# 系统监控
python3 webhook_monitor.py

# 查看定时任务
crontab -l

# 查看日志
tail -f webhook.log
tail -f webhook-log/webhook_$(date +%Y%m%d).log
tail -f cron.log
```

### 数据库操作
```bash
# 连接MySQL
mysql -u root -p

# 备份数据库
mysqldump -u root -p 6page > backup.sql

# 导入数据库
mysql -u root -p 6page < backup.sql
```

### Web服务器管理
```bash
# 重启Nginx
systemctl restart nginx

# 检查Nginx状态
systemctl status nginx

# 测试Nginx配置
nginx -t

# 查看Nginx日志
tail -f /www/server/nginx/logs/error.log
```

### 服务管理
```bash
# MySQL服务
systemctl status mysql
systemctl restart mysql

# Redis服务
systemctl status redis
systemctl restart redis

# PHP-FPM服务
systemctl status php74-php-fpm
systemctl restart php74-php-fpm
```

## 配置文件

### 应用配置
- `/www/wwwroot/www.6page.cn/application/config.php` - 主应用配置
- `/www/wwwroot/www.6page.cn/application/database.php` - 数据库设置
- `/www/wwwroot/www.6page.cn/application/constant.php` - 应用常量

### 服务器配置
- `/www/server/nginx/conf/nginx.conf` - Nginx主配置
- `/www/server/mysql/my.cnf` - MySQL配置
- `/www/server/php/74/etc/php.ini` - PHP配置

## 文件结构

```
/www/wwwroot/www.6page.cn/
├── application/           # 应用程序代码
│   ├── admin/            # 管理模块
│   ├── wap/              # 移动端接口
│   ├── web/              # Web接口
│   ├── wechat/           # 微信集成
│   └── common.php        # 公共函数
├── public/               # 公共Web目录
│   ├── index.php         # 入口文件
│   ├── pc/               # PC端静态资源
│   ├── static/           # 静态文件
│   └── uploads/          # 上传目录
├── extend/               # 扩展类库
├── thinkphp/             # ThinkPHP框架
├── vendor/               # Composer依赖
└── runtime/              # 运行时缓存/日志

/www/wwwroot/ana/          # 数据分析系统
├── app.py                # Flask主应用
├── database.py           # 数据库查询模块
├── config.py             # 配置文件
├── webhook.py            # 用户活动日报脚本
├── webhook_monitor.py    # 系统监控脚本
├── test_webhook.py       # Webhook测试脚本
├── start_webhook.sh      # Webhook启动脚本
├── README_webhook.md     # Webhook系统说明文档
├── templates/            # HTML模板
│   └── index.html        # 主页模板
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css     # 样式文件
│   ├── js/
│   │   └── app.js        # JavaScript文件
│   └── images/           # 图片资源
├── webhook-log/          # Webhook发送日志目录
│   └── webhook_YYYYMMDD.log  # 按日期分文件保存
├── logs/                 # 系统监控日志目录
├── app.log               # 应用日志
├── webhook.log           # Webhook运行日志
├── cron.log              # 定时任务日志
├── requirements.txt      # Python依赖
└── start.sh              # Flask启动脚本
```

## 安全注意事项

- 数据库凭据存储在 `/www/wwwroot/www.6page.cn/application/database.php`
- 文件上传处理在 `/www/wwwroot/www.6page.cn/public/uploads/`
- SSL证书和安全配置应通过宝塔面板管理
- 进行重大更改前务必备份数据库

## 故障排除

### 常见问题
1. **权限错误**：检查 `/www/wwwroot/` 目录的文件权限
2. **数据库连接**：验证MySQL服务和凭据
3. **Nginx 502错误**：检查PHP-FPM服务状态
4. **文件上传问题**：检查 `uploads/` 目录权限

### 日志文件
- 应用日志：`/www/wwwroot/www.6page.cn/runtime/log/`
- Ana分析日志：`/www/wwwroot/ana/app.log`
- Nginx日志：`/www/server/nginx/logs/`
- MySQL日志：`/www/server/data/mysql-slow.log`
- PHP日志：`/var/log/php74/php-fpm.log`

## Ana用户配置

- **用户名**：ana
- **密码**：lin@3
- **权限**：sudo无密码权限
- **主目录**：/home/ana
- **工作目录**：/home/ana（用户的所有项目和文件都在此目录下）
- **项目目录**：/www/wwwroot/ana（数据分析系统部署目录）
- **自动启动**：登录时自动执行 `claude --dangerously-skip-permissions`

### 重要说明
- Ana用户的工作环境在 `/home/ana` 目录
- 不要在 `/www/wwwroot` 目录下查找用户文件
- 所有个人配置、脚本、项目文件都位于 `/home/ana`