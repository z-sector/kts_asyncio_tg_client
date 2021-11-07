from json import JSONDecodeError
from typing import Optional, List

from aiohttp import ClientResponse
from marshmallow import ValidationError

from clients.base import ClientError, Client
from clients.tg.dcs import UpdateObj, Message, GetUpdatesResponse


class TgClientError(ClientError):
    pass


class TgClient(Client):
    BASE_PATH = 'https://api.telegram.org'

    def __init__(self, token: str = ''):
        super().__init__()
        self.token = token

    def get_path(self, url: str) -> str:
        return f"{self.get_base_path().strip('/')}/bot{self.token}/{url.lstrip('/')}"

    async def _handle_response(self, resp: ClientResponse) -> dict:
        if resp.status >= 400:
            raise TgClientError(resp, await resp.text())
        try:
            data = await resp.json()
        except JSONDecodeError:
            raise TgClientError(resp, await resp.text())
        return data

    async def get_me(self) -> dict:
        return await self._perform_request('get', self.get_path('getMe'))

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 0) -> dict:
        params = {} if offset is None else {'offset': offset}
        if timeout > 0:
            params['timeout'] = timeout
        data = await self._perform_request('get', self.get_path('getUpdates'), params=params)
        return data

    async def get_updates_in_objects(self, *args, **kwargs) -> List[UpdateObj]:
        data = await self.get_updates(*args, **kwargs)
        try:
            resp_obj: GetUpdatesResponse = GetUpdatesResponse.Schema().load(data)
        except ValidationError:
            raise TgClientError(data)
        return resp_obj.result

    async def send_message(self, chat_id: int, text: str) -> Message:
        data = await self._perform_request('post', self.get_path('sendMessage'), json={'chat_id': chat_id, 'text': text})
        res: Message = Message.Schema().load(data['result'])
        return res
