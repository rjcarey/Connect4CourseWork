from configs import serverIP, serverPort
from asyncio import Queue, wait, create_task, FIRST_COMPLETED
from json import dumps, loads
from websockets import connect


class client:
    def __init__(self):
        self.__uri = f"ws://{serverIP}:{serverPort}"
        self.__txq = Queue()
        self.__rxq = Queue()
        self.__running = False

    def quit(self):
        self.__running = False
        # put items into each queue without blocking
        self.__txq.put_nowait(dumps("Stop"))
        self.__rxq.put_nowait(dumps("Stop"))

    async def send(self, message):
        # wait to put message in the transmit queue
        # print(message)
        await self.__txq.put(dumps(message))

    async def recv(self):
        # wait until a message is received
        message = await self.__rxq.get()
        return loads(message)

    def canRcv(self):
        return False if self.__rxq.empty() else True

    async def __consumer_handler(self, websocket):
        # while the client is running
        while self.__running:
            # wait to receive a message from the websocket
            message = await websocket.recv()
            # wait to put it in the receive queue
            await self.__rxq.put(message)

    async def __producer_handler(self, websocket):
        # while the client is running
        while self.__running:
            # wait for a message to transmit
            message = await self.__txq.get()
            # wait to send the message to the websocket
            await websocket.send(message)

    async def run(self):
        # set the client state to be running
        self.__running = True
        async with connect(self.__uri) as websocket:
            # done = completed tasks, pending = uncompleted tasks
            # repeat call consumer handler then call producer handler until the first task is complete
            done, pending = await wait([create_task(self.__consumer_handler(websocket)), create_task(self.__producer_handler(websocket))], return_when=FIRST_COMPLETED)
            # cancel remaining tasks
            for task in pending:
                task.cancel()
