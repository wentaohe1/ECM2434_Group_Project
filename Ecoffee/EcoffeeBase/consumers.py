import json
import hmac
import time
from channels.generic.websocket import AsyncWebsocketConsumer

class QRConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_initial_params()

    async def send_initial_params(self):
        params = await self.generate_params()
        await self.send(json.dumps(params))

    async def generate_params(self):
        timestamp = int(time.time() // 1200) * 1200
        signature = hmac.new(
            b'your-secret-key-123',
            str(timestamp).encode(),
            'user111'
        ).hexdigest()
        return {'t': timestamp, 'sig': signature}

    async def keep_updating(self):
        while True:
            await asyncio.sleep(1200)
            params = await self.generate_params()
            await self.send(json.dumps(params))
