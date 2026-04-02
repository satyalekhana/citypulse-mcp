import os
import httpx
import google.generativeai as genai

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

async def get_weather(city: str) -> str:
    coords = {
        "tokyo": (35.68, 139.69), "paris": (48.85, 2.35),
        "london": (51.51, -0.13), "new york": (40.71, -74.01),
        "mumbai": (19.07, 72.87), "dubai": (25.20, 55.27),
        "sydney": (-33.87, 151.21), "hyderabad": (17.38, 78.47),
        "delhi": (28.61, 77.21), "singapore": (1.35, 103.82)
    }
    lat, lon = coords.get(city.lower(), (17.38, 78.47))
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url)
            data = r.json()
        current = data["current"]
        codes = {0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Foggy",61:"Light rain",63:"Moderate rain",80:"Rain showers",95:"Thunderstorm"}
        return f"Temperature: {current['temperature_2m']}°C, Wind: {current['windspeed_10m']} km/h, Humidity: {current['relative_humidity_2m']}%, Condition: {codes.get(current['weathercode'], 'Clear')}"
    except Exception as e:
        return f"Weather data unavailable: {str(e)}"

async def get_city_highlights(city: str) -> str:
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city.replace(' ','_').title()}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url)
            data = r.json()
        return data.get("extract", "No highlights found")[:500]
    except Exception as e:
        return f"City highlights unavailable: {str(e)}"

async def get_country_info(country_code: str) -> str:
    url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url)
            data = r.json()[0]
        languages = list(data.get("languages", {}).values())[:2]
        currencies = [v["name"] for v in data.get("currencies", {}).values()]
        return f"Country: {data['name']['common']}, Capital: {data.get('capital',[''])[0]}, Languages: {', '.join(languages)}, Currency: {', '.join(currencies)}"
    except Exception as e:
        return f"Country info unavailable: {str(e)}"

async def run_agent(question: str) -> str:
    city_map = {
        "tokyo": "JP", "paris": "FR", "london": "GB",
        "new york": "US", "mumbai": "IN", "dubai": "AE",
        "sydney": "AU", "hyderabad": "IN", "delhi": "IN",
        "singapore": "SG"
    }
    city = "hyderabad"
    for c in city_map:
        if c in question.lower():
            city = c
            break
    country_code = city_map.get(city, "IN")

    weather = await get_weather(city)
    highlights = await get_city_highlights(city)
    country = await get_country_info(country_code)

    prompt = f"""You are CityPulse, an enthusiastic AI travel guide.

Here is live data fetched using MCP tools:

WEATHER DATA: {weather}
CITY HIGHLIGHTS: {highlights}
COUNTRY INFO: {country}

User asked: {question}

Respond in this format:
🌤️ Weather Right Now
[weather details here]

🏛️ City Highlights
[city highlights here]

🍜 Local Food and Culture
[food and culture info here]

✈️ Travel Tip
[one personalized tip based on weather]

Be enthusiastic and helpful!"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI response error: {str(e)}"