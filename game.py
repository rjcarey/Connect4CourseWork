import sqlite3
from random import randint


class gameError(Exception):
    pass


class nameError(Exception):
    pass


class game:

    EMPTY = " "
    PONE = "❂"
    PTWO = "⍟"
    
    def __init__(self):
        # store the board
        self.Board = [[game.EMPTY for _ in range(7)] for _ in range(6)]
        # and whose turn it is
        self._Player = game.PONE
        # and the moves that are played in order
        self._Played = []

    def __repr__(self):
        # create a board display to be called when the object is printed
        board = game.EMPTY
        for column in range(1, 8):
            board += f"{column} "
        board += "\n"
        for rowNumber in range(len(self.Board)):
            board += "|"
            row = self.Board[rowNumber]
            for column in row:
                board += f"{column}|"
            board += "\n"
        return board
    
    @property
    def getPlayer(self):
        # return whose turn it is
        return self._Player

    @property
    def getRun(self):
        # check horizontal
        player = game.EMPTY
        counters = []
        for ir, row in enumerate(self.Board):
            run = 0
            for ic, col in enumerate(row):
                if col == player:
                    run += 1
                    counters.append((ir, ic))
                    if run == 4 and player != game.EMPTY:
                        return player, counters
                else:
                    player = col
                    counters = [(ir, ic)]
                    run = 1

        # check vertical
        player = game.EMPTY
        counters = []
        for column in range(7):
            run = 0
            for row in range(6):
                if self.Board[row][column] == player:
                    run += 1
                    counters.append((row, column))
                    if run == 4 and player != game.EMPTY:
                        return player, counters
                else:
                    player = self.Board[row][column]
                    counters = [(row, column)]
                    run = 1

        # check diagonal
        for rowNum, row in enumerate(self.Board):
            for colNum, col in enumerate(row):
                if col != game.EMPTY:
                    # \ diagonal
                    if colNum < 4 and rowNum < 3:
                        counterOne = self.Board[rowNum][colNum]
                        counterTwo = self.Board[rowNum + 1][colNum + 1]
                        counterThree = self.Board[rowNum + 2][colNum + 2]
                        counterFour = self.Board[rowNum + 3][colNum + 3]
                        if counterOne == counterTwo == counterThree == counterFour:
                            return col, [(rowNum, colNum), (rowNum + 1, colNum + 1), (rowNum + 2, colNum + 2), (rowNum + 3, colNum + 3)]

                    # / diagonal
                    if colNum > 2 and rowNum < 3:
                        counterOne = self.Board[rowNum][colNum]
                        counterTwo = self.Board[rowNum + 1][colNum - 1]
                        counterThree = self.Board[rowNum + 2][colNum - 2]
                        counterFour = self.Board[rowNum + 3][colNum - 3]
                        if counterOne == counterTwo == counterThree == counterFour:
                            return col, [(rowNum, colNum), (rowNum + 1, colNum - 1), (rowNum + 2, colNum - 2), (rowNum + 3, colNum - 3)]
        # check draw
        occupiedCount = 0
        for row in self.Board:
            for col in row:
                if col != game.EMPTY:
                    occupiedCount += 1
        if occupiedCount == 42:
            return "Draw", []
        return None, []

    @property
    def getWinner(self):
        # return the winner of the game and the winning run of counters
        winner, run = self.getRun
        return winner

    def play(self, column):
        # change column number into an index
        col = column - 1
        if self.Board[0][col] != game.EMPTY:
            # if the column is full, raise an error
            raise gameError("column full, play again...")
        for i, row in enumerate(reversed(self.Board)):
            # for each slot in the column (from bottom to top) if the slot is empty, place a counter there
            if row[col] == game.EMPTY:
                # set the space to the counter
                row[col] = self._Player
                playedRow = i
                # add the coordinates to the list of played moves
                self._Played.append((5 - playedRow, col))
                break
        # flip the turn
        self._Player = game.PTWO if self._Player == game.PONE else game.PONE
        # return which row was played in
        return playedRow

    def undo(self):
        # if at least one move has been played
        if self._Played:
            # get the coordinates of the last move
            lastRow, lastCol = self._Played.pop()
            # set the slot to be empty
            self.Board[lastRow][lastCol] = game.EMPTY
            # flip the turn
            self._Player = game.PTWO if self._Player == game.PONE else game.PONE
            # return the coordinates of the last move
            return lastRow, lastCol
        else:
            # if there are no moves to undo, raise an error message
            raise gameError("no moves to undo...")

    def save(self, name, opponent, account):
        # connect to database
        connection = sqlite3.connect('connectFour.db')

        # get a string of the moves
        moves = ""
        for move in self._Played:
            moves += str(move[1])

        # add game to database
        sql = f"""INSERT INTO SAVES (NAME,MOVES,OPPONENT,ACCOUNT)
              VALUES ('{name}', '{moves}', '{opponent}', '{account}')"""
        connection.execute(sql)
        connection.commit()

        # close connection
        connection.close()

    def load(self, name, username):
        connection = sqlite3.connect('connectFour.db')
        # get the game info of the game identified by the name
        sql = f"SELECT NAME, MOVES, OPPONENT, ACCOUNT from SAVES WHERE NAME == '{name}' and ACCOUNT == '{username}'"
        gameInfo = connection.execute(sql)
        name, moves, opponent, account = None, None, None, None
        for row in gameInfo:
            name, moves, opponent, account = row
        # if the game return the move string, play the moves
        if moves:
            for move in moves:
                self.play(int(move)+1)
            connection.close()
            # return the opponent type
            return opponent
        else:
            # if not then there was no saved game with this name so raise an error
            connection.close()
            raise nameError("name invalid...")

    def loadPuzzle(self, puzzleCode):
        connection = sqlite3.connect('connectFour.db')
        if puzzleCode == "random":
            # get random puzzle id from the saved puzzles
            sql = f"SELECT * from PUZZLES"
            puzzleInfo = connection.execute(sql)
            results = puzzleInfo.fetchall()
            puzzleCode = results[randint(0, len(results)-1)][0]
        # get the puzzle game info using the puzzle id
        sql = f"SELECT ID, MOVES, SOLUTION from PUZZLES WHERE ID == '{puzzleCode}'"
        puzzleInfo = connection.execute(sql)
        ID, moves, solution = None, None, None
        for row in puzzleInfo:
            ID, moves, solution = row
        # if the game return the move string, play the moves
        if moves:
            for move in moves:
                self.play(int(move)+1)
            connection.close()
            # reset the played moves
            self._Played = []
            # return the solution move and the id of the puzzle
            return solution, ID
        else:
            # if not then there was no saved puzzle with this id so raise an error
            connection.close()
            raise nameError("ID invalid...")

    def savePuzzle(self, ID, solution):
        # connect to database
        connection = sqlite3.connect('connectFour.db')

        # get a string of the moves
        moves = ""
        for move in self._Played:
            moves += str(move[1])

        # add game to database
        sql = f"""INSERT INTO PUZZLES (ID,MOVES,SOLUTION)
                      VALUES ('{ID}', '{moves}', '{solution}')"""
        connection.execute(sql)
        connection.commit()

        # close connection
        connection.close()

    def getSpace(self, row, column):
        # return the counter at coordinates passed in
        return self.Board[row][column]
