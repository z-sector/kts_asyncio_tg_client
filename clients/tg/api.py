from json import JSONDecodeError
from typing import Optional, List

from aiohttp import ClientResponse

from clients.base import ClientError, Client
from clients.tg.dcs import UpdateObj, Message


class TgClientError(ClientError):
    pass


class TgClient(Client):
    BASE_PATH = 'https://api.telegram.org/bot'

    def __init__(self, token: str = ''):
        super().__init__()
        self.token = token

    def get_path(self, url: str) -> str:
        return f"{self.get_base_path().strip('/')}{self.token}/{url.lstrip('/')}"

    async def _handle_response(self, resp: ClientResponse) -> dict:
        if resp.status != 200:
            raise TgClientError(resp, await resp.text())
        try:
            data = await resp.json()
        except JSONDecodeError:
            raise TgClientError(resp, await resp.text())
        return await resp.json()

    async def get_me(self) -> dict:
        return await self._perform_request('get', self.get_path('getMe'))

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 0) -> dict:
        raise NotImplementedError

    async def get_updates_in_objects(self, *args, **kwargs) -> List[UpdateObj]:
        raise NotImplementedError

    async def send_message(self, chat_id: int, text: str) -> Message:
        raise NotImplementedError
