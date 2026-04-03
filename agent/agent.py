import os
import httpx

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

CITIES = {
    "tokyo": ("JP", 35.68, 139.69),
    "paris": ("FR", 48.85, 2.35),
    "london": ("GB", 51.51, -0.13),
    "new york": ("US", 40.71, -74.01),
    "mumbai": ("IN", 19.07, 72.87),
    "dubai": ("AE", 25.20, 55.27),
    "sydney": ("AU", -33.87, 151.21),
    "hyderabad": ("IN", 17.38, 78.47),
    "delhi": ("IN", 28.61, 77.21),
    "singapore": ("SG", 1.35, 103.82),
    "bangkok": ("TH", 13.75, 100.52),
    "berlin": ("DE", 52.52, 13.40),
    "toronto": ("CA", 43.65, -79.38),
    "seoul": ("KR", 37.57, 126.98),
    "rome": ("IT", 41.90, 12.50),
    "amsterdam": ("NL", 52.37, 4.90),
    "barcelona": ("ES", 41.39, 2.16),
    "istanbul": ("TR", 41.01, 28.95),
    "cairo": ("EG", 30.04, 31.24),
    "cape town": ("ZA", -33.92, 18.42)
}

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
    3: "Overcast", 45: "Foggy", 61: "Light rain",
    63: "Moderate rain", 80: "Rain showers", 95: "Thunderstorm"
}

BEST_TIME = {
    "JP": "March-May (Cherry Blossom) or Oct-Nov",
    "FR": "April-June or September-October",
    "GB": "May-September",
    "US": "April-June or September-November",
    "IN": "October-March",
    "AE": "November-March",
    "AU": "September-November or March-May",
    "SG": "February-April",
    "TH": "November-February",
    "DE": "May-September",
    "CA": "June-August",
    "KR": "March-May or September-November",
    "IT": "April-June or September-October",
    "NL": "April-May or June-August",
    "ES": "April-June or September-October",
    "TR": "April-May or September-October",
    "EG": "October-April",
    "ZA": "May-September"
}

SAFETY = {
    "JP": "Very Safe", "FR": "Safe", "GB": "Very Safe",
    "US": "Moderate", "IN": "Moderate", "AE": "Very Safe",
    "AU": "Very Safe", "SG": "Very Safe", "TH": "Safe",
    "DE": "Very Safe", "CA": "Very Safe", "KR": "Very Safe",
    "IT": "Safe", "NL": "Very Safe", "ES": "Safe",
    "TR": "Moderate", "EG": "Moderate", "ZA": "Moderate"
}

LOCAL_PHRASES = {
    "JP": "Konnichiwa (Hello), Arigato (Thank you)",
    "FR": "Bonjour (Hello), Merci (Thank you)",
    "GB": "Cheers (Thank you), Brilliant (Great)",
    "US": "Howdy (Hello), You bet (Sure)",
    "IN": "Namaste (Hello), Shukriya (Thank you)",
    "AE": "Marhaba (Hello), Shukran (Thank you)",
    "AU": "G'day (Hello), No worries (You're welcome)",
    "SG": "Lah (emphasis), Shiok (Amazing)",
    "TH": "Sawasdee (Hello), Khob Khun (Thank you)",
    "DE": "Hallo (Hello), Danke (Thank you)",
    "CA": "Sorry (Hello lol), Thanks (Thank you)",
    "KR": "Annyeong (Hello), Gamsahamnida (Thank you)",
    "IT": "Ciao (Hello), Grazie (Thank you)",
    "NL": "Hoi (Hello), Dank je (Thank you)",
    "ES": "Hola (Hello), Gracias (Thank you)",
    "TR": "Merhaba (Hello), Tesekkur (Thank you)",
    "EG": "Ahlan (Hello), Shukran (Thank you)",
    "ZA": "Howzit (How are you), Lekker (Nice)"
}


