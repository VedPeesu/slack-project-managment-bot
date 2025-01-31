#!/bin/bash

# Slack Bot Deployment Script
echo "🚀 Deploying Enhanced Slack Project Management Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Slack Bot Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SIGNING_SECRET=your-signing-secret-here
SLACK_CHANNEL=your-channel-id-here

# Optional: Weather API (get from https://openweathermap.org/api)
WEATHER_API_KEY=your-weather-api-key-here
EOF
    echo "📝 Please edit .env file with your actual credentials"
    echo "🔗 See slack_setup.md for setup instructions"
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

# Set permissions
echo "🔐 Setting permissions..."
chmod +x main.py
chmod 600 .env

# Run tests
echo "🧪 Running tests..."
python tests.py

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Slack credentials"
echo "2. Follow the setup guide in slack_setup.md"
echo "3. Run the bot: python main.py"
echo ""
echo "🔗 Documentation: README.md"
echo "🔧 Setup Guide: slack_setup.md"
echo ""
echo "🚀 Happy coding!" 