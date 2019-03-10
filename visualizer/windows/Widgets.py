from PyQt4 import QtGui, QtCore
from functools import partial

from math import ceil

import os

import Constants

class CallRequestDialog(QtGui.QDialog):

    def __init__(self, floorAmt, parent = None,):
        super(CallRequestDialog, self).__init__(parent)

        self.setWindowTitle("Call Request")

        self.cols = 5

        self.type = None
        self.floor = None

        self.mainVBox = QtGui.QVBoxLayout()

        self.reqLabel = QtGui.QLabel()
        self.reqLabel.setText("Direction : {} \nFloor : {}".format(self.type, self.floor))
        self.mainVBox.addWidget(self.reqLabel)

        self.setTypeButtons()
        self.setFloorButtons(floorAmt)

        buttons = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                        QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.mainVBox.addWidget(buttons)

        self.setLayout(self.mainVBox)

        self.show()

    def setTypeButtons(self):

        hbox = QtGui.QHBoxLayout()

        self.upBtn = QtGui.QPushButton("Up", self)
        self.upBtn.clicked.connect(lambda: self.setType(Constants.UPDIR))
        self.upBtn.resize(self.upBtn.sizeHint())
        hbox.addWidget(self.upBtn)

        self.downBtn = QtGui.QPushButton("Down", self)
        self.downBtn.clicked.connect(lambda: self.setType(Constants.DOWNDIR))
        self.downBtn.resize(self.downBtn.sizeHint())
        hbox.addWidget(self.downBtn)

        self.mainVBox.addLayout(hbox)

    def setFloorButtons(self,floorAmt):

        self.grid = QtGui.QGridLayout()

        rows = int(ceil(floorAmt/float(self.cols)))

        self.buttons = {}
        for i in range(0, rows):
            for j in range(0, self.cols):
                if self.cols*i + j+1 <= floorAmt:
                    button = QtGui.QPushButton(str(self.cols*i + j+1))
                    self.buttons[i,j] = button
                    button.clicked.connect(partial(self.setFloor, self.cols*i + j+1))

                    self.grid.addWidget(self.buttons[i,j], i, j)

        self.mainVBox.addLayout(self.grid)

    def setType(self, dir):
        self.type = dir

        self.reqLabel.setText("Direction : {} \nFloor : {}".format(self.type, self.floor))

    def setFloor(self, floor):
        self.floor = floor

        self.reqLabel.setText("Direction : {} \nFloor : {}".format(self.type, self.floor))

    @staticmethod
    def getRequest(floors, parent=None):
        dialog = CallRequestDialog(floors, parent)
        result = dialog.exec_()

        return (result == QtGui.QDialog.Accepted, dialog.type, dialog.floor)

class DeliverRequestDialog(QtGui.QDialog):

    def __init__(self, floorAmt, elevAmt, parent=None, ):
        super(DeliverRequestDialog, self).__init__(parent)

        self.setWindowTitle("Deliver Request")

        self.cols = 5

        self.elevator = None
        self.floor = None

        self.mainVBox = QtGui.QVBoxLayout()

        self.reqLabel = QtGui.QLabel()
        self.reqLabel.setText("Elevator : {} \nFloor : {}".format(self.elevator, self.floor))
        self.mainVBox.addWidget(self.reqLabel)

        self.setElevatorButtons(elevAmt)
        self.setFloorButtons(floorAmt)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                         QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.mainVBox.addWidget(buttons)

        self.setLayout(self.mainVBox)

        self.show()

    def setElevatorButtons(self, elevAmt):

        self.elevatorGrid = QtGui.QGridLayout()

        rows = int(ceil(elevAmt / float(self.cols)))

        self.buttons = {}
        for i in range(0, rows):
            for j in range(0, self.cols):
                if self.cols * i + j + 1 <= elevAmt:
                    button = QtGui.QPushButton("Elev " + str(self.cols * i + j + 1))
                    self.buttons[i, j] = button
                    button.clicked.connect(partial(self.setElevator, self.cols * i + j + 1))

                    self.elevatorGrid.addWidget(self.buttons[i, j], i, j)

        self.mainVBox.addLayout(self.elevatorGrid)


    def setFloorButtons(self, floorAmt):

        self.floorGrid = QtGui.QGridLayout()

        rows = int(ceil(floorAmt / float(self.cols)))

        self.buttons = {}
        for i in range(0, rows):
            for j in range(0, self.cols):
                if self.cols * i + j + 1 <= floorAmt:
                    button = QtGui.QPushButton(str(self.cols * i + j + 1))
                    self.buttons[i, j] = button
                    button.clicked.connect(partial(self.setFloor, self.cols * i + j + 1))

                    self.floorGrid.addWidget(self.buttons[i, j], i, j)

        self.mainVBox.addLayout(self.floorGrid)

    def setElevator(self, elev):
        self.elevator = elev

        self.reqLabel.setText("Elevator : {} \nFloor : {}".format(self.elevator, self.floor))

    def setFloor(self, floor):
        self.floor = floor

        self.reqLabel.setText("Elevator : {} \nFloor : {}".format(self.elevator, self.floor))

    @staticmethod
    def getRequest(floors, elevs, parent=None):
        dialog = DeliverRequestDialog(floors, elevs, parent)
        result = dialog.exec_()

        return (result == QtGui.QDialog.Accepted, dialog.elevator, dialog.floor)


