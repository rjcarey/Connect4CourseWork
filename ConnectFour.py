from ui import terminal, gui
from sys import argv
from asyncio import run, create_task, gather


def usage():
    # print how the game should be booted and then quit the program
    print(f"Error: Incorrect run command\nCommand: ConnectFour.py [g | t | tn | gn]\ng : play with the GUI\nt : play with the Terminal\ntn : play LAN on the Terminal\ngn : play LAN on the GUI")
    quit()


async def startGame():
    network = False
    ui = terminal(network)
    if len(argv) == 2:
        if argv[1] == "t":
            # if the user entered 't' create a terminal object
            print("initialising terminal mode...\n")
            ui = terminal(network)
        elif argv[1] == "g":
            # if the user entered 'g' create a gui object
            print("initialising gui mode...\n")
            ui = gui(network)
        elif argv[1] == "tn":
            # if the user entered 'tn' set network to true and create a terminal object
            print("initialising terminal LAN mode...\n")
            network = True
            ui = terminal(network)
        elif argv[1] == "gn":
            # if the user entered 'gn' set network to true and create a gui object
            print("initialising gui LAN mode...\n")
            network = True
            ui = gui(network)
        else:
            # if the user didn't enter any of the above options then call the usage method
            usage()
    else:
        # if the user didn't launch with the correct number of arguments then call the usage method
        usage()
    # create a list of tasks starting with running the ui
    tasks = [create_task(ui.run())]
    # if playing the networked version, add running the client to the list of tasks
    if network:
        tasks.append(create_task(ui.runClient()))
    await gather(*tasks)

    # if the user wanted to play the over the terminal, check if the user wants to play again
    if argv[1] == "t":
        while True:
            choice = ""
            while choice != "y" and choice != "n":
                try:
                    choice = input("y: Play Again\nn: Quit\nEnter [y|n]: ")
                    if choice != "y" and choice != "n":
                        raise ValueError
                except ValueError:
                    print("\n\n\n\nERROR: enter 'y' or 'n'")
                    continue
            if choice == "n":
                break
            ui = terminal(network)
            tasks = [create_task(ui.run())]
            await gather(*tasks)

if __name__ == "__main__":
    # run the game
    run(startGame())
