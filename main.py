import slack
import os
from dotenv import load_dotenv
from pathlib import Path
import certifi
import schedule
import time
from datetime import date
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, request, Response, jsonify
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from slack_sdk.errors import SlackApiError

os.environ['SSL_CERT_FILE'] = certifi.where()

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)
client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

tasks = {}
task_counter = 1
reminders = {}
notifications = {}
project_summaries = {}

logging.basicConfig(level=logging.DEBUG)

scheduler = BackgroundScheduler()
scheduler.start()    

@app.route('/assign-task', methods=['POST'])
def assign_task():
    data = request.form
    command_text = data.get('text')
    task_id_str, user_id = command_text.split(' ', 1)
    task_id = int(task_id_str)

    if task_id in tasks:
        tasks[task_id]['assigned_to'] = user_id
        response_message = f"Task '{task_id}' has been assigned to user '{user_id}'."
    else:
        response_message = f"Task ID '{task_id}' not found."

    return jsonify(response_type='in_channel', text=response_message)

@app.route('/unassign-task', methods=['POST'])
def unassign_task():
    data = request.form
    command_text = data.get('text')
    task_id = int(command_text.split())

    if task_id in tasks:
        tasks[task_id]['assigned_to'] = None
        response_message = f"Task '{task_id}' has been unassigned."
    else:
        response_message = f"Task ID '{task_id}' not found."

    return jsonify(response_type='in_channel', text=response_message)

@app.route('/create-project-summary', methods=['POST'])
def create_project_summary():
    data = request.form
    command_text = data.get('text').strip()

    if ',' not in command_text:
        return "Invalid format. Please use: /create-project-summary <project_name>, <summary>"

    parts = command_text.split(' ', 1)

    if len(parts) < 2:
        return "Invalid format. Please use: /create-project-summary <project_name> <summary>"
    
    project_name, summary = command_text.split(',', 1)
    project_name = project_name.strip()
    summary = summary.strip()
    project_summaries[project_name] = summary
    return f"Project summary for '{project_name}',"

@app.route('/list-project-summaries', methods=['POST'])
def list_project_summaries():
    if not project_summaries:
        return "No project summaries available."
    response_text = "Project Summaries:\n"

    for project_name, summary in project_summaries.items():
        response_text += f"Project: {project_name}, Summary: {summary}\n\n"
    return response_text

@app.route('/notify-me', methods=['POST'])
def notify_me():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    text = data.get('text')
    parts = text.split(',')

    if len(parts) != 2:
        return Response("Invalid format. Use: 'Message, HH:MM'", status=400)
    
    message = parts[0].strip()
    time_str = parts[1].strip()

    try:
        notify_time = datetime.strptime(time_str, "%H:%M").time()
        now = datetime.now()
        notify_datetime = datetime.combine(now.date(), notify_time)

        if notify_datetime < now:
            notify_datetime += timedelta(days=1)
        
        scheduler.add_job(
            func=lambda: client.chat_postMessage(channel=channel_id, text=f"Reminder: {message}"),
            trigger=DateTrigger(run_date=notify_datetime),
            id=str(user_id) + '-' + str(notify_time)
        )

        return Response(f"Reminder set for {notify_datetime.strftime('%H:%M')}: {message}"), 200
    
    except ValueError:
        return Response("Invalid time format. Use HH:MM.", status=400)


@app.route('/create-task', methods=['POST'])
def create_task():
    global task_counter
    command_text = request.form.get('text', '').strip()

    if not command_text:
        return "Please provide a task description."
    
    task_id = task_counter
    tasks[task_id] = {'description': command_text, 'priority': 'Normal'}
    task_counter += 1
    
    return f"Task created: {command_text}. Task ID: {task_id}"
    

@app.route('/task-priority', methods=['POST'])
def set_task_priority():
    command_text = request.form.get('text', '').strip()
    if ' ' not in command_text:
        return "Invalid format. Please use: /task-priority <task_id> <priority_level>"
    
    try:
        task_id, new_priority = command_text.split(' ', 1)
        task_id = int(task_id) 
        
        if task_id in tasks:
            tasks[task_id]['priority'] = new_priority
            return f"Priority for task ID {task_id} updated to {new_priority}."
        else:
            return "Task ID not found."
        
    except ValueError:
        return "Invalid format. Please use: /task-priority <task_id> <priority_level>"

