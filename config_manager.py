import json
import os
from datetime import datetime

CONFIG_FILE = "config.json"

# ADDED: min_delay and max_delay defaults
DEFAULT_CONFIG = {
    "app_password": "",
    "sender_email": "",
    "daily_limit": 50,
    "current_daily_count": 0,
    "min_delay": 30,
    "max_delay": 90,
    "last_run_date": "",
    "active_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "session_times": "09:00-12:00, 14:00-17:00",
    "templates": [
        {"subject": "Subject 1", "body": "Hello {Name}, ..."},
        {"subject": "Subject 2", "body": "Hi {Name}, ..."},
        {"subject": "Subject 3", "body": "Dear {Name}, ..."}
    ]
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    
    # Ensure new keys exist if loading an old config file
    if "min_delay" not in config: config["min_delay"] = 30
    if "max_delay" not in config: config["max_delay"] = 90

    # Check Daily Reset Logic
    today_str = datetime.now().strftime("%Y-%m-%d")
    if config.get("last_run_date") != today_str:
        config["last_run_date"] = today_str
        config["current_daily_count"] = 0
        save_config(config)
        
    return config

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

def increment_daily_count():
    config = load_config()
    config["current_daily_count"] += 1
    save_config(config)