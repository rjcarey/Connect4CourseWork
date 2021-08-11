from configs import serverIP, serverPort
from asyncio import Queue, wait, create_task, FIRST_COMPLETED
from json import dumps, loads
from websockets import connect


class client:
    def __init__(self):
        self._uri = f"ws://{serverIP}:{serverPort}"
        self._txq = Queue()
        self._rxq = Queue()
        self._running = False

    def quit(self):
        self._running = False
        # put items into each queue without blocking
        self._txq.put_nowait(dumps("Stop"))
        self._rxq.put_nowait(dumps("Stop"))

    async def send(self, message):
        # wait to put message in the transmit queue
        # print(message)
        await self._txq.put(dumps(message))

    async def recv(self):
        # wait until a message is received
        message = await self._rxq.get()
        return loads(message)

    async def _consumer_handler(self, websocket):
        # while the client is running
        while self._running:
            # wait to receive a message from the websocket
            message = await websocket.recv()
            # wait to put it in the receive queue
            await self._rxq.put(message)

    async def _producer_handler(self, websocket):
        # while the client is running
        while self._running:
            # wait for a message to transmit
            message = await self._txq.get()
            # wait to send the message to the websocket
            await websocket.send(message)

    async def run(self):
        # set the client state to be running
        self._running = True
        async with connect(self._uri) as websocket:
            # done = completed tasks, pending = uncompleted tasks
            # repeat call consumer handler then call producer handler until the first task is complete
            done, pending = await wait([create_task(self._consumer_handler(websocket)), create_task(self._producer_handler(websocket))],return_when=FIRST_COMPLETED)
            # cancel remaining tasks
            for task in pending:
                task.cancel()
