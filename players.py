from random import randint

class Ai:
    def __init__(self, difficulty):
        self.__difficulty = difficulty

    def getColumn(self, board, counter):
        if self.__difficulty == "Practice AI":
            move = self.practiceAI(board)
        elif self.__difficulty == "Easy AI":
            move = self.easyAI(board, counter)
        elif self.__difficulty == "Medium AI":
            move = self.mediumAI(board)
        elif self.__difficulty == "Hard AI":
            move = self.hardAI(board)

        return move

    def practiceAI(self, board):
        col = -1
        while col == -1:
            #play random column
            move = randint(0, 6)
            if board[0][move] == " ":
                col = move
        return col

    def easyAI(self, board, counter):
        scores = [0,0,0,0,0,0,0]
        for column in range(7):
            # check for full row
            if board[0][column] != " ":
                scores[column] = -1
                break

            #find the row that would be played in
            for i, row in enumerate(reversed(board)):
                if row[column] == " ":
                    playedRow = 5 - i

            #check what counters this play would connect with and calculate resulting score
            leftOne = True if column > 0 else False
            leftTwo = True if column > 1 else False
            leftThree = True if column > 2 else False
            downOne = True if playedRow < 6 else False
            downTwo = True if playedRow < 5 else False
            downThree = True if playedRow > 4 else False
            rightOne = True if column < 6 else False
            rightTwo = True if column < 5 else False
            rightThree = True if column < 4 else False
            upOne = True if playedRow > 0 else False
            upTwo = True if playedRow > 1 else False
            upThree = True if playedRow > 2 else False

            score = 0
            currentScore = 0
            if upOne and leftOne:
                if board[playedRow - 1][column - 1] == counter:
                    currentScore += 1
                    if upTwo and leftTwo:
                        if board[playedRow - 2][column - 2] == counter:
                            currentScore *= 2
                            if upThree and leftThree:
                                if board[playedRow - 3][column - 3] == counter:
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if leftOne:
                if board[playedRow][column - 1] == counter:
                    currentScore += 1
                    if leftTwo:
                        if board[playedRow][column - 2] == counter:
                            currentScore *= 2
                            if leftThree:
                                if board[playedRow][column - 3] == counter:
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0

            if downOne and leftOne:
                if board[playedRow + 1][column - 1] == counter:
                    currentScore += 1
                    if downTwo and leftTwo:
                        if board[playedRow + 2][column - 2] == counter:
                            currentScore *= 2
                            if downThree and leftThree:
                                if board[playedRow + 3][column - 3] == counter:
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if downOne:
                if board[playedRow + 1][column] == counter:
                    currentScore += 1
                    if downTwo:
                        if board[playedRow + 2][column] == counter:
                            currentScore *= 2
                            if downThree:
                                if board[playedRow + 3][column] == counter:
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if downOne and rightOne:
                if board[playedRow + 1][column + 1] == counter:
                    currentScore += 1
                    if downTwo and rightTwo:
                        if board[playedRow + 2][column + 2] == counter:
                            currentScore *= 2
                            if downThree and rightThree:
                                if board[playedRow + 3][column + 3] == counter:
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if rightOne:
                if board[playedRow][column + 1] == counter:
                    currentScore += 1
                    if rightTwo:
                        if board[playedRow][column + 2] == counter:
                            currentScore *= 2
                            if rightThree:
                                if board[playedRow][column + 3] == counter:
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if upOne and rightOne:
                if board[playedRow - 1][column + 1] == counter:
                    currentScore += 1
                    if upTwo and rightTwo:
                        if board[playedRow - 2][column + 2] == counter:
                            currentScore *= 2
                            if upThree and rightThree:
                                if board[playedRow - 3][column + 3] == counter:
                                    currentScore *= 9999

            score += currentScore
            scores[column] = score

        #find the best scoring move
        maxScore = -1
        maxIndex = []
        for i, score in enumerate(scores):
            if maxScore < score:
                maxScore = score
                maxIndex = [i]
            elif maxScore == score:
                maxIndex.append(i)
        return maxIndex[randint(0, len(maxIndex) - 1)]

    def mediumAI(self, board):
        #low depth minimax
        pass

    def hardAI(self, board):
        #medium depth minimax and trapping
        pass
