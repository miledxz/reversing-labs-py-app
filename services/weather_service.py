import asyncio
from typing import List, Optional
import httpx
import pandas as pd

from schemas import WeatherQuery, WeatherResponse
from weather_client import fetch_city, normalize
from utils import to_dataframe
from s3_uploader import upload_csv
from storage import save_log
from caching import get_from_cache, set_to_cache


class WeatherService:
    def __init__(self):
        pass
    
    async def get_weather_data(self, cities: List[str], units: str) -> List[dict]:
        """Fetch weather data for multiple cities with caching"""
        items = []
        async with httpx.AsyncClient() as session:
            tasks = []
            for city in cities:
                key = (city.lower(), units)
                cached = get_from_cache(key)
                if cached:
                    items.append(cached)
                else:
                    tasks.append((key, city, fetch_city(session, city, units)))
            
            if tasks:
                results = await asyncio.gather(*[t[2] for t in tasks])
                for (key, city, _), payload in zip(tasks, results):
                    norm = normalize(city, payload)
                    set_to_cache(key, norm)
                    items.append(norm)
        
        return items
    
    def create_dataframe(self, items: List[dict]) -> pd.DataFrame:
        """Convert weather items to pandas DataFrame"""
        return to_dataframe(items)
    
    def upload_csv_to_s3(self, df: pd.DataFrame, units: str) -> Optional[str]:
        """Upload CSV to S3 and return the URL"""
        try:
            key = f"reports/weather_{units}.csv"
            return upload_csv(df, key)
        except Exception as e:
            print(f"Failed to upload CSV to S3: {e}")
            return None
    
    def save_request_log(self, db, headers: dict, params: dict, data: dict):
        """Save request log to database"""
        return save_log(db, headers, params, data)
    
    async def get_weather(self, cities: List[str], units: str, headers: dict, db) -> WeatherResponse:
        """Main method to get weather data with all business logic"""
        items = await self.get_weather_data(cities, units)
        
        df = self.create_dataframe(items)
        
        self.save_request_log(db, headers, {"cities": cities, "units": units}, {"items": items})
        
        return WeatherResponse(items=items, csv_url=None)
    
    async def get_weather_with_upload(self, cities: List[str], units: str, headers: dict, db, do_upload: bool = False) -> WeatherResponse:
        """Get weather data with optional S3 upload"""
        items = await self.get_weather_data(cities, units)
        
        df = self.create_dataframe(items)
        
        csv_url = None
        if do_upload:
            csv_url = self.upload_csv_to_s3(df, units)
        
        self.save_request_log(db, headers, {"cities": cities, "units": units}, {"items": items, "csv_url": csv_url})
        
        return WeatherResponse(items=items, csv_url=csv_url)
    
    def export_to_csv(self, items: List[dict]) -> str:
        """Export weather items to CSV format"""
        df = pd.DataFrame([i.model_dump() if hasattr(i, 'model_dump') else dict(i) for i in items])
        return df.to_csv(index=False)
