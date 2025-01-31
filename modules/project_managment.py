from datetime import datetime, date
from flask import request
from utils.data_manager import project_summaries, save_data

def create_project():
    """Create a new project"""
    data = request.form
    command_text = data.get('text', '').strip()
    user_id = data.get('user_id')
    
    if '|' not in command_text:
        return "Format: /create-project <name> | <description> | <deadline> | <budget>"
    
    parts = command_text.split('|')
    if len(parts) < 2:
        return "Format: /create-project <name> | <description> | <deadline> | <budget>"
    
    name = parts[0].strip()
    description = parts[1].strip()
    deadline = parts[2].strip() if len(parts) > 2 else None
    budget = parts[3].strip() if len(parts) > 3 else None
    
    project_id = f"proj_{len(project_summaries) + 1}"
    project_summaries[project_id] = {
        'name': name,
        'description': description,
        'deadline': deadline,
        'budget': budget,
        'created_by': user_id,
        'created_at': datetime.now().isoformat(),
        'status': 'Active',
        'progress': 0,
        'tasks': [],
        'team_members': [],
        'milestones': []
    }
    
    save_data()
    return f"🚀 Project created: {name}\n📋 ID: {project_id}\n📝 Description: {description}"

def update_project_progress():
    """Update project progress"""
    data = request.form
    command_text = data.get('text', '').strip()
    
    if ' ' not in command_text:
        return "Format: /project-progress <project_id> <percentage>"
    
    project_id, progress_str = command_text.split(' ', 1)
    
    try:
        progress = int(progress_str)
        if progress < 0 or progress > 100:
            return "❌ Progress must be between 0 and 100"
        
        if project_id in project_summaries:
            project_summaries[project_id]['progress'] = progress
            save_data()
            return f"📊 Project {project_id} progress updated to {progress}%"
        else:
            return "❌ Project not found"
    except ValueError:
        return "❌ Invalid progress percentage"

def create_project_summary():
    """Create a project summary"""
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
    save_data()
    return f"Project summary for '{project_name}' created."

def list_project_summaries():
    """List all project summaries"""
    if not project_summaries:
        return "No project summaries available."
    response_text = "Project Summaries:\n"

    for project_name, summary in project_summaries.items():
        response_text += f"Project: {project_name}, Summary: {summary}\n\n"
    return response_text

def get_project_analytics():
    """Get project analytics"""
    if not project_summaries:
        return "📊 No projects available for analytics."
    
    response_text = "📊 Project Analytics:\n\n"
    
    total_projects = len(project_summaries)
    active_projects = len([p for p in project_summaries.values() if isinstance(p, dict) and p.get('status') == 'Active'])
    completed_projects = len([p for p in project_summaries.values() if isinstance(p, dict) and p.get('status') == 'Completed'])
    
    response_text += f"📈 Project Overview:\n"
    response_text += f"   🚀 Total Projects: {total_projects}\n"
    response_text += f"   🔄 Active Projects: {active_projects}\n"
    response_text += f"   ✅ Completed Projects: {completed_projects}\n\n"
    
    from utils.data_manager import tasks
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks.values() if t['status'].lower() == 'completed'])
    overdue_tasks = len([t for t in tasks.values() if t.get('due_date') and datetime.fromisoformat(t['due_date']).date() < date.today() and t['status'].lower() != 'completed'])
    
    response_text += f"📋 Task Analytics:\n"
    response_text += f"   📊 Total Tasks: {total_tasks}\n"
    response_text += f"   ✅ Completed: {completed_tasks}\n"
    response_text += f"   ⚠️ Overdue: {overdue_tasks}\n"
    response_text += f"   📈 Completion Rate: {(completed_tasks/total_tasks*100):.1f}%\n\n"
    
    priority_counts = {}
    for task in tasks.values():
        priority = task['priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    response_text += f"🎯 Priority Breakdown:\n"
    for priority, count in priority_counts.items():
        response_text += f"   {priority}: {count} tasks\n"
    
    return response_text 