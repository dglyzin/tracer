'''
pf$ srun -n 1   -p all  --exclusive  ~/anaconda3/bin/./python3 -u -c "import hybriddomain.solvers.ms.python.solver as ts; ts.run()" -model lab/hybriddomain/hybriddomain/gui/2d/web/model/data/physics/n-body/test0 -steps 1 -log_level info -plot False

pf$ ~/anaconda3/bin/./python3 -c "import hybriddomain.solvers.ms.python.solver as ts; ts.run()" -model ~/Documents/projects/projectsNew/lab/hybriddomain/hybriddomain/gui/2d/web/model/data/physics/n-body/test0 -steps 1 -log_level info -plot False

v, u = np.meshgrid(y, x)

In [55]: v = -(v-1)

In [56]: u = u-1

In [57]: q = pylab.quiver(u, v)

In [88]: s = np.zeros(a.shape)
In [88]: a, b = np.meshgrid(y, x)

cond = (a-1)**2+(b-1)**2 < 0.1

# sphere field:
v[cond] = -(v[cond]-1)
u[cond] = u[cond]+1

# river field
v[not cond] = 0
u[not cond] = u[not cond]*(u[not cond]-2)
'''
from hybriddomain.solvers.ms.python.bounds import Bounds

from PIL import Image
# from matplotlib.pyplot import imread
from matplotlib.pyplot import imsave
# import base64
import json
import os
import sys
from functools import reduce
import sympy
import numpy as np
from time import time

from hybriddomain.solvers.ms.python.threads import Kernel as bKernel
from hybriddomain.solvers.ms.python.threads import mp
from hybriddomain.solvers.ms.python.threads import queue

from hybriddomain.solvers.ms.postproc.postprocessor import Postproc
import multiprocessing as mp

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ms.solver')
logger.setLevel(level=log_level)


class Thread(bKernel):
    def __init__(self, net, work_queue, number):
        self.net = net
        bKernel.__init__(self, work_queue, number)

    def do_work(self, entry):
        '''Run solver kernel for each thread'''
        # print(entry)
        import sympy
        self.net.kernel(*entry)
        # print("thread: %d finished" % (self.number))


class Process():

    def __init__(self, net):
        self.net = net

    def do_work(self, entry):
        '''Run solver kernel for each thread'''
        # print(entry)
        
        self.net.kernel(*entry)
        # print("thread: %d finished" % (self.number))
    

