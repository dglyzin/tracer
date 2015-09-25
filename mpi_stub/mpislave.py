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
    print "i am slave", rank
    print MPI.Get_processor_name()
if __name__ == '__main__':
    start_serving()
