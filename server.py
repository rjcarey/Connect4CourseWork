from asyncio import Queue, create_task, wait, FIRST_COMPLETED, get_event_loop
from websockets import serve
from json import dumps
from configs import serverIP, serverPort
import sqlite3


class server:
    def __init__(self):
        # set of connected devices
        self.__connections = set()
        # queue of messages
        self.__messageQ = Queue()
        # Host List
        self.__hosts = set()

    async def __consumer_handler(self, websocket):
        async for message in websocket:
            # wait for a message and put it in the queue when received
            print(message)
            dictionary = eval(message)
            if dictionary.get('cmd', None) == 'hHost':
                self.__hosts.add(dictionary.get('from', None))
            elif dictionary.get('cmd', None) == 'cHost':
                self.__hosts.remove(dictionary.get('from', None))
            elif dictionary.get('cmd', None) == 'hJoin':
                if dictionary.get('joinCode', None) in self.__hosts:
                    self.__hosts.remove(dictionary.get('joinCode', None))
                    await self.__messageQ.put(message)
                else:
                    msg = {'to': dictionary.get('from', None), 'cmd': 'hnf'}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'logIn':
                username = dictionary.get('from', None)
                connection = sqlite3.connect('connectFour.db')
                # verify account details
                sql = f"SELECT * from ACCOUNTS WHERE USERNAME == '{username}'"
                accountInfo = connection.execute(sql)
                accountInfoRow = None
                for row in accountInfo:
                    accountInfoRow = row
                connection.close()
                msg = {'to': username, 'cmd': 'logIn', "accountInfo": accountInfoRow}
                print(msg)
                await self.__messageQ.put(dumps(msg))
            else:
                await self.__messageQ.put(message)

    async def __producer_handler(self):
        while True:
            # wait for a message in the message queue and when there is one, dequeue the first message
            message = await self.__messageQ.get()
            # if there are connected devices...
            if self.__connections:
                # complete send the message to each device in connections
                await wait([create_task(device.send(message)) for device in self.__connections])

    async def __server(self, websocket, path):
        # register connection
        self.__connections.add(websocket)
        try:
            # done = completed tasks, pending = uncompleted tasks
            # repeat call consumer handler then call producer handler until the first task is complete
            done, pending = await wait([create_task(self.__consumer_handler(websocket)), create_task(self.__producer_handler())], return_when=FIRST_COMPLETED)

            # cancel remaining tasks
            for task in pending:
                task.cancel()
        finally:
            # unregister connection
            self.__connections.remove(websocket)

    def run(self):
        loop = get_event_loop()
        # create a server which runs self._server on serverIP IP address, on serverPort port
        server_task = serve(self.__server, serverIP, serverPort)
        loop.run_until_complete(server_task)
        loop.run_forever()


if __name__ == "__main__":
    # create a server object
    server = server()
    # run the server
    server.run()
