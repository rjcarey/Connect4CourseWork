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
            print("initialising terminal mode...")
        elif argv[1] == "g":
            print("initialising gui mode...")
        else:
            usage()
    else:
        usage()
