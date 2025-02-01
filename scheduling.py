from datetime import datetime, timedelta
from flask import request, Response
from utils.data_manager import reminders, save_data
from apscheduler.triggers.date import DateTrigger

def schedule_meeting(client, scheduler):
    """Schedule a meeting"""
    data = request.form
    command_text = data.get('text', '').strip()
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    
    if '|' not in command_text:
        return "Format: /schedule-meeting <title> | <date> | <time> | <duration_minutes> | <participants>"
    
    parts = command_text.split('|')
    if len(parts) < 4:
        return "Format: /schedule-meeting <title> | <date> | <time> | <duration_minutes> | <participants>"
    
    title = parts[0].strip()
    date_str = parts[1].strip()
    time_str = parts[2].strip()
    duration = int(parts[3].strip())
    participants = parts[4].strip().split(',') if len(parts) > 4 else []
    
    try:
        meeting_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        reminder_time = meeting_datetime - timedelta(minutes=15)
        if reminder_time > datetime.now():
            scheduler.add_job(
                func=lambda: client.chat_postMessage(
                    channel=channel_id,
                    text=f"🔔 Meeting reminder: {title} starts in 15 minutes!"
                ),
                trigger=DateTrigger(run_date=reminder_time),
                id=f"meeting_reminder_{title}_{meeting_datetime.isoformat()}"
            )
        
        scheduler.add_job(
            func=lambda: client.chat_postMessage(
                channel=channel_id,
                text=f"🎯 Meeting starting: {title}\n⏱️ Duration: {duration} minutes\n👥 Participants: {', '.join(participants) if participants else 'All team members'}"
            ),
            trigger=DateTrigger(run_date=meeting_datetime),
            id=f"meeting_start_{title}_{meeting_datetime.isoformat()}"
        )
        
        return f"📅 Meeting scheduled: {title}\n📅 Date: {meeting_datetime.strftime('%Y-%m-%d %H:%M')}\n⏱️ Duration: {duration} minutes"
        
    except ValueError as e:
        return f"❌ Invalid date/time format: {e}"

def set_recurring_reminder(client, scheduler):
    """Set a recurring reminder"""
    data = request.form
    command_text = data.get('text', '').strip()
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    
    if '|' not in command_text:
        return "Format: /recurring-reminder <message> | <frequency> | <time>"
    
    parts = command_text.split('|')
    if len(parts) < 3:
        return "Format: /recurring-reminder <message> | <frequency> | <time>"
    
    message = parts[0].strip()
    frequency = parts[1].strip().lower()
    time_str = parts[2].strip()
    
    try:
        hour, minute = map(int, time_str.split(':'))
        
        if frequency == 'daily':
            scheduler.add_job(
                func=lambda: client.chat_postMessage(channel=channel_id, text=f"🔄 Daily reminder: {message}"),
                trigger='cron',
                hour=hour,
                minute=minute,
                id=f"daily_reminder_{user_id}_{message[:20]}"
            )
        elif frequency == 'weekly':
            scheduler.add_job(
                func=lambda: client.chat_postMessage(channel=channel_id, text=f"🔄 Weekly reminder: {message}"),
                trigger='cron',
                day_of_week='mon',
                hour=hour,
                minute=minute,
                id=f"weekly_reminder_{user_id}_{message[:20]}"
            )
        elif frequency == 'monthly':
            scheduler.add_job(
                func=lambda: client.chat_postMessage(channel=channel_id, text=f"🔄 Monthly reminder: {message}"),
                trigger='cron',
                day=1,
                hour=hour,
                minute=minute,
                id=f"monthly_reminder_{user_id}_{message[:20]}"
            )
        else:
            return "❌ Invalid frequency. Use: daily, weekly, monthly"
        
        return f"🔄 Recurring reminder set: {message}\n📅 Frequency: {frequency}\n⏰ Time: {time_str}"
        
    except ValueError:
        return "❌ Invalid time format. Use HH:MM"

def notify_me(client, scheduler):
    """Set a one-time notification"""
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
            func=lambda: client.chat_postMessage(channel=channel_id, text=f"🔔 Reminder: {message}"),
            trigger=DateTrigger(run_date=notify_datetime),
            id=str(user_id) + '-' + str(notify_time)
        )

        return Response(f"✅ Reminder set for {notify_datetime.strftime('%H:%M')}: {message}", status=200)
    
    except ValueError:
        return Response("❌ Invalid time format. Use HH:MM.", status=400)

def set_reminder(client):
    """Set a 24-hour reminder"""
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    text = data.get('text')

    reminders[user_id] = {
        'channel_id': channel_id,
        'text': text,
        'time': datetime.now() + timedelta(hours=24)
    }

    client.chat_postMessage(channel=channel_id, text=f"🔔 Reminder set for 24 hours: {text}")
    return Response(), 200

def send_reminder(client, user_id):
    """Send a reminder to a user"""
    reminder = reminders.get(user_id)
    if reminder:
        client.chat_postMessage(channel=reminder['channel_id'], text=f"🔔 Reminder: {reminder['text']}")
        del reminders[user_id]

def smart_notify(client):
    """Send smart notifications based on conditions"""
    data = request.form
    command_text = data.get('text', '').strip()
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    
    if '|' not in command_text:
        return "Format: /smart-notify <message> | <condition> | <time>"
    
    parts = command_text.split('|')
    if len(parts) < 3:
        return "Format: /smart-notify <message> | <condition> | <time>"
    
    message = parts[0].strip()
    condition = parts[1].strip()
    time_str = parts[2].strip()
    
    from utils.data_manager import tasks, project_summaries
    
    if condition.lower() == 'task_completion':
        high_priority_tasks = [t for t in tasks.values() if t['priority'].lower() == 'high' and t['status'].lower() != 'completed']
        if not high_priority_tasks:
            client.chat_postMessage(channel=channel_id, text=f"🎉 Smart notification: {message}")
            return "✅ Smart notification sent!"
    
    elif condition.lower() == 'project_deadline':
        today = datetime.now().date()
        for project_id, project in project_summaries.items():
            if isinstance(project, dict) and project.get('deadline'):
                try:
                    deadline = datetime.strptime(project['deadline'], '%Y-%m-%d').date()
                    days_until_deadline = (deadline - today).days
                    if days_until_deadline <= 7:
                        client.chat_postMessage(channel=channel_id, text=f"⚠️ Project deadline alert: {message}")
                        return "✅ Smart notification sent!"
                except:
                    pass
    
    return "❌ Condition not met for smart notification" 