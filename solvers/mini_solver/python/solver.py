from solvers.mini_solver.python.bounds import Bounds


class Solver():
    
    def __init__(self, unbound_value):
        self.dx = self.dy = 0.01
        self.dt = 0.000001
        self.bounds = Bounds(unbound_value=unbound_value,
                             dxdy=[self.dx, self.dy])
        
    def run(self, result, source,
            csIdxs, cFuncs,
            bsIdxs, btypes, bFuncs,
            ITERATION_COUNT):

        # donot touch to border:
        idxXs = range(1, source.shape[0]-1)
        idxYs = range(1, source.shape[1]-1)

        for step in range(ITERATION_COUNT):
            for idxX in idxXs:
                for idxY in idxYs:
                    on_bounds = self.bounds.set_bounds(idxX, idxY,
                                                       result, source,
                                                       bsIdxs, btypes, bFuncs)
                    
                    # if not on_bounds:
                    if bsIdxs[idxX, idxY] == self.bounds.unbound_value:
                        dx, dy, dt = [self.dx, self.dy, self.dt]
                        func = cFuncs[csIdxs[idxX, idxY]]
                        result[idxX, idxY] = func(idxX, idxY, source, dt, dx, dy)
                        # print("result[idxX, idxY]:")
                        # print(result[idxX, idxY])
            source = result.copy()
                        
        return(result)


if __name__ == "__main__":

    import numpy as np

    source = np.ones((10, 10))
    # source = np.ones((100, 100))
    result = source.copy()

    csIdxs = np.zeros(source.shape)

    csIdxs[5:8, 5:8] = 1
    # csIdxs[50:80, 50:80] = 1
    csIdxs = csIdxs.astype(np.int)
    print("csIdxs:")
    print(csIdxs)

    def eq_test(idxX, idxY, u, dt, dx, dy, a):
        return(10*a)

    def eq_heat(idxX, idxY, u, dt, dx, dy, a):
        return(
            u[idxX, idxY]
            + dt*a*((u[idxX+1, idxY]-2*u[idxX, idxY] + u[idxX-1, idxY])/dx**2
                    + (u[idxX, idxY+1]-2*u[idxX, idxY] + u[idxX, idxY-1])/dy**2))
    
    cFuncs = [(lambda x, y, u, dt, dx, dy, a=0.1*i: eq_heat(x, y, u, dt, dx, dy, a))
              for i in [100, 1]]
    print("cFuncs[0](0,0,0,0,0,0):")
    # print(cFuncs[0](0, 0, 0, 0, 0, 0))
    print("cFuncs[1](0,0,0,0,0,0):")
    # print(cFuncs[1](0, 0, 0, 0, 0, 0))
    unbound_value = -1

    bsIdxs = np.zeros(source.shape) + unbound_value

    # side 2:
    bsIdxs[0] = 2
    # bsIdxs[0, 3:7] = 2
    # bsIdxs[0, 7:9] = 3

    # side 3:
    bsIdxs[9] = 3
    # bsIdxs[9, 1:5] = 2
    # bsIdxs[9, 5:7] = 3

    # side 0:
    bsIdxs[1:9, 0] = 0
    # bsIdxs[1:99, 0] = 0

    # side 1:
    bsIdxs[:, 9] = 1
    # bsIdxs[:, 99] = 1
    # bsIdxs[1:7, 9] = 4
    # bsIdxs[7:9, 9] =

    # inner borders:
    bsIdxs[3:5, 3:5] = 4
    # bsIdxs[30:40, 30:40] = 4
    # bsIdxs[30:40, 30:40] = 4
    # bsIdxs[30:40, 30:40] = 4
    # bsIdxs[4, 4] = 4
    bsIdxs = bsIdxs.astype(np.int)
    print("bsIdxs:")
    print(bsIdxs)

    btypes = [1, 1, 1, 1, 1]

    bFuncs = [lambda idxX, idxY: 10*i for i in range(len(btypes))]
    
    solver = Solver(unbound_value)
    
    ITERATION_COUNT = 10
    solver.run(result, source, csIdxs, cFuncs, bsIdxs, btypes, bFuncs,
               ITERATION_COUNT)
    import matplotlib.pyplot as plt
    plt.imshow(result)
    plt.show()
    print("result:")
    print(result)
