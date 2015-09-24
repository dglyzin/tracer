# -*- coding: utf-8 -*-
'''
Аргументы:
0. уникальный id задачи, если -1 то работаем без базы
1. json-файл проекта
2. json-файл подключения
3.
Если этот аргумент не указан, то вычисления начинаются с нуля
иначе продолжается либо с последнего существующего, либо с явно указанного
-cont
-cont=<bin state filename to continue>
4. 
-finish=255
время для окончания вычислений, замещает время из json


Модуль импортирует входной json
Покдлючается к удаленной машине
Копирует туда этот же json и напускает на него jsontobin
Запускает решатель

model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''
remoteRunScriptName='project.sh'
remoteProjectFileName='project.json'
remoteMp4Name = 'project.mp4'

import json
import os
import socket
import getpass
import paramiko
import argparse
from collections import OrderedDict



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
        
        
def remoteProjectRun(connection, inputFile, continueEnabled, optionalArgs):
    #get project file name without extension
    print inputFile
    projectPathName, _ = os.path.splitext(inputFile)   
    projectName = os.path.basename(projectPathName)
    #get password
    if connection.password == "":
        tmpPass = os.getenv("CLUSTER_PASS")
        if tmpPass is None:
            print "Please enter password for user "+ connection.username+":"
            passwd = getpass.getpass()
        else:
            passwd = tmpPass
    else:
        passwd = connection.password

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #print conn.host, conn.username, passwd, conn.port
    try:
        client.connect(hostname=connection.host, username=connection.username, password=passwd, port=connection.port )

        print "Checking if folder "+connection.workspace+" exists..."
        stdin, stdout, stderr = client.exec_command('test -d '+connection.workspace)
        if stdout.channel.recv_exit_status():
            print "Please create workspace folder and put hybriddomain preprocessor into it"
            return
        else:
            print "Workspace OK."

        projFolder = connection.workspace+"/"+projectName
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
        cftp=client.open_sftp()
        cftp.put(inputFile, projFolder+"/"+remoteProjectFileName)
        cftp.close()
        
        #3 Run jsontobin on json
        print 'Running preprocessor:'
        command = 'python '+connection.tracerFolder+'/hybriddomain/jsontobin.py '+ projFolder+'/'+remoteProjectFileName + " " + connection.tracerFolder
        
        print command, optionalArgs
        stdin, stdout, stderr = client.exec_command(command+optionalArgs)
        print stdout.read()

        #4 Run Solver binary on created files
        print "Checking if solver executable at "+connection.tracerFolder+"/hybridsolver/bin/HS exists..."
        stdin, stdout, stderr = client.exec_command('test -f '+connection.tracerFolder + "/hybridsolver/bin/HS")
        if stdout.channel.recv_exit_status():
            print "Please provide correct path to the solver executable."
            return
        else:
            print "Solver executable found."

        stdin, stdout, stderr = client.exec_command('sh '+projFolder+'/'+remoteRunScriptName)
        print stdout.read()
        print stderr.read()
        
        #get resulting files
        #cftp=client.open_sftp()
        #cftp.get(projFolder+"/"+remoteMp4Name, projectPathName+".mp4")
        #cftp.close()
        
        client.close()

    #Обрабатываю исключения
    except paramiko.ssh_exception.AuthenticationException:
        return u'Неверный логин или пароль'
    except socket.error:
        return u'Указан неправильный адрес или порт'
    except paramiko.ssh_exception.SSHException:
        return u'Ошибка в протоколе SSH'



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
    parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
    
    args = parser.parse_args()
    
    connFileName = args.connFileName    
    inputFile = args.projectFileName
    
    
    
    finishTime = args.finish
    finishTimeProvided = not (finishTime is None)
    continueFileName = args.cont  
    continueEnabled = not (continueFileName is None)
    continueFnameProvided =  not (continueFileName == "/") if continueEnabled else False
        
    
  
    optionalArgs=''
    
    if not (args.jobId is None):
        optionalArgs+=" -jobId "+str(args.jobId)
    if finishTimeProvided:
        optionalArgs+=" -finish "+str(finishTime)
    if continueEnabled:
        optionalArgs+=" -cont"
        if continueFnameProvided:
            optionalArgs+=" "+continueFileName
    if args.debug:
        optionalArgs+=" -debug"
        
        
    connFile = open(connFileName,"r")    
    connDict = json.loads(connFile.read())
    connFile.close()
    
    connection = Connection()
    connection.fromDict(connDict)        
       
    remoteProjectRun(connection, inputFile, continueEnabled, optionalArgs)