async def get_weather(city, lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weathercode,windspeed_10m,relative_humidity_2m"
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url, params=params)
            data = r.json()
        current = data["current"]
        condition = WEATHER_CODES.get(current["weathercode"], "Clear")
        return {
            "temperature": current["temperature_2m"],
            "wind": current["windspeed_10m"],
            "humidity": current["relative_humidity_2m"],
            "condition": condition
        }
    except Exception as e:
        return {"temperature": "N/A", "wind": "N/A", "humidity": "N/A", "condition": "N/A"}


async def get_city_highlights(city):
    city_formatted = city.replace(" ", "_").title()
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city_formatted}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url)
            data = r.json()
        return data.get("extract", "A wonderful city to explore!")[:600]
    except Exception:
        return "A wonderful city to explore!"


async def get_country_info(country_code):
    url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url)
            data = r.json()[0]
        languages = list(data.get("languages", {}).values())[:2]
        currencies = [v["name"] for v in data.get("currencies", {}).values()]
        capital = data.get("capital", [""])[0]
        country_name = data["name"]["common"]
        population = data.get("population", 0)
        return {
            "country": country_name,
            "capital": capital,
            "languages": ", ".join(languages),
            "currencies": ", ".join(currencies),
            "population": f"{population:,}"
        }
    except Exception:
        return {"country": "Unknown", "capital": "Unknown", "languages": "Unknown", "currencies": "Unknown", "population": "Unknown"}


async def run_agent(question):
    city = "hyderabad"
    for c in CITIES:
        if c in question.lower():
            city = c
            break

    country_code, lat, lon = CITIES[city]

    weather = await get_weather(city, lat, lon)
    highlights = await get_city_highlights(city)
    country = await get_country_info(country_code)
    best_time = BEST_TIME.get(country_code, "Year round")
    safety = SAFETY.get(country_code, "Check travel advisories")
    phrases = LOCAL_PHRASES.get(country_code, "Learn a few local words!")

    prompt = "You are CityPulse, an enthusiastic expert AI travel guide powered by Google ADK and MCP Protocol.\n\n"
    prompt += f"City: {city.title()}\n"
    prompt += f"LIVE WEATHER (from MCP Weather Tool): Temperature {weather['temperature']}C, Wind {weather['wind']} km/h, Humidity {weather['humidity']}%, Condition: {weather['condition']}\n"
    prompt += f"CITY INFO (from MCP Wikipedia Tool): {highlights}\n"
    prompt += f"COUNTRY DATA (from MCP Countries Tool): Country {country['country']}, Capital {country['capital']}, Languages {country['languages']}, Currency {country['currencies']}, Population {country['population']}\n"
    prompt += f"BEST TIME TO VISIT: {best_time}\n"
    prompt += f"SAFETY RATING: {safety}\n"
    prompt += f"LOCAL PHRASES: {phrases}\n\n"
    prompt += f"User asked: {question}\n\n"
    prompt += "Give a detailed, enthusiastic response in EXACTLY this format:\n\n"
    prompt += "WEATHER RIGHT NOW\n"
    prompt += "Describe the current weather and what it means for travelers\n\n"
    prompt += "CITY HIGHLIGHTS\n"
    prompt += "Top 3 must-see attractions and what makes this city unique\n\n"
    prompt += "LOCAL FOOD AND CULTURE\n"
    prompt += "Must-try foods and cultural experiences\n\n"
    prompt += "PRACTICAL INFO\n"
    prompt += "Best time to visit, safety rating, local currency and language\n\n"
    prompt += "LOCAL PHRASES\n"
    prompt += "Useful phrases with meaning\n\n"
    prompt += "TRAVEL TIP\n"
    prompt += "One personalized tip based on current weather\n\n"
    prompt += "Be enthusiastic, detailed and helpful! Use emojis!"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": "Bearer " + str(GROQ_API_KEY),
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1500
                }
            )
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            elif "error" in data:
                return "Error: " + str(data["error"]["message"])
            return "Unexpected response"
    except Exception as e:
        return "AI response error: " + str(e)
