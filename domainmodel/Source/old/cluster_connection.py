# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import matplotlib.pyplot as plt
import socket
import numpy as np
import json
from PyQt4 import QtGui, QtCore
import paramiko
from multiprocessing import Process
import threading
import struct
import time

#TODO:
#wait for server  to start before connecting socket to port
#Large arrays do not work with paramiko channel
#replace gather with gatherv
#bring back adaptive step
#reconnecting?
#GUI

curDir = os.path.abspath(os.curdir)
flagClose = False

def recvLargeArray(sock, length):
    if length>1024:
        buf =  sock.recv(1024)
        #print "want 1024, got ", len(buf)
        result = np.fromstring(buf, dtype = np.float64)
        length = length- 1024

        while (length>1024):
            buf =  sock.recv(1024)
            #print "want 1024, got ",len(buf)
            result = np.concatenate((result,np.fromstring(buf, dtype = np.float64)) )
            length = length - 1024

        buf= sock.recv(length);
        #print "want ", length, ", got ", len(buf)
        result = np.concatenate((result,np.fromstring(buf, dtype = np.float64)) )
    else:
        buf =  sock.recv(length)
        #print len(buf)
        result = np.fromstring(buf, dtype = np.float64)
    return result

def serverRunProcess(work_port, procnum, login,password,ip,port,command):
    #c_relpath = '../../../c-core/src/'
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=str(ip), username=str(login), password=str(password), port=int(port))
        outText='Complite'
        print "sending..."
        if command=='InterfaceMode':
            stdin, stdout, stderr = client.exec_command('rm -r ndtracer; mkdir ndtracer')
            time.sleep(0.3)
            cftp=client.open_sftp()
            cftp.put('..\\..\\..\\..\\c-core\\src\\core\\server.c', 'ndtracer/server.c')
            cftp.put('..\\..\\..\\..\\c-core\\src\\core\\odemeth_mpi.c', 'ndtracer/odemeth_mpi.c')
            cftp.put('..\\..\\..\\..\\c-core\\src\\core\\odemeth_mpi.h', 'ndtracer/odemeth_mpi.h')
            cftp.put('..\\..\\..\\..\\c-core\\src\\core\\coreintegr.c', 'ndtracer/coreintegr.c')
            cftp.put('..\\..\\..\\..\\c-core\\src\\core\\coreintegr.h', 'ndtracer/coreintegr.h')
            cftp.put('..\\..\\..\\..\\c-core\\src\\userfunc_ode_mpi.c', 'ndtracer/userfunc_ode_mpi.c')
            cftp.put('..\\..\\..\\..\\c-core\\src\\userfunc_ode_mpi.h', 'ndtracer/userfunc_ode_mpi.h')

            cftp.close()
            #time.sleep(2)
            print "compiling..."
            stdin, stdout, stderr = client.exec_command('cd ndtracer; mpicc server.c coreintegr.c odemeth_mpi.c userfunc_ode_mpi.c -o server')
            print stdout.read(), stderr.read()

            print "running..."
            #stdin, stdout, stderr = client.exec_command('cd ndtracer; salloc -n 32 -F machinefile mpirun ./server '+str(SOCK_PORT))
            #print type(procnum), type(work_port)
            comstr = 'cd ndtracer; salloc -n '+ str(procnum) +' mpirun ./server '+str(work_port)
            stdin, stdout, stderr = client.exec_command(comstr)
            #stdin, stdout, stderr = client.exec_command('cd ndtracer; salloc -n '+ procnum +' mpirun ./server '+work_port)
            #stdin, stdout, stderr = client.exec_command('cd ndtracer')
            print stdout.read(), stderr.read()

        #Компилируем для консольного режима
        else:
            stdin, stdout, stderr = client.exec_command('rm -r ndtracer; mkdir ndtracer')
            time.sleep(0.3)
            cftp=client.open_sftp()
