from datetime import datetime
from flask import request
from utils.data_manager import team_members, user_roles, tasks, save_data

def add_team_member():
    """Add a team member"""
    data = request.form
    command_text = data.get('text', '').strip()
    
    if ' ' not in command_text:
        return "Format: /add-team-member <user_id> <role>"
    
    user_id, role = command_text.split(' ', 1)
    team_members[user_id] = {
        'role': role,
        'joined_at': datetime.now().isoformat(),
        'tasks_completed': 0,
        'current_tasks': []
    }
    user_roles[user_id] = role
    save_data()
    return f"👥 Added {user_id} to team as {role}"