class RequestsWindow(QtGui.QWidget):

    def __init__(self):
        super(RequestsWindow, self).__init__()
        self.setWindowTitle("Requests")

        self.hbox = QtGui.QHBoxLayout()

        self.served = RequestBox("No Requests Served", "Served Requests: ")
        self.added = RequestBox("No Requests Added", "Added Requests: ")

        self.hbox.addWidget(self.served)
        self.hbox.addWidget(self.added)

        self.setLayout(self.hbox)

    @QtCore.pyqtSlot(dict, dict)
    def setRequests(self, served, added):

        self.served.setRequests(served)
        self.added.setRequests(added)

    def reset(self):

        self.served.reset()
        self.added.reset()

class RequestBox(QtGui.QWidget):

    def __init__(self, emptyStr, Str):
        super(RequestBox, self).__init__()

        self.reqs = {}
        self.emptyStr = emptyStr
        self.notemptyStr = Str

        self.StretcherVBox = QtGui.QVBoxLayout()
        self.header = QtGui.QLabel(self.emptyStr)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.header)
        self.StretcherVBox.addLayout(self.vbox)
        self.StretcherVBox.addStretch(1)

        self.setLayout(self.StretcherVBox)

    def setRequests(self, new):

        for time in new:
            if new[time] != []:
                string = "In step " + str(time) + " : " + ",  ".join(new[time])
                if time not in self.reqs:
                    label = QtGui.QLabel(string, self)
                    self.reqs[time] = label
                    self.vbox.addWidget(label)
                else:
                    self.reqs[time].setText(string)

        if self.reqs != {}:
            self.header.setText(self.notemptyStr)

    def reset(self):
        for i in reversed(range(self.vbox.count())):
            self.vbox.itemAt(i).widget().setParent(None)

        self.reqs = {}

        self.header.setText(self.emptyStr)
        self.vbox.addWidget(self.header)


class PlanWindow(QtGui.QWidget):

    def __init__(self):
        super(PlanWindow, self).__init__()
        self.setWindowTitle("Plan")

        self.vbox = QtGui.QVBoxLayout()
        self.planWidget = PlanWidget()

        self.headerText = QtGui.QLabel("No Plan yet")
        self.headerButton = QtGui.QPushButton("Toggle Action Text")
        self.headerButton.clicked.connect(self.planWidget.toggleText)
        self.headerButton.resize(self.headerButton.sizeHint())

        self.header = QtGui.QHBoxLayout()
        self.header.addWidget(self.headerText)
        self.header.addWidget(self.headerButton)

        self.scroller = QtGui.QScrollArea()
        self.scroller.setWidget(self.planWidget)
        self.scroller.setWidgetResizable(True)

        self.vbox.addLayout(self.header)
        self.vbox.addWidget(self.scroller)

        self.setLayout(self.vbox)

    @QtCore.pyqtSlot(dict)
    def setPlan(self, plan):

        if plan != {}:
            self.headerText.setText("--- Plan ---")

        self.planWidget.setPlan(plan)
        self.planWidget.repaint()

    def reset(self):
        self.planWidget.reset()
        self.headerText.setText("No Plan yet")


