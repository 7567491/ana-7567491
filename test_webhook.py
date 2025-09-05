#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webhook.py的测试脚本
使用基于测试的开发方法验证各项功能
"""

import sys
import os
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# 添加项目路径到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from webhook import UserActivityReporter
except ImportError as e:
    print(f"导入webhook模块失败: {e}")
    sys.exit(1)

class TestUserActivityReporter(unittest.TestCase):
    """用户活动报告器测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.reporter = UserActivityReporter()
        
        # 模拟测试数据
        self.mock_new_users = [
            {'uid': 1, 'phone': '13800138001', 'nickname': 'test1', 'wechat_name': '微信用户1', 'register_time': datetime.now()},
            {'uid': 2, 'phone': '13800138002', 'nickname': 'test2', 'wechat_name': '微信用户2', 'register_time': datetime.now()}
        ]
        
        self.mock_purchases = [
            {'uid': 1, 'phone': '13800138001', 'wechat_name': '微信用户1', 'product_name': '课程A', 'pay_price': 99.0, 'purchase_time': datetime.now()},
            {'uid': 2, 'phone': '13800138002', 'wechat_name': '微信用户2', 'product_name': '课程B', 'pay_price': 199.0, 'purchase_time': datetime.now()}
        ]
        
        self.mock_logins = [
            {'uid': 3, 'phone': '13800138003', 'wechat_name': '老用户1', 'last_login_time': datetime.now(), 'register_time': 1640995200}
        ]
        
        self.mock_course_watches = [
            {'uid': 1, 'phone': '13800138001', 'wechat_name': '微信用户1', 'course_name': '课程A', 'viewing_time': 30.5, 'percentage': 80.0, 'watch_time': datetime.now()}
        ]
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.reporter.db_config)
        self.assertIsInstance(self.reporter.now, datetime)
        self.assertIsInstance(self.reporter.yesterday, datetime)
        
    def test_format_user_info(self):
        """测试用户信息格式化"""
        user1 = {'wechat_name': '张三', 'phone': '13800138001'}
        result1 = self.reporter.format_user_info(user1)
        self.assertEqual(result1, "微信:张三 手机:8001")
        
        user2 = {'wechat_name': None, 'phone': None}
        result2 = self.reporter.format_user_info(user2)
        self.assertEqual(result2, "微信:未绑定 手机:未填写")
        
        user3 = {'wechat_name': '李四', 'phone': ''}
        result3 = self.reporter.format_user_info(user3)
        self.assertEqual(result3, "微信:李四 手机:未填写")
    
    @patch('webhook.UserActivityReporter.execute_query')
    def test_get_new_registrations(self, mock_execute_query):
        """测试获取新注册用户"""
        mock_execute_query.return_value = self.mock_new_users
        
        result = self.reporter.get_new_registrations()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['uid'], 1)
        mock_execute_query.assert_called_once()
    
    @patch('webhook.UserActivityReporter.execute_query')
    def test_get_product_purchases(self, mock_execute_query):
        """测试获取产品购买"""
        mock_execute_query.return_value = self.mock_purchases
        
        result = self.reporter.get_product_purchases()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['pay_price'], 99.0)
        mock_execute_query.assert_called_once()
    
    @patch('webhook.UserActivityReporter.execute_query')
    def test_get_user_logins(self, mock_execute_query):
        """测试获取用户登录"""
        mock_execute_query.return_value = self.mock_logins
        
        result = self.reporter.get_user_logins()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['uid'], 3)
        mock_execute_query.assert_called_once()
    
    @patch('webhook.UserActivityReporter.execute_query')
    def test_get_course_watching(self, mock_execute_query):
        """测试获取课程观看"""
        mock_execute_query.return_value = self.mock_course_watches
        
        result = self.reporter.get_course_watching()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['viewing_time'], 30.5)
        mock_execute_query.assert_called_once()
    
    @patch('webhook.UserActivityReporter.get_course_watching')
    @patch('webhook.UserActivityReporter.get_user_logins')
    @patch('webhook.UserActivityReporter.get_product_purchases')
    @patch('webhook.UserActivityReporter.get_new_registrations')
    def test_generate_report(self, mock_new_users, mock_purchases, mock_logins, mock_watches):
        """测试报告生成"""
        # 设置mock返回值
        mock_new_users.return_value = self.mock_new_users
        mock_purchases.return_value = self.mock_purchases
        mock_logins.return_value = self.mock_logins
        mock_watches.return_value = self.mock_course_watches
        
        report = self.reporter.generate_report()
        
        # 验证报告内容
        self.assertIsInstance(report, str)
        self.assertIn("6页网24小时用户活动报告", report)
        self.assertIn("新注册用户：2人", report)
        self.assertIn("产品购买：2笔", report)
        self.assertIn("活跃老用户：1人登录", report)
        self.assertIn("课程观看：1次", report)
        
        # 验证报告长度限制（应该控制在合理范围内）
        self.assertLessEqual(len(report), 500)  # 允许一些缓冲，但不应该过长
    
    @patch('webhook.UserActivityReporter.get_course_watching')
    @patch('webhook.UserActivityReporter.get_user_logins') 
    @patch('webhook.UserActivityReporter.get_product_purchases')
    @patch('webhook.UserActivityReporter.get_new_registrations')
    def test_generate_report_empty_data(self, mock_new_users, mock_purchases, mock_logins, mock_watches):
        """测试空数据情况下的报告生成"""
        # 设置空数据
        mock_new_users.return_value = []
        mock_purchases.return_value = []
        mock_logins.return_value = []
        mock_watches.return_value = []
        
        report = self.reporter.generate_report()
        
        # 验证空数据报告
        self.assertIn("新注册用户：0人", report)
        self.assertIn("产品购买：0笔", report)
        self.assertIn("活跃老用户：0人", report)
        self.assertIn("课程观看：0次", report)
    
    @patch('requests.post')
    def test_send_webhook_success(self, mock_post):
        """测试webhook发送成功"""
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'errcode': 0, 'errmsg': 'ok'}
        mock_post.return_value = mock_response
        
        result = self.reporter.send_webhook("测试消息")
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_webhook_failure(self, mock_post):
        """测试webhook发送失败"""
        # 模拟失败响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'errcode': 40001, 'errmsg': 'invalid key'}
        mock_post.return_value = mock_response
        
        result = self.reporter.send_webhook("测试消息")
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_send_webhook_http_error(self, mock_post):
        """测试HTTP错误"""
        # 模拟HTTP错误
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        result = self.reporter.send_webhook("测试消息")
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_send_webhook_exception(self, mock_post):
        """测试异常处理"""
        # 模拟异常
        mock_post.side_effect = Exception("网络错误")
        
        result = self.reporter.send_webhook("测试消息")
        self.assertFalse(result)

