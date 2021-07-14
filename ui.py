from abc import ABC, abstractmethod
from tkinter import Tk, Frame, Button, X, Toplevel, N, S, E, W, Grid, Canvas, StringVar, Listbox, Label, END, UNITS, HORIZONTAL, Scale, LEFT, RIGHT, OptionMenu
from game import game, gameError
from time import sleep
from players import Ai

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
        self.__gameInProgress = False
        self.__helpInProgress = False
        self.__setupInProgress = False
        self.__gameOver = False
        self.__animating = False
        
        Button(frame, text="Help", command=self._help).pack(fill=X)
        Button(frame, text="Play", command=self._gameSetup).pack(fill=X)
        Button(frame, text="Quit", command=self._quit).pack(fill=X)

    def _gameSetup(self):
        if not self.__setupInProgress:
            self.__setupInProgress = True
            setupWin = Toplevel(self.__root)
            setupWin.title("Game Setup")
            frame = Frame(setupWin)
            self.__setupWin = setupWin
            self.__opponentType = StringVar()
            self.__opponent = None

            Grid.columnconfigure(self.__setupWin, 0, weight=1)
            Grid.rowconfigure(self.__setupWin, 0, weight=1)
            frame.grid(row=0, column=0, sticky=N + S + W + E)

            #first player
            '''
            Label(frame, text="Choose Player 1:").grid(row=0)
            Label(frame, text="RED").grid(row=1, column=0)
            turnSlider = Scale(self.__setupWin, from_=0, to_=1, orient=HORIZONTAL, showvalue=0)
            turnSlider.grid(row=1, column=1)
            Label(frame, text="YELLOW").grid(row=1, column=2)
            #self._firstTurn = turnSlider.get()
            '''

            #opponent
            Label(frame, text="Choose Opponent:").grid(row=0, column=0)
            options = ["Human", "AI"]
            self.__opponentType.set("Human")
            opponentDropDown = OptionMenu(self.__setupWin, self.__opponentType, *options)
            opponentDropDown.grid(row=0, column=1, sticky=N)

            #play button
            Button(frame, text="Play", command=self._play).grid(row=1, column=0, columnspan=2)

            #back button
            Button(frame, text="Back", command=self._dismissSetup).grid(row=2, column=0, columnspan=2)

    def _dismissSetup(self):
        self.__setupWin.destroy()
        self.__setupInProgress = False

    def _help(self):
        if not self.__helpInProgress:
            self.__helpInProgress = True
            helpWin = Toplevel(self.__root)
            helpWin.title("Help")
            frame = Frame(helpWin)
            frame.pack()
            self.__helpWin = helpWin

            #rule display
            Label(frame, text="Take it in turns to  drop counters into the board.").pack()
            Label(frame, text="First person to get a vertical, horizontal or diagonal run of four counters wins!").pack()
            Label(frame, text="If the board fills and nobody has a run of four yet then the game is drawn.").pack()

            #dismiss button
            Button(frame, text="Dismiss", command=self._dismissHelp).pack()
    
    def _play(self):
        if not self.__gameInProgress:
            if self.__opponentType == "AI":
                self.__opponent = Ai()
            self.__gameInProgress = True
            self.__game = game()
            gameWin = Toplevel(self.__root)
            gameWin.title("Game")
            frame = Frame(gameWin)
            self.__gameWin = gameWin

            Grid.columnconfigure(gameWin, 0, weight=1)
            Grid.rowconfigure(gameWin, 0, weight=1)
            frame.grid(row=0, column=0, sticky=N + S + W + E)

            #console
            console = Listbox(frame, height=3)
            console.grid(row=0, column=0, columnspan=4, sticky=E + W)
            self.__gameConsole = console
            self.__gameConsole.insert(END, f"1| game against {self.__opponentType.get()}")

            #player turn label
            self.__playerTurn = StringVar()
            self.__playerTurn.set('RED TO PLAY\nCHOOSE COLUMN')
            Label(frame, textvariable=self.__playerTurn, bg='gray').grid(row=0, column=4, columnspan=3, sticky=N + S + E + W)

            #board
            #Change tile to change board size
            winWidth = self.__gameWin.winfo_screenwidth()
            if winWidth < 40:
                #min board tile size
                winWidth = 40
            elif winWidth > 110:
                #max board tile size
                winWidth = 110
            tile = winWidth
            counterSize = tile * 0.8
            boardWidth = 7 * tile
            boardHeight = 6 * tile
            board = Canvas(gameWin, width=boardWidth, height=boardHeight, bg='blue')
            baseX1 = tile / 10
            baseY1 = tile / 10
            baseX2 = baseX1 + counterSize
            baseY2 =baseY1 + counterSize
            self.__spaces = [[None for _ in range(7)] for _ in range(6)]
            for row in range(6):
                for column in range(7):
                    # create white circles on blue background
                    oval = board.create_oval(baseX1 + (column*tile), baseY1 + (row*tile), baseX2 + (column*tile), baseY2 + (row*tile), fill="white")#, dash=(7,1,1,1)
                    self.__spaces[row][column] = oval
            board.grid(row=1, column=0)
            self.__canvas = board

            #undo button
            Button(gameWin, text="Undo", command=self._undoMove).grid(row=3, column=0, sticky=N+S+W+E)
            #dismiss button
            Button(gameWin, text="Dismiss", command=self._dismissGame).grid(row=4, column=0, sticky=N+S+W+E)

            #column buttons
            for col in range(7):
                t = StringVar()
                t.set(col + 1)
                cmd = lambda c=col: self.__playMove(c)
                Button(frame, textvariable=t, command=cmd).grid(row=1, column=col, sticky=N+S+W+E)

            # resizing
            for col in range(7):
                Grid.columnconfigure(frame, col, weight=1)

    def _undoMove(self):
        if not self.__gameOver:
            try:
                row, col = self.__game.undo()
                self.__canvas.itemconfig(self.__spaces[row][col], fill="white")
                counter = 'RED' if self.__game.getPlayer == game.PONE else 'YELLOW'
                self.__playerTurn.set(f'{counter} TO PLAY\nCHOOSE COLUMN')
            except gameError as e:
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {e}")
                if self.__gameConsole.size() > 3:
                    self.__gameConsole.yview_scroll(1, UNITS)
        else:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| undo unavailable")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)


    def __playMove(self, col):
        if self.__animating:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| please wait...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)
        elif not self.__game.getWinner:
            try:
                counter = 'red' if self.__game.getPlayer == game.PONE else '#e6e600'
                row = 5 - self.__game.play(col + 1)
                self.__animatedDrop(row, col, counter)
                self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)
                counter = 'RED' if self.__game.getPlayer == game.PONE else 'YELLOW'
                self.__playerTurn.set(f'{counter} TO PLAY\nCHOOSE COLUMN')
            except gameError as e:
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {e}")
                if self.__gameConsole.size() > 3:
                    self.__gameConsole.yview_scroll(1, UNITS)

            winningPlayer, run = self.__game.getRun
            if winningPlayer:
                self.__gameOver = True
                if self.__game.getWinner != "Draw":
                    winner = 'RED' if self.__game.getWinner == game.PONE else 'YELLOW'
                    self.__playerTurn.set(f'{winner} HAS WON\nCONGRATULATIONS!')
                else:
                    self.__playerTurn.set(f'THE GAME WAS DRAWN')

                #highlight winning run
                if run:
                    counter = "#ff9999" if winningPlayer == game.PONE else "#ffffb3"
                    for row, col in run:
                        self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)

    def __animatedDrop(self, row, col, counter):
        self.__animating = True
        for iRow in range(row):
            self.__canvas.itemconfig(self.__spaces[iRow][col], fill=counter)
            self.__canvas.update()
            sleep(0.4)
            self.__canvas.itemconfig(self.__spaces[iRow][col], fill="white")
            self.__canvas.update()
            sleep(0.1)
        self.__animating = False

    def _dismissGame(self):
        self.__gameWin.destroy()
        self.__gameOver = False
        self.__gameInProgress = False

    def _dismissHelp(self):
        self.__helpWin.destroy()
        self.__helpInProgress = False

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
