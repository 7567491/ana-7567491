#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook系统监控和维护脚本
定期检查系统状态，清理日志，发送状态报告
"""

import sys
import os
import glob
from datetime import datetime, timedelta
import logging
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from webhook import UserActivityReporter

# 配置
LOG_RETENTION_DAYS = 30  # 日志保留天数
MAX_LOG_SIZE_MB = 100    # 单个日志文件最大大小MB

class WebhookMonitor:
    """Webhook系统监控器"""
    
    def __init__(self):
        self.base_dir = Path("/www/wwwroot/ana")
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # 设置监控日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / 'monitor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_database_connection(self):
        """检查数据库连接"""
        try:
            reporter = UserActivityReporter()
            conn = reporter.get_db_connection()
            if conn:
                conn.close()
                self.logger.info("数据库连接检查: ✅ 正常")
                return True
            else:
                self.logger.error("数据库连接检查: ❌ 失败")
                return False
        except Exception as e:
            self.logger.error(f"数据库连接检查异常: {e}")
            return False
    
    def check_webhook_connectivity(self):
        """检查webhook连通性"""
        try:
            import requests
            url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d3ed6660-1f33-47cc-83dd-84423fc7f8ac"
            
            # 发送测试消息
            test_data = {
                "msgtype": "text", 
                "text": {
                    "content": f"🧪 系统监控测试\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ Webhook连接正常"
                }
            }
            
            response = requests.post(url, json=test_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    self.logger.info("Webhook连接检查: ✅ 正常")
                    return True
                else:
                    self.logger.error(f"Webhook连接检查: ❌ API错误 {result}")
                    return False
            else:
                self.logger.error(f"Webhook连接检查: ❌ HTTP错误 {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Webhook连接检查异常: {e}")
            return False
    
    def clean_old_logs(self):
        """清理旧日志文件"""
        try:
            cutoff_date = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
            cleaned_count = 0
            
            # 清理各种日志文件
            log_patterns = ['*.log', '*.log.*', 'webhook_*.log']
            
            for pattern in log_patterns:
                for log_file in self.log_dir.glob(pattern):
                    try:
                        # 检查文件修改时间
                        file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                        
                        if file_mtime < cutoff_date:
                            log_file.unlink()
                            cleaned_count += 1
                            self.logger.info(f"删除旧日志: {log_file.name}")
                            
                    except Exception as e:
                        self.logger.warning(f"删除日志文件失败 {log_file}: {e}")
            
            if cleaned_count > 0:
                self.logger.info(f"日志清理完成: 删除了{cleaned_count}个旧文件")
            else:
                self.logger.info("日志清理: 无需清理")
                
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"日志清理失败: {e}")
            return 0
    
    def check_log_sizes(self):
        """检查日志文件大小"""
        try:
            large_logs = []
            max_size_bytes = MAX_LOG_SIZE_MB * 1024 * 1024
            
            for log_file in self.log_dir.glob('*.log'):
                try:
                    file_size = log_file.stat().st_size
                    size_mb = file_size / (1024 * 1024)
                    
                    if file_size > max_size_bytes:
                        large_logs.append((log_file.name, size_mb))
                        self.logger.warning(f"大日志文件: {log_file.name} ({size_mb:.1f}MB)")
                        
                except Exception as e:
                    self.logger.warning(f"检查日志大小失败 {log_file}: {e}")
            
            if large_logs:
                self.logger.warning(f"发现{len(large_logs)}个大日志文件，建议清理")
                return large_logs
            else:
                self.logger.info("日志文件大小检查: ✅ 正常")
                return []
                
        except Exception as e:
            self.logger.error(f"日志大小检查失败: {e}")
            return []
    
    def check_crontab_status(self):
        """检查crontab任务状态"""
        try:
            import subprocess
            
            # 获取当前用户的crontab
            result = subprocess.run(['crontab', '-l'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                crontab_content = result.stdout
                
                # 检查webhook任务是否存在
                if 'webhook.py' in crontab_content:
                    self.logger.info("Crontab任务检查: ✅ 正常")
                    return True
                else:
                    self.logger.error("Crontab任务检查: ❌ 未找到webhook任务")
                    return False
            else:
                self.logger.error("Crontab任务检查: ❌ 无法获取crontab")
                return False
                
        except Exception as e:
            self.logger.error(f"Crontab任务检查异常: {e}")
            return False
    
    def generate_system_status_report(self):
        """生成系统状态报告"""
        try:
            self.logger.info("开始系统状态检查...")
            
            # 执行各项检查
            db_status = self.check_database_connection()
            webhook_status = self.check_webhook_connectivity()
            crontab_status = self.check_crontab_status()
            large_logs = self.check_log_sizes()
            cleaned_logs = self.clean_old_logs()
            
            # 生成状态报告
            report = f"🔧 6页网Webhook系统状态报告\n"
            report += f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # 系统状态
            status_emoji = "✅" if all([db_status, webhook_status, crontab_status]) else "⚠️"
            report += f"{status_emoji} 系统状态: {'正常' if all([db_status, webhook_status, crontab_status]) else '异常'}\n"
            
            # 详细状态
            if not db_status:
                report += "❌ 数据库连接异常\n"
            if not webhook_status:
                report += "❌ Webhook连接异常\n" 
            if not crontab_status:
                report += "❌ 定时任务异常\n"
            if large_logs:
                report += f"⚠️ 发现{len(large_logs)}个大日志文件\n"
            
            # 维护信息
            if cleaned_logs > 0:
                report += f"🧹 清理了{cleaned_logs}个旧日志文件\n"
            
            self.logger.info("系统状态检查完成")
            return report, all([db_status, webhook_status, crontab_status])
            
        except Exception as e:
            error_report = f"⚠️ 系统状态检查失败: {str(e)}"
            self.logger.error(f"系统状态检查失败: {e}")
            return error_report, False
    
    def send_status_report(self, report, is_healthy):
        """发送状态报告"""
        try:
            # 只在有问题时发送报告，避免过度通知
            if not is_healthy:
                reporter = UserActivityReporter()
                success = reporter.send_webhook(report)
                
                if success:
                    self.logger.info("状态报告发送成功")
                else:
                    self.logger.error("状态报告发送失败")
                    
                return success
            else:
                self.logger.info("系统状态正常，跳过报告发送")
                return True
                
        except Exception as e:
            self.logger.error(f"发送状态报告失败: {e}")
            return False
    
    def run_monitor(self):
        """运行监控检查"""
        try:
            self.logger.info("开始系统监控...")
            
            # 生成状态报告
            report, is_healthy = self.generate_system_status_report()
            
            # 发送状态报告
            self.send_status_report(report, is_healthy)
            
            self.logger.info("系统监控完成")
            return is_healthy
            
        except Exception as e:
            self.logger.error(f"系统监控失败: {e}")
            return False

def main():
    """主函数"""
    monitor = WebhookMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "health":
            # 健康检查
            success = monitor.run_monitor()
            sys.exit(0 if success else 1)
            
        elif command == "clean":
            # 清理日志
            cleaned = monitor.clean_old_logs()
            print(f"清理了 {cleaned} 个旧日志文件")
            
        elif command == "test":
            # 测试连接
            db_ok = monitor.check_database_connection()
            webhook_ok = monitor.check_webhook_connectivity()
            crontab_ok = monitor.check_crontab_status()
            
            print(f"数据库连接: {'✅' if db_ok else '❌'}")
            print(f"Webhook连接: {'✅' if webhook_ok else '❌'}")
            print(f"定时任务: {'✅' if crontab_ok else '❌'}")
            
            sys.exit(0 if all([db_ok, webhook_ok, crontab_ok]) else 1)
            
        else:
            print("未知命令")
            sys.exit(1)
    else:
        # 默认运行监控
        success = monitor.run_monitor()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()