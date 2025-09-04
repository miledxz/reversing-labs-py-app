from fastapi import FastAPI
from routes.weather import router as weather_router

app = FastAPI(title="Weather Service", version="1.0.0")

# Include routers
app.include_router(weather_router)

# Health check endpoint
@app.get("/healthz")
def healthz():
    return {"status": "ok"}