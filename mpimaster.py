# -*- coding: utf-8 -*-
'''
Created on Sep 23, 2015

@author: dglyzin
'''

from mpi4py import MPI
import numpy as np
import argparse
from domainmodel.binaryFileReader import readDomFile
from domainmodel.dbConnector import setDbJobState
from domainmodel.enums import *
import time

def polling_receive(comm, source):
    # Set this to 0 for maximum responsiveness, but that will peg CPU to 100%
    sleep_seconds = 0.1
    if sleep_seconds > 0:
        while not comm.Iprobe(source=MPI.ANY_SOURCE):
            time.sleep(sleep_seconds)
    
    status = MPI.Status()
    result = comm.recv(source=MPI.ANY_SOURCE, status=status)
            
    return result

def get_acquainted():
    pass


    

def start_serving(args, geometry, dimension):
    #compute cycle:
    #-1. split workers into separate communicator
    world = MPI.COMM_WORLD
    python_comm = world.Split(0, 0)
   

    rank = world.Get_rank()
    size = world.Get_size()

    user_status = np.zeros(1, dtype="int32")
    
    #user_status[0] = USER_STATUS_START
    user_status[0] = USER_STATUS_STOP
    #    Порядок работы
    #                    1. WORLD+COMP                          2. WORLD ONLY
    #+    1. WORLD Bcast user-status, источник - world-0    |    +
    #+                 xx.  идет расчет шага, используется только COMP
    #пока нет    2. WORLD Allreduce compute-status                 |    +
    #пока нет       xx.  идет расчет ошибки, используется только COMP
    #+    5. accept/reject, comp-0 -> world-0               |    -
    #+    6. new timestep, comp-0 -> world-0                |    -
    #+    7. ready to collect data, comp-0 -> world-0       |    -
    #+    8. WORLD collect data                             |    +
    ##  9. stop/continue comp-0 -> world-0                |    -

    #1.
    world.Bcast([user_status, MPI.INT], root=0)
    #world.Recv([data, MPI.DOUBLE], source=idx, tag = 0)


if __name__ == '__main__':
    #input args
    parser = argparse.ArgumentParser(description='Master MPI process.', epilog = "Have fun!")
    parser.add_argument('jobId', type = int, help = "unique job ID")
    parser.add_argument('domainFileName', type = str, help = ".dom file")    
    parser.add_argument('flag', type = int, help = "secret flag")
    parser.add_argument('finishTime', type=str, help = "new finish time to override json value")
    parser.add_argument('contFileName', type=str, help = "filename to continue from")
    
    args = parser.parse_args()
    geometry, _, _, _, _, dimension = readDomFile(args.domainFileName)
    start_serving(args, geometry, dimension)
    print "Python Master finished OK."
