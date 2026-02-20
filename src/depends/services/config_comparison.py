from typing import Optional

from src.depends.db.session import get_session
from src.services.config_comparison import ConfigComparisonService
from src.services.db.transaction import TransactionStrategy


async def get_config_comparison_service(
        transaction_strategy: Optional[TransactionStrategy] = TransactionStrategy.ONE_PER_REQUEST,
) -> ConfigComparisonService:
    """
    Args:
        transaction_strategy (Optional[TransactionStrategy], optional).
        Defaults to TransactionStrategy.ONE_PER_REQUEST.

    Returns:
        ConfigComparisonService:
    """
    return ConfigComparisonService(
        session_or_pool=get_session(db='postgresql_stats'),
        transaction_strategy=transaction_strategy
    )
