from http.cookies import SimpleCookie
from json import JSONDecodeError
from typing import Tuple

from aiohttp import ClientResponse

from clients.base import ClientError, Client


class LmsClientError(ClientError):
    pass


class LmsClient(Client):
    BASE_PATH = 'https://lms.metaclass.kts.studio/api'

    def __init__(self, token: str):
        super().__init__()
        self.token = token

    async def _handle_response(self, resp: ClientResponse) -> Tuple[dict, ClientResponse]:
        if resp.status >= 400:
            raise LmsClientError(resp, await resp.text())
        try:
            data = await resp.json()
        except JSONDecodeError:
            raise LmsClientError(resp, await resp.text())
        return data, resp

    async def get_user_current(self) -> dict:
        data, resp = await self._perform_request('get', self.get_path('v2.user.current'))
        return data

    async def login(self, email: str, password: str) -> str:
        data, resp = await self._perform_request('post', self.get_path('v2.user.login'), json={'email': email, 'password': password})
        cookies: SimpleCookie[str] = resp.cookies

        cookie_session = cookies.get('sessionid')
        if cookie_session is None:
            raise LmsClientError(resp, await resp.text())

        return cookie_session.value
