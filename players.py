from random import randint
from game import game, gameError
from copy import deepcopy

class Ai:
    def __init__(self, difficulty):
        self.__difficulty = difficulty

    def getColumn(self, board, counter):
        self.__aiCounter = counter
        self.__playerCounter = "❂" if counter != "❂" else "⍟"
        if self.__difficulty == "Practice AI":
            move = self.practiceAI(board)
        elif self.__difficulty == "Easy AI":
            move = self.easyAI(board, counter)
        elif self.__difficulty == "Medium AI":
            move = self.mediumAI(board)
        elif self.__difficulty == "Hard AI":
            move = self.hardAI(board)

        # return the ai's move
        return move

    def practiceAI(self, board):
        col = -1
        while col == -1:
            # play random column
            move = randint(0, 6)
            if board[0][move] == " ":
                col = move
        return col

    def easyAI(self, board, counter):
        scores = [0, 0, 0, 0, 0, 0, 0]
        for column in range(7):
            # print(f"column {column + 1}:")
            # check for full row
            if board[0][column] != " ":
                # print(f"{column} full")
                scores[column] = -1
                break

            # find the row that would be played in
            # print(board)
            for i, row in enumerate(board):
                # print(f"{i}, {row}")
                if row[column] != " ":
                    playedRow = i - 1
                    break
                elif i == 5:
                    playedRow = 5

            # print(f"played row: {playedRow}")

            # check what counters this play would connect with and calculate resulting score
            leftOne = True if column > 0 else False
            leftTwo = True if column > 1 else False
            leftThree = True if column > 2 else False
            downOne = True if playedRow < 5 else False
            downTwo = True if playedRow < 4 else False
            downThree = True if playedRow < 3 else False
            rightOne = True if column < 6 else False
            rightTwo = True if column < 5 else False
            rightThree = True if column < 4 else False
            upOne = True if playedRow > 0 else False
            upTwo = True if playedRow > 1 else False
            upThree = True if playedRow > 2 else False
            # print(f"{column}, {playedRow}: {leftOne}, {leftTwo}, {leftThree}, {downOne}, {downTwo}, {downThree}, {rightOne}, {rightTwo}, {rightThree}, {upOne}, {upTwo}, {upThree}")

            score = 0
            currentScore = 0
            if upOne and leftOne:
                if board[playedRow - 1][column - 1] == counter:
                    # print("upOne and leftOne")
                    currentScore += 1
                    if upTwo and leftTwo:
                        if board[playedRow - 2][column - 2] == counter:
                            # print("upTwo and leftTwo")
                            currentScore *= 2
                            if upThree and leftThree:
                                if board[playedRow - 3][column - 3] == counter:
                                    # print("upThree and leftThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if leftOne:
                if board[playedRow][column - 1] == counter:
                    # print("leftOne")
                    currentScore += 1
                    if leftTwo:
                        if board[playedRow][column - 2] == counter:
                            # print("leftTwo")
                            currentScore *= 2
                            if leftThree:
                                if board[playedRow][column - 3] == counter:
                                    # print("leftThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if downOne and leftOne:
                if board[playedRow + 1][column - 1] == counter:
                    # print("downOne and leftOne")
                    currentScore += 1
                    if downTwo and leftTwo:
                        if board[playedRow + 2][column - 2] == counter:
                            # print("downTwo and leftTwo")
                            currentScore *= 2
                            if downThree and leftThree:
                                if board[playedRow + 3][column - 3] == counter:
                                    # print("downThree and leftThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if downOne:
                if board[playedRow + 1][column] == counter:
                    # print("downOne")
                    currentScore += 1
                    if downTwo:
                        if board[playedRow + 2][column] == counter:
                            # print("downTwo")
                            currentScore *= 2
                            if downThree:
                                if board[playedRow + 3][column] == counter:
                                    # print("downThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if downOne and rightOne:
                if board[playedRow + 1][column + 1] == counter:
                    # print("downOne and rightOne")
                    currentScore += 1
                    if downTwo and rightTwo:
                        if board[playedRow + 2][column + 2] == counter:
                            # print("downTwo and rightTwo")
                            currentScore *= 2
                            if downThree and rightThree:
                                if board[playedRow + 3][column + 3] == counter:
                                    # print("downThree and rightThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if rightOne:
                if board[playedRow][column + 1] == counter:
                    # print("rightOne")
                    currentScore += 1
                    if rightTwo:
                        if board[playedRow][column + 2] == counter:
                            # print("rightTwo")
                            currentScore *= 2
                            if rightThree:
                                if board[playedRow][column + 3] == counter:
                                    # print(rightThree)
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if upOne and rightOne:
                if board[playedRow - 1][column + 1] == counter:
                    # print("upOne and rightOne")
                    currentScore += 1
                    if upTwo and rightTwo:
                        if board[playedRow - 2][column + 2] == counter:
                            # print("upTwo and rightTwo")
                            currentScore *= 2
                            if upThree and rightThree:
                                if board[playedRow - 3][column + 3] == counter:
                                    # print("upThree and rightThree")
                                    currentScore *= 9999

            score += currentScore
            scores[column] = score

        # find the best scoring move
        # print(scores)
        maxScore = -1
        maxIndex = []
        for i, score in enumerate(scores):
            if maxScore < score:
                maxScore = score
                maxIndex = [i]
            elif maxScore == score:
                maxIndex.append(i)
        index = 0 if len(maxIndex) == 1 else randint(0, len(maxIndex) - 1)
        return maxIndex[index]

    def mediumAI(self, board):
        boards = self.nextBoards(board, self.__aiCounter)
        boardList = []
        for key in boards.keys():
            boardList.append((key, boards[key]))
        moves = []
        value = -9999999
        for newBoard in boards.values():
            newVal = self.myMiniMax(3, newBoard, False)
            for item in boardList:
                if item[1] == newBoard:
                    move = item[0]
            if newVal > value:
                value = newVal
                moves = [move]
            elif newVal == value:
                value += newVal
                moves.append(move)
        if len(moves) > 1:
            return moves[randint(0, len(moves) - 1)]
        else:
            return moves[0]

    def hardAI(self, board):
        # medium depth minimax and trapping
        return move

    def myMiniMax(self, depth, board, aiTurn):
        end = self.checkTerminal(board)
        if depth == 0 or end is not None:
            if end == self.__aiCounter:
                return 9999999 if depth == 1 else 1
            elif end == self.__playerCounter:
                return -9999999 if depth == 1 else -1
            else:
                return 0
        if aiTurn:
            value = -9999999
            newBoards = self.nextBoards(board, self.__aiCounter)
            for newBoard in newBoards.values():
                newVal = self.myMiniMax(depth-1, newBoard, False)
                if newVal > value:
                    value = newVal
                elif newVal == value:
                    value += newVal
            return value
        else:
            value = 9999999
            newBoards = self.nextBoards(board, self.__playerCounter)
            for newBoard in newBoards.values():
                newVal = self.myMiniMax(depth - 1, newBoard, True)
                if newVal < value:
                    value = newVal
                elif newVal == value:
                    value += newVal
            return value

    def nextBoards(self, board, counter):
        boards = {}
        for iC, column in enumerate(board[0]):
            if column == " ":
                newBoard = game()
                newBoard.loadAI(deepcopy(board), counter)
                boards[iC] = newBoard.Board
        return boards

    def checkTerminal(self, board):
        # check horizontal
        player = " "
        counters = []
        for ir, row in enumerate(board):
            run = 0
            for ic, col in enumerate(row):
                if col == player:
                    run += 1
                    counters.append((ir, ic))
                    if run == 4 and player != " ":
                        return player # , counters
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
                if board[row][column] == player:
                    run += 1
                    counters.append((row, column))
                    if run == 4 and player != " ":
                        return player # , counters
                else:
                    player = board[row][column]
                    counters = [(row, column)]
                    run = 1

        # check diagonal
        for rowNum, row in enumerate(board):
            for colNum, col in enumerate(row):
                if col != " ":
                    # \ diagonal
                    if colNum < 4 and rowNum < 3:
                        counterOne = board[rowNum][colNum]
                        counterTwo = board[rowNum + 1][colNum + 1]
                        counterThree = board[rowNum + 2][colNum + 2]
                        counterFour = board[rowNum + 3][colNum + 3]
                        if counterOne == counterTwo == counterThree == counterFour:
                            return col # , [(rowNum, colNum), (rowNum + 1, colNum + 1), (rowNum + 2, colNum + 2), (rowNum + 3, colNum + 3)]

                    # / diagonal
                    if colNum > 2 and rowNum < 3:
                        counterOne = board[rowNum][colNum]
                        counterTwo = board[rowNum + 1][colNum - 1]
                        counterThree = board[rowNum + 2][colNum - 2]
                        counterFour = board[rowNum + 3][colNum - 3]
                        if counterOne == counterTwo == counterThree == counterFour:
                            return col # , [(rowNum, colNum), (rowNum + 1, colNum - 1), (rowNum + 2, colNum - 2), (rowNum + 3, colNum - 3)]
        # check draw
        occupiedCount = 0
        for row in board:
            for col in row:
                if col != " ":
                    occupiedCount += 1
        if occupiedCount == 42:
            return "Draw" # , []
        return None # , []
