import requests
from datetime import datetime, timedelta
import random
import re

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

def get_weather_description(code):
    """Convert weather code to description"""
    weather_codes = {
        0: "☀️ Clear", 1: "🌤️ Mostly Clear", 2: "⛅ Partly Cloudy", 
        3: "☁️ Overcast", 45: "🌫️ Foggy", 48: "🌫️ Foggy",
        51: "🌦️ Light Drizzle", 53: "🌦️ Drizzle", 55: "🌧️ Heavy Drizzle",
        61: "🌧️ Light Rain", 63: "🌧️ Rain", 65: "🌧️ Heavy Rain",
        71: "🌨️ Light Snow", 73: "❄️ Snow", 75: "❄️ Heavy Snow",
        80: "🌦️ Rain Showers", 81: "⛈️ Rain Showers", 82: "⛈️ Heavy Rain Showers",
        95: "⛈️ Thunderstorm", 96: "⛈️ Thunderstorm + Hail", 99: "⛈️ Severe Thunderstorm"
    }
    return weather_codes.get(code, "❓ Unknown")

def vader_intro():
    """Darth Vader introduction phrases"""
    intros = [
        "The Empire's meteorological systems reveal",
        "I sense through the Force",
        "The Dark Side shows me",
        "Your inquiry is answered",
        "The atmospheric patterns are clear",
        "I have felt a great disturbance in the atmosphere",
        "The power of the Empire's satellites is absolute",
        "The Imperial weather network responds",
        "Search your feelings, you know the forecast to be true",
        "Do not underestimate the power of atmospheric data",
        "The circle is now complete. The weather data unfolds",
        "I find your meteorological curiosity... impressive",
        "The Force flows through these readings",
        "Your lack of weather knowledge ends now",
        "Impressive... most impressive. The data reveals"
    ]
    return random.choice(intros)

