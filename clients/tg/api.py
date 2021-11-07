from typing import Optional, List

from clients.base import ClientError, Client
from clients.tg.dcs import UpdateObj, Message


class TgClientError(ClientError):
    pass


class TgClient(Client):
    def __init__(self, token: str = ''):
        self.token = token

    async def get_me(self) -> dict:
        raise NotImplementedError

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 0) -> dict:
        raise NotImplementedError

    async def get_updates_in_objects(self, *args, **kwargs) -> List[UpdateObj]:
        raise NotImplementedError

    async def send_message(self, chat_id: int, text: str) -> Message:
        raise NotImplementedError
