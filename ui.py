from abc import ABC, abstractmethod
from game import game

class ui(ABC):
    @abstractmethod
    def run(self):
        raise NotImplementedError

class gui(ui):
    def __init__(self):
        pass

    def run(self):
        pass

class terminal(ui):
    def __init__(self):
        self._Game = game()

    def run(self):
        while not self._Game.getWinner:
            print(self._Game)
            print(f"{self._Game.getPlayer} to play...")
            column = int(input("Enter column number to drop counter: "))
            self._Game.play(column)
        print(self._Game)
        winner = self._Game.getWinner
        if winner == "Draw":
            print("The game was a draw!")
        else:
            print(f"{winner} has won, well played!")
        