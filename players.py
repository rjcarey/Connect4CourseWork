from random import randint
from game import game
from copy import deepcopy
from collections import defaultdict as dd


class Ai:
    def __init__(self, difficulty):
        self.__difficulty = difficulty
        self.__priorList = [3, 2, 4, 1, 5, 0, 6]
        self.__aiCounter = None
        self.__playerCounter = None

    def getColumn(self, board, counter):
        move = None
        self.__aiCounter = counter
        self.__playerCounter = game.PONE if counter != game.PONE else game.PTWO
        if self.__difficulty == "Practice AI":
            move = self.__practiceAI(board)
        elif self.__difficulty == "Easy AI":
            move = self.__easyAI(board, counter)
        elif self.__difficulty == "Medium AI":
            move = self.__mediumAI(board)
        elif self.__difficulty == "Hard AI":
            move = self.__hardAI(board, counter)

        # return the ai's move
        return move

    @staticmethod
    def __practiceAI(board):
        col = -1
        while col == -1:
            # play random column
            move = randint(0, 6)
            if board[0][move] == " ":
                col = move
        return col

    def __easyAI(self, board, counter):
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
            playedRow = None
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
            # \ diagonal
            if (upOne and leftOne) and board[playedRow - 1][column - 1] == counter:
                currentScore += 1
                if (upTwo and leftTwo) and board[playedRow - 2][column - 2] == counter:
                    currentScore *= 2
                    if (upThree and leftThree) and board[playedRow - 3][column - 3] == counter:
                        currentScore *= 9999
                    elif (downOne and rightOne) and board[playedRow + 1][column + 1] == counter:
                        currentScore *= 9999
                elif (downOne and rightOne) and board[playedRow + 1][column + 1] == counter:
                    currentScore *= 2
                    if (downTwo and rightTwo) and board[playedRow + 2][column + 2] == counter:
                        currentScore *= 9999
            elif (downOne and rightOne) and board[playedRow + 1][column + 1] == counter:
                currentScore += 1
                if (downTwo and rightTwo) and board[playedRow + 2][column + 2] == counter:
                    currentScore *= 2
                    if (downThree and rightThree) and board[playedRow + 3][column + 3] == counter:
                        currentScore *= 9999

            score += currentScore
            currentScore = 0
            # / diagonal
            if (downOne and leftOne) and board[playedRow + 1][column - 1] == counter:
                currentScore += 1
                if (downTwo and leftTwo) and board[playedRow + 2][column - 2] == counter:
                    currentScore *= 2
                    if (downThree and leftThree) and board[playedRow + 3][column - 3] == counter:
                        currentScore *= 9999
                    elif (upOne and rightOne) and board[playedRow - 1][column + 1] == counter:
                        currentScore *= 9999
                elif (upOne and rightOne) and board[playedRow - 1][column + 1] == counter:
                    currentScore *= 2
                    if (upTwo and rightTwo) and board[playedRow - 2][column + 2] == counter:
                        currentScore *= 9999
            elif (upOne and rightOne) and board[playedRow - 1][column + 1] == counter:
                currentScore += 1
                if (upTwo and rightTwo) and board[playedRow - 2][column + 2] == counter:
                    currentScore *= 2
                    if (upThree and rightThree) and board[playedRow - 3][column + 3] == counter:
                        currentScore *= 999

            score += currentScore
            currentScore = 0
            # Across
            if leftOne and board[playedRow][column - 1] == counter:
                currentScore += 1
                if leftTwo and board[playedRow][column - 2] == counter:
                    currentScore *= 2
                    if leftThree and board[playedRow][column - 3] == counter:
                        currentScore *= 9999
                    elif rightOne and board[playedRow][column + 1] == counter:
                        currentScore *= 9999
                elif rightOne and board[playedRow][column + 1] == counter:
                    currentScore *= 2
                    if rightTwo and board[playedRow][column + 2] == counter:
                        currentScore *= 9999
            elif rightOne and board[playedRow][column + 1] == counter:
                currentScore += 1
                if rightTwo and board[playedRow][column + 2] == counter:
                    currentScore *= 2
                    if rightThree and board[playedRow][column + 3] == counter:
                        currentScore *= 9999

            score += currentScore
            currentScore = 0
            # Down
            if downOne and board[playedRow + 1][column] == counter:
                currentScore += 1
                if downTwo and board[playedRow + 2][column] == counter:
                    currentScore *= 2
                    if downThree and board[playedRow + 3][column] == counter:
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
        for move in self.__priorList:
            if move in maxIndex:
                return move

    def __mediumAI(self, board):
        boards = self.__nextBoards(board, self.__aiCounter)
        boardList = []
        moves = []
        for key in boards.keys():
            boardList.append((key, boards[key], self.__medMiniMax(3, boards[key], False)))
        value = -9999999
        for newBoard in boardList:
            if newBoard[2] > value:
                value = newBoard[2]
                moves = [newBoard[0]]
            elif newBoard[2] == value:
                moves.append(newBoard[0])
        for move in self.__priorList:
            if move in moves:
                return move

    def __hardAI(self, board, counter):
        # include trapping, traps can be detected be detected by checking if there all the children node are 1 (winning trap) or all the children nodes are -1 (losing trap)
        boards = self.__nextBoards(board, self.__aiCounter)
        boardList = []
        moves = []
        for key in boards.keys():
            boardList.append((key, boards[key], self.__hardMiniMax(5, boards[key], False)))
        value = -9999999
        for newBoard in boardList:
            if newBoard[2] > value:
                value = newBoard[2]
                moves = [newBoard[0]]
            elif newBoard[2] == value:
                moves.append(newBoard[2])
        if len(moves) == 7:
            return self.__easyAI(board, counter)
        for move in self.__priorList:
            if move in moves:
                return move

    def __medMiniMax(self, depth, board, aiTurn):
        end = self.__checkTerminal(board)
        if depth == 0 or end is not None:
            if end == self.__aiCounter:
                return 1 + depth
            elif end == self.__playerCounter:
                return -1 - depth
            else:
                return 0
        if aiTurn:
            value = -9999999
            newBoards = self.__nextBoards(board, self.__aiCounter)
            for newBoard in newBoards.values():
                newVal = self.__medMiniMax(depth - 1, newBoard, False)
                if newVal > value:
                    value = newVal
            return value
        else:
            value = 9999999
            newBoards = self.__nextBoards(board, self.__playerCounter)
            for newBoard in newBoards.values():
                newVal = self.__medMiniMax(depth - 1, newBoard, True)
                if newVal < value:
                    value = newVal
            return value

    def __hardMiniMax(self, depth, board, aiTurn):
        depthValues = dd(lambda: 0)
        end = self.__checkTerminal(board)
        if depth == 0 or end is not None:
            if end == self.__aiCounter:
                return 1 + depth
            elif end == self.__playerCounter:
                return -1 - depth
            else:
                return 0
        if aiTurn:
            value = -9999999
            newBoards = self.__nextBoards(board, self.__aiCounter)
            for newBoard in newBoards.values():
                newVal = self.__hardMiniMax(depth - 1, newBoard, False)
                depthValues[newVal] += 1
                if newVal > value:
                    value = newVal
            if len(depthValues) == 1:
                value += 0.1
            return value
        else:
            value = 9999999
            newBoards = self.__nextBoards(board, self.__playerCounter)
            for newBoard in newBoards.values():
                newVal = self.__hardMiniMax(depth - 1, newBoard, True)
                depthValues[newVal] += 1
                if newVal < value:
                    value = newVal
            if len(depthValues) == 1:
                value -= 0.1
            return value

    @staticmethod
    def __nextBoards(board, counter):
        boards = {}
        for iC, column in enumerate(board[0]):
            if column == " ":
                newBoard = game()
                newBoard.loadAI(deepcopy(board), counter)
                newBoard.play(iC+1)
                boards[iC] = newBoard.Board
        return boards

    @staticmethod
    def __checkTerminal(board):
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
                        return player  # , counters
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
                        return player  # , counters
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
                            return col  # , [(rowNum, colNum), (rowNum + 1, colNum + 1), (rowNum + 2, colNum + 2), (rowNum + 3, colNum + 3)]

                    # / diagonal
                    if colNum > 2 and rowNum < 3:
                        counterOne = board[rowNum][colNum]
                        counterTwo = board[rowNum + 1][colNum - 1]
                        counterThree = board[rowNum + 2][colNum - 2]
                        counterFour = board[rowNum + 3][colNum - 3]
                        if counterOne == counterTwo == counterThree == counterFour:
                            return col  # , [(rowNum, colNum), (rowNum + 1, colNum - 1), (rowNum + 2, colNum - 2), (rowNum + 3, colNum - 3)]
        # check draw
        occupiedCount = 0
        for row in board:
            for col in row:
                if col != " ":
                    occupiedCount += 1
        if occupiedCount == 42:
            return "Draw"  # , []
        return None  # , []
