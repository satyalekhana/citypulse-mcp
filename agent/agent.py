
import os
import httpx

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


async def get_weather(city):
    coords = {
        "tokyo": (35.68, 139.69),
        "paris": (48.85, 2.35),
        "london": (51.51, -0.13),
        "new york": (40.71, -74.01),
        "mumbai": (19.07, 72.87),
        "dubai": (25.20, 55.27),
        "sydney": (-33.87, 151.21),
        "hyderabad": (17.38, 78.47),
        "delhi": (28.61, 77.21),
        "singapore": (1.35, 103.82)
    }
    lat, lon = coords.get(city.lower(), (17.38, 78.47))
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
        codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            61: "Light rain",
            63: "Moderate rain",
            80: "Rain showers",
            95: "Thunderstorm"
        }
        condition = codes.get(current["weathercode"], "Clear")
        temp = current["temperature_2m"]
        wind = current["windspeed_10m"]
        humidity = current["relative_humidity_2m"]
        return f"Temperature: {temp}C, Wind: {wind} km/h, Humidity: {humidity}%, Condition: {condition}"
    except Exception as e:
        return f"Weather unavailable: {str(e)}"


async def get_city_highlights(city):
    city_formatted = city.replace(" ", "_").title()
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city_formatted}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url)
            data = r.json()
        return data.get("extract", "No highlights found")[:500]
    except Exception as e:
        return f"Highlights unavailable: {str(e)}"


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
        return f"Country: {country_name}, Capital: {capital}, Languages: {', '.join(languages)}, Currency: {', '.join(currencies)}"
    except Exception as e:
        return f"Country info unavailable: {str(e)}"


async def run_agent(question):
    city_map = {
        "tokyo": "JP",
        "paris": "FR",
        "london": "GB",
        "new york": "US",
        "mumbai": "IN",
        "dubai": "AE",
        "sydney": "AU",
        "hyderabad": "IN",
        "delhi": "IN",
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

    prompt = "You are CityPulse, an enthusiastic AI travel guide.\n\n"
    prompt += "Live data fetched using MCP tools:\n\n"
    prompt += "WEATHER DATA: " + weather + "\n"
    prompt += "CITY HIGHLIGHTS: " + highlights + "\n"
    prompt += "COUNTRY INFO: " + country + "\n\n"
    prompt += "User asked: " + question + "\n\n"
    prompt += "Respond in this format:\n"
    prompt += "Weather Right Now\n"
    prompt += "[weather details]\n\n"
    prompt += "City Highlights\n"
    prompt += "[city highlights]\n\n"
    prompt += "Local Food and Culture\n"
    prompt += "[food and culture]\n\n"
    prompt += "Travel Tip\n"
    prompt += "[one tip based on weather]\n\n"
    prompt += "Be enthusiastic and helpful!"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": "Bearer " + str(GROQ_API_KEY),
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1000
                }
            )
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            elif "error" in data:
                return "Groq error: " + str(data["error"]["message"])
            else:
                return "Unexpected response: " + str(data)
    except Exception as e:
        return "AI response error: " + str(e)
