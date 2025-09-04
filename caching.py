from cachetools import TTLCache
from typing import Tuple, Dict

cache = TTLCache(maxsize=256, ttl=300)

def get_from_cache(key: Tuple[str, str]):
    return cache.get(key)

def set_to_cache(key: Tuple[str, str], value: Dict):
    cache[key] = value