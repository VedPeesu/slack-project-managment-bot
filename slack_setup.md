# Slack App Setup Guide

## 1. Create a Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Enter app name: "Project Management Bot"
5. Select your workspace

## 2. Configure OAuth & Permissions

1. Go to "OAuth & Permissions" in the sidebar
2. Add the following Bot Token Scopes:
   - `chat:write` - Send messages
   - `reactions:write` - Add reactions
   - `users:read` - Read user information
   - `commands` - Add slash commands

3. Install the app to your workspace
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

## 3. Configure Event Subscriptions

1. Go to "Event Subscriptions" in the sidebar
2. Enable Events
3. Set your Request URL to: `https://your-domain.com/slack/events`
4. Subscribe to bot events:
   - `message.channels` - Listen to messages in channels
   - `reaction_added` - Listen to reactions (optional)

## 4. Create Slash Commands

Go to "Slash Commands" and create the following commands:

### Task Management Commands
```
/create-task
Description: Create a new task with optional details
Usage: /create-task <description> | [due_date] | [priority] | [category] | [estimated_hours]
Request URL: https://your-domain.com/create-task
```

```
/update-task
Description: Update task details
Usage: /update-task <task_id> <field> <value>
Request URL: https://your-domain.com/update-task
```

```
/task-status
Description: Update task status
Usage: /task-status <task_id> <status>
Request URL: https://your-domain.com/task-status
```

```
/list-tasks
Description: List all tasks with optional filters
Usage: /list-tasks [filters]
Request URL: https://your-domain.com/list-tasks
```

```
/assign-task
Description: Assign task to user
Usage: /assign-task <task_id> <user_id>
Request URL: https://your-domain.com/assign-task
```

```
/unassign-task
Description: Unassign task
Usage: /unassign-task <task_id>
Request URL: https://your-domain.com/unassign-task
```

```
/task-priority
Description: Set task priority
Usage: /task-priority <task_id> <priority>
Request URL: https://your-domain.com/task-priority
```

```
/clear-tasks
Description: Clear all tasks
Usage: /clear-tasks
Request URL: https://your-domain.com/clear-tasks
```

### Project Management Commands
```
/create-project
Description: Create a new project
Usage: /create-project <name> | <description> | <deadline> | <budget>
Request URL: https://your-domain.com/create-project
```

```
/project-progress
Description: Update project progress
Usage: /project-progress <project_id> <percentage>
Request URL: https://your-domain.com/project-progress
```

```
/create-project-summary
Description: Create project summary
Usage: /create-project-summary <name>, <summary>
Request URL: https://your-domain.com/create-project-summary
```

```
/list-project-summaries
Description: List all project summaries
Usage: /list-project-summaries
Request URL: https://your-domain.com/list-project-summaries
```

### Team Collaboration Commands
```
/add-team-member
Description: Add team member
Usage: /add-team-member <user_id> <role>
Request URL: https://your-domain.com/add-team-member
```

```
/team-stats
Description: Get team statistics
Usage: /team-stats
Request URL: https://your-domain.com/team-stats
```

```
/get-contact-info
Description: Get user contact information
Usage: /get-contact-info <user_id>
Request URL: https://your-domain.com/get-contact-info
```

### Scheduling Commands
```
/schedule-meeting
Description: Schedule a meeting
Usage: /schedule-meeting <title> | <date> | <time> | <duration> | [participants]
Request URL: https://your-domain.com/schedule-meeting
```

```
/recurring-reminder
Description: Set recurring reminder
Usage: /recurring-reminder <message> | <frequency> | <time>
Request URL: https://your-domain.com/recurring-reminder
```

```
/notify-me
Description: Set one-time reminder
Usage: /notify-me <message>, <time>
Request URL: https://your-domain.com/notify-me
```

```
/set-reminder
Description: Set 24-hour reminder
Usage: /set-reminder <message>
Request URL: https://your-domain.com/set-reminder
```

### File Management Commands
```
/add-file-link
Description: Add file link
Usage: /add-file-link <name> | <url> | [category]
Request URL: https://your-domain.com/add-file-link
```

```
/list-files
Description: List file links
Usage: /list-files [category]
Request URL: https://your-domain.com/list-files
```

### Analytics Commands
```
/project-analytics
Description: Get project analytics
Usage: /project-analytics
Request URL: https://your-domain.com/project-analytics
```

```
/smart-notify
Description: Set smart notification
Usage: /smart-notify <message> | <condition> | <time>
Request URL: https://your-domain.com/smart-notify
```

### Integration Commands
```
/weather
Description: Get weather information
Usage: /weather <city>
Request URL: https://your-domain.com/weather
```

```
/motivational-quote
Description: Get motivational quote
Usage: /motivational-quote
Request URL: https://your-domain.com/motivational-quote
```

### Bot Commands
```
/bot-intro
Description: Get bot introduction and help
Usage: /bot-intro
Request URL: https://your-domain.com/bot-intro
```

## 5. Environment Variables

Create a `.env` file with:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SIGNING_SECRET=your-signing-secret-here
SLACK_CHANNEL=your-channel-id-here
```

## 6. Deploy Your Bot

1. Deploy your Flask app to a server with HTTPS
2. Update all Request URLs to use your domain
3. Test the commands in Slack

## 7. Optional: Weather API Setup

For the weather feature to work, you'll need an OpenWeatherMap API key:

1. Sign up at https://openweathermap.org/api
2. Get your API key
3. Update the weather function in `main.py` with your API key

## 8. Testing

Test each command to ensure they work correctly:

1. `/bot-intro` - Should show bot introduction
2. `/create-task Test task` - Should create a task
3. `/list-tasks` - Should show the created task
4. `/create-project Test Project | Test Description` - Should create a project

## 9. Troubleshooting

### Common Issues:

1. **"Command not found"** - Make sure the slash command is properly configured
2. **"Invalid signature"** - Check your SIGNING_SECRET
3. **"Bot not responding"** - Verify your SLACK_BOT_TOKEN
4. **"Permission denied"** - Check bot token scopes

### Debug Mode:

Set `logging.basicConfig(level=logging.DEBUG)` in your code to see detailed logs.

## 10. Security Notes

- Never commit your `.env` file to version control
- Use HTTPS for all webhook URLs
- Regularly rotate your bot tokens
- Monitor your app's usage and permissions 