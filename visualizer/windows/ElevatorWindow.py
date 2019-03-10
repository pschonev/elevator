from PyQt4 import QtGui, QtCore

import EncodingManager
import SolverConfig, VisConfig
from Constants import *

import os, time


class ElevatorVis(QtGui.QWidget):
    """Visualizer Class for an individual Elevator"""
    def __init__(self, size):
        """
        :param size: size of the squares
        """
        super(ElevatorVis, self).__init__()

        self.size = size

        # data
        self.floors = None
        self.currentFloor = None
        self.lastAction = None

        # this should be changed. Generally x stays at 0 but y must best the amount of floors time the size of the floors in pixels.
        self.xpos = 0
        self.ypos = 0

        # images for the actions
        self.actionpic = QtGui.QLabel(self)
        self.imagedict = {}
        self.imagedict[UP] = QtGui.QPixmap(os.getcwd() + "/res/uparrow.png")
        self.imagedict[DOWN] = QtGui.QPixmap(os.getcwd() + "/res/downarrow.png")
        self.imagedict[WAIT] = QtGui.QPixmap(os.getcwd() + "/res/stay.png")
        self.imagedict[SERVE] = QtGui.QPixmap(os.getcwd() + "/res/serve.png")
        self.imagedict[NONEACT] = QtGui.QPixmap(os.getcwd() + "/res/none.png")

    def setDrawPos(self, x, y):
        """
        :param x: usually left as 0 as the pyQT widget superclass takes over the x positioning.
        :param y: should be the position when on floor 1 (ground floor), basically the height of the whole elevator "shaft"
        :return: void
        """

        self.xpos = x
        self.ypos = y

    def paintEvent(self, QPaintEvent):
        qp = QtGui.QPainter()
        qp.begin(self)

        self.drawWidget(qp)

        qp.end()
        time.sleep(0.01)

    def updateElevator(self, elevator):
        """
        Get elevator data object to display on the next draw call
        :param elevator: elevator data object
        :return: void
        """
        self.floors = elevator.floors
        self.currentFloor = elevator.currentFloor
        self.lastAction = elevator.lastAction
        self.update()

    def drawWidget(self, qp):

        color = QtGui.QColor(0, 0, 0)
        qp.setPen(color)

        #draw floor squares plus numbers
        qp.drawLine(self.xpos, self.ypos, self.xpos, self.ypos - self.floors * self.size)
        qp.drawLine(self.xpos + self.size, self.ypos, self.xpos + self.size, self.ypos - self.floors * self.size)

        for f in range(0, self.floors + 1):
            y = self.ypos - f * self.size
            qp.drawLine(self.xpos, y, self.xpos + self.size, y)

            if f != self.floors:
                qp.setFont(QtGui.QFont('Decorative', 15))
                text = "%d" %(f+1)
                #NOTE the x and y pos for the text is the BOTTOM LEFT part
                qp.drawText(self.xpos + 2, y - 2, text)

        if self.lastAction == SERVE:
            qp.setBrush(QtGui.QColor(0, 200, 0))
        else:
            qp.setBrush(QtGui.QColor(200, 0, 0))

        #the +2 and -4 are to make the elevator square a bit smaller than the floor box
        #should probably add a variable for those :v
        qp.drawRect(self.xpos + 2, self.ypos + 2 - self.currentFloor * self.size, self.size - 4, self.size - 4)

        # draw image of last action
        if self.lastAction != None:
            self.actionpic.setPixmap(self.imagedict[self.lastAction])

        # the +15 after ypos is to separate the image from the elevator a bit
        self.actionpic.setGeometry((self.size-32)/2, self.ypos + 15, self.size, self.size)

