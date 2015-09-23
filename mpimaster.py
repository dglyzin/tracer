'''
Created on Sep 23, 2015

@author: dglyzin
'''

from mpi4py import MPI


def get_acquainted():
    pass

def start_serving():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    if rank == 0:
        for idx in range(size):
            recId = comm.recv(source=idx, tag = 0)
            print recId
    else:
        comm.send(rank+100, dest = 0, tag = 0)


if __name__ == '__main__':
    start_serving()