from datetime import datetime
from flask import request
from utils.data_manager import file_links, save_data

def add_file_link():
    """Add a file link"""
    data = request.form
    command_text = data.get('text', '').strip()
    
    if '|' not in command_text:
        return "Format: /add-file-link <name> | <url> | <category>"
    
    parts = command_text.split('|')
    if len(parts) < 2:
        return "Format: /add-file-link <name> | <url> | <category>"
    
    name = parts[0].strip()
    url = parts[1].strip()
    category = parts[2].strip() if len(parts) > 2 else 'General'
    
    file_id = f"file_{len(file_links) + 1}"
    file_links[file_id] = {
        'name': name,
        'url': url,
        'category': category,
        'added_at': datetime.now().isoformat(),
        'added_by': data.get('user_id')
    }
    
    save_data()
    return f"📎 File link added: {name}\n🔗 URL: {url}\n📁 Category: {category}"

def list_files():
    """List files with optional category filtering"""
    data = request.form
    command_text = data.get('text', '').strip()
    
    if not file_links:
        return "📎 No file links available."
    
    category_filter = command_text if command_text else None
    
    filtered_files = {}
    for file_id, file_info in file_links.items():
        if category_filter and file_info['category'].lower() != category_filter.lower():
            continue
        filtered_files[file_id] = file_info
    
    if not filtered_files:
        return "📎 No files match the specified category."
    
    response_text = f"📎 Files ({len(filtered_files)} found):\n\n"
    
    for file_id, file_info in filtered_files.items():
        response_text += f"📄 **{file_info['name']}**\n"
        response_text += f"   🔗 {file_info['url']}\n"
        response_text += f"   📁 Category: {file_info['category']}\n"
        response_text += f"   📅 Added: {file_info['added_at'][:10]}\n\n"
    
    return response_text 