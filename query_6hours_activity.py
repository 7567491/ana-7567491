# -*- coding: utf-8 -*-
"""
查询过去6小时用户活动数据
包括：新用户注册、产品购买、老用户登录、课程观看等信息
"""
import pymysql
import sys
import os
from datetime import datetime, timedelta
import json

# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': '6page',
    'password': '5NsFLLBFFsnZb3fh',
    'database': '6page',
    'charset': 'utf8mb4'
}

class SixHoursActivityQuery:
    def __init__(self):
        self.config = DATABASE_CONFIG
        
    def get_connection(self):
        return pymysql.connect(
            host=self.config['host'],
            port=self.config['port'],
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database'],
            charset=self.config['charset'],
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def execute_query(self, sql, params=None):
        """执行查询并返回结果"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"查询出错: {e}")
            return []
        finally:
            conn.close()
    
    def get_new_registrations(self):
        """查询过去6小时新用户注册"""
        sql = """
        SELECT 
            u.uid,
            u.nickname as user_name,
            u.phone,
            FROM_UNIXTIME(u.add_time) as register_time,
            CASE 
                WHEN wu.openid IS NOT NULL THEN '微信注册'
                ELSE '手机注册'
            END as register_type,
            wu.nickname as wechat_name
        FROM wy_user u
        LEFT JOIN wy_wechat_user wu ON u.uid = wu.uid
        WHERE u.add_time > UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 6 HOUR))
        AND u.status = 1
        ORDER BY u.add_time DESC
        """
        return self.execute_query(sql)
    
    def get_product_purchases(self):
        """查询过去6小时产品购买"""
        sql = """
        SELECT 
            o.uid,
            u.nickname as user_name,
            u.phone,
            wu.nickname as wechat_name,
            o.order_id,
            o.pay_price,
            FROM_UNIXTIME(o.add_time) as purchase_time,
            GROUP_CONCAT(DISTINCT s.title ORDER BY s.title SEPARATOR ', ') as products
        FROM wy_store_order o
        LEFT JOIN wy_user u ON o.uid = u.uid
        LEFT JOIN wy_wechat_user wu ON u.uid = wu.uid
        LEFT JOIN wy_store_order_cart_info ci ON o.id = ci.oid
        LEFT JOIN wy_special s ON ci.product_id = s.id
        WHERE o.paid = 1 
        AND o.add_time > UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 6 HOUR))
        GROUP BY o.id, o.uid, u.nickname, u.phone, wu.nickname, o.order_id, o.pay_price, o.add_time
        ORDER BY o.add_time DESC
        """
        return self.execute_query(sql)
    
    def get_user_logins(self):
        """查询过去6小时老用户登录（基于last_time更新）"""
        sql = """
        SELECT 
            u.uid,
            u.nickname as user_name,
            u.phone,
            wu.nickname as wechat_name,
            FROM_UNIXTIME(u.last_time) as last_login_time,
            FROM_UNIXTIME(u.add_time) as register_time,
            DATEDIFF(NOW(), FROM_UNIXTIME(u.add_time)) as register_days_ago
        FROM wy_user u
        LEFT JOIN wy_wechat_user wu ON u.uid = wu.uid
        WHERE u.last_time > UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 6 HOUR))
        AND u.add_time < UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 1 DAY))  -- 排除新用户
        AND u.status = 1
        ORDER BY u.last_time DESC
        """
        return self.execute_query(sql)
    
    def get_course_watching(self):
        """查询过去6小时课程观看"""
        sql = """
        SELECT 
            sw.uid,
            u.nickname as user_name,
            u.phone,
            wu.nickname as wechat_name,
            s.title as course_name,
            sw.viewing_time as watch_duration_minutes,
            sw.percentage as completion_percentage,
            FROM_UNIXTIME(sw.add_time) as watch_start_time,
            CASE 
                WHEN sw.is_complete = 1 THEN '已完成'
                ELSE '观看中'
            END as watch_status
        FROM wy_special_watch sw
        LEFT JOIN wy_user u ON sw.uid = u.uid
        LEFT JOIN wy_wechat_user wu ON u.uid = wu.uid
        LEFT JOIN wy_special s ON sw.special_id = s.id
        WHERE sw.add_time > UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 6 HOUR))
        AND u.status = 1
        AND s.is_del = 0
        ORDER BY sw.add_time DESC
        """
        return self.execute_query(sql)
    
    def format_results(self):
        """格式化并输出所有结果"""
        current_time = datetime.now()
        six_hours_ago = current_time - timedelta(hours=6)
        
        print(f"\n=== 6页网用户活动报告 ===")
        print(f"查询时间范围: {six_hours_ago.strftime('%Y-%m-%d %H:%M:%S')} 至 {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 新用户注册
        new_users = self.get_new_registrations()
        print(f"\n【新用户注册】共 {len(new_users)} 人")
        print("-" * 60)
        if new_users:
            for user in new_users:
                wechat_info = f"微信名: {user['wechat_name']}" if user['wechat_name'] else "无微信信息"
                print(f"用户ID: {user['uid']} | 昵称: {user['user_name']} | 手机: {user['phone'] or '未绑定'}")
                print(f"注册方式: {user['register_type']} | {wechat_info}")
                print(f"注册时间: {user['register_time']}")
                print("-" * 40)
        else:
            print("暂无新用户注册")
        
        # 2. 产品购买
        purchases = self.get_product_purchases()
        print(f"\n【产品购买】共 {len(purchases)} 笔订单")
        print("-" * 60)
        if purchases:
            total_amount = sum(float(p['pay_price'] or 0) for p in purchases)
            for purchase in purchases:
                wechat_info = f"微信名: {purchase['wechat_name']}" if purchase['wechat_name'] else "无微信信息"
                print(f"用户ID: {purchase['uid']} | 昵称: {purchase['user_name']} | 手机: {purchase['phone'] or '未绑定'}")
                print(f"{wechat_info}")
                print(f"订单号: {purchase['order_id']} | 金额: ¥{purchase['pay_price']}")
                print(f"购买产品: {purchase['products'] or '未知产品'}")
                print(f"购买时间: {purchase['purchase_time']}")
                print("-" * 40)
            print(f"总收入: ¥{total_amount:.2f}")
        else:
            print("暂无产品购买")
        
        # 3. 老用户登录
        logins = self.get_user_logins()
        print(f"\n【老用户登录】共 {len(logins)} 人")
        print("-" * 60)
        if logins:
            for login in logins:
                wechat_info = f"微信名: {login['wechat_name']}" if login['wechat_name'] else "无微信信息"
                print(f"用户ID: {login['uid']} | 昵称: {login['user_name']} | 手机: {login['phone'] or '未绑定'}")
                print(f"{wechat_info}")
                print(f"最后登录: {login['last_login_time']} | 注册于 {login['register_days_ago']} 天前")
                print("-" * 40)
        else:
            print("暂无老用户登录")
        
        # 4. 课程观看
        watching = self.get_course_watching()
        print(f"\n【课程观看】共 {len(watching)} 次观看")
        print("-" * 60)
        if watching:
            total_watch_time = sum(float(w['watch_duration_minutes'] or 0) for w in watching)
            for watch in watching:
                wechat_info = f"微信名: {watch['wechat_name']}" if watch['wechat_name'] else "无微信信息"
                print(f"用户ID: {watch['uid']} | 昵称: {watch['user_name']} | 手机: {watch['phone'] or '未绑定'}")
                print(f"{wechat_info}")
                print(f"观看课程: {watch['course_name']}")
                print(f"观看时长: {watch['watch_duration_minutes'] or 0} 分钟 | 完成度: {watch['completion_percentage'] or 0:.1f}%")
                print(f"状态: {watch['watch_status']} | 开始时间: {watch['watch_start_time']}")
                print("-" * 40)
            print(f"总观看时长: {total_watch_time:.1f} 分钟 ({total_watch_time/60:.1f} 小时)")
        else:
            print("暂无课程观看记录")
        
        # 汇总信息
        print(f"\n=== 活动汇总 ===")
        print(f"新注册用户: {len(new_users)} 人")
        print(f"产品购买: {len(purchases)} 笔订单")
        print(f"老用户登录: {len(logins)} 人")
        print(f"课程观看: {len(watching)} 次")
        print("=" * 80)

if __name__ == "__main__":
    try:
        query = SixHoursActivityQuery()
        query.format_results()
    except Exception as e:
        print(f"执行出错: {e}")
        sys.exit(1)