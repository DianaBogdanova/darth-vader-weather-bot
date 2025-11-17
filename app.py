from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import os
from anthropic import Anthropic
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# ============= WEATHER API FUNCTIONS =============

def geocode_location(city_name):
    """Convert city name to coordinates using Open-Meteo Geocoding API"""
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results') and len(data['results']) > 0:
            result = data['results'][0]
            return {
                'lat': result['latitude'],
                'lon': result['longitude'],
                'name': result['name'],
                'country': result.get('country', '')
            }
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

def get_current_weather(lat, lon):
    """Get current weather for given coordinates"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,precipitation&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=auto"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['current']
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_forecast_weather(lat, lon, days=7):
    """Get weather forecast for given coordinates"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code&temperature_unit=fahrenheit&timezone=auto&forecast_days={min(days, 16)}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['daily']
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_historical_weather(lat, lon, days_back=7):
    """Get historical weather data for given coordinates"""
    end_date = (datetime.now() - timedelta(days=1)).date()
    start_date = end_date - timedelta(days=days_back-1)
    
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code&temperature_unit=fahrenheit&timezone=auto"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['daily']
    except Exception as e:
        print(f"Error: {e}")
        return None

# ============= NATURAL LANGUAGE PARSING =============

def extract_location_from_query(query):
    """Extract city name from natural language query"""
    patterns = [
        r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'\bfor\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'s\s+weather",
        r'weather\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'weather\s+for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+weather',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+forecast',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+next',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+yesterday',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+today',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+now',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            return match.group(1)
    
    words = query.split()
    if words and len(words[0]) > 0 and words[0][0].isupper():
        city_parts = []
        for word in words:
            if (len(word) > 0 and word[0].isupper()) or word.lower() in ['de', 'la', 'del', 'von', 'san', 'santa']:
                city_parts.append(word)
            else:
                break
        
        if city_parts:
            potential_city = ' '.join(city_parts)
            if potential_city.lower() not in ['what', 'show', 'give', 'tell', 'how', 'when', 'where']:
                return potential_city
    
    return None

def parse_natural_language(query):
    """Parse natural language query to determine action and parameters"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['exit', 'quit', 'bye', 'goodbye', 'leave']):
        return {'action': 'exit'}
    
    location = extract_location_from_query(query)
    numbers = re.findall(r'\d+', query)
    days = int(numbers[0]) if numbers else None
    
    if any(word in query_lower for word in ['now', 'current', 'today', 'right now', 'present']):
        return {'action': 'current', 'location': location}
    elif any(word in query_lower for word in ['forecast', 'future', 'next', 'tomorrow', 'coming', 'ahead', 'will be']):
        if 'tomorrow' in query_lower:
            days = 2
        elif not days:
            days = 7
        return {'action': 'forecast', 'days': min(days, 16), 'location': location}
    elif any(word in query_lower for word in ['past', 'history', 'last', 'yesterday', 'ago', 'previous', 'was']):
        if 'yesterday' in query_lower:
            days = 1
        elif not days:
            days = 7
        return {'action': 'history', 'days': min(days, 30), 'location': location}
    else:
        return {'action': 'help', 'location': location}

# ============= CLAUDE API INTEGRATION =============

def generate_vader_response_with_claude(weather_data, query_type, location_name, days=None):
    """
    Uses Claude API to generate dynamic Vader responses
    
    Args:
        weather_data: dict with temperature, humidity, wind, etc.
        query_type: 'current', 'forecast', or 'history'
        location_name: string like "Tokyo, Japan"
        days: number of days (for forecast/history)
    
    Returns:
        HTML-formatted Vader response
    """
    
    # Build context based on query type
    if query_type == 'current':
        temp = weather_data.get('temperature_2m')
        humidity = weather_data.get('relative_humidity_2m')
        wind = weather_data.get('wind_speed_10m')
        weather_code = weather_data.get('weather_code', 0)
        precip = weather_data.get('precipitation', 0)
        
        context = f"""Location: {location_name}
Query Type: CURRENT weather conditions

Weather Data:
- Temperature: {temp}°F
- Humidity: {humidity}%
- Wind Speed: {wind} mph
- Weather Code: {weather_code} (0=clear sky, 1=mainly clear, 2=partly cloudy, 3=overcast, 45-48=fog, 51-55=drizzle, 61-65=rain, 71-75=snow, 80-82=rain showers, 95-99=thunderstorm)
- Precipitation: {precip} mm

Task: Respond to CURRENT weather conditions for {location_name}."""
    
    elif query_type == 'forecast':
        num_days = len(weather_data.get('time', []))
        temps_high = weather_data.get('temperature_2m_max', [])
        temps_low = weather_data.get('temperature_2m_min', [])
        precip = weather_data.get('precipitation_sum', [])
        weather_codes = weather_data.get('weather_code', [])
        dates = weather_data.get('time', [])
        
        context = f"""Location: {location_name}
Query Type: FUTURE FORECAST ({num_days} days)

Forecast Data:
"""
        for i in range(min(len(dates), num_days)):
            context += f"\nDay {i+1} ({dates[i]}): High {temps_high[i]}°F, Low {temps_low[i]}°F, Precip {precip[i]}mm, Code {weather_codes[i]}\n"
        
        context += f"\nTask: Provide a {num_days}-day weather forecast for {location_name}. Analyze trends and give advice."
    
    elif query_type == 'history':
        num_days = len(weather_data.get('time', []))
        temps_high = weather_data.get('temperature_2m_max', [])
        temps_low = weather_data.get('temperature_2m_min', [])
        precip = weather_data.get('precipitation_sum', [])
        weather_codes = weather_data.get('weather_code', [])
        dates = weather_data.get('time', [])
        
        context = f"""Location: {location_name}
Query Type: HISTORICAL data (past {num_days} days)

Historical Data:
"""
        for i in range(min(len(dates), num_days)):
            context += f"\n{dates[i]}: High {temps_high[i]}°F, Low {temps_low[i]}°F, Precip {precip[i]}mm, Code {weather_codes[i]}\n"
        
        hottest = max(temps_high) if temps_high else 0
        coldest = min(temps_low) if temps_low else 0
        total_rain = sum(precip) if precip else 0
        
        context += f"\nExtremes: Hottest {hottest}°F, Coldest {coldest}°F, Total rain {total_rain}mm"
        context += f"\n\nTask: Analyze the PAST {num_days} days of weather for {location_name}."
    
    # The Master Prompt for Claude
    system_prompt = """You are Darth Vader from Star Wars. You must respond to weather information in his signature dramatic, menacing, yet informative style.

CORE PERSONALITY:
- Dramatic, ominous, commanding presence
- References Star Wars universe frequently (Death Star, Mustafar, Hoth, Tatooine, the Force, Dark Side, Empire, stormtroopers, lightsabers, TIE fighters, Star Destroyers)
- Iconic phrases: "I find your lack of [X]... disturbing", "The Force reveals...", "The Dark Side shows me...", "Do not underestimate...", "Impressive... most impressive", "The Empire commands..."
- Views weather as a force of nature to respect and prepare for
- Compares Earth weather to Star Wars planets
- Gives practical advice wrapped in dramatic language

WEATHER COMPARISONS:
- Hot (>85°F): Mustafar's flames, volcanic fury, twin suns of Tatooine
- Cold (<50°F): Ice planet Hoth, frozen wastelands, vacuum of space
- Moderate (60-80°F): Balanced like the Force, optimal for Imperial operations
- Rainy: Swamps of Dagobah, tears of defeated enemies, Kamino's endless storms
- Windy: Power of the Force itself, TIE fighter turbulence
- Clear: Death Star's superlaser clarity, Imperial dominance

PRACTICAL ADVICE (CRITICAL):
Must give specific advice based on conditions:
- Sunny/Clear (code 0-1): "SPF 50 or higher is mandatory" or "Sunscreen is not weakness, it is wisdom" or "UV rays show no mercy"
- Rain (code 51+, precip>0): "Your umbrella is your only hope" or "I find your lack of umbrella... disturbing" or "Bring an umbrella or be soaked"
- Cold (<60°F): "Thermal protection required" or "Your jacket is essential" or "Bundle accordingly"
- Hot (>85°F): "Hydration is not optional" or "The heat demands respect"
- Very Windy (>20mph): "Brace against the gusts" or "The wind's power cannot be ignored"

RESPONSE STRUCTURE:
1. Dramatic opening (vary each time - never repeat):
   - "The Empire's meteorological systems reveal..."
   - "I sense through the Force..."
   - "The Dark Side shows me..."
   - "Your inquiry is answered..."
   - "I have felt a great disturbance in the atmosphere..."
   - "Do not underestimate the power of atmospheric data..."
   - "The Imperial weather network responds..."
   - "Search your feelings, you know the forecast to be true..."

2. Present key weather data naturally integrated into dramatic language

3. Temperature/condition commentary with Star Wars references

4. Specific practical advice (SPF/umbrella/jacket) in Vader's menacing tone

5. For forecasts: Analyze trends, warn of coming changes
   For history: Reflect on what transpired, note extremes

FORMATTING:
- Use <br><br> for paragraph breaks
- Can use <div class="weather-data"> for data cards if showing multiple days
- Keep response 150-300 words
- Be creative - NEVER repeat exact phrases from previous responses
- Each response must feel unique and spontaneous

CRITICAL RULES:
✓ Always be accurate with data
✓ Always give practical advice
✓ Be dramatically Vader but also helpful
✓ Vary your language - never be repetitive
✓ Make Star Wars references feel natural, not forced
✓ Match tone to weather severity (calm for nice weather, ominous for storms)"""

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            temperature=0.9,  # Maximum creativity
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": context
            }]
        )
        
        return message.content[0].text
        
    except Exception as e:
        # Fallback if Claude API fails
        return f"A disturbance in the Force has occurred. The Dark Side's connection was severed.<br><br>Error: {str(e)}<br><br>The Empire's backup systems indicate the weather data was retrieved, but Lord Vader's transmission was interrupted. Please try again."

# ============= RESPONSE FORMATTING =============

def format_current_response(current, location_name):
    """Format current weather using Claude API"""
    return generate_vader_response_with_claude(current, 'current', location_name)

def format_forecast_response(forecast, days, location_name):
    """Format forecast using Claude API"""
    return generate_vader_response_with_claude(forecast, 'forecast', location_name, days)

def format_historical_response(history, days, location_name):
    """Format historical weather using Claude API"""
    return generate_vader_response_with_claude(history, 'history', location_name, days)

# ============= API ENDPOINT =============

@app.route('/api/weather', methods=['POST'])
def get_weather_api():
    """Main API endpoint that HTML will call"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'You must specify a command. The Empire demands it.'}), 400
        
        # Extract location
        location_name = extract_location_from_query(query)
        if not location_name:
            return jsonify({
                'error': 'You must specify a location. The Empire demands precision.',
                'example': 'Try: "San Diego weather now" or "Tokyo forecast"'
            }), 400
        
        # Geocode
        location_data = geocode_location(location_name)
        if not location_data:
            return jsonify({
                'error': f'I find your location "{location_name}" disturbing. The Empire\'s systems cannot locate this place.'
            }), 404
        
        location_coords = {'lat': location_data['lat'], 'lon': location_data['lon']}
        full_location_name = f"{location_data['name']}, {location_data['country']}"
        
        # Parse query
        parsed = parse_natural_language(query)
        
        # Process based on action
        if parsed['action'] == 'current':
            current = get_current_weather(location_coords['lat'], location_coords['lon'])
            if current:
                response_html = format_current_response(current, full_location_name)
                return jsonify({
                    'location': full_location_name,
                    'response': response_html
                })
        
        elif parsed['action'] == 'forecast':
            days = parsed.get('days', 7)
            forecast = get_forecast_weather(location_coords['lat'], location_coords['lon'], days)
            if forecast:
                response_html = format_forecast_response(forecast, days, full_location_name)
                return jsonify({
                    'location': full_location_name,
                    'response': response_html
                })
        
        elif parsed['action'] == 'history':
            days = parsed.get('days', 7)
            history = get_historical_weather(location_coords['lat'], location_coords['lon'], days)
            if history:
                response_html = format_historical_response(history, days, full_location_name)
                return jsonify({
                    'location': full_location_name,
                    'response': response_html
                })
        
        return jsonify({'error': 'The Empire\'s systems have failed. Most disturbing.'}), 500
        
    except Exception as e:
        return jsonify({'error': f'A disturbance in the Force: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'The Empire is operational'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