##            if os.path.exists('./File/'+command):
##                cftp.put('./File/'+command, 'ndtracer/'+command)
##            else:
##                outText='Файл отсутствует'
            if os.path.exists(command):
                cftp.put(command, 'ndtracer/'+command)
                cftp.put('libuserfuncs.so', 'ndtracer/'+'libuserfuncs.so')
                stdin, stdout, stderr = client.exec_command('cd ndtracer; mkdir doc' )
                cftp.put('.\\doc\\userfuncs.h', 'ndtracer/doc/userfuncs.h')
            else:
                outText='Файл отсутствует'

            cftp.close()
            print "compiling..."+command[:-2]
            stdin, stdout, stderr = client.exec_command('cd ndtracer; pwd')
            outPathCompile = stdout.read()
##            stdin, stdout, stderr = client.exec_command('cd ndtracer; g++ '+command+' -std=c99 -lm -o '+command[:-2])
            outCommand = "gcc "+ command + " -shared  -O3 -o libuserfuncs.so -fPIC"
            stdin, stdout, stderr = client.exec_command('cd ndtracer; '+outCommand)
            outText=str(stdout.read()+stderr.read())
            if outText=='':
                outText=u'Файл скомпилирован в каталоге: '+outPathCompile
            print outText

        client.close()
        return outText
    #Обрабатываю исключения
    except paramiko.ssh_exception.AuthenticationException:
        return u'Неверный логин\пароль'
    except paramiko.ssh_exception.SSHException:
        return u'Ошибка в протоколе SSH'

def talkToServer(sock,cont,lexpnumber):
    print "recving array..."
    #p = sock.recv_into(rcvArr, 10*8, socket.MSG_WAITALL)
    #rcvArr = recvLargeArray( sock, 8*dimension*(1+lexpnumber))
    print "time = ", struct.unpack('d',sock.recv(8))[0]
    print "stepsize = ", struct.unpack('d',sock.recv(8))[0]
    rcvArr = recvLargeArray( sock, 8*(1+lexpnumber))
    sock.send(cont) #do not stop
    print rcvArr

def makeGraph():
##    os.popen('cd '+os.getcwd()[0:1]+':/File/')
##    files = os.listdir(os.getcwd()[0:1]+':/File/');
    os.popen('cd '+curDir+'/File/')
    files = os.listdir(curDir+'/File/');
    lastFile=0
    ylist1=list("")
    if(len(files)!=0):
        print str(len(files))+" files in directory"
        for file in files:
            ylist1=list("")
            last=file[8:-4]
            if(lastFile<int(last)):
                lastFile=int(last)
        print lastFile
        textLastFile=curDir+'\\File\\'+'file_out'+str(lastFile)+'.txt'
        f = open(textLastFile.replace('\\','/'))
        text = f.read()
        ylist=text.split(' ')
        for kk in ylist:
            if len(kk)>1:
                ylist1.append(float(kk))
        return ylist1
    else:
        print "No files in directory"
        return ylist1

def arrayNode(strIn):
    freeNode=list("")
    index=-1
    for line in strIn:
        print "test:", line
        index=line.find("idle")
        if index!=-1:
            line=line[index:]
            indexLeft=line.find("[")
            indexRight=line.find("]")
            if indexLeft!=-1 and indexRight!=-1:
                line=line[indexLeft+1:indexRight]
                nodeArray=line.split(',')
                if len(nodeArray)>0:
                    for elem in nodeArray:
                        if elem.isdigit():
                            freeNode.append(int(elem))
                        else:
                            array = elem.split("-")
                            if len(array)>0:
                                if array[0].isdigit() and array[1].isdigit():
                                    for x in range(int(array[0]),int(array[1])+1):
                                        freeNode.append(int(x))
    return freeNode

def closeConnect(ip, login, password, port):
    global flagClose
    flagClose=True

def GettingFile(ip, port, login, password, mainnode, work_port, dimension, lexpnumber, steps, iters):
    if flagClose==True:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=str(ip), username=str(login), password=str(password), port=int(port))
        stdin, stdout, stderr = client.exec_command('scancel -u tester')
        print stdout.read(), stderr.read()
        print 'Connection close'
        client.close()
    else:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=str(ip), username=str(login), password=str(password), port=int(port))
        cftp=client.open_sftp()
        stdin, stdout, stderr = client.exec_command('cd ndtracer; ls')
        while True:
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
        cftp.close()
        #Add last update
        client.close()

