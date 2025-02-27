from kademlia.network import Server
import asyncio

class DHTServer:
    def __init__(self):
        self.server = Server()
        self.loop = asyncio.new_event_loop()

    async def bootstrap(self):
        await self.server.listen(8468)
        await self.server.bootstrap([("127.0.0.1", 8468)])

    async def set(self, key, value):
        await self.server.set(key, value)

    async def get(self, key):
        return await self.server.get(key)

    async def register_user(self, user_id, host, port):
        """
        Регистрирует пользователя в DHT.
        """
        await self.set(user_id, f"{host}:{port}")

    async def find_user(self, user_id):
        """
        Ищет пользователя в DHT по его ID.
        """
        return await self.get(user_id)