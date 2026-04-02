import os
import google.generativeai as genai
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8080/mcp")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

async def run_agent(question: str) -> str:
    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            
            tool_descriptions = "\n".join([
                f"- {t.name}: {t.description}" 
                for t in tools.tools
            ])
            
            prompt = f"""You are CityPulse, an enthusiastic AI travel guide.

You have access to these tools:
{tool_descriptions}

To get weather, use coordinates:
- Tokyo: lat=35.68, lon=139.69
- Paris: lat=48.85, lon=2.35
- London: lat=51.51, lon=-0.13
- New York: lat=40.71, lon=-74.01
- Mumbai: lat=19.07, lon=72.87
- Dubai: lat=25.20, lon=55.27
- Sydney: lat=-33.87, lon=151.21
- Hyderabad: lat=17.38, lon=78.47
- Delhi: lat=28.61, lon=77.21
- Singapore: lat=1.35, lon=103.82

For country codes use: JP, FR, GB, US, IN, AE, AU, SG

User question: {question}

Call the tools and respond with:
🌤️ Weather Right Now
🏛️ City Highlights  
🍜 Local Food and Culture
✈️ Travel Tip

Be enthusiastic and helpful!"""

            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            return response.text
