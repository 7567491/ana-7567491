#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户活动日报webhook脚本
每日上午10点和晚上10点运行，报告过去24小时用户活动情况
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pymysql
import requests
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from config import DATABASE_CONFIG

# 企业微信Webhook配置
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d3ed6660-1f33-47cc-83dd-84423fc7f8ac"

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/www/wwwroot/ana/webhook.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UserActivityReporter:
    """用户活动报告生成器"""
    
    def __init__(self):
        self.db_config = DATABASE_CONFIG
        self.now = datetime.now()
        self.yesterday = self.now - timedelta(days=1)
        
    def get_db_connection(self):
        """获取数据库连接"""
        try:
            conn = pymysql.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                charset=self.db_config['charset'],
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return None
    
    def execute_query(self, sql, params=None):
        """执行SQL查询"""
        conn = self.get_db_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_new_registrations(self):
        """获取过去24小时新注册用户"""
        sql = """
        SELECT 
            u.uid,
            u.phone,
            u.nickname,
            wu.nickname as wechat_name,
            FROM_UNIXTIME(u.add_time) as register_time
        FROM wy_user u
        LEFT JOIN wy_wechat_user wu ON u.uid = wu.uid
        WHERE u.add_time >= UNIX_TIMESTAMP(%s) 
        AND u.add_time < UNIX_TIMESTAMP(%s)
        ORDER BY u.add_time DESC
        """
        return self.execute_query(sql, [self.yesterday, self.now])
    
    def get_product_purchases(self):
        """获取过去24小时产品购买情况"""
        sql = """
        SELECT 
            sb.uid,
            u.phone,
            wu.nickname as wechat_name,
            s.title as product_name,
            o.pay_price,
            FROM_UNIXTIME(sb.add_time) as purchase_time
        FROM wy_special_buy sb
        JOIN wy_user u ON sb.uid = u.uid
        LEFT JOIN wy_wechat_user wu ON u.uid = wu.uid
        LEFT JOIN wy_special s ON sb.special_id = s.id
        LEFT JOIN wy_store_order o ON sb.order_id = o.order_id
        WHERE sb.add_time >= UNIX_TIMESTAMP(%s)
        AND sb.add_time < UNIX_TIMESTAMP(%s)
        AND sb.is_del = 0
        ORDER BY sb.add_time DESC
        """
        return self.execute_query(sql, [self.yesterday, self.now])
    
    def get_user_logins(self):
        """获取过去24小时老用户登录情况"""
        sql = """
        SELECT 
            u.uid,
            u.phone,
            wu.nickname as wechat_name,
            FROM_UNIXTIME(u.last_time) as last_login_time,
            u.add_time as register_time
        FROM wy_user u
        LEFT JOIN wy_wechat_user wu ON u.uid = wu.uid
        WHERE u.last_time >= UNIX_TIMESTAMP(%s)
        AND u.last_time < UNIX_TIMESTAMP(%s)
        AND u.add_time < UNIX_TIMESTAMP(%s)
        ORDER BY u.last_time DESC
        LIMIT 20
        """
        return self.execute_query(sql, [self.yesterday, self.now, self.yesterday])
    
    def get_course_watching(self):
        """获取过去24小时课程观看情况"""
        sql = """
        SELECT 
            sw.uid,
            u.phone,
            wu.nickname as wechat_name,
            s.title as course_name,
            sw.viewing_time,
            sw.percentage,
            FROM_UNIXTIME(sw.add_time) as watch_time
        FROM wy_special_watch sw
        JOIN wy_user u ON sw.uid = u.uid
        LEFT JOIN wy_wechat_user wu ON u.uid = wu.uid
        LEFT JOIN wy_special s ON sw.special_id = s.id
        WHERE sw.add_time >= UNIX_TIMESTAMP(%s)
        AND sw.add_time < UNIX_TIMESTAMP(%s)
        ORDER BY sw.viewing_time DESC
        LIMIT 20
        """
        return self.execute_query(sql, [self.yesterday, self.now])
    
    def format_user_info(self, user):
        """格式化用户信息"""
        wechat_name = user.get('wechat_name') or '未绑定'
        phone = user.get('phone') or '未填写'
        return f"微信:{wechat_name} 手机:{phone[-4:]if phone != '未填写' else phone}"
    
    def generate_report(self):
        """生成活动报告"""
        try:
            logger.info("开始生成用户活动报告...")
            
            # 获取数据
            new_users = self.get_new_registrations()
            purchases = self.get_product_purchases()
            logins = self.get_user_logins()
            course_watches = self.get_course_watching()
            
            # 生成报告内容
            report_time = self.now.strftime("%m-%d %H:%M")
            report = f"📊 6页网24小时活动报告({report_time})\n"
            
            # 只显示有数据的项目
            has_activity = False
            
            # 新用户注册
            if new_users:
                has_activity = True
                report += f"🆕 新注册{len(new_users)}人："
                for i, user in enumerate(new_users[:2]):  # 最多显示2个
                    report += f"{self.format_user_info(user)}"
                    if i < len(new_users[:2]) - 1:
                        report += ";"
                if len(new_users) > 2:
                    report += f"等{len(new_users)}人"
                report += "\n"
            
            # 产品购买
            if purchases:
                has_activity = True
                total_revenue = sum(p.get('pay_price', 0) for p in purchases if p.get('pay_price'))
                report += f"💰 购买{len(purchases)}笔¥{total_revenue:.0f}："
                for i, purchase in enumerate(purchases[:2]):  # 最多显示2个
                    report += f"{self.format_user_info(purchase)}购买{purchase.get('product_name', '课程')}"
                    if i < len(purchases[:2]) - 1:
                        report += ";"
                if len(purchases) > 2:
                    report += f"等{len(purchases)}笔"
                report += "\n"
            
            # 老用户登录
            if logins:
                has_activity = True
                report += f"👥 活跃{len(logins)}人："
                for i, login in enumerate(logins[:2]):  # 最多显示2个
                    report += f"{self.format_user_info(login)}"
                    if i < len(logins[:2]) - 1:
                        report += ";"
                if len(logins) > 2:
                    report += f"等{len(logins)}人"
                report += "\n"
            
            # 课程观看
            if course_watches:
                has_activity = True
                total_watch_time = sum(c.get('viewing_time', 0) for c in course_watches)
                # 转换观看时长显示：如果超过60分钟显示小时，否则显示分钟
                if total_watch_time > 60:
                    time_display = f"{total_watch_time/60:.1f}小时"
                else:
                    time_display = f"{total_watch_time:.0f}分钟"
                
                report += f"📚 观看{len(course_watches)}次{time_display}："
                for i, watch in enumerate(course_watches[:2]):  # 最多显示2个
                    watch_time = watch.get('viewing_time', 0)
                    if watch_time > 60:
                        time_str = f"{watch_time/60:.1f}小时"
                    else:
                        time_str = f"{watch_time:.0f}分钟"
                    report += f"{self.format_user_info(watch)}看{watch.get('course_name', '课程')}{time_str}"
                    if i < len(course_watches[:2]) - 1:
                        report += ";"
                if len(course_watches) > 2:
                    report += f"等{len(course_watches)}次"
                report += "\n"
            
            # 如果所有数据都为0，显示无活动信息
            if not has_activity:
                report += "暂无新活动"
            else:
                # 去掉最后的换行符
                report = report.rstrip('\n')
                
            logger.info(f"报告生成成功，长度: {len(report)}字符")
            return report
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return f"⚠️ 报告生成失败: {str(e)}"
    
    def send_webhook(self, message):
        """发送企业微信webhook消息"""
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            response = requests.post(WEBHOOK_URL, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    logger.info("Webhook发送成功")
                    return True
                else:
                    logger.error(f"Webhook发送失败: {result}")
                    return False
            else:
                logger.error(f"HTTP请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"发送webhook失败: {e}")
            return False
    
    def save_webhook_log(self, report, success):
        """保存webhook日志到文件"""
        try:
            # 创建webhook-log目录
            log_dir = Path("/www/wwwroot/ana/webhook-log")
            log_dir.mkdir(exist_ok=True)
            
            # 生成日志文件名（按日期）
            log_filename = f"webhook_{self.now.strftime('%Y%m%d')}.log"
            log_file = log_dir / log_filename
            
            # 准备日志内容
            timestamp = self.now.strftime('%Y-%m-%d %H:%M:%S')
            status = "成功" if success else "失败"
            
            log_content = f"""
==========================================
时间: {timestamp}
状态: {status}
内容: 
{report}
==========================================

"""
            
            # 写入日志文件（追加模式）
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_content)
            
            logger.info(f"Webhook日志已保存到: {log_file}")
            
        except Exception as e:
            logger.error(f"保存webhook日志失败: {e}")

    def run(self):
        """运行报告生成和发送"""
        try:
            logger.info("开始执行用户活动日报任务...")
            
            # 生成报告
            report = self.generate_report()
            
            # 发送webhook
            success = self.send_webhook(report)
            
            # 保存日志
            self.save_webhook_log(report, success)
            
            if success:
                logger.info("用户活动日报发送成功")
                print("✅ 用户活动日报发送成功")
            else:
                logger.error("用户活动日报发送失败")
                print("❌ 用户活动日报发送失败")
                
            return success
            
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            print(f"❌ 任务执行失败: {e}")
            return False

def main():
    """主函数"""
    try:
        reporter = UserActivityReporter()
        success = reporter.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        print(f"❌ 程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()