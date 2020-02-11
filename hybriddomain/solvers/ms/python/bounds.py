import numpy as np


class Bounds():
    
    def __init__(self, unbound_value=-1, dxdy=[0.01, 0.01]):
        self.unbound_value = unbound_value

        '''
        indexes for 5 main elements of win:
        
        (for bwin_main):
        u[idx-1, idy] = win[0]
        u[idx, idy-1] = win[1]
        u[idx, idy] = win[2]
        u[idx, idy+1] = win[3]
        u[idx+1, idy] = win[4]
        '''
        self.idxXs_main = lambda idx: np.array([idx-1, idx, idx, idx, idx+1])
        self.idxYs_main = lambda idy: np.array([idy, idy-1, idy, idy+1, idy])

        '''
        indexes for all elements of win:

        (for bwin):
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
        self.idxXs = lambda idx: np.array([idx-1, idx-1, idx-1, idx, idx, idx, idx+1, idx+1, idx+1])
        self.idxYs = lambda idy: np.array([idy-1, idy, idy+1, idy-1, idy, idy+1, idy-1, idy, idy+1])
        self.dx, self.dy = dxdy

    def on_bounds(self, idxX, idxY, result, source, bsIdxs, btypes):
        '''
        
        O ->y
        |
        V
        x
        '''
        bwin_main = bsIdxs[self.idxXs_main(idxX), self.idxYs_main(idxY)]
        # print("bwin_main:")
        # print(bwin_main)
        if (bwin_main != self.unbound_value).any():
            # if we near some border
            # (i.e. it intersects with main part of win):
            bwin = bsIdxs[self.idxXs(idxX), self.idxYs(idxY)]
            bwin = bwin.reshape((3, 3))

            # take bound value for all in bwin:
            f = np.vectorize(lambda x: btypes[int(x)])
            btypeswin = f(bwin)

            # reshape bwin_main so that it looks like
            # window (like bwin, for ex)
            # and usable for get_border_type:
            u_value = self.unbound_value
            bwin_main_new = np.array([[u_value, bwin_main[0], u_value],
                                      [bwin_main[1], u_value, bwin_main[3]],
                                      [u_value, bwin_main[4], u_value]])
            # print("bwin_main")
            # print(bwin_main)

            # swin = source[self.idxXs, self.idxYs]
            return((bwin, bwin_main_new,
                    btypeswin))
        else:
            return(None)

    def set_bounds(self, idxX, idxY, result, source, bsIdxs, btypes, bsFuncs):
        
        '''If needed, fill bounds for ``idxX``, ``idxY`` for current iteration,
        else do nothing.

        - ``bsIdxs`` -- array of indexes of bound functions
        for each cell (point in grid) in current state (grid)
        (i.e. bsIdxs.shape = (dim X, dim Y))
  
        '''

        on_bound = self.on_bounds(idxX, idxY, result, source, bsIdxs, btypes)
        if on_bound is None:
            # if central case:
            return(False)
        bwin, bwin_main,  btypeswin = on_bound
        if 0 in btypeswin:
            # even if there is btype == 1 inside bwin, use Dirichlet:
            self.set_bound_dirichlet(idxX, idxY,
                                     result, bwin, bwin_main, bsFuncs)
            
        else:
            # assuming that all btypeswin is Neumann:
            self.set_bound_neumann(idxX, idxY,
                                   result, source, bwin, bwin_main, bsFuncs)
        return(True)

    def set_bound_neumann(self, idxX, idxY, result, source,
                          bwin, bwin_main, bsFuncs):
        dx = self.dx
        dy = self.dy
        idx = idxX
        idy = idxY
        u = source

        condition_name = self.get_border_type(bwin_main)
        '''
        # FOR debug 
        if condition_name is not None:
            print("condition_name: " + condition_name)
        else:
            print("unknown condition:")
            print(bwin)
            print(bwin_main)
        # END FOR
        '''
        if condition_name == "r":
            '''
            O ->y
            |
            V
            x

               0
            0     1
               0
            '''
            phi = bsFuncs[bwin[1, 2]]
            result[idx, idy+1] = u[idx, idy] - dy * phi(idx, idy+1)
            # u[idx, idy] = -1
        elif condition_name == "b":
            '''
            O ->y
            |
            V
            x

               0
            0     0
               1
            '''
            # u[i+1, j] = u[i, j] - dx * phi(i, j)
            phi = bsFuncs[bwin[2, 1]]
            result[idx+1, idy] = u[idx, idy] - dx * phi(idx+1, idy)
            # u[idx, idy] = -90
        elif condition_name == "l":
            '''
            O ->y
            |
            V
            x

               0
            1     0
               0
            '''
            # u[i, j-1] = u[i, j] - dy * phi(i,j-1)
            phi = bsFuncs[bwin[1, 0]]
            result[idx, idy-1] = u[idx, idy] - dy * phi(idx, idy-1)
        
            # u[idx, idy] = -180
        elif condition_name == "t":
            '''
            O ->y
            |
            V
            x

               1
            0     0
               0
            '''
            # u[i-1, j] = u[i, j] - dx * phi(i-1, j)

            phi = bsFuncs[bwin[0, 1]]
            result[idx-1, idy] = u[idx, idy] - dx * phi(idx-1, idy)
            # u[idx, idy] = -240

        elif condition_name == "br":
            '''
            O ->y
            |
            V
            x

               0
            0     1
               1
            '''
            dr = np.sqrt(dx**2 + dy**2)
            
            # du_dr = (u[i-1, j] - u[i, j-1])/dr
            du_dr = (u[idx-1, idy] - u[idx, idy-1])/dr

            # FOR u[i, j+1]

            phi = bsFuncs[bwin[1, 2]]

            # du_dy = - 1/2 * (phi(i, j+1) + du_dr)
            du_dy = -1/2. * (phi(idx, idy+1) + du_dr)
            
            # u[i, j+1] = u[i, j] + dy * du_dy
            result[idx, idy+1] = u[idx, idy] + dy * du_dy
            # END FOR

            # FOR u[i+1, j]
            phi = bsFuncs[bwin[2, 1]]
  
            # du_dx = 1/2 * (du_dr - phi(i+1, j))
            du_dx = 1/2. * (du_dr - phi(idx+1, idy))
            # u[i+1, j] = u[i, j] + dx * du_dx
            result[idx+1, idy] = u[idx, idy] + dx * du_dx
            # END FOR

            # u[idx, idy] = -45

        elif condition_name == "bl":
            '''
            O ->y
            |
            V
            x

               0
            1     0
               1
            '''
            dr = np.sqrt(dx**2 + dy**2)
            # du_dr = (u[i, j+1] - u[i-1, j])/dr
            du_dr = (u[idx, idy+1] - u[idx-1, idy])/dr

            # FOR u[i, j-1]
            phi = bsFuncs[bwin[1, 0]]

            # du_dy = 1/2 * (du_dr + phi(i, j-1))
            du_dy = 1/2. * (du_dr + phi(idx, idy-1))
            
            # u[i, j-1] = u[i, j] - dy * du_dy
            result[idx, idy-1] = u[idx, idy] - dy * du_dy
            # END FOR

            # FOR u[i+1, j]
            phi = bsFuncs[bwin[2, 1]]

            # du_dx = 1/2 * (du_dr - phi(i+1, j))
            du_dx = 1/2. * (du_dr - phi(idx+1, idy))
            # u[i+1, j] = u[i, j] + dx * du_dx
            result[idx+1, idy] = u[idx, idy] + dx * du_dx
            # END FOR

            # u[idx, idy] = -135
        elif condition_name == "tl":
            '''
            O ->y
            |
            V
            x

               1
            1     0
               0
            '''
            dr = np.sqrt(dx**2 + dy**2)
            # du_dr = (u[i+1, j] - u[i, j+1])/dr
            du_dr = (u[idx+1, idy] - u[idx, idy+1])/dr

            # FOR u[i-1, j]

            phi = bsFuncs[bwin[0, 1]]
            # du_dx = 1/2 * (phi(i-1, j) + du_dr)
            du_dx = 1/2. * (phi(idx-1, idy) + du_dr)
            
            # u[i-1, j] = u[i, j] - dx * du_dx
            result[idx-1, idy] = u[idx, idy] - dx * du_dx
            # END FOR

            # FOR u[i, j-1]
            phi = bsFuncs[bwin[1, 0]]

            # du_dy = 1/2 * (phi(i, j-1) - du_dr)
            du_dy = 1/2. * (phi(idx, idy-1) - du_dr)
            # u[i, j-1] = u[i, j] - dy * du_dy
            result[idx, idy-1] = u[idx, idy] - dy * du_dy
            # END FOR

            # u[idx, idy] = -181

        elif condition_name == "tr":
            '''
            O ->y
            |
            V
            x

               1
            0     1
               0
            '''

            dr = np.sqrt(dx**2 + dy**2)
            # du_dr = (u[i+1, j] - u[i, j-1])/dr
            du_dr = (u[idx+1, idy] - u[idx, idy-1])/dr

            # FOR u[i-1, j]

            phi = bsFuncs[bwin[0, 1]]
            
            # du_dx = 1/2 * (phi(i-1, j) + du_dr)
            du_dx = 1/2. * (phi(idx-1, idy) + du_dr)
            
            # u[i-1, j] = u[i, j] - dx * du_dx
            result[idx-1, idy] = u[idx, idy] - dx * du_dx
            # END FOR

            # FOR u[i, j+1]

            phi = bsFuncs[bwin[1, 2]]

            # du_dy = 1/2 * (du_dr - phi(i, j+1))
            du_dy = 1/2. * (du_dr - phi(idx, idy+1))
            # u[i, j+1] = u[i, j] + dy * du_dy
            result[idx, idy+1] = u[idx, idy] + dy * du_dy
            # END FOR

            # u[idx, idy] = -225

    def set_bound_dirichlet(self, idxX, idxY, result,
                            bwin, bwin_main, bsFuncs):
        condition_name = self.get_border_type(bwin_main)
        '''
        # FOR debug
        if condition_name is not None:
            print("condition_name: " + condition_name)
        else:
            print("unknown condition:")
            print(bwin)
            print(bwin_main)
        # END FOR
        '''
        if condition_name == "r":
            '''
            O ->y
            |
            V
            x

               0
            0     1
               0
            '''
            result[idxX, idxY+1] = bsFuncs[bwin[1, 2]](idxX, idxY+1)

        elif condition_name == "b":
            '''
            O ->y
            |
            V
            x

               0
            0     0
               1
            '''
            result[idxX+1, idxY] = bsFuncs[bwin[2, 1]](idxX+1, idxY)

        elif condition_name == "l":
            '''
            O ->y
            |
            V
            x

               0
            1     0
               0
            '''
            result[idxX, idxY-1] = bsFuncs[bwin[1, 0]](idxX, idxY-1)

        elif condition_name == "t":
            '''
            O ->y
            |
            V
            x

               1
            0     0
               0
            '''
            result[idxX-1, idxY] = bsFuncs[bwin[0, 1]](idxX-1, idxY)

        elif condition_name == "br":
            '''
            O ->y
            |
            V
            x

               0
            0     1
               1
            '''
            result[idxX, idxY+1] = bsFuncs[bwin[1, 2]](idxX, idxY+1)
            result[idxX+1, idxY] = bsFuncs[bwin[2, 1]](idxX+1, idxY)

        elif condition_name == "bl":
            '''
            O ->y
            |
            V
            x

               0
            1     0
               1
            '''
            result[idxX, idxY-1] = bsFuncs[bwin[1, 0]](idxX, idxY-1)
            result[idxX+1, idxY] = bsFuncs[bwin[2, 1]](idxX+1, idxY)

        elif condition_name == "tl":
            '''
            O ->y
            |
            V
            x

               1
            1     0
               0
            '''
            result[idxX, idxY-1] = bsFuncs[bwin[1, 0]](idxX, idxY-1)
            result[idxX-1, idxY] = bsFuncs[bwin[0, 1]](idxX-1, idxY)

        elif condition_name == "tr":
            '''
            O ->y
            |
            V
            x

               1
            0     1
               0
            '''
            result[idxX-1, idxY] = bsFuncs[bwin[0, 1]](idxX-1, idxY)
            result[idxX, idxY+1] = bsFuncs[bwin[1, 2]](idxX, idxY+1)

    def get_border_type(self, bwin):
        cond = (bwin != self.unbound_value)
        # print("cond")
        # print(cond)
        # print(bwin[cond].size)
        '''
           0
        0     1
           0
        '''
        if cond[1, 2] and bwin[cond].size == 1:
            return("r")

        '''
           0
        0     0
           1
        '''
        if cond[2, 1] and bwin[cond].size == 1:
            return("b")

        '''
           0
        1     0
           0
        '''
        if cond[1, 0] and bwin[cond].size == 1:
            return("l")

        '''
           1
        0     0
           0
        '''
        if cond[0, 1] and bwin[cond].size == 1:
            return("t")
        
        '''
           0
        0     1
           1
        '''
        if cond[1, 2] and cond[2, 1] and bwin[cond].size == 2:
            return("br")
        
        '''
           0
        1     0
           1
        '''
        if cond[1, 0] and cond[2, 1] and bwin[cond].size == 2:
            return("bl")

        '''
           1
        1     0
           0
        '''
        if cond[1, 0] and cond[0, 1] and bwin[cond].size == 2:
            return("tl")

        '''
           1
        0     1
           0
        '''
        if cond[0, 1] and cond[1, 2] and bwin[cond].size == 2:
            return("tr")
        
