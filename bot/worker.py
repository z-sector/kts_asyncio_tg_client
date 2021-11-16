import asyncio
from dataclasses import dataclass
from typing import List, Set

from bot.utils import log_exceptions
from clients.fapi.s3 import S3Client
from clients.fapi.tg import TgClientWithFile
from clients.tg.dcs import UpdateObj


@dataclass
class WorkerConfig:
    endpoint_url: str
    aws_secret_access_key: str
    aws_access_key_id: str
    bucket: str
    concurrent_workers: int = 1


class Worker:
    def __init__(self, token: str, queue: asyncio.Queue, config: WorkerConfig):
        self.tg_client = TgClientWithFile(token)
        self.queue = queue
        self.config = config
        self.is_running = False
        # обязательный параметр, в него нужно сохранить запущенные корутины воркера
        self._tasks: List[asyncio.Task] = []
        # обязательный параметр, выполнять работу с s3 нужно через объект класса self.s3
        # для загрузки файла нужно использовать функцию fetch_and_upload или stream_upload
        self.users: Set[int] = set()
        self.s3 = S3Client(
            endpoint_url=config.endpoint_url,
            aws_secret_access_key=config.aws_secret_access_key,
            aws_access_key_id=config.aws_access_key_id
        )

    async def handle_update(self, upd: UpdateObj):
        """
        в этом методе должна происходить обработка сообщений и реализация бизнес-логики
        бизнес-логика бота тестируется с помощью этого метода, файл с тестами tests.bot.test_worker::TestHandler
        """
        user_id = upd.message.from_.id
        if user_id not in self.users:
            await self.tg_client.send_message(upd.message.chat.id, '[greeting]')
            self.users.add(user_id)
            return

        if upd.message.document:
            await self.tg_client.send_message(upd.message.chat.id, '[document]')
            f = await self.tg_client.get_file(upd.message.document.file_id)
            url = f'{self.tg_client.API_PATH}/file/bot{self.tg_client.token}/{f.file_path}'
            await self.s3.fetch_and_upload(self.config.bucket, upd.message.document.file_name, url)
            await self.tg_client.send_message(upd.message.chat.id, '[document has been saved]')
        else:
            await self.tg_client.send_message(upd.message.chat.id, '[document is required]')

    async def _worker(self):
        """
        должен получать сообщения из очереди и вызывать handle_update
        """
        while True:
            upd = await self.queue.get()
            await self.handle_update(upd)
            self.queue.task_done()

    def start(self):
        """
        должен запустить столько воркеров, сколько указано в config.concurrent_workers
        запущенные задачи нужно положить в _tasks
        """
        self.is_running = True
        self._tasks = [
            asyncio.create_task(log_exceptions(self._worker()))
            for _ in range(self.config.concurrent_workers)
        ]

    async def stop(self):
        """
        нужно дождаться пока очередь не станет пустой (метод join у очереди), а потом отменить все воркеры
        """
        await self.queue.join()
        self.is_running = False
        for t in self._tasks:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass
