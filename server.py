from asyncio import Queue, create_task, wait, FIRST_COMPLETED, get_event_loop
from websockets import serve
from json import dumps
from configs import serverIP, serverPort
import sqlite3
from sqlite3 import IntegrityError, OperationalError
from hashlib import pbkdf2_hmac
from os import urandom
from random import randint


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

            elif dictionary.get('cmd', None) == 'addAccount':
                # get random salt
                salt = urandom(4)
                # get the integer value of the salt to store
                key = int.from_bytes(salt, byteorder="big")
                # get hashed password
                hashedPassword = pbkdf2_hmac('sha256', dictionary.get('pword', None).encode('utf-8'), salt, 100000)
                connection = sqlite3.connect('connectFour.db')
                try:
                    # try to add the account to the database
                    sql = f"""INSERT INTO ACCOUNTS (USERNAME,KEY,HPWORD,SPLAYED,SWON,SLOST,SDRAWN,SPFIN,SPMADE) VALUES ("{dictionary.get('from', None)}", "{key}", "{hashedPassword}", 0, 0, 0, 0, 0, 0)"""
                    connection.execute(sql)
                    connection.commit()
                    # close connection
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'addAccount', "valid": True}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
                except IntegrityError:
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'addAccount', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'updatePFin':
                connection = sqlite3.connect('connectFour.db')
                try:
                    stmt = f"UPDATE ACCOUNTS set SPFIN = {dictionary.get('pFin', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    connection.execute(stmt)
                    connection.commit()
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": True}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
                except OperationalError:
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'updatePMade':
                connection = sqlite3.connect('connectFour.db')
                try:
                    stmt = f"UPDATE ACCOUNTS set SPMADE = {dictionary.get('pMade', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    connection.execute(stmt)
                    connection.commit()
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": True}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
                except OperationalError:
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get("cmd", None) == 'updateGameStats':
                connection = sqlite3.connect('connectFour.db')
                try:
                    connection = sqlite3.connect('connectFour.db')
                    stmt = f"UPDATE ACCOUNTS set SPLAYED = {dictionary.get('played', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    connection.execute(stmt)
                    stmt = f"UPDATE ACCOUNTS set SWON = {dictionary.get('won', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    connection.execute(stmt)
                    stmt = f"UPDATE ACCOUNTS set SLOST = {dictionary.get('lost', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    connection.execute(stmt)
                    stmt = f"UPDATE ACCOUNTS set SDRAWN = {dictionary.get('drawn', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    connection.execute(stmt)
                    connection.commit()
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": True}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
                except OperationalError:
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))#

            elif dictionary.get('cmd', None) == 'loadPuzzle':
                username = dictionary.get('from', None)
                puzzleCode = dictionary.get('puzzleID', None)
                connection = sqlite3.connect('connectFour.db')
                if puzzleCode == "random":
                    # get random puzzle id from the saved puzzles
                    sql = f"SELECT * from PUZZLES"
                    puzzleInfo = connection.execute(sql)
                    results = puzzleInfo.fetchall()
                    puzzleCode = results[randint(0, len(results) - 1)][0]
                # get the puzzle game info using the puzzle id
                sql = f"SELECT ID, MOVES, SOLUTION from PUZZLES WHERE ID == '{puzzleCode}'"
                puzzleInfo = connection.execute(sql)
                puzzleInfoRow = None
                for row in puzzleInfo:
                    puzzleInfoRow = row
                connection.close()
                msg = {'to': username, 'cmd': 'loadPuzzle', "puzzleInfo": puzzleInfoRow}
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
