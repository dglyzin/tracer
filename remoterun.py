# -*- coding: utf-8 -*-
'''
Аргументы:
1. json-файл подключения
2. json-файл проекта
3. -jobId=  
уникальный id задачи, если параметра нет, то работаем без базы и без питоновского мастер-процесса в mpi
работа с базой возможна только если запись номер jobId была предварительно создана веб-сервером

4.
Если этот аргумент не указан, то вычисления начинаются с нуля
иначе продолжается либо с последнего существующего, либо с явно указанного
-cont
-cont=<bin state filename to continue>
5. 
-finish=255
время для окончания вычислений, замещает время из json


Модуль импортирует входной json
Покдлючается к удаленной машине
Копирует туда этот же json и напускает на него jsontobin
Запускает решатель

model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''
#remoteRunScriptName='project.sh'
#remoteProjectFileName='project.json'
#remoteMp4Name = 'project.mp4'
from __future__ import print_function

import json
import os
import socket
import getpass
import paramiko
import argparse
from collections import OrderedDict

from domainmodel.logger import Logger, LL_USER, LL_DEVEL, LL_API 


class Connection(object):
    def __init__(self):
        self.host = "corp7.uniyar.ac.ru"
        self.port = 2222
        self.username = "tester"
        self.password = ""
        self.workspace = "/home/tester/Tracer"
        self.tracerFolder = "/home/dglyzin/Tracer"        

    def toDict(self):
        connDict = OrderedDict([
        ("Host", self.host),
        ("Port", self.port),
        ("Username", self.username),
        ("Password", self.password),
        ("Workspace", self.workspace),
        ("TracerFolder", self.tracerFolder)
        ])
        return connDict

    def fromDict(self, connDict):
        self.host = connDict["Host"]
        self.port = connDict["Port"]
        self.username = connDict["Username"]
        self.password = connDict["Password"]
        self.workspace = connDict["Workspace"]
        self.tracerFolder = connDict["TracerFolder"]
    
    def loadFromFile(self, fileNamePath):
        pass
        
def remoteProjectRun(connection, inputFile, params, projectFolder, logger):
    '''
      connection: file with connection settings
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
    optionalArgs = ''
    if not (params["jobId"] is None):
        optionalArgs += " -jobId "+str(params["jobId"])
    if not (params["finish"] is None):
        optionalArgs += " -finish "+str(params["finishTime"])
    if params["continueEnabled"]:
        optionalArgs += " -cont"
        if params["continueFnameProvided"]:
            optionalArgs += " "+params["continueFileName"]
    if params["nortpng"]:
        optionalArgs += " -nortpng"
    if not (params["partition"] is None):
        optionalArgs += " -p "+str(params["partition"])
    if not (params["nodes"] is None):
        optionalArgs += " -w " + str(params["nodes"])
    if not (params["affinity"] is None):
        optionalArgs += " -aff " + str(params["affinity"])
    if not (params["mpimap"] is None):
        optionalArgs += " -mpimap " + str(params["mpimap"])


    
    #get project file name without extension
    logger.log(inputFile, LL_USER)
    if projectFolder is None:
        projectPathName, _ = os.path.splitext(inputFile)  
        localProjectPath, _ = os.path.split(projectPathName) 
        projectFolder = os.path.basename(projectPathName)
    
    projectTitle = projectFolder
    remoteRunScriptName = projectTitle+'.sh'
    remoteProjectFileName = projectTitle+'.json'
    remoteMp4Name = projectTitle+'.mp4'



    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #print conn.host, conn.username, passwd, conn.port
    try:
        client.connect(hostname=connection.host, username=connection.username, password=connection.password, port=connection.port )

        logger.log("Checking if folder "+connection.workspace+" exists...", LL_USER)
        stdin, stdout, stderr = client.exec_command('test -d '+connection.workspace)
        if stdout.channel.recv_exit_status():
            logger.log("Please create workspace folder", LL_USER)
            return()
        else:
            logger.log("Workspace OK.", LL_USER)

        projFolder = connection.workspace+"/"+projectFolder
        logger.log("Creating/cleaning project folder: ", LL_USER)
        stdin, stdout, stderr = client.exec_command('test -d  '+projFolder)
        if stdout.channel.recv_exit_status():
            stdin, stdout, stderr = client.exec_command('mkdir  '+projFolder)
            logger.log("Folder created.", LL_USER)
        else:
            if not params["continueEnabled"]:
                stdin, stdout, stderr = client.exec_command('rm -rf '+projFolder+'/*')
                stdout.read()
                logger.log("Folder cleaned.", LL_USER)                
            else:
                logger.log("Folder exists, no cleaning needed.", LL_USER)
                #now check if file to continue from exists
                if params["continueFnameProvided"]:
                    logger.log("Checking if file to continue from  ("+params["continueFileName"]+") exists...", LL_USER)
                    stdin, stdout, stderr = client.exec_command('test -f '+params["continueFileName"])
                    if stdout.channel.recv_exit_status():
                        logger.log("File not found, please specify existing file to continue", LL_USER)
                        return
                    else:
                        logger.log("File OK.", LL_USER)
                                      
        cftp=client.open_sftp()
        cftp.put(inputFile, projFolder+"/"+remoteProjectFileName)
        cftp.close()
        
        #3 Run jsontobin on json
        logger.log('\nRunning preprocessor:', LL_USER)
        
        if params["nocppgen"]:
            optionalArgs += ' -nocppgen'
            #also put cpp from local machine
            projectPathName, _ = os.path.splitext(inputFile)  
            cppFileNamePath = projectPathName+".cpp"
            remoteCppFileName, _ = os.path.splitext(remoteProjectFileName)
            remoteCppFileName += ".cpp"
            
            cftp=client.open_sftp()
            cftp.put(cppFileNamePath, projFolder+"/"+remoteCppFileName)
            cftp.close()
            
            
        command = 'python2 '+connection.tracerFolder+'/hybriddomain/jsontobin.py '+ projFolder+'/'+remoteProjectFileName + " " + connection.tracerFolder
        
        logger.log(command + optionalArgs, LL_USER)
        stdin, stdout, stderr = client.exec_command(command+optionalArgs)
        
        logger.log("finally", LL_USER)
        logger.log( stdout.read(), LL_USER)
        logger.log("jsontobin stderr:", LL_USER)
        logger.log(stderr.read(), LL_USER)
        logger.log("stderr END", LL_USER)

        #4 Run Solver binary on created files
        logger.log("Checking if solver executable at "+connection.tracerFolder+"/hybridsolver/bin/HS exists...", LL_USER)
        stdin, stdout, stderr = client.exec_command('test -f '+connection.tracerFolder + "/hybridsolver/bin/HS")
        if stdout.channel.recv_exit_status():
            logger.log("Please provide correct path to the solver executable.", LL_USER)
            return
        else:
            logger.log( "Solver executable found.", LL_USER)

        #stdin, stdout, stderr = client.exec_command('sh '+projFolder+'/'+remoteRunScriptName, get_pty=True)
        stdin, stdout, stderr = client.exec_command('sh '+projFolder+'/'+remoteRunScriptName + " 2>&1")
        for line in iter(lambda: stdout.readline(2048), ""): 
            try:
                logger.log(line, LL_USER, end='' )
            except:
                logger.log("Wrong symbol", LL_USER)
        logger.log(stdout.read(), LL_USER)
        logger.log(stderr.read(),LL_USER)
        
        #get resulting files
        logger.log("Downloading results...", LL_USER)
        cftp=client.open_sftp()
        cftp.chdir(projFolder)
        for filename in sorted(cftp.listdir()):
            if filename.endswith('mp4'):        
                cftp.get(filename, os.path.join(localProjectPath, filename) )
            if filename.endswith('out'):        
                cftp.get(filename, os.path.join(localProjectPath, filename) )
            
                #cftp.get(projFolder+"/"+remoteMp4Name, projectPathName+"-plot"+str(plotIdx)+".mp4")            
        cftp.close()
        logger.log("Done!", LL_USER)
        client.close()

    #Обрабатываю исключения
    except paramiko.ssh_exception.AuthenticationException:
        return u'Неверный логин или пароль'
    except socket.error:
        return u'Указан неправильный адрес или порт'
    except paramiko.ssh_exception.SSHException:
        return u'Ошибка в протоколе SSH'


