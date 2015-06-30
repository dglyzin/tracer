# -*- coding: utf-8 -*-
'''
один входной аргумент - json файл, для которого уже выполнены расчеты
рядом с этим файлом будет создана папка с такимо же именем, в которую будут закачаны все 
вычисления, после чего будет для каждого файла нарисована картинка, а затем все 
склеено в видеофайл.
'''
import struct
import numpy as np
#import matplotlib.pyplot as plt
import sys
import subprocess

from domainmodel.model import Model
import getpass
import paramiko, socket
from os import listdir
  
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm
#from matplotlib import colorbar
  
def savePng(filename, X, Y, layer, minTemp, maxTemp):
    figure = Figure()
    canvas = FigureCanvas(figure)
    axes = figure.add_subplot(111)
    figure.subplots_adjust(right=0.8)
    cbaxes = figure.add_axes([0.85, 0.15, 0.05, 0.7])

    cmap=cm.jet
    minTemp = layer.min()
    maxTemp = layer.max()

    cb = axes.pcolormesh(X, Y, layer, vmin=minTemp, vmax=maxTemp, cmap=cmap)
    axes.axis([X.min(), X.max(), Y.min(), Y.max()])
    axes.set_aspect('equal')

    figure.colorbar(cb, cax=cbaxes)
    ###    
    canvas.draw()
    figure.savefig(filename, format='png')            
    figure.clear()
  
def generatePng(projectDir):    
    #reading dom file
    dom = open(projectDir+"/project.dom", 'rb')    
    m254, = struct.unpack('b', dom.read(1))
    versionMajor, = struct.unpack('b', dom.read(1))
    versionMinor, = struct.unpack('b', dom.read(1))
    
    startTime, = struct.unpack('d', dom.read(8))
    finishTime, = struct.unpack('d', dom.read(8))
    timeStep, = struct.unpack('d', dom.read(8))
    
    saveInterval, = struct.unpack('d', dom.read(8))
    
    dx, = struct.unpack('d', dom.read(8))
    dy, = struct.unpack('d', dom.read(8))
    dz, = struct.unpack('d', dom.read(8))
    
    cellSize, = struct.unpack('i', dom.read(4))
    haloSize, = struct.unpack('i', dom.read(4))
    
    solverNumber, = struct.unpack('i', dom.read(4))
    
    aTol, = struct.unpack('d', dom.read(8))
    rTol, = struct.unpack('d', dom.read(8))
    
    blockCount, = struct.unpack('i', dom.read(4))
    
    info = []
    for index in range(blockCount) :
        dimension, = struct.unpack('i', dom.read(4))
        node, = struct.unpack('i', dom.read(4))
        deviceType, = struct.unpack('i', dom.read(4))
        deviveNumber, = struct.unpack('i', dom.read(4))
        
        blockInfo = []
        blockInfo.append(0)
        blockInfo.append(0)
        blockInfo.append(0)
        blockInfo.append(1)
        blockInfo.append(1)
        blockInfo.append(1)
        
        for x in range(dimension) :
            coord, = struct.unpack('i', dom.read(4))
            blockInfo[x] = coord
        
        for x in range(dimension) :
            count, = struct.unpack('i', dom.read(4))
            blockInfo[x + 3] = count
        
        info.append(blockInfo)
        
        total = blockInfo[3] * blockInfo[4] * blockInfo[5]
        dom.read(2 * 2 * total)
    dom.close()
    #dom file read
    
    #get sorted binary file list
    unsortedBinFileList =  [ f for f in listdir(projectDir) if f.endswith(".bin") ]
    binTime = np.array([float(f.split('.bin')[0].split('project-')[1])  for f in unsortedBinFileList])    
    print np.argsort(binTime)
    binFileList = [ unsortedBinFileList[idx] for idx in np.argsort(binTime)]
    print binFileList
    
    #
    minZ = 0
    maxZ = 0
    
    minY = 0
    maxY = 0
    
    minX = 0
    maxX = 0
    
    for i in range( len(info) ) :
        if info[i][2] < minZ :
            minZ = info[i][2]
    
        if info[i][2] + info[i][5] > maxZ :
            maxZ = info[i][2] + info[i][5]
    
        if info[i][1] < minY :
            minY = info[i][1]
    
        if info[i][1] + info[i][4] > maxY :
            maxY = info[i][1] + info[i][4]
    
        if info[i][0] < minX :
            minX = info[i][2]
    
        if info[i][0] + info[i][3] > maxX :
            maxX = info[i][0] + info[i][3]
    
    
    countZ = maxZ - minZ
    countY = maxY - minY
    countX = maxX - minX
    
    
    offsetZ = -minZ
    offsetY = -minY
    offsetX = -minX
    
    
    data = np.zeros((countZ, countY, countX, cellSize), dtype=np.float64)
    
    maxValue = sys.float_info.min
    minValue = sys.float_info.max
    
    for idx, binFile in enumerate(binFileList):
        bin = open(projectDir+"/"+binFile, 'rb')
        m253, = struct.unpack('b', bin.read(1))
        versionMajor, = struct.unpack('b', bin.read(1))
        versionMinor, = struct.unpack('b', bin.read(1))
        time, = struct.unpack('d', bin.read(8))
    
        for j in range( len(info) ) :
            countZBlock = info[j][5]
            countYBlock = info[j][4]
            countXBlock = info[j][3]
        
            coordZBlock = info[j][2] - offsetZ
            coordYBlock = info[j][1] - offsetY
            coordXBlock = info[j][0] - offsetX
        
            total = countZBlock * countYBlock * countXBlock * cellSize
        
            blockData = np.fromfile(bin, dtype=np.float64, count=total)
            blockData = blockData.reshape(countZBlock, countYBlock, countXBlock, cellSize);
            data[coordZBlock : coordZBlock + countZBlock, coordYBlock : coordYBlock + countYBlock, coordXBlock : coordXBlock + countXBlock, :] = blockData[:, :, :, :]
        bin.close()
        
        tmpMaxValue = np.max(data)
        tmpMinValue = np.min(data)
        
        if tmpMaxValue > maxValue:
            maxValue = tmpMaxValue
            
        if tmpMinValue < minValue:
            minValue = tmpMinValue



 
    
    for idx, binFile in enumerate(binFileList):
        bin = open(projectDir+"/"+binFile, 'rb')
        m253, = struct.unpack('b', bin.read(1))
        versionMajor, = struct.unpack('b', bin.read(1))
        versionMinor, = struct.unpack('b', bin.read(1))
        time, = struct.unpack('d', bin.read(8))
    
        for j in range( len(info) ) :
            countZBlock = info[j][5]
            countYBlock = info[j][4]
            countXBlock = info[j][3]
        
            coordZBlock = info[j][2] - offsetZ
            coordYBlock = info[j][1] - offsetY
            coordXBlock = info[j][0] - offsetX
        
            total = countZBlock * countYBlock * countXBlock * cellSize
        
            blockData = np.fromfile(bin, dtype=np.float64, count=total)
            blockData = blockData.reshape(countZBlock, countYBlock, countXBlock, cellSize);
            data[coordZBlock : coordZBlock + countZBlock, coordYBlock : coordYBlock + countYBlock, coordXBlock : coordXBlock + countXBlock, :] = blockData[:, :, :, :]
        bin.close()
        
        xs = np.arange(0, countX)*dx
        ys = np.arange(0, countY)*dy
    
    
        X,Y = np.meshgrid(xs,ys)
        layer = data[0,:,:,0]
        
        filename = projectDir+"/image-" + str(idx) + ".png"        
        savePng(filename, X, Y, layer, tmpMinValue, tmpMaxValue)
        
        
        print 'save #', idx, binFile, "->", filename
        
        

    
    
    

