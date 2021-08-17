from abc import ABC, abstractmethod
from tkinter import Tk, Frame, Button, X, Toplevel, N, S, E, W, Grid, Canvas, StringVar, Listbox, Label, END, UNITS, HORIZONTAL, Scale, LEFT, RIGHT, OptionMenu, Entry
from game import game, gameError
from time import sleep
from players import Ai
from client import client
from aioconsole import ainput
from time import localtime, time
from asyncio import sleep as s
from asyncio import get_event_loop
from sqlite3 import IntegrityError


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
        self.__gameOver = False
        self.__animating = False
        self._opponent = None
        self.__opponentType = StringVar(value="Human")
        self.__waitingForHost = False
        self.__waitingForJoin = False
        self.__waitingForMove = False
        self.__client = client()
        self._clientTurn = True
        
        Button(frame, text="Help", command=self._help).pack(fill=X)
        Button(frame, text="Play", command=self._gametype).pack(fill=X)
        Button(frame, text="Quit", command=self._quit).pack(fill=X)

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
            Button(frame, text="Dismiss", command=self._dismissTypeChoice).pack(fill=X)

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

            # load button
            Button(frame, text="Load", command=self._load).grid(row=1, column=0, columnspan=2)

            # play button
            Button(frame, text="Play", command=self._play).grid(row=2, column=0, columnspan=2)

            # back button
            Button(frame, text="Back", command=self._dismissSetup).grid(row=3, column=0, columnspan=2)

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
            Button(frame, text="Save", command=self._loadGame).pack(fill=X)
            # console
            console = Listbox(frame, height=3)
            console.pack(fill=X)
            self.__loadConsole = console
            # self.__loadConsole.insert(END, f"1| ")
            # cancel button
            Button(frame, text="Cancel", command=self._cancelLoad).pack(fill=X)

    def _loadGame(self):
        pass

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
            # if the opponent is not human, create an AI object
            if self.__opponentType.get() != "Human":
                self.__opponent = Ai(self.__opponentType.get())
            self.__gameInProgress = True
            # create a game object
            self.__game = game()

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
                self.__playerTurn.set('RED TO PLAY\nCHOOSE COLUMN')
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
            elif winWidth > 110:
                # max board tile size
                winWidth = 110
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
                    # create white circles on blue background
                    oval = board.create_oval(baseX1 + (column*tile), baseY1 + (row*tile), baseX2 + (column*tile), baseY2 + (row*tile), fill="white")# , dash=(7,1,1,1)
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
            self.__game.save(self.__gameName)
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
        # if a counter is falling or the client is waiting for the opponent to move, print a wait message
        if self.__animating or not self._clientTurn:
            self.__gameConsole.insert(END, f"{self.__gameConsole.size() + 1}| please wait...")
            if self.__gameConsole.size() > 3:
                self.__gameConsole.yview_scroll(1, UNITS)

        # if the game isn't won and its the client's move
        elif not self.__game.getWinner:
            try:
                # set the counter colour
                counter = 'red' if self.__game.getPlayer == game.PONE else '#e6e600'
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
                    counter = 'RED' if self.__game.getPlayer == game.PONE else 'YELLOW'
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
                counter = 'red' if self.__game.getPlayer == game.PONE else '#e6e600'
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
                winner = 'RED' if self.__game.getWinner == game.PONE else 'YELLOW'
                if self.__opponentType.get() == "Human":
                    winner = 'RED' if self.__game.getWinner == game.PONE else 'YELLOW'
                    self.__playerTurn.set(f'{winner} HAS WON\nCONGRATULATIONS!')
                else:
                    winner = 'YOU' if self.__game.getWinner == game.PONE else 'OPPONENT'
                    self.__playerTurn.set(f'{winner} WON\nGOOD GAME!')
            else:
                self.__playerTurn.set(f'THE GAME WAS DRAWN')

            # highlight winning run
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
