import requests
from datetime import datetime, timedelta
import random
import re

def get_current_weather():
    latitude = 32.7157
    longitude = -117.1611
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=America/Los_Angeles"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['current']
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_forecast_weather(days=7):
    latitude = 32.7157
    longitude = -117.1611
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code&temperature_unit=fahrenheit&timezone=America/Los_Angeles&forecast_days={days}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['daily']
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_natural_language(query):
    query_lower = query.lower()
    if any(word in query_lower for word in ['exit', 'quit', 'bye']):
        return {'action': 'exit'}
    numbers = re.findall(r'\d+', query)
    days = int(numbers[0]) if numbers else None
    if any(word in query_lower for word in ['now', 'current', 'today']):
        return {'action': 'current'}
    elif any(word in query_lower for word in ['forecast', 'future', 'next']):
        return {'action': 'forecast', 'days': days or 7}
    else:
        return {'action': 'help'}

def display_current():
    print("\n" + "="*70)
    print("⚫ CURRENT CONDITIONS - SAN DIEGO ⚫")
    print("="*70)
    current = get_current_weather()
    if current:
        print(f"\n⚫ Darth Vader: The Empire's systems reveal...")
        print(f"  🌡️  Temperature: {current['temperature_2m']}°F")
        print(f"  💧 Humidity: {current['relative_humidity_2m']}%")
        print(f"  💨 Wind: {current['wind_speed_10m']} mph")
    print("="*70)

def weather_chatbot():
    print("\n⚫ DARTH VADER - IMPERIAL WEATHER COMMAND ⚫")
    print("Examples: 'current weather', 'next 5 days'\n")
    
    while True:
        user_input = input("⚫ You: ").strip()
        if not user_input:
            continue
        
        parsed = parse_natural_language(user_input)
        
        if parsed['action'] == 'exit':
            print("\n⚫ Darth Vader: The Force will be with you... always. ⚫\n")
            break
        elif parsed['action'] == 'current':
            display_current()
        else:
            print("⚫ Ask about 'current weather' or type 'exit'\n")

if __name__ == "__main__":
    weather_chatbot()
