class SimpleProgress():
    def __init__(self, steps):
        self.steps = steps

    def succ(self, step):
        print(("%d" % int((step/self.steps)*100))+"%")