class Elevator():
    """
    Elevator data class. Keeps track of the elevator position.
    """
    def __init__(self, floors, startPos):
        """

        :param floors: total amount of floors
        :param startPos: starting floor
        """
        self.floors = floors
        self.step = 0
        self.lastStep = 0
        self.history = [startPos]

        self.moveDict = {}
        self.moveDict[UP] = 1
        self.moveDict[DOWN] = -1
        self.moveDict[WAIT] = 0
        self.moveDict[SERVE] = 0
        self.moveDict[NONEACT] = 0


        self.actionHistory = [NONEACT]

    def execute(self, action):
        """
        Only needs to know where to move. So depending on the action is goes up, down or stays.
        This should only be called with a new action that directly follows the last one completed
        :param action: Action as defined in the Constants.py file
        :return: void
        """
        currentFloor = self.history[self.lastStep]
        self.actionHistory.append(action)
        if action == DOWN and currentFloor == 1:
            print "Invalid move, trying to move down when already at the bottom floor."
            return

        if action == UP and currentFloor == self.floors:
            print "Invalid move, trying to move up when already at the top floor."
            return

        self.history.append(self.currentFloor + self.moveDict[action])

        self.lastStep += 1

    def next(self):
        if self.step < self.lastStep:
            self.step += 1

    def previous(self):
        if self.step > 0:
            self.step -= 1

    @property
    def currentFloor(self):
        return self.history[self.step]

    @property
    def lastAction(self):
        return self.actionHistory[self.step]

class ElevatorInterfaceVis(QtGui.QWidget):
    """ Visualizer for the whole instance. Keeps track of every elevator in the instance."""
    def __init__(self, size):
        """
        Initialize core visualization stuff. It is necessary to pass the data object to the initialize function after creating the object
        :param encoding: encoding
        :param instance: instance
        :param size: size of the squares that represent the floors, usually defined in the VisConfig.py file
        """
        super(ElevatorInterfaceVis, self).__init__()

        self.size = size

        #distance between elevator shafts
        self.elevatorSeparation = 20

        self.hbox = QtGui.QHBoxLayout()

        self.setLayout(self.hbox)


    def initialize(self, elevatorInterface):

        # calculate the total height of the shaft
        self.ypos = self.size * elevatorInterface.floors

        self.setElevVis(elevatorInterface.elevatorCount, elevatorInterface.floors)
        self.updateElevators(elevatorInterface)


    def setElevVis(self, elevatorCount, floors):
        """
        Create a visualizer for every elevator in the instance and add it to the layout.
        """
        self.elevatorsVis = []
        for i in range(elevatorCount):
            vis = ElevatorVis(self.size)
            vis.setDrawPos(0, self.ypos)
            # the +2 after the floors thing is to also include the images
            vis.setMinimumSize(self.size + 4, self.size * (floors + 2) + 4)

            self.elevatorsVis.append(vis)
            self.hbox.addWidget(vis)


    def updateElevators(self, elevatorInterface):
        """
        updated object needs to be passed to the individual elevator visualizers.
        """

        for i in range(0, len(self.elevatorsVis)):
            self.elevatorsVis[i].updateElevator(elevatorInterface.elevators[i])

    def reset(self):
        """
        Resets the whole interface and deletes the old elevator visualizers from the layout container. Then, it creates everything again
        """
        for i in reversed(range(self.hbox.count())):
            self.hbox.itemAt(i).widget().setParent(None)




