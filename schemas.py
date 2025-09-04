from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class WeatherQuery(BaseModel):
    cities: List[str] = Field(..., description="One or more city names")
    units: str = Field("metric", pattern="^(metric|imperial)$")


class WeatherItem(BaseModel):
    city: str
    temperature: float
    humidity: int
    wind_speed: float
    description: str
    clouds: int
    pressure: int
    visibility: int
    sunrise: int
    sunset: int


class WeatherResponse(BaseModel):
    items: List[WeatherItem]
    csv_url: Optional[str] = None


class RequestLogOut(BaseModel):
    id: int
    user_agent: str
    host: str
    params: Dict[str, Any]
    data: Dict[str, Any]
    created_at: datetime


class LogQuery(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None