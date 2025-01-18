# -*- coding: utf-8 -*-

import sys
import os
import unittest
from datetime import datetime
import pytz

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nlp.text_parser import TextParser
from src.calendar.ics_generator import ICSGenerator

class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.parser = TextParser(api_key="sk-f0d7440b9ccc4fdaa077ddb4a5738e4d")
        cls.generator = ICSGenerator()
        
    def setUp(self):
        """Reset generator before each test"""
        self.generator.clear()
    
    def test_english_basic(self):
        """Test basic English inputs"""
        test_cases = [
            "tomorrow at 3pm meeting with Zhang San about project progress",
            "next Monday 9:30am weekly standup meeting",
            "meeting with clients from 3pm to 4:30pm today in Room 2A",
        ]
        
        for text in test_cases:
            event = self.parser.parse_to_event_data(text)
            self.assertIsNotNone(event.summary)
            self.assertIsNotNone(event.start_time)
            self.assertIsNotNone(event.end_time)
            
    def test_english_advanced(self):
        """Test advanced English inputs"""
        test_cases = [
            "important presentation at 4pm tomorrow in main hall, remind me 1 hour before",
            "project review with john@example.com and mary@example.com next Tuesday 2pm",
            "quarterly review meeting on Jan 31st from 9am to 12pm in Room 3B with department heads, set 45min reminder",
        ]
        
        for text in test_cases:
            event = self.parser.parse_to_event_data(text)
            self.assertIsNotNone(event.summary)
            self.assertIsNotNone(event.start_time)
            self.assertIsNotNone(event.end_time)
    
    def test_chinese_basic(self):
        """Test basic Chinese inputs"""
        test_cases = [
            "明天上午10点和产品部开需求评审会",
            "下周二下午2点半在3楼会议室和客户开项目进展会",
            "后天下午3点到5点在腾讯会议和开发团队开代码评审",
        ]
        
        for text in test_cases:
            event = self.parser.parse_to_event_data(text)
            self.assertIsNotNone(event.summary)
            self.assertIsNotNone(event.start_time)
            self.assertIsNotNone(event.end_time)
    
    def test_chinese_advanced(self):
        """Test advanced Chinese inputs"""
        test_cases = [
            "明天下午3点要去面试，地点是中关村软件园，提前1小时提醒",
            "明天上午11点和李总(lz@example.com)、王经理(wjl@example.com)开会讨论预算",
            "五一节前一天下午2点开总结会",
        ]
        
        for text in test_cases:
            event = self.parser.parse_to_event_data(text)
            self.assertIsNotNone(event.summary)
            self.assertIsNotNone(event.start_time)
            self.assertIsNotNone(event.end_time)
    
    def test_special_cases(self):
        """Test special cases and edge cases"""
        test_cases = [
            # 节假日相关
            "五一节前一天下午2点开会",
            "春节后第一个工作日上午9点开会",
            
            # 特殊时间表达
            "下下周一上午10点开会",
            "本月最后一个工作日下午3点开会",
            
            # 复杂地点表达
            "明天下午3点在公司对面的星巴克见面",
            "下周三中午12点在西二旗地铁站B口等你",
        ]
        
        for text in test_cases:
            try:
                event = self.parser.parse_to_event_data(text)
                self.assertIsNotNone(event.summary)
                self.assertIsNotNone(event.start_time)
                self.assertIsNotNone(event.end_time)
            except Exception as e:
                self.fail(f"Failed to parse: {text}, error: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling"""
        test_cases = [
            "",  # 空字符串
            "明天",  # 缺少具体时间
            "约你吃饭",  # 缺少时间信息
            "2024-01-01",  # 仅日期无具体事件
        ]
        
        for text in test_cases:
            with self.assertRaises(Exception):
                self.parser.parse_to_event_data(text)

if __name__ == '__main__':
    unittest.main() 