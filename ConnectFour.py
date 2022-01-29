from ui import terminal, gui
from sys import argv
from asyncio import run, create_task, gather


def usage():
    # Print how the game should be booted and then quit the program
    print(f"Error: Incorrect run command\nCommand: ConnectFour.py [g | t | tn | gn]\ng : play with the GUI\nt : play with the Terminal\ntn : play LAN on the Terminal\ngn : play LAN on the GUI")
    quit()


async def startGame(network, ui):
    ui = ui(network)
    # Create a list of tasks starting with running the ui
    tasks = [create_task(ui.run())]
    # If playing the networked version, add running the client to the list of tasks
    if network:
        tasks.append(create_task(ui.runClient()))
    await gather(*tasks)

    # If the user played in normal terminal mode, ask if they want to replay
    if argv[1] == "t":
        while True:
            choice = ""
            while choice != "y" and choice != "n":
                ##########################################################################################
                # EXCELLENT CODING STYLE:                                                                #
                #   ==================================================================================   #
                # Exception Handling: If the user enter neither 'y' nor 'n' report this without crashing #
                ##########################################################################################
                try:
                    choice = input("y: Play Again\nn: Quit\nEnter [y|n]: ")
                    if choice != "y" and choice != "n":
                        raise ValueError
                except ValueError:
                    print("\n\n\n\nERROR: enter 'y' or 'n'")
                    continue
            if choice == "n":
                break
            else:
                # If the user wants to play again, re-add running the ui to the tasks and run the tasks
                ui = terminal(network)
                tasks = [create_task(ui.run())]
                await gather(*tasks)


if __name__ == "__main__":
    network = False
    ui = None
    if len(argv) == 2:
        if argv[1] == "t":
            print("initialising terminal mode...\n")
            ui = terminal
        elif argv[1] == "g":
            print("initialising gui mode...\n")
            ui = gui
        elif argv[1] == "tn":
            print("initialising terminal LAN mode...\n")
            network = True
            ui = terminal
        elif argv[1] == "gn":
            print("initialising gui LAN mode...\n")
            network = True
            ui = gui
        else:
            # If the user didn't enter any of the above options then call the usage method
            usage()
    else:
        # If the user didn't launch with the correct number of arguments then call the usage method
        usage()
    run(startGame(network, ui))
