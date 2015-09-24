'''
Created on Sep 23, 2015

@author: dglyzin
'''

from mpi4py import MPI
import numpy as np

def get_acquainted():
    pass

def start_serving():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    if rank == 0:
        data = np.empty(1, dtype="float64")
        for idx in range(1,size):
            comm.Recv([data, MPI.DOUBLE],  source=idx, tag = 0)
            print data
    else:        
        data = np.empty(1, dtype="float64")
        data[0] = rank+100
        comm.Send([data, MPI.DOUBLE], dest = 0, tag = 0)

if __name__ == '__main__':
    start_serving()
