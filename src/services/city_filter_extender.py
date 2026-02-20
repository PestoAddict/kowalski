import pandas as pd

class CityFilterExtenderService:
    def expand_directions(self, direction:str) -> list:
        """Makes list of possible directions contains 2 points from given direction

        Args:
            direction (str): a pair like "MOW-LED"

        Returns:
            list: list of possible directions like ["MOW-LED","LED-MOW","MOW-LED|LED-MOW","LED-MOW|MOW-LED"]
        """
        parts = direction.split('-')
        reverse = f"{parts[1]}-{parts[0]}"
        return [direction, reverse, f"{direction}|{reverse}", f"{reverse}|{direction}"]

    def process_city_filter(self, file_content: bytes):
        """
        Processes the city filter by reading file content, cleaning the data,
        expanding directions, and generating a downloadable CSV response.

        This method:
        - Reads and decodes the file content into a list of city directions.
        - Removes extra whitespace and extracts unique city directions.
        - Trims each direction to the first 7 characters.
        - Expands directions using the `expand_directions` method.
        - Removes duplicates and prepares the result as a txt file.

        Returns:
            StreamingResponse: A text-based response containing the processed
            city filter data as a txt file.
        """
        lines = file_content.decode('utf-8').splitlines()
        city_filter = pd.DataFrame(lines, columns=['Direction'])

        city_filter['Direction'] = city_filter['Direction'].str.strip()
        city_filter_unique = city_filter['Direction'].unique()
        city_filter = pd.DataFrame(city_filter_unique, columns=['Direction'])
        city_filter['Direction'] = city_filter['Direction'].str[:7]

        expanded_directions = []
        for direction in city_filter['Direction']:
            expanded_directions.extend(self.expand_directions(direction))

        new_filter = pd.DataFrame(expanded_directions, columns=['Direction'])
        new_filter=new_filter.drop_duplicates()

        return new_filter

city_filter_extender = CityFilterExtenderService()
