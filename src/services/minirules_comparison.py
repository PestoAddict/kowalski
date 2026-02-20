import json
from typing import Optional
import logging

import pandas as pd
import requests

from src.services.db.raw.base import RawDatabaseService
from src.services.http.base import HTTPXClient
from src.utils.utils import convert_data
from src.services.utils.comparators_utils import format_routes,make_fast_search_url,prepare_minirules_comparison_report
from src.dto.minirules_comparison import MinirulesComparisonBody
from src.dto.config_comparison import Route

#pylint: disable=singleton-comparison

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MinirulesComparisonService(RawDatabaseService, HTTPXClient):

    def url_constructor(self, params: MinirulesComparisonBody, route:Route) -> str:
        """
        Generates a URL for the fast search API request.

        This function constructs a URL for querying the fast search

        Args:
            params (dict):
                - search_date (str): Date of the search in format '%Y-%m-%d'.
                - avia_config_item_ids (str): Configuration ID for the API request.
                - exclude_gds (str): Excluded Global Distribution Systems (GDS).
                - filter_airlines (str): Allowed airlines for filtering.
                - filter_gds (str): Allowed GDS providers for filtering.
                - force_search (int): Whether to force the search (1 or 0).
                - api_key (str): API key for authentication.
                - max_segments (int): Maximum number of segments allowed.
                - service_class (str): Class of service (e.g., A, B).

            departure (str): IATA code of the departure airport.
            arrival (str): IATA code of the arrival airport.

        Returns:
            str: The fully constructed API request URL.
        """
        url = make_fast_search_url(
            route=route,
            api_key = params.api_key,
            avia_config_item_ids=params.avia_config_item_ids,
            fast_search_params=params.fast_search_params
            )
        return url

    async def fetch_url_response(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: int = 18
    ) -> dict:
        """
        Asynchronously fetches a response from a given URL.

        This function makes an asynchronous GET request to the provided URL,
        optionally including query parameters and headers. If the request is
        successful, it returns the response data. If an exception occurs, it
        returns an error message.

        Args:
            url (str): The URL to send the GET request to.
            params (dict, optional): Query parameters to be sent with the request. Defaults to None.
            headers (dict, optional): HTTP headers to include in the request. Defaults to None.
            timeout (int, optional): The request timeout in seconds. Defaults to 18.

        Returns:
            dict: A dictionary containing:
                - 'URL' (str): The requested URL.
                - 'response' (str or dict): The response data or an error message if the request fails.
        """
        try:
            response, _ = await self.get(url, params=params, headers=headers, timeout=timeout)
            return {'URL': url, 'response': response}
        except requests.exceptions.RequestException as e:
            logger.error("URL: %s , response : Error: %s", url, e)
            return {'URL': url, 'response': f'Error: {e}'}

    async def make_recomendations_table(self, result: list) -> pd.DataFrame:
        """
        Parses and transforms API response data into a structured Pandas DataFrame.

        This function processes raw API responses containing flight recommendations,
        extracting relevant fields. It also formats the flight routes
        for easier analysis.

        Args:
            result (list): A list of API response dictionaries containing flight
                           recommendation details.

        Returns:
            pd.DataFrame: A structured DataFrame containing extracted information,
                          including:
                - 'status_code': API response status code.
                - 'session': Unique session ID for the request.
                - 'trip_id': Unique ID for each recommendation.
                - 'amount': Flight price in RUB.
                - 'gds_id': Global Distribution System identifier.
                - 'config_id': Configuration ID used in the search.
                - 'fare': Fare details.
                - 'validating_supplier': Airline supplier validating the ticket.
                - 'route_index': Index of the flight route.
                - 'routes_formatted': Human-readable string representing flight routes.
                - 'fares': List of fare codes for each segment.
                - 'refunds': Refundability information per segment.
                - 'departure_city', 'arrival_city': City codes for each segment.
                - 'flight_number': Flight number for each segment.
                - 'service_class': Class of service for the segment.
                - 'baggage': Baggage allowance for each segment.
                - 'mini_rules': Additional mini-rules applied to the fare.

        Raises:
            ValueError: If the response structure is incorrect or contains unexpected data.
        """
        responces = pd.DataFrame(result)
        responces['parsed_responce'] = responces['response'].apply(
            lambda x: x if isinstance(x, dict) else json.loads(
                x) if isinstance(x, str) else None
        )
        responces['status_code'] = responces.apply(
            lambda x: x['parsed_responce']['response']['result']['code'], axis=1)
        responces['session'] = responces.apply(
            lambda x: x['parsed_responce']['response']['session']['id'], axis=1)
        responces['recommendations'] = responces.apply(
            lambda x: x['parsed_responce']['response']['recommendations'], axis=1)
        responces = responces[responces['recommendations'].map(len) > 0]
        responces = responces.explode('recommendations').reset_index(drop=True)
        responces['trip_id'] = responces.apply(
            lambda x: x['recommendations']['id'], axis=1)
        responces['amount'] = responces.apply(
            lambda x: x['recommendations']['amount']['RUB'], axis=1)
        responces['gds_id'] = responces.apply(
            lambda x: x['recommendations']['gds_id'], axis=1)
        responces['config_id'] = responces.apply(
            lambda x: x['recommendations']['config_id'], axis=1)
        responces['fare'] = responces.apply(
            lambda x: x['recommendations']['fare'], axis=1)
        responces['validating_supplier'] = responces.apply(
            lambda x: x['recommendations']['validating_supplier'], axis=1)
        responces['all_routes'] = responces.apply(
            lambda x: [
                {
                    'route_index': route['route_index'],
                    'segments': [

                        {'segment_index': segment['segment_index'],
                            'fare_code': segment['fare_code'],
                            'supplier_code': segment['supplier_code'],
                            'departure_city': segment['departure_city'],
                            'arrival_city': segment['arrival_city'],
                            'departure_time': segment['departure_time'],
                            'arrival_time': segment['arrival_time'],
                            'flight_number': segment['flight_number'],
                            'service_class': segment['service_class'],
                            'baggage': segment['baggage'],
                            'mini_rules': segment['mini_rules'],
                         } for segment in route['segments']
                    ]
                } for route in x['recommendations']['routes']
            ],
            axis=1
        )
        responces['routes'] = responces['all_routes']
        responces = responces.explode('routes').reset_index(drop=True)
        responces['route_index'] = responces.apply(
            lambda x: x['routes']['route_index'], axis=1)
        responces['all_segments'] = responces.apply(
            lambda x: x['routes']['segments'], axis=1)
        responces['all_segments'] = responces['all_segments'].apply(
            lambda x: x if isinstance(x, list) else [])
        responces['segments'] = responces['all_segments']
        responces = responces.explode('segments').reset_index(drop=True)
        responces['fares'] = responces.apply(
            lambda x: list(
                segment['fare_code']
                for route in x['recommendations']['routes']
                for segment in route['segments']
            ),
            axis=1
        )
        responces['refunds'] = responces.apply(
            lambda x: list(
                segment['mini_rules']['system_rules']['exchange_block']
                for route in x['recommendations']['routes']
                for segment in route['segments']
            ),
            axis=1
        )

        responces['routes_formatted'] = responces.apply(
            lambda x: format_routes(x['recommendations']['routes']), axis=1
        )


        return responces

    async def get_top_directions(self, params:MinirulesComparisonBody) -> pd.DataFrame:
        """
        Retrieves the most and least popular flight directions based on statistics.
        """
        if len(params.directions) == 0:
            kwargs = {
                "top_directions_from_date": params.top_directions_from_date,
                "filter_airlines": params.fast_search_params.filter_airlines,
                "limit_directions": params.limit_directions,
            }
            statement = """
                    with agg_f as (
                        select
                            carrier_code as supplier_code,
                            city_dep.iata || city_arr.iata as direction,
                            count(*) as popularity
                        from tol.flight f
                            join tol.city city_dep on city_dep.id = f.city_dep_id
                            join tol.city city_arr on city_arr.id = f.city_arr_id
                        where 1=1
                            AND carrier_code = :filter_airlines
                            and date_dep >= :top_directions_from_date
                        group by
                            carrier_code,city_dep.iata, city_arr.iata
                        order by
                            popularity desc),
                    top_ as(
                        select
                            *
                        from
                            agg_f
                        order by
                            popularity desc
                        limit :limit_directions),
                    bttm_ as (
                        select
                            *
                        from agg_f
                        order by
                            popularity asc
                        limit :limit_directions)
                    SELECT
                        *
                    from top_ union (SELECT * from bttm_)
                """
            result = await self._execute(statement, **kwargs)
            result = result.all()
            if not result:
                return pd.DataFrame(columns=['supplier_code', 'direction', 'popularity'])
            result = pd.DataFrame(
                result, columns=['supplier_code', 'direction', 'popularity'])
            return result

        result = pd.DataFrame(params.directions)
        result.columns = ['direction']
        result['supplier_code'] = params.fast_search_params.filter_airlines
        result['popularity'] = result.index + 1
        return result

    async def make_minirules_comparison(self, params: MinirulesComparisonBody) -> dict:
        """
        Compares mini-rules for airline fares based on the given parameters.

        This function retrieves top flight directions, fetches API responses,
        processes fare information, and generates a detailed comparison report
        on fare attributes such as baggage, refundability, and exchangeability.

        Args:
            params (dict):
                - api_key (str): API key for authentication.
                - avia_config_item_ids (str): Config ID for fare rules.
                - filter_airlines (str): Airline carrier code filter.
                - top_directions_from_date (str): Start date for top directions ('%Y-%m-%d').
                - limit_directions (int): Number of top directions to retrieve.
                - directions (list): Predefined list of directions (optional).

        Returns:
            dict: A report summarizing fare mini-rules, including:
                - 'supplier_code': The airline code.
                - 'count_unique_fares': Number of unique fares.
                - 'check_accessories_or_carryon_flag': Flag if missing data is found.
                - 'check_luggage_flag': Flag if luggage details are missing.
                - 'check_exchange_flag': Flag if exchange rules are missing.
                - 'check_refund_flag': Flag if refund rules are missing.
                - Detailed baggage, refund, and exchange breakdowns.
        """

        top_directions = await self.get_top_directions(params)
        if top_directions.empty and len(params.directions) == 0:
            return convert_data({
                'Description':'''No data returned by sql query,
                make shure you set params.top_directions_from_date correctly or
                please try again with params.directions given.'''})
        top_directions['departure'] = top_directions.direction.str[:3]
        top_directions['arrival'] = top_directions.direction.str[3:]
        top_directions['url'] = top_directions.apply(
            lambda row: self.url_constructor(
                params=params,
                route=Route(
                    departure=row.departure,
                    arrival=row.arrival
                    )
                ),
            axis=1
            )

        responces = await self.make_recomendations_table([
            await self.fetch_url_response(url)
            for url in top_directions.url.to_list()
        ])

        responces['api_key'] = params.api_key
        responces['avia_config_item_ids'] = params.avia_config_item_ids
        responces = pd.concat(
            [
                responces.reset_index(drop=True),
                pd.json_normalize(responces['segments'])
            ],
            axis=1)

        fares = responces[['gds_id', 'config_id', 'routes_formatted',
                           'api_key', 'avia_config_item_ids',
                           'validating_supplier', 'route_index',
                           'segment_index', 'fare_code',
                           'supplier_code',  'service_class', 'baggage',
                           'mini_rules.system_rules.refund', 'mini_rules.system_rules.exchange',
                           # 'mini_rules.system_rules.comment',
                           'mini_rules.system_rules.refund_comment',
                           'mini_rules.system_rules.exchange_comment',
                           'mini_rules.system_rules.baggage_block.accessories.piece',
                           'mini_rules.system_rules.baggage_block.accessories.weight',
                           'mini_rules.system_rules.baggage_block.luggage.piece',
                           'mini_rules.system_rules.baggage_block.luggage.weight.type',
                           'mini_rules.system_rules.baggage_block.luggage.weight.value',
                           'mini_rules.system_rules.baggage_block.carryon.piece',
                           'mini_rules.system_rules.baggage_block.carryon.weight.type',
                           'mini_rules.system_rules.baggage_block.carryon.weight.value',
                           'mini_rules.system_rules.baggage_block.carryon.dimensions',
                           'mini_rules.system_rules.refund_block.before_departure.available',
                           'mini_rules.system_rules.refund_block.before_departure.is_free',
                           # 'mini_rules.system_rules.refund_block.before_departure.comment',
                           'mini_rules.system_rules.exchange_block.before_departure.available',
                           'mini_rules.system_rules.exchange_block.before_departure.is_free',
                           # 'mini_rules.system_rules.exchange_block.before_departure.comment'
                           ]]

        unique_fares = fares.drop_duplicates()
        top_directions['direction'] = top_directions['departure'] + \
            top_directions['arrival']

        report = prepare_minirules_comparison_report(
            params=params,
            unique_fares=unique_fares,
            top_directions=top_directions
            )

        return convert_data(report)
