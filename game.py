class gameError(Exception):
    pass


class StackEmptyError(Exception):
    pass


########################
# GROUP A SKILL: Stack #
########################
class MoveStack:
    def __init__(self):
        self.__stack = []
        self.__topOfStack = -1

    def pop(self):
        self.__topOfStack -= 1
        return self.__stack.pop()

    def push(self, item):
        self.__topOfStack += 1
        self.__stack.append(item)

    def peek(self):
        if self.__topOfStack > -1:
            return self.__stack[self.__topOfStack]
        else:
            raise StackEmptyError

    def getMoves(self):
        moves = ""
        for move in self.__stack:
            moves += str(move[1])
        return moves


class game:

    ############################################################
    # GOOD CODING STYLE                                        #
    #   ====================================================   #
    # Use of class constants to store commonly repeated values #
    ############################################################
    # Class constants for counters
    EMPTY = " "
    PONE = "❂"
    PTWO = "⍟"
    
    def __init__(self):
        ######################################
        # GROUP B SKILL: 2-Dimensional Array #
        ######################################
        # Store the board, a 7x6 2D array, with each element starting as an 'EMPTY' space
        self.Board = [[game.EMPTY for _ in range(7)] for _ in range(6)]
        self.__Player = game.PONE
        ########################
        # GROUP A SKILL: Stack #
        ########################
        self.__Played = MoveStack()

    def __repr__(self):
        # Create a board display to be called when the object is printed
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
        # Return whose turn it is
        return self.__Player

    @property
    def getRun(self):
        #####################################################################################################################################################################
        # GROUP A SKILL: Complex user-defined algorithm to find a run of four counters, if found return the player's counter and the coordinates of the counters in the run #
        #####################################################################################################################################################################

        # Check for a horizontal run
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

        # Check for a vertical run
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

        # Check for a diagonal run
        for rowNum, row in enumerate(self.Board):
            for colNum, col in enumerate(row):
                if col != game.EMPTY:
                    # Check \ diagonal
                    if colNum < 4 and rowNum < 3:
                        if self.Board[rowNum][colNum] == self.Board[rowNum + 1][colNum + 1] == self.Board[rowNum + 2][colNum + 2] == self.Board[rowNum + 3][colNum + 3]:
                            return col, [(rowNum, colNum), (rowNum + 1, colNum + 1), (rowNum + 2, colNum + 2), (rowNum + 3, colNum + 3)]
                    # Check / diagonal
                    if colNum > 2 and rowNum < 3:
                        if self.Board[rowNum][colNum] == self.Board[rowNum + 1][colNum - 1] == self.Board[rowNum + 2][colNum - 2] == self.Board[rowNum + 3][colNum - 3]:
                            return col, [(rowNum, colNum), (rowNum + 1, colNum - 1), (rowNum + 2, colNum - 2), (rowNum + 3, colNum - 3)]

        # Check for a draw
        for col in self.Board[0]:
            if col == game.EMPTY:
                return None, []
        return "Draw", []

    @property
    def getWinner(self):
        winner, run = self.getRun
        return winner

    def play(self, column):
        col = column - 1
        if self.Board[0][col] != game.EMPTY:
            # If the column is full, raise an error (Exception Handling)
            raise gameError("column full, play again...")
        playedRow = None
        for i, row in enumerate(reversed(self.Board)):
            # Place the counter in the correct space
            if row[col] == game.EMPTY:
                row[col] = self.__Player
                playedRow = i
                self.__Played.push((5 - playedRow, col))
                break
        self.__Player = game.PTWO if self.__Player == game.PONE else game.PONE
        return playedRow

    def undo(self):
        if self.__Played:
            lastRow, lastCol = self.__Played.pop()
            self.Board[lastRow][lastCol] = game.EMPTY
            self.__Player = game.PTWO if self.__Player == game.PONE else game.PONE
            return lastRow, lastCol
        else:
            # If are no moves to undo raise an error (Exception Handling)
            raise gameError("no moves to undo...")

    def load(self, moves):
        # Play all the stored moves in order
        for move in moves:
            self.play(int(move)+1)

    def loadPuzzle(self, moves):
        self.load(moves)
        # Reset the played moves so that the puzzle can't be undone past how it was loaded
        self.__Played = []

    @property
    def getMoves(self):
        # Return a string of the moves in the order they were played
        return self.__Played.getMoves()

    def getSpace(self, row, column):
        return self.Board[row][column]

    def loadAI(self, board, counter):
        self.Board = board
        self.__Player = counter
