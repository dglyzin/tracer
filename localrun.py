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
remoteRunScriptName='project.sh'
remoteProjectFileName='project.json'

import json
import os
import getpass
import argparse

        
def localProjectRun(inputFile, continueEnabled, continueFnameProvided, continueFileName, jobId, finishTimeProvided, finishTime, debug, projectFolder):
    '''      
      inputFile:  project file
      continueEnabled: true if user wants to continue from computed file 
      continueFnameProvided: true if user wants to continue from specific file, false if the last computed file to be used
      continueFileName:
      jobId: id of the task in the db
      finishTimeProvided: true if user wants to override json value for finish time
      finishTime:
      debug: true if user wants to run small problem (10 min. max)
      projectFolder: defaults to json file name unless specified
    '''
    
    #prepare command line argumetnts for preprocessor
    optionalArgs=''    
    if not (jobId is None):
        optionalArgs+=" -jobId "+str(jobId)
    if finishTimeProvided:
        optionalArgs+=" -finish "+str(finishTime)
    if continueEnabled:
        optionalArgs+=" -cont"
        if continueFnameProvided:
            optionalArgs+=" "+continueFileName
    if debug:
        optionalArgs+=" -debug"
    
    
    #get project file name without extension
    print inputFile
    if projectFolder is None:
        projectPathName, _ = os.path.splitext(inputFile)   
        projectFolder = os.path.basename(projectPathName)
    

    print "Checking if folder "+connection.workspace+" exists..."
    stdin, stdout, stderr = client.exec_command('test -d '+connection.workspace)
    if stdout.channel.recv_exit_status():
        print "Please create workspace folder and put hybriddomain preprocessor into it"
        return
    else:
        print "Workspace OK."

    projFolder = connection.workspace+"/"+projectFolder
    print "Creating/cleaning project folder: "
    stdin, stdout, stderr = client.exec_command('test -d  '+projFolder)
    if stdout.channel.recv_exit_status():
        stdin, stdout, stderr = client.exec_command('mkdir  '+projFolder)
        print "Folder created."
    else:
        if not continueEnabled:  
            stdin, stdout, stderr = client.exec_command('rm -rf '+projFolder+'/*')
            stdout.read()
            print "Folder cleaned."                
        else:
            print "Folder exists, no cleaning needed."
            #now check if file to continue from exists
            if continueFnameProvided:
                print "Checking if file to continue from  ("+continueFileName+") exists..."
                stdin, stdout, stderr = client.exec_command('test -f '+continueFileName)
                if stdout.channel.recv_exit_status():
                    print "File not found, please specify existing file to continue"
                    return
                else:
                    print "File OK."
        
    #copy instead
    cftp.put(inputFile, projFolder+"/"+remoteProjectFileName)
    
    #3 Run jsontobin on json
    print '\nRunning preprocessor:'
    command = 'python '+connection.tracerFolder+'/hybriddomain/jsontobin.py '+ projFolder +    '/'+remoteProjectFileName + " " + connection.tracerFolder
        
    print command, optionalArgs
    
    #4 Run Solver binary on created files
    print "Checking if solver executable at "+connection.tracerFolder+"/hybridsolver/bin/HS exists..."
    stdin, stdout, stderr = client.exec_command('test -f '+connection.tracerFolder + "/hybridsolver/bin/HS")
    if stdout.channel.recv_exit_status():
        print "Please provide correct path to the solver executable."
        return
    else:
        print "Solver executable found."


def finalParseAndRun(inputFileName, args, projectFolder):
    finishTimeProvided = not (args.finish is None)
    continueFileName = args.cont  
    continueEnabled = not (continueFileName is None)
    continueFnameProvided =  not (continueFileName == "/") if continueEnabled else False
       
    localProjectRun(connection, inputFileName, continueEnabled, continueFnameProvided, continueFileName, args.jobId, finishTimeProvided, args.finish, args.debug, projectFolder)


if __name__=='__main__':    
    parser = argparse.ArgumentParser(description='Processing json file on a local cluster.', epilog = "Have fun!")
    #mandatory argument, json filename
    parser.add_argument('projectFileName', type = str, help = "local json file to process")
    parser.add_argument('projectFolder', type = str, help = "folder to store project data")
    #optional argument, unique job Id for identification in database
    parser.add_argument('-jobId', type = int, help = "unique job ID") 
    #optional argument, exactly one float to override json finish time
    parser.add_argument('-finish', type=float, help = "new finish time to override json value")
    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
    
    args = parser.parse_args()
    
    inputFileName = args.projectFileName
   
    finalParseAndRun(inputFileName, args)