class Solver():
    
    def __init__(self, unbound_value, model_path=None):
        self.model_path = model_path
        self.dx = self.dy = 0.01
        self.dt = 0.000001
        self.bounds = Bounds(unbound_value=unbound_value,
                             dxdy=[self.dx, self.dy])
        
        # self.process = Process(self)
        # self.num_worker_threads = mp.cpu_count()
        self.start_workers()

    def start_workers(self):
        # FOR init threads:
        self.num_worker_threads = mp.cpu_count()
        logger.info("count of physical cpu:")
        logger.info(self.num_worker_threads)
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
                    # logger.debug("result[idxX, idxY]:")
                    # logger.debug(result[idxX, idxY])

    def run(self, result, source,
            csIdxs, cFuncs,
            bsIdxs, btypes, bFuncs,
            ITERATION_COUNT, progress=None):
        
        # donot touch to border:
        idxXs = list(range(1, source.shape[0]-1))
        idxYs = range(1, source.shape[1]-1)

        n = len(idxXs)
        m = self.num_worker_threads
        logger.debug("n=len(idxXs):")
        logger.debug(n)
        
        # here "else idxXs[i*int(n/m):]" used for fill remained:
        splited_idxXs = [idxXs[i*int(n/m)+2: (i+1)*(int(n/m))-1]
                         if i < m-1 else idxXs[i*int(n/m)+2:]
                         for i in range(m)]
        logger.debug("for queue:")
        logger.debug(splited_idxXs)
        
        # because of borders area between threads computed
        # at single thread:
        splited_idxXs_remainds = [idxXs[i*int(n/m)-1: (i)*(int(n/m))+2]
                                  if i != 0 else idxXs[i*int(n/m):i*int(n/m)+2]
                                  for i in range(m)]
        logger.debug("for single thread:")
        logger.debug(splited_idxXs_remainds)
        '''
        splited_idxXs = [idxXs[i*int(n/m): (i+1)*(int(n/m))]
                         if i < m-1 else idxXs[i*int(n/m):]
                         for i in range(m)]
        '''
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
        # pool = mp.Pool(processes=self.num_worker_threads)
        start_time = time()
        for step in range(ITERATION_COUNT):
            
            logger.debug("compute threads: ...")
            '''
            args_list = [[entry_idxXs, idxYs,
                          result, source,
                          csIdxs, cFuncs,
                          bsIdxs, btypes, bFuncs]
                         for entry_idxXs in splited_idxXs]
            pool.map(self.process.do_work, args_list)
            '''
            for idx, entry_idxXs in enumerate(splited_idxXs):
                
                # logger.debug("bounds between threads:")
                # a = bsIdxs[entry_idxXs[-1]-1: entry_idxXs[-1]+1, :]
                # logger.debug(a[a != self.bounds.unbound_value])
                self.queue.put([entry_idxXs, idxYs,
                                result, source,
                                csIdxs, cFuncs,
                                bsIdxs, btypes, bFuncs])
            self.queue.join()
            logger.debug("... done")

            logger.debug("compute remainds at single thread: ...")
            '''
            args_list = [[entry_idxXs, idxYs,
                          result, source,
                          csIdxs, cFuncs,
                          bsIdxs, btypes, bFuncs]
                         for entry_idxXs in splited_idxXs_remainds]
            pool.map(self.process.do_work, args_list)
            '''
            for idx, entry_idxXs in enumerate(splited_idxXs_remainds):
                self.kernel(entry_idxXs, idxYs,
                            result, source,
                            csIdxs, cFuncs,
                            bsIdxs, btypes, bFuncs)
            logger.debug("... done")

            source = result.copy()

            # update progress:
            if progress is not None:
                progress.succ(step+1)
            if self.model_path is not None:
                imsave(os.path.join(self.model_path,
                                    "result_%s.png" % str(step+1)), result)
        self.stop_workers()
        self.running_time = time() - start_time
        logger.info("running_time: %s" % str(self.running_time))
        logger.info("Done!")
        return(result)


def imread(path, mode=None):
    im = Image.open(path)
    if mode == "L":
        return(np.array(im.convert("L")))
    return(np.array(im))


