import requests
import random
from flask import request

def get_weather():
    """Get weather information for a city"""
    data = request.form
    command_text = data.get('text', '').strip()
    
    if not command_text:
        return "Format: /weather <city>"
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={command_text}&appid=YOUR_API_KEY&units=metric"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            weather_data = response.json()
            temp = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
            humidity = weather_data['main']['humidity']
            
            return f"🌤️ Weather in {command_text}:\n🌡️ Temperature: {temp}°C\n☁️ Conditions: {description}\n💧 Humidity: {humidity}%"
        else:
            return f"❌ Could not fetch weather for {command_text}"
    except:
        return f"❌ Error fetching weather data for {command_text}"

def get_motivational_quote():
    """Get a random motivational quote"""
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
        "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt"
    ]
    
    quote = random.choice(quotes)
    return f"💪 **Motivational Quote of the Day:**\n\n> {quote}" 