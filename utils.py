import pandas as pd
from typing import List, Dict

def to_dataframe(items: List[Dict]) -> pd.DataFrame:
    return pd.DataFrame(items)