class TestDatabaseConnection(unittest.TestCase):
    """数据库连接测试"""
    
    def setUp(self):
        self.reporter = UserActivityReporter()
    
    def test_database_connection_config(self):
        """测试数据库配置"""
        self.assertEqual(self.reporter.db_config['host'], 'localhost')
        self.assertEqual(self.reporter.db_config['user'], '6page')
        self.assertEqual(self.reporter.db_config['database'], '6page')
        self.assertEqual(self.reporter.db_config['charset'], 'utf8mb4')
    
    def test_get_db_connection_real(self):
        """测试实际数据库连接"""
        try:
            conn = self.reporter.get_db_connection()
            if conn:
                self.assertIsNotNone(conn)
                conn.close()
                print("✅ 数据库连接测试成功")
            else:
                print("⚠️ 数据库连接失败，请检查配置")
        except Exception as e:
            print(f"⚠️ 数据库连接异常: {e}")

def run_integration_test():
    """集成测试 - 测试实际的webhook发送"""
    print("\n" + "="*50)
    print("开始集成测试...")
    print("="*50)
    
    try:
        reporter = UserActivityReporter()
        
        # 测试数据库连接
        print("1. 测试数据库连接...")
        conn = reporter.get_db_connection()
        if conn:
            print("   ✅ 数据库连接成功")
            conn.close()
        else:
            print("   ❌ 数据库连接失败")
            return False
        
        # 测试查询功能
        print("2. 测试数据查询功能...")
        try:
            new_users = reporter.get_new_registrations()
            purchases = reporter.get_product_purchases() 
            logins = reporter.get_user_logins()
            watches = reporter.get_course_watching()
            print(f"   ✅ 查询成功 - 新用户:{len(new_users)}, 购买:{len(purchases)}, 登录:{len(logins)}, 观看:{len(watches)}")
        except Exception as e:
            print(f"   ❌ 查询失败: {e}")
            return False
        
        # 测试报告生成
        print("3. 测试报告生成...")
        try:
            report = reporter.generate_report()
            print(f"   ✅ 报告生成成功，长度: {len(report)}字符")
            print("   报告预览:")
            print("   " + "\n   ".join(report.split("\n")[:5]))  # 显示前5行
        except Exception as e:
            print(f"   ❌ 报告生成失败: {e}")
            return False
        
        # 测试webhook发送（使用测试消息）
        print("4. 测试Webhook发送...")
        test_message = f"🧪 Webhook测试消息\n⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ 系统运行正常"
        try:
            success = reporter.send_webhook(test_message)
            if success:
                print("   ✅ Webhook发送成功")
            else:
                print("   ❌ Webhook发送失败")
                return False
        except Exception as e:
            print(f"   ❌ Webhook发送异常: {e}")
            return False
        
        print("\n🎉 集成测试完成！所有功能正常运行")
        return True
        
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始webhook.py功能测试...")
    print("="*50)
    
    # 运行单元测试
    print("1. 运行单元测试...")
    unittest_loader = unittest.TestLoader()
    unittest_suite = unittest.TestSuite()
    
    # 添加测试用例
    unittest_suite.addTest(unittest_loader.loadTestsFromTestCase(TestUserActivityReporter))
    unittest_suite.addTest(unittest_loader.loadTestsFromTestCase(TestDatabaseConnection))
    
    # 运行测试
    unittest_runner = unittest.TextTestRunner(verbosity=2)
    unittest_result = unittest_runner.run(unittest_suite)
    
    # 单元测试结果
    if unittest_result.wasSuccessful():
        print("\n✅ 单元测试通过")
    else:
        print(f"\n❌ 单元测试失败 - 失败:{len(unittest_result.failures)}, 错误:{len(unittest_result.errors)}")
    
    # 运行集成测试
    print("\n2. 运行集成测试...")
    integration_success = run_integration_test()
    
    # 总结
    print("\n" + "="*50)
    print("测试总结:")
    print(f"  单元测试: {'通过' if unittest_result.wasSuccessful() else '失败'}")
    print(f"  集成测试: {'通过' if integration_success else '失败'}")
    
    if unittest_result.wasSuccessful() and integration_success:
        print("\n🎉 所有测试通过！webhook.py准备就绪")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查问题后重试")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)