import json, os

import clingo

import Checker
import SolverConfig
from windows.Constants import *


class Solver():

    def __init__(self, encoding, instance):
        self.encoding = encoding
        self.instance = instance

        self.control = clingo.Control(SolverConfig.options)
        self.control.load(instance)
        self.control.load(encoding)

        self.grounded = 0

        #self.imin = self.get(self.control.get_const("imin"), clingo.Number(0))
        self.imax = self.get(self.control.get_const("imax"), clingo.Number(100))
        self.istop = self.get(self.control.get_const("istop"), clingo.String("SAT"))

        self.elevAmt = self.control.get_const("agents").number

        self.step, self.ret = 1, None
        self.solved = False

        self.grounded = 0
        self.solvingStep = 0

        # lists for externals
        self.moved = []
        self.newRequests = []

        # full solution for the last solve call
        self.completePlan = []

        # stat recording vars

        self.totalSolvingTime = Stat(name = "Total Solving Time", val = 0)
        self.totalGroundingTime = Stat(name = "Total Grounding Time", val = 0)
        self.checkErrors = CheckerStat(name="Checker Status")
        self.reqs = RequestStat(name="Current Requests")

        self.groundStart()

        self.checker = Checker.Checker(SolverConfig.checker)

        self.getInitialReqs()

    def get(self, val, default):
        return val if val != None else default


    def getInitialReqs(self):

        self.reqs.val = []

        for x in self.control.symbolic_atoms:
            if x.is_fact:
                atom = x.symbol
                if atom.name == "holds":
                    if atom.arguments[0].name == "request":
                        self.reqs.val.append(atom)

    def groundStart(self):
        """
        Have to call this if something is to be added at time 0, E.G requests
        :return: void
        """

        if self.grounded == 0 and self.step == 1:
            self.control.ground([("base", []), ("init", []), ("step", [self.step]), ("check", [self.step])])
            self.grounded = 1

    def solve(self):

        self.solved = False

        self.ret = None
        self.lastMove = None
        #add the last actions
        for move in self.moved:
            self.control.assign_external(move, True)

        for req in self.newRequests:
            self.control.assign_external(req, True)

        #self.newRequests = []

        while (self.step < self.imax.number) and\
                (self.ret == None or (self.istop.string == "SAT" and not self.ret.satisfiable)):

            #this is here in case the groundStart function was not called before
            if self.grounded == 0 and self.step == 1:
                self.control.ground([("base", []), ("init", []), ("step", [self.step]), ("check", [self.step])])
                self.grounded = 1
            #####

            elif self.grounded < self.step:
                parts = []
                parts.append(("check", [self.step]))
                parts.append(("step", [self.step]))
                self.control.cleanup()

                self.control.ground(parts)

                self.grounded += 1

            self.control.assign_external(clingo.Function("query", [self.step]), True)
            self.ret = self.control.solve(self.on_model)
            self.control.release_external(clingo.Function("query", [self.step]))

            self.step = self.step + 1

    def on_model(self, model):

        print "Model found\n"
        #increase solving step and set the step var to this value so that on the next solve call it starts solving there.
        self.solvingStep += 1
        self.step = self.solvingStep

        # update stat recording of the current step and stat var for the solving status is made true
        self.solved = True

        self.completePlan = []
        for atom in model.symbols(atoms = True):
            if atom.name == "do":
                self.completePlan.append(atom)

        self.reqs.val = []
        for atom in model.symbols(atoms=True):
            if atom.name == "holds":
                if atom.arguments[0].name == "request":
                    self.reqs.val.append(atom)

        if os.path.isfile(SolverConfig.checker):
            # check model
            # convert shown atoms (which should be the actions) into a list of strings
            self.checker.checkList(self.instance, [a.__str__() for a in self.completePlan])
            self.checkErrors.val = self.checker.shownAtoms


        if SolverConfig.printAtoms:
            self.printAtoms(model.symbols(atoms=True))

    def actionFilter(self, atom):
        """
        Filters an action atom of the form do(E,A,T) and return the elevator number and action type
        :param atom: Action atom do(E,A,T)
        :return: elevator number, action type
        """
        elevator = atom.arguments[0].arguments[0].number

        action = atom.arguments[1]

        if action.name == "serve":
            actionType = SERVE
        elif action.name == "wait":
            actionType = WAIT
        elif action.arguments[0].number == 1:
            actionType = UP
        elif action.arguments[0].number == -1:
            actionType = DOWN
        else:
            print "Invalid action"

        return elevator, actionType

    def callSolver(self, step=None):
        """
        This is the main call to the solver. Parameter step is used for solve calls after the first one.
        :param step: Must be the amount of steps that were already executed. Adds the action up to this number to the history. Leave as None for the first call.
        :return: void
        """
        print "Solving... \n"
        if step is not None and self.solved:
            self.updateHistory(step)
        self.solve()
        #self.stats()
        print "Finished Solving.\n"

    def solveFullPlan(self):
        """
        Use this to only solve and print the full plan
        """

        self.solve()
        for a in self.completePlan:
            print a

    def getFullPlan(self):
        """
        This returns the full plan as a dictionary. Each key is the time step. The value of the key is a list of lists that contain the elevator ID and the action
        :return: Plan dictionary
        """

        plan = {}

        for action in self.completePlan:
            elevator, actionType= self.actionFilter(action)
            time = action.arguments[-1].number

            if time not in plan:
                plan[time] = []

            plan[time].append([elevator, actionType])


        return plan


    def updateHistory(self, step):
        """
        Updates the History of actions that will be added to the solver as externals
        :param step: The last time step where actions will be added
        :return: void
        """

        for action in self.completePlan:
            time = action.arguments[-1].number
            if time >= self.solvingStep and time <= step:
                self.moved.append(clingo.Function("history", action.arguments))

        self.solvingStep = step
        self.step = step

    def printAtoms(self, atoms):
        # This is mostly for debugging encoding
        # atoms is usually a list of all atoms in the model
        # use model.symbols(atoms=True) as parameter inside the on_model function to give the full atom list
        goal = None

        for atom in atoms:
            if atom.name == "holds":
                if atom.arguments[0].name == "request" and atom.arguments[-1].number == self.solvingStep:
                    print atom
                if atom.arguments[0].name == "at" and atom.arguments[-1].number == self.solvingStep:
                    print atom

            if atom.name == "goal":
                if goal != None:
                    if atom.arguments[0] > goal.arguments[0]:
                        goal = atom
                else:
                    goal = atom


        print goal

    def addRequest(self, reqtype, time, params):
        """
        Create a clingo function object for the request and add it  to the request list of externals.

        :param reqtype: either call or deliver, it should be as the ones defined in the Constants.py file.
        :param time: time at which the request is added
        :param params: parameters of the request. Differs depending on the type. Either direction and destination for CALL requests
                       or elevator ID and destination for DELIVER requests
        :return: void
        """
        if self.solvingStep == 0:
            requestTime = 1
        else:
            requestTime = time


        if reqtype == REQ_CALL:
            request = clingo.Function("callrequest", [clingo.Function(params[0]), params[1], requestTime])

        if reqtype == REQ_DELIVER:
            request = clingo.Function("deliverrequest", [params[0], params[1], requestTime])

        print "Request " + str(request) + " has been added."
        self.newRequests.append(request)

    def stats(self):
        """
        Update the stats. Called after each solver call.
        :return: void
        """
        statistics = json.loads(json.dumps(self.control.statistics, sort_keys=True, indent=4, separators=(',', ': ')))

        solve = statistics["summary"]["time_solve"]
        ground = statistics["summary"]["time_total"] - self.control.stats["summary"]["time_solve"]

        #record stats

        self.totalSolvingTime.val += float(solve)
        self.totalGroundingTime.val += float(ground)



    def getRequestInfo(self):
        """
        Returns the requests as a dictionary similarly to the getFullPlan function.
        Each key is the time point with the value being a list containing the requests as strings
        :return: Request as a dictionary
        """
        reqs = {}

        for req in self.reqs.val:
            time = req.arguments[-1].number

            reqatom = req.arguments[0]
            reqtype = str(reqatom.arguments[0])
            dest = str(reqatom.arguments[1])

            if time not in reqs:
                reqs[time] = []

            if reqtype[:4] == "call":
                middle = " from "
            else:
                middle = " to "

            string = reqtype + middle + dest
            reqs[time].append(string)

        return reqs

    def getStats(self):
        # order matters if being used by the InfoPanel class of the visualizer
        return [self.totalSolvingTime,
                self.totalGroundingTime,
                self.checkErrors]


class Stat(object):

    def __init__(self, name = "", val = None):

        self.name = name
        self.val = val

    def string(self):
        return self.name + " = " + str(self.val)


class CheckerStat(Stat):

    def string(self):
        string = ""
        if self.val is not None:
            for i in self.val:
                string += str(i)+"\n"

        else:
            string = str(self.val)

        return self.name + " = " + string

class RequestStat(Stat):

    def string(self):
        string = ""
        if self.val is not None and self.val != []:
            for i in self.val:
                reqatom = i.arguments[0]
                reqtype = str(reqatom.arguments[0])
                dest = str(reqatom.arguments[1])

                if reqtype[:4] == "call":
                    middle = " from "
                else:
                    middle = " to "

                string += reqtype + middle + dest + "\n"
        else:
            string = "None"

        return self.name + " = " + string


if __name__ == "__main__":
    s = Solver("Elevator.lp", "Elevatorinstance.lp")
    s.callSolver()
