from typing import Optional
from src.services.city_filter_extender import CityFilterExtenderService


async def get_city_filter_extender_service(
    file_content: bytes,
    new_filename: Optional[str] = "new_city_filter.txt"
) -> CityFilterExtenderService:
    """
    Args:
        file_content (bytes): file with routes should be in result city-filter
        new_filename (Optional[str], optional):
        Defaults to "new_city_filter.txt".

    Returns:
        CityFilterExtenderService:
    """
    return CityFilterExtenderService(file_content=file_content, new_filename=new_filename)
