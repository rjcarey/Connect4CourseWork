from ui import terminal, gui
from sys import argv

def usage():
    print(f"Error: Incorrect run command\nCommand: ConnectFour.py [g | t | tn]\ng : play with the GUI\nt : play with the Terminal\ntn : play LAN on the Terminal")
    quit()

network = False

if __name__ == "__main__":
    if len(argv) == 2:
        if argv[1] == "t":
            print("initialising terminal mode...\n")
            ui = terminal()
        elif argv[1] == "g":
            print("initialising gui mode...\n")
            ui = gui()
        elif argv[1] == "tn":
            print("initialising terminal LAN mode...\n")
            network = True
            ui = terminal()
        else:
            usage()
    else:
        usage()

    ui.run()
    if argv[1] == "t":
        while True:
            choice = " "
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
            ui = terminal()
            ui.run()
