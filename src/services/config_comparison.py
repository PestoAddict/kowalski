import json
from typing import Optional
import logging

import pandas as pd
import requests

from src.services.db.raw.base import RawDatabaseService
from src.services.http.base import HTTPXClient
from src.utils.utils import convert_data
from src.dto.config_comparison import ConfigComparisonBody, Route
from src.services.utils.comparators_utils import format_routes, make_fast_search_url
from src.utils.logger import logger



class ConfigComparisonService(RawDatabaseService, HTTPXClient):

    def url_constructor(
        self,
        params: ConfigComparisonBody,
        connection: int,
        route: Route,
        ) -> str:
        """Making url for fast search^ depends on connection.
        connection based on ConfigComparisonBody
        1 : api_key_1, avia_config_item_ids_1
        2 : api_key_2, avia_config_item_ids_2

        Args:
            params (ConfigComparisonBody):
            connection (int):
            route (Route):

        Returns:
            str: url
        """
        if connection == 1:
            api_key = params.api_key_1
            avia_config_item_ids = params.avia_config_item_ids_1
        else:
            api_key = params.api_key_2
            avia_config_item_ids = params.avia_config_item_ids_2


        url = make_fast_search_url(
            route=route,
            api_key = api_key,
            avia_config_item_ids=avia_config_item_ids,
            fast_search_params=params.fast_search_params
            )
        return url

    async def fetch_url_response(
        self,
        url: str,
        params: Optional[dict]=None,
        headers: Optional[dict]=None,
        timeout: Optional[int]=18
    ) -> dict:
        """fetch responce

        Args:
            url (str):
            params (dict, optional): Defaults to None.
            headers (_type_, optional): Defaults to None.
            timeout (int, optional): Defaults to 18.

        Returns:
            dict: {'URL': url, 'response': response}
        """
        try:
            response, _ = await self.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
                )
            return {'URL': url, 'response': response}
        except requests.exceptions.RequestException as e:
            logger.error("URL: %s , response : Error: %s", url, e)
            return {'URL': url, 'response': f'Error: {e}'}

    async def make_recomendations_table(
        self,
        result: list
        ) -> pd.DataFrame:
        """Returns DataFrame where each row contains single recomendation

        Args:
            result (list[dict]): list of urls & responces

        Returns:
            pd.DataFrame: each row contains single recomendation
        """
        responces = pd.DataFrame(result)
        responces['parsed_responce'] = responces['parsed_responce'] = responces['response'].apply(
            lambda x: json.loads(x) if isinstance(x, str) else x
            )
        responces['status_code'] = responces.apply(
            lambda x: x['parsed_responce']['response']['result']['code'], axis=1)
        responces['session'] = responces.apply(
            lambda x: x['parsed_responce']['response']['session']['id'], axis=1)
        responces['recommendations'] = responces.apply(
            lambda x: x['parsed_responce']['response']['recommendations'], axis=1)
        responces = responces[responces['recommendations'].map(len) > 0]
        responces = responces.explode('recommendations')
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

        # Сериализуем маршруты в читаемый вид
        responces['routes'] = responces.apply(
            lambda x: [
                {
                    'route_index': route['route_index'],
                    'segments': [
                        {'segment_index': segment['segment_index'],
                            'supplier_code': segment['supplier_code'],
                            'departure_city': segment['departure_city'],
                            'arrival_city': segment['arrival_city'],
                            'departure_time': segment['departure_time'],
                            'arrival_time': segment['arrival_time'],
                            'flight_number': segment['flight_number'],
                            'service_class': segment['service_class'],
                            'baggage': segment['baggage']
                         } for segment in route['segments']
                    ]
                } for route in x['recommendations']['routes']
            ],
            axis=1
        )

        responces['routes_formatted'] = responces.apply(
            lambda x: format_routes(x['recommendations']['routes']), axis=1
        )

        return responces

    async def get_top_directions(
        self,
        params: ConfigComparisonBody
        ) -> pd.DataFrame:
        """
        Retrieves the most popular travel directions from the statistics database.

        This method fetches the top travel directions for a given supplier airline
        from the `statistics.mvw_grouped_hits` table, filtered by date and provider.
        If no predefined directions are provided in `params.directions`, the data
        is queried from the database. Otherwise, a DataFrame is created using
        the given directions.

        Args:
            params: An object containing filtering parameters:
                - top_directions_from_date (str): Start date in format '%Y-%m-%d'.
                - filter_airlines (str): Airline supplier code to filter by.
                - limit_directions (int): Number of top directions to retrieve.
                - directions (list): Predefined list of directions (optional).

        Returns:
            pd.DataFrame: A DataFrame containing the top directions with columns:
                - 'supplier_code': Airline supplier code.
                - 'direction': The travel direction.
                - 'popularity': Popularity ranking of the direction.
        """
        if len(params.directions) == 0:
            kwargs = {
                "top_directions_from_date": params.top_directions_from_date,
                "filter_airlines": params.fast_search_params.filter_airlines,
                "limit_directions": params.limit_directions
                }
            statement = """
                SELECT supplier_code, LEFT(direction, 6) AS direction, sum(cnt) as popularity
                from "statistics".mvw_grouped_hits
                where 1=1
                and created >= :top_directions_from_date
                and supplier_code = :filter_airlines
                and provider = 'TUA'
                group by supplier_code, LEFT(direction, 6)
                order by popularity desc
                limit :limit_directions
                """
            result = await self._execute(statement, **kwargs)
            result = result.all()
            if not result:
                logger.error("step: %s , response : Error: %s", 'get_top_directions', 'empty df')
                return pd.DataFrame(columns=['supplier_code', 'direction', 'popularity'])
            result = pd.DataFrame(
                result, columns=['supplier_code', 'direction', 'popularity'])
            return result

        result = pd.DataFrame(params.directions)
        result.columns = ['direction']
        result['supplier_code'] = params.fast_search_params.filter_airlines
        result['popularity'] = result.index + 1
        return result

    async def make_config_comparison(
        self,
        params: ConfigComparisonBody
        ) -> dict:
        """
        Performs a configuration-based comparison of airline recommendations.

        This function retrieves the top flight directions, generates search URLs for two different
        configurations, fetches responses for each configuration, and then compares the recommendations.
        The comparison includes price differences, counts of recommendations per supplier, API key usage,
        and other relevant statistics.

        Args:
            params (dict): A dictionary containing the following keys:
                - api_key_1 (str): API key for the first configuration.
                - api_key_2 (str): API key for the second configuration.
                - avia_config_item_ids_1 (str): Config ID for the first API.
                - avia_config_item_ids_2 (str): Config ID for the second API.
                - top_directions_from_date (str): Start date for top directions in '%Y-%m-%d' format.
                - filter_airlines (str): Airline supplier code filter.
                - limit_directions (int): Number of top directions to retrieve.
                - directions (list): Predefined list of directions (optional).

        Returns:
            dict: A report containing the following comparison statistics:
                - 'count_directions': Number of unique flight directions analyzed.
                - 'count_min_recommendations': Count of minimal-priced recommendations.
                - 'count_recommendations': Total number of recommendations.
                - 'top_3_directions': List of the top 3 most popular flight directions.
                - 'top_suppliers_by_recommendations': Count of recommendations per supplier.
                - 'top_suppliers_by_directions': Count of suppliers in the analyzed directions.
                - 'top_api_keys_by_directions': Count of directions processed per API key.
                - 'top_api_keys_by_min_recommendations': Count of minimal recommendations per API key.
                - 'top_api_keys_by_recommendations': Count of total recommendations per API key.
                - 'avia_config_item_ids_by_directions': Count of config IDs per direction.
                - 'avia_config_item_ids_by_min_recommendations': Count of minimal recommendations per config ID.
                - 'avia_config_item_ids_by_recommendations': Count of total recommendations per config ID.
                - 'top_config_ids_min_recommendations_from': Most frequently occurring config IDs in minimal recommendations.
                - 'top_config_ids_recommendations_from': Most frequently occurring config IDs in total recommendations.
                - 'top_gds_ids_min_recommendations_from': Most frequently occurring GDS IDs in minimal recommendations.
                - 'top_gds_ids_recommendations_from': Most frequently occurring GDS IDs in total recommendations.
                - 'top_config_ids_directions_from': Most frequently occurring config IDs in top directions.
                - 'top_gds_ids_directions_from': Most frequently occurring GDS IDs in top directions.
                - 'price_diff_statistics': Statistical summary of price differences between configurations.

        """
        top_directions = await self.get_top_directions(params)

        if top_directions.empty:
            return convert_data({
                'Description':'''No data returned by sql query,
                make shure you set params.top_directions_from_date correctly or
                please try again with params.directions given.'''})
        top_directions['departure'] = top_directions.direction.str[:3]
        top_directions['arrival'] = top_directions.direction.str[3:]

        top_directions['url1'] = top_directions.apply(
            lambda row: self.url_constructor(params, 1, Route(departure=row.departure, arrival=row.arrival)), axis=1
        )
        top_directions['url2'] = top_directions.apply(
            lambda row: self.url_constructor(params, 2, Route(departure=row.departure, arrival=row.arrival)), axis=1
        )

        urls1 = top_directions.url1.to_list()
        urls2 = top_directions.url2.to_list()

        result1 = [
            await self.fetch_url_response(url)
            for url in urls1
        ]
        result2 = [await self.fetch_url_response(url) for url in urls2]

        responces1 = await self.make_recomendations_table(result1)
        responces2 = await self.make_recomendations_table(result2)
        responces1['api_key'] = params.api_key_1
        responces1['avia_config_item_ids'] = params.avia_config_item_ids_1
        responces2['api_key'] = params.api_key_2
        responces2['avia_config_item_ids'] = params.avia_config_item_ids_2
        recommendations = pd.concat(
            [responces1, responces2], ignore_index=True
        )

        min_recommendations_2_keys = (
            recommendations
            .groupby(by=['validating_supplier', 'routes_formatted', 'URL'], as_index=False).agg(
                {'amount': 'min'}
            )
            .merge(
                recommendations, how='left', left_on=['validating_supplier', 'routes_formatted', 'amount', 'URL'],
                right_on=['validating_supplier',
                          'routes_formatted', 'amount', 'URL']
            )[
                [
                    'validating_supplier',
                    'routes_formatted',
                    'amount',
                    'URL',
                    'status_code',
                    'session',
                    'trip_id',
                    'gds_id',
                    'config_id',
                    'api_key',
                    'avia_config_item_ids',
                ]
            ]
        )
        min_recommendations_2_keys = min_recommendations_2_keys.drop_duplicates()
        min_recommendations_2_keys = min_recommendations_2_keys.merge(
            top_directions[['direction', 'popularity',
                            'departure', 'arrival', 'url1']],
            how='left',
            left_on='URL',
            right_on='url1',
        )[
            [
                'direction',
                'popularity',
                'departure',
                'arrival',
                'validating_supplier',
                'routes_formatted',
                'amount',
                'status_code',
                'session',
                'trip_id',
                'gds_id',
                'config_id',
                'api_key',
                'avia_config_item_ids',
                'URL',
            ]

        ].merge(
            top_directions[['direction', 'popularity',
                            'departure', 'arrival', 'url2']],
            how='left',
            left_on='URL',
            right_on='url2'
        )
        min_recommendations_2_keys = min_recommendations_2_keys.drop_duplicates()
        min_recommendations_2_keys['direction'] = min_recommendations_2_keys['direction_x'].fillna(
            min_recommendations_2_keys['direction_y']
        )
        min_recommendations_2_keys['popularity'] = min_recommendations_2_keys['popularity_x'].fillna(
            min_recommendations_2_keys['popularity_y']
        )
        min_recommendations_2_keys['departure'] = min_recommendations_2_keys['departure_x'].fillna(
            min_recommendations_2_keys['departure_y']
        )
        min_recommendations_2_keys['arrival'] = min_recommendations_2_keys['arrival_x'].fillna(
            min_recommendations_2_keys['arrival_y']
        )
        min_recommendations_2_keys = min_recommendations_2_keys[
            [
                'direction',
                'popularity',
                'departure',
                'arrival',
                'validating_supplier',
                'routes_formatted',
                'amount',
                'status_code',
                'session',
                'trip_id',
                'gds_id',
                'config_id',
                'api_key',
                'avia_config_item_ids',
                'URL',
            ]
        ]
        min_recommendations_2_keys = min_recommendations_2_keys.drop_duplicates()

        min_recommendations = recommendations.groupby(
            by=['validating_supplier', 'routes_formatted'],
            as_index=False
        ).agg(
            {'amount': 'min'},
        ).merge(
            recommendations,
            how='left',
            left_on=['validating_supplier', 'routes_formatted', 'amount'],
            right_on=['validating_supplier', 'routes_formatted', 'amount'],
        )[
            [
                'validating_supplier',
                'routes_formatted',
                'amount',
                'URL',
                'status_code',
                'session',
                'trip_id',
                'gds_id',
                'config_id',
                'api_key',
                'avia_config_item_ids'
            ]
        ]
        min_recommendations = min_recommendations.drop_duplicates()
        min_recommendations = min_recommendations.merge(
            top_directions[
                ['direction', 'popularity', 'departure', 'arrival', 'url1']
            ],
            how='left',
            left_on='URL',
            right_on='url1',
        )[
            [
                'direction',
                'popularity',
                'departure',
                'arrival',
                'validating_supplier',
                'routes_formatted',
                'amount',
                'status_code',
                'session',
                'trip_id',
                'gds_id',
                'config_id',
                'api_key',
                'avia_config_item_ids',
                'URL',
            ]
        ].merge(
            top_directions[['direction', 'popularity',
                            'departure', 'arrival', 'url2']],
            how='left',
            left_on='URL',
            right_on='url2',
        )
        min_recommendations = min_recommendations.drop_duplicates()
        min_recommendations['direction'] = min_recommendations['direction_x'].fillna(
            min_recommendations['direction_y'])
        min_recommendations['popularity'] = min_recommendations['popularity_x'].fillna(
            min_recommendations['popularity_y'])
        min_recommendations['departure'] = min_recommendations['departure_x'].fillna(
            min_recommendations['departure_y'])
        min_recommendations['arrival'] = min_recommendations['arrival_x'].fillna(
            min_recommendations['arrival_y'])
        min_recommendations = min_recommendations[
            [
                'direction',
                'popularity',
                'departure',
                'arrival',
                'validating_supplier',
                'routes_formatted',
                'amount',
                'status_code',
                'session',
                'trip_id',
                'gds_id',
                'config_id',
                'api_key',
                'avia_config_item_ids',
                'URL',
            ]
        ]
        min_recommendations = min_recommendations.drop_duplicates()

        groupped_min_recommendations = min_recommendations.groupby(
            by=[
                'direction',
                'api_key',
                'avia_config_item_ids',
                'gds_id',
                'config_id',
                'validating_supplier',
                'popularity',
                'departure',
                'arrival',
            ],
            as_index=False
        ).agg({
            'routes_formatted': 'count',
            'amount': 'min',
            'trip_id': 'count'
            })

        vs = (
            min_recommendations_2_keys.groupby(
                ['routes_formatted'],
                as_index=False
            )
            .agg({'amount': 'min'})
            .merge(
                min_recommendations_2_keys.groupby(
                    ['routes_formatted'], as_index=False).agg({
                        'amount': 'max'
                        }),
                on='routes_formatted',
                how='inner',
            )
        )
        vs.columns = ['routes_formatted', 'min', 'max']
        vs['diff'] = vs['max'] - vs['min']
        vs['persent_diff'] = 100 * vs['diff'] / vs['max']

        report = {
            'count_directions': groupped_min_recommendations.direction.count(),
            'count_min_recomendations': min_recommendations.routes_formatted.count(),
            'count_recomendations': recommendations.routes_formatted.count(),

            'top_3_directions': top_directions.direction[:3].to_list(),
            'top_suppliers_by_recomendations': min_recommendations.validating_supplier.value_counts().to_dict(),
            'top_suppliers_by_directions': groupped_min_recommendations.validating_supplier.value_counts().to_dict(),

            'top_api_keys_by_directions': groupped_min_recommendations.api_key.value_counts().to_dict(),
            'top_api_keys_by_min_recomendations': min_recommendations.api_key.value_counts().to_dict(),
            'top_api_keys_by_recomendations': recommendations.api_key.value_counts().to_dict(),

            'avia_config_item_ids_by_directions': groupped_min_recommendations.avia_config_item_ids.value_counts().to_dict(),
            'avia_config_item_ids_by_min_recomendations': min_recommendations.avia_config_item_ids.value_counts().to_dict(),
            'avia_config_item_ids_by_recomendations': recommendations.avia_config_item_ids.value_counts().to_dict(),

            'top_config_ids_min_recomendations_from': min_recommendations.config_id.value_counts().to_dict(),
            'top_config_ids_recomendations_from': recommendations.config_id.value_counts().to_dict(),
            'top_gds_ids_min_recomendations_from': min_recommendations.gds_id.value_counts().to_dict(),
            'top_gds_ids_recomendations_from': recommendations.gds_id.value_counts().to_dict(),

            'top_config_ids_directions_from': groupped_min_recommendations.config_id.value_counts().to_dict(),
            'top_gds_ids_directions_from': groupped_min_recommendations.config_id.value_counts().to_dict(),
            'price_diff_statistics': vs.describe().to_dict()

        }

        return convert_data(report)
