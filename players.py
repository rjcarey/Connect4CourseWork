from random import randint
from game import game
from copy import deepcopy
from collections import defaultdict as dd


class Ai:
    def __init__(self, difficulty):
        self.__difficulty = difficulty
        self.__priorList = [3, 2, 4, 1, 5, 0, 6]
        self.__aiCounter = self.__playerCounter = None

    def getColumn(self, board, counter):
        self.__aiCounter = counter
        self.__playerCounter = game.PONE if counter != game.PONE else game.PTWO
        algorithms = {"Practice AI": self.__practiceAI, "Easy AI": self.__easyAI, "Medium AI": self.__mediumAI, "Hard AI": self.__hardAI}
        # Return the column for the AI to play in
        return algorithms[self.__difficulty](board)

    @staticmethod
    def __practiceAI(board):
        # Pick a random column, check if it is not full, if it is not full, return that column number
        col = -1
        while col == -1:
            move = randint(0, 6)
            if board[0][move] == " ":
                col = move
        return col

    def __easyAI(self, board):
        # Evaluate a score for each possible move and return the move of the highest score
        scores = [0] * 7
        for column in range(7):
            # If the column is full, avoid playing here by setting negative score
            scores[column] = -1 if board[0][column] != " " else self.__evaluateBoard(board, column, True)

        # Find the best scoring move and return it
        maxScore = -1
        maxIndex = []
        for i, score in enumerate(scores):
            if maxScore < score:
                maxScore = score
                maxIndex = [i]
            elif maxScore == score:
                maxIndex.append(i)

        # If there is more than one best move, pick the move with the highest priority
        for move in self.__priorList:
            if move in maxIndex:
                return move

    def __mediumAI(self, board):
        # Use a low depth minimax with no heuristics to find the best move
        boards = self.__nextBoards(board, self.__aiCounter)
        boardList = []
        moves = []

        for key in boards.keys():
            boardList.append((key, boards[key], self.__miniMax(3, boards[key], False, False, key)))

        value = -9999999
        for newBoard in boardList:
            if newBoard[2] > value:
                value = newBoard[2]
                moves = [newBoard[0]]
            elif newBoard[2] == value:
                moves.append(newBoard[0])

        # If there is more than one best move, pick the move with the highest priority
        for move in self.__priorList:
            if move in moves:
                return move

    def __hardAI(self, board):
        # Use a minimax, which accounts for trapping and uses the easy AI algorithm for non-terminal leaf nodes to return the best move
        boards = self.__nextBoards(board, self.__aiCounter)
        boardList = []
        moves = []

        for key in boards.keys():
            boardList.append((key, boards[key], self.__miniMax(5, boards[key], False, True, key)))

        value = -9999999
        for newBoard in boardList:
            if newBoard[2] > value:
                value = newBoard[2]
                moves = [newBoard[0]]
            elif newBoard[2] == value:
                moves.append(newBoard[2])

        # If there is more than one best move, pick the move with the highest priority
        for move in self.__priorList:
            if move in moves:
                return move

    def __miniMax(self, depth, board, aiTurn, hardAI, col):
        ##############################################
        # GROUP A SKILL: Recursive minimax algorithm #
        ##############################################
        depthValues = dd(lambda: 0)
        end = self.__checkTerminal(board)

        if depth == 0 or end is not None:
            if end == self.__aiCounter:
                return 1 + depth
            elif end == self.__playerCounter:
                return -1 - depth
            elif end is None and hardAI:
                return self.__evaluateBoard(board, col, False)
            else:
                return 0

        if aiTurn:
            value = -9999999
            newBoards = self.__nextBoards(board, self.__aiCounter)
            for move in newBoards.keys():
                newVal = self.__miniMax(depth - 1, newBoards[move], False, hardAI, move)
                depthValues[newVal] += 1
                if newVal > value:
                    value = newVal

            if len(depthValues) == 1 and hardAI:
                value += 0.1
            return value

        else:
            value = 9999999
            newBoards = self.__nextBoards(board, self.__playerCounter)
            for move in newBoards.keys():
                newVal = self.__miniMax(depth - 1, newBoards[move], True, hardAI, move)
                depthValues[newVal] += 1
                if newVal < value:
                    value = newVal

            if len(depthValues) == 1 and hardAI:
                value -= 0.1
            return value

    def __evaluateBoard(self, board, column, easyAI):
        #########################################################################################
        # GROUP A SKILL: Complex user defined algorithm to evaluate a score for a possible move #
        #########################################################################################
        playedRow = 5
        for i, row in enumerate(board):
            if row[column] != " ":
                if easyAI:
                    playedRow = i - 1
                else:
                    playedRow = i
                break

        # Set flags to determine where to search for runs
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

        score = 0
        currentScore = 0

        # Check \ diagonal
        if (upOne and leftOne) and board[playedRow - 1][column - 1] == self.__aiCounter:
            currentScore += 0.0001
            if (upTwo and leftTwo) and board[playedRow - 2][column - 2] == self.__aiCounter:
                currentScore *= 3
                if (upThree and leftThree) and board[playedRow - 3][column - 3] == self.__aiCounter:
                    return 1
                elif (downOne and rightOne) and board[playedRow + 1][column + 1] == self.__aiCounter:
                    return 1
            elif (downOne and rightOne) and board[playedRow + 1][column + 1] == self.__aiCounter:
                currentScore *= 3
                if (downTwo and rightTwo) and board[playedRow + 2][column + 2] == self.__aiCounter:
                    return 1
        elif (downOne and rightOne) and board[playedRow + 1][column + 1] == self.__aiCounter:
            currentScore += 0.0001
            if (downTwo and rightTwo) and board[playedRow + 2][column + 2] == self.__aiCounter:
                currentScore *= 3
                if (downThree and rightThree) and board[playedRow + 3][column + 3] == self.__aiCounter:
                    return 1
        score += currentScore
        currentScore = 0

        # Check / diagonal
        if (downOne and leftOne) and board[playedRow + 1][column - 1] == self.__aiCounter:
            currentScore += 0.0001
            if (downTwo and leftTwo) and board[playedRow + 2][column - 2] == self.__aiCounter:
                currentScore *= 3
                if (downThree and leftThree) and board[playedRow + 3][column - 3] == self.__aiCounter:
                    return 1
                elif (upOne and rightOne) and board[playedRow - 1][column + 1] == self.__aiCounter:
                    return 1
            elif (upOne and rightOne) and board[playedRow - 1][column + 1] == self.__aiCounter:
                currentScore *= 3
                if (upTwo and rightTwo) and board[playedRow - 2][column + 2] == self.__aiCounter:
                    return 1
        elif (upOne and rightOne) and board[playedRow - 1][column + 1] == self.__aiCounter:
            currentScore += 0.0001
            if (upTwo and rightTwo) and board[playedRow - 2][column + 2] == self.__aiCounter:
                currentScore *= 3
                if (upThree and rightThree) and board[playedRow - 3][column + 3] == self.__aiCounter:
                    return 1
        score += currentScore
        currentScore = 0

        # Check horizontal
        if leftOne and board[playedRow][column - 1] == self.__aiCounter:
            currentScore += 0.0001
            if leftTwo and board[playedRow][column - 2] == self.__aiCounter:
                currentScore *= 3
                if leftThree and board[playedRow][column - 3] == self.__aiCounter:
                    return 1
                elif rightOne and board[playedRow][column + 1] == self.__aiCounter:
                    return 1
            elif rightOne and board[playedRow][column + 1] == self.__aiCounter:
                currentScore *= 3
                if rightTwo and board[playedRow][column + 2] == self.__aiCounter:
                    return 1
        elif rightOne and board[playedRow][column + 1] == self.__aiCounter:
            currentScore += 0.0001
            if rightTwo and board[playedRow][column + 2] == self.__aiCounter:
                currentScore *= 3
                if rightThree and board[playedRow][column + 3] == self.__aiCounter:
                    return 1
        score += currentScore
        currentScore = 0

        # Check vertical
        if downOne and board[playedRow + 1][column] == self.__aiCounter:
            currentScore += 0.0001
            if downTwo and board[playedRow + 2][column] == self.__aiCounter:
                currentScore *= 3
                if downThree and board[playedRow + 3][column] == self.__aiCounter:
                    return 1
        score += currentScore

        return score

    @staticmethod
    def __nextBoards(board, counter):
        # Return a dictionary of board which are one move forward from the board passed in, whose keys are the move taken to get to the board
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
        # Complex user defined algorithm to check if the passed in game is a terminal game (adaption of getRun method in game class)
        # Check for horizontal run
        player = " "
        for ir, row in enumerate(board):
            run = 0
            for ic, col in enumerate(row):
                if col == player:
                    run += 1
                    if run == 4 and player != " ":
                        return player
                else:
                    player = col
                    run = 1

        # Check for vertical run
        player = " "
        for column in range(7):
            run = 0
            for row in range(6):
                if board[row][column] == player:
                    run += 1
                    if run == 4 and player != " ":
                        return player
                else:
                    player = board[row][column]
                    run = 1

        for rowNum, row in enumerate(board):
            for colNum, col in enumerate(row):
                if col != " ":
                    # Check \ diagonal
                    if colNum < 4 and rowNum < 3:
                        if board[rowNum][colNum] == board[rowNum + 1][colNum + 1] == board[rowNum + 2][colNum + 2] == board[rowNum + 3][colNum + 3]:
                            return col
                    # Check / diagonal
                    if colNum > 2 and rowNum < 3:
                        if board[rowNum][colNum] == board[rowNum + 1][colNum - 1] == board[rowNum + 2][colNum - 2] == board[rowNum + 3][colNum - 3]:
                            return col

        # Check for a draw
        for col in board[0]:
            if col == game.EMPTY:
                return None
        return "Draw"