class PlanWidget(QtGui.QWidget):

    def __init__(self, parent = None):
        super(PlanWidget, self).__init__(parent)

        self.showText = True

        self.vbox = QtGui.QVBoxLayout()

        self.elevatorGrid = QtGui.QGridLayout()
        self.vbox.addLayout(self.elevatorGrid)
        self.vbox.addStretch(1)

        self.elevatorActionDict = {}

        self.setLayout(self.vbox)

    def setPlan(self, plan):

        if plan != {}:

            if self.elevatorGrid.count() == 0:
                for move in plan[1]:
                    elev = move[0]
                    label = QtGui.QLabel("Elev " + str(elev))
                    self.elevatorGrid.addWidget(label, 0, elev)

            for time in plan:
                if not self.elevatorGrid.itemAtPosition(time, 0):
                    label = QtGui.QLabel("Step " + str(time), self)
                    self.elevatorGrid.addWidget(label, time, 0)

                for move in plan[time]:
                    elev = move[0]
                    action = move[1]

                    if not self.elevatorGrid.itemAtPosition(time, elev):
                        actionwidget = ActionWidget(action, self.showText)
                        self.elevatorActionDict[time, elev] = actionwidget
                        self.elevatorGrid.addWidget(actionwidget, time, elev)
                    else:
                        self.elevatorGrid.itemAtPosition(time, elev).widget().setAction(action)

    def toggleText(self):

        self.showText = not self.showText

        if len(self.elevatorActionDict) != 0:
            for item in self.elevatorActionDict:
                self.elevatorActionDict[item].setVisibleText(self.showText)


    def reset(self):

        for i in reversed(range(self.elevatorGrid.count())):
            self.elevatorGrid.itemAt(i).widget().setParent(None)


        self.elevatorActionDict = {}


class ActionWidget(QtGui.QWidget):

    def __init__(self, action, displayText = False):
        super(ActionWidget, self).__init__()

        # images
        self.imagedict = {}
        self.imagedict[Constants.UP] = QtGui.QPixmap(os.getcwd() + "/res/uparrow.png")
        self.imagedict[Constants.DOWN] = QtGui.QPixmap(os.getcwd() + "/res/downarrow.png")
        self.imagedict[Constants.WAIT] = QtGui.QPixmap(os.getcwd() + "/res/stay.png")
        self.imagedict[Constants.SERVE] = QtGui.QPixmap(os.getcwd() + "/res/serve.png")
        self.imagedict[Constants.NONEACT] = QtGui.QPixmap(os.getcwd() + "/res/none.png")

        # Action text
        self.textDict = {}
        self.textDict[Constants.UP] = Constants.UPTEXT
        self.textDict[Constants.DOWN] = Constants.DOWNTEXT
        self.textDict[Constants.SERVE] = Constants.SERVETEXT
        self.textDict[Constants.WAIT] = Constants.WAITTEXT
        self.textDict[Constants.NONEACT] = Constants.NONEACTTEXT

        self.picture = QtGui.QLabel(self)
        self.picture.setPixmap(self.imagedict[action])
        if self.imagedict[action].isNull():
            self.picture.hide()

        self.text = QtGui.QLabel(self.textDict[action], self)
        if not displayText:
            self.text.hide()

        self.vbox = QtGui.QVBoxLayout()

        self.vbox.addWidget(self.picture)
        self.vbox.addWidget(self.text)

        self.setLayout(self.vbox)

    def setAction(self, action):
        self.picture.setPixmap(self.imagedict[action])
        if self.imagedict[action].isNull():
            self.picture.hide()
        else:
            self.picture.show()

        self.text.setText(self.textDict[action])

    def setVisibleText(self, bool):
        if bool:
            self.text.show()
        else:
            self.text.hide()