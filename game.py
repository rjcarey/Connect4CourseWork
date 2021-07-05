class game:
    
    PONE = "❂"
    PTWO = "⍟"
    
    def __init__(self):
        self._Board = [[" "] * 7] * 6
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

    def play(self,row,col):
        pass

if __name__ == "__main__":
    pass