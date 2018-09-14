class GenBaseCommon():

    '''Base for all common objects methods'''

    def fill_func_names_stack(self, funcNamesStack,
                              funcNamesStackLocal):

        '''fill ``self.funcNamesStack`` that will be used
        for ``funcNames`` in cpp templates and for indexes
        in dom file'''

        # check if funcNamesStack alredy exist:
        # if 'funcNamesStack' in self.net.params.__dict__:

        for funcName in funcNamesStackLocal:
            # remove duplicates:
            if funcName not in funcNamesStack:
                funcNamesStack.append(funcName)
        
        self.net.params.funcNamesStack = funcNamesStack

        # self.net.params.funcNamesStack.extend(funcNamesStackLocal)

        # remove duplicates:
        # self.net.params.funcNamesStack = list(set(self.funcNamesStack))



class Params:
    '''
    DESCRIPTION::

    Represent param/s of some
    object.
    
    Can be used as list.
    
    '''
    def __init__(self):
        # in case when used as list
        self.nodes = []
    
    def __getitem__(self, k):
        return(self.nodes[k])

    def append(self, v):
        self.nodes.append(v)

    def __len__(self):
        return(len(self.nodes))
