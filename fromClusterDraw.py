import struct
import numpy as np
import matplotlib.pyplot as plt
import sys

def runDrow(fileDom,fileBin,inZ):
    dom = open(fileDom, 'rb')
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

    print blockCount

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

    print info

    dom.close()

    z = inZ

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

    #print minZ
    #print maxZ
    #
    #print minY
    #print maxY
    #
    #print minX
    #print maxX

    countZ = maxZ - minZ
    countY = maxY - minY
    countX = maxX - minX

    print countZ
    print countY
    print countX

    offsetZ = -minZ
    offsetY = -minY
    offsetX = -minX

    print offsetZ
    print offsetY
    print offsetX

    data = np.zeros((countZ, countY, countX, cellSize), dtype=np.float64)
    #print data

    #resultTemperature[offsetZ:offsetZ+zc, offsetY:offsetY+yc, offsetX:offsetX+xc] = temperature[:, :, :]

    bin = open(unicode(fileBin), 'rb')
    m253, = struct.unpack('b', bin.read(1))
    versionMajor, = struct.unpack('b', bin.read(1))
    versionMinor, = struct.unpack('b', bin.read(1))
    time, = struct.unpack('d', bin.read(8))

    for i in range( len(info) ) :
      countZBlock = info[i][5]
      countYBlock = info[i][4]
      countXBlock = info[i][3]

      coordZBlock = info[i][2] - offsetZ
      coordYBlock = info[i][1] - offsetY
      coordXBlock = info[i][0] - offsetX

      total = countZBlock * countYBlock * countXBlock * cellSize

      blockData = np.fromfile(bin, dtype=np.float64, count=total)
      blockData = blockData.reshape(countZBlock, countYBlock, countXBlock, cellSize);
      print coordXBlock , coordXBlock + countXBlock
      print data.shape
      print blockData.shape
      data[coordZBlock : coordZBlock + countZBlock, coordYBlock : coordYBlock + countYBlock, coordXBlock : coordXBlock + countXBlock, :] = blockData[:, :, :, :]

    xs = np.arange(0, countX)*dx
    ys = np.arange(0, countY)*dy

    X,Y = np.meshgrid(xs,ys)
    layer = data[int(z),:,:,0]
    print X.shape, Y.shape, layer.shape
    print layer
    plt.pcolormesh(X, Y, layer)
    plt.show()
