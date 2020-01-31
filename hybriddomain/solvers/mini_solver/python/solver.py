from hybriddomain.solvers.mini_solver.python.bounds import Bounds

from scipy.misc import imread
from scipy.misc import imsave
# import base64
import json
import os
from functools import reduce
import sympy
import numpy as np

from threads import Kernel as bKernel
from threads import mp
from threads import queue


class Thread(bKernel):
    def __init__(self, net, work_queue, number):
        self.net = net
        bKernel.__init__(self, work_queue, number)

    def do_work(self, entry):
        '''Run solver kernel for each thread'''
        # print(entry)
        
        self.net.kernel(*entry)
        print("thread: %d finished" % (self.number))


class Solver():
    
    def __init__(self, unbound_value):
        self.dx = self.dy = 0.01
        self.dt = 0.000001
        self.bounds = Bounds(unbound_value=unbound_value,
                             dxdy=[self.dx, self.dy])
        self.start_workers()

    def start_workers(self):
        # FOR init threads:
        self.num_worker_threads = mp.cpu_count()
        print("count of physical cpu:")
        print(self.num_worker_threads)
        self.threads = []
        self.queue = queue.Queue()

        for i in range(self.num_worker_threads):
            # t = threading.Thread(target=worker)
            t = Thread(self, self.queue, i)
            t.start()
            self.threads.append(t)
        # END FOR

    def stop_workers(self):
        # stop workers
        for i in range(self.num_worker_threads):
            self.queue.put(None)
        for t in self.threads:
            t.join()

    def kernel(self, entry_idxXs, idxYs,
               result, source,
               csIdxs, cFuncs,
               bsIdxs, btypes, bFuncs):
        '''What each thread will solve'''

        # for idxX in idxXs:
        for idxX in entry_idxXs:
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

    def run(self, result, source,
            csIdxs, cFuncs,
            bsIdxs, btypes, bFuncs,
            ITERATION_COUNT, progress=None):
        
        # donot touch to border:
        idxXs = list(range(1, source.shape[0]-1))
        idxYs = range(1, source.shape[1]-1)

        n = len(idxXs)
        m = self.num_worker_threads
        print("n=len(idxXs):")
        print(n)
        
        # here "else idxXs[i*int(n/m):]" used for fill remained:
        splited_idxXs = [idxXs[i*int(n/m): (i+1)*(int(n/m))]
                         if i < m-1 else idxXs[i*int(n/m):]
                         for i in range(m)]
        print("for queue:")
        print(splited_idxXs)
        '''not used:
        # check if all data in idxXs can be achived with m+1 i.e.
        # if possible satisfy: (i+1)*[m/k]>=n which is equal to
        # (m+1)*[m/k]>=n for i = m (=range(m+1)[-1])
        if int(n/m) < m+1:
            raise(BaseException("int(n/m)<m+1: n=%d, m=%d"
                                % (n, m)))
        M = m if n % m == 0 else m + 1
        splited_idxXs = [idxXs[i*int(n/m): (i+1)*(int(n/m))]
                         for i in range(M)]
        '''
        for step in range(ITERATION_COUNT):
            
            # update progress:
            if progress is not None:
                progress.succ(step)
                
            for idx, entry_idxXs in enumerate(splited_idxXs):
                
                print("bounds between threads:")
                a = bsIdxs[entry_idxXs[-1]-1: entry_idxXs[-1]+1, :]
                print(a[a != self.bounds.unbound_value])
        
                self.queue.put([entry_idxXs, idxYs,
                                result, source,
                                csIdxs, cFuncs,
                                bsIdxs, btypes, bFuncs])
                '''
                self.kernel(entry_idxXs, idxYs,
                            result, source,
                            csIdxs, cFuncs,
                            bsIdxs, btypes, bFuncs)
                '''
            self.queue.join()
            source = result.copy()

        self.stop_workers()

        return(result)


