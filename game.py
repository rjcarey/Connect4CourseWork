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
        self.__Player = game.PONE
        # and the moves that are played in order
        self.__Played = []

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
        return self.__Player

    @property
    def getRun(self):
        # check horizontal
        player = game.EMPTY
        for ir, row in enumerate(self.Board):
            run = 0
            counters = []
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
        playedRow = 0
        for i, row in enumerate(reversed(self.Board)):
            # for each slot in the column (from bottom to top) if the slot is empty, place a counter there
            if row[col] == game.EMPTY:
                # set the space to the counter
                row[col] = self.__Player
                playedRow = i
                # add the coordinates to the list of played moves
                self.__Played.append((5 - playedRow, col))
                break
        # flip the turn
        self.__Player = game.PTWO if self.__Player == game.PONE else game.PONE
        # return which row was played in
        return playedRow

    def undo(self):
        # if at least one move has been played
        if self.__Played:
            # get the coordinates of the last move
            lastRow, lastCol = self.__Played.pop()
            # set the slot to be empty
            self.Board[lastRow][lastCol] = game.EMPTY
            # flip the turn
            self.__Player = game.PTWO if self.__Player == game.PONE else game.PONE
            # return the coordinates of the last move
            return lastRow, lastCol
        else:
            # if there are no moves to undo, raise an error message
            raise gameError("no moves to undo...")

    def load(self, moves):
        for move in moves:
            self.play(int(move)+1)

    def loadPuzzle(self, moves):
        self.load(moves)
        # reset the played moves so that the puzzle can't be undone past the save
        self.__Played = []

    @property
    def getMoves(self):
        # get a string of the moves
        moves = ""
        for move in self.__Played:
            moves += str(move[1])
        return moves

    def getSpace(self, row, column):
        # return the counter at coordinates passed in
        return self.Board[row][column]

    def loadAI(self, board, counter):
        self.Board = board
        self.__Player = counter
