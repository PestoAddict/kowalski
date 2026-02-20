import datetime as dt
import inspect
from functools import wraps
from typing import Callable, Awaitable, Any, Union, Iterable, Optional

import numpy as np
import pandas as pd

from src.core.config import settings
from src.utils.logger import logger


def depends_decorator(
        **decorator_kwargs: Union[
            Callable[[], Awaitable[Any]],
            Callable[[], Any],
            tuple[Callable[[Any], Awaitable[Any]], Iterable, dict],
            tuple[Callable[[Any], Any], Iterable, dict],

        ]
):
    """_summary_
    """
    def func_wrapper(func):
        """_summary_

        Args:
            func (_type_): _description_

        Returns:
            _type_: _description_
        """
        @wraps(func)
        async def inner(*args, **kwargs):
            """_summary_

            Returns:
                _type_: _description_
            """
            inner_kwargs = {}
            for key, value in decorator_kwargs.items():
                if isinstance(value, tuple):
                    result = value[0](*value[1], **value[2])
                else:
                    result = value()
                if inspect.isawaitable(result):
                    result = await result
                inner_kwargs[key] = result
            return await func(*args, **kwargs, **inner_kwargs)

        return inner

    return func_wrapper


def get_current_datetime(tz=3) -> dt.datetime:
    """_summary_

    Args:
        tz (int, optional): _description_. Defaults to 3.

    Returns:
        dt.datetime: _description_
    """
    return dt.datetime.now() + dt.timedelta(hours=tz - settings.TIMEZONE)


def get_current_day_datetime() -> dt.datetime:
    """_summary_

    Returns:
        dt.datetime: _description_
    """
    now = dt.datetime.now()
    return dt.datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=3,
        minute=0,
        second=0,
        tzinfo=now.tzinfo,
    )


def get_current_date() -> dt.date:
    """_summary_

    Returns:
        dt.date: _description_
    """
    return dt.date.today()


def get_number_of_days(
        dates: list[
            list[dt.date, dt.date]
        ]
) -> int:
    """_summary_

    Args:
        dates (list[ list[dt.date, dt.date] ]): _description_

    Returns:
        int: _description_
    """
    number_of_days = 0
    for start, end in dates:
        number_of_days += (end - start).days + 1
    return number_of_days


def get_first_day_of_the_year() -> dt.date:
    """_summary_

    Returns:
        dt.date: _description_
    """
    now = dt.datetime.now()
    return dt.date(
        year=now.year,
        month=1,
        day=1,
    )


def is_today_weekend() -> bool:
    """_summary_

    Returns:
        bool: _description_
    """
    current_weekday = dt.datetime.now().weekday()
    return current_weekday in [5, 6]


def get_current_month():
    """_summary_

    Returns:
        _type_: _description_
    """
    now = dt.datetime.now()
    return dt.date(
        year=now.year,
        month=now.month,
        day=1,
    )


def get_previous_month():
    """get_previous_month
    """
    now = dt.datetime.now()
    if now.month == 1:
        return dt.date(
            year=now.year - 1,
            month=12,
            day=1,
        )
    return dt.date(
        year=now.year,
        month=now.month - 1,
        day=1,
    )


def get_datetime_from_hour_and_minute(
        string: str,
        datetime_: Optional[dt.datetime] = None,
) -> dt.datetime:
    """_summary_

    Args:
        string (str): _description_
        datetime_ (Optional[dt.datetime], optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        dt.datetime: _description_
    """
    current_date = get_current_datetime() if datetime_ is None else datetime_
    h, m = list(map(int, string.split(":")))
    if not 0 <= h <= 23 and not 0 <= m <= 59:
        raise ValueError
    return dt.datetime(
        year=current_date.year,
        month=current_date.month,
        day=current_date.day,
        hour=h,
        minute=m,
    )


def log_handler(prefix: str = ""):
    """_summary_

    Args:
        prefix (str, optional): _description_. Defaults to "".
    """
    def func_wrapper(func):
        """_summary_

        Args:
            func (_type_): _description_

        Returns:
            _type_: _description_
        """
        @wraps(func)
        async def inner(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:  # pylint: disable=W0718
                await logger.critical(
                    f"{prefix} {func.__name__} failed \n {e}",
                )

        return inner

    return func_wrapper

def convert_data(data: Any) -> Union[dict, list, int, float, Any]:
    """
    Рекурсивно преобразует данные в удобный формат для JSON.

    - Преобразует словари, списки и NumPy/Pandas объекты в нативные Python типы.
    - Поддерживает `dict`, `list`, `np.integer`, `np.float`, `pd.Series`, `pd.DataFrame`, `pd.Index`.

    Args:
        data (Any): Входные данные любого типа.

    Returns:
        Union[dict, list, int, float, Any]: Преобразованные данные.
    """

    if isinstance(data, dict):
        return {key: convert_data(value) for key, value in data.items()}

    if isinstance(data, (list, pd.Index)):
        return [convert_data(item) for item in list(data)]

    if isinstance(data, (np.integer, np.int64)):
        return int(data)

    if isinstance(data, (np.floating, np.float64)):
        return float(data)

    if isinstance(data, (pd.Series, pd.DataFrame)):
        return data.to_dict()

    return data
