from datetime import date

from pydantic import BaseModel


class FastSearchParamsBody(BaseModel):
    filter_airlines: str
    search_date: date
    filter_gds: str=''
    exclude_gds: str=''
    force_search: str='1' # 1 - обходит кеш
    max_segments: str='' #'' <-- по умолчанию 1- 9999
    service_class: str='A' # A <-- все E <-- эконом B <-- Бизнес F <-- Первый W <-- Комфорт

class ConfigComparisonBody(BaseModel):
    api_key_1: str='3519bbc3-6dbf-435d-8944-e987868145eb' # raw avsl prod
    api_key_2: str='5479b81f-6da1-4a22-b835-0cb26415b8e1' # dev all cf opened
    avia_config_item_ids_1: str='' # None
    avia_config_item_ids_2: str='2164' # kokpit
    fast_search_params: FastSearchParamsBody
    directions: list[str]
    top_directions_from_date: date
    limit_directions: int=5

class Route(BaseModel):
    departure: str
    arrival: str
