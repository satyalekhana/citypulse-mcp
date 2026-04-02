# CityPulse — AI Travel Intelligence Agent

## What it does
CityPulse is an AI travel guide built using Google ADK and Model Context Protocol (MCP).
Ask about any city and get live weather, highlights, and food culture instantly.

## Architecture
- **MCP Server** — Exposes 3 tools: Weather, City Highlights, Country Info
- **ADK Agent** — Powered by Gemini 2.0 Flash, connects to MCP server
- **Beautiful UI** — Chat interface for live city queries

## Tools Used
- Open-Meteo API — Live weather data
- Wikipedia API — City highlights
- REST Countries API — Food and culture

## Tech Stack
- Google ADK + Gemini 2.0 Flash
- Model Context Protocol (MCP)
- FastAPI + Railway deployment
