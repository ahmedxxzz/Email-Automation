import time
import random
from datetime import datetime

DAYS_MAP = {
    "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6
}

def check_limits(config):
    """Returns True if daily limit not reached."""
    return config["current_daily_count"] < int(config["daily_limit"])

def check_session_time(config):
    """
    Checks if current time is within allowed sessions.
    Format expected: '09:00-12:00, 14:00-17:00'
    """
    now = datetime.now()
    
    # 1. Check Day
    current_day_idx = now.weekday()
    allowed_days = [DAYS_MAP[d] for d in config.get("active_days", [])]
    if current_day_idx not in allowed_days:
        return False, "Today is not an active sending day."

    # 2. Check Time Ranges
    time_str = config.get("session_times", "")
    if not time_str: 
        return True, "No sessions defined (Always Open)"

    ranges = [x.strip() for x in time_str.split(',')]
    current_time = now.time()
    
    for r in ranges:
        try:
            start_str, end_str = r.split('-')
            start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
            end_time = datetime.strptime(end_str.strip(), "%H:%M").time()
            
            if start_time <= current_time <= end_time:
                return True, "Session Active"
        except ValueError:
            continue # Skip malformed ranges

    return False, "Current time is outside defined sessions."

# UPDATED: Accepts custom min and max
def perform_throttle_delay(log_callback, min_delay=30, max_delay=90):
    """Sleeps for random seconds between min and max."""
    # Safety check to prevent crash if user puts Min > Max
    if min_delay > max_delay:
        min_delay, max_delay = max_delay, min_delay
        
    delay = random.uniform(float(min_delay), float(max_delay))
    log_callback(f"Throttling: Sleeping for {int(delay)} seconds...")
    time.sleep(delay)