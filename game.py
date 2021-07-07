class gameError(Exception):
    pass


class game:
    
    PONE = "❂"
    PTWO = "⍟"
    
    def __init__(self):
        self._Board = [[" " for _ in range(7)] for _ in range(6)]
        self._Player = game.PONE

    def __repr__(self):
        board = " "
        for column in range(1, 8):
            board += f"{column} "
        board += "\n"
        for rowNumber in range(len(self._Board)):
            board += "|"
            row = self._Board[rowNumber]
            for column in row:
                board += f"{column}|"
            board += "\n"
        return board
    
    @property
    def getPlayer(self):
        return self._Player
    
    @property
    def getWinner(self):
        winner = None
        # check horizontal
        player = " "
        for row in self._Board:
            run = 0
            for col in row:
                if col == player:
                    run += 1
                    if run == 4 and player != " ":
                        return player
                else:
                    player = col
                    run = 1
                    
        # check vertical
        player = " "
        for column in range(7):
            run = 0
            for row in range(6):
                if self._Board[row][column] == player:
                    run += 1
                    if run == 4 and player != " ":
                        return player
                else:
                    player = self._Board[row][column]
                    run = 1
        
        # check diagonal
        player = " "
        for rowNum, row in enumerate(self._Board):
            for colNum, col in enumerate(row):
                if col != " ":
                    # \ diagonal
                    if colNum < 4 and rowNum < 3:
                        counterOne = self._Board[rowNum][colNum]
                        counterTwo = self._Board[rowNum + 1][colNum + 1]
                        counterThree = self._Board[rowNum + 2][colNum + 2]
                        counterFour = self._Board[rowNum + 3][colNum + 3]
                        if counterOne == counterTwo == counterThree == counterFour:
                            return col
                        
                    # / diagonal
                    if colNum > 2 and rowNum < 3:
                        counterOne = self._Board[rowNum][colNum]
                        counterTwo = self._Board[rowNum + 1][colNum - 1]
                        counterThree = self._Board[rowNum + 2][colNum - 2]
                        counterFour = self._Board[rowNum + 3][colNum - 3]
                        if counterOne == counterTwo == counterThree == counterFour:
                            return col 
        # check draw
        occupiedCount = 0
        for row in self._Board:
            for col in row:
                if col != " ":
                    occupiedCount += 1
        if occupiedCount == 42:
            return "Draw"
        return winner

    def play(self, column):
        col = column - 1
        if self._Board[0][col] != " ":
            raise gameError
        for i, row in enumerate(reversed(self._Board)):
            if row[col] == " ":
                row[col] = self._Player
                playedRow = i
                break
        self._Player = game.PTWO if self._Player == game.PONE else game.PONE
        return playedRow


if __name__ == "__main__":
    pass
