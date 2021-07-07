from abc import ABC, abstractmethod
from tkinter import Tk, Frame, Button, X, Toplevel, N, S, E, W, Grid, Canvas, StringVar, Listbox, Label, END, UNITS
from game import game, gameError


class ui(ABC):
    @abstractmethod
    def run(self):
        raise NotImplementedError


class gui(ui):
    def __init__(self):
        root = Tk()
        root.title("ConnectFour")
        frame = Frame(root)
        frame.pack()
        self.__root = root
        
        Button(frame, text="Help", command=self._help).pack(fill=X)
        Button(frame, text="Play", command=self._play).pack(fill=X)
        Button(frame, text="Quit", command=self._quit).pack(fill=X)
        
    def _help(self):
        pass
    
    def _play(self):
        self.__game = game()
        gameWin = Toplevel(self.__root)
        gameWin.title("Game")
        frame = Frame(gameWin)
        self.__gameWin = gameWin

        Grid.columnconfigure(gameWin, 0, weight=1)
        Grid.rowconfigure(gameWin, 0, weight=1)
        frame.grid(row=0, column=0, sticky=N+S+W+E)

        board = Canvas(gameWin, width=700, height=600, bg='blue')
        baseX1 = 10
        baseY1 = 10
        baseX2 = 90
        baseY2 = 90
        step = 100
        self.__spaces = [[None for _ in range(7)] for _ in range(6)]
        for row in range(6):
            for column in range(7):
                # create white circle on blue background
                oval = board.create_oval(baseX1 + (column*step), baseY1 + (row*step), baseX2 + (column*step), baseY2 + (row*step), fill="white")#, dash=(7,1,1,1)
                self.__spaces[row][column] = oval
        board.grid(row=1, column=0)
        self.__canvas = board

        console = Listbox(frame, height=5)
        console.grid(row=2, column=0, columnspan=4, sticky=E+W)
        self.__gameConsole = console

        self.__playerTurn = StringVar()
        self.__playerTurn.set('red to play')
        Label(frame, textvariable=self.__playerTurn, bg='gray').grid(row=2, column=4, columnspan=3, sticky=N+S+E+W)

        Button(gameWin, text="Dismiss", command=self._dismissGame).grid(row=3, column=0, sticky=N+S+W+E)

        for col in range(7):
            t = StringVar()
            t.set(col + 1)
            cmd = lambda c=col: self.__playMove(c)
            Button(frame, textvariable=t, command=cmd).grid(row=0, column=col, sticky=N+S+W+E)

        # resizing
        for col in range(7):
            Grid.columnconfigure(frame, col, weight=1)

    def __playMove(self, col):
        if not self.__game.getWinner:
            try:
                counter = 'red' if self.__game.getPlayer == game.PONE else 'yellow'
                row = 5 - self.__game.play(col + 1)
                self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)
                counter = 'red' if self.__game.getPlayer == game.PONE else 'yellow'
                self.__playerTurn.set(f'{counter} to play')
            except gameError as e:
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {e}")
                if self.__gameConsole.size() > 5:
                    self.__gameConsole.yview_scroll(1, UNITS)
            if self.__game.getWinner:
                winner = 'red' if self.__game.getWinner == game.PONE else 'yellow'
                message = f"{winner} has won, well played!" if self.__game.getWinner != "Draw" else "The game was a draw!"
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {message}")
                if self.__gameConsole.size() > 5:
                    self.__gameConsole.yview_scroll(1, UNITS)

    def _dismissGame(self):
        self.__gameWin.destroy()

    def _quit(self):
        self.__root.quit()
        
    def run(self):
        self.__root.mainloop()


class terminal(ui):
    def __init__(self):
        self._Game = game()

    def run(self):
        while not self._Game.getWinner:
            print(self._Game)
            print(f"{self._Game.getPlayer} to play...")
            # type check
            try:
                column = int(input("Enter column number to drop counter: "))
            except ValueError:
                print("\n\n\n\nERROR: invalid input: expected integer")
                continue
            # range check
            if 1 <= column <= 7:
                try:
                    self._Game.play(column)
                except gameError:
                    print("\n\n\n\nERROR: column full")
            else:
                print("\n\n\n\nERROR: input must be between 1 and 7 inclusive")
        print(self._Game)
        winner = self._Game.getWinner
        if winner == "Draw":
            print("The game was a draw!")
        else:
            print(f"{winner} has won, well played!")
