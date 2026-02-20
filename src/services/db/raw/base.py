import contextlib
import sys
from typing import Union, cast, Optional

from sqlalchemy import text, Result
from sqlalchemy.ext.asyncio import (AsyncSession,
                                    AsyncSessionTransaction)
from sqlalchemy.orm import sessionmaker

from src.services.db.transaction import Transaction, TransactionStrategy

DEFAULT_STRATEGY = TransactionStrategy.ONE_PER_REQUEST
ASTERISK = '*'


class RawDatabaseService:
    table_name: str = None

    # table_name будет подставляться в statement,
    # ставьте {} куда нужно подставить в statement

    def __init__(
            self,
            session_or_pool: Union[sessionmaker, AsyncSession],
            *args,
            table_name: Optional[str] = None,
            transaction_strategy: Optional[TransactionStrategy] = TransactionStrategy.ONE_PER_REQUEST,
            **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if isinstance(session_or_pool, sessionmaker):
            self._session: AsyncSession = cast(AsyncSession, session_or_pool())
        else:
            self._session = session_or_pool
        self.table_name = self.table_name if table_name is None else table_name
        self.transaction_strategy = transaction_strategy
        self._transaction = Transaction(self._session, transaction_strategy)

    @contextlib.asynccontextmanager
    async def transaction(self) -> AsyncSessionTransaction:
        """_summary_

        Raises:
            ex: _description_

        Returns:
            AsyncSessionTransaction: _description_

        Yields:
            Iterator[AsyncSessionTransaction]: _description_
        """
        self._transaction.change_strategy(TransactionStrategy.KEEP_ALIVE)
        try:
            yield await self._transaction.__aenter__()  # noqa: WPS609  pylint:disable=unnecessary-dunder-call
        except Exception as ex:
            await self._transaction.__aexit__(*sys.exc_info())  # noqa: WPS609
            raise ex
        finally:
            await self._transaction.close()
            self._transaction.change_strategy(self.transaction_strategy)

    async def commit(self):
        """Use if you are using KEEP_ALIVE transactions"""
        await self._transaction.close()

    async def _execute(self, statement: str, **kwargs) -> Result:
        statement = text(statement.format(self.table_name))
        async with self._transaction:
            result: Result = await self._session.execute(statement, kwargs)
        return result
