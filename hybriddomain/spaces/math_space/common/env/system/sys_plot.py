class sysPlotter():
    def __init__(self, net):
        self.net = net

    def show_original(self):
        for eq in self.net.eqs:
            eq.show_original()

    def show_cpp(self):
        for eq in self.net.eqs:
            eq.replacer.cpp.show_cpp()