@app.route('/list-tasks', methods=['POST'])
def list_tasks():
    if not tasks:
        return "No tasks available."
    
    response_text = "Tasks:\n"

    for task_id, task_info in tasks.items():
        assigned_to = task_info.get('assigned_to', "Unassigned")
        response_text += f"ID: {task_id}, Description: {task_info['description']}, Priority: {task_info['priority']}, Assigned to: {assigned_to}\n"
    
    return response_text

@app.route('/clear-tasks', methods=['POST'])
def clear_tasks():
    tasks.clear()
    return "All tasks have been cleared."

@app.route('/set-reminder', methods=['POST'])
def set_reminder():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    text = data.get('text')

    reminders[user_id] = {
        'channel_id': channel_id,
        'text': text,
        'time': datetime.now() + timedelta(hours=24)
    }

    client.chat_postMessage(channel=channel_id, text=f"Reminder set for 24 hours: {text}")
    schedule.every(24).hours.do(send_reminder, user_id=user_id)
    return Response(), 200

def send_reminder(user_id):
    reminder = reminders.get(user_id)
    if reminder:
        client.chat_postMessage(channel=reminder['channel_id'], text=f"Reminder: {reminder['text']}")
        del reminders[user_id]

@app.route('/bot-intro', methods=['POST'])
def bot_intro():
    data = request.form
    channel_id = data.get('channel_id')

    intro_message = "Hi, I'm a project and task managment bot here to assist you."

    client.chat_postMessage(channel=channel_id, text=intro_message)
    return Response(), 200

@app.route('/get-contact-info', methods=['POST'])
def get_contact_info():
    data = request.form
    command_text = data.get('text').strip()

    if not command_text:
        return jsonify(response_type='ephemeral', text="Please format with user_id for me to get the contact infromation. Use: /get-contact-info (user_id)"), 200
    user_id = command_text
    
    try:
        response = client.users_info(user=user_id)
        user = response['user']
        email = user['profile'].get('email', 'Email not found')
        real_name = user['real name']
        contact_info = f"User: {real_name}\nEmail: {email}"

    except SlackApiError as e:
        contact_info = f"Error getting the user info."
    
    return jsonify(response_type='in_channel', text=contact_info), 200
                
def send_standup_prompt():
    client.chat_postMessage(
        channel='',
        text="Hello, it is time for our daily standup. Reply with:\n1. What you worked on yesterday\n2. What the plan is for today\n3. Any additional updates"
    )

schedule.every().monday.at("09:00").do(send_standup_prompt)
schedule.every().tuesday.at("09:00").do(send_standup_prompt)
schedule.every().wednesday.at("09:00").do(send_standup_prompt)
schedule.every().thursday.at("09:00").do(send_standup_prompt)
schedule.every().friday.at("09:00").do(send_standup_prompt)
schedule.every().saturday.at("09:00").do(send_standup_prompt)
schedule.every().sunday.at("09:00").do(send_standup_prompt)

def send_weekly_standup_prompt():
    client.chat_postMessage(
        channel='',
        text="Hello, it's time for our weekly standup where we can share updates. Please reply with:\n1. What you worked on this week\n2. What you plan to work on next week\n3. Any additonal updates"
    )

scheduler.add_job(
    func=send_weekly_standup_prompt,
    trigger='cron',
    day_of_week='mon',
    hour=9,
    minute=0
)

def send_monthly_standup_prompt():
    client.chat_postMessage(
        channel='',
        text="Hello, this is a monthly project goals and vision update. Please reply with:\n1. What new goal you have for the project this month and any changes to your future vision for the project."
    )

scheduler.add_job(
    func=send_monthly_standup_prompt,
    trigger='cron',
    day=1,
    hour=9,
    minute=0
)

@slack_event_adapter.on('message')
def handle_message(event_data):
    event = event_data['event']
    
    if 'subtype' in event:
        return
    
    user = event.get('user')
    text = event.get('text')
    channel = event.get('channel')
    
    if channel == '':  
        logging.info(f"Received weekly update from user {user}: {text}")

    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True, port=5003)

while True:
    schedule.run_pending()
    time.sleep(1)