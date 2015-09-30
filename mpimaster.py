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
    #0. broadcast to everyone user status from db
    
    #1. collect from everyone step processing status
    #    if step was successful, continue
    #2. get new time step here and new time
    #3. collect solution if it is time to save it
    #4. broadcast user status from db, goto 1 or exit
    
    #-1
    comm = MPI.COMM_WORLD
    python_comm = comm.Split(0, 0)
   

    rank = comm.Get_rank()
    size = comm.Get_size()

    user_status = np.zeros(1, dtype="int32")
    
    user_status[0] = USER_STATUS_START
    #0.
    comm.Bcast([user_status, MPI.INT], root=0)



if __name__ == '__main__':
    #input args
    parser = argparse.ArgumentParser(description='Master MPI process.', epilog = "Have fun!")
    parser.add_argument('jobId', type = int, help = "unique job ID")
    parser.add_argument('domainFileName', type = str, help = ".dom file")    
    parser.add_argument('flag', type = int, help = "secret flag")
    parser.add_argument('finishTime', type=float, help = "new finish time to override json value")
    parser.add_argument('contFileName', type=float, help = "filename to continue from")
    
    args = parser.parse_args()
    geometry, _, _, _, _, dimension = readDomFile(args.domainFilename)
    start_serving(args, geometry, dimension)
