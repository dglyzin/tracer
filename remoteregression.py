# -*- coding: utf-8 -*-
'''
запуск тестов регрессии на удаленном кластере

Аргументы:
connection
  json-файл с параметрами подключения

параметры:
-folder 
запуск тестов из подпапки, по умолчанию выполняются все тесты из regression/

-nodecount=4
будут запущены только те тесты, для которых требуется меньше или равно nodecount узлов

-norun 
запуск только сравнений, на случай если все уже посчитано

подключаемся, запускаем regression.py с заданными параметрами
копируем назад лог тестирования
'''

import json
import os
import socket
import getpass
import paramiko
import argparse
from collections import OrderedDict
from remoterun import Connection
        
def remoteRegressionRun(connection, args):
    '''
      connection: dictionary with connection settings
      args.nodecount:  skip tests that require more nodes
      args.folder : relative to connection.tracerfolder/hybriddomain/
      args.norun: do not run computations
      args.debug: use debug partition (does not work now as everything goes to debug)
    '''
    
    #prepare command line argumetnts for preprocessor
    optionalArgs=" -nodecount " + str(args.nodecount) + " -folder " + args.folder    
    
    if args.norun:
        optionalArgs+=" -norun"
    if args.debug:
        optionalArgs+=" -debug"    
    
    #get project file name without extension
    domainFolder = connection.tracerFolder+"/hybriddomain"
    regscript = connection.tracerFolder+"/hybriddomain/regression.py"
    regfolder = connection.tracerFolder+"/hybriddomain/"+args.folder
    remoteRegLog = regfolder+"/regression.log" 
    
    print "Running regression script {} on the remote machine with parameters {}".format(regscript, optionalArgs)
    
    localRegLog = "remoteregression.log"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #print conn.host, conn.username, passwd, conn.port
    try:
        client.connect(hostname=connection.host, username=connection.username, password=connection.password, port=connection.port )

        print "Checking if folder "+regfolder+" exists..."
        stdin, stdout, stderr = client.exec_command('test -d '+regfolder)
        if stdout.channel.recv_exit_status():
            print "Please specify existing folder with tests"
            return
        else:
            print "Regfolder OK."

        print "Checking if solver executable at "+connection.tracerFolder+"/hybridsolver/bin/HS exists..."
        stdin, stdout, stderr = client.exec_command('test -f '+connection.tracerFolder + "/hybridsolver/bin/HS")
        if stdout.channel.recv_exit_status():
            print "Please provide correct path to the solver executable."
            return
        else:
            print "Solver executable found."
        
        #3 Run jsontobin on json
        print '\nRunning regression script:'
        command = "cd "+domainFolder+'; python ' + regscript 
        
        print "executing ", command, optionalArgs
        stdin, stdout, stderr = client.exec_command(command+optionalArgs)
        print stdout.read()
        print "regtest stderr:"
        print stderr.read()
        print "stderr END"
        
        #get resulting files
        cftp=client.open_sftp()        
        cftp.get(remoteRegLog, localRegLog)
        cftp.close()
        
        client.close()

    #Обрабатываю исключения
    except paramiko.ssh_exception.AuthenticationException:
        return u'Неверный логин или пароль'
    except socket.error:
        return u'Указан неправильный адрес или порт'
    except paramiko.ssh_exception.SSHException:
        return u'Ошибка в протоколе SSH'


def getGonnection(connFileName):
    connFile = open(connFileName,"r")    
    connDict = json.loads(connFile.read())
    connFile.close()
    
    connection = Connection()
    connection.fromDict(connDict)        
    #get password
    if connection.password == "":
        connection.password = os.getenv("CLUSTER_PASS")
        if connection.password is None:
            print "Please enter password for user "+ connection.username+":"
            connection.password = getpass.getpass()
    return connection


       
if __name__=='__main__':    
    parser = argparse.ArgumentParser(description='Processing json file on a remote cluster.', epilog = "Have fun!")
    parser.add_argument('connFileName', type = str, help = "local json file with connection info")    
    parser.add_argument('-nodecount', type = int, default=4, help = "Number of available nodes to run tests on.")    
    parser.add_argument('-folder', type = str, default="regression", help = "Folder to search tests in (including subfolders).")    
    parser.add_argument('-norun', help="Do not make runs, only compare existing data.", action="store_true")
    parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")    
    args = parser.parse_args()
    
    connFileName = args.connFileName    
    connection = getGonnection(connFileName)
    remoteRegressionRun(connection, args)


