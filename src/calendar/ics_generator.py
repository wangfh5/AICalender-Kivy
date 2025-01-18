# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from icalendar import Calendar, Event, Alarm
import pytz
from typing import Optional, List, Dict, Union
from dataclasses import dataclass

@dataclass
class EventData:
    """Event data structure for calendar events"""
    summary: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    description: Optional[str] = None
    attendees: Optional[List[str]] = None
    reminder_minutes: Optional[int] = 15

class ICSGenerator:
    """ICS file generator for calendar events"""
    
    def __init__(self, timezone: str = 'Asia/Shanghai'):
        """Initialize the generator with specified timezone"""
        self.timezone = pytz.timezone(timezone)
        self.calendar = Calendar()
        self.calendar.add('prodid', '-//AI Calendar Assistant//aicalendar.example.com//')
        self.calendar.add('version', '2.0')
        
    def create_event(self, event_data: EventData) -> Event:
        """Create a calendar event from EventData"""
        event = Event()
        
        # Add basic info
        event.add('summary', event_data.summary)
        
        # Handle time
        start_time = self.timezone.localize(event_data.start_time)
        end_time = self.timezone.localize(event_data.end_time)
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        
        # Add optional info
        if event_data.location:
            event.add('location', event_data.location)
        if event_data.description:
            event.add('description', event_data.description)
            
        # Add attendees
        if event_data.attendees:
            for attendee in event_data.attendees:
                event.add('attendee', f'mailto:{attendee}')
                
        # Add reminder
        if event_data.reminder_minutes is not None:
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('trigger', timedelta(minutes=-event_data.reminder_minutes))
            alarm.add('description', f'Reminder for {event_data.summary}')
            event.add_component(alarm)
            
        return event
    
    def add_event(self, event_data: EventData) -> None:
        """Add an event to the calendar"""
        event = self.create_event(event_data)
        self.calendar.add_component(event)
        
    def add_events(self, events_data: List[EventData]) -> None:
        """Add multiple events to the calendar"""
        for event_data in events_data:
            self.add_event(event_data)
            
    def save(self, filename: str) -> None:
        """Save the calendar to an ICS file"""
        with open(filename, 'wb') as f:
            f.write(self.calendar.to_ical())
            
    def clear(self) -> None:
        """Clear all events from the calendar"""
        self.calendar = Calendar()
        self.calendar.add('prodid', '-//AI Calendar Assistant//aicalendar.example.com//')
        self.calendar.add('version', '2.0') 