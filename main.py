import slack
import os
import json
from dotenv import load_dotenv
from pathlib import Path
import certifi
import schedule
import time
from datetime import date, datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.webhook import WebhookClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, request, Response, jsonify
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from slack_sdk.errors import SlackApiError
import requests
import random
from typing import Dict, List, Optional, Any
import threading

from utils.data_manager import load_data, save_data, tasks
from modules.task_management import (
    create_task, update_task, set_task_status, list_tasks,
    assign_task, unassign_task, set_task_priority, clear_tasks
)
from modules.project_management import (
    create_project, update_project_progress, create_project_summary,
    list_project_summaries, get_project_analytics
)
from modules.team_collaboration import (
    add_team_member, get_team_stats, get_contact_info
)
from modules.scheduling import (
    schedule_meeting, set_recurring_reminder, notify_me,
    set_reminder, send_reminder, smart_notify
)
from modules.file_management import add_file_link, list_files
from modules.integrations import get_weather, get_motivational_quote
from utils.standup import (
    send_standup_prompt, send_weekly_standup_prompt, send_monthly_standup_prompt
)
from utils.bot_intro import get_bot_intro

os.environ['SSL_CERT_FILE'] = certifi.where()

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)
client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '')

logging.basicConfig(level=logging.DEBUG)

scheduler = BackgroundScheduler()
scheduler.start()