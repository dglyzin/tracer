from hybriddomain.solvers.hs.solver_gen_sh import GenSH


class SolverHS():

    '''
    Generate sh
    Copy data to server
    run solver at server
       including continue
    getting results
    '''

    def __init__(self, model, pathes):

        self.model = model
        self.pathes = pathes

        # common for cpp and dom:
        self.gen_sh = GenSH(self)
        
        # cpp template render:

    