class ElevatorInterface(QtCore.QObject):
    """
    Data class for the whole instance. Keeps track of every individual elevator.
    """

    planChangedSignal = QtCore.pyqtSignal(dict)
    requestChangedSignal = QtCore.pyqtSignal(dict, dict)

    def __init__(self):
        """
        Parameters usually in the VisConfig.py file
        :param id : id of the solver to be used.
        """

        super(ElevatorInterface, self).__init__()

        self.bridge = Connect()

        self.elevatorCount = self.bridge.getElevatorAmt()
        self.floors = self.bridge.getFloorAmt()

        self.step = 0
        self.highestStep = 0
        self.planLength = 0

        self.setElevators()

        self.plan = {}
        self.requestInfo = self.bridge.getRequests()
        self.addedRequests = {}

        self.requestsServed = {}

        self.hasToSolve = True

    def setElevators(self):
        """
        Create elevator data object for every elevator
        """
        self.elevators = []

        for i in range(1, self.elevatorCount + 1):
            elevatorStart = self.bridge.startingPosition(i)
            elevator = Elevator(self.floors, elevatorStart)

            self.elevators.append(elevator)


    def next(self):
        """
        Solves if it needs to solve
        go to the next step, if it has not been executed -> give the action to elevator to execute it
                             if it has been executed -> increase step counter by one
        Then, call the next function on every elevator
        """

        if self.hasToSolve:
            self.solve()
            self.hasToSolve = False



        if len(self.plan) > self.step:
            self.step += 1

            if self.step - 1 == self.highestStep:
                self.highestStep += 1

                moves = self.plan[self.step]
                for move in moves:
                    # get elevator ID
                    elevator = move[0]
                    action = move[1]
                    self.elevators[elevator - 1].execute(action)



            for e in self.elevators:
                e.next()


    def previous(self):
        """
        Lowers step value. if counter is at 1 (lowest) -> do nothing
        :return:
        """

        if self.step >= 1:
            self.step -= 1

            for e in self.elevators:
                e.previous()



    def solve(self):
        self.plan = self.bridge.nextMoves(self.highestStep)
        self.planLength = max(self.plan)

        self.fillPlan()

        self.requestInfo = self.bridge.getRequests()
        if len(self.requestInfo) != 0:
            self.addedRequests[0] = self.requestInfo[0]

        self.parseRequests()

        self.planChangedSignal.emit(self.plan)
        self.requestChangedSignal.emit(self.requestsServed, self.addedRequests)

    def fillPlan(self):
        """
        Fills the spots in the plan with no actions to contain a NONEACT.
        """

        for t in range(1, self.planLength + 1):
            if t in self.plan:
                if len(self.plan[t]) != self.elevatorCount:
                    elevs = range(1, self.elevatorCount+1)
                    for move in self.plan[t]:
                        elevs.remove(move[0])

                    for e in elevs:
                        self.plan[t].append([e, NONEACT])
            else:
                elevs = range(1, self.elevatorCount + 1)
                self.plan[t] = []
                for e in elevs:
                    self.plan[t].append([e, NONEACT])


    def parseRequests(self):

        self.requestsServed = self.requestInfo.copy()

        for time in self.requestInfo:
            completed = []
            if time+1 in self.requestInfo:
                for req in self.requestInfo[time]:
                    if req not in self.requestInfo[time+1]:
                        completed.append(req)
            else:
                for req in self.requestInfo[time]:
                    completed.append(req)

            self.requestsServed[time+1] = completed

        self.requestsServed[0] = []

    @property
    def requestCompleted(self):
        try:
            return ", ".join(self.requestsServed[self.step])
        except (TypeError, KeyError):
            return "No Requests"

    @property
    def currentRequests(self):
        try:
            return ", ".join(self.requestInfo[self.step])
        except (TypeError, KeyError):
            return "No Requests"


    def addRequest(self, type, *params):
        self.hasToSolve = True
        self.bridge.addRequest(type, self.highestStep, params)

        if type == REQ_CALL:
            string = "call({}) to {}".format(params[0], params[1])
        elif type == REQ_DELIVER:
            string = "deliver({}) from {}".format(params[0], params[1])

        if self.highestStep not in self.addedRequests:
            self.addedRequests[self.highestStep] = [string]
        else:
            self.addedRequests[self.highestStep].append(string)

    def getStats(self):
        """
        It just calls the getStats function from the encoding manager (solver) and return the value
        :return: list of Stat objects
        """

        return self.bridge.getStats()

    def reset(self):
        """
        Creates a new solver object so that it reloads everything.
        The request amount is not used for now.

        It also creates the elevetor object again.
        """
        self.bridge.reset()
        self.elevatorCount = self.bridge.getElevatorAmt()
        self.floors = self.bridge.getFloorAmt()
        self.step = 0
        self.highestStep = 0
        self.planLength = 0

        self.plan = {}
        self.requestInfo = self.bridge.getRequests()
        self.addedRequests = {}

        self.requestsServed = {}

        self.setElevators()

        self.hasToSolve = True


