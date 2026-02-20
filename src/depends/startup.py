from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# pylint: disable=unused-import
from src.core.config import settings
from src.db import main_db


async def startup():
    """startup
    """

    postgresql_core_engine = create_async_engine(
        settings.POSTGRES_CORE.build_url(),
        connect_args={'server_settings': {'application_name': settings.PROJECT_NAME}},
    )

    postgresql_stats_engine = create_async_engine(
        settings.POSTGRES_STATS.build_url(),
        connect_args={'server_settings': {'application_name': settings.PROJECT_NAME}},
    )

    main_db.session_factory['postgresql_core'] = sessionmaker(
        bind=postgresql_core_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    main_db.session_factory['postgresql_stats'] = sessionmaker(
        bind=postgresql_stats_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
