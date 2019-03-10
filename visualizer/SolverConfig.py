import os

# ASP configuration

#list of encodings and instance

thispath = os.path.dirname(os.path.realpath(__file__))

encoding = thispath + "/../elevator.lp"

instance = thispath + "/../instances/instance-04_5-2.lp"

# Checker encoding
checker = ""

# clingo solver options
# for more information on the options use the help command of the clingo module (clingo -h)
options = ["--configuration=auto"]

# Misc configuration

printAtoms = False
