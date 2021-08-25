from abc import ABC, abstractmethod
from tkinter import Tk, Frame, Button, X, Toplevel, N, S, E, W, Grid, Canvas, StringVar, Listbox, Label, END, UNITS, HORIZONTAL, Scale, LEFT, RIGHT, OptionMenu, Entry
from game import game, gameError, nameError
from time import sleep
from players import Ai
from client import client
from aioconsole import ainput
from time import localtime, time
from asyncio import sleep as s
from asyncio import get_event_loop
from sqlite3 import IntegrityError
import sqlite3
from hashlib import pbkdf2_hmac
from os import urandom

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
        self._network = network
        root = Tk()
        root.title("ConnectFour")
        frame = Frame(root)
        frame.pack()
        self.__root = root

        self.__running = False
        self.__gameInProgress = False
        self.__helpInProgress = False
        self.__setupInProgress = False
        self.__typeChoiceInProgress = False
        self.__LANSetupInProgress = False
        self.__localInProgress = False
        self.__saveInProgress = False
        self.__loadInProgress = False
        self.__puzzleSetupInProgress = False
        self.__puzzleInProgress = False
        self.__gameOver = False
        self.__animating = False
        self.__inMenu = False
        self.__creatingAccount = False
        self.__statsInProgress = False

        self._opponent = None
        self.__opponentType = StringVar(value="Human")
        self.__waitingForHost = False
        self.__waitingForJoin = False
        self.__waitingForMove = False
        self.__client = client()
        self._clientTurn = True

        self.__colours = ['#ff0000', '#e6e600', '#cc00ff', '#ff33cc', '#ff6600', '#0099cc', '#33cc33', '#000000']
        self.__highlights = ['#ff9999', '#ffffb3', '#cc99ff', '#ff99cc', '#ffcc99', '#66ccff', '#99ff99', '#808080']
        self.__counters = ['RED', 'YELLOW', 'PURPLE', 'PINK', 'ORANGE', 'BLUE', 'GREEN', 'BLACK']
        self.__pOneColour = 0
        self.__pTwoColour = 1

        self.__username = StringVar()
        self.__password = StringVar()

        Label(frame, text="Connect 4").pack(fill=X)
        Entry(frame, textvariable=self.__username).pack(fill=X)
        Entry(frame, textvariable=self.__password).pack(fill=X)
        Button(frame, text="Log In", command=self._logIn).pack(fill=X)
        Button(frame, text="Create Account", command=self._createAccount).pack(fill=X)
        Button(frame, text="Play As Guest", command=self._guestLogIn).pack(fill=X)
        Button(frame, text="Quit", command=self._quit).pack(fill=X)

        console = Listbox(frame, height=3)
        console.pack(fill=X)
        self.__logInConsole = console

    def _logIn(self):
        if not self.__inMenu and not self.__creatingAccount:
            try:
                connection = sqlite3.connect('connectFour.db')
                # verify account details
                sql = f"SELECT * from ACCOUNTS WHERE USERNAME == '{self.__username.get()}'"
                accountInfo = connection.execute(sql)
                username, key, hashedPassword, self.__statsPlayed, self.__statsWon, self.__statsLost, self.__statsDrawn, self.__statsPFin, self.__statsPMade = None, None, None, 0, 0, 0, 0, 0, 0
                for row in accountInfo:
                    username, key, hashedPassword, self.__statsPlayed, self.__statsWon, self.__statsLost, self.__statsDrawn, self.__statsPFin, self.__statsPMade = row
                if username:
                    salt = key.to_bytes(4, byteorder="big")
                    password = pbkdf2_hmac('sha256', self.__password.get().encode('utf-8'), salt, 100000)
                    if str(password) == str(hashedPassword):
                        # if details are verified, keep record of account name and open menu
                        self.__password.set("")
                        self.__guest = False
                        self._menu()
                        connection.close()
                    else:
                        # if not then print error message to log in window
                        self.__password.set("")
                        self.__username.set("")
                        connection.close()
                        raise accountError
                else:
                    raise accountError
            except accountError:
                # print error message to console
                self.__logInConsole.insert(END, f"{self.__logInConsole.size() + 1}| username or password incorrect...")
                # scroll console if needed
                if self.__logInConsole.size() > 3:
                    self.__logInConsole.yview_scroll(1, UNITS)

    def _createAccount(self):
        if not self.__inMenu and not self.__creatingAccount:
            self.__creatingAccount = True
            accountCreationWin = Toplevel(self.__root)
            accountCreationWin.title("Create Account")
            frame = Frame(accountCreationWin)
            frame.pack()
            self.__accountCreationWin = accountCreationWin

            self.__uName = StringVar()
            self.__pWord = StringVar()
            self.__confPWord = StringVar()

            Entry(frame, textvariable=self.__uName).pack(fill=X)
            Entry(frame, textvariable=self.__pWord).pack(fill=X)
            Entry(frame, textvariable=self.__confPWord).pack(fill=X)
            Button(frame, text="Create Account", command=self._addAccount).pack(fill=X)

            console = Listbox(frame, height=3)
            console.pack(fill=X)
            self.__createAccountConsole = console

            Button(frame, text="Cancel", command=self._cancelCreate).pack(fill=X)

    def _addAccount(self):
        if self.__pWord.get() == self.__confPWord.get():
            # get random salt
            salt = urandom(4)
            # get the integer value of the salt to store
            key = int.from_bytes(salt, byteorder="big")
            # get hashed password
            hashedPassword = pbkdf2_hmac('sha256', self.__pWord.get().encode('utf-8'), salt, 100000)
            # try to add the account to the database
            connection = sqlite3.connect('connectFour.db')
            try:
                sql = f"""INSERT INTO ACCOUNTS (USERNAME,KEY,HPWORD,SPLAYED,SWON,SLOST,SDRAWN,SPFIN,SPMADE)
                              VALUES ("{self.__uName.get()}", "{key}", "{hashedPassword}", 0, 0, 0, 0, 0, 0)"""
                connection.execute(sql)
                connection.commit()
                # close connection
                connection.close()
                # close account creation window
                self._cancelCreate()
                # print message to log in console
                self.__logInConsole.insert(END, f"{self.__logInConsole.size() + 1}| account created...")
                # scroll console if needed
                if self.__logInConsole.size() > 3:
                    self.__logInConsole.yview_scroll(1, UNITS)
            except IntegrityError:
                # close connection
                connection.close()
                # print error message
                self.__createAccountConsole.insert(END, f"{self.__createAccountConsole.size() + 1}| username taken, try again...")
                if self.__createAccountConsole.size() > 3:
                    self.__createAccountConsole.yview_scroll(1, UNITS)
        else:
            self.__createAccountConsole.insert(END, f"{self.__createAccountConsole.size() + 1}| passwords don't match, try again...")
            if self.__createAccountConsole.size() > 3:
                self.__createAccountConsole.yview_scroll(1, UNITS)

    def _cancelCreate(self):
        self.__accountCreationWin.destroy()
        self.__creatingAccount = False

    def _guestLogIn(self):
        self.__guest = True
        self._menu()

    def _menu(self):
        if not self.__inMenu:
            self.__inMenu = True
            menuWin = Toplevel(self.__root)
            menuWin.title("Menu")
            frame = Frame(menuWin)
            frame.pack()
            self.__menuWin = menuWin

            Button(frame, text="Play", command=self._gametype).pack(fill=X)
            Button(frame, text="Help", command=self._help).pack(fill=X)
            Button(frame, text="Stats", command=self._stats).pack(fill=X)
            Button(frame, text="Dismiss", command=self._dismissMenu).pack(fill=X)

    def _stats(self):
        if not self.__guest and not self.__statsInProgress:
            self.__statsInProgress = True
            statsWin = Toplevel(self.__root)
            statsWin.title("Stats")
            frame = Frame(statsWin)
            frame.pack()
            self.__statsWin = statsWin

            # stats (played, lost, won, drawn, puzzles finished, puzzles made)
            Label(frame, text=f"{self.__username.get()}'s stats:").pack(fill=X)
            Label(frame, text=f"PLAYED: {self.__statsPlayed}").pack(fill=X)
            Label(frame, text=f"WON: {self.__statsWon}").pack(fill=X)
            Label(frame, text=f"LOST: {self.__statsLost}").pack(fill=X)
            Label(frame, text=f"DRAWN: {self.__statsDrawn}").pack(fill=X)
            Label(frame, text=f"PUZZLE WINS: {self.__statsPFin}").pack(fill=X)
            Label(frame, text=f"PUZZLES MADE: {self.__statsPMade}").pack(fill=X)
            # back button
            Button(frame, text="Dismiss", command=self._dismissStats).pack(fill=X)

    def _dismissStats(self):
        self.__statsWin.destroy()
        self.__statsInProgress = False

    def _dismissMenu(self):
        self.__menuWin.destroy()
        self.__inMenu = False

    def _gametype(self):
        if not self.__typeChoiceInProgress:
            self.__typeChoiceInProgress = True
            typeChoiceWin = Toplevel(self.__root)
            typeChoiceWin.title("Game Type")
            frame = Frame(typeChoiceWin)
            frame.pack()
            self.__typeChoiceWin = typeChoiceWin

            Button(frame, text="Pass and Play", command=self._gameSetup).pack(fill=X)
            if self._network:
                Button(frame, text="Play Local Online", command=self._LANSetup).pack(fill=X)
            Button(frame, text="Puzzles", command=self._puzzleSetup).pack(fill=X)
            Button(frame, text="Dismiss", command=self._dismissTypeChoice).pack(fill=X)

    def _puzzleSetup(self):
        if not self.__puzzleSetupInProgress:
            self.__puzzleSetupInProgress = True
            puzzleSetupWin = Toplevel(self.__root)
            puzzleSetupWin.title("Puzzle Setup")
            frame = Frame(puzzleSetupWin)
            frame.pack()
            self.__puzzleSetupWin = puzzleSetupWin

            self.__puzzleCode = StringVar()

            Button(frame, text="Create", command=self._puzzleCreate).pack(fill=X)
            Button(frame, text="Random", command=self._puzzleRandom).pack(fill=X)
            Entry(frame, textvariable=self.__puzzleCode).pack(fill=X)
            Button(frame, text="Load", command=self._puzzleLoad).pack(fill=X)

            # colour choices
            self.__pOne = StringVar()
            self.__pOne.set("RED")
            self.__pTwo = StringVar()
            self.__pTwo.set("YELLOW")
            Label(frame, text=f"Player 1 colour:").pack(fill=X)
            pOneDropDown = OptionMenu(frame, self.__pOne, *self.__counters)
            pOneDropDown.pack(fill=X)
            Label(frame, text=f"Player 2 colour:").pack(fill=X)
            pTwoDropDown = OptionMenu(frame, self.__pTwo, *self.__counters)
            pTwoDropDown.pack(fill=X)

            Button(frame, text="Dismiss", command=self._dismissPuzzleSetup).pack(fill=X)

            console = Listbox(frame, height=3)
            console.pack(fill=X)
            self.__puzzleSetupConsole = console

            self.__puzzleSetupConsole.insert(END, f"1| enter ID to load")
            self.__game = game()

    def _puzzleCreate(self):
        self._puzzleGame(create=True)

    def _puzzleRandom(self):
        self.__puzzleCode.set("random")
        self._puzzleLoad()

    def _puzzleLoad(self):
        try:
            self.__puzzleSolution, self.__puzzleCode = self.__game.loadPuzzle(self.__puzzleCode.get())
            self._puzzleGame()
        except nameError as e:
            # print error message to console
            self.__puzzleSetupConsole.insert(END, f"{self.__puzzleSetupConsole.size() + 1}| {e}")
            # scroll console if needed
            if self.__puzzleSetupConsole.size() > 3:
                self.__puzzleSetupConsole.yview_scroll(1, UNITS)

    def _puzzleGame(self, create=False):
        if not self.__puzzleInProgress:
            self._dismissPuzzleSetup()
            self.__puzzleInProgress = True

            # set the colours
            for i, colour in enumerate(self.__counters):
                if colour == self.__pOne.get():
                    self.__pOneColour = i
                elif colour == self.__pTwo.get():
                    self.__pTwoColour = i

            # create the puzzle window
            puzzleWin = Toplevel(self.__root)
            puzzleWin.title("Puzzle")
            frame = Frame(puzzleWin)
            self.__puzzleWin = puzzleWin

            Grid.columnconfigure(puzzleWin, 0, weight=1)
            Grid.rowconfigure(puzzleWin, 0, weight=1)
            frame.grid(row=0, column=0, sticky=N + S + W + E)

            # console
            console = Listbox(frame, height=3)
            console.grid(row=0, column=0, columnspan=4, sticky=E + W)
            self.__gameConsole = console

            # instruction label
            if create:
                t = "PUT IN SOME COUNTERS, ENTER A PUZZLE ID THEN SAVE"
            else:
                player = self.__counters[self.__pOneColour] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour]
                t = f"PLAY THE BEST MOVE POSSIBLE FOR {player}"
            Label(frame, text=t, bg='gray').grid(row=0, column=4, columnspan=3, sticky=N + S + E + W)

            # board
            # Change tile to change board size
            winWidth = self.__puzzleWin.winfo_screenwidth()
            if winWidth < 40:
                # min board tile size
                winWidth = 40
            elif winWidth > 100:
                # max board tile size
                winWidth = 100
            tile = winWidth
            counterSize = tile * 0.8
            boardWidth = 7 * tile
            boardHeight = 6 * tile
            board = Canvas(puzzleWin, width=boardWidth, height=boardHeight, bg='blue')
            baseX1 = tile / 10
            baseY1 = tile / 10
            baseX2 = baseX1 + counterSize
            baseY2 = baseY1 + counterSize
            self.__spaces = [[None for _ in range(7)] for _ in range(6)]
            for row in range(6):
                for column in range(7):
                    # create counter slots
                    space = self.__game.getSpace(row, column)
                    if space == game.PONE:
                        counterColour = self.__colours[self.__pOneColour]
                    elif space == game.PTWO:
                        counterColour = self.__colours[self.__pTwoColour]
                    else:
                        counterColour = "white"
                    oval = board.create_oval(baseX1 + (column * tile), baseY1 + (row * tile), baseX2 + (column * tile), baseY2 + (row * tile), fill=counterColour)  # , dash=(7,1,1,1)
                    self.__spaces[row][column] = oval
            board.grid(row=1, column=0)
            self.__canvas = board

            self.__puzzleID = StringVar()

            if create:
                self.__creative = True
                # puzzle id entry
                Entry(frame, textvariable=self.__puzzleID).grid(row=3, column=0, sticky=N + S + W + E)
                # save button
                Button(puzzleWin, text="Save", command=self._savePuzzle).grid(row=4, column=0, sticky=N + S + W + E)
            else:
                self.__creative = False
                # puzzle id label
                Label(puzzleWin, text=f"ID: {self.__puzzleCode}").grid(row=3, column=0, sticky=N + S + W + E)
                # solve button
                Button(puzzleWin, text="Solve", command=self._solvePuzzle).grid(row=4, column=0, sticky=N + S + W + E)
            # undo button
            Button(puzzleWin, text="Undo", command=self._undoMove).grid(row=5, column=0, sticky=N + S + W + E)
            # exit button
            Button(puzzleWin, text="Exit", command=self._exitPuzzle).grid(row=6, column=0, sticky=N + S + W + E)

            # column buttons
            for col in range(7):
                t = StringVar()
                t.set(col + 1)
                cmd = lambda c=col: self.__playPuzzleMove(c)
                Button(frame, textvariable=t, command=cmd).grid(row=1, column=col, sticky=N + S + W + E)

            # resizing
            for col in range(7):
                Grid.columnconfigure(frame, col, weight=1)

            self._puzzleOver = False

    def __playPuzzleMove(self, col):
        # if a counter is falling print a wait message
        if self.__animating:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| please wait...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)
        # if the game isn't won
        elif not self._puzzleOver:
            try:
                # set the counter colour
                counter = self.__colours[self.__pOneColour] if self.__game.getPlayer == game.PONE else self.__colours[self.__pTwoColour]
                # play the counter
                row = 5 - self.__game.play(col + 1)
                # animate the counter
                self.__animatedDrop(row, col, counter)
                self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)
            except gameError as e:
                # print error message to console
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {e}")
                # scroll console if needed
                if self.__gameConsole.size() > 3:
                    self.__gameConsole.yview_scroll(1, UNITS)
            if not self.__creative:
                # check if played winning move
                self._puzzleOver = True
                # if the player played the solution move call the popup
                if col == self.__puzzleSolution:
                    self._puzzleWin()
                # else, let the player know they played the wrong move
                else:
                    self._puzzleLose()
        elif self._puzzleOver:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| undo move or exit...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)

    def _puzzleWin(self):
        solvedWin = Toplevel(self.__root)
        solvedWin.title("Solved")
        frame = Frame(solvedWin)
        frame.pack()
        self.__solvedWin = solvedWin

        Label(frame, text=f"CORRECT MOVE!").pack(fill=X)
        Label(frame, text="WELL DONE!").pack(fill=X)
        Button(frame, text="Exit", command=self._exitSolved).pack(fill=X)

        # update stats
        if not self.__guest:
            self.__statsPFin += 1
            connection = sqlite3.connect('connectFour.db')
            stmt = f"UPDATE ACCOUNTS set SPFIN = {self.__statsPFin} WHERE USERNAME = '{self.__username.get()}';"
            connection.execute(stmt)
            connection.commit()
            connection.close()

    def _puzzleLose(self):
        loseWin = Toplevel(self.__root)
        loseWin.title("Solved")
        frame = Frame(loseWin)
        frame.pack()
        self.__loseWin = loseWin

        Label(frame, text=f"INCORRECT MOVE!").pack(fill=X)
        Label(frame, text="UNDO OR EXIT").pack(fill=X)
        Button(frame, text="Exit", command=self._exitLost).pack(fill=X)

    def _exitLost(self):
        self.__loseWin.destroy()

    def _exitSolved(self):
        self.__solvedWin.destroy()

    def _savePuzzle(self):
        # get solution
        solution = self._solvePuzzle(saving=True)

        # get id
        ID = self.__puzzleID.get()

        # try to save
        try:
            self.__game.savePuzzle(ID,solution)
            self._exitPuzzle()

            # update stats
            self.__statsPMade += 1
            connection = sqlite3.connect('connectFour.db')
            stmt = f"UPDATE ACCOUNTS set SPMADE = {self.__statsPMade} WHERE USERNAME = '{self.__username.get()}';"
            connection.execute(stmt)
            connection.commit()
            connection.close()

        # if the name is not unique, print an error message
        except IntegrityError:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| ID taken, try again...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)

    def _solvePuzzle(self, saving=False):
        if not self._puzzleOver:
            # create computer to get best move
            computer = Ai("Easy AI") #"Hard AI"
            # get best move
            column = computer.getColumn(self.__game.Board, self.__game.getPlayer)
            # if saving, return the column to be saved in the database
            if saving:
                return column
            # otherwise,
            else:
                # play move
                counter = self.__colours[self.__pOneColour] if self.__game.getPlayer == game.PONE else self.__colours[self.__pTwoColour]
                row = 5 - self.__game.play(column + 1)
                # animate drop
                self.__animatedDrop(row, column, counter)
                self.__canvas.itemconfig(self.__spaces[row][column], fill=counter)
                # highlight solution
                counter = self.__highlights[self.__pOneColour] if not self.__game.getPlayer == game.PONE else self.__highlights[self.__pTwoColour]
                self.__canvas.itemconfig(self.__spaces[row][column], fill=counter)
                self._puzzleOver = True

    def _exitPuzzle(self):
        self.__puzzleWin.destroy()
        self.__puzzleInProgress = False

    def _dismissPuzzleSetup(self):
        self.__puzzleSetupWin.destroy()
        self.__puzzleSetupInProgress = False

    def _dismissTypeChoice(self):
        self.__typeChoiceWin.destroy()
        self.__typeChoiceInProgress = False

    def _LANSetup(self):
        if not self.__LANSetupInProgress:
            self.__LANSetupInProgress = True
            LANSetupWin = Toplevel(self.__root)
            LANSetupWin.title("LAN Setup")
            frame = Frame(LANSetupWin)
            frame.pack()
            self.__LANSetupWin = LANSetupWin
            self.__joinCode = StringVar()

            timeStamp = localtime(time())
            clientCode = str(timeStamp[2])
            clientCode += str(timeStamp[4])
            clientCode += str(timeStamp[5])
            self.__clientCode = clientCode

            Button(frame, text="Host", command=self._hostGame).pack(fill=X)
            Entry(frame, textvariable=self.__joinCode).pack(fill=X)
            Button(frame, text="Join", command=self._attemptJoin).pack(fill=X)

            # colour choices
            self.__pOne = StringVar()
            self.__pOne.set("RED")
            self.__pTwo = StringVar()
            self.__pTwo.set("YELLOW")
            Label(frame, text=f"Player 1 colour:").pack(fill=X)
            pOneDropDown = OptionMenu(frame, self.__pOne, *self.__counters)
            pOneDropDown.pack(fill=X)
            Label(frame, text=f"Player 2 colour:").pack(fill=X)
            pTwoDropDown = OptionMenu(frame, self.__pTwo, *self.__counters)
            pTwoDropDown.pack(fill=X)

            Button(frame, text="Back", command=self._dismissLANSetup).pack(fill=X)

            # console
            console = Listbox(frame, height=3)
            console.pack(fill=X)
            self.__LANConsole = console
            # self.__LANConsole.insert(END, f"1| ")

    def _hostGame(self):
        if not self.__localInProgress and not self.__gameInProgress:
            self.__localInProgress = True
            hostWin = Toplevel(self.__root)
            hostWin.title("Host")
            frame = Frame(hostWin)
            frame.pack()
            self.__hostWin = hostWin

            Label(frame, text=f"JOIN CODE: {self.__clientCode}").pack(fill=X)
            Label(frame, text="WAITING FOR OPPONENT...").pack(fill=X)
            Button(frame, text="Back", command=self._dismissHost).pack(fill=X)

            self.__waitingForJoin = True

    def _dismissHost(self):
        self.__hostWin.destroy()
        self.__localInProgress = False

    def _attemptJoin(self):
        if not self.__localInProgress and not self.__gameInProgress:
            self.__localInProgress = True
            message = {"joinCode": self.__joinCode.get(), "from": self.__clientCode, "cmd": "hJoin"}
            get_event_loop().create_task(self.__client.send(message))
            self.__waitingForHost = True

    def _dismissLANSetup(self):
        self.__LANSetupWin.destroy()
        self.__LANSetupInProgress = False

    def _gameSetup(self):
        if not self.__setupInProgress:
            self.__setupInProgress = True
            setupWin = Toplevel(self.__root)
            setupWin.title("Game Setup")
            frame = Frame(setupWin)
            self.__setupWin = setupWin
            self.__opponent = None

            Grid.columnconfigure(self.__setupWin, 0, weight=1)
            Grid.rowconfigure(self.__setupWin, 0, weight=1)
            frame.grid(row=0, column=0, sticky=N + S + W + E)

            # first player
            '''
            Label(frame, text="Choose Player 1:").grid(row=0)
            Label(frame, text="RED").grid(row=1, column=0)
            turnSlider = Scale(self.__setupWin, from_=0, to_=1, orient=HORIZONTAL, showvalue=0)
            turnSlider.grid(row=1, column=1)
            Label(frame, text="YELLOW").grid(row=1, column=2)
            #self._firstTurn = turnSlider.get()
            '''

            # opponent
            Label(frame, text="Choose Opponent:").grid(row=0, column=0)
            options = ["Human", "Practice AI", "Easy AI", "Medium AI", "Hard AI"]
            self.__opponentType.set("Human")
            opponentDropDown = OptionMenu(self.__setupWin, self.__opponentType, *options)
            opponentDropDown.grid(row=0, column=1, sticky=N)

            # colour choices
            playerOne = "Player 1" if self.__guest else f"{self.__username.get()}"
            Label(frame, text=f"{playerOne} colour:").grid(row=1, column=0)
            playerTwo = "Player 2" if self.__guest else f"Opponent"
            Label(frame, text=f"{playerTwo} colour:").grid(row=2, column=0)
            self.__pOne = StringVar()
            self.__pOne.set("RED")
            self.__pTwo = StringVar()
            self.__pTwo.set("YELLOW")
            pOneDropDown = OptionMenu(self.__setupWin, self.__pOne, *self.__counters)
            pOneDropDown.grid(row=1, column=1, sticky=N)
            pTwoDropDown = OptionMenu(self.__setupWin, self.__pTwo, *self.__counters)
            pTwoDropDown.grid(row=2, column=1, sticky=N)

            # load button
            Button(frame, text="Load", command=self._load).grid(row=3, column=0)

            # play button
            Button(frame, text="Play", command=self._play).grid(row=4, column=0)

            # back button
            Button(frame, text="Back", command=self._dismissSetup).grid(row=5, column=0)

            # create a game object
            self.__game = game()

    def _dismissSetup(self):
        self.__setupWin.destroy()
        self.__setupInProgress = False

    def _load(self):
        if not self.__loadInProgress and not self.__gameInProgress:
            self.__loadInProgress = True
            loadWin = Toplevel(self.__root)
            loadWin.title("Load Game")
            frame = Frame(loadWin)
            frame.pack()
            self.__loadWin = loadWin

            self.__loadName = StringVar()

            # instruction
            Label(frame, text=f"ENTER GAME NAME BELOW").pack(fill=X)
            # text entry
            Entry(frame, textvariable=self.__loadName).pack(fill=X)
            # save button
            Button(frame, text="Load", command=self._loadGame).pack(fill=X)
            # console
            console = Listbox(frame, height=3)
            console.pack(fill=X)
            self.__loadConsole = console
            # self.__loadConsole.insert(END, f"1| ")
            # cancel button
            Button(frame, text="Cancel", command=self._cancelLoad).pack(fill=X)

    def _loadGame(self):
        try:
            opponent = self.__game.load(self.__loadName.get())
            self.__opponentType.set(opponent)
            self.__loadWin.destroy()
            self.__loadInProgress = False
            self._play()
        except nameError as e:
            # print error message to console
            self.__loadConsole.insert(END, f"{self.__loadConsole.size() + 1}| {e}")
            # scroll console if needed
            if self.__loadConsole.size() > 3:
                self.__loadConsole.yview_scroll(1, UNITS)

    def _cancelLoad(self):
        self.__loadWin.destroy()
        self.__loadInProgress = False

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
        # print(self.__opponentType.get())
        if not self.__gameInProgress:
            self._dismissSetup()
            # if the opponent is not human, create an AI object
            if self.__opponentType.get() != "Human":
                self.__opponent = Ai(self.__opponentType.get())
            self.__gameInProgress = True

            # set the colours
            for i, colour in enumerate(self.__counters):
                if colour == self.__pOne.get():
                    self.__pOneColour = i
                elif colour == self.__pTwo.get():
                    self.__pTwoColour = i

            # create the game window
            gameWin = Toplevel(self.__root)
            gameWin.title("Game")
            frame = Frame(gameWin)
            self.__gameWin = gameWin

            Grid.columnconfigure(gameWin, 0, weight=1)
            Grid.rowconfigure(gameWin, 0, weight=1)
            frame.grid(row=0, column=0, sticky=N + S + W + E)

            # console
            console = Listbox(frame, height=3)
            console.grid(row=0, column=0, columnspan=4, sticky=E + W)
            self.__gameConsole = console
            if self._network:
                self.__gameConsole.insert(END, f"1| local game")
            else:
                self.__gameConsole.insert(END, f"1| game against {self.__opponentType.get()}")

            # player turn label
            self.__playerTurn = StringVar()
            if self.__opponentType.get() == "Human" and not self._network:
                counter = self.__counters[self.__pOneColour] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour]
                self.__playerTurn.set(f'{counter} TO PLAY\nCHOOSE COLUMN')
            elif self.__opponentType.get() == "Human" and self._network:
                if self._clientTurn:
                    self.__playerTurn.set('YOUR TURN\nCHOOSE COLUMN')
                else:
                    self.__playerTurn.set("OPPONENT'S TURN\nPLEASE WAIT")
            else:
                self.__playerTurn.set('YOUR TURN\nCHOOSE COLUMN')

            Label(frame, textvariable=self.__playerTurn, bg='gray').grid(row=0, column=4, columnspan=3, sticky=N + S + E + W)

            # board
            # Change tile to change board size
            winWidth = self.__gameWin.winfo_screenwidth()
            if winWidth < 40:
                # min board tile size
                winWidth = 40
            elif winWidth > 100:
                # max board tile size
                winWidth = 100
            tile = winWidth
            counterSize = tile * 0.8
            boardWidth = 7 * tile
            boardHeight = 6 * tile
            board = Canvas(gameWin, width=boardWidth, height=boardHeight, bg='blue')
            baseX1 = tile / 10
            baseY1 = tile / 10
            baseX2 = baseX1 + counterSize
            baseY2 = baseY1 + counterSize
            self.__spaces = [[None for _ in range(7)] for _ in range(6)]
            for row in range(6):
                for column in range(7):
                    # create counter slots
                    space = self.__game.getSpace(row, column)
                    if space == game.PONE:
                        counterColour = self.__colours[self.__pOneColour]
                    elif space == game.PTWO:
                        counterColour = self.__colours[self.__pTwoColour]
                    else:
                        counterColour = "white"
                    oval = board.create_oval(baseX1 + (column*tile), baseY1 + (row*tile), baseX2 + (column*tile), baseY2 + (row*tile), fill=counterColour)# , dash=(7,1,1,1)
                    self.__spaces[row][column] = oval
            board.grid(row=1, column=0)
            self.__canvas = board

            if not self._network:
                # undo button
                Button(gameWin, text="Undo", command=self._undoMove).grid(row=3, column=0, sticky=N+S+W+E)
                # save and exit button
                Button(gameWin, text="Save and Exit", command=self._saveAndExit).grid(row=4, column=0, sticky=N+S+W+E)

            # dismiss button
            Button(gameWin, text="Dismiss", command=self._dismissGame).grid(row=5, column=0, sticky=N+S+W+E)

            # column buttons
            for col in range(7):
                t = StringVar()
                t.set(col + 1)
                cmd = lambda c=col: self.__playMove(c)
                Button(frame, textvariable=t, command=cmd).grid(row=1, column=col, sticky=N+S+W+E)

            # resizing
            for col in range(7):
                Grid.columnconfigure(frame, col, weight=1)

    def _saveAndExit(self):
        # if a counter is falling print a wait message
        if self.__animating:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| please wait...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)
        elif not self.__saveInProgress:
            self.__saveInProgress = True
            saveWin = Toplevel(self.__root)
            saveWin.title("Save and Exit")
            frame = Frame(saveWin)
            frame.pack()
            self.__saveWin = saveWin

            self.__gameName = StringVar()

            # instruction
            Label(frame, text=f"ENTER GAME NAME BELOW").pack(fill=X)
            # text entry
            Entry(frame, textvariable=self.__gameName).pack(fill=X)
            # save button
            Button(frame, text="Save", command=self._saveGame).pack(fill=X)
            # console
            console = Listbox(frame, height=3)
            console.pack(fill=X)
            self.__saveConsole = console
            # self.__saveConsole.insert(END, f"1| ")
            # cancel button
            Button(frame, text="Cancel", command=self._cancelSave).pack(fill=X)

    def _saveGame(self):
        # try to save
        try:
            self.__game.save(self.__gameName.get(), self.__opponentType.get())
            self._cancelSave()
            self._dismissGame()
        # if the name is not unique, print an error message
        except IntegrityError:
            self.__saveConsole.insert(END, f"{self.__saveConsole.size() + 1}| name taken, try again...")
            if self.__saveConsole.size() > 3:
                self.__saveConsole.yview_scroll(1, UNITS)

    def _cancelSave(self):
        self.__saveWin.destroy()
        self.__saveInProgress = False

    def _undoMove(self):
        if not self.__gameOver and self.__opponentType.get() == "Human":
            try:
                row, col = self.__game.undo()
                self.__canvas.itemconfig(self.__spaces[row][col], fill="white")
                if not self.__puzzleInProgress:
                    counter = self.__counters[self.__pOneColour] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour]
                    self.__playerTurn.set(f'{counter} TO PLAY\nCHOOSE COLUMN')
                else:
                    self._puzzleOver = False
            except gameError as e:
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {e}")
                if self.__gameConsole.size() > 3:
                    self.__gameConsole.yview_scroll(1, UNITS)
        else:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| undo unavailable")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)

    def __playMove(self, col):
        # if a counter is falling or the client is waiting for the opponent to move, print a wait message
        if self.__animating or not self._clientTurn:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| please wait...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)

        # if the game isn't won and its the client's move
        elif not self.__game.getWinner:
            try:
                # set the counter colour
                counter = self.__colours[self.__pOneColour] if self.__game.getPlayer == game.PONE else self.__colours[self.__pTwoColour]
                # play the counter
                row = 5 - self.__game.play(col + 1)
                # if playing a networked game send the move to the opponent
                if self._network:
                    message = {"to": self._opponent, "from": self.__clientCode, "cmd": "move", "col": col}
                    get_event_loop().create_task(self.__client.send(message))
                # animate the counter
                self.__animatedDrop(row, col, counter)
                self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)
                # change turn display
                if self.__opponentType.get() == "Human" and not self._network:
                    # if its pass and play, use the counter colour to say whose turn it is
                    counter = self.__counters[self.__pOneColour] if self.__game.getPlayer == game.PONE else self.__counters[self.__pTwoColour]
                    self.__playerTurn.set(f'{counter} TO PLAY\nCHOOSE COLUMN')
                elif self.__opponentType.get() == "Human" and self._network:
                    # if it is a networked game, flip whose turn
                    self._clientTurn = True if not self._clientTurn else False
                    if self._clientTurn:
                        self.__playerTurn.set(f'YOUR TURN\nCHOOSE COLUMN')
                        self.__waitingForMove = False
                    else:
                        self.__playerTurn.set(f'OPPONENTS TURN\nPLEASE WAIT')
                        self.__waitingForMove = True
                else:
                    # if it's a game against AI tell the player it's the AI's turn
                    self.__playerTurn.set(f'OPPONENTS TURN\nPLEASE WAIT')
            except gameError as e:
                # print error message to console
                self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| {e}")
                # scroll console if needed
                if self.__gameConsole.size() > 3:
                    self.__gameConsole.yview_scroll(1, UNITS)
            # check if played winning move
            self.__checkIfWon()

            # if it's a game against the AI, play the AI's move
            if self.__opponentType.get() != "Human" and not self.__game.getWinner:
                # AI move
                counter = self.__colours[self.__pOneColour] if self.__game.getPlayer == game.PONE else self.__colours[self.__pTwoColour]
                col = self.__opponent.getColumn(self.__game.Board, self.__game.getPlayer)
                row = 5 - self.__game.play(col + 1)
                # animate drop
                self.__animatedDrop(row, col, counter)
                self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)
                # change turn display
                self.__playerTurn.set(f'YOUR TURN\nCHOOSE COLUMN')
                # check if played a winning move
                self.__checkIfWon()

    def __checkIfWon(self):
        winningPlayer, run = self.__game.getRun
        if winningPlayer:
            self.__gameOver = True
            if self.__game.getWinner != "Draw":
                winner = self.__counters[self.__pOneColour] if self.__game.getWinner == game.PONE else self.__counters[self.__pTwoColour]
                if self.__opponentType.get() == "Human":
                    self.__playerTurn.set(f'{winner} HAS WON\nCONGRATULATIONS!')
                else:
                    winner = 'YOU' if self.__game.getWinner == game.PONE else 'OPPONENT'
                    self.__playerTurn.set(f'{winner} WON\nGOOD GAME!')
            else:
                self.__playerTurn.set(f'THE GAME WAS DRAWN')

            # highlight winning run
            if run:
                counter = self.__highlights[self.__pOneColour] if winningPlayer == game.PONE else self.__highlights[self.__pTwoColour]
                for row, col in run:
                    self.__canvas.itemconfig(self.__spaces[row][col], fill=counter)

            # update stats
            if not self.__guest:
                self.__statsPlayed += 1
                if self.__game.getWinner == "Draw":
                    self.__statsDrawn += 1
                elif self.__game.getWinner == game.PONE:
                    self.__statsWon += 1
                else:
                    self.__statsLost += 1

                connection = sqlite3.connect('connectFour.db')

                stmt = f"UPDATE ACCOUNTS set SPLAYED = {self.__statsPlayed} WHERE USERNAME = '{self.__username.get()}';"
                connection.execute(stmt)
                stmt = f"UPDATE ACCOUNTS set SWON = {self.__statsWon} WHERE USERNAME = '{self.__username.get()}';"
                connection.execute(stmt)
                stmt = f"UPDATE ACCOUNTS set SLOST = {self.__statsLost} WHERE USERNAME = '{self.__username.get()}';"
                connection.execute(stmt)
                stmt = f"UPDATE ACCOUNTS set SDRAWN = {self.__statsDrawn} WHERE USERNAME = '{self.__username.get()}';"
                connection.execute(stmt)

                connection.commit()
                connection.close()

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
        self.__running = False

    async def runClient(self):
        await self.__client.run()

    async def run(self):
        # simulate mainloop so that the gui and client can both run
        self.__running = True
        while self.__running:
            await s(0.1)
            # substitute for tk.mainloop()
            self.__root.update()
            # wait for a message from the host
            if self.__waitingForHost:
                # while client doesnt have an opponent, wait for the host to reply with an accept
                while not self._opponent:
                    counter = 0
                    message = await self.__client.recv()
                    cmd = message.get("cmd", None)
                    if cmd == "match" and message.get("to", None) == self.__clientCode:
                        self._opponent = message.get("from", None)
                        self.__localInProgress = False
                        # if int(self.__clientCode) % int(self.__clientCode[4:]) > int(self._opponent) % int(self._opponent[4:]):
                        if self.__clientCode > self._opponent:
                            self._clientTurn = True
                            self.__waitingForMove = False
                        else:
                            self._clientTurn = False
                            self.__waitingForMove = True
                        self._play()
                    else:
                        counter += 1
                        if counter == 5:
                            self.__waitingForHost = False
                            self.__LANConsole.insert(END, f"{self.__LANConsole.size() + 1}| host not found...")
                            if self.__LANConsole.size() > 3:
                                self.__LANConsole.yview_scroll(1, UNITS)

            # wait for a message from the joiner
            elif self.__waitingForJoin:
                # while client doesn't have an opponent, wait for someone to request a match
                while not self._opponent:
                    message = await self.__client.recv()
                    cmd = message.get("cmd", None)
                    if cmd == "hJoin" and message.get("joinCode", None) == self.__clientCode:
                        self._opponent = message.get("from", None)
                        await self.__client.send({"to": self._opponent, "from": self.__clientCode, "cmd": "match"})
                        self.__waitingForJoin = False
                        self.__localInProgress = False
                        # if int(self.__clientCode) % int(self.__clientCode[4:]) > int(self._opponent) % int(self._opponent[4:]):
                        if self.__clientCode > self._opponent:
                            self._clientTurn = True
                            self.__waitingForMove = False
                        else:
                            self._clientTurn = False
                            self.__waitingForMove = True
                        self._play()

            if self.__waitingForMove:
                # if waiting for move, wait for a move message from the opponent and play the move
                while self.__waitingForMove:
                    message = await self.__client.recv()
                    cmd = message.get("cmd", None)
                    if cmd == "move" and message.get("to", None) == self.__clientCode:
                        self.__playMove(message.get("col", None))


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
        await self._client.run()

    async def run(self):
        if self._network:
            #if playing a networked game:
            #initialise a client object
            self._client = client()
            #allow the user to enter a username
            self._name = await ainput("Enter a username: ")
            try:
                #hosting or joining?
                playerType = await ainput("Would you like to host a game or join a game? [h|j]\n")
                if playerType == 'h':
                    #if hosting, send a host command
                    await self._client.send({"from": self._name, "cmd": "tHost"})
                    self._hosting = True
                #if joining
                elif playerType == 'j':
                        #ask for the name of the host
                        hostName = await ainput("Enter the host's username: ")
                        #send a join command to the host
                        await self._client.send({"from": self._name, "to": hostName, "cmd": "tJoin"})
                else:
                    raise hostError
            except hostError:
                print("incorrect input, please enter 'h' or 'j'")

            # while the client hasn't got an opponent
            while not self._opponent:
                # wait for a message from the server
                message = await self._client.recv()
                # get the value from the key 'cmd' in the dictionary 'message', if the is no key 'cmd' return 'None' as the value
                cmd = message.get("cmd", None)

                if cmd == "tHost":
                    # if there is a host command, let clients know who's hosting
                    print(f'{message.get("from", None)} is waiting for opponent...')
                elif cmd == "tJoin" and message.get("to", None) == self._name and self._hosting and not self._opponent:
                    # if there is a join command check if it is directed to this client
                    # ask if the client wants to accept the match
                    accepted = ""
                    while accepted != "y" and accepted != "n":
                        accepted = await ainput(f'Accept match from {message.get("from", None)}? [y|n]\n')
                        # if the match is accepted set opponent to the sender and send an acknowledgment to the opponent
                        if accepted == "y":
                            # let the joiner know the match has been accepted
                            await self._client.send({"from": self._name, "to": message.get("from", None), "cmd": "acc"})
                            # set the opponent
                            self._opponent = message.get("from", None)
                        elif accepted == "n":
                            # let the joiner know the match has been rejected
                            await self._client.send({"to": message.get("from", None), "from": self._name, "cmd": "rej"})
                        else:
                            print("invalid input")
                elif cmd == "acc" and self._name == message.get("to", None):
                    # if the client receives an accept message
                    # let the user know their match has been accepted
                    print("match request accepted")
                    # set the clientTurn to false as the joiner has the second turn
                    self._clientTurn = False
                    # set the opponent
                    self._opponent = message.get("from", None)
                elif cmd == "rej" and self._name == message.get("to", None):
                    # let the user know their match has been rejected and ask them for a new host username
                    print("match request rejected")
                    # ask for the name of the host
                    hostName = await ainput("Enter the host's username: ")
                    # send a join command to the host
                    await self._client.send({"from": self._name, "to": hostName, "cmd": "tJoin"})

        # while the game is not won
        while not self._Game.getWinner:
            # print the board
            print(self._Game)
            if self._clientTurn:
                # if its my turn
                # notify whose turn it is
                if not self._client:
                    print(f"{self._Game.getPlayer} to play...")
                else:
                    print(f"Your turn...")

                # type check
                try:
                    column = await ainput("Enter column number to drop counter: ")
                    column = int(column)
                except ValueError:
                    print("\n\n\n\nERROR: invalid input: expected integer")
                    continue
                # range check
                if 1 <= column <= 7:
                    try:
                        self._Game.play(column)
                    except gameError:
                        # column full error
                        print("\n\n\n\nERROR: column full")
                else:
                    print("\n\n\n\nERROR: input must be between 1 and 7 inclusive")

                if self._client:
                    # if playing a networked game, send the move to the opponent
                    await self._client.send({"from": self._name, "to": self._opponent, "cmd": "move", "col": column})
            else:
                # if its the opponents turn
                # print whose turn it is
                print(f"{self._opponent}'s turn, please wait...")
                col = -1
                while col == -1:
                    # wait for a message from the server
                    message = await self._client.recv()
                    cmd = message.get("cmd", None)
                    # if the message is a move command directed to this client
                    if cmd == "move" and message.get("to", None) == self._name:
                        # get the move
                        col = message.get("col", -1)
                self._Game.play(col)

            if self._client:
                # if the client is playing a networked game flip the turn
                self._clientTurn = True if not self._clientTurn else False

        # when somebody has won, print the board
        print(self._Game)
        # get the winner
        winner = self._Game.getWinner
        # print the game end message
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
