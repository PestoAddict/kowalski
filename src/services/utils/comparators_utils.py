import pandas as pd

from src.dto.minirules_comparison import MinirulesComparisonBody
from src.dto.config_comparison import Route, FastSearchParamsBody



#pylint: disable=singleton-comparison

def format_routes(
    routes:list[dict]
    )-> str:
    """makes recomendation key
    Args:
        routes (list[dict]):
    Returns:
        str: recomendation key
    """
    formatted_routes = []
    for route in routes:
        route_index = route['route_index']
        for segment in route['segments']:
            segment_index = segment['segment_index']
            supplier_code = segment['supplier_code']
            departure_city = segment['departure_city']
            arrival_city = segment['arrival_city']
            flight_number = segment['flight_number']
            formatted_routes.append(
                f"""{route_index}[{segment_index}|
                {departure_city}-{arrival_city}|
                {supplier_code}{flight_number}]"""
                )
    return "|".join(formatted_routes)

def make_fast_search_url(
    route: Route,
    api_key: str,
    avia_config_item_ids: str,
    fast_search_params: FastSearchParamsBody
    ) -> str:
    """Making url for fast search.

        Args:
            params (ConfigComparisonBody):
            connection (int):
            route (Route):

        Returns:
            str: url
    """
    date_departure = fast_search_params.search_date.strftime('%d-%m-%Y')  # формат у ядра "dd-mm-yyyy"

    url = (
        f'https://api-deac.crpo.su/avia/fast_search.json'
        f'?account_code[0][code]='
        f'&account_code[0][gds_id]='
        f'&adt=1&avia_config_item_ids[0]={avia_config_item_ids}'
        f'&chd=0&count=&destinations[0][arrival]={route.arrival}'
        f'&destinations[0][date]={date_departure}'
        f'&destinations[0][departure]={route.departure}'
        f'&disable_estream=1'
        f'&disable_pre_filters=0'
        f'&exclude_airlines='
        f'&exclude_gds={fast_search_params.exclude_gds}'
        f'&filter_airlines={fast_search_params.filter_airlines}'
        f'&filter_gds={fast_search_params.filter_gds}'
        f'&force_search={fast_search_params.force_search}'
        f'&include_pricer=0'
        f'&inf=0'
        f'&ins=0'
        f'&is_test=1'
        f'&key={api_key}'
        f'&lang=en'
        f'&loyalty_code='
        f'&max_segments={fast_search_params.max_segments}'
        f'&min_pass_count='
        f'&mpis=0'
        f'&service_class={fast_search_params.service_class}'
        f'&src=0'
        f'&strategy='
        f'&yth=0'
    )
    return url

def make_check_laggage_flag(unique_fares: pd.DataFrame) -> bool:
    """flag means that there is no baggage or nonbaggage fares
    Args:
        unique_fares (pd.DataFrame):
    Returns:
        bool:
    """
    len_unique_fares = len(set(unique_fares.fare_code.to_list()))
    len_unique_fares_wo_baggage = len(
        set(
            unique_fares[unique_fares['baggage'].isna()
                         ].fare_code.to_list()
        )
    )
    len_unique_fares_with_baggage = len(
        set(
            unique_fares[~unique_fares['baggage'].isna()
                         ].fare_code.to_list()
        )
    )
    all_wo_baggage_condition = len_unique_fares == len_unique_fares_wo_baggage
    all_baggage_condition = len_unique_fares == len_unique_fares_with_baggage
    return  all_wo_baggage_condition and all_baggage_condition

def make_check_exchange_flag(unique_fares: pd.DataFrame) -> bool:
    """flag means that there is no exchangeable fares
    Args:
        unique_fares (pd.DataFrame):
    Returns:
        bool:
    """
    len_unique_fares = len(set(unique_fares.fare_code.to_list()))
    len_unique_fares_wo_exchange = len(
        set(
            unique_fares[unique_fares['mini_rules.system_rules.exchange'].isna(
            )].fare_code.to_list()
        )
    )
    exchange_condition = len_unique_fares == len_unique_fares_wo_exchange
    return exchange_condition

def make_check_refund_flag(unique_fares: pd.DataFrame) -> bool:
    """flag means that there is no refundable fares
    Args:
        unique_fares (pd.DataFrame):
    Returns:
        bool:
    """
    len_unique_fares = len(set(unique_fares.fare_code.to_list()))
    len_unique_fares_wo_refund = len(
        set(
            unique_fares[unique_fares['mini_rules.system_rules.refund'].isna(
            )].fare_code.to_list()
        )
    )
    refund_condition = len_unique_fares == len_unique_fares_wo_refund
    return refund_condition

def unique_fares_wo_accessories_and_carryon(unique_fares: pd.DataFrame) -> set:
    """unique_fares_wo_accessories_and_carryon
    Args:
        unique_fares (pd.DataFrame):
    Returns:
        int:
    """
    return set(unique_fares[
        ((unique_fares['mini_rules.system_rules.baggage_block.accessories.piece'].isna()) &
         (unique_fares['mini_rules.system_rules.baggage_block.accessories.weight'].isna())) &
        ((unique_fares['mini_rules.system_rules.baggage_block.carryon.piece'].isna()) &
         (unique_fares['mini_rules.system_rules.baggage_block.carryon.weight.value'].isna()))
    ].fare_code.to_list())

