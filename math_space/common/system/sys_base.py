class sysBase():
    def __init__(self, net, name, vars, cpp=False):
        self.net = net

        self.name = name
        self.vars = vars
        self.cpp = cpp

    def set_default(self):
        self.vars = "x"
        self.cpp = False
