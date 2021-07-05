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

    def play(self, column):
        col = column - 1
        for row in reversed(self._Board):
            if row[col] == " ":
                row[col] = self._Player
                break
        self._Player = game.PTWO if self._Player == game.PONE else game.PONE            

if __name__ == "__main__":
    pass