from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
from agent import run_agent

app = FastAPI(title="CityPulse Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

@app.get("/health")
async def health():
    return {"status": "CityPulse is live!", "version": "1.0"}

@app.post("/query")
async def query(body: Query):
    try:
        response = await run_agent(body.question)
        return {"response": response, "status": "success"}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "status": "error"}

@app.get("/")
async def root():
    return FileResponse("index.html")