def run_files(model_path, steps=3, plot=False):
    
    source = imread(os.path.join(model_path, "initials_img.png"), mode="L")
    csIdxs = imread(os.path.join(model_path, "centrals_img.png"), mode="L")
    bsIdxs = imread(os.path.join(model_path, "bounds_img.png"), mode="L")
    
    # source = imread(os.path.join(model_path, "initials_img.png"), mode="L")
    # csIdxs = imread(os.path.join(model_path, "centrals_img.png"), mode="L")
    # bsIdxs = imread(os.path.join(model_path, "bounds_img.png"), mode="L")
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

    logger.debug("centrals_colors_table:")
    logger.debug(centrals_colors_table)
    logger.debug("bounds_colors_table:")
    logger.debug(bounds_colors_table)
    logger.debug("initials_colors_table:")
    logger.debug(initials_colors_table)

    with open(os.path.join(model_path, "equations_table.json")) as f:
        equations_table = json.loads(f.read())
    
    with open(os.path.join(model_path, "equations_bs_table.json")) as f:
        equations_bs_table = json.loads(f.read())
    
    # convert indexes from colors to equations numbers:
    logger.debug("bsIdxs:")
    logger.debug(bsIdxs)

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
        
    logger.debug("centrals_equations_numbers:")
    logger.debug(centrals_equations_numbers)
    logger.debug("bounds_eq_numbers_btype:")
    logger.debug(bounds_eq_number_btype)

    logger.debug("bounds_equations_numbers:")
    logger.debug(bounds_equations_numbers)

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

    logger.debug("csIdxs:")
    logger.debug(csIdxs)
    logger.debug("bsIdxs:")
    logger.debug(bsIdxs)
    
    # FOR cFuncs:
    cFuncs = {}
    # logger.debug("eval(equations_table[0][0]):")
    # logger.debug(eval(equations_table[0][0]))
    for eq_num in centrals_equations_numbers:
        if eq_num not in range(len(equations_table)):
            raise(BaseException("no equation for num: %s"
                                % (eq_num)))
        # only on equation in system, for now:
        cFuncs[eq_num] = (lambda idxX, idxY, u, dt, dx, dy:
                          eval(equations_table[eq_num][0]))
    logger.debug("equations_table:")
    logger.debug(equations_table)
    logger.debug("cFuncs:")
    logger.debug(cFuncs)
    logger.debug(cFuncs[0](0, 0,
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
        logger.debug(equations_bs_table[eq_num][0])
        lambda_sympy = sympy.sympify(equations_bs_table[eq_num][0])
        logger.debug(lambda_sympy)
        bFuncs[eq_num] = (lambda x, y, a=lambda_sympy:
                          float(a.subs({"idxX": x, "idxY": y})))
        logger.debug("bFuncs[%d](1, 3):" % eq_num)
        logger.debug(bFuncs[eq_num])
        logger.debug(bFuncs[eq_num](1, 3))
        # bFuncs[eq_num] = (lambda idxX, idxY:
        #                   eval(equations_bs_table[eq_num][0]))
        btype = bounds_eq_number_btype[eq_num]
        if btype == "Dirichlet":
            btypes[eq_num] = 0
        else:
            btypes[eq_num] = 1
    # for default
    if unbound_value not in btypes:
        btypes[unbound_value] = -1  # otherwise all bound will be Dirichlet
    logger.debug("equations_bs_table:")
    logger.debug(equations_bs_table)
    logger.debug("bFuncs:")
    logger.debug(bFuncs)
    logger.debug("btypes:")
    logger.debug(btypes)
    # END FOR
    
    ITERATION_COUNT = steps
    result = run_cmd(source, csIdxs, cFuncs,
                     bsIdxs, btypes, bFuncs, unbound_value,
                     ITERATION_COUNT, model_path=model_path)

    if plot:
        import matplotlib.pyplot as plt
        plt.imshow(result)
        plt.show()
    logger.debug("result:")
    logger.debug(result)
    imsave(os.path.join(model_path, "result.png"), result)


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
    run_files(model_path, plot=True)


def run_cmd(source, csIdxs, cFuncs,
            bsIdxs, btypes, bFuncs, unbound_value,
            ITERATION_COUNT, model_path=None):

    result = source.copy()

    # TODO: clear previus results, if not from remoterun
    # from hybriddomain.solvers.hs.remoterun.progresses.progress_cmd import ProgressCmd
    # progress_cmd = ProgressCmd(ITERATION_COUNT)
    class SimpleProgress():
        def __init__(self, steps):
            self.steps = steps

        def succ(self, step):
            print(("%d" % int((step/self.steps)*100))+"%")
    progress = SimpleProgress(ITERATION_COUNT)

    solver = Solver(unbound_value, model_path=model_path)

    solver.run(result, source, csIdxs, cFuncs,
               bsIdxs, btypes, bFuncs,
               ITERATION_COUNT, progress)
    if model_path is not None:
        postproc = Postproc(logger, model_path)
        postproc.createVideoFile()
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


def run():
    # print(sys.argv)
    if '-model' in sys.argv:
        model_path = sys.argv[sys.argv.index('-model') + 1]
    else:
        raise(BaseException("-model needed"))

    if '-steps' in sys.argv:
        steps = sys.argv[sys.argv.index('-steps') + 1]
        steps = int(steps)
    else:
        raise(BaseException("-steps needed"))

    if '-plot' in sys.argv:
        plot = sys.argv[sys.argv.index('-plot') + 1]
        plot = eval(plot)
    else:
        plot = False

    if '-log_level' in sys.argv:
        log_level_str = sys.argv[sys.argv.index('-log_level') + 1]
        log_level_str = log_level_str.lower()
        if "info" == log_level_str:
            logger.setLevel(level=logging.INFO)
        elif("debug" == log_level_str):
            logger.setLevel(level=logging.DEBUG)
        else:
            raise(BaseException("-log_level either info or debug"))
    else:
        pass
    
    run_files(model_path, steps=steps, plot=plot)


if __name__ == "__main__":
    
    run()
    # test_files()
    # test_cmd()
