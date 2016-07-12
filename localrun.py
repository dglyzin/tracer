# -*- coding: utf-8 -*-
'''
Created on July 07, 2016

@author: dglyzin

запускает задачу, находясь на кластере
нужно главным образом для тестов

Аргументы:
1. json-файл проекта
2.
Если этот аргумент не указан, то вычисления начинаются с нуля
иначе продолжается либо с последнего существующего, либо с явно указанного
-cont
-cont=<bin state filename to continue>
3. 
-finish=255
время для окончания вычислений, замещает время из json

model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''

import os
import argparse
from subprocess import call
import glob
        
def localProjectRun(inputFile, continueEnabled, continueFnameProvided, continueFileName, jobId, finishTimeProvided, finishTime, debug, outFileName):
    '''      
      inputFile:  project file
      continueEnabled: true if user wants to continue from computed file 
      continueFnameProvided: true if user wants to continue from specific file, false if the last computed file to be used
      continueFileName:
      jobId: id of the task in the db
      finishTimeProvided: true if user wants to override json value for finish time
      finishTime:
      debug: true if user wants to run small problem (10 min. max)
      
    '''
    runOk = True
    tracerFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/..")
    #prepare command line argumetnts for preprocessor
    optionalArgs=[]    
    if not (jobId is None):
        optionalArgs+=["-jobId", str(jobId)]
    if finishTimeProvided:
        optionalArgs+=["-finish", str(finishTime)]
    if continueEnabled: 
        optionalArgs+=["-cont"]
        if continueFnameProvided:
            optionalArgs+=[continueFileName]
    if debug:
        optionalArgs+=["-debug"]
    if not (outFileName is None):
        optionalArgs+=["-outFileName", outFileName]
    #get project file name without extension
    inputFile = os.path.abspath(inputFile)
    print "Absolute project path:", inputFile        
    projectFolder = os.path.dirname(inputFile)
    print projectFolder
    projectPathName, _ = os.path.splitext(inputFile)
    if not (outFileName is None):
        projectPathName = os.path.join(projectFolder, outFileName )  
    
    if not continueEnabled:  
        call(["rm", projectPathName+'.cpp'])
        call(["rm", projectFolder+'/libuserfuncs.so'])
        call(["rm", projectPathName+'.sh'])
        call(["rm", projectPathName+'.dom'])
        files = glob.glob(projectPathName+'*.lbin')        
        call(["rm"] + files)     
        files = glob.glob(projectPathName+'*.dbin')
        call(["rm"] + files)        
        print "Folder cleaned."                
    else:
        print "Folder exists, no cleaning needed."
        #now check if file to continue from exists
        if continueFnameProvided:
            print "Checking if file to continue from  ("+continueFileName+") exists..."            
            if call(['test', '-f', continueFileName]):
                print "File not found, please specify existing file to continue"
                return
            else:
                print "File OK."


    
    #3 Run jsontobin on json    
    command = ['python', tracerFolder+'/hybriddomain/jsontobin.py', inputFile, tracerFolder]
    print '\nRunning preprocessor:', command    
    call(command+optionalArgs)

    #4 Run Solver binary on created files
    print "Checking if solver executable at "+tracerFolder+"/hybridsolver/bin/HS exists..."    
    if call(['test', '-f', tracerFolder + "/hybridsolver/bin/HS"]):
        print "Please provide correct path to the solver executable."
        return
    else:
        print "Solver executable found."
    
    call(['sh', projectPathName + '.sh'])
    
    return runOk


def finalParseAndRun(inputFileName, args):
    finishTimeProvided = not (args.finish is None)
    continueFileName = args.cont  
    continueEnabled = not (continueFileName is None)
    continueFnameProvided =  not (continueFileName == "/") if continueEnabled else False
       
    return localProjectRun(inputFileName, continueEnabled, continueFnameProvided, continueFileName, args.jobId, finishTimeProvided, args.finish, args.debug, args.outFileName)


if __name__=='__main__':    
    parser = argparse.ArgumentParser(description='Processing json file on a local cluster.', epilog = "Have fun!")
    #mandatory argument, json filename
    parser.add_argument('projectFileName', type = str, help = "local json file to process")
    #optional argument, unique job Id for identification in database
    parser.add_argument('-jobId', type = int, help = "unique job ID") 
    #optional argument, exactly one float to override json finish time
    parser.add_argument('-finish', type=float, help = "new finish time to override json value")
    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
    parser.add_argument('-outFileName', type = str, help="specify output project filename (fileName is default)")
    args = parser.parse_args()
    
    inputFileName = args.projectFileName
   
    finalParseAndRun(inputFileName, args)


