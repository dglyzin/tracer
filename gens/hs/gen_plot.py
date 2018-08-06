class GenPlot():

    '''
    Generate sh file.
    '''

    def __init__(self, net):
        
        self.net = net

        self.model = net.model

        # where save plot params:
        # self.out = net.settings.pathes['hd']['plot']
        
    def save(self, path):
        
        modelParams = {}
        modelParams['plots'] = self.model.plots
        modelParams['results'] = self.model.results
        modelParams['namesEquations'] = [eq.sent
                                         for eq in self.model.equations[0].eqs]
        with open(path, 'w') as f:
            f.write(str(modelParams))
