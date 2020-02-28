'''
~/anaconda3/bin/./python3 -c "import hybriddomain.solvers.ms.python.field as ts; ts.run()" -model ~/Documents/projects/projectsNew/lab/hybriddomain/hybriddomain/gui/2d/web/model/data/physics/n-body/test1 -steps 130 -log_level info -start_from field_27.png -save_interval 7 -plot False

~/anaconda3/bin/./python3 -c "import hybriddomain.solvers.ms.python.field as ts; ts.run()" -model ~/Documents/projects/projectsNew/lab/hybriddomain/hybriddomain/gui/2d/web/model/data/physics/n-body/test0 -steps 7 -log_level info
'''
import os
import sys
import numpy as np
import pylab
from functools import reduce
from matplotlib.pyplot import imsave

from hybriddomain.solvers.ms.python.solver import imread

from hybriddomain.solvers.ms.postproc.postprocessor import Postproc

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ms.field')
logger.setLevel(level=log_level)

default = 30


def create_field0(shape=None, plot=True):
    if shape is not None:
        x = np.linspace(0, 3, shape[0])
        y = np.linspace(0, 5.5, shape[1])
        # y = np.linspace(0, 3, shape[1])
        # sphere_center:
        # sphc = (3/2, 3/2)
        # sphc = (3/2, 5.5/2)
        sphc = (3/2, 1)
        r = 1
        ks = 7
        kr = 0.01
        # reiver center:
        # h = 3
        h = 5.5
    else:
        x = np.linspace(0, 3, 30)
        y = np.linspace(0, 2, 20)
        sphc = (1.5, 1)
        r = 1
        h = 3
        ks = 13
        kr = 1
    # logger.debug("x:")
    # logger.debug(x)

    # logger.debug("y:")
    # logger.debug(y)
    
    # sphere field:
    v, u = np.meshgrid(y, x)
    b, a = np.meshgrid(y, x)
    
    cond = (a-sphc[0])**2+(b-sphc[1])**2 < r
    # v = -(30*v-1)
    # u = 30*u-1
    u[cond] = ks*(u[cond]-sphc[0])
    v[cond] = -ks*(v[cond]-sphc[1])

    # river field
    # u[cond == False] = 0
    # v[cond == False] = 0
    u[cond == False] = kr*u[cond == False]*(u[cond == False]-h)
    v[cond == False] = 0
    # u = kr*u
    # u = (u+h)*(u-h)
    # v[:] = 0
    logger.debug("u")
    logger.debug(u.shape)
    # logger.debug(u[1])
    # logger.debug(u[150])
    # logger.debug(u[151])
    # logger.debug(u[152])
 
    if plot:
        import matplotlib.pyplot as plt
        plt.imshow(u)
        plt.show()
        plt.imshow(v)
        plt.show()
    
    # q = pylab.quiver(u, v)
    # q = pylab.quiver(u[170:230, 270:330], v[170:230, 270:330])
    # pylab.show(q)
    return(u, v)


def test_field(model_path, steps, progress=None,
               save_interval=3, start_from=None,
               plot=True):
    if start_from is None:
        csIdxs = imread(os.path.join(model_path, "centrals_img.png"), mode="L")
        file_idx = 0
    else:
        csIdxs = imread(os.path.join(model_path, start_from), mode="L")
        import re
        file_idx = int(re.search("\d+", start_from).group())

    logger.debug("csIdxs:")
    logger.debug(csIdxs.shape)
    logger.debug(csIdxs)
    logger.info("csIdxs.shape:")
    logger.info(csIdxs.shape)
    # print("0 in csIdxs:")
    # print(csIdxs[csIdxs == 0])
    # create_field0((300, 300))
    u, v = create_field0(csIdxs.shape, plot=plot)
    u_max, v_max = u.max(), v.max()

    # inverse speed:
    ui = u_max - u
    vi = v_max - v

    du = ui[1:] - ui[:-1]
    dv = vi[1:] - vi[:-1]
    du_min = abs(du).min()
    dv_min = abs(dv).min()
    print("max u, max v:")
    print((u.max(), v.max()))
    print("min du, min dv:")
    print((du_min, dv_min))
    dt = 0.1
    if du_min < dt:
        du_min = dt
    if dv_min < dt:
        dv_min = dt

    if plot:
        import matplotlib.pyplot as plt
        plt.imshow(csIdxs)
        plt.show()

    # csIdxs1 = csIdxs.copy()
    x_storage = np.zeros(u.shape)
    y_storage = np.zeros(v.shape)
    
    diff = 1
    # diff = 0.1
    
    save_interval_steps = file_idx
    for step in range(steps):
        # calculating speed:
        x_storage[x_storage < ui] += du_min  # *dt
        x_storage[x_storage >= ui] = 0
        
        # print("x_storage[x_storage < ui]:")
        # print(x_storage[x_storage < ui])

        y_storage[y_storage < vi] += dv_min  # *dt
        y_storage[y_storage >= vi] = 0
        # print("y_storage[y_storage < vi]:")
        # print(y_storage[y_storage < vi])

        for i in range(csIdxs.shape[0])[:-1]:
            shift(csIdxs, x_storage, u, i)
        
        for i in range(csIdxs.shape[1])[:-1]:
            shift(csIdxs.T, y_storage.T, v.T, i)

            '''
            for j in range(csIdxs.shape[1])[0:-1]:
                # for x (u) direction:
                x_storage[i, j] = x_storage[i, j] + abs(u[i, j])*dt
                i_idx = i
                if x_storage[i, j] > diff:  # *abs(u[i, j])
                    x_storage[i, j] = 0
                    if u[i, j] > 0:
                        # logger.debug("swap i pos")
                        swap(i, j, i+1, j, csIdxs, csIdxs1)
                        i_idx = i+1
                    elif(u[i, j] < 0):
                        # logger.debug("swap i neg")
                        swap(i, j, i-1, j, csIdxs, csIdxs1)
                        i_idx = i-1

                # for y (v) direction:
                y_storage[i, j] = y_storage[i, j] + abs(v[i, j])*dt
                if y_storage[i, j] > diff:  # *abs(v[i, j])
                    y_storage[i, j] = 0
                    if v[i, j] > 0:
                        # logger.debug("swap j pos")
                        swap(i_idx, j, i_idx, j+1, csIdxs, csIdxs1)
                    elif v[i, j] < 0:
                        # logger.debug("swap j neg")
                        swap(i_idx, j, i_idx, j-1, csIdxs, csIdxs1)
            '''
        # csIdxs = csIdxs1.copy()

        # update progress:
        if progress is not None:
            progress.succ(step+1)
        if step % save_interval == 0:
            save_interval_steps += 1
            imsave(os.path.join(model_path,
                                ("field_%s.png"
                                 % str(save_interval_steps))),
                   csIdxs)

    # import matplotlib.pyplot as plt
    # plt.imshow(csIdxs)
    # plt.show()
    if save_interval_steps != step+1:
        imsave(os.path.join(model_path,
                            "field_%s.png"
                            % str(save_interval_steps+1)),
               csIdxs)