def communicator(ip, port, login, password, mainnode, work_port, dimension, lexpnumber, steps, iters):
    #wait somehow till server starts
    print "waiting for server..."
    #time.sleep(10)

    transport = paramiko.Transport((str(ip), int(port)))
    transport.connect(hostkey  = None, username = str(login), password = str(password), pkey     = None)
    connected = False
    timeout = 25
    while (not connected) and (timeout>0):
        try:
            #print "type type tpye", type(mainnode)
            sock = transport.open_channel('direct-tcpip', (str(mainnode), int(work_port)), ("127.0.0.1", 40606))
            connected = True
            print "connected"
        except:
            timeout = timeout-1;
            print "connecting..."
            if flagClose==True:
                GettingFile(ip, port, login, password, mainnode, work_port, dimension, lexpnumber, steps, iters)
            time.sleep(1)
    #sock = transport.open_channel('direct-tcpip', ("10.7.129.44", SOCK_PORT), ("127.0.0.1", 40606))
    if not connected:
        return
    sock.setblocking(1)
    #sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    #sock.connect(("127.0.0.1", SOCK_PORT))

    sock.send("Hello from client!\n")
    #send dimension and number of exponents to compute
    buf = struct.pack('i',dimension)
    sock.send(buf)
    buf = struct.pack('i',lexpnumber)
    sock.send(buf)

    buf = struct.pack('i',steps)
    sock.send(buf)
    #send array of params
    params = np.empty((10), dtype =  np.float64)
    params[0] = 21
    sock.send(params.tostring())

    for i in range(iters):
        if flagClose<>True:
            talkToServer(sock,"0",lexpnumber)
            GettingFile(ip, port, login, password, mainnode, work_port, dimension, lexpnumber, steps, iters)
    if flagClose<>True:
        talkToServer(sock,"1",lexpnumber)

    sock.close()
    transport.close()

def DeleteDir(dir):
    if len(os.listdir(dir))>=1:
        for name in os.listdir(dir):
            file = os.path.join(dir, name)
            if not os.path.islink(file) and os.path.isdir(file):
                DeleteDir(file)
            else:
                os.remove(file)
        os.rmdir(dir)

def OnClickConnect(dim_str, lexp_str, steps_str, iters_str, work_port, mainnode, procnum, login,password,ip,port,command):
    dimension = int(dim_str)
    lexpnumber = int(lexp_str)
    steps = int(steps_str)
    iters = int(iters_str)
    global flagClose
    flagClose = False
    print "starting server..."
    #1. Connect, copy, compile and run
    #srvThread = Process(target=serverRunProcess, args=(work_port, procnum, login, password, ip, port))
##    srvThread = threading.Thread(target=serverRunProcess, args=(work_port, procnum, login, password, ip, port,command))
##    srvThread.start()
    out = serverRunProcess(work_port, procnum, login, password, ip, port,command)

    if command=='InterfaceMode':
        time.sleep(5)
        #commProcess = Process(target=communicator, args=(ip, port, login, password, mainnode, work_port, dimension, lexpnumber))
        ClearOutDirectory()
        commProcess = threading.Thread(target=communicator, args=(ip, port, login, password, mainnode, work_port, dimension, lexpnumber, steps, iters))
        commProcess.start()
        #print "Waiting for the server process to join.."
        #srvThread.join()
    return out

def ClearOutDirectory():
    textCurDir=curDir+'\File'
    for name in os.listdir('./'):
        if name=='File':
            DeleteDir('./File/')
    try:
        os.mkdir('.\\File')
    except OSError:
        print "test already exists"

if __name__ == '__main__':
    OnClickConnect("640", "10", "1000", "5", "15561", "cnode1", "16", "tester","tester","corp7.uniyar.ac.ru","2222",'InterfaceMode')
