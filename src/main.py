#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from typing import List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nlp.text_parser import TextParser
from src.calendar.ics_generator import ICSGenerator

def get_api_settings() -> dict:
    """获取用户的API设置"""
    print("\n欢迎使用AI日历助手！")
    
    # 获取API Key
    print("请输入您的 API Key (输入内容不会显示在屏幕上)：")
    import getpass
    api_key = getpass.getpass()
    
    # 获取Base URL
    print("\n请输入API的Base URL")
    print("直接回车使用默认值: https://api.openai.com/v1")
    base_url = input("Base URL: ").strip()
    if not base_url:
        base_url = "https://api.openai.com/v1"
    
    # 获取模型名称
    print("\n请输入要使用的模型名称")
    print("直接回车使用默认值: gpt-3.5-turbo")
    model = input("Model: ").strip()
    if not model:
        model = "gpt-3.5-turbo"
    
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model
    }

def get_event_texts() -> List[str]:
    """获取用户输入的日程文本"""
    print("\n请输入您的日程安排。每个日程可以包含多行文本。")
    print("输入 '---' 或 '===' 开始下一个日程")
    print("输入 'done' 或 'exit' 或连续两次回车完成所有输入")
    print("\n示例输入：")
    print("明天下午2点开产品评审会")
    print("需要讨论新功能的设计方案")
    print("---")
    print("下周一上午10点到11点半在3楼会议室开项目进展会")
    print("done")
    print("\n请开始输入您的日程：")
    
    texts = []
    current_text = []
    last_empty = False
    
    while True:
        try:
            line = input()
            line = line.strip()
            
            # 检查是否结束所有输入
            if line.lower() in ['done', 'exit'] or (not line and last_empty):
                if current_text:
                    texts.append('\n'.join(current_text))
                if len(texts) == 0:
                    print("请至少输入一个日程！")
                    current_text = []
                    last_empty = False
                    continue
                break
                
            # 检查是否开始新的日程
            if line in ['---', '===']:
                if current_text:
                    texts.append('\n'.join(current_text))
                    current_text = []
                    last_empty = False
                continue
                
            # 更新空行状态
            last_empty = not line
            
            # 添加当前行到当前日程
            if line:
                current_text.append(line)
                last_empty = False
                
        except KeyboardInterrupt:
            print("\n\n检测到Ctrl+C，结束输入...")
            if current_text:
                texts.append('\n'.join(current_text))
            if len(texts) == 0:
                sys.exit(0)
            break
        except EOFError:
            print("\n\n检测到Ctrl+D，结束输入...")
            if current_text:
                texts.append('\n'.join(current_text))
            if len(texts) == 0:
                sys.exit(0)
            break
    
    return texts

def main():
    try:
        # 获取API设置
        settings = get_api_settings()
        
        # 获取日程文本
        texts = get_event_texts()
        
        print(f"\n收到 {len(texts)} 个日程，开始处理...")
        
        # 初始化解析器和生成器
        parser = TextParser(
            api_key=settings["api_key"],
            base_url=settings["base_url"],
            model=settings["model"]
        )
        generator = ICSGenerator()
        
        # 处理每个日程
        for i, text in enumerate(texts, 1):
            try:
                print(f"\n处理日程 {i}: {text}")
                event = parser.parse_to_event_data(text)
                generator.add_event(event)
                print(f"✓ 日程 {i} 已添加: {event.summary}")
                print(f"  时间: {event.start_time.strftime('%Y-%m-%d %H:%M')} - {event.end_time.strftime('%Y-%m-%d %H:%M')}")
                if event.location:
                    print(f"  地点: {event.location}")
                if event.attendees:
                    print(f"  参与者: {', '.join(event.attendees)}")
                
            except Exception as e:
                print(f"✗ 日程 {i} 处理失败: {str(e)}")
                continue
        
        # 保存日历文件
        output_file = "my_calendar.ics"
        generator.save(output_file)
        print(f"\n✓ 已生成日历文件: {output_file}")
        print("您可以将此文件导入到您的日历软件中（如 Google Calendar、Apple Calendar 等）")
        
    except Exception as e:
        print(f"\n程序出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 