def shift(csIdxs, storage, speed, i):

    '''Move dots in csIdxs according to
    storage values and speed direction'''

    i_max, j_max = csIdxs.shape
    and_func = np.vectorize(lambda x, y: x and y)

    # cond = and_func(csIdxs[i] != default, x_storage[i] == 0)
    args = (csIdxs[i] != default, storage[i] == 0, speed[i] > 0)
    js, = reduce(lambda acc, elm: and_func(acc, elm),
                 args[1:], args[0]).nonzero()
    # js, = and_func(cond, u[i] > 0)[i].nonzero()
    # x_neg, = and_func(cond, u[i] < 0)[i].nonzero()
    '''
    if len(js) > 0:
        print("js[::-1] for i=%d:" % i)
        print(js[::-1])
        print("js[-1]: ", js[-1])
        print(csIdxs[i, js[-1]+1])
    '''
    # if u > 0 => right
    # => from right to left
    # (ex: 00** -> 0*0* -> *00* -> *0*0 -> **00)
    for j in js[::-1]:
        # if emptiness in distination:
        if j+1 <= j_max and csIdxs[i][j+1] == default:
            # print("swap(%d, %d)" % (i, j))
            swap(i, j, i, j+1, csIdxs)

    # cond = and_func(csIdxs[i] != default, x_storage[i] == 0)
    args = (csIdxs[i] != default, storage[i] == 0, speed[i] < 0)
    js, = reduce(lambda acc, elm: and_func(acc, elm),
                 args[1:], args[0]).nonzero()
    # js, = and_func(cond, u[i] > 0)[i].nonzero()
    # x_neg, = and_func(cond, u[i] < 0)[i].nonzero()
    
    # if u < 0 => left
    # => from left to right
    # (ex: **00 -> *0*0 -> *00* -> 0*0* -> 00**)
    for j in js:
        # if emptiness in distination:
        if j >= 1 and csIdxs[i][j-1] == default:
            # print("swap(%d, %d)" % (i, j))
            swap(i, j, i, j-1, csIdxs)


def swap(i0, j0, i1, j1, a, b=None):
    '''
    b[i1, j1] = a[i0, j0]
    b[i0, j0] = a[i1, j1]
    '''
    tmp = a[i1, j1]
    a[i1, j1] = a[i0, j0]
    a[i0, j0] = tmp
    

def run():
    if '-model' in sys.argv:
        model_path = sys.argv[sys.argv.index('-model') + 1]
    else:
        raise(BaseException("-model needed"))
    if '-steps' in sys.argv:
        steps = sys.argv[sys.argv.index('-steps') + 1]
        steps = int(steps)
    else:
        raise(BaseException("-steps needed"))
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

    if '-start_from' in sys.argv:
        start_from = sys.argv[sys.argv.index('-start_from') + 1]
    else:
        start_from = None

    if '-save_interval' in sys.argv:
        save_interval = sys.argv[sys.argv.index('-save_interval') + 1]
        save_interval = int(save_interval)
    else:
        save_interval = 3

    if '-plot' in sys.argv:
        plot = sys.argv[sys.argv.index('-plot') + 1]
        plot = eval(plot)
    else:
        plot = False

    # from hybriddomain.solvers.hs.remoterun.progresses.progress_cmd import ProgressCmd
    # progress_cmd = ProgressCmd(steps)
    from hybriddomain.solvers.ms.remoterun.progresses.progress_cmd import SimpleProgress
    progress_cmd = SimpleProgress(steps)

    print("save_interval:")
    print(save_interval)
    test_field(model_path, steps, progress=progress_cmd,
               start_from=start_from, save_interval=save_interval,
               plot=plot)

    if model_path is not None:
        postproc = Postproc(logger, model_path, results_name="field")
        postproc.createVideoFile()

