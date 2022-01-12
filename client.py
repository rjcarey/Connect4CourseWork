from configs import serverIP, serverPort
from asyncio import Queue, wait, create_task, FIRST_COMPLETED
from json import dumps, loads
from websockets import connect


##############################################
# GROUP A SKILL: Complex Client-Server Model #
##############################################
class client:
    def __init__(self):
        self.__uri = f"ws://{serverIP}:{serverPort}"
        #########################
        # GROUP A SKILL: Queues #
        #########################
        self.__txq = Queue()
        self.__rxq = Queue()
        self.__running = False

    def quit(self):
        self.__running = False
        ###################################################################################
        # GROUP A SKILL                                                                   #
        #   ===========================================================================   #
        # Using JSON loads and dumps to convert python data structure to and from strings #
        ###################################################################################
        self.__txq.put_nowait(dumps("stop"))
        self.__rxq.put_nowait(dumps("stop"))

    async def send(self, message):
        # Non-blocking wait to put message in the transmit queue as a string
        ###################################################################################
        # GROUP A SKILL                                                                   #
        #   ===========================================================================   #
        # Using JSON loads and dumps to convert python data structure to and from strings #
        ###################################################################################
        await self.__txq.put(dumps(message))

    async def recv(self):
        # Non-blocking wait until a message is received and return it as a string
        message = await self.__rxq.get()
        ###################################################################################
        # GROUP A SKILL                                                                   #
        #   ===========================================================================   #
        # Using JSON loads and dumps to convert python data structure to and from strings #
        ###################################################################################
        return loads(message)

    def canRcv(self):
        # Non-blocking check to check if there are received messages to handle
        return False if self.__rxq.empty() else True

    async def __consumer_handler(self, websocket):
        while self.__running:
            # Non-blocking wait to receive a message from the server
            message = await websocket.recv()
            # Non-blocking wait to put the message in the receive queue
            await self.__rxq.put(message)

    async def __producer_handler(self, websocket):
        while self.__running:
            # Non-blocking wait for a message to transmit
            message = await self.__txq.get()
            # Non-blocking wait to send the message to the server
            await websocket.send(message)

    async def run(self):
        self.__running = True
        async with connect(self.__uri) as websocket:
            # Repeatedly call the consumer handler method then call producer handler method until the first task is complete
            done, pending = await wait([create_task(self.__consumer_handler(websocket)), create_task(self.__producer_handler(websocket))], return_when=FIRST_COMPLETED)
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