def count_unique_fares_wo_accessories_and_carryon(unique_fares: pd.DataFrame) -> int:
    """count_unique_fares_wo_accessories_and_carryon
    Args:
        unique_fares (pd.DataFrame): _description_
    Returns:
        int: _description_
    """
    return len(unique_fares_wo_accessories_and_carryon(unique_fares))

def count_unique_carryon_fares(unique_fares: pd.DataFrame) -> int:
    """_summary_
    Args:
        unique_fares (pd.DataFrame):
    Returns:
        int:
    """
    return len(list(set(unique_fares[
        ~((unique_fares['mini_rules.system_rules.baggage_block.carryon.piece'].isna()) &
          (unique_fares['mini_rules.system_rules.baggage_block.carryon.weight.value'].isna()))
    ].fare_code.to_list())))

def count_unique_accessories_fares(unique_fares: pd.DataFrame) -> int:
    """_summary_
    Args:
        unique_fares (pd.DataFrame):
    Returns:
        int:
    """
    return len(list(set(unique_fares[
        ~((unique_fares['mini_rules.system_rules.baggage_block.accessories.piece'].isna()) &
          (unique_fares['mini_rules.system_rules.baggage_block.accessories.weight'].isna()))
    ].fare_code.to_list())))

def prepare_minirules_comparison_report(
    params: MinirulesComparisonBody,
    unique_fares: pd.DataFrame,
    top_directions: pd.DataFrame
    ) -> dict:
    """_summary_
    Returns:
        dict: _description_
    """
    report = {
        'supplier_code': params.fast_search_params.filter_airlines,
        'avia_config_item_ids': params.avia_config_item_ids,
        'api_key': params.api_key,
        'gds_id': list(set(unique_fares.gds_id.to_list())),
        'config_id': list(set(unique_fares.config_id.to_list())),
        'directions': list(set(top_directions['direction'].to_list())),
        'count_unique_fares': len(set(unique_fares.fare_code.to_list())),
        'check_accessories_and_carryon_flag': count_unique_fares_wo_accessories_and_carryon(unique_fares) > 0,
        'check_laggage_flag': make_check_laggage_flag(unique_fares),
        'check_exchange_flag': make_check_exchange_flag(unique_fares),
        'check_refund_flag': make_check_refund_flag(unique_fares),
        'baggage_block': {
            'count_unique_fares_wo_accessories_and_carryon': count_unique_fares_wo_accessories_and_carryon(unique_fares),
            'count_unique_carryon_fares': count_unique_carryon_fares(unique_fares),
            'count_unique_accessories_fares': count_unique_accessories_fares(unique_fares),
            'count_unique_fares_with_no_data_baggage': len(set(
                unique_fares[unique_fares['baggage'].isna()].fare_code.to_list()
                )),
        },
        'refund_block': {
            'count_unique_fares_wo_refund': len(set(
                unique_fares[unique_fares['mini_rules.system_rules.refund']
                             == False].fare_code.to_list()
            )),
            'count_unique_fares_with_no_data_refund': len(set(
                unique_fares[unique_fares['mini_rules.system_rules.refund'].isna(
                )].fare_code.to_list()
            )),
            'count_unique_fares_refundable': len(set(
                unique_fares[unique_fares['mini_rules.system_rules.refund']
                             == True].fare_code.to_list()
            )),
        },
        'exchange_block': {
            'count_unique_fares_wo_exchange': len(set(
                unique_fares[unique_fares['mini_rules.system_rules.exchange']
                             == False].fare_code.to_list()
            )),
            'count_unique_fares_with_no_data_exchange': len(set(
                unique_fares[unique_fares['mini_rules.system_rules.exchange'].isna(
                )].fare_code.to_list()
            )),
            'count_unique_fares_exchangeable': len(set(
                unique_fares[unique_fares['mini_rules.system_rules.exchange']
                             == True].fare_code.to_list()
            )),
        },
        'detailed': {
            'unique_fares': list(set(unique_fares.fare_code.to_list())),
            'fares_with_no_data_baggage': list(set(
                unique_fares[unique_fares['baggage'].isna()
                             ].fare_code.to_list()
            )),
            'unique_fares_with_no_data_accessories_and_carryon': list(
                unique_fares_wo_accessories_and_carryon(unique_fares)
            ),
            'unique_fares_with_no_data_refund': list(set(
                unique_fares[unique_fares['mini_rules.system_rules.refund'].isna(
                )].fare_code.to_list()
            )),
            'unique_fares_with_no_data_exchange': list(set(
                unique_fares[unique_fares['mini_rules.system_rules.exchange'].isna(
                )].fare_code.to_list()
            )),
        },
    }
    return report
