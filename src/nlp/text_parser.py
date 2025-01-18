# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from openai import OpenAI
import pytz
import time
from json.decoder import JSONDecodeError

# ������־
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ParsingError(Exception):
    """Custom exception for parsing errors"""
    pass

def get_system_prompt(current_date: str) -> str:
    """Generate system prompt with current date"""
    return f"""You are a calendar event parsing assistant. Your task is to extract event information from natural language descriptions.

Please extract the following information in JSON format:
{{
    "summary": "Event title",
    "start_time": "YYYY-MM-DD HH:mm",
    "end_time": "YYYY-MM-DD HH:mm",
    "location": "Location",
    "description": "Detailed event information, excluding time/location/basic attendee info that are covered by other fields",
    "attendees": ["attendee1@email.com", "attendee2@email.com"],
    "reminder_minutes": reminder time in minutes
}}

Today's date is {current_date}.

2025年节假日调休安排：
- 元旦：2024-12-30 至 2025-01-01，共3天
- 春节：2025-01-28 至 2025-02-04，共8天
- 清明节：2025-04-05 至 2025-04-07，共3天
- 劳动节：2025-05-01 至 2025-05-05，共5天
- 端午节：2025-05-31 至 2025-06-02，共3天
- 中秋节：2025-10-06，共1天（与国庆节连休）
- 国庆节：2025-10-01 至 2025-10-08，共8天

Rules:
1. Language matching (IMPORTANT):
   - For Chinese input (contains any Chinese characters), MUST output summary and description in Chinese
   - For English input (no Chinese characters), output summary and description in English
   - Examples for Chinese input:
     - Input: "明天下午3点在星巴克见面" -> summary: "星巴克见面"
     - Input: "下周一开产品评审会" -> summary: "产品评审会"
   - Examples for English input:
     - Input: "meeting tomorrow 3pm" -> summary: "Meeting"
     - Input: "product review next Monday" -> summary: "Product Review"

2. Time parsing rules:
   - "today" refers to {current_date}
   - "tomorrow" means the next day
   - "next Monday" means the next occurring Monday
   - For dates like "Jan 25th", assume it's in the current year unless specified
   - If only time is given without date, assume today ({current_date})
   - Parse all times to 24-hour format (e.g., "2pm" -> "14:00")
   - For morning/afternoon without specific time: morning = 9:00, afternoon = 14:00

3. Duration rules:
   - If no end time is specified, assume the event lasts for 1 hour
   - For "lunch" or "dinner" without specified duration, assume 1.5 hours
   - For "meeting" without specified duration, assume 1 hour

4. Location handling:
   - If no location is specified, return null
   - Keep the exact location name as provided
   - For online meetings without specific location, use "Online" for English, "线上" for Chinese

5. Attendee rules:
   - Extract all email addresses as attendees
   - If no attendees are specified, return empty list
   - Include any email addresses mentioned in the description

6. Reminder rules:
   - Default reminder is 15 minutes before
   - Parse explicit reminder times (e.g., "remind me 1 hour before" -> 60)
   - For important meetings/presentations, set default reminder to 30 minutes

7. Title and description:
   - Make the summary concise but informative
   - Include the meeting type (e.g., "Team Meeting"/"团队会议", "Client Meeting"/"客户会议")
   - For description, preserve all important details while improving readability:
     - Keep all event-specific information (abstract, agenda, biography, etc.)
     - Preserve technical details (meeting links, IDs, passwords, etc.)
     - Remove only information that's already covered by other fields (time, location, basic attendee list)
     - Format the text for better readability (add line breaks, sections, etc.)
     - Chinese example:
       Input: "明天下午3点在星巴克见面，讨论新项目方案。具体议程：1. 项目背景介绍 2. 技术方案讨论 3. 时间节点确认。腾讯会议：888 999 000，密码：1234"
       Description: "议程：
1. 项目背景介绍
2. 技术方案讨论
3. 时间节点确认

腾讯会议：888 999 000
密码：1234"
     - English example:
       Input: "Prof. Smith's seminar on Quantum Computing. Abstract: This talk introduces recent developments in quantum error correction. We will discuss the surface code and its implementation on superconducting circuits. Join via Zoom: https://zoom.us/j/123456, Passcode: qc2024"
       Description: "Speaker: Prof. Smith

Abstract:
This talk introduces recent developments in quantum error correction. We will discuss the surface code and its implementation on superconducting circuits.

Meeting Link:
Zoom: https://zoom.us/j/123456
Passcode: qc2024"

Return only the JSON result without any additional text."""

