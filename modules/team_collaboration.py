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

def get_team_stats():
    """Get team statistics"""
    if not team_members:
        return "👥 No team members found."
    
    response_text = "📊 Team Statistics:\n\n"
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks.values() if t['status'].lower() == 'completed'])
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    response_text += f"📈 Overall Progress: {completion_rate:.1f}% ({completed_tasks}/{total_tasks} tasks)\n\n"
    
    for user_id, member in team_members.items():
        user_tasks = [t for t in tasks.values() if t.get('assigned_to') == user_id]
        completed_user_tasks = [t for t in user_tasks if t['status'].lower() == 'completed']
        
        response_text += f"👤 **{user_id}** ({member['role']})\n"
        response_text += f"   📋 Tasks: {len(completed_user_tasks)}/{len(user_tasks)} completed\n"
        response_text += f"   📅 Joined: {member['joined_at'][:10]}\n\n"
    
    return response_text

def get_contact_info():
    """Get contact information for a user"""
    data = request.form
    command_text = data.get('text').strip()

    if not command_text:
        return "Please format with user_id for me to get the contact information. Use: /get-contact-info (user_id)"
    
    user_id = command_text
    
    try:
        from main import client
        response = client.users_info(user=user_id)
        user = response['user']
        email = user['profile'].get('email', 'Email not found')
        real_name = user['real_name']
        contact_info = f"👤 User: {real_name}\n📧 Email: {email}"

    except Exception as e:
        contact_info = f"❌ Error getting the user info."
    
    return contact_info 