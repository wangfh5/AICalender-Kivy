from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

import os
from src.nlp.text_parser import TextParser
from src.calendar.ics_generator import ICSGenerator

class CalendarApp(App):
    def build(self):
        # Set up the main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Settings layout
        settings_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
        
        # API Key input
        api_key_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        api_key_label = Label(text='API Key:', size_hint_x=0.3)
        self.api_key_input = TextInput(password=True, multiline=False)
        api_key_layout.add_widget(api_key_label)
        api_key_layout.add_widget(self.api_key_input)
        
        # Base URL input
        base_url_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        base_url_label = Label(text='Base URL:', size_hint_x=0.3)
        self.base_url_input = TextInput(
            text='https://api.openai.com/v1',
            multiline=False
        )
        base_url_layout.add_widget(base_url_label)
        base_url_layout.add_widget(self.base_url_input)
        
        # Model name input
        model_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        model_label = Label(text='Model:', size_hint_x=0.3)
        self.model_input = TextInput(
            text='gpt-3.5-turbo',
            multiline=False
        )
        model_layout.add_widget(model_label)
        model_layout.add_widget(self.model_input)
        
        # Add settings to settings layout
        settings_layout.add_widget(api_key_layout)
        settings_layout.add_widget(base_url_layout)
        settings_layout.add_widget(model_layout)
        
        # Event text input
        event_label = Label(text='Event Description:', size_hint_y=None, height=30)
        self.event_input = TextInput(multiline=True)
        
        # Generate button
        self.generate_button = Button(
            text='Generate Calendar',
            size_hint_y=None,
            height=50
        )
        self.generate_button.bind(on_press=self.generate_calendar)
        
        # Status label
        self.status_label = Label(
            text='Ready',
            size_hint_y=None,
            height=30
        )
        
        # Add widgets to layout
        layout.add_widget(settings_layout)
        layout.add_widget(event_label)
        layout.add_widget(self.event_input)
        layout.add_widget(self.generate_button)
        layout.add_widget(self.status_label)
        
        return layout
    
    def generate_calendar(self, instance):
        # Disable button and show loading state
        self.generate_button.disabled = True
        self.status_label.text = 'Processing...'
        
        # Get input values
        api_key = self.api_key_input.text
        event_text = self.event_input.text
        
        if not api_key or not event_text:
            self.status_label.text = 'Please enter both API key and event description'
            self.generate_button.disabled = False
            return
        
        # Schedule the actual processing to avoid blocking the UI
        Clock.schedule_once(lambda dt: self.process_calendar(api_key, event_text))
    
    def process_calendar(self, api_key, event_text):
        try:
            # Initialize parser and generator
            parser = TextParser(
                api_key=api_key,
                base_url=self.base_url_input.text,
                model=self.model_input.text
            )
            generator = ICSGenerator()
            
            # Parse event text
            event = parser.parse_to_event_data(event_text)
            
            # Generate ICS file
            if android:
                # For Android, save to app-specific storage
                from android.storage import app_storage_path
                calendar_path = os.path.join(app_storage_path(), 'my_calendar.ics')
            else:
                # For desktop, save to current directory
                calendar_path = 'my_calendar.ics'
            
            # Add events and save to file
            generator.add_event(event)
            generator.save(calendar_path)
            
            self.status_label.text = f'Calendar saved to {calendar_path}'
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'
        finally:
            self.generate_button.disabled = False

if __name__ == '__main__':
    try:
        import android
    except ImportError:
        android = None
    
    Window.clearcolor = (0.9, 0.9, 0.9, 1)  # Light gray background
    CalendarApp().run()