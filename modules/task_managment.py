from datetime import datetime, date
from flask import request, jsonify
from utils.data_manager import tasks, save_data, get_task_counter, increment_task_counter

def create_task():
    """Create a new task"""
    data = request.form
    command_text = data.get('text', '').strip()
    user_id = data.get('user_id')

    if not command_text:
        return "Please provide a task description. Format: /create-task <description> [due_date] [priority] [category]"

    parts = command_text.split('|')
    description = parts[0].strip()
    
    due_date = None
    priority = 'Normal'
    category = 'General'
    estimated_hours = None
    
    if len(parts) > 1 and parts[1].strip():
        try:
            due_date = datetime.strptime(parts[1].strip(), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if len(parts) > 2 and parts[2].strip():
        priority = parts[2].strip()
    
    if len(parts) > 3 and parts[3].strip():
        category = parts[3].strip()
    
    if len(parts) > 4 and parts[4].strip():
        try:
            estimated_hours = float(parts[4].strip())
        except ValueError:
            pass

    task_id = get_task_counter()
    tasks[task_id] = {
        'description': description,
        'priority': priority,
        'category': category,
        'status': 'Open',
        'created_by': user_id,
        'created_at': datetime.now().isoformat(),
        'due_date': due_date.isoformat() if due_date else None,
        'estimated_hours': estimated_hours,
        'assigned_to': None,
        'completed_at': None,
        'actual_hours': None,
        'comments': [],
        'attachments': []
    }
    increment_task_counter()
    save_data()
    
    return f"✅ Task created: {description}\n📋 ID: {task_id} | Priority: {priority} | Category: {category}"

def update_task():
    """Update an existing task"""
    data = request.form
    command_text = data.get('text', '').strip()
    
    if not command_text or ' ' not in command_text:
        return "Format: /update-task <task_id> <field> <value>"
    
    parts = command_text.split(' ', 2)
    if len(parts) < 3:
        return "Format: /update-task <task_id> <field> <value>"
    
    try:
        task_id = int(parts[0])
        field = parts[1].lower()
        value = parts[2]
        
        if task_id not in tasks:
            return "❌ Task ID not found."
        
        task = tasks[task_id]
        
        if field == 'status':
            task['status'] = value
            if value.lower() == 'completed':
                task['completed_at'] = datetime.now().isoformat()
        elif field == 'priority':
            task['priority'] = value
        elif field == 'category':
            task['category'] = value
        elif field == 'description':
            task['description'] = value
        elif field == 'due_date':
            try:
                due_date = datetime.strptime(value, '%Y-%m-%d').date()
                task['due_date'] = due_date.isoformat()
            except ValueError:
                return "❌ Invalid date format. Use YYYY-MM-DD"
        elif field == 'estimated_hours':
            try:
                task['estimated_hours'] = float(value)
            except ValueError:
                return "❌ Invalid hours format"
        else:
            return "❌ Invalid field. Use: status, priority, category, description, due_date, estimated_hours"
        
        save_data()
        return f"✅ Task {task_id} updated: {field} = {value}"
        
    except ValueError:
        return "❌ Invalid task ID"

def set_task_status():
    """Set task status"""
    data = request.form
    command_text = data.get('text', '').strip()
    
    if ' ' not in command_text:
        return "Format: /task-status <task_id> <status>"
    
    task_id_str, status = command_text.split(' ', 1)
    
    try:
        task_id = int(task_id_str)
        if task_id in tasks:
            tasks[task_id]['status'] = status
            if status.lower() == 'completed':
                tasks[task_id]['completed_at'] = datetime.now().isoformat()
            save_data()
            return f"✅ Task {task_id} status updated to: {status}"
        else:
            return "❌ Task ID not found."
    except ValueError:
        return "❌ Invalid task ID"

def list_tasks():
    """List tasks with optional filtering"""
    data = request.form
    command_text = data.get('text', '').strip()
    
    if not tasks:
        return "📝 No tasks available."
    
    status_filter = None
    priority_filter = None
    category_filter = None
    assigned_filter = None
    
    if command_text:
        filters = command_text.split()
        for filter_item in filters:
            if filter_item.startswith('status:'):
                status_filter = filter_item.split(':')[1]
            elif filter_item.startswith('priority:'):
                priority_filter = filter_item.split(':')[1]
            elif filter_item.startswith('category:'):
                category_filter = filter_item.split(':')[1]
            elif filter_item.startswith('assigned:'):
                assigned_filter = filter_item.split(':')[1]
    
    filtered_tasks = {}
    for task_id, task in tasks.items():
        if status_filter and task['status'].lower() != status_filter.lower():
            continue
        if priority_filter and task['priority'].lower() != priority_filter.lower():
            continue
        if category_filter and task['category'].lower() != category_filter.lower():
            continue
        if assigned_filter and task.get('assigned_to') != assigned_filter:
            continue
        filtered_tasks[task_id] = task
    
    if not filtered_tasks:
        return "📝 No tasks match the specified filters."
    
    response_text = f"📋 Tasks ({len(filtered_tasks)} found):\n\n"
    
    for task_id, task in filtered_tasks.items():
        status_emoji = {
            'open': '🔴',
            'in_progress': '🟡',
            'review': '🟠',
            'completed': '🟢',
            'blocked': '🔴'
        }.get(task['status'].lower(), '⚪')
        
        priority_emoji = {
            'low': '🟢',
            'normal': '🟡',
            'high': '🟠',
            'urgent': '🔴'
        }.get(task['priority'].lower(), '⚪')
        
        assigned_to = task.get('assigned_to', "Unassigned")
        due_date = task.get('due_date', 'No due date')
        if due_date and due_date != 'No due date':
            try:
                due_date = datetime.fromisoformat(due_date).strftime('%Y-%m-%d')
            except:
                pass
        
        response_text += f"{status_emoji} **{task_id}**: {task['description']}\n"
        response_text += f"   {priority_emoji} Priority: {task['priority']} | 📁 Category: {task['category']}\n"
        response_text += f"   👤 Assigned: {assigned_to} | 📅 Due: {due_date}\n"
        response_text += f"   ⏱️ Est: {task.get('estimated_hours', 'N/A')}h | 🏷️ Status: {task['status']}\n\n"
    
    return response_text

def assign_task():
    """Assign a task to a user"""
    data = request.form
    command_text = data.get('text')
    task_id_str, user_id = command_text.split(' ', 1)
    task_id = int(task_id_str)

    if task_id in tasks:
        tasks[task_id]['assigned_to'] = user_id
        save_data()
        response_message = f"✅ Task '{task_id}' has been assigned to user '{user_id}'."
    else:
        response_message = f"❌ Task ID '{task_id}' not found."

    return jsonify(response_type='in_channel', text=response_message)

def unassign_task():
    """Unassign a task"""
    data = request.form
    command_text = data.get('text')
    task_id = int(command_text.split())

    if task_id in tasks:
        tasks[task_id]['assigned_to'] = None
        save_data()
        response_message = f"✅ Task '{task_id}' has been unassigned."
    else:
        response_message = f"❌ Task ID '{task_id}' not found."

    return jsonify(response_type='in_channel', text=response_message)

def set_task_priority():
    """Set task priority"""
    command_text = request.form.get('text', '').strip()
    if ' ' not in command_text:
        return "Invalid format. Please use: /task-priority <task_id> <priority_level>"
    
    try:
        task_id, new_priority = command_text.split(' ', 1)
        task_id = int(task_id) 
        
        if task_id in tasks:
            tasks[task_id]['priority'] = new_priority
            save_data()
            return f"✅ Priority for task ID {task_id} updated to {new_priority}."
        else:
            return "❌ Task ID not found."
        
    except ValueError:
        return "❌ Invalid format. Please use: /task-priority <task_id> <priority_level>"

def clear_tasks():
    """Clear all tasks"""
    tasks.clear()
    save_data()
    return "✅ All tasks have been cleared." 