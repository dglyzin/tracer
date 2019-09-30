import numpy as np


class Bounds():
    
    def __init__(self, unbound_value=-1):
        self.unbound_value = unbound_value

    def on_bounds(self, idxX, idxY, bsIdxs, source):
        '''
        
        O ->y
        |
        V
        x
        u[idx-1, idy-1] = win[0]
        u[idx-1, idy] = win[1]
        u[idx-1, idy+1] = win[2]
        u[idx, idy-1] = win[3]
        u[idx, idy] = win[4]
        u[idx, idy+1] = win[5]
        u[idx+1, idy-1] = win[6]
        u[idx+1, idy] = win[7]
        u[idx+1, idy+1] = win[8]
       
        '''
        idx = idxX
        idy = idxY
        win = source[np.array([idx-1, idx-1, idx-1, idx, idx, idx, idx+1, idx+1, idx+1]),
                     np.array([idy-1, idy, idy+1, idy-1, idy, idy+1, idy-1, idy, idy+1])]
        if self.unbound_value in win:
            return(win.reshape((3, 3)))
        else:
            return(None)

    def set_bounds(self, source, bsIdxs, btypes, idxX, idxY, bsFuncs):
        win = self.on_bounds(idxX, idxY, bsIdxs, source)
        if win is None:
            # if central case:
            return()
        
        bIdx = bsIdxs[idxX, idxY]
        btype = btypes[bIdx]
        if btype == 0:
            self.set_bound_dirichlet(win, idxX, idxY)
            
        elif btype == 1:
            self.set_bound_neumann(win, idxX, idxY)
            
    def get_border_type(self, win):
        cond = (win == self.unbound_value)
        
        '''
           0
        0     1
           0
        '''
        if cond[1, 2] and win[cond].size == 1:
            return("r")

        '''
           0
        0     0
           1
        '''
        if cond[2, 1] and win[cond].size == 1:
            return("b")

        '''
           0
        1     0
           0
        '''
        if cond[1, 0] and win[cond].size == 1:
            return("l")

        '''
           1
        0     0
           0
        '''
        if cond[0, 1] and win[cond].size == 1:
            return("t")
        
        '''
           0
        0     1
           1
        '''
        if cond[1, 2] and cond[2, 1] and win[cond].size == 2:
            return("br")
        
        '''
           0
        1     0
           1
        '''
        if cond[1, 0] and cond[2, 1] and win[cond].size == 2:
            return("bl")

        '''
           1
        1     0
           0
        '''
        if cond[1, 0] and cond[0, 1] and win[cond].size == 2:
            return("tl")

        '''
           1
        0     1
           0
        '''
        if cond[0, 1] and cond[1, 2] and win[cond].size == 2:
            return("tr")
        
