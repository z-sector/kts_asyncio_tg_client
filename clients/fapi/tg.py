from json import JSONDecodeError

import aiohttp

from clients.tg.api import TgClient, TgClientError
from clients.tg.dcs import File, Message


class TgClientWithFile(TgClient):
    async def get_file(self, file_id: str) -> File:
        data = await self._perform_request('get', self.get_path('getFile'), params={"file_id": file_id})
        file: File = File.Schema().load(data['result'])
        return file

    async def download_file(self, file_path: str, destination_path: str):
        async with self.session.request('get', f'{self.get_base_path()}/file/bot{self.token}/{file_path}') as resp:
            if resp.status >= 400:
                raise TgClientError(resp, await resp.text())

            with open(destination_path, 'wb') as fd:
                async for data in resp.content.iter_chunked(1024):
                    fd.write(data)

    async def send_document(self, chat_id: int, document_path) -> Message:
        data = aiohttp.FormData()
        data.add_field(
            'document',
            open(document_path, 'rb'),
            content_type='text/plain'
        )
        data.add_field(
            'chat_id',
            chat_id,
            content_type='text/plain'
        )

        async with self.session.request('post', self.get_path('sendDocument'), data=data) as resp:
            if resp.status >= 400:
                raise TgClientError(resp, await resp.text())

            try:
                data = await resp.json()
            except JSONDecodeError:
                raise TgClientError(resp, await resp.text())

            res: Message = Message.Schema().load(data['result'])

        return res

