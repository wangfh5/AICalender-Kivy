# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nlp.text_parser import TextParser
from src.calendar.ics_generator import ICSGenerator

def main():
    # Initialize parser and generator
    parser = TextParser(api_key="sk-f0d7440b9ccc4fdaa077ddb4a5738e4d")
    generator = ICSGenerator()
    
    # Example cases
    examples = [
        # Basic meeting
        "Product review meeting tomorrow at 2pm",
        
        # Meeting with location and time range
        "下周一上午10点到11点半在3楼会议室开项目进展会",
        
        # Meeting with attendees and reminder
        "Budget meeting with Mr. Zhang (zhang@example.com) and Manager Li (li@example.com) at 3pm the day after tomorrow, remind me 30 minutes before",

        # 节假日相关
        "五一节前一天下午2点开会",
        "春节后第一个工作日上午9点开会",
        
        # 特殊时间表达
        "下下周一上午10点开会",
        "本月最后一个工作日下午3点开会",

        # 复杂地点表达
        "Meeting at Starbucks across from the company at 3pm tomorrow",
        "下周三中午12点在西二旗地铁站B口等你"
    ]
    
    print("Current time:", datetime.now(), "\n")
    
    for text in examples:
        print(f"\nInput text: {text}")
        try:
            # Parse text to event data
            event = parser.parse_to_event_data(text)
            
            # Print parsed result
            print("\nParsed result:")
            print(f"Title: {event.summary}")
            print(f"Start: {event.start_time}")
            print(f"End: {event.end_time}")
            print(f"Location: {event.location}")
            print(f"Attendees: {event.attendees}")
            print(f"Reminder: {event.reminder_minutes} minutes before")
            
            # Add event to calendar
            generator.add_event(event)
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Save calendar file
    generator.save("my_calendar.ics")
    print("\nAll events have been saved to my_calendar.ics")

if __name__ == "__main__":
    main() 