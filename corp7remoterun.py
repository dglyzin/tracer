# -*- coding: utf-8 -*-
'''
Модуль импортирует входной json
Покдлючается к удаленной машине
Копирует туда этот же json и напускает на него jsontobin
Запускает решатель

model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''

import sys
import socket
import getpass
import paramiko

from domainmodel.model import Model

def remoteProjectRun(InputFile):
    #2 Get connection data and copy json to the cluster
    model = Model()
    model.loadFromFile(InputFile)
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
        client.connect(hostname="corp7.uniyar.ac.ru", username=conn.username, password=passwd, port=2222 )

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
            stdin, stdout, stderr = client.exec_command('rm -rf '+projFolder+'/*')
            print "Folder cleaned."
        cftp=client.open_sftp()
        cftp.put(InputFile, projFolder+"/project.json")
        cftp.close()

        #3 Run jsontobin on json
        print 'Running preprocessor:'
        print 'python '+conn.workspace+'/hybriddomain/jsontobin.py '+projFolder+'/project.json'
        stdin, stdout, stderr = client.exec_command('python '+conn.workspace+'/hybriddomain/jsontobin.py '+projFolder+'/project.json')
        print stdout.read()

        #4 Run Solver binary on created files
        print "Checking if solver executable at "+conn.solverExecutable+" exists..."
        stdin, stdout, stderr = client.exec_command('test -f '+conn.solverExecutable)
        if stdout.channel.recv_exit_status():
            print "Please provide correct path to the solver executable."
            return
        else:
            print "Solver executable found."

        stdin, stdout, stderr = client.exec_command('sh '+projFolder+'/project.sh')
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



    '''projectName = "brusselator_1block"
    InputFile = projectName+".json"
    OutputDataFile = projectName+".dom"
    OutputFuncFile = projectName+".cpp"
    model = Model()
    model.loadFromFile(InputFile)
    print "Max derivative order is ", model.getMaxDerivOrder()
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)

    bm = BinaryModel(partModel)
    bm.saveDomain(OutputDataFile)
    bm.saveFuncs(OutputFuncFile)
    bm.compileFuncs(OutputFuncFile)
    #model.saveBinaryData(OutputDataFile, OutputFuncFile)
'''


if __name__=='__main__':
    #1 Get file name from command line
    if len(sys.argv)==1:
        print "Please specify a json file to read"
    else:
        InputFile = sys.argv[1]
        remoteProjectRun(InputFile)
##    remoteProjectRun("tests/test3_heat_wbounds2.json")

