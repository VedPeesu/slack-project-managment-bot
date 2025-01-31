import unittest
from main import app
import json
import os

class SlackBotTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        # Clear any existing data
        if os.path.exists('bot_data.json'):
            os.remove('bot_data.json')

    def tearDown(self):
        # Clean up after tests
        if os.path.exists('bot_data.json'):
            os.remove('bot_data.json')

    # Enhanced Task Management Tests
    def test_create_task_enhanced(self):
        response = self.client.post('/create-task', data={
            'text': 'Design homepage | 2024-01-15 | High | Frontend | 8',
            'user_id': 'test_user'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task created: Design homepage", response.data)
        self.assertIn(b"Priority: High", response.data)

    def test_update_task(self):
        # First create a task
        self.client.post('/create-task', data={
            'text': 'Test task',
            'user_id': 'test_user'
        })
        
        # Then update it
        response = self.client.post('/update-task', data={
            'text': '1 status completed'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task 1 updated: status = completed", response.data)

    def test_task_status(self):
        # First create a task
        self.client.post('/create-task', data={
            'text': 'Test task',
            'user_id': 'test_user'
        })
        
        response = self.client.post('/task-status', data={
            'text': '1 in_progress'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task 1 status updated to: in_progress", response.data)

    def test_list_tasks_with_filters(self):
        # Create some tasks first
        self.client.post('/create-task', data={
            'text': 'High priority task | 2024-01-15 | High | Frontend',
            'user_id': 'test_user'
        })
        self.client.post('/create-task', data={
            'text': 'Low priority task | 2024-01-20 | Low | Backend',
            'user_id': 'test_user'
        })
        
        response = self.client.post('/list-tasks', data={
            'text': 'priority:High'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"High priority task", response.data)
        self.assertNotIn(b"Low priority task", response.data)

    # Project Management Tests
    def test_create_project(self):
        response = self.client.post('/create-project', data={
            'text': 'Website Redesign | Complete overhaul | 2024-02-01 | $5000',
            'user_id': 'test_user'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Project created: Website Redesign", response.data)

    def test_project_progress(self):
        # First create a project
        self.client.post('/create-project', data={
            'text': 'Test Project | Test Description',
            'user_id': 'test_user'
        })
        
        response = self.client.post('/project-progress', data={
            'text': 'proj_1 75'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Project proj_1 progress updated to 75%", response.data)

    # Team Collaboration Tests
    def test_add_team_member(self):
        response = self.client.post('/add-team-member', data={
            'text': 'U1234567890 Developer'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Added U1234567890 to team as Developer", response.data)

    def test_team_stats(self):
        # Add a team member first
        self.client.post('/add-team-member', data={
            'text': 'U1234567890 Developer'
        })
        
        response = self.client.post('/team-stats')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Team Statistics", response.data)

    # Scheduling Tests
    def test_schedule_meeting(self):
        response = self.client.post('/schedule-meeting', data={
            'text': 'Sprint Planning | 2024-01-10 | 14:00 | 60 | user1,user2',
            'user_id': 'test_user',
            'channel_id': 'test_channel'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Meeting scheduled: Sprint Planning", response.data)

    def test_recurring_reminder(self):
        response = self.client.post('/recurring-reminder', data={
            'text': 'Check email | daily | 09:00',
            'user_id': 'test_user',
            'channel_id': 'test_channel'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Recurring reminder set: Check email", response.data)

    # File Management Tests
    def test_add_file_link(self):
        response = self.client.post('/add-file-link', data={
            'text': 'Project Docs | https://docs.example.com | Documentation',
            'user_id': 'test_user'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"File link added: Project Docs", response.data)

    def test_list_files(self):
        # Add a file first
        self.client.post('/add-file-link', data={
            'text': 'Test File | https://example.com | Test',
            'user_id': 'test_user'
        })
        
        response = self.client.post('/list-files')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Files", response.data)

    # Analytics Tests
    def test_project_analytics(self):
        response = self.client.post('/project-analytics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Project Analytics", response.data)

    # Integration Tests
    def test_motivational_quote(self):
        response = self.client.post('/motivational-quote')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Motivational Quote of the Day", response.data)

    def test_weather(self):
        response = self.client.post('/weather', data={
            'text': 'London'
        })
        self.assertEqual(response.status_code, 200)
        # Note: This will fail without a real API key, but we're testing the format

    # Smart Notifications Tests
    def test_smart_notify(self):
        response = self.client.post('/smart-notify', data={
            'text': 'Test message | task_completion | 14:00',
            'user_id': 'test_user',
            'channel_id': 'test_channel'
        })
        self.assertEqual(response.status_code, 200)
        # Will return condition not met since no high priority tasks exist

    # Legacy Tests (for backward compatibility)
    def test_assign_task(self):
        # First create a task
        self.client.post('/create-task', data={
            'text': 'Test task',
            'user_id': 'test_user'
        })
        
        response = self.client.post('/assign-task', data={'text': '1 user4'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task '1' has been assigned to 'user4'", response.data)
    
    def test_unassign_task(self):
        # First create and assign a task
        self.client.post('/create-task', data={
            'text': 'Test task',
            'user_id': 'test_user'
        })
        self.client.post('/assign-task', data={'text': '1 user4'})
        
        response = self.client.post('/unassign-task', data={'text': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task '1' has been unassigned", response.data)
    
    def test_create_project_summary(self):
        response = self.client.post('/create-project-summary', data={'text': 'Project Design, Example summary.'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Project summary for 'Project Design'", response.data)

    def test_list_project_summaries(self):
        self.client.post('/create-project-summary', data={'text': 'Project A, Summary A'})
        response = self.client.post('/list-project-summaries')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Project Summaries:", response.data)

    def test_notify_me(self):
        response = self.client.post('/notify-me', data={
            'text': 'Meeting, 12:45', 
            'user_id': 'exampleuser', 
            'channel_id': 'test_channel'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Reminder set for", response.data)
    
    def test_set_task_priority(self):
        self.client.post('/create-task', data={'text': 'Test task', 'user_id': 'test_user'})
        response = self.client.post('/task-priority', data={'text': '1 High'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Priority for task ID 1 updated to High", response.data)

    def test_list_tasks(self):
        self.client.post('/create-task', data={'text': 'Test task', 'user_id': 'test_user'})
        response = self.client.post('/list-tasks')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Tasks:", response.data)

    def test_clear_tasks(self):
        self.client.post('/create-task', data={'text': 'Test task', 'user_id': 'test_user'})
        response = self.client.post('/clear-tasks')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"All tasks have been cleared", response.data)

    def test_set_reminder(self):
        response = self.client.post('/set-reminder', data={
            'text': 'Example reminder', 
            'user_id': 'exampleuser', 
            'channel_id': 'test_channel'
        })
        self.assertEqual(response.status_code, 200)

    def test_bot_intro(self):
        response = self.client.post('/bot-intro', data={'channel_id': 'test_channel'})
        self.assertEqual(response.status_code, 200)

    def test_get_contact_info(self):
        response = self.client.post('/get-contact-info', data={'text': 'test_user'})
        self.assertEqual(response.status_code, 200)

    # Data Persistence Tests
    def test_data_persistence(self):
        # Create a task
        self.client.post('/create-task', data={
            'text': 'Persistent task',
            'user_id': 'test_user'
        })
        
        # Check if data file was created
        self.assertTrue(os.path.exists('bot_data.json'))
        
        # Read the data file
        with open('bot_data.json', 'r') as f:
            data = json.load(f)
        
        # Verify task was saved
        self.assertIn('1', data['tasks'])
        self.assertEqual(data['tasks']['1']['description'], 'Persistent task')

if __name__ == '__main__':
    unittest.main()