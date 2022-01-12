from asyncio import Queue, create_task, wait, FIRST_COMPLETED, get_event_loop
from websockets import serve
from json import dumps, loads
from configs import serverIP, serverPort
import sqlite3
from sqlite3 import IntegrityError, OperationalError
from hashlib import pbkdf2_hmac
from os import urandom


###############################
# GROUP A SKILL:              #
#   =======================   #
# Complex Client-Server Model #
###############################
class server:

    ############################################################
    # GOOD CODING STYLE:                                       #
    #   ====================================================   #
    # Use of class constants to store commonly repeated values #
    ############################################################
    DATABASE = 'connectFour.db'

    def __init__(self):
        # Set of connected devices
        self.__connections = set()
        # Set of hosts
        self.__gHosts = set()
        self.__tHosts = set()
        ###############################
        # GROUP A SKILL:              #
        #   =======================   #
        # Queue of messages to handle #
        ###############################
        self.__messageQ = Queue()

    async def __consumer_handler(self, websocket):
        async for message in websocket:
            # Wait for a message and put it in the queue when received
            # Handle some types of messages differently
            ###################################################################################
            # GROUP A SKILL:                                                                  #
            #   ===========================================================================   #
            # Using JSON loads and dumps to convert python data structure to and from strings #
            ###################################################################################
            dictionary = loads(message)
            print(dictionary)
            if dictionary == 'stop':
                pass
            elif dictionary.get('cmd', None) == 'tHost':
                # If the message has the terminal host command, add the sender to the terminal host set
                self.__tHosts.add(dictionary.get('from', None))
                await self.__messageQ.put(message)

            elif dictionary.get('cmd', None) == 'hostList':
                # If the message has the host list command, send back a list of hosts in the terminal host set
                msg = {'to': dictionary.get('from', None), 'cmd': 'hostList', 'hostList': [host for host in self.__tHosts]}
                print(msg)
                ###################################################################################
                # GROUP A SKILL:                                                                  #
                #   ===========================================================================   #
                # Using JSON loads and dumps to convert python data structure to and from strings #
                ###################################################################################
                await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'tJoin':
                # If the message has the terminal join command, check if the hosts name is in the terminal host set and if it is, forward the join request to the host
                if dictionary.get('to', None) in self.__tHosts:
                    await self.__messageQ.put(message)
                else:
                    # If the join code is not valid, return a HostNotFound message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'hnf'}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'acc':
                # If the message has the accept command, remove the sender from the terminal host set and forward the accept message
                self.__tHosts.remove(dictionary.get('from', None))
                await self.__messageQ.put(message)

            elif dictionary.get('cmd', None) == 'gHost':
                # If the message has the gui host command, add the sender to the gui host set
                self.__gHosts.add(dictionary.get('from', None))

            elif dictionary.get('cmd', None) == 'cHost':
                # If the message has the cancel host command, remove the sender from the gui host set
                self.__gHosts.remove(dictionary.get('from', None))

            elif dictionary.get('cmd', None) == 'gJoin':
                # If the message has the gui join command, remove the recipient from the gui host set and forward the message
                if dictionary.get('joinCode', None) in self.__gHosts:
                    self.__gHosts.remove(dictionary.get('joinCode', None))
                    await self.__messageQ.put(message)
                else:
                    # If the join code is not valid, return a HostNotFound message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'hnf'}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'logIn':
                # Retrieve stored account details
                sql = f"SELECT * FROM ACCOUNTS WHERE USERNAME == '{dictionary.get('from', None)}'"
                accountInfo = self.__executeSQL(sql, True)
                # Send back a message with the account details
                #######################################################################
                # EXCELLENT CODING STYLE:                                             #
                #   ================================================================= #
                # Exception Handling: Try to send the first item of the returned list #
                #######################################################################
                try:
                    msg = {'to': dictionary.get('from', None), 'cmd': 'logIn', "accountInfo": accountInfo[0]}
                except IndexError:
                    # If there are no records returned from the sql execution, send 'None' as accountInfo
                    msg = {'to': dictionary.get('from', None), 'cmd': 'logIn', "accountInfo": None}
                print(msg)
                ###################################################################################
                # GROUP A SKILL:                                                                  #
                #   ===========================================================================   #
                # Using JSON loads and dumps to convert python data structure to and from strings #
                ###################################################################################
                await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'addAccount':
                # Get random salt and convert it to an integer, then get the hashed password
                salt = urandom(4)
                key = int.from_bytes(salt, byteorder="big")
                hashedPassword = pbkdf2_hmac('sha256', dictionary.get('pword', None).encode('utf-8'), salt, 100000)
                # Try to add the account to the database
                ###########################################################
                # EXCELLENT CODING STYLE:                                 #
                #   ===================================================   #
                # Exception Handling: Try to add the account to the table #
                ###########################################################
                try:
                    sql = f"INSERT INTO ACCOUNTS (USERNAME,KEY,HPWORD,SPLAYED,SWON,SLOST,SDRAWN,SPFIN,SPMADE) VALUES ('{dictionary.get('from', None)}', '{key}', '{hashedPassword}', 0, 0, 0, 0, 0, 0)"
                    self.__executeSQL(sql, False)
                    # Send back a message to let the client know if the insert was successful
                    msg = {'to': dictionary.get('from', None), 'cmd': 'addAccount', "valid": True}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))
                except IntegrityError:
                    # If the username is not unique, return an 'invalid' message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'addAccount', "valid": False}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'updatePFin':
                # Update the puzzles finished stat for an account
                ####################################################
                # EXCELLENT CODING STYLE:                          #
                #   ============================================== #
                # Exception Handling: Try to update the statistics #
                ####################################################
                try:
                    sql = f"UPDATE ACCOUNTS SET SPFIN = {dictionary.get('pFin', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    self.__executeSQL(sql, False)
                    # Send back a message to let the client know if the update was successful
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": True}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))
                except OperationalError:
                    # If the stat fails to update, return an 'invalid' message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": False}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'updatePMade':
                # Update the puzzles made stat for an account
                ####################################################
                # EXCELLENT CODING STYLE:                          #
                #   ============================================   #
                # Exception Handling: Try to update the statistics #
                ####################################################
                try:
                    sql = f"UPDATE ACCOUNTS SET SPMADE = {dictionary.get('pMade', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    self.__executeSQL(sql, False)
                    # Send back a message to let the client know if the update was successful
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": True}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))
                except OperationalError:
                    # If the stat fails to update, return an 'invalid' message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": False}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get("cmd", None) == 'updateGameStats':
                # Update the normal game stats for an account
                ####################################################
                # EXCELLENT CODING STYLE:                          #
                #   ============================================== #
                # Exception Handling: Try to update the statistics #
                ####################################################
                try:
                    sql = f"UPDATE ACCOUNTS SET SPLAYED = {dictionary.get('played', None)}, SWON = {dictionary.get('won', None)}, SLOST = {dictionary.get('lost', None)}, SDRAWN = {dictionary.get('drawn', None)} WHERE USERNAME = '{dictionary.get('from', None)}';"
                    self.__executeSQL(sql, False)
                    # Send back a message to let the client know if the update was successful
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": True}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))
                except OperationalError:
                    # If the stats fail to update, return an 'invalid' message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'updateStats', "valid": False}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'loadPuzzle':
                puzzleCode = dictionary.get('puzzleID', None)
                # Retrieve the puzzle game info and send it back to the payer
                if puzzleCode == "random":
                    # Get random puzzle info from the saved puzzles if the player chose random
                    #########################
                    # GROUP B SKILL:        #
                    #   =================   #
                    # Non-Parameterised SQL #
                    #########################
                    sql = f"SELECT * FROM PUZZLES ORDER BY RANDOM() LIMIT 1"
                else:
                    sql = f"SELECT * FROM PUZZLES WHERE ID == '{puzzleCode}'"
                puzzleInfo = self.__executeSQL(sql, True)
                # Send back the retrieved puzzle information
                #######################################################################
                # EXCELLENT CODING STYLE:                                             #
                #   ================================================================= #
                # Exception Handling: Try to send the first item of the returned list #
                #######################################################################
                try:
                    msg = {'to': dictionary.get('from', None), 'cmd': 'loadPuzzle', "puzzleInfo": puzzleInfo[0]}
                except IndexError:
                    # If there are no records returned from the sql execution, send 'None' as puzzle
                    msg = {'to': dictionary.get('from', None), 'cmd': 'loadPuzzle', "puzzleInfo": None}
                print(msg)
                ###################################################################################
                # GROUP A SKILL:                                                                  #
                #   ===========================================================================   #
                # Using JSON loads and dumps to convert python data structure to and from strings #
                ###################################################################################
                await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'savePuzzle':
                # Try to add the game info to the database
                #################################################################
                # EXCELLENT CODING STYLE:                                       #
                #   =========================================================   #
                # Exception Handling: Try to ad the puzzle to the puzzles table #
                #################################################################
                try:
                    sql = f"INSERT INTO PUZZLES (ID,MOVES,SOLUTION) VALUES ('{dictionary.get('puzzleID', None)}', '{dictionary.get('puzzleMoves', None)}', '{dictionary.get('puzzleSolution', None)}')"
                    self.__executeSQL(sql, False)
                    # Send back a message to let the client know if the insert was successful
                    msg = {'to': dictionary.get('from', None), 'cmd': 'savePuzzle', "valid": True}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))
                except IntegrityError:
                    # If the puzzle ID is not unique, return an 'invalid' message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'savePuzzle', "valid": False}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'loadGame':
                # Retrieve the game info stored with the game name and account name given in the load message
                sql = f"SELECT NAME, MOVES, OPPONENT, ACCOUNT FROM SAVES WHERE NAME == '{dictionary.get('gameName', None)}' AND ACCOUNT == '{dictionary.get('from', None)}'"
                gameInfo = self.__executeSQL(sql, True)
                #######################################################################
                # EXCELLENT CODING STYLE:                                             #
                #   ================================================================= #
                # Exception Handling: Try to send the first item of the returned list #
                #######################################################################
                try:
                    msg = {'to': dictionary.get('from', None), 'cmd': 'loadPuzzle', "gameInfo": gameInfo[0]}
                except IndexError:
                    # If there are no records returned from the sql execution, send 'None' as puzzle
                    msg = {'to': dictionary.get('from', None), 'cmd': 'loadPuzzle', "gameInfo": None}
                print(msg)
                ###################################################################################
                # GROUP A SKILL:                                                                  #
                #   ===========================================================================   #
                # Using JSON loads and dumps to convert python data structure to and from strings #
                ###################################################################################
                await self.__messageQ.put(dumps(msg))

            elif dictionary.get('cmd', None) == 'saveGame':
                # Try to add the game info to the database
                ###################################################################
                # EXCELLENT CODING STYLE:                                         #
                #   ===========================================================   #
                # Exception Handling: Try to add the game info to the saves table #
                ###################################################################
                try:
                    sql = f"INSERT INTO SAVES (NAME,MOVES,OPPONENT,ACCOUNT) VALUES ('{dictionary.get('gameName', None)}', '{dictionary.get('gameMoves', None)}', '{dictionary.get('opponent', None)}', '{dictionary.get('from', None)}')"
                    self.__executeSQL(sql, False)
                    # Send back a message to let the client know if the insert was successful
                    msg = {'to': dictionary.get('from', None), 'cmd': 'saveGame', "valid": True}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
                    await self.__messageQ.put(dumps(msg))
                except IntegrityError:
                    # If the game name is not unique, return an 'invalid' message
                    msg = {'to': dictionary.get('from', None), 'cmd': 'saveGame', "valid": False}
                    print(msg)
                    ###################################################################################
                    # GROUP A SKILL:                                                                  #
                    #   ===========================================================================   #
                    # Using JSON loads and dumps to convert python data structure to and from strings #
                    ###################################################################################
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

    @staticmethod
    def __createDatabase():
        # Create the tables used by the program if they do not already exist
        #########################
        # GROUP B SKILL:        #
        #   =================   #
        # Non-Parameterised SQL #
        #########################
        print("creating tables...")
        connection = sqlite3.connect(server.DATABASE)
        sql = '''CREATE TABLE IF NOT EXISTS "ACCOUNTS" (
            "USERNAME"	TEXT NOT NULL UNIQUE,
            "KEY"	INTEGER NOT NULL,
            "HPWORD"	TEXT NOT NULL,
            "SPLAYED"	INTEGER NOT NULL,
            "SWON"	INTEGER NOT NULL,
            "SLOST"	INTEGER NOT NULL,
            "SDRAWN"	INTEGER NOT NULL,
            "SPFIN"	INTEGER NOT NULL,
            "SPMADE"	INTEGER NOT NULL,
            PRIMARY KEY("USERNAME")
        );'''
        connection.execute(sql)
        connection.commit()
        sql = '''CREATE TABLE IF NOT EXISTS "PUZZLES" (
            "ID"	INTEGER NOT NULL UNIQUE,
            "MOVES"	TEXT NOT NULL,
            "SOLUTION"	INTEGER NOT NULL,
            PRIMARY KEY("ID")
        );'''
        connection.execute(sql)
        connection.commit()
        sql = '''CREATE TABLE IF NOT EXISTS "SAVES" (
            "NAME"	TEXT NOT NULL UNIQUE,
            "MOVES"	TEXT NOT NULL,
            "OPPONENT"	TEXT NOT NULL,
            "ACCOUNT"	TEXT NOT NULL,
            PRIMARY KEY("NAME")
        );'''
        connection.execute(sql)
        connection.commit()
        connection.close()

    def __executeSQL(self, sql, returnFlag):
        # Try to execute the passed in sql statement
        ######################################################
        # EXCELLENT CODING STYLE:                            #
        #   ==============================================   #
        # Exception Handling: Try to connect to the database #
        ######################################################
        try:
            connection = sqlite3.connect(server.DATABASE)
            result = connection.execute(sql)
        except OperationalError:
            # If the database file doesn't exist, create one and connect to it
            self.__createDatabase()
            connection = sqlite3.connect(server.DATABASE)
            result = connection.execute(sql)
        connection.commit()
        # Convert the return of the sql statement into a list and, if returning something, return the list
        rows = []
        for row in result:
            rows.append(row)
        connection.close()
        if returnFlag:
            return rows

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
