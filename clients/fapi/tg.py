from clients.tg.api import TgClient
from clients.tg.dcs import File, Message


class TgClientWithFile(TgClient):
    async def get_file(self, file_id: str) -> File:
        data = await self._perform_request('get', self.get_path('getFile'), params={"file_id": file_id})
        file: File = File.Schema().load(data['result'])
        return file

    async def download_file(self, file_path: str, destination_path: str):
        raise NotImplementedError

    async def send_document(self, chat_id: int, document_path) -> Message:
        raise NotImplementedError