def extract_location_from_query(query):
    """Extract city name from natural language query"""
    # Common patterns: "in [city]", "for [city]", "[city]'s weather", "weather in [city]"
    patterns = [
        r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "in Paris"
        r'\bfor\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "for London"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'s\s+weather",  # "Tokyo's weather"
        r'weather\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "weather in Berlin"
        r'weather\s+for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "weather for Madrid"
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+weather',  # "Barcelona weather"
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+forecast',  # "Tokyo forecast"
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+next',  # "London next 5 days"
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+yesterday',  # "Paris yesterday"
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+today',  # "Rome today"
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+now',  # "Sydney now"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            return match.group(1)
    
    # If no pattern matches, check if query starts with a capitalized word
    # This handles cases like "Barcelona weather in 3 days"
    words = query.split()
    if words and len(words[0]) > 0 and words[0][0].isupper():
        # Take consecutive capitalized words
        city_parts = []
        for word in words:
            # Check if word is capitalized or is a common connector in city names
            if (len(word) > 0 and word[0].isupper()) or word.lower() in ['de', 'la', 'del', 'von', 'san', 'santa']:
                city_parts.append(word)
            else:
                break
        
        if city_parts:
            potential_city = ' '.join(city_parts)
            # Don't return if it's just a question word
            if potential_city.lower() not in ['what', 'show', 'give', 'tell', 'how', 'when', 'where']:
                return potential_city
    
    return None

def parse_natural_language(query):
    """Parse natural language query to determine action and parameters"""
    query_lower = query.lower()
    
    # Check for exit commands
    if any(word in query_lower for word in ['exit', 'quit', 'bye', 'goodbye', 'leave']):
        return {'action': 'exit'}
    
    # Extract location from query
    location = extract_location_from_query(query)
    
    # Extract numbers for days
    numbers = re.findall(r'\d+', query)
    days = int(numbers[0]) if numbers else None
    
    # Determine query type
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

def get_weather_advice(weather_code, temp, precip):
    """Generate Vader-style weather advice based on conditions"""
    advice = []
    
    # Sunny/Clear conditions - SPF advice
    if weather_code in [0, 1]:
        spf_comments = [
            "The sun's rays are merciless. SPF protection is not weakness... it is wisdom.",
            "Do not underestimate the power of UV radiation. Apply sunscreen, or suffer the consequences.",
            "The star at the center of this system burns bright. Your skin is vulnerable. Protect it with SPF.",
            "Even the Dark Side respects the sun's power. Sunscreen is your shield against solar domination.",
            "I find your lack of sunscreen... disturbing. The UV rays show no mercy.",
            "SPF 50 or higher. This is not a request. It is a command from the Empire.",
            "The sun is as relentless as my pursuit of the Rebels. Defend yourself with sunscreen.",
            "Your epidermis will betray you without SPF. The sun's power is absolute."
        ]
        advice.append(random.choice(spf_comments))
    
    # Rainy conditions - umbrella advice
    if weather_code >= 51 or precip > 0.1:
        umbrella_comments = [
            "The skies will weep. Your umbrella is your only hope against the deluge.",
            "Rain falls like the tears of the Rebel Alliance. I find your lack of umbrella... disturbing.",
            "Precipitation is imminent. An umbrella would serve the Empire well in these conditions.",
            "The clouds rebel against us. Bring an umbrella, or be soaked like a defeated enemy.",
            "Water descends from above. Your umbrella is as essential as a lightsaber to a Sith Lord.",
            "The heavens cry out. Without an umbrella, you will be as drenched as the swamps of Dagobah.",
            "Rain approaches with the certainty of Imperial victory. An umbrella is not optional.",
            "The storm comes. Your umbrella will be your shield, or you will suffer the wetness of failure.",
            "I sense moisture in the air. Much moisture. Bring your umbrella, young one.",
            "The precipitation will show no mercy. Neither should you. Pack an umbrella immediately."
        ]
        advice.append(random.choice(umbrella_comments))
    
    # Heavy rain - extra warning
    if weather_code >= 63 or precip > 5:
        heavy_rain_comments = [
            "The deluge will be torrential. This is no mere drizzle. Prepare for aquatic warfare.",
            "Heavy rain approaches with the force of a Star Destroyer. Your umbrella may prove inadequate.",
            "The skies open like the gates of the Death Star. Waterproof defenses are mandatory.",
            "This is not rain. This is nature's bombardment. The Empire recommends staying indoors."
        ]
        advice.append(random.choice(heavy_rain_comments))
    
    # Cold temperatures - jacket advice
    if temp < 60:
        cold_comments = [
            "The cold is as penetrating as the vacuum of space. A jacket is required.",
            "The temperature falls like a TIE fighter in battle. Thermal protection is essential.",
            "I sense a disturbance in the temperature. The cold side is strong. Bundle accordingly.",
            "Even Hoth was barely colder. Your jacket is not a suggestion, it is survival."
        ]
        advice.append(random.choice(cold_comments))
    
    return advice

def get_rain_commentary(precip, weather_code):
    """Get varied rain commentary"""
    if weather_code >= 80 or precip > 10:  # Heavy rain/storms
        comments = [
            "The storm rages with the fury of the Dark Side itself.",
            "Rain hammers down like blaster fire in the heat of battle.",
            "The skies unleash their full power. Even the Empire bows to this tempest.",
            "A deluge worthy of legends. The clouds have declared total war.",
            "This is no ordinary rain. This is atmospheric domination."
        ]
    elif weather_code >= 61 or precip > 3:  # Moderate rain
        comments = [
            "The rain falls steadily, like the march of stormtroopers across a conquered world.",
            "Precipitation descends with purpose. The clouds know their duty.",
            "The skies weep, but not from weakness. From power.",
            "Rain claims the atmosphere as the Empire claims the galaxy.",
            "Water falls as inevitably as the fall of the Rebellion."
        ]
    elif precip > 0:  # Light rain
        comments = [
            "A light drizzle disturbs the air. Insignificant, yet persistent.",
            "Minimal precipitation. The clouds show restraint... for now.",
            "A gentle rain, like the whisper of defeat in my enemies' ears.",
            "The moisture is light, but do not be deceived. It accumulates."
        ]
    else:
        comments = [
            "The skies remain obedient. No rain dares to fall.",
            "Dry conditions prevail. The Empire has commanded it so.",
            "Not a drop shall descend. The atmosphere bends to our will."
        ]
    
    return random.choice(comments)

def get_forecast_opening(days):
    """Get varied forecast opening statements"""
    openings = [
        f"I have foreseen the next {days} days. The future is clear to me",
        f"The Force reveals what lies ahead. {days} days of atmospheric destiny await",
        f"Your future for the next {days} days is unavoidable. It has been foreseen",
        f"The prophecy of the next {days} days unfolds before me. Listen well",
        f"I see through the veil of time. {days} days hence, the weather will be thus",
        f"The Dark Side grants me vision of the coming {days} days. Heed my words",
        f"The future bends to my will. Here is what the next {days} days hold",
        f"Time flows forward, and I see all. The next {days} days are mine to command"
    ]
    return random.choice(openings)

def get_historical_opening(days):
    """Get varied historical opening statements"""
    openings = [
        f"The archives reveal the past {days} days. Nothing escapes the Empire's memory",
        f"I remember the past {days} days as clearly as the destruction of Alderaan",
        f"The Force never forgets. Neither do I. The past {days} days are recorded thus",
        f"Let me tell you of the {days} days that have passed. Every detail is preserved",
        f"The Empire's records are eternal. The past {days} days are laid bare before you",
        f"Time moves forward, but the past remains frozen. The last {days} days were thus",
        f"Search the Imperial archives. The past {days} days are documented with absolute precision",
        f"I sense you seek knowledge of what was. The past {days} days cannot be changed, only understood"
    ]
    return random.choice(openings)

def get_historical_closing():
    """Get varied historical closing statements"""
    closings = [
        "The past is unchangeable, like fate itself. What has been cannot be altered.",
        "These days are now history, preserved forever in the Empire's eternal memory.",
        "What has occurred is carved in stone. Learn from it, or be doomed to repeat it.",
        "The past flows behind us like the wake of a Star Destroyer. Immutable. Absolute.",
        "Time marches forward, but history remains. The Empire remembers all.",
        "These atmospheric records are as permanent as carbonite. Study them well.",
        "The Force preserves all that has transpired. Nothing is ever truly forgotten.",
        "What was, will always have been. The past is the Dark Side's eternal domain."
    ]
    return random.choice(closings)


def display_current(current, location_name):
    """Display current weather with Vader commentary"""
    print("\n" + "=" * 70)
    print(f"⚫ CURRENT CONDITIONS - {location_name.upper()} ⚫")
    print("=" * 70)
    
    if current:
        temp = current['temperature_2m']
        humidity = current['relative_humidity_2m']
        wind = current['wind_speed_10m']
        weather_code = current.get('weather_code', 0)
        precip = current.get('precipitation', 0)
        
        print(f"\n⚫ Darth Vader: {vader_intro()}...")
        print(f"\n  🌡️  Temperature: {temp}°F")
        print(f"  💧 Humidity: {humidity}%")
        print(f"  💨 Wind Speed: {wind} mph")
        print(f"  {get_weather_description(weather_code)}")
        print(f"  🕐 Time: {current['time']}")
        
        # Temperature commentary - more variety
        if temp > 95:
            comments = [
                f"The heat is devastating at {temp}°F. Like standing on the surface of a star.",
                f"{temp}°F. Even Tatooine's twin suns would be impressed by this inferno.",
                f"The temperature reaches {temp}°F. Oppressive. Merciless. Like the Empire itself."
            ]
        elif temp > 85:
            comments = [
                f"The heat is oppressive at {temp}°F. Like the flames that consumed me on Mustafar.",
                f"{temp}°F. The sun's power rivals that of the Death Star's superlaser.",
                f"At {temp}°F, the air burns. This is the temperature of conquest and domination."
            ]
        elif temp > 75:
            comments = [
                f"{temp}°F. A pleasant warmth. The Force is balanced today.",
                f"At {temp}°F, conditions are optimal for Imperial operations.",
                f"The temperature stands at {temp}°F. Acceptable. The Dark Side approves.",
                f"{temp}°F. Comfortable, yet I remain ever vigilant. As should you."
            ]
        elif temp > 65:
            comments = [
                f"{temp}°F. Mild conditions. Do not be deceived by this comfort.",
                f"The temperature registers at {temp}°F. Adequate, but unremarkable.",
                f"At {temp}°F, the weather serves neither hot nor cold. Balanced, like the Force should be.",
                f"{temp}°F. Temperate. But remember: comfort breeds complacency."
            ]
        elif temp > 50:
            comments = [
                f"The cold grips at {temp}°F. I find your lack of warm clothing... disturbing.",
                f"At {temp}°F, the chill of the Dark Side begins to manifest.",
                f"{temp}°F. Cool enough to remind you that the universe is cold and unforgiving.",
                f"The temperature falls to {temp}°F. The cold side grows stronger."
            ]
        else:
            comments = [
                f"The cold dominates at {temp}°F. Like the icy void between stars.",
                f"At {temp}°F, even Hoth seems welcoming. Bundle your defenses.",
                f"{temp}°F. The freeze is absolute. The Dark Side chills to the bone.",
                f"The temperature plummets to {temp}°F. This is the cold of death itself."
            ]
        
        print(f"\n⚫ Darth Vader: {random.choice(comments)}")
        
        # Wind commentary - more variety
        if wind > 30:
            wind_comments = [
                f"The winds scream at {wind} mph! Hurricane-force power tears through the atmosphere!",
                f"At {wind} mph, the very air rebels! Even Star Destroyers would struggle in this tempest!",
                f"Winds of {wind} mph. Nature unleashes its full fury. Impressive... most impressive."
            ]
            print(f"⚫ Darth Vader: {random.choice(wind_comments)}")
        elif wind > 20:
            wind_comments = [
                f"The winds rage at {wind} mph. Strong, like the power of the Dark Side.",
                f"At {wind} mph, these gusts could scatter stormtroopers. Show respect for this force.",
                f"Winds of {wind} mph tear through the atmosphere. The Force itself pushes against you.",
                f"{wind} mph winds. Even my cape billows dramatically in this power."
            ]
            print(f"⚫ Darth Vader: {random.choice(wind_comments)}")
        elif wind > 10:
            wind_comments = [
                f"The wind blows at {wind} mph. A moderate force, yet not to be ignored.",
                f"Winds at {wind} mph. The atmosphere stirs, like the whispers of the Force.",
                f"{wind} mph. The breeze carries the will of the Empire across the land."
            ]
            print(f"⚫ Darth Vader: {random.choice(wind_comments)}")
        
        # Rain commentary if applicable
        if weather_code >= 51 or precip > 0:
            print(f"⚫ Darth Vader: {get_rain_commentary(precip, weather_code)}")
        
        # Humidity commentary
        if humidity > 85:
            humidity_comments = [
                f"Humidity at {humidity}%. The air is thick, oppressive... like the grip of the Empire.",
                f"{humidity}% humidity. The moisture suffocates, much like my own mechanical breathing.",
                f"The humidity chokes at {humidity}%. Even breathing becomes a battle."
            ]
            print(f"⚫ Darth Vader: {random.choice(humidity_comments)}")
        
        # Weather-specific advice
        advice = get_weather_advice(weather_code, temp, precip)
        for comment in advice:
            print(f"⚫ Darth Vader: {comment}")
    
    print("=" * 70)

def display_forecast(forecast, days, location_name):
    """Display forecast with Vader commentary"""
    print("\n" + "=" * 70)
    print(f"⚫ {days}-DAY FORECAST - {location_name.upper()} ⚫")
    print("=" * 70)
    
    print(f"\n⚫ Darth Vader: {get_forecast_opening(days)}...")
    
    if forecast:
        sunny_days = 0
        rainy_days = 0
        total_precip = 0
        
        for i in range(len(forecast['time'])):
            weather_code = forecast['weather_code'][i]
            precip = forecast['precipitation_sum'][i]
            
            if weather_code in [0, 1]:
                sunny_days += 1
            if weather_code >= 51 or precip > 0:
                rainy_days += 1
                total_precip += precip
            
            print(f"\n📆 {forecast['time'][i]}")
            print(f"   🌡️  High: {forecast['temperature_2m_max'][i]}°F | Low: {forecast['temperature_2m_min'][i]}°F")
            print(f"   {get_weather_description(weather_code)}")
            if precip > 0:
                print(f"   💧 Precipitation: {precip} mm")
        
        avg_high = sum(forecast['temperature_2m_max']) / len(forecast['temperature_2m_max'])
        avg_low = sum(forecast['temperature_2m_min']) / len(forecast['temperature_2m_min'])
        
        summary_comments = [
            f"The average high will be {avg_high:.1f}°F, with lows of {avg_low:.1f}°F. Plan your strategies accordingly.",
            f"Temperatures will range from {avg_low:.1f}°F to {avg_high:.1f}°F. The Empire demands preparedness.",
            f"Expect an average high of {avg_high:.1f}°F. The forecast bends to my will.",
            f"The thermal readings average {avg_high:.1f}°F at peak. Adjust your plans to this reality."
        ]
        print(f"\n⚫ Darth Vader: {random.choice(summary_comments)}")
        
        # Overall forecast advice
        if sunny_days > days / 2:
            sun_summary = [
                f"{sunny_days} days of sun ahead. The UV rays will be relentless. SPF protection is mandatory.",
                f"The sun dominates {sunny_days} of the coming days. Its power is absolute. Defend yourself with sunscreen.",
                f"{sunny_days} days of clear skies. Do not mistake beauty for safety. The sun shows no mercy.",
                f"Clear conditions prevail for {sunny_days} days. The solar radiation will be merciless. Prepare accordingly."
            ]
            print(f"⚫ Darth Vader: {random.choice(sun_summary)}")
        
        if rainy_days > days / 2:
            rain_summary = [
                f"{rainy_days} days of rain dominate this period. Total precipitation: {total_precip:.1f}mm. Your umbrella is essential.",
                f"The clouds rebel for {rainy_days} days. {total_precip:.1f}mm will fall. I find your lack of umbrella disturbing.",
                f"Rain claims {rainy_days} of these days. {total_precip:.1f}mm from the heavens. Waterproof defenses required.",
                f"{rainy_days} days of wetness await. The skies will weep {total_precip:.1f}mm. Be prepared, or be soaked."
            ]
            print(f"⚫ Darth Vader: {random.choice(rain_summary)}")
        elif rainy_days > 0:
            rain_mention = [
                f"{rainy_days} day(s) of rain approach. Do not forget your umbrella on those days.",
                f"Rain threatens on {rainy_days} day(s). Vigilance and an umbrella will serve you well.",
                f"{rainy_days} day(s) will see precipitation. The prepared survive. The unprepared suffer."
            ]
            print(f"⚫ Darth Vader: {random.choice(rain_mention)}")
        
        if rainy_days == 0 and sunny_days < days / 2:
            cloudy_summary = [
                "No rain foreseen, yet clouds may linger. The skies remain neutral.",
                "Dry conditions throughout. The clouds hold their water, as if commanded by the Empire.",
                "The forecast shows no precipitation. The atmosphere remains under control."
            ]
            print(f"⚫ Darth Vader: {random.choice(cloudy_summary)}")
    
    print("=" * 70)


def display_historical(history, days, location_name):
    """Display historical weather with Vader commentary"""
    print("\n" + "=" * 70)
    print(f"⚫ PAST {days} DAYS - {location_name.upper()} ⚫")
    print("=" * 70)
    
    print(f"\n⚫ Darth Vader: {get_historical_opening(days)}...")
    
    if history:
        coldest = min(history['temperature_2m_min'])
        hottest = max(history['temperature_2m_max'])
        total_rain = sum(history['precipitation_sum'])
        rainy_days = sum(1 for p in history['precipitation_sum'] if p > 0)
        
        for i in range(len(history['time'])):
            print(f"\n📆 {history['time'][i]}")
            print(f"   🌡️  High: {history['temperature_2m_max'][i]}°F | Low: {history['temperature_2m_min'][i]}°F")
            print(f"   {get_weather_description(history['weather_code'][i])}")
            if history['precipitation_sum'][i] > 0:
                print(f"   💧 Precipitation: {history['precipitation_sum'][i]} mm")
        
        # Historical analysis
        analysis = [
            f"\n⚫ Darth Vader: {get_historical_closing()}",
        ]
        
        if hottest > 90:
            heat_comments = [
                f"The hottest moment reached {hottest}°F. Even the sun bowed to the Dark Side during that hour.",
                f"Peak temperature: {hottest}°F. The heat was oppressive, as it should be.",
                f"{hottest}°F at maximum. The atmosphere burned with Imperial fury."
            ]
            analysis.append(f"⚫ Darth Vader: {random.choice(heat_comments)}")
        
        if coldest < 40:
            cold_comments = [
                f"The coldest moment fell to {coldest}°F. The icy grip of the Dark Side was strong.",
                f"Minimum temperature: {coldest}°F. The cold was as penetrating as the void of space.",
                f"{coldest}°F at the lowest. Even Hoth would respect such temperatures."
            ]
            analysis.append(f"⚫ Darth Vader: {random.choice(cold_comments)}")
        
        if total_rain > 20:
            rain_comments = [
                f"Much rain fell - {total_rain:.1f}mm across {rainy_days} day(s). The clouds showed their dominance.",
                f"The skies wept {total_rain:.1f}mm over {rainy_days} day(s). The precipitation was... substantial.",
                f"{total_rain:.1f}mm of rain descended. The atmosphere demonstrated its power over {rainy_days} day(s).",
                f"Total precipitation: {total_rain:.1f}mm. The clouds released their burden over {rainy_days} day(s) of wetness."
            ]
            analysis.append(f"⚫ Darth Vader: {random.choice(rain_comments)}")
        elif total_rain > 0:
            rain_comments = [
                f"Some rain fell - {total_rain:.1f}mm over {rainy_days} day(s). A minor disturbance in the atmosphere.",
                f"{rainy_days} day(s) saw precipitation. Total: {total_rain:.1f}mm. Insignificant, yet recorded.",
                f"Light rain appeared on {rainy_days} day(s). {total_rain:.1f}mm total. The clouds showed restraint."
            ]
            analysis.append(f"⚫ Darth Vader: {random.choice(rain_comments)}")
        else:
            dry_comments = [
                "Not a single drop of rain fell. The skies remained obedient to the Empire's will.",
                "Zero precipitation. The atmosphere knew its place. Dry and compliant.",
                "The clouds held their water. Complete atmospheric discipline throughout this period."
            ]
            analysis.append(f"⚫ Darth Vader: {random.choice(dry_comments)}")
        
        for line in analysis:
            print(line)
    
    print("=" * 70)

def show_help():
    """Show example queries"""
    print("\n⚫ Darth Vader: Speak clearly. Here are acceptable commands:")
    print("\n  • 'What's the weather in Tokyo now?'")
    print("  • 'Show me London's forecast for next 5 days'")
    print("  • 'What was Paris weather yesterday?'")
    print("  • 'Current weather in San Diego'")
    print("  • 'New York forecast for tomorrow'")
    print("  • 'Exit' - to leave\n")

def weather_chatbot():
    """Main weather chatbot with single input for location and query"""
    print("\n" + "=" * 70)
    print("⚫ DARTH VADER - IMPERIAL WEATHER COMMAND ⚫")
    print("=" * 70)
    print("⚫ Darth Vader: Ask about any location. The Force will understand.")
    print("=" * 70)
    print("\nExamples: 'Tokyo weather now', 'London next 5 days', 'Paris yesterday'\n")
    
    while True:
        user_input = input("⚫ Command: ").strip()
        
        if not user_input:
            continue
        
        parsed = parse_natural_language(user_input)
        
        if parsed['action'] == 'exit':
            print("\n⚫ Darth Vader: The Force will be with you... always. ⚫\n")
            break
        
        # Get location from query
        location_name = parsed.get('location')
        
        if not location_name:
            print("\n⚫ Darth Vader: You must specify a location. The Empire demands precision.")
            print("   Example: 'San Diego weather now' or 'Tokyo forecast'\n")
            continue
        
        print(f"\n[Accessing Imperial systems for {location_name}...]")
        location_data = geocode_location(location_name)
        
        if not location_data:
            print(f"\n⚫ Darth Vader: I find your location '{location_name}' disturbing. The Empire cannot locate this place.\n")
            continue
        
        location_coords = {'lat': location_data['lat'], 'lon': location_data['lon']}
        full_location_name = f"{location_data['name']}, {location_data['country']}"
        
        if parsed['action'] == 'current':
            print("\n[Consulting the Dark Side...]")
            current = get_current_weather(location_coords['lat'], location_coords['lon'])
            if current:
                display_current(current, full_location_name)
            else:
                print("\n⚫ Darth Vader: The Empire's systems have failed. Most disturbing.\n")
        
        elif parsed['action'] == 'forecast':
            days = parsed.get('days', 7)
            print("\n[Consulting the Dark Side...]")
            forecast = get_forecast_weather(location_coords['lat'], location_coords['lon'], days)
            if forecast:
                display_forecast(forecast, days, full_location_name)
            else:
                print("\n⚫ Darth Vader: The forecast is clouded. Try again.\n")
        
        elif parsed['action'] == 'history':
            days = parsed.get('days', 7)
            print("\n[Accessing Imperial archives...]")
            history = get_historical_weather(location_coords['lat'], location_coords['lon'], days)
            if history:
                display_historical(history, days, full_location_name)
            else:
                print("\n⚫ Darth Vader: The archives have been corrupted.\n")
        
        elif parsed['action'] == 'help':
            show_help()
        
        print()

if __name__ == "__main__":
    weather_chatbot()
    