class TextParser:
    """Parse natural language text into calendar event data"""
    
    def __init__(self, api_key: str, timezone: str = 'Asia/Shanghai', max_retries: int = 3):
        """Initialize the parser with API key and timezone"""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.timezone = pytz.timezone(timezone)
        self.max_retries = max_retries
        
    def _call_api(self, messages: list, retry_count: int = 0) -> Dict[str, Any]:
        """Call the API with retry mechanism"""
        try:
            logger.info(f"Calling API (attempt {retry_count + 1})")
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False
            )
            content = response.choices[0].message.content
            logger.debug(f"API Response: {content}")
            
            try:
                return json.loads(content)
            except JSONDecodeError as e:
                logger.warning(f"JSON parsing error: {str(e)}")
                logger.warning(f"Raw response: {content}")
                if retry_count < self.max_retries:
                    logger.info(f"Retrying... ({retry_count + 1}/{self.max_retries})")
                    time.sleep(1)  # ���Ӷ����ӳٱ����������
                    return self._call_api(messages, retry_count + 1)
                raise ParsingError(f"Failed to parse JSON after {self.max_retries} attempts")
                
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying... ({retry_count + 1}/{self.max_retries})")
                time.sleep(1)
                return self._call_api(messages, retry_count + 1)
            raise ParsingError(f"API call failed after {self.max_retries} attempts: {str(e)}")
    
    def parse_text(self, text: str) -> Dict[str, Any]:
        """Parse natural language text into event data"""
        logger.info(f"Parsing text: {text}")
        
        # Validate input text
        if not text or not text.strip():
            raise ParsingError("Empty or invalid input text")
            
        # Check for minimum required information
        text = text.strip()
        if len(text) < 3:  # Set minimum length requirement
            raise ParsingError("Input text too short")
            
        # Check for time-related information
        time_indicators = [
            # English time indicators
            'today', 'tomorrow', 'next',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'am', 'pm', ':', 'at',
            'morning', 'afternoon', 'evening',
            
            # Chinese time indicators
            '点', '分', '早上', '上午', '中午', '下午', '晚上', '傍晚',
            '今天', '明天', '后天', '大后天',
            '周一', '周二', '周三', '周四', '周五', '周六', '周日',
            '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日',
            '下周', '下下周', '这周', '本周',
            '月', '年', '日',
            '过', '到', '从'
        ]
        
        has_time_info = any(indicator in text for indicator in time_indicators)
        if not has_time_info:
            raise ParsingError("No time information found in input text")
            
        # Get current date in the specified timezone
        now = datetime.now(self.timezone)
        current_date = now.strftime('%Y-%m-%d')
        
        messages = [
            {"role": "system", "content": get_system_prompt(current_date)},
            {"role": "user", "content": text}
        ]
        
        result = self._call_api(messages)
        
        # Validate required fields
        required_fields = ['summary', 'start_time']
        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            raise ParsingError(f"Missing required fields: {', '.join(missing_fields)}")
        
        try:
            # Validate date format
            datetime.strptime(result['start_time'], '%Y-%m-%d %H:%M')
            if 'end_time' in result:
                datetime.strptime(result['end_time'], '%Y-%m-%d %H:%M')
        except ValueError as e:
            raise ParsingError(f"Invalid datetime format: {str(e)}")
        
        # If no end time is specified, set it to 1 hour after start time
        if not result.get('end_time'):
            start_time = datetime.strptime(result['start_time'], '%Y-%m-%d %H:%M')
            result['end_time'] = (start_time + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
            
        # Set other default values
        result.setdefault('location', None)
        result.setdefault('description', text)
        result.setdefault('attendees', [])
        result.setdefault('reminder_minutes', 15)
        
        logger.info("Successfully parsed text")
        logger.debug(f"Parsing result: {result}")
        
        return result
        
    def parse_to_event_data(self, text: str) -> 'EventData':
        """Parse text and return EventData object"""
        from src.calendar.ics_generator import EventData
        
        try:
            result = self.parse_text(text)
            
            # Convert time strings to datetime objects
            start_time = datetime.strptime(result['start_time'], '%Y-%m-%d %H:%M')
            end_time = datetime.strptime(result['end_time'], '%Y-%m-%d %H:%M')
            
            return EventData(
                summary=result['summary'],
                start_time=start_time,
                end_time=end_time,
                location=result['location'],
                description=result['description'],
                attendees=result['attendees'],
                reminder_minutes=result['reminder_minutes']
            )
        except Exception as e:
            logger.error(f"Error creating EventData: {str(e)}")
            raise 