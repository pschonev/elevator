import clingo
import tempfile
import os, sys

import argparse



class Checker(object):
    """
    Object to check a plan for a domain. It is usually created with the checker script as argument
    and for every check the instance and plan is given to a fucntion.
    """
    def __init__(self, checkerEncoding):
        self.checkerEnc = checkerEncoding

        self.hasErrors = False
        self.shownAtoms = []

    def checkStr(self, instance, actions):
        """
        Should not be used for now.

        Checks the plan given as a string as outputted by clingo without incremental solving(actions separated by a white space.
        It replaces the whitespace in between them to a dot and then writes a file. Then the solver is called.
        :param instance: file name of instance
        :param actions: actions separated by whitespace. Must be in the clingo input format
                        and have the form "do(elevator(ID),A,T)" with ID and int, A an action, and T the time step
        :return: void
        """
        tp = tempfile.NamedTemporaryFile()

        tp.write("#program base.\n")

        if type(actions) == str:
            tp.write(actions.replace(" ", "."))
        elif type(actions) == list:
            for line in actions:
                tp.write(line + ".")

        tp.read()

        control = clingo.Control()
        control.load(instance)
        control.load(tp.name)
        control.load(self.checkerEnc)

        self.solve(control)

        tp.close()

    def checkList(self, instance, actions):
        """
        Takes a list of actions formatted correctly ( E.G. do(elevator(1),serve,1) ) and writes them into a file. It calls the solver and finally deletes the file.

        :param instance: file name of instance
        :param actions: list of actions
        :return: void
        """
        tempname = "temp.lp"

        with open(tempname, "w") as t:
            t.write("#program base.")
            for line in actions:
                t.write(line + ".")

        control = clingo.Control()
        control.load(instance)
        control.load(tempname)
        control.load(self.checkerEnc)

        self.solve(control)

        os.remove("temp.lp")

    def checkFile(self, instance, path):
        """
        Takes a file with the actions in it and checks the plan.

        :param instance: file name of instance
        :param path: path to the file with the actions
        :return: void
        """
        control = clingo.Control()
        control.load(instance)
        control.load(path)
        control.load(self.checkerEnc)

        self.solve(control)


    def solve(self, control):
        """
        takes a clingo control argument, ground it and solves it.
        :param control: clingo controls argument
        :return: void
        """

        control.ground([("base", [])])
        control.solve(self.on_model)

    def on_model(self, model):
        """
        Callback to clingo solve call.
        prints the shown atoms in the model

        :param model: model given by the clingo solve function
        :return: void
        """
        self.shownAtoms = []
        print "Checking model... \n"

        for atom in model.symbols(shown=True):
            if atom.name == "error":
                self.hasErrors = True
            if atom.name == "error" or atom.name =="noerror":
                self.shownAtoms.append(str(atom))
                print atom

        print "\nFinished Checking.\n"

if __name__ == "__main__":

    desc = "Checks a plan for an elevator domain for correctness. It takes as input a list of actions, " \
           " or a file with the actions in it. " \
           "If there is an error it ouputs the type of error, the elevator that has the error, and the time step it happened in."

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("checker", help="Encoding that implements the checker.")
    parser.add_argument("instance", help="Instance for which the plan was calculated.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", help="Actions in a file.")
    group.add_argument("-a", "--a-list", nargs="+", help="List of actions correctly formatted as atom. E.G do(elevator(1),move(1),1). The dot is not needed.")


    args = parser.parse_args()

    c = Checker(args.checker)
    if args.file != None:
        c.checkFile(args.instance, args.file)
    elif args.a_list != None:
        c.checkList(args.instance, args.a_list)
    else:
        print "ERROR : there must be a file or a list of actions as argument!\nExiting..."
        sys.exit()


    #testing
    #c.checkStr("Elevatorinstance2.lp", "do(elevator(1),move(-1),1) do(elevator(1),move(-1),2) do(elevator(1),move(-1),3) do(elevator(1),move(-1),4).")
    #c.checkList("Elevatorinstance2.lp", [ "do(elevator(1),move(1),1)", "do(elevator(1),move(-1),2)", "do(elevator(1),move(-1),3)" ] )
    #c.checkStr("Elevatorinstance2.lp", [ "do(elevator(1),move(-1),1)", "do(elevator(1),move(-1),2)", "do(elevator(1),move(-1),3)" ] )


    #c.checkFile("Elevatorinstance2.lp", "temp.lp")