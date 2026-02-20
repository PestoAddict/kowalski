from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from src.utils import exceptions

session_factory: dict[str, sessionmaker] = {}
engines: dict[str, AsyncEngine] = {}
Base = declarative_base()


def get_session_factory(db: str) -> sessionmaker:
    """_summary_

    Args:
        db (str): _description_

    Raises:
        exceptions.DatabaseExemplarNotFoundError: _description_

    Returns:
        sessionmaker: _description_
    """
    if not session_factory[db]:
        raise exceptions.DatabaseExemplarNotFoundError
    return session_factory[db]
