class gameError(Exception):
    pass

class game:

    EMPTY = " "
    PONE = "❂"
    PTWO = "⍟"
    
    def __init__(self):
        self.Board = [[" " for _ in range(7)] for _ in range(6)]
        self._Player = game.PONE
        self._Played = []

    def __repr__(self):
        board = " "
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
        player = " "
        counters = []
        for ir, row in enumerate(self.Board):
            run = 0
            for ic, col in enumerate(row):
                if col == player:
                    run += 1
                    counters.append((ir, ic))
                    if run == 4 and player != " ":
                        return player, counters
                else:
                    player = col
                    counters = [(ir, ic)]
                    run = 1

        # check vertical
        player = " "
        counters = []
        for column in range(7):
            run = 0
            for row in range(6):
                if self.Board[row][column] == player:
                    run += 1
                    counters.append((row, column))
                    if run == 4 and player != " ":
                        return player, counters
                else:
                    player = self.Board[row][column]
                    counters = [(row, column)]
                    run = 1

        # check diagonal
        for rowNum, row in enumerate(self.Board):
            for colNum, col in enumerate(row):
                if col != " ":
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
                if col != " ":
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
        if self.Board[0][col] != " ":
            raise gameError("column full, play again...")
        for i, row in enumerate(reversed(self.Board)):
            if row[col] == " ":
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

if __name__ == "__main__":
    pass
