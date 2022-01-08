from abc import ABC, abstractmethod
from tkinter import Tk, Frame, Button, X, Toplevel, N, S, E, W, Grid, Canvas, StringVar, Listbox, Label, END, UNITS, OptionMenu, Entry, Scale, HORIZONTAL
from game import game, gameError
from time import sleep
from players import Ai
from client import client
from aioconsole import ainput
from time import localtime, time
from asyncio import sleep as s
from asyncio import get_event_loop
from hashlib import pbkdf2_hmac


class accountError(Exception):
    pass


class hostError(Exception):
    pass


class ui(ABC):
    @abstractmethod
    def run(self):
        raise NotImplementedError


class gui(ui):
    def __init__(self, network):
        self.__network = network
        root = Tk()
        root.title("ConnectFour")
        root.configure(bg='#9DE3FD')
        frame = Frame(root)
        self.__quitFrame = Frame(root)
        frame.pack()
        self.__quitFrame.pack()
        self.__root = root
        self.__running = False
        self.__gameInProgress = False
        self.__puzzleInProgress = False
        self.__puzzleOver = True
        self.__helpCreated = False
        self.__setupCreated = False
        self.__typeChoiceCreated = False
        self.__LANSetupCreated = False
        self.__localInProgress = False
        self.__saveCreated = False
        self.__loadCreated = False
        self.__puzzleSetupCreated = False
        self.__gameOver = False
        self.__animating = False
        self.__menuFrameCreated = False
        self.__createAccountFrame = False
        self.__localGame = False
        self.__hostCreated = False
        self.__waitingForLogin = False
        self.__waitingForAddAccount = False
        self.__waitingForUpdateStats = False
        self.__waitingForLoadPuzzle = False
        self.__waitingForSavePuzzle = False
        self.__waitingForLoadGame = False
        self.__waitingForSaveGame = False
        self.__guest = False
        self.__opponent = None
        self.__opponentType = StringVar(value="Human")
        self.__waitingForHost = False
        self.__waitingForJoin = False
        self.__waitingForMove = False
        self.__client = client()
        self.__clientTurn = True
        # GROUP B SKILL: Dictionary
        self.__counters = {'RED': ('#ff0000', '#ff9999'), 'YELLOW': ('#e6e600', '#ffffb3'), 'PURPLE': ('#cc00ff', '#cc99ff'), 'PINK': ('#ff33cc', '#ff99cc'), 'ORANGE': ('#ff6600', '#ffcc99'), 'BLUE': ('#0099cc', '#66ccff'), 'GREEN': ('#33cc33', '#99ff99'), 'BLACK': ('#000000', '#808080')}
        self.__pOneColour = 'RED'
        self.__pTwoColour = 'YELLOW'
        self.__username = StringVar()
        self.__password = StringVar()
        self.__username.set("Enter Username")
        self.__password.set("Enter Password")
        # Set up the window
        Label(frame, text="Connect 4", bg='#9DE3FD', font='{Copperplate Gothic Bold} 40', pady=25, padx=45).pack(fill=X)
        Entry(frame, textvariable=self.__username).pack(fill=X)
        Entry(frame, textvariable=self.__password).pack(fill=X)
        Button(frame, text="Log In", font='{Copperplate Gothic Light} 14', command=self.__logIn).pack(fill=X)
        Label(frame, text="", bg='#9DE3FD').pack(fill=X)
        Button(frame, text="Create Account", font='{Copperplate Gothic Light} 14', command=self.__createAccount).pack(fill=X)
        Button(frame, text="Play As Guest", font='{Copperplate Gothic Light} 14', command=self.__guestLogIn).pack(fill=X)
        Label(frame, text="", bg='#9DE3FD').pack(fill=X)
        Button(self.__quitFrame, text="Quit", font='{Copperplate Gothic Light} 14', command=self.__quit).pack(fill=X)
        Label(frame, text="", bg='#9DE3FD').pack(fill=X)
        console = Listbox(frame, height=3, width=100)
        console.pack()
        self.__logInConsole = console
        self.__loginFrame = frame
        self.__toUnpack = [self.__loginFrame]

    def __unPack(self):
        # Unpack all packed frames
        while self.__toUnpack:
            self.__toUnpack.pop(0).pack_forget()
        self.__quitFrame.pack_forget()

    def __logIn(self):
        # Send a message to the server with the logIn command and the account details so that the server can verify the login
        if self.__network:
            message = {"from": self.__username.get(), "cmd": "logIn", "pword": self.__password.get()}
            get_event_loop().create_task(self.__client.send(message))
            self.__waitingForLogin = True
        else:
            # If not in network mode (could be because of exception handling in runClient method) print an error message to the console
            self.__logInConsole.insert(END, f"{self.__logInConsole.size() + 1}| server offline, play as guest...")
            if self.__logInConsole.size() > 3:
                self.__logInConsole.yview_scroll(1, UNITS)

    def __createAccount(self):
        if self.__network:
            self.__unPack()
            if not self.__createAccountFrame:
                self.__createAccountFrame = True
                frame = Frame(self.__root)
                frame.pack()
                self.__uName = StringVar()
                self.__pWord = StringVar()
                self.__confPWord = StringVar()
                self.__uName.set("Enter Username")
                self.__pWord.set("Enter Password")
                self.__confPWord.set("Confirm Password")
                # Set up the window
                Label(frame, text="Create Account", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
                Entry(frame, textvariable=self.__uName).pack(fill=X)
                Entry(frame, textvariable=self.__pWord).pack(fill=X)
                Entry(frame, textvariable=self.__confPWord).pack(fill=X)
                Button(frame, text="Create Account", command=self.__addAccount, font='{Copperplate Gothic Light} 14').pack(fill=X)
                Label(frame, text="", bg='#9DE3FD').pack(fill=X)
                console = Listbox(frame, height=3, width=100)
                console.pack()
                self.__createAccountConsole = console
                Button(frame, text="Cancel", command=self.__cancelCreate, font='{Copperplate Gothic Light} 14').pack(fill=X)
                self.__accountFrame = frame
            else:
                self.__accountFrame.pack()
            self.__quitFrame.pack()
            self.__toUnpack.append(self.__accountFrame)
        else:
            # If not in network mode (could be because of exception handling in runClient method) print an error message to the console
            self.__logInConsole.insert(END, f"{self.__logInConsole.size() + 1}| server offline, play as guest...")
            if self.__logInConsole.size() > 3:
                self.__logInConsole.yview_scroll(1, UNITS)

    def __addAccount(self):
        # Send a message to the server with the addAccount command and the account details so that the can be validated and added to the database if valid
        if self.__pWord.get() == self.__confPWord.get():
            message = {"from": self.__uName.get(), "cmd": "addAccount", "pword": self.__pWord.get()}
            get_event_loop().create_task(self.__client.send(message))
            self.__waitingForAddAccount = True
        else:
            # If the passwords don't match, notify the user and don't try to add the account to the database
            self.__createAccountConsole.insert(END, f"{self.__createAccountConsole.size() + 1}| passwords don't match, try again...")
            if self.__createAccountConsole.size() > 3:
                self.__createAccountConsole.yview_scroll(1, UNITS)

    def __cancelCreate(self):
        self.__unPack()
        self.__loginFrame.pack()
        self.__toUnpack.append(self.__loginFrame)
        self.__quitFrame.pack()

    def __guestLogIn(self):
        self.__guest = True
        self.__username.set("Enter Username")
        self.__menu()

    def __menu(self):
        self.__unPack()
        if not self.__menuFrameCreated:
            self.__menuFrameCreated = True
            frame = Frame(self.__root)
            frame.pack()
            # Set up the window
            Label(frame, text="Menu", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
            Button(frame, text="Play", command=self.__gametype, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Button(frame, text="Help", command=self.__help, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Button(frame, text="Stats", command=self.__stats, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frame, text="", bg='#9DE3FD').pack(fill=X)
            Button(frame, text="Log Out", command=self.__dismissMenu, font='{Copperplate Gothic Light} 14').pack(fill=X)
            self.__menuFrame = frame
        else:
            self.__menuFrame.pack()
        self.__quitFrame.pack()
        self.__toUnpack.append(self.__menuFrame)

    def __stats(self):
        # If the user is not playing as a guest, display the stored statistics
        if not self.__guest:
            self.__unPack()
            frame = Frame(self.__root)
            frame.pack()
            # Set up the window
            Label(frame, text=f"{self.__username.get()}'s stats:", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30').pack(fill=X)
            Label(frame, text=f"PLAYED: {self.__statsPlayed}", bg='#9DE3FD', font='{Copperplate Gothic Light} 12').pack(fill=X)
            Label(frame, text=f"WON: {self.__statsWon}", bg='#9DE3FD', font='{Copperplate Gothic Light} 12').pack(fill=X)
            Label(frame, text=f"LOST: {self.__statsLost}", bg='#9DE3FD', font='{Copperplate Gothic Light} 12').pack(fill=X)
            Label(frame, text=f"DRAWN: {self.__statsDrawn}", bg='#9DE3FD', font='{Copperplate Gothic Light} 12').pack(fill=X)
            Label(frame, text=f"PUZZLE WINS: {self.__statsPFin}", bg='#9DE3FD', font='{Copperplate Gothic Light} 12').pack(fill=X)
            Label(frame, text=f"PUZZLES MADE: {self.__statsPMade}", bg='#9DE3FD', font='{Copperplate Gothic Light} 12').pack(fill=X)
            Button(frame, text="Dismiss", command=self.__dismissStats, font='{Copperplate Gothic Light} 14').pack(fill=X)
            self.__statsFrame = frame
            self.__quitFrame.pack()
            self.__toUnpack.append(self.__statsFrame)

    def __dismissStats(self):
        self.__unPack()
        self.__menuFrame.pack()
        self.__toUnpack.append(self.__menuFrame)
        self.__quitFrame.pack()

    def __dismissMenu(self):
        self.__username.set("Enter Username")
        self.__password.set("Enter Password")
        self.__unPack()
        self.__loginFrame.pack()
        self.__toUnpack.append(self.__loginFrame)
        self.__quitFrame.pack()
        self.__setupCreated = False

    def __gametype(self):
        self.__unPack()
        if not self.__typeChoiceCreated:
            self.__typeChoiceCreated = True
            frame = Frame(self.__root)
            frame.pack()
            # Set up the window
            Label(frame, text="Play", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
            Button(frame, text="Pass and Play", command=self.__gameSetup, font='{Copperplate Gothic Light} 14').pack(fill=X)
            if self.__network:
                Button(frame, text="Play Local Online", command=self.__LANSetup, font='{Copperplate Gothic Light} 14').pack(fill=X)
                Button(frame, text="Puzzles", command=self.__puzzleSetup, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frame, text="", bg='#9DE3FD').pack(fill=X)
            Button(frame, text="Dismiss", command=self.__dismissTypeChoice, font='{Copperplate Gothic Light} 14').pack(fill=X)
            self.__gameTypeFrame = frame
        else:
            self.__gameTypeFrame.pack()
        self.__quitFrame.pack()
        self.__toUnpack.append(self.__gameTypeFrame)

    def __puzzleSetup(self):
        self.__unPack()
        self.__game = game()
        self.__puzzleSolution = None
        if not self.__puzzleSetupCreated:
            self.__puzzleSetupCreated = True
            frameUpper = Frame(self.__root)
            frameUpper.pack()
            self.__puzzleCode = StringVar()
            self.__puzzleCode.set("Enter Puzzle ID")
            # Set up the window
            Label(frameUpper, text="Puzzles", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
            Button(frameUpper, text="Create", command=self.__puzzleCreate, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Button(frameUpper, text="Random", command=self.__puzzleRandom, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frameUpper, text="", bg='#9DE3FD').pack(fill=X)
            Entry(frameUpper, textvariable=self.__puzzleCode).pack(fill=X)
            Button(frameUpper, text="Load", command=self.__puzzleLoad, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frameUpper, text="", bg='#9DE3FD').pack(fill=X)
            frameMiddle = Frame(self.__root, bg='#9DE3FD')
            frameMiddle.pack()
            self.__pOne = StringVar()
            self.__pOne.set("RED")
            self.__pTwo = StringVar()
            self.__pTwo.set("YELLOW")
            Label(frameMiddle, text=f"Player 1 colour:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=0, column=0, sticky=W)
            pOneDropDown = OptionMenu(frameMiddle, self.__pOne, *self.__counters.keys())
            pOneDropDown.configure(font='{Copperplate Gothic Light} 14')
            pOneDropDown.grid(row=0, column=1, sticky=W)
            Label(frameMiddle, text=f"Player 2 colour:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=1, column=0, sticky=W)
            pTwoDropDown = OptionMenu(frameMiddle, self.__pTwo, *self.__counters.keys())
            pTwoDropDown.configure(font='{Copperplate Gothic Light} 14')
            pTwoDropDown.grid(row=1, column=1, sticky=W)
            Label(frameMiddle, text=f"Shape:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=2, column=0, sticky=W)
            self.__shape = StringVar()
            self.__shape.set("CIRCLE")
            shapes = ["CIRCLE", "SQUARE", "TRIANGLE"]
            shapeDropDown = OptionMenu(frameMiddle, self.__shape, *shapes)
            shapeDropDown.configure(font='{Copperplate Gothic Light} 14')
            shapeDropDown.grid(row=2, column=1, sticky=W)
            Label(frameMiddle, text="Board Size:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=3, column=0, sticky=W)
            self.__boardSize = Scale(frameMiddle, from_=40, to=135, orient=HORIZONTAL)
            self.__boardSize.set(120)
            self.__boardSize.grid(row=3, column=1, sticky=W)
            frameLower = Frame(self.__root)
            frameLower.pack()
            Label(frameLower, text="", bg='#9DE3FD').pack(fill=X)
            Button(frameLower, text="Dismiss", font='{Copperplate Gothic Light} 14', command=self.__dismissPuzzleSetup).pack(fill=X)
            Label(frameLower, text="", bg='#9DE3FD').pack(fill=X)
            console = Listbox(frameLower, height=3, width=100)
            console.pack()
            self.__puzzleSetupConsole = console
            self.__puzzleSetupConsole.insert(END, f"1| enter ID to load")
            self.__puzzleUpper = frameUpper
            self.__puzzleMiddle = frameMiddle
            self.__puzzleLower = frameLower
        else:
            self.__puzzleUpper.pack()
            self.__puzzleMiddle.pack()
            self.__puzzleLower.pack()
        self.__quitFrame.pack()
        self.__toUnpack.append(self.__puzzleUpper)
        self.__toUnpack.append(self.__puzzleMiddle)
        self.__toUnpack.append(self.__puzzleLower)

    def __puzzleCreate(self):
        self.__puzzleGame(create=True)

    def __puzzleRandom(self):
        self.__puzzleCode.set("random")
        self.__puzzleLoad()

    def __puzzleLoad(self):
        # Send a message to the server with the load puzzle command and the puzzle ID so that the puzzle's information can be retrieved
        message = {"from": self.__username.get(), "cmd": "loadPuzzle", "puzzleID": self.__puzzleCode.get()}
        get_event_loop().create_task(self.__client.send(message))
        self.__waitingForLoadPuzzle = True

    def __puzzleGame(self, create=False):
        self.__unPack()
        self.__puzzleInProgress = True
        self.__pOneColour = self.__pOne.get()
        self.__pTwoColour = self.__pTwo.get()
        frameButtons = Frame(self.__root, bg='#9DE3FD')
        frameButtons.pack()
        # Set up the window
        for col in range(7):
            t = StringVar()
            t.set(col + 1)
            cmd = lambda c=col: self.__playPuzzleMove(c)
            Button(frameButtons, textvariable=t, command=cmd, font='{Copperplate Gothic Light} 14').grid(row=0, column=col, sticky=N+S+W+E)
        for col in range(7):
            Grid.columnconfigure(frameButtons, col, weight=1)
        # Create the game board using a method that allows for an easy resize of the board
        tile = self.__boardSize.get()
        counterSize = tile * 0.8
        boardWidth = 7 * tile
        boardHeight = 6 * tile
        board = Canvas(frameButtons, width=boardWidth, height=boardHeight, bg='blue')
        baseX1 = tile / 10
        baseY1 = tile / 10
        baseX2 = baseX1 + counterSize
        baseY2 = baseY1 + counterSize
        self.__spaces = [[None for _ in range(7)] for _ in range(6)]
        for row in range(6):
            for column in range(7):
                space = self.__game.getSpace(row, column)
                if space == game.PONE:
                    counterColour = self.__counters[self.__pOneColour][0]
                elif space == game.PTWO:
                    counterColour = self.__counters[self.__pTwoColour][0]
                else:
                    counterColour = "white"
                if self.__shape.get() == 'SQUARE':
                    shape = board.create_rectangle(baseX1 + (column * tile), baseY1 + (row * tile), baseX2 + (column * tile), baseY2 + (row * tile), fill=counterColour)
                elif self.__shape.get() == 'TRIANGLE':
                    shape = board.create_polygon(baseX1 + counterSize / 2 + (column * tile), baseY1 + (row * tile), baseX2 + (column * tile), baseY2 + (row * tile), baseX2 - counterSize + (column * tile), baseY2 + (row * tile), fill=counterColour)
                else:
                    shape = board.create_oval(baseX1 + (column * tile), baseY1 + (row * tile), baseX2 + (column * tile), baseY2 + (row * tile), fill=counterColour)
                self.__spaces[row][column] = shape
        board.grid(row=1, columnspan=7)
        self.__canvas = board
        frameMenu = Frame(self.__root, bg='#9DE3FD')
        frameMenu.pack()
        self.__puzzleID = StringVar()
        self.__puzzleID.set("Set Puzzle ID")
        # Add more buttons/labels below the board's canvas
        if create:
            t = "PUT IN SOME COUNTERS, ENTER A PUZZLE ID THEN SAVE"
        else:
            player = self.__pOneColour if self.__game.getPlayer == game.PONE else self.__pTwoColour
            t = f"PLAY THE BEST MOVE POSSIBLE FOR {player}"
        Label(frameMenu, text=t, font='{Copperplate Gothic Light} 14').grid(row=0, column=0, sticky=N+S+E+W)
        if create:
            self.__creative = True
            Entry(frameMenu, textvariable=self.__puzzleID).grid(row=0, column=1, sticky=N+S+W+E)
            Button(frameMenu, text="Save", command=self.__savePuzzle, font='{Copperplate Gothic Light} 14').grid(row=1, column=1, sticky=N+S+W+E)
        else:
            self.__creative = False
            Label(frameMenu, text=f"ID: {self.__loadPuzzleID}", font='{Copperplate Gothic Light} 14').grid(row=0, column=1, sticky=N+S+W+E)
            Button(frameMenu, text="Solve", command=self.__solvePuzzle, font='{Copperplate Gothic Light} 14').grid(row=1, column=1, sticky=N+S+W+E)
        Button(frameMenu, text="Undo", command=self.__undoMove, font='{Copperplate Gothic Light} 14').grid(row=1, column=0, sticky=N+S+W+E)
        frameBottom = Frame(self.__root, bg='#9DE3FD')
        frameBottom.pack()
        Button(frameBottom, text="Exit", command=self.__exitPuzzle, font='{Copperplate Gothic Light} 14').pack()
        console = Listbox(frameBottom, height=3, width=60)
        console.pack()
        self.__gameConsole = console
        self.__puzzleOver = False
        self.__quitFrame.pack()
        self.__pgButtons = frameButtons
        self.__pgMenu = frameMenu
        self.__pgBottom = frameBottom
        self.__toUnpack.append(self.__pgButtons)
        self.__toUnpack.append(self.__pgMenu)
        self.__toUnpack.append(self.__pgBottom)

    def __playPuzzleMove(self, col):
        if self.__animating:
            # If there is a counter falling, tell the user to wait
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| please wait...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)
        elif not self.__puzzleOver:
            # Exception Handling: If the column is full report the error to the user without crashing
            try:
                counter = self.__counters[self.__pOneColour][0] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour][0]
                row = 5 - self.__game.play(col + 1)
                # Animate the counter being played
                self.__animatedDrop(row, col, counter)
                self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)
            except gameError as e:
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {e}")
                if self.__gameConsole.size() > 3:
                    self.__gameConsole.yview_scroll(1, UNITS)
            if not self.__creative:
                self.__puzzleOver = True
                if col == self.__puzzleSolution:
                    self.__puzzleWin()
                else:
                    self.__puzzleLose()
        elif self.__puzzleOver:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| undo move or exit...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)

    def __puzzleWin(self):
        solvedWin = Toplevel(self.__root)
        solvedWin.title("Solved")
        solvedWin.configure(bg='#9DE3FD')
        frame = Frame(solvedWin)
        frame.pack()
        self.__solvedWin = solvedWin
        # Set up the window
        Label(frame, text=f"CORRECT MOVE!", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
        Label(frame, text="WELL DONE!", bg='#9DE3FD', font='{Copperplate Gothic Light} 14', pady=5, padx=10).pack(fill=X)
        Button(frame, text="Exit", command=self.__exitSolved, font='{Copperplate Gothic Light} 14').pack(fill=X)
        # Send a message to the server so with the stats update command and the new value so that the server can update the database
        if not self.__guest and self.__network:
            self.__statsPFin += 1
            message = {"from": self.__username.get(), "cmd": "updatePFin", "pFin": self.__statsPFin}
            get_event_loop().create_task(self.__client.send(message))
            self.__waitingForUpdateStats = True

    def __puzzleLose(self):
        loseWin = Toplevel(self.__root)
        loseWin.title("Solved")
        loseWin.configure(bg='#9DE3FD')
        frame = Frame(loseWin)
        frame.pack()
        self.__loseWin = loseWin
        # Set up the window
        Label(frame, text=f"INCORRECT MOVE!", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
        Label(frame, text="UNDO OR EXIT", bg='#9DE3FD', font='{Copperplate Gothic Light} 14', pady=5, padx=10).pack(fill=X)
        Button(frame, text="Exit", command=self.__exitLost, font='{Copperplate Gothic Light} 14').pack(fill=X)

    def __exitLost(self):
        self.__loseWin.destroy()

    def __exitSolved(self):
        self.__solvedWin.destroy()

    def __savePuzzle(self):
        solution = self.__solvePuzzle(saving=True)
        ID = self.__puzzleID.get()
        moves = self.__game.getMoves
        # Send a message to the server with the savePuzzle command, the puzzle ID, ordered move list and solution so that it can be saved to the database
        if self.__network:
            message = {"from": self.__username.get(), "cmd": "savePuzzle", "puzzleID": ID, "puzzleMoves": moves, "puzzleSolution": solution}
            get_event_loop().create_task(self.__client.send(message))
            self.__waitingForSavePuzzle = True
        else:
            # If not in network mode (could be because of exception handling in runClient method) print an error message to the console
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| server offline...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)

    def __solvePuzzle(self, saving=False):
        if not self.__puzzleOver:
            if self.__puzzleSolution is not None:
                column = self.__puzzleSolution
            else:
                # Use the Hard AI to find the best move
                computer = Ai("Hard AI")
                column = computer.getColumn(self.__game.Board, self.__game.getPlayer)
            if saving:
                return column
            else:
                counter = self.__counters[self.__pOneColour][0] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour][0]
                row = 5 - self.__game.play(column + 1)
                # Animate the counter played
                self.__animatedDrop(row, column, counter)
                self.__canvas.itemconfig(self.__spaces[row][column], fill=counter)
                counter = self.__counters[self.__pOneColour][1] if not self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour][1]
                self.__canvas.itemconfig(self.__spaces[row][column], fill=counter)
                self.__puzzleOver = True

    def __exitPuzzle(self):
        self.__puzzleInProgress = False
        self.__unPack()
        self.__gameTypeFrame.pack()
        self.__toUnpack.append(self.__gameTypeFrame)
        self.__quitFrame.pack()

    def __dismissPuzzleSetup(self):
        self.__unPack()
        self.__gameTypeFrame.pack()
        self.__toUnpack.append(self.__gameTypeFrame)
        self.__quitFrame.pack()

    def __dismissTypeChoice(self):
        self.__unPack()
        self.__menuFrame.pack()
        self.__toUnpack.append(self.__menuFrame)
        self.__quitFrame.pack()

    def __LANSetup(self):
        self.__unPack()
        if not self.__LANSetupCreated:
            self.__firstTurn = StringVar()
            self.__firstTurn.set("opp")
            self.__LANSetupCreated = True
            frameUpper = Frame(self.__root)
            frameUpper.pack()
            self.__joinCode = StringVar()
            self.__joinCode.set("Enter Join Code")
            # Create a client code to uniquely identify the client
            timeStamp = localtime(time())
            clientCode = str(timeStamp[3])
            clientCode += str(timeStamp[4])
            clientCode += str(timeStamp[5])
            self.__clientCode = clientCode
            # Set up the window
            Label(frameUpper, text=f"Local Play", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
            Button(frameUpper, text="Host", command=self.__hostGame, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frameUpper, text="", bg='#9DE3FD').pack(fill=X)
            Entry(frameUpper, textvariable=self.__joinCode).pack(fill=X)
            Button(frameUpper, text="Join", command=self.__attemptJoin, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frameUpper, text="", bg='#9DE3FD').pack(fill=X)
            frameMiddle = Frame(self.__root, bg='#9DE3FD')
            frameMiddle.pack()
            self.__pOne = StringVar()
            self.__pOne.set("RED")
            self.__pTwo = StringVar()
            self.__pTwo.set("YELLOW")
            Label(frameMiddle, text=f"Player 1 colour:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=0, column=0, sticky=W)
            pOneDropDown = OptionMenu(frameMiddle, self.__pOne, *self.__counters.keys())
            pOneDropDown.configure(font='{Copperplate Gothic Light} 14')
            pOneDropDown.grid(row=0, column=1, sticky=W)
            Label(frameMiddle, text=f"Player 2 colour:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=1, column=0, sticky=W)
            pTwoDropDown = OptionMenu(frameMiddle, self.__pTwo, *self.__counters.keys())
            pTwoDropDown.configure(font='{Copperplate Gothic Light} 14')
            pTwoDropDown.grid(row=1, column=1, sticky=W)
            Label(frameMiddle, text=f"Shape:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=2, column=0, sticky=W)
            self.__shape = StringVar()
            self.__shape.set("CIRCLE")
            shapes = ["CIRCLE", "SQUARE", "TRIANGLE"]
            shapeDropDown = OptionMenu(frameMiddle, self.__shape, *shapes)
            shapeDropDown.configure(font='{Copperplate Gothic Light} 14')
            shapeDropDown.grid(row=2, column=1, sticky=W)
            Label(frameMiddle, text="Board Size:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=3, column=0, sticky=W)
            self.__boardSize = Scale(frameMiddle, from_=40, to=135, orient=HORIZONTAL)
            self.__boardSize.set(120)
            self.__boardSize.grid(row=3, column=1, sticky=W)
            frameLower = Frame(self.__root)
            frameLower.pack()
            Label(frameLower, text="", bg='#9DE3FD').pack(fill=X)
            Button(frameLower, text="Back", command=self.__dismissLANSetup, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frameLower, text="", bg='#9DE3FD').pack(fill=X)
            console = Listbox(frameLower, height=3, width=100)
            console.pack()
            self.__LANConsole = console
            self.__LANSetupUpper = frameUpper
            self.__LANSetupMiddle = frameMiddle
            self.__LANSetupLower = frameLower
        else:
            self.__LANSetupUpper.pack()
            self.__LANSetupMiddle.pack()
            self.__LANSetupLower.pack()
        self.__quitFrame.pack()
        self.__toUnpack.append(self.__LANSetupUpper)
        self.__toUnpack.append(self.__LANSetupMiddle)
        self.__toUnpack.append(self.__LANSetupLower)

    def __hostGame(self):
        self.__unPack()
        self.__localInProgress = True
        frame = Frame(self.__root)
        frame.pack()
        # Set up the window
        Label(frame, text=f"Host Game", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
        Label(frame, text=f"JOIN CODE: {self.__clientCode}", bg='#9DE3FD', font='{Copperplate Gothic Light} 14', pady=5, padx=10).pack(fill=X)
        Label(frame, text="WAITING FOR OPPONENT...", bg='#9DE3FD', font='{Copperplate Gothic Light} 14', pady=5, padx=10).pack(fill=X)
        Label(frame, text="", bg='#9DE3FD').pack(fill=X)
        Button(frame, text="Back", command=self.__dismissHost, font='{Copperplate Gothic Light} 14').pack(fill=X)
        # Send a message to the server with the host command so that this user can be added to the set of hosts
        message = {"from": self.__clientCode, "cmd": "gHost"}
        get_event_loop().create_task(self.__client.send(message))
        self.__waitingForJoin = True
        self.__toUnpack.append(frame)
        self.__quitFrame.pack()

    def __dismissHost(self):
        # Send a message to the server with the cancel host command so that this user can be removed from the set of hosts
        message = {"from": self.__clientCode, "cmd": "cHost"}
        get_event_loop().create_task(self.__client.send(message))
        self.__waitingForJoin = False
        self.__unPack()
        self.__LANSetupUpper.pack()
        self.__LANSetupMiddle.pack()
        self.__LANSetupLower.pack()
        self.__toUnpack.append(self.__LANSetupUpper)
        self.__toUnpack.append(self.__LANSetupMiddle)
        self.__toUnpack.append(self.__LANSetupLower)
        self.__quitFrame.pack()

    def __attemptJoin(self):
        # Send a message to the server with the join command and the host's name
        if not self.__localInProgress and not self.__gameInProgress:
            self.__localInProgress = True
            message = {"joinCode": self.__joinCode.get(), "from": self.__clientCode, "cmd": "gJoin"}
            get_event_loop().create_task(self.__client.send(message))
            self.__waitingForHost = True

    def __dismissLANSetup(self):
        self.__unPack()
        self.__gameTypeFrame.pack()
        self.__toUnpack.append(self.__gameTypeFrame)
        self.__quitFrame.pack()

    def __gameSetup(self):
        self.__unPack()
        self.__opponent = None
        frameUpper = Frame(self.__root)
        frameUpper.pack()
        # Set up the window
        Label(frameUpper, text=f"Play", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
        self.__firstTurn = StringVar()
        self.__firstTurn.set("Choose First Player")
        if not self.__guest:
            firstTurnDropDown = OptionMenu(frameUpper, self.__firstTurn, *[self.__username.get(), "Guest"])
            firstTurnDropDown.configure(font='{Copperplate Gothic Light} 14')
            firstTurnDropDown.pack(fill=X)
        frameMiddle = Frame(self.__root, bg='#9DE3FD')
        frameMiddle.pack()
        Label(frameMiddle, text="Choose Opponent:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=0, column=0, sticky=W)
        options = ["Human", "Practice AI", "Easy AI", "Medium AI", "Hard AI"]
        self.__opponentType.set("Human")
        opponentDropDown = OptionMenu(frameMiddle, self.__opponentType, *options)
        opponentDropDown.configure(font='{Copperplate Gothic Light} 14')
        opponentDropDown.grid(row=0, column=1, sticky=W)
        playerOne = "Player 1" if self.__guest else f"{self.__username.get()}"
        Label(frameMiddle, text=f"{playerOne} colour:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=1, column=0, sticky=W)
        playerTwo = "Player 2" if self.__guest else f"Opponent"
        Label(frameMiddle, text=f"{playerTwo} colour:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=2, column=0, sticky=W)
        self.__pOne = StringVar()
        self.__pOne.set("RED")
        self.__pTwo = StringVar()
        self.__pTwo.set("YELLOW")
        pOneDropDown = OptionMenu(frameMiddle, self.__pOne, *self.__counters.keys())
        pOneDropDown.configure(font='{Copperplate Gothic Light} 14')
        pOneDropDown.grid(row=1, column=1, sticky=W)
        pTwoDropDown = OptionMenu(frameMiddle, self.__pTwo, *self.__counters.keys())
        pTwoDropDown.configure(font='{Copperplate Gothic Light} 14')
        pTwoDropDown.grid(row=2, column=1, sticky=W)
        Label(frameMiddle, text="Shape:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=3, column=0, sticky=W)
        self.__shape = StringVar()
        self.__shape.set("CIRCLE")
        shapes = ["CIRCLE", "SQUARE", "TRIANGLE"]
        shapeDropDown = OptionMenu(frameMiddle, self.__shape, *shapes)
        shapeDropDown.configure(font='{Copperplate Gothic Light} 14')
        shapeDropDown.grid(row=3, column=1, sticky=W)
        Label(frameMiddle, text="Board Size:", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').grid(row=4, column=0, sticky=W)
        self.__boardSize = Scale(frameMiddle, from_=40, to=135, orient=HORIZONTAL)
        self.__boardSize.set(120)
        self.__boardSize.grid(row=4, column=1, sticky=W)
        frameLower = Frame(self.__root)
        frameLower.pack()
        Label(frameLower, text="", bg='#9DE3FD').pack(fill=X)
        Button(frameLower, text="Play", command=self.__play, font='{Copperplate Gothic Light} 14').pack(fill=X)
        Button(frameLower, text="Load", command=self.__load, font='{Copperplate Gothic Light} 14').pack(fill=X)
        Label(frameLower, text="", bg='#9DE3FD').pack(fill=X)
        Button(frameLower, text="Back", command=self.__dismissSetup, font='{Copperplate Gothic Light} 14').pack(fill=X)
        self.__gameUpper = frameUpper
        self.__gameMiddle = frameMiddle
        self.__gameLower = frameLower
        self.__quitFrame.pack()
        self.__toUnpack.append(self.__gameUpper)
        self.__toUnpack.append(self.__gameMiddle)
        self.__toUnpack.append(self.__gameLower)
        self.__game = game()

    def __dismissSetup(self):
        self.__unPack()
        self.__gameTypeFrame.pack()
        self.__toUnpack.append(self.__gameTypeFrame)
        self.__quitFrame.pack()

    def __load(self):
        self.__unPack()
        if not self.__loadCreated:
            self.__loadCreated = True
            frame = Frame(self.__root)
            frame.pack()
            # Set up the window
            Label(frame, text=f"Load", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
            self.__loadName = StringVar()
            self.__loadName.set("Enter Game Name")
            Label(frame, text=f"ENTER GAME NAME BELOW", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').pack(fill=X)
            Entry(frame, textvariable=self.__loadName).pack(fill=X)
            Button(frame, text="Load", command=self.__loadGame, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frame, text="", bg='#9DE3FD').pack(fill=X)
            Button(frame, text="Cancel", command=self.__cancelLoad, font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frame, text="", bg='#9DE3FD').pack(fill=X)
            console = Listbox(frame, height=3, width=100)
            console.pack()
            self.__loadConsole = console
            self.__loadFrame = frame
        else:
            self.__loadFrame.pack()
        self.__quitFrame.pack()
        self.__toUnpack.append(self.__loadFrame)

    def __loadGame(self):
        # Send a message to the server with the load game command and the game name so that the game's information can be retrieved
        username = "Enter Username" if self.__guest else self.__username.get()
        if self.__network:
            message = {"from": username, "cmd": "loadGame", "gameName": self.__loadName.get()}
            get_event_loop().create_task(self.__client.send(message))
            self.__waitingForLoadGame = True
        else:
            # If not in network mode (could be because of exception handling in runClient method) print an error message to the console
            self.__loadConsole.insert(END, f"{self.__loadConsole.size() + 1}| server offline...")
            if self.__loadConsole.size() > 3:
                self.__loadConsole.yview_scroll(1, UNITS)

    def __cancelLoad(self):
        self.__unPack()
        self.__gameUpper.pack()
        self.__gameMiddle.pack()
        self.__gameLower.pack()
        self.__toUnpack.append(self.__gameUpper)
        self.__toUnpack.append(self.__gameMiddle)
        self.__toUnpack.append(self.__gameLower)
        self.__quitFrame.pack()

    def __help(self):
        self.__unPack()
        if not self.__helpCreated:
            self.__helpCreated = True
            frame = Frame(self.__root)
            frame.pack()
            # Set up the window
            Label(frame, text=f"Help", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
            Label(frame, text="Take it in turns to  drop counters into the board.", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frame, text="First person to get a vertical, horizontal or diagonal run of four counters wins!", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frame, text="If the board fills and nobody has a run of four yet then the game is drawn.", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').pack(fill=X)
            Label(frame, text="", bg='#9DE3FD').pack(fill=X)
            Button(frame, text="Dismiss", command=self.__dismissHelp, font='{Copperplate Gothic Light} 14').pack(fill=X)
            self.__helpFrame = frame
        else:
            self.__helpFrame.pack()
        self.__quitFrame.pack()
        self.__toUnpack.append(self.__helpFrame)

    def __play(self):
        self.__unPack()
        if not self.__setupCreated:
            self.__game = game()
        if self.__opponentType.get() != "Human":
            self.__opponent = Ai(self.__opponentType.get())
        self.__gameInProgress = True
        self.__pOneColour = self.__pOne.get()
        self.__pTwoColour = self.__pTwo.get()
        frameButtons = Frame(self.__root, bg='#9DE3FD')
        frameButtons.pack()
        # Set up the window
        for col in range(7):
            t = StringVar()
            t.set(col + 1)
            cmd = lambda c=col: self.__attemptPlay(c)
            Button(frameButtons, textvariable=t, command=cmd, font='{Copperplate Gothic Light} 14').grid(row=0, column=col, sticky=E + W)
        for col in range(7):
            Grid.columnconfigure(frameButtons, col, weight=1)
        # Create the game board using a method that allows for an easy resize of the board
        tile = self.__boardSize.get()
        counterSize = tile * 0.8
        boardWidth = 7 * tile
        boardHeight = 6 * tile
        board = Canvas(frameButtons, width=boardWidth, height=boardHeight, bg='blue')
        baseX1 = tile / 10
        baseY1 = tile / 10
        baseX2 = baseX1 + counterSize
        baseY2 = baseY1 + counterSize
        self.__spaces = [[None for _ in range(7)] for _ in range(6)]
        for row in range(6):
            for column in range(7):
                space = self.__game.getSpace(row, column)
                if space == game.PONE:
                    counterColour = self.__counters[self.__pOneColour][0]
                elif space == game.PTWO:
                    counterColour = self.__counters[self.__pTwoColour][0]
                else:
                    counterColour = "white"
                if self.__shape.get() == 'SQUARE':
                    shape = board.create_rectangle(baseX1 + (column * tile), baseY1 + (row * tile), baseX2 + (column * tile), baseY2 + (row * tile), fill=counterColour)
                elif self.__shape.get() == 'TRIANGLE':
                    shape = board.create_polygon(baseX1 + counterSize / 2 + (column * tile), baseY1 + (row * tile), baseX2 + (column * tile), baseY2 + (row * tile), baseX2 - counterSize + (column * tile), baseY2 + (row * tile), fill=counterColour)
                else:
                    shape = board.create_oval(baseX1 + (column * tile), baseY1 + (row * tile), baseX2 + (column * tile), baseY2 + (row * tile), fill=counterColour)
                self.__spaces[row][column] = shape
        board.grid(row=1, columnspan=7)
        self.__canvas = board
        frameMenu = Frame(self.__root, bg='#9DE3FD')
        frameMenu.pack()
        self.__playerTurn = StringVar()
        counter = self.__pOneColour if self.__game.getPlayer == game.PONE else self.__pTwoColour
        textColour = self.__counters[self.__pOneColour][0] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour][0]
        # Add more buttons/labels below the board's canvas
        if self.__opponentType.get() == "Human" and not self.__localGame:
            self.__playerTurn.set(f'{counter} TO PLAY\nCHOOSE COLUMN')
        elif self.__opponentType.get() == "Human" and self.__localGame:
            if self.__clientTurn:
                self.__playerTurn.set('YOUR TURN\nCHOOSE COLUMN')
            else:
                self.__playerTurn.set("OPPONENT'S TURN\nPLEASE WAIT")
        else:
            self.__playerTurn.set('YOUR TURN\nCHOOSE COLUMN')
        self.__playerTurnLabel = Label(frameMenu, textvariable=self.__playerTurn, fg=textColour, font='{Copperplate Gothic Light} 14')
        self.__playerTurnLabel.grid(row=0, column=0, sticky=N+S+E+W)
        Button(frameMenu, text="Dismiss", command=self.__dismissGame, font='{Copperplate Gothic Light} 14').grid(row=1, column=0, sticky=N+S+E+W)
        if not self.__localGame:
            Button(frameMenu, text="Undo", command=self.__undoMove, font='{Copperplate Gothic Light} 14').grid(row=0, column=1, sticky=N+S+E+W)
            Button(frameMenu, text="Save and Exit", command=self.__saveAndExit, font='{Copperplate Gothic Light} 14').grid(row=1, column=1, sticky=N+S+E+W)
        frameConsole = Frame(self.__root, bg='#9DE3FD')
        frameConsole.pack()
        console = Listbox(frameConsole, height=3, width=60)
        console.pack()
        self.__gameConsole = console
        if self.__localGame:
            self.__gameConsole.insert(END, f"1| local game (vs {self.__opponent})")
        else:
            self.__gameConsole.insert(END, f"1| game against {self.__opponentType.get()}")
        self.__quitFrame.pack()
        self.__ggButtons = frameButtons
        self.__ggMenu = frameMenu
        self.__ggConsole = frameConsole
        self.__toUnpack.append(self.__ggButtons)
        self.__toUnpack.append(self.__ggMenu)
        self.__toUnpack.append(self.__ggConsole)

    def __saveAndExit(self):
        if self.__animating:
            # If there is a counter falling, tell the user to wait
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| please wait...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)
        else:
            self.__unPack()
            if not self.__saveCreated:
                self.__saveCreated = True
                frame = Frame(self.__root)
                frame.pack()
                self.__gameName = StringVar()
                self.__gameName.set("Enter Game Name")
                # Set up the window
                Label(frame, text=f"Save", bg='#9DE3FD', font='{Copperplate Gothic Bold} 30', pady=25, padx=45).pack(fill=X)
                Label(frame, text=f"ENTER GAME NAME BELOW", bg='#9DE3FD', font='{Copperplate Gothic Light} 14').pack(fill=X)
                Entry(frame, textvariable=self.__gameName).pack(fill=X)
                Button(frame, text="Save", command=self.__saveGame, font='{Copperplate Gothic Light} 14').pack(fill=X)
                Label(frame, text="", bg='#9DE3FD').pack(fill=X)
                Button(frame, text="Cancel", command=self.__cancelSave, font='{Copperplate Gothic Light} 14').pack(fill=X)
                Label(frame, text="", bg='#9DE3FD').pack(fill=X)
                console = Listbox(frame, height=3, width=100)
                console.pack()
                self.__saveConsole = console
                self.__saveAndExitFrame = frame
            else:
                self.__saveAndExitFrame.pack()
            self.__quitFrame.pack()
            self.__toUnpack.append(self.__saveAndExitFrame)

    def __saveGame(self):
        # Send a message to the server with the saveGame command, the game name and the ordered move list so that it can be saved to the database
        username = "Enter Username" if self.__guest else self.__username.get()
        moves = self.__game.getMoves
        if self.__network:
            message = {"from": username, "cmd": "saveGame", "gameName": self.__gameName.get(), "gameMoves": moves, "opponent": self.__opponentType.get()}
            get_event_loop().create_task(self.__client.send(message))
            self.__waitingForSaveGame = True
        else:
            # If not in network mode (could be because of exception handling in runClient method) print an error message to the console
            self.__saveConsole.insert(END, f"{self.__saveConsole.size() + 1}| server offline...")
            if self.__saveConsole.size() > 3:
                self.__saveConsole.yview_scroll(1, UNITS)

    def __cancelSave(self):
        self.__unPack()
        self.__ggButtons.pack()
        self.__ggMenu.pack()
        self.__ggConsole.pack()
        self.__toUnpack.append(self.__ggButtons)
        self.__toUnpack.append(self.__ggMenu)
        self.__toUnpack.append(self.__ggConsole)
        self.__quitFrame.pack()

    def __undoMove(self):
        if not self.__gameOver and self.__opponentType.get() == "Human":
            # If it is a pass and play against a human and the game isn't finished, undo the last move
            try:
                # Exception Handling: If there is no move to undo, report this without crashing, otherwise, undo the last move
                row, col = self.__game.undo()
                self.__canvas.itemconfig(self.__spaces[row][col], fill="white")
                if not self.__puzzleInProgress:
                    counter = self.__pOneColour if self.__game.getPlayer == game.PONE else self.__pTwoColour
                    textColour = self.__counters[self.__pOneColour][0] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour][0]
                    self.__playerTurnLabel.config(fg=textColour)
                    self.__playerTurn.set(f'{counter} TO PLAY\nCHOOSE COLUMN')
                else:
                    self.__puzzleOver = False
            except gameError as e:
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {e}")
                if self.__gameConsole.size() > 3:
                    self.__gameConsole.yview_scroll(1, UNITS)
        else:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| undo unavailable")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)

    def __attemptPlay(self, col):
        if self.__clientTurn:
            # If it is not the clients turn (it is opponents turn on networked game) tell the user to wait
            self.__playMove(col)
        else:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| please wait...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)

    def __playMove(self, col):
        if self.__animating:
            # If there is a counter falling, tell the user to wait
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| please wait...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)
        elif not self.__game.getWinner:
            # Exception Handling: If the column is full, report the error to the user without crashing
            try:
                counter = self.__counters[self.__pOneColour][0] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour][0]
                row = 5 - self.__game.play(col + 1)
                # If playing a networked game, send a message to the server with the move command, the column played in and the opponent's name, to be forwarded to the opponent
                if self.__localGame and self.__clientTurn:
                    message = {"to": self.__opponent, "from": self.__clientCode, "cmd": "move", "col": col}
                    get_event_loop().create_task(self.__client.send(message))
                # Animate the played counter
                self.__animatedDrop(row, col, counter)
                self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)
                counter = self.__pOneColour if self.__game.getPlayer == game.PONE else self.__pTwoColour
                textColour = self.__counters[self.__pOneColour][0] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour][0]
                self.__playerTurnLabel.config(fg=textColour)
                # Update the turn label
                if self.__opponentType.get() == "Human" and not self.__localGame:
                    self.__playerTurn.set(f'{counter} TO PLAY\nCHOOSE COLUMN')
                elif self.__opponentType.get() == "Human" and self.__localGame:
                    self.__clientTurn = True if not self.__clientTurn else False
                    if self.__clientTurn:
                        self.__playerTurn.set(f'YOUR TURN\nCHOOSE COLUMN')
                    else:
                        self.__playerTurn.set(f'OPPONENTS TURN\nPLEASE WAIT')
                else:
                    self.__playerTurn.set(f'OPPONENTS TURN\nPLEASE WAIT')
            except gameError as e:
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {e}")
                if self.__gameConsole.size() > 3:
                    self.__gameConsole.yview_scroll(1, UNITS)
            if self.__network:
                if self.__clientTurn:
                    self.__waitingForMove = False
                else:
                    self.__waitingForMove = True
            self.__checkIfWon()
            self.__canvas.update()
            if self.__opponentType.get() != "Human" and not self.__game.getWinner:
                # If playing against an AI, play the AI's turn
                counter = self.__counters[self.__pOneColour][0] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour][0]
                col = self.__opponent.getColumn(self.__game.Board, self.__game.getPlayer)
                row = 5 - self.__game.play(col + 1)
                self.__animatedDrop(row, col, counter)
                self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)
                textColour = self.__counters[self.__pOneColour][0] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour][0]
                self.__playerTurnLabel.config(fg=textColour)
                self.__playerTurn.set(f'YOUR TURN\nCHOOSE COLUMN')
                self.__checkIfWon()

    def __checkIfWon(self):
        # Check if the game is over
        winningPlayer, run = self.__game.getRun
        if winningPlayer:
            self.__gameOver = True
            if self.__game.getWinner != "Draw":
                winner = self.__pOneColour if self.__game.getWinner == game.PONE else self.__pTwoColour
                textColour = self.__counters[winner][0]
                self.__playerTurnLabel.config(fg=textColour)
                # Update the turn label with the win message
                if self.__opponentType.get() == "Human" and not self.__localGame:
                    self.__playerTurn.set(f'{winner} HAS WON\nCONGRATULATIONS!')
                elif not self.__localGame:
                    winner = 'YOU' if self.__game.getWinner == game.PONE else 'OPPONENT'
                    self.__playerTurn.set(f'{winner} WON\nGOOD GAME!')
                else:
                    winner = 'YOU' if self.__game.getWinner == game.PONE and self.__firstTurn.get() == self.__username.get() else 'OPPONENT'
                    self.__playerTurn.set(f'{winner} WON\nGOOD GAME!')
            else:
                textColour = "#000000"
                self.__playerTurnLabel.config(fg=textColour)
                self.__playerTurn.set(f'THE GAME WAS DRAWN')
            if self.__localGame:
                self.__waitingForMove = False
                self.__localGame = False
            if run:
                # Highlight the winning run of counters
                counter = self.__counters[self.__pOneColour][1] if winningPlayer == game.PONE else self.__counters[self.__pTwoColour][1]
                for row, col in run:
                    self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)
            if not self.__guest:
                # Update locally stored statistics
                self.__statsPlayed += 1
                if self.__game.getWinner == "Draw":
                    self.__statsDrawn += 1
                elif self.__game.getWinner == game.PONE and self.__firstTurn.get() == self.__username.get():
                    self.__statsWon += 1
                else:
                    self.__statsLost += 1
                # Send a message to the server with the update stats command and the new values so that the server can update the database
                if self.__network:
                    message = {"from": self.__username.get(), "cmd": "updateGameStats", "played": self.__statsPlayed, "won": self.__statsWon, "lost": self.__statsLost, "drawn": self.__statsDrawn}
                    get_event_loop().create_task(self.__client.send(message))
                    self.__waitingForUpdateStats = True

    def __animatedDrop(self, row, col, counter):
        self.__animating = True
        # Fill then unfill each counter slot from the top of the column to the last empty slot with the colour of the counter being played
        for iRow in range(row):
            self.__canvas.itemconfig(self.__spaces[iRow][col], fill=counter)
            self.__canvas.update()
            sleep(0.2)
            self.__canvas.itemconfig(self.__spaces[iRow][col], fill="white")
            self.__canvas.update()
            sleep(0.02)
        self.__animating = False

    def __dismissGame(self):
        # Send a message to the server with the endGame command so that the opponent can be notified that this user has left
        if self.__localGame:
            message = {"from": self.__clientCode, "to": self.__opponent, "cmd": "endGame"}
            get_event_loop().create_task(self.__client.send(message))
            self.__waitingForMove = False
            self.__localGame = False
            self.__clientTurn = True
        self.__unPack()
        self.__gameTypeFrame.pack()
        self.__toUnpack.append(self.__gameTypeFrame)
        self.__quitFrame.pack()
        self.__gameOver = False
        self.__gameInProgress = False

    def __dismissHelp(self):
        self.__unPack()
        self.__menuFrame.pack()
        self.__toUnpack.append(self.__menuFrame)
        self.__quitFrame.pack()

    def __quit(self):
        self.__root.quit()
        self.__running = False

    async def runClient(self):
        # Exception Handling: If the user cannot connect to the server, report this error without crashing and set the network flag to False
        try:
            await self.__client.run()
        except ConnectionRefusedError:
            self.__network = False
            self.__logInConsole.insert(END, f"{self.__logInConsole.size() + 1}| server offline, play as guest...")
            if self.__logInConsole.size() > 3:
                self.__logInConsole.yview_scroll(1, UNITS)

    async def run(self):
        self.__running = True
        while self.__running:
            await s(0.1)
            self.__root.update()
            if self.__waitingForHost:
                # While the joiner doesn't have an opponent, wait for the host to reply with an accept message
                while not self.__opponent and self.__waitingForHost:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "match" and str(message.get("to", None)) == str(self.__clientCode):
                            # Once the client receives confirmation from the host, set up the game
                            self.__opponent = message.get("from", None)
                            self.__waitingForHost = False
                            self.__localInProgress = False
                            self.__localGame = True
                            if self.__clientCode > self.__opponent:
                                self.__clientTurn = True
                                self.__waitingForMove = False
                                if not self.__guest:
                                    self.__firstTurn.set(self.__username.get())
                            else:
                                self.__clientTurn = False
                                self.__waitingForMove = True
                            self.__play()
                        # If the host is not in the server's host set report this to the user
                        elif cmd == "hnf" and str(message.get("to", None)) == str(self.__clientCode):
                            self.__waitingForHost = False
                            self.__localInProgress = False
                            self.__LANConsole.insert(END, f"{self.__LANConsole.size() + 1}| host not found...")
                            if self.__LANConsole.size() > 3:
                                self.__LANConsole.yview_scroll(1, UNITS)
            elif self.__waitingForJoin:
                # While host doesn't have an opponent, wait for someone to request to join
                while not self.__opponent:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "gJoin" and message.get("joinCode", None) == self.__clientCode:
                            # Once the host receives a join request, respond with a match message and set up the game
                            self.__opponent = message.get("from", None)
                            await self.__client.send({"to": self.__opponent, "from": self.__clientCode, "cmd": "match"})
                            self.__waitingForJoin = False
                            self.__localInProgress = False
                            self.__localGame = True
                            if self.__clientCode > self.__opponent:
                                self.__clientTurn = True
                                self.__waitingForMove = False
                                if not self.__guest:
                                    self.__firstTurn.set(self.__username.get())
                            else:
                                self.__clientTurn = False
                                self.__waitingForMove = True
                            self.__play()
            elif self.__waitingForMove:
                # If waiting for move, wait for a move message from the opponent and play the move
                while self.__waitingForMove:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "move" and message.get("to", None) == self.__clientCode:
                            # If the client receives a move message addressed to itself, play the move sent with the message
                            self.__playMove(message.get("col", None))
                        elif cmd == "endGame" and message.get("to", None) == self.__clientCode:
                            # If the client receives an endgame message addressed to itself. notify the user
                            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| opponent has quit...")
                            if self.__gameConsole.size() > 3:
                                self.__gameConsole.yview_scroll(1, UNITS)
            elif self.__waitingForLogin:
                # If waiting to log in, wait for the server to respond with the account's information
                while self.__waitingForLogin:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "logIn" and message.get("to", None) == self.__username.get():
                            # Exception Handling: If the username or password is incorrect, report the error without crashing
                            try:
                                if message.get("accountInfo", None) is not None:
                                    username, key, hashedPassword, self.__statsPlayed, self.__statsWon, self.__statsLost, self.__statsDrawn, self.__statsPFin, self.__statsPMade = message.get("accountInfo", None)
                                    salt = key.to_bytes(4, byteorder="big")
                                    password = pbkdf2_hmac('sha256', self.__password.get().encode('utf-8'), salt, 100000)
                                    if str(password) == str(hashedPassword):
                                        # If the password is correct, go to the menu, logged in
                                        self.__password.set("")
                                        self.__guest = False
                                        self.__menu()
                                        self.__waitingForLogin = False
                                    else:
                                        # If the password is incorrect, reset the statistics and raise an accountError
                                        username, key, hashedPassword, self.__statsPlayed, self.__statsWon, self.__statsLost, self.__statsDrawn, self.__statsPFin, self.__statsPMade = None, None, None, 0, 0, 0, 0, 0, 0
                                        self.__password.set("")
                                        self.__username.set("")
                                        self.__waitingForLogin = False
                                        raise accountError
                                else:
                                    self.__waitingForLogin = False
                                    raise accountError
                            except accountError:
                                # If the username or password is incorrect, notify the user
                                self.__logInConsole.insert(END, f"{self.__logInConsole.size() + 1}| username or password incorrect...")
                                if self.__logInConsole.size() > 3:
                                    self.__logInConsole.yview_scroll(1, UNITS)
            elif self.__waitingForAddAccount:
                # If waiting for a new account to be added to the database, wait for a response from the server to determine whether the addition was valid or not
                while self.__waitingForAddAccount:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "addAccount" and message.get("to", None) == self.__uName.get():
                            # Notify the user as to whether the account creation was successful or not
                            if message.get("valid", False):
                                self.__cancelCreate()
                                self.__logInConsole.insert(END, f"{self.__logInConsole.size() + 1}| account created...")
                                if self.__logInConsole.size() > 3:
                                    self.__logInConsole.yview_scroll(1, UNITS)
                                self.__waitingForAddAccount = False
                            else:
                                self.__createAccountConsole.insert(END, f"{self.__createAccountConsole.size() + 1}| username taken, try again...")
                                if self.__createAccountConsole.size() > 3:
                                    self.__createAccountConsole.yview_scroll(1, UNITS)
                                self.__waitingForAddAccount = False
            elif self.__waitingForUpdateStats:
                # If waiting for update stats, wait for a response from the server to determine whether the update was valid or not
                while self.__waitingForUpdateStats:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "updateStats" and message.get("to", None) == self.__username.get():
                            if message.get("valid", False):
                                self.__waitingForUpdateStats = False
                            else:
                                # If the statistics failed to update, notify the user
                                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| failed to update stats...")
                                if self.__gameConsole.size() > 3:
                                    self.__gameConsole.yview_scroll(1, UNITS)
                                self.__waitingForUpdateStats = False
            elif self.__waitingForLoadPuzzle:
                # If waiting to load a puzzle, wait for the server to respond with the puzzle's information
                while self.__waitingForLoadPuzzle:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "loadPuzzle" and message.get("to", None) == self.__username.get():
                            if message.get("puzzleInfo", None) is not None:
                                # If the puzzle ID successfully retrieves puzzle information, load the puzzle
                                self.__loadPuzzleID, moves, self.__puzzleSolution = message.get("puzzleInfo", None)
                                self.__game.loadPuzzle(moves)
                                self.__puzzleGame()
                                self.__waitingForLoadPuzzle = False
                            else:
                                # If the puzzle ID does not retrieve puzzle information, notify the user that the ID is invalid
                                self.__puzzleSetupConsole.insert(END, f"{self.__puzzleSetupConsole.size() + 1}| ID invalid...")
                                if self.__puzzleSetupConsole.size() > 3:
                                    self.__puzzleSetupConsole.yview_scroll(1, UNITS)
                                self.__waitingForLoadPuzzle = False
            elif self.__waitingForSavePuzzle:
                # If waiting to save a puzzle, wait for a response from the server to determine whether the save was valid or not
                while self.__waitingForSavePuzzle:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "savePuzzle" and message.get("to", None) == self.__username.get():
                            if message.get("valid", False):
                                self.__exitPuzzle()
                                self.__waitingForSavePuzzle = False
                                # Send a message to the server with the update stats command and the new value
                                if not self.__guest and self.__network:
                                    self.__statsPMade += 1
                                    message = {"from": self.__username.get(), "cmd": "updatePMade", "pMade": self.__statsPMade}
                                    get_event_loop().create_task(self.__client.send(message))
                                    self.__waitingForUpdateStats = True
                            else:
                                # If the puzzle is unable to be stored in the database, notify the user that the ID is invalid
                                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| ID taken, try again...")
                                if self.__gameConsole.size() > 3:
                                    self.__gameConsole.yview_scroll(1, UNITS)
                                self.__waitingForSavePuzzle = False
            elif self.__waitingForLoadGame:
                # If waiting to load a game, wait for the server to respond with the game's information
                while self.__waitingForLoadGame:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "loadGame" and message.get("to", None) == self.__username.get():
                            if message.get("gameInfo", None) is not None:
                                # If the game name successfully retrieves game information, load the game
                                name, moves, opponent, account = message.get("gameInfo", None)
                                self.__opponentType.set(opponent)
                                self.__game.load(moves)
                                self.__cancelLoad()
                                self.__loadCreated = False
                                self.__play()
                                self.__waitingForLoadGame = False
                            else:
                                # If the game name does not retrieve game information, notify the user that the name is invalid
                                self.__loadConsole.insert(END, f"{self.__loadConsole.size() + 1}| game name invalid...")
                                if self.__loadConsole.size() > 3:
                                    self.__loadConsole.yview_scroll(1, UNITS)
                                self.__waitingForLoadGame = False
            elif self.__waitingForSaveGame:
                # If waiting to save a game, wait for a response from the server to determine whether the save was valid or not
                while self.__waitingForSaveGame:
                    self.__root.update()
                    await s(0.1)
                    if self.__client.canRcv():
                        message = await self.__client.recv()
                        cmd = message.get("cmd", None)
                        if cmd == "saveGame" and message.get("to", None) == self.__username.get():
                            if message.get("valid", False):
                                self.__dismissGame()
                                self.__waitingForSaveGame = False
                            else:
                                # If the game is unable to be stored in the database, notify the user that the ID is invalid
                                self.__saveConsole.insert(END, f"{self.__saveConsole.size() + 1}| name taken, try again...")
                                if self.__saveConsole.size() > 3:
                                    self.__saveConsole.yview_scroll(1, UNITS)
                                self.__waitingForSaveGame = False


class terminal(ui):
    def __init__(self, network):
        self._Game = game()
        self._network = network
        self._client = None
        self._name = ""
        self._opponent = ""
        self._hosting = False
        self._clientTurn = True

    async def runClient(self):
        # Exception Handling: If the client cannot connect to the server, report the error and the quit the program
        try:
            await self._client.run()
        except ConnectionRefusedError:
            print("server offline...")
            quit()

    async def run(self):
        if self._network:
            self._client = client()
            self._name = await ainput("Enter a username: ")
            playerType = ''
            while playerType not in ['h', 'j']:
                # Exception Handling: Validate the user input without crashing
                try:
                    playerType = await ainput("Would you like to host a game or join a game? [h|j]\n")
                    if playerType == 'h':
                        # If hosting, send a host command to the server so the server can add this user to the host set
                        await self._client.send({"from": self._name, "cmd": "tHost"})
                        self._hosting = True
                    elif playerType == 'j':
                        hostName = ""
                        while hostName == "":
                            waitingForHostList = True
                            while waitingForHostList:
                                # Send a request to the server for the list of hosts
                                await self._client.send({"from": self._name, "cmd": "hostList"})
                                message = await self._client.recv()
                                cmd = message.get("cmd", None)
                                if cmd == 'hostList' and message.get("to", None) == self._name:
                                    # Build a print a list of the current hosts
                                    hostList = message.get("hostList", None)
                                    result = 'Host list:'
                                    for host in hostList:
                                        result += host + ', '
                                    print(result[:-2])
                                    waitingForHostList = False
                            hostName = await ainput("Enter the host's username or enter nothing to refresh the host list: ")
                            if hostName != "":
                                # If the host name is valid, send a join request to the server, to be forwarded to the host
                                await self._client.send({"from": self._name, "to": hostName, "cmd": "tJoin"})
                    else:
                        raise hostError
                except hostError:
                    print("incorrect input, please enter 'h' or 'j'")
            while not self._opponent:
                # While the user does not have an opponent, wait for a message from the server
                message = await self._client.recv()
                cmd = message.get("cmd", None)
                if cmd == "tHost" and playerType == 'h':
                    print(f'{message.get("from", None)} is hosting...')
                elif cmd == "tJoin" and message.get("to", None) == self._name and self._hosting and not self._opponent:
                    accepted = ""
                    while accepted != "y" and accepted != "n":
                        # If the match is accepted set opponent to the sender and send positive response to the opponent otherwise don't store the opponent and send negative response
                        accepted = await ainput(f'Accept match from {message.get("from", None)}? [y|n]\n')
                        if accepted == "y":
                            await self._client.send({"from": self._name, "to": message.get("from", None), "cmd": "acc"})
                            self._opponent = message.get("from", None)
                        elif accepted == "n":
                            await self._client.send({"to": message.get("from", None), "from": self._name, "cmd": "rej"})
                        else:
                            print("invalid input")
                elif cmd == "acc" and self._name == message.get("to", None) and playerType == 'j':
                    # If the joiner receives an accept message, set the opponent and notify the user
                    print("match request accepted")
                    self._clientTurn = False
                    self._opponent = message.get("from", None)
                elif cmd == "rej" and self._name == message.get("to", None):
                    # If the joiner receives a reject message, notify the user and ask them for a new host username
                    print("match request rejected")
                    hostName = ""
                    while hostName == "":
                        waitingForHostList = True
                        while waitingForHostList:
                            # Send a request to the server for the list of hosts
                            await self._client.send({"from": self._name, "cmd": "hostList"})
                            message = await self._client.recv()
                            cmd = message.get("cmd", None)
                            if cmd == 'hostList' and message.get("to", None) == self._name:
                                # Build a print a list of the current hosts
                                hostList = message.get("hostList", None)
                                result = 'Host list:'
                                for host in hostList:
                                    result += host + ', '
                                print(result[:-2])
                                waitingForHostList = False
                        hostName = await ainput("Enter the host's username or enter nothing to refresh the host list: ")
                        if hostName != "":
                            # If the host name is valid, send a join request to the server, to be forwarded to the host
                            await self._client.send({"from": self._name, "to": hostName, "cmd": "tJoin"})
                elif cmd == "hnf" and self._name == message.get("to", None):
                    # If the host name is not in the server's host set, notify the user
                    print("host not found")
                    hostName = ""
                    while hostName == "":
                        waitingForHostList = True
                        while waitingForHostList:
                            # Send a request to the server for the list of hosts
                            await self._client.send({"from": self._name, "cmd": "hostList"})
                            message = await self._client.recv()
                            cmd = message.get("cmd", None)
                            if cmd == 'hostList' and message.get("to", None) == self._name:
                                # Build a print a list of the current hosts
                                hostList = message.get("hostList", None)
                                result = 'Host list:'
                                for host in hostList:
                                    result += host + ', '
                                print(result[:-2])
                                waitingForHostList = False
                        hostName = await ainput("Enter the host's username or enter nothing to refresh the host list: ")
                        if hostName != "":
                            # If the host name is valid, send a join request to the server, to be forwarded to the host
                            await self._client.send({"from": self._name, "to": hostName, "cmd": "tJoin"})
        while not self._Game.getWinner:
            print(self._Game)
            if self._clientTurn:
                if not self._client:
                    print(f"{self._Game.getPlayer} to play...")
                else:
                    print(f"Your turn...")
                # Exception Handling: if the user does not enter an integer, report the error without crashing
                try:
                    column = await ainput("Enter column number to drop counter: ")
                    column = int(column)
                except ValueError:
                    print("\n\n\n\nERROR: invalid input: expected integer")
                    continue
                # Range check on the inputted number to make sure it is in range of the columns
                if 1 <= column <= 7:
                    # Exception Handling: if the user tries to play in a full column, report the error without crashing
                    try:
                        self._Game.play(column)
                    except gameError:
                        print("\n\n\n\nERROR: column full")
                else:
                    print("\n\n\n\nERROR: input must be between 1 and 7 inclusive")
                if self._client:
                    # If playing a networked game, send a message to the server with the move command, the column played in and the opponent's name
                    await self._client.send({"from": self._name, "to": self._opponent, "cmd": "move", "col": column})
            else:
                # If it is not the clients turn, wait for a move to be sent from the opponent, and then play the move
                print(f"{self._opponent}'s turn, please wait...")
                col = -1
                while col == -1:
                    message = await self._client.recv()
                    cmd = message.get("cmd", None)
                    if cmd == "move" and message.get("to", None) == self._name:
                        # If the client receives a move message addressed to itself, play the move sent with the message
                        self._Game.play(message.get("col", -1))
            if self._client:
                self._clientTurn = True if not self._clientTurn else False
        # When the game has finished, get the end game information and display it
        print(self._Game)
        winner = self._Game.getWinner
        if winner == "Draw":
            print("The game was a draw!")
        else:
            if not self._client:
                print(f"{winner} has won, well played!")
            else:
                if self._clientTurn:
                    print("You lost!")
                else:
                    print("You won!")
