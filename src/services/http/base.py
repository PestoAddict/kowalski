from abc import abstractmethod
from typing import Optional

import httpx


class AbstractHTTPClient:

    @abstractmethod
    async def get(
            self,
            url: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None,
            timeout: int = 60,
    ) -> tuple[dict, int]:
        """_summary_

        Args:
            url (str): _description_
            params (dict, optional): _description_. Defaults to None.
            headers (dict, optional): _description_. Defaults to None.
            timeout (int, optional): _description_. Defaults to 60.

        Returns:
            tuple[dict, int]: _description_
        """


    @abstractmethod
    async def post(
            self,
            url: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None,
            body: Optional[dict] = None,
    ) -> tuple[dict, int]:
        """_summary_

        Args:
            url (str): _description_
            params (dict, optional): _description_. Defaults to None.
            headers (dict, optional): _description_. Defaults to None.
            body (dict, optional): _description_. Defaults to None.

        Returns:
            tuple[dict, int]: _description_
        """



class HTTPXClient(AbstractHTTPClient):
    client: httpx.AsyncClient

    def __init__(self, *args, **kwargs):
        """_summary_
        """
        super().__init__(*args, **kwargs)
        self.client = httpx.AsyncClient()

    async def get(
            self,
            url: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None,
            timeout: Optional[int] = 60,
    ) -> tuple[dict, int]:
        params = {} if params is None else params
        headers = {} if headers is None else headers
        response = await self.client.get(
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json(), response.status_code

    async def post(
            self,
            url: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None,
            body: Optional[dict] = None,
    ) -> tuple[dict, int]:
        """_summary_

        Args:
            url (str): _description_
            params (dict, optional): _description_. Defaults to None.
            headers (dict, optional): _description_. Defaults to None.
            body (dict, optional): _description_. Defaults to None.

        Returns:
            tuple[dict, int]: _description_
        """
        params = {} if params is None else params
        headers = {} if headers is None else headers
        body = {} if body is None else body
        response = await self.client.post(
            url=url,
            params=params,
            headers=headers,
            json=body
        )
        response.raise_for_status()
        return response.json(), response.status_code
