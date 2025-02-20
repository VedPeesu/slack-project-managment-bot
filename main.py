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

load_data()

@app.route('/create-task', methods=['POST'])
def create_task_route():
    return create_task()

@app.route('/update-task', methods=['POST'])
def update_task_route():
    return update_task()

@app.route('/task-status', methods=['POST'])
def set_task_status_route():
    return set_task_status()

@app.route('/list-tasks', methods=['POST'])
def list_tasks_route():
    return list_tasks()

@app.route('/assign-task', methods=['POST'])
def assign_task_route():
    return assign_task()

@app.route('/unassign-task', methods=['POST'])
def unassign_task_route():
    return unassign_task()

@app.route('/task-priority', methods=['POST'])
def set_task_priority_route():
    return set_task_priority()

@app.route('/clear-tasks', methods=['POST'])
def clear_tasks_route():
    return clear_tasks()

@app.route('/create-project', methods=['POST'])
def create_project_route():
    return create_project()

@app.route('/project-progress', methods=['POST'])
def update_project_progress_route():
    return update_project_progress()

@app.route('/create-project-summary', methods=['POST'])
def create_project_summary_route():
    return create_project_summary()

@app.route('/list-project-summaries', methods=['POST'])
def list_project_summaries_route():
    return list_project_summaries()

@app.route('/project-analytics', methods=['POST'])
def get_project_analytics_route():
    return get_project_analytics()

@app.route('/add-team-member', methods=['POST'])
def add_team_member_route():
    return add_team_member()

@app.route('/team-stats', methods=['POST'])
def get_team_stats_route():
    return get_team_stats()

@app.route('/get-contact-info', methods=['POST'])
def get_contact_info_route():
    return get_contact_info()

@app.route('/schedule-meeting', methods=['POST'])
def schedule_meeting_route():
    return schedule_meeting(client, scheduler)

@app.route('/recurring-reminder', methods=['POST'])
def set_recurring_reminder_route():
    return set_recurring_reminder(client, scheduler)

@app.route('/notify-me', methods=['POST'])
def notify_me_route():
    return notify_me(client, scheduler)

@app.route('/set-reminder', methods=['POST'])
def set_reminder_route():
    return set_reminder(client)

@app.route('/smart-notify', methods=['POST'])
def smart_notify_route():
    return smart_notify(client)

@app.route('/add-file-link', methods=['POST'])
def add_file_link_route():
    return add_file_link()

@app.route('/list-files', methods=['POST'])
def list_files_route():
    return list_files()

@app.route('/weather', methods=['POST'])
def get_weather_route():
    return get_weather()

@app.route('/motivational-quote', methods=['POST'])
def get_motivational_quote_route():
    return get_motivational_quote()

@app.route('/bot-intro', methods=['POST'])
def bot_intro():
    data = request.form
    channel_id = data.get('channel_id')
    intro_message = get_bot_intro()
    client.chat_postMessage(channel=channel_id, text=intro_message)
    return Response(), 200

@slack_event_adapter.on('message')
def handle_message(event_data):
    event = event_data['event']
    
    if 'subtype' in event:
        return
    
    user = event.get('user')
    text = event.get('text')
    channel = event.get('channel')
    
    if channel == SLACK_CHANNEL:  
        logging.info(f"Received message from user {user}: {text}")
        
        if any(word in text.lower() for word in ['good job', 'great work', 'excellent', 'awesome']):
            try:
                client.reactions_add(channel=channel, timestamp=event['ts'], name='thumbsup')
            except:
                pass
        
        if any(word in text.lower() for word in ['overdue', 'late', 'missed deadline']):
            overdue_tasks = [t for t in tasks.values() if t.get('due_date') and datetime.fromisoformat(t['due_date']).date() < date.today() and t['status'].lower() != 'completed']
            if overdue_tasks:
                overdue_message = "⚠️ **Overdue Tasks Detected:**\n"
                for task in overdue_tasks[:5]:
                    overdue_message += f"• {task['description']} (Due: {task['due_date'][:10]})\n"
                client.chat_postMessage(channel=channel, text=overdue_message)

    return Response(), 200


schedule.every().monday.at("09:00").do(lambda: send_standup_prompt(client, SLACK_CHANNEL))
schedule.every().tuesday.at("09:00").do(lambda: send_standup_prompt(client, SLACK_CHANNEL))
schedule.every().wednesday.at("09:00").do(lambda: send_standup_prompt(client, SLACK_CHANNEL))
schedule.every().thursday.at("09:00").do(lambda: send_standup_prompt(client, SLACK_CHANNEL))
schedule.every().friday.at("09:00").do(lambda: send_standup_prompt(client, SLACK_CHANNEL))

scheduler.add_job(
    func=lambda: send_weekly_standup_prompt(client, SLACK_CHANNEL),
    day_of_week='mon',
    hour=9,
    minute=0
)

scheduler.add_job(
    func=lambda: send_monthly_standup_prompt(client, SLACK_CHANNEL),
    day=1,
    hour=9,
    minute=0
)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
    app.run(debug=True, port=5003) 