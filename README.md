# SlackProjectManagmentBot
This project utilizes ngrok and Slack API to deliver groups in Slack a quick and easy way to maximize project efficency and team collaboration. It involves daily automated Standup reminders, various commands, and summaries to assist users in completing tasks.
# Features
- Daily, weekly, and monthly automated Standup reminders for users to plan out their day regarding their proejcts, goals, and updates.
- Task managment through differnt commands like setting task priority, assigining tasks, and getting project summaries.
- Reminders and notifications that users can quickly add and manage through discussions in the channels.
- Project deadlines and updates to further development.


# Installation
### **Steps**


1. Clone the repository
   ```bash
   git clone https://github.com/VedPeesu/SlackProjectManagmentBot.git
   ```


2. Create a virual enviroment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```


3. Set up Slack
   - Create or open an existing channel
   - Install the app to your workspace
   - Retrieve your Bot User OAuth Access Token and Signing Secret from the OAuth & Permissions section of your Slack app
  4. Add the following to your own .env file
  ```bash
  SLACK_BOT_TOKEN=xoxb-your-bot-token-here
  SIGNING_SECRET=your-signing-secret-here
   ```
5. Run the application
   ```bash
   python main.py
   ```