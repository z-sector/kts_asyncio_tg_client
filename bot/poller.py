import asyncio
from typing import Optional

from bot.utils import log_exceptions
from clients.fapi.tg import TgClientWithFile


class Poller:
    def __init__(self, token: str, queue: asyncio.Queue):
        self.tg_client = TgClientWithFile(token)
        self.queue = queue
        self.is_running = False
        # обязательный параметр, в _task нужно положить запущенную корутину поллера
        self._task: Optional[asyncio.Task] = None

    async def _worker(self):
        """
        нужно получать данные из tg, стоит использовать метод get_updates_in_objects
        полученные сообщения нужно положить в очередь queue
        в очередь queue нужно класть UpdateObj
        """
        offset = 0
        while self.is_running:
            updates = await self.tg_client.get_updates_in_objects(offset=offset, timeout=60)
            for u in updates:
                offset = u.update_id + 1
                self.queue.put_nowait(u)

    def start(self):
        """
        нужно запустить корутину _worker
        """
        self.is_running = True
        self._task = asyncio.create_task(log_exceptions(self._worker()))

    async def stop(self):
        """
        нужно отменить корутину _worker и дождаться ее отмены
        """
        self.is_running = False
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
