from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from typing import List, Optional
from datetime import datetime

from schemas import WeatherQuery, WeatherResponse, LogQuery, RequestLogOut
from services.weather_service import WeatherService
from storage import query_logs
from deps import get_db

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post("", response_model=WeatherResponse)
async def get_weather(
    req: Request, 
    body: WeatherQuery, 
    db=Depends(get_db)
):
    """Get weather data for multiple cities"""
    weather_service = WeatherService()
    
    do_upload = req.query_params.get("upload") == "1"
    
    if do_upload:
        return await weather_service.get_weather_with_upload(
            cities=body.cities,
            units=body.units,
            headers=dict(req.headers),
            db=db,
            do_upload=True
        )
    else:
        return await weather_service.get_weather(
            cities=body.cities,
            units=body.units,
            headers=dict(req.headers),
            db=db
        )


@router.post("/csv")
async def get_weather_csv(
    req: Request, 
    body: WeatherQuery, 
    db=Depends(get_db)
):
    """Get weather data in CSV format"""
    weather_service = WeatherService()
    
    weather_response = await weather_service.get_weather(
        cities=body.cities,
        units=body.units,
        headers=dict(req.headers),
        db=db
    )
    
    # Convert to CSV
    csv_content = weather_service.export_to_csv(weather_response.items)
    
    return PlainTextResponse(csv_content, media_type="text/csv")


@router.get("/logs", response_model=List[RequestLogOut])
async def get_request_logs(
    start: Optional[datetime] = Query(None, description="Start date for filtering (ISO format)"),
    end: Optional[datetime] = Query(None, description="End date for filtering (ISO format)"),
    db=Depends(get_db)
):
    """Retrieve stored request logs filtered by date range"""
    try:
        logs = query_logs(db, start, end)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")
