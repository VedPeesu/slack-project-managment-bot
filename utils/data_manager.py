import json
import os
from typing import Dict, Any
from datetime import datetime

DATA_FILE = 'bot_data.json'

tasks = {}
task_counter = 1
reminders = {}
notifications = {}
project_summaries = {}
team_members = {}
project_analytics = {}
file_links = {}
team_stats = {}
user_roles = {}

def load_data():
    """Load data from JSON file"""
    global tasks, task_counter, reminders, notifications, project_summaries, team_members, project_analytics, file_links, team_stats, user_roles
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            tasks = data.get('tasks', {})
            task_counter = data.get('task_counter', 1)
            reminders = data.get('reminders', {})
            notifications = data.get('notifications', {})
            project_summaries = data.get('project_summaries', {})
            team_members = data.get('team_members', {})
            project_analytics = data.get('project_analytics', {})
            file_links = data.get('file_links', {})
            team_stats = data.get('team_stats', {})
            user_roles = data.get('user_roles', {})
    except FileNotFoundError:
        pass

def save_data():
    """Save data to JSON file"""
    data = {
        'tasks': tasks,
        'task_counter': task_counter,
        'reminders': reminders,
        'notifications': notifications,
        'project_summaries': project_summaries,
        'team_members': team_members,
        'project_analytics': project_analytics,
        'file_links': file_links,
        'team_stats': team_stats,
        'user_roles': user_roles
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_task_counter():
    """Get current task counter"""
    global task_counter
    return task_counter

def increment_task_counter():
    """Increment task counter"""
    global task_counter
    task_counter += 1
    return task_counter 