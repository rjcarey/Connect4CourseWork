import sqlite3


class gameError(Exception):
    pass


class game:

    EMPTY = " "
    PONE = "❂"
    PTWO = "⍟"
    
    def __init__(self):
        self.Board = [[game.EMPTY for _ in range(7)] for _ in range(6)]
        self._Player = game.PONE
        self._Played = []

    def __repr__(self):
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
        winner, run = self.getRun
        return winner

    def play(self, column):
        col = column - 1
        if self.Board[0][col] != game.EMPTY:
            raise gameError("column full, play again...")
        for i, row in enumerate(reversed(self.Board)):
            if row[col] == game.EMPTY:
                row[col] = self._Player
                playedRow = i
                self._Played.append((5 - playedRow, col))
                break
        self._Player = game.PTWO if self._Player == game.PONE else game.PONE
        return playedRow

    def undo(self):
        if self._Played:
            lastRow, lastCol = self._Played.pop()
            self.Board[lastRow][lastCol] = game.EMPTY
            self._Player = game.PTWO if self._Player == game.PONE else game.PONE
            return lastRow, lastCol
        else:
            raise gameError("no moves to undo...")

    def save(self, name):
        # connect to database
        connection = sqlite3.connect('savedGames.db')

        # get a string of the moves
        moves = ""
        for move in self._Played:
            moves += str(move[1])

        # add game to database
        sql = f"""INSERT INTO SAVES (NAME,MOVES,TURN)
              VALUES ('{name.get()}', '{moves}', '{self._Player}')"""
        connection.execute(sql)
        connection.commit()

        # close connection
        connection.close()
