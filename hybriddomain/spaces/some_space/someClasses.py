class Params:
    '''
    DESCRIPTION::

    Represent param/s of some
    object.
    
    Can be used as list.

    TODO: add existance check.
    '''
    def __init__(self):
        # in case when used as list
        self.nodes = []
    
    def __getitem__(self, k):
        return(self.nodes[k])

    def append(self, v):
        self.nodes.append(v)

    def extend(self, vs):
        self.nodes.extend(vs)

    def __len__(self):
        return(len(self.nodes))
