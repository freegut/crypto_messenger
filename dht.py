from kademlia.network import Server
import asyncio

class DHTServer:
    def __init__(self):
        self.server = Server()
        self.loop = asyncio.new_event_loop()

    def bootstrap(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.server.listen(8468))
        self.loop.run_until_complete(self.server.bootstrap([("127.0.0.1", 8468)]))

    def set(self, key, value):
        self.loop.run_until_complete(self.server.set(key, value))

    def get(self, key):
        return self.loop.run_until_complete(self.server.get(key))