def getDataFromCluster(jsonFile, projectDir):
    model = Model()
    model.loadFromFile(jsonFile)
    conn = model.connection
    if conn.password == "":
        print "Please enter password for user "+ model.connection.username+":"
        passwd = getpass.getpass()
    else:
        passwd = conn.password

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())    
    try:
        client.connect(hostname=conn.host, username=conn.username, password=passwd, port=conn.port )

        print "Checking if folder "+conn.workspace+" exists..."
        _, stdout, stderr = client.exec_command('test -d '+conn.workspace)
        if stdout.channel.recv_exit_status():            
            return 1, "Please create workspace folder and put hybriddomain preprocessor into it"
        else:
            print "Workspace OK."

        remoteProjFolder = conn.workspace+"/"+model.projectName
        print "Checking if project folder exists: "
        _, stdout, stderr = client.exec_command('test -d  '+remoteProjFolder)
        if stdout.channel.recv_exit_status():            
            return 1, "Please run computations before getting results." 
        else:
            print "Project folder OK."
        cftp=client.open_sftp()
        cftp.get(remoteProjFolder+"/project.dom", projectDir+"/project.dom")
        binFileList = [ f for f in cftp.listdir(remoteProjFolder) if f.endswith(".bin") ]
        print "Copying", len(binFileList), "files from cluster"
        for binFile in binFileList:
            cftp.get(remoteProjFolder+"/"+binFile, projectDir+"/"+binFile)
        print "Done"     
        cftp.close()        
        client.close()
        
    #Обрабатываю исключения
    except paramiko.ssh_exception.AuthenticationException:
        return 1, u'Неверный логин или пароль'
    except socket.error:
        return 1, u'Указан неправильный адрес или порт'
    except paramiko.ssh_exception.SSHException:
        return 1, u'Ошибка в протоколе SSH'    
    return 0, "Success!"

def createDir(projectDir):
    PIPE = subprocess.PIPE
    subprocess.Popen("mkdir "+projectDir, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)

def createVideoFile(projectDir):
    print "Creating video file:"
    command = "avconv -r 5 -i "+projectDir+"/image-%d.png -b:v 1000k "+projectDir+"/project.mp4"
    print command
    PIPE = subprocess.PIPE
    subprocess.Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)
    print "Done" 



def createMovie(jsonFile):
    projectDir = jsonFile.split('.json')[0]
    #createDir(projectDir)
    #errCode, message = getDataFromCluster(jsonFile, projectDir)
    #if errCode!=0:
    #    print message
    #    return errCode
    generatePng(projectDir)
    #createVideoFile(projectDir)

if __name__ == "__main__":
    if len(sys.argv)==1:
        print "Please specify a json file to read"
    else:
        jsonFile = sys.argv[1]
        createMovie(jsonFile)
        