"""
??? ??? ?? ????
UTC? ??? ??(ICT, UTC+7) ?? ?? ?? ??
"""

import pytz
from datetime import datetime, timezone, timedelta
from typing import Optional, Union

class VietnamTimezoneHandler:
    '''??? ??? ?? ???'''
    
    def __init__(self):
        self.vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')  # ICT, UTC+7
        self.utc_tz = pytz.UTC
    
    def get_vietnam_now(self) -> datetime:
        '''??? ?? ?? ??'''
        return datetime.now(self.vietnam_tz)
    
    def to_vietnam_time(self, utc_datetime: Union[str, datetime]) -> datetime:
        '''UTC ??? ??? ???? ??'''
        if isinstance(utc_datetime, str):
            try:
                if 'T' in utc_datetime and '+' in utc_datetime:
                    utc_datetime = datetime.fromisoformat(utc_datetime.replace('Z', '+00:00'))
                elif utc_datetime.endswith('Z'):
                    utc_datetime = datetime.fromisoformat(utc_datetime.replace('Z', '+00:00'))
                else:
                    utc_datetime = datetime.fromisoformat(utc_datetime)
            except ValueError:
                return self.get_vietnam_now()
        
        if utc_datetime.tzinfo is None:
            utc_datetime = self.utc_tz.localize(utc_datetime)
        
        return utc_datetime.astimezone(self.vietnam_tz)
    
    def to_utc_time(self, vietnam_datetime: Union[str, datetime]) -> datetime:
        '''??? ??? UTC ???? ??'''
        if isinstance(vietnam_datetime, str):
            try:
                vietnam_datetime = datetime.strptime(vietnam_datetime, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                vietnam_datetime = self.get_vietnam_now()
        
        if vietnam_datetime.tzinfo is None:
            vietnam_datetime = self.vietnam_tz.localize(vietnam_datetime)
        
        return vietnam_datetime.astimezone(self.utc_tz)
    
    def get_database_timestamp(self) -> str:
        '''?????? ??? UTC ????? ??'''
        return datetime.now(self.utc_tz).isoformat()
    
    def get_display_timestamp(self, utc_timestamp: Optional[str] = None) -> str:
        '''?? ??? ??? ?? ??? ??'''
        if utc_timestamp:
            vietnam_time = self.to_vietnam_time(utc_timestamp)
        else:
            vietnam_time = self.get_vietnam_now()
        
        return vietnam_time.strftime('%Y-%m-%d %H:%M:%S')

# ?? ????
vietnam_timezone = VietnamTimezoneHandler()

# ?? ???
def get_vietnam_now() -> datetime:
    '''??? ?? ??'''
    return vietnam_timezone.get_vietnam_now()

def get_vietnam_display_time(utc_timestamp: Optional[str] = None) -> str:
    '''??? ??? ?? ???'''
    return vietnam_timezone.get_display_timestamp(utc_timestamp)

def get_database_time() -> str:
    '''?????? ??? UTC ??'''
    return vietnam_timezone.get_database_timestamp()
