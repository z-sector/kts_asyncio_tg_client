from typing import List

import aiohttp
from aiohttp import ClientWebSocketResponse, WSMessage


async def fetch_10() -> List[float]:
    async with aiohttp.ClientSession() as session:
        ws: ClientWebSocketResponse = await session.ws_connect('wss://www.bitmex.com/realtime')
        await ws.__anext__()
        await ws.send_json({"op": "subscribe", "args": ["instrument:XBTUSD"]})
        await ws.__anext__()

        res = []
        while len(res) < 10:
            data: WSMessage = await ws.__anext__()
            json = data.json()

            price = json["data"][0].get('fairPrice')
            if price:
                res.append(price)

        await ws.close()

        return res

