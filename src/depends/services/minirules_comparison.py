from typing import Optional

from src.depends.db.session import get_session
from src.services.minirules_comparison import MinirulesComparisonService
from src.services.db.transaction import TransactionStrategy


async def get_minirules_comparison_service(
        transaction_strategy: Optional[TransactionStrategy] = TransactionStrategy.ONE_PER_REQUEST,
) -> MinirulesComparisonService:
    """
    Args:
        transaction_strategy (Optional[TransactionStrategy], optional):
        Defaults to TransactionStrategy.ONE_PER_REQUEST.

    Returns:
        MinirulesComparisonService:
    """
    return MinirulesComparisonService(
        session_or_pool=get_session(db='postgresql_core'),
        transaction_strategy=transaction_strategy
    )
