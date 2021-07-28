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
            #print(f"column {column + 1}:")
            # check for full row
            if board[0][column] != " ":
                #print(f"{column} full")
                scores[column] = -1
                break

            #find the row that would be played in
            #print(board)
            for i, row in enumerate(board):
                #print(f"{i}, {row}")
                if row[column] != " ":
                    playedRow = i - 1
                    break
                elif i == 5:
                    playedRow = 5

            #print(f"played row: {playedRow}")

            #check what counters this play would connect with and calculate resulting score
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
            #print(f"{column}, {playedRow}: {leftOne}, {leftTwo}, {leftThree}, {downOne}, {downTwo}, {downThree}, {rightOne}, {rightTwo}, {rightThree}, {upOne}, {upTwo}, {upThree}")

            score = 0
            currentScore = 0
            if upOne and leftOne:
                if board[playedRow - 1][column - 1] == counter:
                    #print("upOne and leftOne")
                    currentScore += 1
                    if upTwo and leftTwo:
                        if board[playedRow - 2][column - 2] == counter:
                            #print("upTwo and leftTwo")
                            currentScore *= 2
                            if upThree and leftThree:
                                if board[playedRow - 3][column - 3] == counter:
                                    #print("upThree and leftThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if leftOne:
                if board[playedRow][column - 1] == counter:
                    #print("leftOne")
                    currentScore += 1
                    if leftTwo:
                        if board[playedRow][column - 2] == counter:
                            #print("leftTwo")
                            currentScore *= 2
                            if leftThree:
                                if board[playedRow][column - 3] == counter:
                                    #print("leftThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if downOne and leftOne:
                if board[playedRow + 1][column - 1] == counter:
                    #print("downOne and leftOne")
                    currentScore += 1
                    if downTwo and leftTwo:
                        if board[playedRow + 2][column - 2] == counter:
                            #print("downTwo and leftTwo")
                            currentScore *= 2
                            if downThree and leftThree:
                                if board[playedRow + 3][column - 3] == counter:
                                    #print("downThree and leftThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if downOne:
                if board[playedRow + 1][column] == counter:
                    #print("downOne")
                    currentScore += 1
                    if downTwo:
                        if board[playedRow + 2][column] == counter:
                            #print("downTwo")
                            currentScore *= 2
                            if downThree:
                                if board[playedRow + 3][column] == counter:
                                    #print("downThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if downOne and rightOne:
                if board[playedRow + 1][column + 1] == counter:
                    #print("downOne and rightOne")
                    currentScore += 1
                    if downTwo and rightTwo:
                        if board[playedRow + 2][column + 2] == counter:
                            #print("downTwo and rightTwo")
                            currentScore *= 2
                            if downThree and rightThree:
                                if board[playedRow + 3][column + 3] == counter:
                                    #print("downThree and rightThree")
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if rightOne:
                if board[playedRow][column + 1] == counter:
                    #print("rightOne")
                    currentScore += 1
                    if rightTwo:
                        if board[playedRow][column + 2] == counter:
                            #print("rightTwo")
                            currentScore *= 2
                            if rightThree:
                                if board[playedRow][column + 3] == counter:
                                    #print(rightThree)
                                    currentScore *= 9999

            score += currentScore
            currentScore = 0
            if upOne and rightOne:
                if board[playedRow - 1][column + 1] == counter:
                    #print("upOne and rightOne")
                    currentScore += 1
                    if upTwo and rightTwo:
                        if board[playedRow - 2][column + 2] == counter:
                            #print("upTwo and rightTwo")
                            currentScore *= 2
                            if upThree and rightThree:
                                if board[playedRow - 3][column + 3] == counter:
                                    #print("upThree and rightThree")
                                    currentScore *= 9999

            score += currentScore
            scores[column] = score

        #find the best scoring move
        #print(scores)
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
        #low depth minimax
        pass

    def hardAI(self, board):
        #medium depth minimax and trapping
        pass
