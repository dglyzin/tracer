# -*- coding: utf-8 -*-
'''
Created on Sep 23, 2015

@author: dglyzin
'''

from mpi4py import MPI
import numpy as np
import argparse
from domainmodel.binaryFileReader import readDomFile
import domainmodel.dbConnector as dbc
from domainmodel.enums import *
import time
import os

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
    comp_status = np.zeros(1, dtype="int32")
    lastStepAccepted = np.zeros(1, dtype="int32")
    timeStep = np.zeros(1, dtype="float64")
    problemTime = np.zeros(1, dtype="float64")
    readyToSave = np.zeros(1, dtype="int32")
    percentChanged = np.zeros(1, dtype="int32")
    percentage = np.zeros(1, dtype="int32")
    
    db,cur = dbc.getDbConn(args.jobId)
    dbc.setDbJobPercentage(db, cur, args.jobId, 0)
    
    user_status[0] = dbc.getDbUserStatus(cur, args.jobId)
    #user_status[0] = USER_STATUS_STOP
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
    world.Recv([comp_status, MPI.INT], source=1, tag = 0)    
    #todo change state in db to running& ser slurm task ID
    dbc.setDbJobState(db, cur, args.jobId, comp_status[0])
    
    slurmId = os.getenv("SLURM_JOB_ID")
    dbc.setDbSlurmId(db, cur, args.jobId, slurmId)
    dbc.setDbJobStartTime(db, cur, args.jobId)
    dbc.clearDbJobFinishTime(db, cur, args.jobId)
    
    #main computing loop
    while (user_status[0] == USER_STATUS_START) and (comp_status[0] == JS_RUNNING):
        world.Recv([lastStepAccepted, MPI.INT], source=1, tag = 0)
        world.Recv([timeStep, MPI.DOUBLE], source=1, tag = 0)
        world.Recv([problemTime, MPI.DOUBLE], source=1, tag = 0)

        world.Recv([percentChanged, MPI.INT], source=1, tag = 0)
        if percentChanged[0] == 1:
            world.Recv([percentage, MPI.INT], source=1, tag = 0)
            dbc.setDbJobPercentage(db, cur, args.jobId, percentage[0])

        world.Recv([readyToSave, MPI.INT], source=1, tag = 0)
        world.Recv([comp_status, MPI.INT], source=1, tag = 0)
        #ready to save is actually a moment for lenghty 
        #read/write the db
        #save solution/pictures
        if (readyToSave[0] == 1):
            print "PM: time to save but nothing I can do so far: ", problemTime[0]
            #core decided it's saving time
            #we should receive all the data and save it
            #also save pictures and filename to database
            #world.Recv([data, MPI.DOUBLE], source=idx, tag = 0)    
            dbc.setDbJobState(db, cur, args.jobId, comp_status[0])
            user_status[0] = dbc.getDbUserStatus(cur, args.jobId)
             

        
        
        world.Bcast([user_status, MPI.INT], root=0)
        
        
        
    #end of computing loop    
    if (user_status[0] != USER_STATUS_START):
        print "Leaving main loop with user status ", user_status[0]
    if (comp_status[0] != JS_RUNNING):
        print "Leaving main loop with job state ", comp_status[0]

    dbc.setDbJobFinishTime(db, cur, args.jobId)

    dbc.setDbJobState(db, cur, args.jobId, comp_status[0])
    if comp_status[0] == JS_FINISHED:
        dbc.setDbJobPercentage(db, cur, args.jobId, 100)    
    dbc.freeDbConn(db, cur)



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
