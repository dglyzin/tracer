# -*- coding: utf-8 -*-
'''
Модуль импортирует входной json
Покдлючается к удаленной машине
Копирует туда этот же json и напускает на него jsontobin
Запускает решатель

model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''

import sys
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
    '''while True:
            line = stdout.readline()
            if flagClose==True:
                break
            else:
                if line != '':
                    if line[0:8] == 'file_out':
##                        outCommand = os.popen('if exist "'+curDir+'/File/'+line[:-1]+'"'' (echo file exist)').read()
##                        if outCommand[:-1]=='file exist':
                            if os.path.exists(curDir+'/File/'+line[:-1]):
##                                print 'Yes'
                                continue
                            cftp.get('ndtracer/'+line[:-1],curDir+'/File/'+line[:-1])
##                            makeGraph
                else:
                    break
        
        
        '''
    client.close()
    
    
    
    
    #4 Run Solver binary on created files
    

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
    