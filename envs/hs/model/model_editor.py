class ModelEditor():
    def __init__(self, net):
        self.net = net
            
    def add_bound(self, bound):

        '''Check if bound in self.bounds and if not, add it'''

        self.add(bound, self.net.bounds)
    
    def add_block(self, block):

        '''Check if block in self.blocks and if not, add it'''

        self.add(block, self.net.blocks)

    def add_equation(self, equation):

        '''Check if equation in self.equations and if not, add it'''

        self.add(equation, self.net.equations)

    def add_initial(self, initial):

        '''Check if initial in self.initials and if not, add it'''

        self.add(initial, self.net.initials)
            
    def add_ic(self, ic):

        '''Check if ic in self.initerconnects and if not, add it'''

        self.add(ic, self.net.interconnects)

    def add_compnode(self, compnode):

        '''Check if compnode in self.compnodes and if not, add it'''

        self.add(compnode, self.net.compnodes)

    def add(self, o, ols):
                
        '''This function add obj o to ols,
        if it not exist in model (see obj.__eq__ method for ditails).
        in that case obj.num will be added, that is pointer at number
        in ols (.blocks, .bounds, .eqations, ...).

        Inputs:
        o - object to be added
        ols - objects list for o will be add to (self.net.blocks)'''
        
        if o not in ols:
            index = len(ols)
            o.num = index
            ols.append(o)
        else:
            print("obj alredy exist:")
            print(o)

