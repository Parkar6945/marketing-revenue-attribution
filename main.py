import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from attribution_engine import AttributionEngine
from data_generator import generate_customer_journeys

app = FastAPI(title="Marketing-to-Revenue Attribution Intelligence")

# Ensure dataset exists
if not os.path.exists("customer_journeys.json") or not os.path.exists("channel_costs.json"):
    generate_customer_journeys(500)

engine = AttributionEngine()

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/attribution")
async def get_attribution():
    return engine.calculate_attribution_models()

@app.post("/api/recalculate")
async def recalculate():
    generate_customer_journeys(500)
    global engine
    engine = AttributionEngine()
    return {"status": "success", "message": "Dataset re-simulated."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
