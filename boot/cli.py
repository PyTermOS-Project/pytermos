# PyTerm is now the base of PyTermOS! I changed everything for it to be suitable for ShellOS.
import cmd

class PyTermOS(cmd.Cmd):
    intro = 'Welcome to PyTermOS. Type help or ? or help to list commands.'
    prompt = 'pytermos> '

    def do_exit(self, line):
        "Exit the shell. (exit or exit -h)"
        if line.strip() == "-h":
            print("Exit is a command that sends you back to bash. Basically it just ends the program.")
        else:
            return True

    def do_help(self, line):
        "Show this help message."
        if line.strip() == "-h":
            print("Help is a command that let's you see all the commands in PyTerm.")
        else:
            super().do_help(line)

    def do_type(self, line):
        "Type something and it gets printed back to you."
        if line.strip() == "-h":
            print("Type is a command that copies the text you've already written. I know, it's unuseful but someone would like it.")
        else:
            print(line)

    def do_info(self, line):
        "Display information about PyTerm."
        if line.strip() == "-h":
            print("Info is a command that let's you see all info-data about PyTerm.")
        else:
            print("""
PPPP   y   y  TTTTT  EEEE  RRRR  M   M
P   P   y y     T    E     R   R MM MM
PPPP     y      T    EEE   RRRR  M M M
P        y      T    E     R  R  M   M
P        y      T    EEEE  R   R M   M
                            Operating System

    PyTerm v0.1.0-stable
    Python: v3.8
    Version Created: Twenty-Fourth April 2024
    Initial Day Of Creation: Twenty-Third April 2024
    Operating System: PyTermOS v0.1.0-alpha
            """)

    def do_super(self, line):
        "Activate supermode that lets you use supercommands."
        password = "etsugenfgr"
        enter = input("Password:") 
        if enter == password:
            print("You are now in super mode. Type 'superhelp' for help.")
            return SuperCmd().cmdloop()
        else:
            print("PyTerm error: wrong password.")

class SuperCmd(cmd.Cmd):
    prompt = 'SuperMode> '

    def do_supertype(self, line):
        "Echo back the input string twice."
        print(line + line)

    def do_superexit(self, line):
        "Exit from super mode."
        print("Superexiting...")
        return True

    def do_superinfo(self, line):
        "Show information about super mode."
        print("""
    PPPP   y   y  TTTTT  EEEE  RRRR  M   M 
    P   P   y y     T    E     R   R MM MM       
    PPPP     y      T    EEE   RRRR  M M M       
    P        y      T    E     R  R  M   M      
    P        y      T    EEEE  R   R M   M 
                                Operating System
                                        SUPER MODE

        PyTerm Supermode v1.0
        Python: v3.8
        Version Created: Twenty-Fourth April 2024
        Initial Day Of Creation: Twenty-Third April 2024
        Application: PyTermOSCLIOS v0.1.0-alpha
        """)

    def do_superhelp(self, line):
        "Show help for super mode commands."
        print("Commands: supertype, superexit, superinfo, superhelp. Add-ons: -h")

if __name__ == '__main__':
    PyTermOS().cmdloop()