def getConnection(connFileName):
    connFile = open(connFileName,"r")    
    connDict = json.loads(connFile.read())
    connFile.close()
    
    connection = Connection()
    connection.fromDict(connDict)        
    #get password
    if connection.password == "":
        connection.password = os.getenv("CLUSTER_PASS")
        if connection.password is None:
            print ("Please enter password for user "+ connection.username+":")
            connection.password = getpass.getpass()
    return connection


def finalParseAndRun(connection, inputFileName, args, projectFolder=None):
    continueFileName = args.cont      
    continueEnabled = not (continueFileName is None)
    continueFnameProvided =  not (continueFileName == "/") if continueEnabled else False
    
    logger = Logger(args.verbose, logAPI = False, logFileName = None)

    params = {
        "continueEnabled": continueEnabled,
        "continueFnameProvided": continueFnameProvided,
        "continueFileName": continueFileName,
        "jobId": args.jobId,
        "finish": args.finish,
        "partition": args.p,
        "nodes": args.w,
        "affinity": args.aff,
        "mpimap": args.mpimap,
        "nortpng": args.nortpng,
        "nocppgen": args.nocppgen
    }
       
    remoteProjectRun(connection, inputFileName, params, projectFolder, logger)
    logger.clean()

if __name__=='__main__':    
    parser = argparse.ArgumentParser(description='Processing json file on a remote cluster.', epilog = "Have fun!")
    parser.add_argument('connFileName', type = str, help = "local json file with connection info")    
    #mandatory argument, json filename
    parser.add_argument('projectFileName', type = str, help = "local json file to process")
    #optional argument, unique job Id for identification in database
    parser.add_argument('-jobId', type = int, help = "unique job ID") 
    #optional argument, exactly one float to override json finish time
    parser.add_argument('-finish', type=float, help = "new finish time to override json value")
    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    #partition to run on
    parser.add_argument('-p', type=str, help="slurm partition")
    #also node
    parser.add_argument('-w', type=str, help="slurm nodes")
    #also affinnity
    parser.add_argument('-aff', type=str, help="GOMP_CPU_AFFINITY='?' ")
    #also mapby
    parser.add_argument('-mpimap', type=str, help="mpirun --map-by argument")


    parser.add_argument('-nortpng', help="add this flag to avoid runtime png creation", action="store_true")
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=1, help="set verbosity level [default: %(default)s]")
    parser.add_argument('-nocppgen', help="add this flag to use pre-generated cpp with the same baseneame as .json", action="store_true")
    
    args = parser.parse_args()
    
    connFileName = args.connFileName    
    connection = getConnection(connFileName)

    inputFileName = args.projectFileName
   
    finalParseAndRun(connection, inputFileName, args)


