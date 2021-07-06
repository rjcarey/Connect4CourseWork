from ui import terminal, gui
from sys import argv

def usage():   
    print(f"""
Error: Incorrect run command
Command: ConnectFour.py [g | t]
g : play with the GUI
t : play with the Terminal""")
    quit()

if __name__ == "__main__":
    if len(argv) == 2:
        if argv[1] == "t":
            print("initialising terminal mode...\n")
            ui = terminal()
        elif argv[1] == "g":
            print("initialising gui mode...\n")
            ui = gui()
        else:
            usage()
    else:
        usage()

    ui.run()
    while True:
        choice = " "
        while choice != "y" and choice !="n":
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