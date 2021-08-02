from asyncio import Queue, create_task, wait, FIRST_COMPLETED, get_event_loop
from websockets import serve
from configs import serverIP, serverPort


class server:
    def __innit__(self):
        #set of connected devices
        self._connections = set()
        #queue of messages
        self._messageQ = Queue()

    async def _consumer_handler(self, websocket):
        async for message in websocket:
            #wait for a message and put it in the queue when received
            await self._messageQ.put(message)

    async def _producer_handler(self):
        while True:
            #wait for a message in the message queue and when there is one, dequeue the first message
            message = await self._messageQ.get()
            #if there are connected devices...
            if self._connections:
                #complete send the message to each device in connections
                await wait([create_task(device.send(message)) for device in self._connections])

    async def _server(self, websocket, path):
        #register connection
        self._connections.add(websocket)
        try:
            #done = completed tasks, pending = uncompleted tasks
            #repeat call consumer handler then call producer handler until the first task is complete
            done, pending = await wait([create_task(self._consumer_handler(websocket)), create_task(self._producer_handler())], return_when=FIRST_COMPLETED)

            #cancel remaining tasks
            for task in pending:
                task.cancel()
        finally:
            #unregister connection
            self._connections.remove(websocket)

    def run(self):
        loop = get_event_loop()
        #create a server which runs self._server on serverIP IP address, on serverPort port
        server_task = serve(self._server, serverIP, serverPort)
        loop.run_until_complete(server_task)
        loop.run_forever()

if __name__ == "__main__":
    #create s server object
    server = server()
    #run the server
    server.run()