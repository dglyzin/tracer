'''
USAGE:
    hybriddomain/domainmodel/ms$: python3 main.py
  
    # for tests/2dTests/test2d_for_intervals_single.json only
    # (Block0CountX ...)

    # go to ms/cpp or ms/cuda
    # make solver_cpp
    g++ -I include -g -shared -o solver_cpp.so kernels.cpp from_test_template_2d.cpp -fPIC

    # make solver_gpu
    nvcc -Xcompiler -fPIC -shared -o solver_gpu.so core_v1.cu

    # go back to mini_solver
    # run

       python main.py

    # or use from interpreter:

       >>> import main as mn
       >>> mn.main()

'''
import numpy as np
import ctypes as ct
from time import time
import os
import matplotlib.pyplot as plt

import logging
import subprocess


Block0CountX = 81
Block0CountY = 81
SIZE_OF_RESULT = Block0CountX * Block0CountY


# extract compute_gpu_for_ctype function pointer
# in the shared object core.so:
# nvcc -Xcompiler -fPIC -shared -o core.so core.cu
def get_solver(path=None, cuda=False):
    '''
    DESCRIPTION:
    Get function from .so
    '''
    if cuda:
        _so = 'solver_gpu.so'
    else:
        _so = 'solver_cpp.so'

    # path to core.so
    if path is not None:
        dllName = os.path.join(path, _so)
    else:
        dllName = os.path.join(os.getcwd(), _so)

    print("dllName")
    print(dllName)
    # dllName = os.path.join(os.getcwd(), 'cpp', 'solver_cpp.so')
    # dllName = os.path.join(os.getcwd(), 'cuda', 'solver_gpu.so')

    dll = ct.CDLL(dllName, mode=ct.RTLD_GLOBAL)  # ct.DEFAULT_MODE
    func = dll.compute_for_ctype

    # types of input arguments:

    func.argtypes = [ct.POINTER(ct.c_int),  # int *  funcIdxs
                     ct.POINTER(ct.c_double),  # double* result
                     ct.POINTER(ct.POINTER(ct.c_double * SIZE_OF_RESULT)),  # double** source
                     ct.POINTER(ct.c_double),  # double* params
                     ct.POINTER(ct.c_double),  # double** ic
                     ct.c_int32,  # int SIZE_OF_RESULT
                     ct.c_int32,  # int COUNT_OF_DELAYS
                     ct.c_int32,  # int COUNT_OF_PARAMS
                     ct.c_int32]  # int ITERATION_COUNT
    return func


# convenient python wrapper for _solver
# it does all job with types convertation
# from python ones to C++ ones
def solver(funcIdxs, result, source, params, ic,
           ITERATION_COUNT, path=None, cuda=False):
    '''
    DESCRIPTION:
    Parameter result_p and source_p used for return value (will changed)
    '''
    funcIdxs_p = funcIdxs.ctypes.data_as(ct.POINTER(ct.c_int))
    result_p = result.ctypes.data_as(ct.POINTER(ct.c_double))
    source_p = source.ctypes.data_as(ct.POINTER(ct.c_double*SIZE_OF_RESULT))
    params_p = params.ctypes.data_as(ct.POINTER(ct.c_double))
    ic_p = ic.ctypes.data_as(ct.POINTER(ct.c_double))
    
    COUNT_OF_DELAYS = source.shape[0]
    COUNT_OF_PARAMS = params.size

    # create _matrix_mult function with get_solver()
    _solver = get_solver(path, cuda)

    _solver(funcIdxs_p, result_p, source_p, params_p, ic_p,
            SIZE_OF_RESULT, COUNT_OF_DELAYS, COUNT_OF_PARAMS,
            ITERATION_COUNT)


