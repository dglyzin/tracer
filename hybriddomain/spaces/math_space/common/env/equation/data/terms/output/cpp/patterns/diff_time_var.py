from env.equation.data.terms.output.cpp.patterns.var import Var


class DiffTimeVar(Var):

    '''For term like U', V'. 
    They differ from Var only in lex'''

    def __init__(self, net):
        Var.__init__(self, net)
        self.id = 'diff_time'


