from fastapi import APIRouter, Depends

from src.depends.services.config_comparison import get_config_comparison_service
from src.dto.config_comparison import ConfigComparisonBody
from src.services.config_comparison import ConfigComparisonService

router = APIRouter(tags=["config-comparison"])


@router.post("/config_comparison/")
async def config_comparison(
    params: ConfigComparisonBody,
    config_comparison_service:ConfigComparisonService=Depends(get_config_comparison_service)
):
    """
    Эндпоинт позволяет сравнивать различные поисковые конфиги. \n
    Необходимыми являются параметры: \n
        filter_airlines - Авиакомпания, отчет по которой Вы хотите получить, \n
        date - Дата на которую будет осуществляться поиск, \n
        api_key_1 - Ваши API-ключи, выдачу с которых вы хотите сравнить, \n
        api_key_2 - Ваши API-ключи, выдачу с которых вы хотите сравнить, \n
        service_class - класс обслуживания A <-- все E <-- эконом B <-- Бизнес F <-- Первый W <-- Комфорт\n
        \n
    Возможны варианты работы:\n
        - с параметром: directions - Передавать списком. Чтобы использовать другой вариант передать directions:[]\n
        - с параметрами: top_directions_from_date, limit_directions - передавать строкой.
        Чтобы использовать этот вариант передать directions:[]\n
        \n
    Опциональными являются:\n
        avia_config_item_ids_1 - конфиги, которые вы хотите сравнить, \n
        avia_config_item_ids_2 - конфиги, которые вы хотите сравнить, \n
        filter_gds  - работает по аналогии с filter_airlines (указать ГДС в которой хотите произвести поиск),\n
        exclude_gds - Какую ГДС исключить на поиске, \n
        force_search:'1' -  обходит кеш, \n
        max_segments - Фильтрует рекомендации по количеству сегментов, \n
        \n
    Для опциональных параметров - обязатльно передавать пустую строку, если не используете\n
            """
    return await config_comparison_service.make_config_comparison(params)