class Interface(QtGui.QWidget):
    """
    Class that should hold the information for the elevator. Currently only has the interface but in the future it should hold the stats aswell.
    """
    def __init__(self, parent = None):
        super(Interface, self).__init__(parent)

        self.elevatorInterface = ElevatorInterface()
        self.elevatorInterfaceVis = ElevatorInterfaceVis(VisConfig.size)
        self.elevatorInterfaceVis.initialize(self.elevatorInterface)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.elevatorInterfaceVis)
        self.scrollArea.setWidgetResizable(True)

        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel = InfoPanel(stats)

        self.hbox = QtGui.QHBoxLayout()

        self.hbox.addWidget(self.scrollArea)
        self.hbox.addWidget(self.infoPanel)

        self.setLayout(self.hbox)

    def updateAll(self):
        self.elevatorInterfaceVis.updateElevators(self.elevatorInterface)
        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel.updateStats(stats)

    def next(self):
        self.elevatorInterface.next()
        self.updateAll()

    def previous(self):
        self.elevatorInterface.previous()
        self.updateAll()

    def reset(self):
        self.elevatorInterface.reset()

        self.elevatorInterfaceVis.reset()
        self.elevatorInterfaceVis.initialize(self.elevatorInterface)

        stats = self.elevatorInterface.bridge.getStats()
        self.infoPanel.updateStats(stats)

class ElevatorWindow(Interface):
    """
    This class just creates a window
    """
    def __init__(self, parent = None):
        super(ElevatorWindow, self).__init__(parent)

        self.setGeometry(VisConfig.width, VisConfig.height, VisConfig.width, VisConfig.height)
        self.setWindowTitle("Instance")
        self.move(0, 0)


class InfoPanel(QtGui.QWidget):

    def __init__(self, labels):
        super(InfoPanel, self).__init__()

        self.separation = 10

        self.stats = {}

        self.vbox = QtGui.QVBoxLayout()

        self.initLabels(labels)

        self.setLayout(self.vbox)

    def initLabels(self, labels):

        for s in labels:
            if s.name not in self.stats:
                # create the label and add it vbox
                label = QtGui.QLabel(s.string(), self)
                self.stats[s.name] = label
                self.vbox.addWidget(label)

        self.vbox.addStretch(-1)

    def updateStats(self, stats):

        for s in stats:
            # update label value
            self.stats[s.name].setText(s.string())


class Connect(object):

    def __init__(self):
        self.instance = SolverConfig.instance
        self.encoding = SolverConfig.encoding
        self.solver = EncodingManager.Solver(self.encoding, self.instance)

        self.elevatorCount = self.solver.control.get_const("agents").number
        self.floors = self.solver.control.get_const("floors").number

    def getElevatorAmt(self):

        return self.solver.control.get_const("agents").number

    def getFloorAmt(self):

        return self.solver.control.get_const("floors").number

    def startingPosition(self, elev):

        return self.solver.control.get_const("start%d" % (elev)).number

    def nextMoves(self, step):

        self.solver.callSolver(step)

        return self.solver.getFullPlan()

    def solveFullPlan(self):
        # only prints the plan cause its printed in the encoding manager
        return self.solver.solveFullPlan()

    def getStats(self):

        return self.solver.getStats()

    def getRequests(self):

        return self.solver.getRequestInfo()

    def addRequest(self, type, time, params):

        self.solver.addRequest(type, time, params)

    def reset(self):
        self.solver = EncodingManager.Solver(self.encoding, self.instance)

        self.elevatorCount = self.solver.control.get_const("agents").number
        self.floors = self.solver.control.get_const("floors").number
