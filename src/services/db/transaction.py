import enum
from typing import Optional

from sqlalchemy.ext.asyncio import (AsyncSession,
                                    AsyncSessionTransaction)


class TransactionStrategy(enum.IntEnum):
    ONE_PER_REQUEST = 1
    KEEP_ALIVE = 2


DEFAULT_STRATEGY = TransactionStrategy.ONE_PER_REQUEST


class Transaction:
    """
    Данная обвертка позволяет выполнять несколько запросов в транзакции и управлять тем,
    когда именно нужно закоммитить изменения
    """

    def __init__(self, session: AsyncSession, strategy: TransactionStrategy):
        self._session = session
        self._strategy = strategy
        self._current_txn: Optional[AsyncSessionTransaction] = None

    async def __aenter__(self) -> AsyncSessionTransaction:
        """_summary_

        Returns:
            AsyncSessionTransaction: _description_
        """
        if self._current_txn is not None and self._strategy == TransactionStrategy.KEEP_ALIVE:
            return self._current_txn
        self._current_txn = self._session.begin()
        await self._current_txn.start()
        return self._current_txn

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """_summary_

        Args:
            exc_type (_type_): _description_
            exc_val (_type_): _description_
            exc_tb (_type_): _description_

        Returns:
            _type_: _description_
        """
        if exc_type is not None or exc_val is not None or exc_tb is not None:
            return await self._current_txn.__aexit__(exc_type, exc_val, exc_tb)  # noqa: WPS609
        if self._strategy == TransactionStrategy.KEEP_ALIVE:
            return None
        await self._current_txn.__aexit__(exc_type, exc_val, exc_tb)  # noqa: WPS609

    async def close(self) -> None:
        """_summary_
        """
        await self._current_txn.__aexit__(None, None, None)  # noqa: WPS609

    def change_strategy(self, new_strategy: TransactionStrategy) -> None:
        """_summary_

        Args:
            new_strategy (TransactionStrategy): _description_
        """
        self._strategy = new_strategy
