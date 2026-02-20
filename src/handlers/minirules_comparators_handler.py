from fastapi import APIRouter, Depends

from src.depends.services.minirules_comparison import get_minirules_comparison_service
from src.dto.minirules_comparison import MinirulesComparisonBody

router = APIRouter(tags=["minirules-comparison"])


@router.post("/minirules_comparison/")
async def minirules_comparison(
    params: MinirulesComparisonBody,
    minirules_comparison_service = Depends(get_minirules_comparison_service)
):
    """
    Эндпоинт позволяет сравнивать различные правила тарифов одной авиакомпании и выяснить нужно ли их настраивать.\n
    Необходимыми являются параметры: \n
        filter_airlines - Авиакомпания, отчет по которой Вы хотите получить, \n
        date - Дата на которую будет осуществляться поиск, \n
        api_key - Ваш API-ключ, выдачу с которого ВЫ вы хотите проверить, \n
        service_class - класс обслуживания A <-- все E <-- эконом B <-- Бизнес F <-- Первый W <-- Комфорт\n
        \n
    Возможны варианты работы:\n
        - с параметром: directions - Передавать списком. Чтобы использовать другой вариант передать directions:[]\n
        - с параметрами: top_directions_from_date, limit_directions - передавать строкой.
        Чтобы использовать этот вариант передать directions:[]\n
        \n
    Опциональными являются:\n
        avia_config_item_ids - конфиг, выдачу с которого хотите получить,\n
        filter_gds  - работает по аналогии с filter_airlines (указать ГДС в которой хотите произвести поиск),\n
        exclude_gds - Какую ГДС исключить на поиске,\n
        force_search:'1' -  обходит кеш,\n
        max_segments - Фильтрует рекомендации по количеству сегментов,\n
        \n
    Для опциональных параметров - обязатльно передавать пустую строку, если не используете\n
    """
    return await minirules_comparison_service.make_minirules_comparison(params)
