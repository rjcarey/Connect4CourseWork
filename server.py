from asyncio import Queue, create_task, wait, FIRST_COMPLETED, get_event_loop
from websockets import serve
from json import dumps
from configs import serverIP, serverPort
import sqlite3
from sqlite3 import IntegrityError, OperationalError
from hashlib import pbkdf2_hmac
from os import urandom
from random import randint


# GROUP A SKILL: Complex Client-Server Model
class server:
    def __init__(self):
        # Set of connected devices
        self.__connections = set()
        # Set of hosts
        self.__gHosts = set()
        self.__tHosts = set()
        # GROUP A SKILL: Queue of messages to handle
        self.__messageQ = Queue()

    async def __consumer_handler(self, websocket):
        async for message in websocket:
            # Wait for a message and put it in the queue when received
            # Handle some types of messages differently
            print(message)
            dictionary = eval(message)
            if dictionary.get('cmd', None) == 'tHost':
                self.__tHosts.add(dictionary.get('from', None))
                await self.__messageQ.put(message)
            elif dictionary.get('cmd', None) == 'hostList':
                msg = {'to': dictionary.get('from', None), 'cmd': 'hostList', 'hostList': [host for host in self.__tHosts]}
                print(msg)
                await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'tJoin':
                if dictionary.get('to', None) in self.__tHosts:
                    await self.__messageQ.put(message)
                else:
                    # If the join code is not valid, return a HostNotFound message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'hnf'}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'acc':
                self.__tHosts.remove(dictionary.get('from', None))
                await self.__messageQ.put(message)
            elif dictionary.get('cmd', None) == 'gHost':
                self.__gHosts.add(dictionary.get('from', None))
            elif dictionary.get('cmd', None) == 'cHost':
                self.__gHosts.remove(dictionary.get('from', None))
            elif dictionary.get('cmd', None) == 'gJoin':
                if dictionary.get('joinCode', None) in self.__gHosts:
                    self.__gHosts.remove(dictionary.get('joinCode', None))
                    await self.__messageQ.put(message)
                else:
                    # If the join code is not valid, return a HostNotFound message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'hnf'}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'logIn':
                # Verify account details
                connection = sqlite3.connect('connectFour.db')
                sql = f"SELECT * FROM ACCOUNTS WHERE USERNAME == '{dictionary.get('from', None)}'"
                accountInfo = connection.execute(sql)
                accountInfoRow = None
                for row in accountInfo:
                    accountInfoRow = row
                connection.close()
                msg = {'to': dictionary.get('from', None), 'cmd': 'logIn', "accountInfo": accountInfoRow}
                print(msg)
                await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'addAccount':
                # Get random salt and convert it to an integer, then get hashed password
                salt = urandom(4)
                key = int.from_bytes(salt, byteorder="big")
                hashedPassword = pbkdf2_hmac('sha256', dictionary.get('pword', None).encode('utf-8'), salt, 100000)
                # Try to add the account to the database
                connection = sqlite3.connect('connectFour.db')
                try:
                    sql = f"INSERT INTO ACCOUNTS (USERNAME,KEY,HPWORD,SPLAYED,SWON,SLOST,SDRAWN,SPFIN,SPMADE) VALUES ('{dictionary.get('from', None)}', '{key}', '{hashedPassword}', 0, 0, 0, 0, 0, 0)"
                    connection.execute(sql)
                    connection.commit()
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'addAccount', "valid": True}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
                except IntegrityError:
                    # If the username is not unique, return an 'invalid' message
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'addAccount', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'updatePFin':
                # Update the puzzles finished stat for an account
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
                    # If the stat fails to update, return an 'invalid' message
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'updatePMade':
                # Update the puzzles made stat for an account
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
                    # If the stat fails to update, return an 'invalid' message
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
            elif dictionary.get("cmd", None) == 'updateGameStats':
                # Update the normal game stats for an account
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
                    # If the stats fail to update, return an 'invalid' message
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'loadPuzzle':
                puzzleCode = dictionary.get('puzzleID', None)
                # Retrieve the puzzle game info and send it back to the payer
                connection = sqlite3.connect('connectFour.db')
                if puzzleCode == "random":
                    # Get random puzzle id from the saved puzzles if the player chose random
                    sql = f"SELECT * FROM PUZZLES"
                    puzzleInfo = connection.execute(sql)
                    results = puzzleInfo.fetchall()
                    puzzleCode = results[randint(0, len(results) - 1)][0]
                sql = f"SELECT ID, MOVES, SOLUTION FROM PUZZLES WHERE ID == '{puzzleCode}'"
                puzzleInfo = connection.execute(sql)
                puzzleInfoRow = None
                for row in puzzleInfo:
                    puzzleInfoRow = row
                connection.close()
                msg = {'to': dictionary.get('from', None), 'cmd': 'loadPuzzle', "puzzleInfo": puzzleInfoRow}
                print(msg)
                await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'savePuzzle':
                # Try to add the game info to the database
                connection = sqlite3.connect('connectFour.db')
                try:
                    sql = f"INSERT INTO PUZZLES (ID,MOVES,SOLUTION) VALUES ('{dictionary.get('puzzleID', None)}', '{dictionary.get('puzzleMoves', None)}', '{dictionary.get('puzzleSolution', None)}')"
                    connection.execute(sql)
                    connection.commit()
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'savePuzzle', "valid": True}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
                except IntegrityError:
                    # If the puzzle ID is not unique, return an 'invalid' message
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'savePuzzle', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'loadGame':
                # Retrieve the game info of the requested game
                connection = sqlite3.connect('connectFour.db')
                sql = f"SELECT NAME, MOVES, OPPONENT, ACCOUNT FROM SAVES WHERE NAME == '{dictionary.get('gameName', None)}' AND ACCOUNT == '{dictionary.get('from', None)}'"
                gameInfo = connection.execute(sql)
                gameInfoRow = None
                for row in gameInfo:
                    gameInfoRow = row
                connection.close()
                msg = {'to': dictionary.get('from', None), 'cmd': 'loadPuzzle', "gameInfo": gameInfoRow}
                print(msg)
                await self.__messageQ.put(dumps(msg))
            elif dictionary.get('cmd', None) == 'saveGame':
                # Try to add the game info to the database
                connection = sqlite3.connect('connectFour.db')
                try:
                    sql = f"INSERT INTO SAVES (NAME,MOVES,OPPONENT,ACCOUNT) VALUES ('{dictionary.get('gameName', None)}', '{dictionary.get('gameMoves', None)}', '{dictionary.get('opponent', None)}', '{dictionary.get('from', None)}')"
                    connection.execute(sql)
                    connection.commit()
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'saveGame', "valid": True}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
                except IntegrityError:
                    # If the game name is not unique, return an 'invalid' message
                    connection.close()
                    msg = {'to': dictionary.get('from', None), 'cmd': 'saveGame', "valid": False}
                    print(msg)
                    await self.__messageQ.put(dumps(msg))
            else:
                # A message of any other command should just be forwarded
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
