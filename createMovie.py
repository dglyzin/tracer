import struct
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.backends.backend_pdf import PdfPages
import subprocess

from domainmodel.model import Model
import getpass
import paramiko, socket

def ololo():
    argc = len(sys.argv) - 1
    
    dom = open(unicode(sys.argv[1]), 'rb')
    ##dom = open('projectOut.dom', 'rb')
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
    
    z = sys.argv[argc]
    
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
    
    
    for i in range(2, argc):
        bin = open(unicode(sys.argv[i]), 'rb')
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
        
        xs = np.arange(0, countX)*dx
        ys = np.arange(0, countY)*dy
    
    
        X,Y = np.meshgrid(xs,ys)
        layer = data[int(z),:,:,0]
    
        plt.pcolormesh(X, Y, layer)
      
        filename = 'image-' + str(i-1) + '.png'
        pp = filename
        plt.savefig(pp, format='png')
      
        print 'save #', i-1, filename
        #pp.close()


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
        cftp.get(remoteProjFolder+"", projectDir)
        cftp.close()
        '''
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
        '''
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


def createMovie(jsonFile):
    projectDir = jsonFile.split('.json')[0]
    createDir(projectDir)
    errCode, message =  getDataFromCluster(jsonFile, projectDir)
    if errCode!=0:
        print message
        return errCode
    

if __name__ == "__main__":
    if len(sys.argv)==1:
        print "Please specify a json file to read"
    else:         
        jsonFile = sys.argv[1]
        createMovie(jsonFile)
        