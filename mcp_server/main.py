from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("citypulse-mcp")

@mcp.tool()
async def get_weather(city: str, lat: float, lon: float) -> dict:
    """Get current weather for a city."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()
    current = data["current"]
    codes = {0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Foggy",61:"Light rain",63:"Moderate rain",80:"Rain showers",95:"Thunderstorm"}
    return {
        "temperature_c": current["temperature_2m"],
        "wind_kmh": current["windspeed_10m"],
        "humidity": current["relative_humidity_2m"],
        "condition": codes.get(current["weathercode"], "Unknown")
    }

@mcp.tool()
async def get_city_highlights(city: str) -> dict:
    """Fetch city summary from Wikipedia."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city.replace(' ','_')}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()
    return {
        "summary": data.get("extract", "")[:600],
        "title": data.get("title", city)
    }

@mcp.tool()
async def get_country_info(country_code: str) -> dict:
    """Get country cuisine and culture info."""
    url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()[0]
    return {
        "country": data["name"]["common"],
        "capital": data.get("capital", [""])[0],
        "languages": list(data.get("languages", {}).values())[:3],
        "currencies": [v["name"] for v in data.get("currencies", {}).values()]
    }

if __name__ == "__main__":
    import uvicorn
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="0.0.0.0", port=8080)
