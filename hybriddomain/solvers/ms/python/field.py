'''
~/anaconda3/bin/./python3 -c "import hybriddomain.solvers.ms.python.field as ts; ts.run()" -model ~/Documents/projects/projectsNew/lab/hybriddomain/hybriddomain/gui/2d/web/model/data/physics/n-body/test1 -steps 130 -log_level info -start_from field_350.png
~/anaconda3/bin/./python3 -c "import hybriddomain.solvers.ms.python.field as ts; ts.run()" -model ~/Documents/projects/projectsNew/lab/hybriddomain/hybriddomain/gui/2d/web/model/data/physics/n-body/test0 -steps 7 -log_level info
'''
import os
import sys
import numpy as np
import pylab
from matplotlib.pyplot import imsave

from hybriddomain.solvers.ms.python.solver import imread

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ms.field')
logger.setLevel(level=log_level)


def create_field0(shape=None):
    if shape is not None:
        x = np.linspace(0, 3, shape[0])
        y = np.linspace(0, 5.5, shape[1])
        # y = np.linspace(0, 3, shape[1])
        # sphere_center:
        # sphc = (3/2, 3/2)
        # sphc = (3/2, 5.5/2)
        sphc = (3/2, 1)
        r = 1
        ks = 1
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
        ks = 3
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
               save_interval=3, start_from=None):
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

    # create_field0((300, 300))
    u, v = create_field0(csIdxs.shape)
    print("max u, max v:")
    print((u.max(), v.max()))
    
    import matplotlib.pyplot as plt
    plt.imshow(csIdxs)
    plt.show()

    csIdxs1 = csIdxs.copy()
    x_storage = np.zeros(u.shape)
    y_storage = np.zeros(v.shape)
    diff = 1
    # diff = 0.1
    dt = 0.1
    save_interval_steps = file_idx
    for step in range(steps):
        for i in range(csIdxs.shape[0])[0:-1]:
            for j in range(csIdxs.shape[1])[0:-1]:
                # for x (u) direction:
                x_storage[i, j] = x_storage[i, j] + abs(u[i, j])*dt
                i_idx = i
                if x_storage[i, j] > diff*abs(u[i, j]):
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
                if y_storage[i, j] > diff*abs(v[i, j]):
                    y_storage[i, j] = 0
                    if v[i, j] > 0:
                        # logger.debug("swap j pos")
                        swap(i_idx, j, i_idx, j+1, csIdxs, csIdxs1)
                    elif v[i, j] < 0:
                        # logger.debug("swap j neg")
                        swap(i_idx, j, i_idx, j-1, csIdxs, csIdxs1)
        csIdxs = csIdxs1.copy()

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

    
def swap(i0, j0, i1, j1, a, b):
    b[i1, j1] = a[i0, j0]
    b[i0, j0] = a[i1, j1]
    '''
    tmp = a[i1, j1]
    a[i1, j1] = a[i0, j0]
    a[i0, j0] = tmp
    '''


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

    from hybriddomain.solvers.hs.remoterun.progresses.progress_cmd import ProgressCmd
    progress_cmd = ProgressCmd(steps)
    
    test_field(model_path, steps, progress=progress_cmd,
               start_from=start_from)