def main(_plot=True, cuda=False):
    
    COUNT_OF_DELAYS = 1
    ITERATION_COUNT = 128

    # init arrays
    funcIdxs = np.zeros((Block0CountY, Block0CountX)).astype('int32')
    
    # default
    funcIdxs[:] = 0
    
    # side 2
    funcIdxs[0] = 16
    
    # side 3
    funcIdxs[-1] = 16
    
    # side 0
    funcIdxs.T[0] = 16
    
    # side 1
    funcIdxs.T[-1] = 16
    funcIdxs = funcIdxs.astype('int32')

    result = np.zeros((Block0CountY, Block0CountX)).astype('double')
    result[:] = 4.0
    result = result.astype('double')

    source = np.zeros((COUNT_OF_DELAYS, Block0CountY, Block0CountX)).astype('double')
    source[0][:] = 4.0
    source = source.astype('double')

    params = np.zeros((4))
    params[:] = 1.0
    params = params.astype('double')

    # interconnect dont used now
    ic = np.zeros((1)).astype('double')

    # for time collecting
    time_current = time()
    
    # main code
    solver(funcIdxs, result, source, params, ic,
           ITERATION_COUNT, cuda=cuda)
    
    # time
    time_delta = time() - time_current
    s = np.timedelta64(1, 's')
    us = np.timedelta64(s, 'us')
    time_delta = (time_delta * us)

    # print("A=")
    # print(a)
    
    if plot:
        _plt = plot(result)
        _plt.show()

    print("time =")
    print(time_delta)

    return(str(time_delta))


def plot(result):
    # normalize:
    result = result/result.max()
    result = 256*result
    plt.imshow(result)
    # plt.plot(result)
    return(plt)


def compile_cpp(path=None, _stderr=None):
    # call g++
    # g++ -I include -g -shared -o solver_cpp.so kernels.cpp solver.cpp -fPIC

    # assuming that this file launched from hybriddomain
    if path is not None:
        includes = os.path.join(path, 'cpp', 'include')
        kernels_cpp = os.path.join(path, 'cpp', 'kernels.cpp')
        solver_cpp = os.path.join(path, 'cpp', 'solver.cpp')
        o = os.path.join(path, 'solver_cpp.so')
    else:
        includes = os.path.join('cpp', 'include')
        kernels_cpp = os.path.join('cpp', 'kernels.cpp')
        solver_cpp = os.path.join('cpp', 'solver.cpp')
        o = 'solver_cpp.so'
    cmd = ['g++', '-I', includes, '-g', '-shared', '-o',
           o, kernels_cpp, solver_cpp, '-fPIC']
    # logger.debug("cmd = %s" % str(cmd))
    print(cmd)
    '''
    stdout and stderr PIPE means
    that new child stream will be created
    so standart output will be unused.
    See:
    https://docs.python.org/2.7/library/subprocess.html#frequently-used-arguments
    https://docs.python.org/2.7/library/subprocess.html#subprocess.Popen.communicate
    '''
    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if (err is not None and len(err) > 0
        and _stderr is None):
        raise(GccException(err))
    if _stderr is not None:
        print("out")
        print(out)
        print("err")
        print(err)
    return(out)


def compile_cuda(path=None, _stderr=None):
    # call g++
    # g++ -I include -g -shared -o solver_cpp.so kernels.cpp solver.cpp -fPIC

    # assuming that this file launched from hybriddomain
    if path is not None:
        solver_gpu = os.path.join(path, 'cuda', 'core.cu')
        o = os.path.join(path, 'solver_gpu.so')
    else:
        solver_gpu = os.path.join('cuda', 'core.cu')
        o = 'solver_gpu.so'

    cmd = ['nvcc', '-Xcompiler', '-fPIC', '-shared', '-o',
           o, solver_gpu]
    # logger.debug("cmd = %s" % str(cmd))
    print(cmd)
    '''
    stdout and stderr PIPE means
    that new child stream will be created
    so standart output will be unused.
    See:
    https://docs.python.org/2.7/library/subprocess.html#frequently-used-arguments
    https://docs.python.org/2.7/library/subprocess.html#subprocess.Popen.communicate
    '''
    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if (err is not None and len(err) > 0
        and _stderr is None):
        raise(GccException(err))
    if _stderr is not None:
        print("out")
        print(out)
        print("err")
        print(err)
    return(out)


class GccException(Exception):
    '''
    DESCRIPTION:
    For cathing error of gcc.
    For tests cases in tester.py.
    '''
    def __init__(self, err):
        self.err = err


# testing
if __name__ == '__main__':
    cuda = True
    if cuda:
        compile_cuda(_stderr=1)
    else:
        compile_cpp()
    main(cuda=cuda)
