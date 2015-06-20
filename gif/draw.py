import struct
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.backends.backend_pdf import PdfPages

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
  
  filename = '' + sys.argv[i].split(".")[0] + '.' + sys.argv[i].split(".")[1] + '.png'
  pp = filename
  plt.savefig(pp, format='png')
  
  print 'save #', i-1, filename
  #pp.close()
