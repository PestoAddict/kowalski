from datetime import date

from pydantic import BaseModel

from src.dto.config_comparison import FastSearchParamsBody

class MinirulesComparisonBody(BaseModel):
    api_key: str='3519bbc3-6dbf-435d-8944-e987868145eb' # raw avsl prod
    avia_config_item_ids: str=''
    fast_search_params: FastSearchParamsBody
    directions: list[str]
    top_directions_from_date: date
    limit_directions: int=1
