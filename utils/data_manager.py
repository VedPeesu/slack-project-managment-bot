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