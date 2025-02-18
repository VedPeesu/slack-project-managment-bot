def send_standup_prompt(client, channel):
    """Send daily standup prompt"""
    client.chat_postMessage(
        channel=channel,
        text="🌅 **Daily Standup Time!**\n\nPlease reply with:\n1️⃣ What you worked on yesterday\n2️⃣ What the plan is for today\n3️⃣ Any blockers or updates"
    )

def send_weekly_standup_prompt(client, channel):
    """Send weekly standup prompt"""
    client.chat_postMessage(
        channel=channel,
        text="📅 **Weekly Standup Time!**\n\nPlease share:\n1️⃣ What you accomplished this week\n2️⃣ What you plan to work on next week\n3️⃣ Any challenges or insights"
    )

def send_monthly_standup_prompt(client, channel):
    """Send monthly standup prompt"""
    client.chat_postMessage(
        channel=channel,
        text="📊 **Monthly Review Time!**\n\nPlease reflect on:\n1️⃣ Key achievements this month\n2️⃣ Goals for next month\n3️⃣ Any process improvements or suggestions"
    ) 