def run_files(model_path):

    source = imread(os.path.join(model_path, "initials_img.png"), mode="L")
    csIdxs = imread(os.path.join(model_path, "centrals_img.png"), mode="L")
    bsIdxs = imread(os.path.join(model_path, "bounds_img.png"), mode="L")
    with open(os.path.join(model_path, "centrals_colors_table.json")) as f:
        centrals_colors_table = json.loads(f.read())
    centrals_colors_table = [[int(col) for col in row]
                             for row in centrals_colors_table]

    with open(os.path.join(model_path, "bounds_colors_table.json")) as f:
        bounds_colors_table = json.loads(f.read())
    bounds_colors_table = [[int(col) if col_idx != 2 else col
                            for col_idx, col in enumerate(row)]
                           for row in bounds_colors_table]

    with open(os.path.join(model_path, "initials_colors_table.json")) as f:
        initials_colors_table = json.loads(f.read())
    initials_colors_table = [[int(col) for col_idx, col in enumerate(row)]
                             for row in initials_colors_table]

    print("centrals_colors_table:")
    print(centrals_colors_table)
    print("bounds_colors_table:")
    print(bounds_colors_table)
    print("initials_colors_table:")
    print(initials_colors_table)

    with open(os.path.join(model_path, "equations_table.json")) as f:
        equations_table = json.loads(f.read())
    
    with open(os.path.join(model_path, "equations_bs_table.json")) as f:
        equations_bs_table = json.loads(f.read())
    
    # convert indexes from colors to equations numbers:
    print("bsIdxs:")
    print(bsIdxs)

    # for check if all equations available:
    f = lambda acc, x: acc+[x] if (x not in [y for y in acc]) else acc    
    centrals_equations_numbers = [row[1] for row in centrals_colors_table]
    centrals_equations_numbers = list(reduce(f, centrals_equations_numbers, []))
    
    # add default value:
    if 0 not in centrals_equations_numbers:
        centrals_equations_numbers.append(0)

    bounds_eq_number_btype = dict([(row[1], row[2]) for row in bounds_colors_table])
    bounds_equations_numbers = [row[1] for row in bounds_colors_table]
    bounds_equations_numbers = list(reduce(f, bounds_equations_numbers, []))

    # add default value:
    # if 0 not in bounds_equations_numbers:
    #     bounds_equations_numbers.append(0)
    # if 0 not in bounds_eq_number_btype:
        
    print("centrals_equations_numbers:")
    print(centrals_equations_numbers)
    print("bounds_eq_numbers_btype:")
    print(bounds_eq_number_btype)

    print("bounds_equations_numbers:")
    print(bounds_equations_numbers)

    for row in centrals_colors_table:
        csIdxs[csIdxs == row[0]] = row[1]
    for row in bounds_colors_table:
        bsIdxs[bsIdxs == row[0]] = row[1]

    unbound_value = 0

    def fix_missing_colors(idxs, equations_numbers):
        '''Put all unknown colors to default value'''

        # union(idxs == eq_num, for all eq_nums)
        #  == intersection(idxs != eq_num, for all eq_nums):
        or_args = [idxs != eq_num for eq_num in equations_numbers]
        or_func = np.vectorize(lambda x, y: x and y)
        condition = reduce(lambda acc, elm: or_func(acc, elm),
                           or_args[1:], or_args[0])
        # TODO: csIdxs.unbound_value != bsIdxs.unbound_value:
        idxs[condition] = unbound_value
    fix_missing_colors(csIdxs, centrals_equations_numbers)
    fix_missing_colors(bsIdxs, bounds_equations_numbers)

    print("csIdxs:")
    print(csIdxs)
    print("bsIdxs:")
    print(bsIdxs)
    
    # FOR cFuncs:
    cFuncs = {}
    # print("eval(equations_table[0][0]):")
    # print(eval(equations_table[0][0]))
    for eq_num in centrals_equations_numbers:
        if eq_num not in range(len(equations_table)):
            raise(BaseException("no equation for num: %s"
                                % (eq_num)))
        # only on equation in system, for now:
        cFuncs[eq_num] = (lambda idxX, idxY, u, dt, dx, dy:
                          eval(equations_table[eq_num][0]))
    print("equations_table:")
    print(equations_table)
    print("cFuncs:")
    print(cFuncs)
    print(cFuncs[0](0, 0,
                    {(0, 0): 0, (1, 0): 1, (-1, 0): 1,
                     (0, 1): 1, (0, -1): 1},
                    0.1, 0.1, 0.1))
    # END FOR

    # FOR bFuncs:
    bFuncs = {}
    btypes = {}

    for eq_num in bounds_eq_number_btype:
        if eq_num not in range(len(equations_bs_table)):
            raise(BaseException("no equation for num: %s"
                                % (eq_num)))
        # only on equation in system, for now:
        bFuncs[eq_num] = (lambda idxX, idxY:
                          eval(equations_bs_table[eq_num][0]))
        btype = bounds_eq_number_btype[eq_num]
        if btype == "Dirichlet":
            btypes[eq_num] = 0
        else:
            btypes[eq_num] = 1
    # for default
    if unbound_value not in btypes:
        btypes[unbound_value] = -1  # otherwise all bound will be Dirichlet
    print("equations_bs_table:")
    print(equations_bs_table)
    print("bFuncs:")
    print(bFuncs)
    print("btypes:")
    print(btypes)
    # END FOR

    ITERATION_COUNT = 3
    result = run_cmd(source, csIdxs, cFuncs,
                     bsIdxs, btypes, bFuncs, unbound_value,
                     ITERATION_COUNT)

    import matplotlib.pyplot as plt
    plt.imshow(result)
    plt.show()
    print("result:")
    print(result)


def test_files():
    import os
    path = os.getcwd()
    print("path")
    print(path)
    hd = path.split("solvers")[0]
    model_path = os.path.join(hd, "gui", "2d", "web", "model",
                              "data", "physics", "n-body", "test0")
    print("model_path:")
    print(model_path)
    run_files(model_path)


def run_cmd(source, csIdxs, cFuncs,
            bsIdxs, btypes, bFuncs, unbound_value,
            ITERATION_COUNT):

    result = source.copy()

    from hybriddomain.solvers.hs.remoterun.progresses.progress_cmd import ProgressCmd
    progress_cmd = ProgressCmd(ITERATION_COUNT)

    solver = Solver(unbound_value)

    solver.run(result, source, csIdxs, cFuncs,
               bsIdxs, btypes, bFuncs,
               ITERATION_COUNT, progress_cmd)
    return(result)


def test_cmd():

    import numpy as np

    source = np.ones((10, 10))
    # source = np.ones((100, 100))

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
    # cFuncs[0] = eq_heat(..., i*100), cFuncs[1] = eq_heat(...,i*1)
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

    ITERATION_COUNT = 10

    result = run_cmd(source, csIdxs, cFuncs,
                     bsIdxs, btypes, bFuncs, unbound_value,
                     ITERATION_COUNT)

    import matplotlib.pyplot as plt
    plt.imshow(result)
    plt.show()
    print("result:")
    print(result)


if __name__ == "__main__":
    
    test_files()
    # test_cmd()
