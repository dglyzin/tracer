# -*- coding: utf-8 -*-
'''
Модуль импортирует входной json
Создает по нему модель (включая и задачу, и мэппинг узлов-девайсов)
Создает бинарный файл с геометрией и свойствами области (*.dom)
Создает файл с функциями задачи (*.so)

Файл с состоянием не создается, т.к. у нас имеются функции, которые может вызвать ядро
для заполнения начальных значений


model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''

JS_STARTED = 0
JS_PREPROCESSING = 1
JS_QUEUED = 2
JS_RUNNING = 3
JS_CANCELLED = 4
JS_FINISHED = 5
JS_FAILED = 6

USER_STATUS_STOP = 0
USER_STATUS_START = 1
USER_STATUS_SLEEP = 2
USER_STATUS_END = 3

import argparse
from domainmodel.model import Model
from domainmodel.binarymodel import BinaryModel
from domainmodel.decomposer import partitionAndMap

from fileUtils import getSortedBinFileList
import os
import MySQLdb

def updateDbRecord(jobId):
    db = MySQLdb.connect(host="127.0.0.1", # your host, usually localhost
                         user="cherry", # your username
                         passwd="sho0ro0p", # your password
                         db="cluster") # name of the data base
    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor() 
    #1. get task id
    #command = 'python '+connection.preprocessorFolder+'/jsontobin.py '+str(jobId)+' '   +projFolder+'/'+remoteProjectFileName + " " + 
    #                       connection.solverExecutable + " " + connection.preprocessorFolder
    #2. add task to db
    #3. generate launcher script

    # Use all the SQL you like
    
    cur.execute("DELETE FROM task_results WHERE task_id="+str(jobId) )
    #now record is created form web ui
    #cur.execute("DELETE FROM jobs WHERE id="+str(jobId) )
    #cur.execute("INSERT INTO jobs (id, slurmid, starttime, finishtime, percentage, state, userstatus) VALUES ("+str(jobId)+", 0, NOW(), NOW(), 0, "+str(JS_PREPROCESSING)+", "+str(USER_STATUS_START)+")")
    cur.execute("UPDATE tasks SET update=1, state="+str(JS_PREPROCESSING)+" WHERE id="+str(jobId) )    
    db.commit()


def createBinaries(jobId, inputFile, solverExecutable, preprocessorFolder, runAtDebugPartition, 
                   finishTimeProvided, finishTime, continueEnabled, continueFnameProvided, continueFileName):    
    projectDir = os.path.dirname(inputFile)
    projectName, _ = os.path.splitext(inputFile)   
    projectTitle = os.path.basename(projectName)
    if projectName == '':
        print "Bad file name"
        return

    OutputDataFile = projectName+".dom"
    OutputFuncFile = projectName+".cpp"
    OutputRunFile = projectName+".sh"

    #we want to find the last computed state to continue if user does not provide filename but tell us to continue
    print projectDir
    if continueEnabled and not continueFnameProvided:
        try:
            continueFileName = os.path.join(projectDir, getSortedBinFileList(projectDir, projectTitle)[-1])
        except:
            print "No bin file to continue from!"
            return
  
    model = Model()
    model.loadFromFile(inputFile)
    print "Max derivative order is ", model.getMaxDerivOrder()
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)

    updateDbRecord(jobId)

    bm = BinaryModel(partModel)
    bm.saveFuncs(OutputFuncFile, preprocessorFolder)
    bm.saveDomain(OutputDataFile)
    bm.compileFuncs(OutputFuncFile)
    
    bm.createRunFile(jobId, OutputRunFile, projectDir, solverExecutable, preprocessorFolder, runAtDebugPartition, 
                     OutputDataFile, finishTimeProvided, finishTime, continueEnabled, continueFileName)

                
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Processing json file on a remote cluster.', epilog = "Have fun!")
    #mandatory argument, unique job Id for identification in database
    parser.add_argument('jobId', type = int, help = "unique job ID")
    #mandatory argument, json filename
    parser.add_argument('fileName', type = str, help = "local json file to process")
    parser.add_argument('solverExecutable', type = str, help = "Solver executable")
    parser.add_argument('preprocessorFolder', type = str, help = "Preprocessor folder")
    #optional argument, exactly one float to override json finish time
    parser.add_argument('-finish', type=float, help = "new finish time to override json value")
    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
    args = parser.parse_args()
  
    inputFile = args.fileName
    finishTime = args.finish
    finishTimeProvided = not (finishTime is None)
    continueFileName = args.cont  
    continueEnabled = not (continueFileName is None)
    continueFnameProvided =  not (continueFileName == "/") if continueEnabled else False

    print "jsontobin input!", inputFile, finishTimeProvided, finishTime, continueEnabled, continueFnameProvided, continueFileName
    createBinaries(args.jobId, inputFile, args.solverExecutable, args.preprocessorFolder, args.debug, finishTimeProvided, finishTime, continueEnabled, continueFnameProvided, continueFileName)
    
