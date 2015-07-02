# -*- coding: utf-8 -*-
'''
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


Модуль импортирует входной json
Покдлючается к удаленной машине
Копирует туда этот же json и напускает на него jsontobin
Запускает решатель

model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''
remoteRunScriptName='project.sh'
remoteProjectFileName='project.json'



import sys
import socket
import getpass
import paramiko
import argparse

from domainmodel.model import Model

def remoteProjectRun(inputFile, continueEnabled, optionalArgs):
    #2 Get connection data and copy json to the cluster
    model = Model()
    model.loadFromFile(inputFile)
    conn = model.connection
    if conn.password == "":
        print "Please enter password for user "+ model.connection.username+":"
        passwd = getpass.getpass()
    else:
        passwd = conn.password

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #print conn.host, conn.username, passwd, conn.port
    try:
        client.connect(hostname=conn.host, username=conn.username, password=passwd, port=conn.port )

        print "Checking if folder "+conn.workspace+" exists..."
        stdin, stdout, stderr = client.exec_command('test -d '+conn.workspace)
        if stdout.channel.recv_exit_status():
            print "Please create workspace folder and put hybriddomain preprocessor into it"
            return
        else:
            print "Workspace OK."

        projFolder = conn.workspace+"/"+model.projectName
        print "Creating/cleaning project folder: "
        stdin, stdout, stderr = client.exec_command('test -d  '+projFolder)
        if stdout.channel.recv_exit_status():
            stdin, stdout, stderr = client.exec_command('mkdir  '+projFolder)
            print "Folder created."
        else:
            if not continueEnabled:  
                stdin, stdout, stderr = client.exec_command('rm -rf '+projFolder+'/*')
                print "Folder cleaned."                
            else:
                print "Folder exists, no cleaning needed."                      
        cftp=client.open_sftp()
        cftp.put(inputFile, projFolder+"/"+remoteProjectFileName)
        cftp.close()
        
        #3 Run jsontobin on json
        print 'Running preprocessor:'
        command = 'python '+conn.workspace+'/hybriddomain/jsontobin.py '+projFolder+'/'+remoteProjectFileName
        
        print command, optionalArgs
        stdin, stdout, stderr = client.exec_command(command)
        print stdout.read()

        #4 Run Solver binary on created files
        print "Checking if solver executable at "+conn.solverExecutable+" exists..."
        stdin, stdout, stderr = client.exec_command('test -f '+conn.solverExecutable)
        if stdout.channel.recv_exit_status():
            print "Please provide correct path to the solver executable."
            return
        else:
            print "Solver executable found."

        stdin, stdout, stderr = client.exec_command('sh '+projFolder+'/'+remoteRunScriptName)
        print stdout.read()
        print stderr.read()


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
    #mandatory argument, json filename
    parser.add_argument('fileName', type = str, help = "local json file to process")
    #optional argument, exactly one float to override json finish time
    parser.add_argument('-finish', type=float, help = "new finish time to override json value")
    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    args = parser.parse_args()
    
    
    inputFile = args.fileName
    finishTime = args.finish
    finishTimeProvided = not (finishTime is None)
    continueFileName = args.cont  
    continueEnabled = not (continueFileName is None)
    continueFnameProvided = not (continueFileName == "/")
  
    optionalArgs=''
    if finishTimeProvided:
        optionalArgs+="-finish "+str(finishTime)
    if continueEnabled:
        optionalArgs+=" -cont"
        if continueFnameProvided:
            optionalArgs+=" "+continueFileName
    
       
    remoteProjectRun(inputFile, continueEnabled, optionalArgs)


