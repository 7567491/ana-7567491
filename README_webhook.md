# 6页网用户活动日报系统

## 系统概述

自动化用户活动日报系统，每天上午10点和晚上10点自动统计过去24小时的用户活动，包括：
- 🆕 新用户注册
- 💰 产品购买
- 👥 老用户登录  
- 📚 课程观看

报告通过企业微信webhook发送，同时保存到本地日志文件。

## 文件说明

### 核心文件
- `webhook.py` - 主要脚本，负责数据查询、报告生成和发送
- `test_webhook.py` - 测试脚本，包含单元测试和集成测试
- `webhook_monitor.py` - 系统监控脚本，检查运行状态和清理日志
- `start_webhook.sh` - 启动脚本，包含健康检查和错误处理

### 配置文件
- `config.py` - 数据库连接配置
- `webhook.md` - 企业微信webhook发送说明

### 日志目录
- `webhook-log/` - webhook发送日志，按日期保存
- `logs/` - 系统运行日志和监控日志

## 安装部署

### 1. 依赖安装
```bash
pip3 install pymysql requests
```

### 2. 权限设置
```bash
chmod +x webhook.py
chmod +x start_webhook.sh  
chmod +x webhook_monitor.py
```

### 3. 定时任务配置
```bash
# 查看当前定时任务
crontab -l

# 手动编辑（如需修改）
crontab -e

# 当前配置：每天10点和22点运行
0 10,22 * * * cd /www/wwwroot/ana && /usr/bin/python3 webhook.py >> /www/wwwroot/ana/cron.log 2>&1
```

## 使用方法

### 手动运行
```bash
# 直接运行
cd /www/wwwroot/ana
python3 webhook.py

# 使用启动脚本（推荐）
./start_webhook.sh run
```

### 健康检查
```bash
# 系统健康检查
./start_webhook.sh health

# 运行测试
./start_webhook.sh test
python3 test_webhook.py
```

### 系统监控
```bash
# 运行系统监控
python3 webhook_monitor.py

# 清理旧日志
python3 webhook_monitor.py clean

# 测试各项连接
python3 webhook_monitor.py test
```

## 报告格式

### 简洁版本（当前）
```
📊 6页网24小时活动报告(2025-09-05 10:00)
🆕 新注册：3人
💰 购买：2笔，收入¥298
👥 活跃：15人登录
📚 观看：25次，120分钟
```

### 说明
- 只显示有数据的项目（如果某项为0则不显示）
- 每项一句话，保持简洁
- 按日期时间标注报告时间

## 日志管理

### Webhook日志
- 位置: `webhook-log/webhook_YYYYMMDD.log`
- 格式: 时间戳 + 状态 + 发送内容
- 按天分文件，便于查看历史记录

### 系统日志  
- 位置: `webhook.log`
- 内容: 脚本运行日志、错误信息
- 位置: `logs/monitor.log`
- 内容: 系统监控日志

### 定时任务日志
- 位置: `cron.log`
- 内容: crontab执行日志

## 数据查询逻辑

### 新用户注册
- 表: `wy_user` + `wy_wechat_user`
- 条件: 过去24小时内注册的用户
- 显示: 用户数量

### 产品购买
- 表: `wy_special_buy` + `wy_store_order` + `wy_special`
- 条件: 过去24小时内的购买记录
- 显示: 购买笔数、总收入

### 用户登录
- 表: `wy_user` + `wy_wechat_user`
- 条件: 过去24小时内登录的老用户（注册时间早于昨天）
- 显示: 活跃用户数

### 课程观看
- 表: `wy_special_watch` + `wy_special` + `wy_user`
- 条件: 过去24小时内的观看记录
- 显示: 观看次数、总时长

## 监控和维护

### 自动监控
- 数据库连接检查
- Webhook连通性测试
- 定时任务状态检查
- 日志文件大小监控
- 旧日志自动清理（保留30天）

### 错误处理
- 超时处理（5分钟超时）
- 重试机制
- 错误通知（发送到企业微信）
- 详细日志记录

### 性能优化
- 查询优化（限制结果数量）
- 连接池管理
- 内存使用控制

## 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查数据库服务
   systemctl status mysql
   
   # 检查配置
   python3 -c "from config import DATABASE_CONFIG; print(DATABASE_CONFIG)"
   ```

2. **Webhook发送失败**
   ```bash
   # 检查网络连接
   curl -X POST 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d3ed6660-1f33-47cc-83dd-84423fc7f8ac' \
   -H 'Content-Type: application/json' \
   -d '{"msgtype":"text","text":{"content":"测试消息"}}'
   ```

3. **定时任务不运行**
   ```bash
   # 检查crontab服务
   systemctl status crond
   
   # 查看crontab日志
   tail -f /www/wwwroot/ana/cron.log
   ```

4. **权限问题**
   ```bash
   # 检查文件权限
   ls -la /www/wwwroot/ana/
   
   # 修复权限
   chown -R ana:ana /www/wwwroot/ana/
   chmod +x /www/wwwroot/ana/*.py
   chmod +x /www/wwwroot/ana/*.sh
   ```

### 日志查看
```bash
# 查看最近的运行日志
tail -f /www/wwwroot/ana/webhook.log

# 查看webhook发送记录
tail -f /www/wwwroot/ana/webhook-log/webhook_$(date +%Y%m%d).log

# 查看定时任务执行情况
tail -f /www/wwwroot/ana/cron.log

# 查看系统监控日志
tail -f /www/wwwroot/ana/logs/monitor.log
```

## 安全注意事项

1. **数据库密码**: 存储在`config.py`中，请妥善保管
2. **Webhook密钥**: 写在代码中，生产环境建议使用环境变量
3. **日志文件**: 包含用户信息，注意访问权限控制
4. **网络安全**: 确保webhook URL的安全性

## 维护计划

### 日常维护
- 每周检查日志文件大小
- 每月检查系统运行状态
- 定期更新依赖包

### 定期任务
- 每30天自动清理旧日志
- 每季度检查数据库性能
- 年度安全审计

## 联系方式

如有问题，请查看日志文件或联系系统管理员。

---

*最后更新: 2025-09-05*