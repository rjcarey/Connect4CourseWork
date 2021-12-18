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
        # Set of connected devices
        self.__connections = set()
        # Set of hosts
        self.__hosts = set()
        self.__messageQ = Queue()

    async def __consumer_handler(self, websocket):
        async for message in websocket:
            # Wait for a message and put it in the queue when received
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
                sql = f"SELECT * FROM ACCOUNTS WHERE USERNAME == '{username}'"
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
                    sql = f"INSERT INTO ACCOUNTS (USERNAME,KEY,HPWORD,SPLAYED,SWON,SLOST,SDRAWN,SPFIN,SPMADE) VALUES ('{dictionary.get('from', None)}', '{key}', '{hashedPassword}', 0, 0, 0, 0, 0, 0)"
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
                    stmt = f"UPDATE ACCOUNTS SET SPFIN = {dictionary.get('pFin', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
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
                    stmt = f"UPDATE ACCOUNTS SET SPMADE = {dictionary.get('pMade', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
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
                    stmt = f"UPDATE ACCOUNTS SET SPLAYED = {dictionary.get('played', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    connection.execute(stmt)
                    stmt = f"UPDATE ACCOUNTS SET SWON = {dictionary.get('won', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    connection.execute(stmt)
                    stmt = f"UPDATE ACCOUNTS SET SLOST = {dictionary.get('lost', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    connection.execute(stmt)
                    stmt = f"UPDATE ACCOUNTS SET SDRAWN = {dictionary.get('drawn', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
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

            elif dictionary.get('cmd', None) == 'loadPuzzle':
                username = dictionary.get('from', None)
                puzzleCode = dictionary.get('puzzleID', None)
                connection = sqlite3.connect('connectFour.db')
                if puzzleCode == "random":
                    # get random puzzle id from the saved puzzles
                    sql = f"SELECT * FROM PUZZLES"
                    puzzleInfo = connection.execute(sql)
                    results = puzzleInfo.fetchall()
                    puzzleCode = results[randint(0, len(results) - 1)][0]
                # get the puzzle game info using the puzzle id
                sql = f"SELECT ID, MOVES, SOLUTION FROM PUZZLES WHERE ID == '{puzzleCode}'"
                puzzleInfo = connection.execute(sql)
                puzzleInfoRow = None
                for row in puzzleInfo:
                    puzzleInfoRow = row
                connection.close()
                msg = {'to': username, 'cmd': 'loadPuzzle', "puzzleInfo": puzzleInfoRow}
                print(msg)
                await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'savePuzzle':
                # connect to database
                connection = sqlite3.connect('connectFour.db')
                try:
                    # add game to database
                    sql = f"INSERT INTO PUZZLES (ID,MOVES,SOLUTION) VALUES ('{dictionary.get('puzzleID', None)}', '{dictionary.get('puzzleMoves', None)}', '{dictionary.get('puzzleSolution', None)}')"
                    connection.execute(sql)
                    connection.commit()
                    # close connection
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'savePuzzle', "valid": True}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
                except IntegrityError:
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'savePuzzle', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'loadGame':
                username = dictionary.get('from', None)
                gameName = dictionary.get('gameName', None)
                connection = sqlite3.connect('connectFour.db')
                # get the game info of the game identified by the name
                sql = f"SELECT NAME, MOVES, OPPONENT, ACCOUNT FROM SAVES WHERE NAME == '{gameName}' AND ACCOUNT == '{username}'"
                gameInfo = connection.execute(sql)
                gameInfoRow = None
                for row in gameInfo:
                    gameInfoRow = row
                connection.close()
                msg = {'to': username, 'cmd': 'loadPuzzle', "gameInfo": gameInfoRow}
                print(msg)
                await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'saveGame':
                # connect to database
                connection = sqlite3.connect('connectFour.db')
                try:
                    # add game to database
                    sql = f"INSERT INTO SAVES (NAME,MOVES,OPPONENT,ACCOUNT) VALUES ('{dictionary.get('gameName', None)}', '{dictionary.get('gameMoves', None)}', '{dictionary.get('opponent', None)}', '{dictionary.get('from', None)}')"
                    connection.execute(sql)
                    connection.commit()
                    # close connection
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'saveGame', "valid": True}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
                except IntegrityError:
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'saveGame', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))

            else:
                await self.__messageQ.put(message)

    async def __producer_handler(self):
        while True:
            # Non-blocking wait for a message in the message queue and when there is one, dequeue the first message
            message = await self.__messageQ.get()
            if self.__connections:
                # Forward the received message to all connected devices
                await wait([create_task(device.send(message)) for device in self.__connections])

    async def __server(self, websocket, path):
        # Register connection
        self.__connections.add(websocket)
        # Exception Handling
        try:
            # Repeatedly call the consumer handler method then call producer handler method until the first task is complete
            done, pending = await wait([create_task(self.__consumer_handler(websocket)), create_task(self.__producer_handler())], return_when=FIRST_COMPLETED)
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
        finally:
            # Unregister connection
            self.__connections.remove(websocket)

    def run(self):
        loop = get_event_loop()
        # Create and run a server which runs 'self._server' on 'serverIP' IP address, on 'serverPort' port
        server_task = serve(self.__server, serverIP, serverPort)
        loop.run_until_complete(server_task)
        loop.run_forever()


if __name__ == "__main__":
    server = server()
    # Run the server
    server.run()
