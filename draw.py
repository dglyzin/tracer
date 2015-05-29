import struct
import numpy as np
import matplotlib.pyplot as plt
import sys

dom = open(unicode(sys.argv[1]), 'rb')
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
  
print info

dom.close()


#bin = open(unicode(sys.argv[2]), 'rb')
#m253, = struct.unpack('b', bin.read(1))
#versionMajor, = struct.unpack('b', bin.read(1))
#versionMinor, = struct.unpack('b', bin.read(1))
#time, = struct.unpack('d', bin.read(8))

z = sys.argv[3]

minZ = 0
maxZ = 0

minY = 0
maxY = 0

minX = 0
maxX = 0

for i in range( len(info) ) :
  if info[i][0] < minZ :
    minZ = info[i][0]
    
  if info[i][0] + info[i][3] > maxZ :
    maxZ = info[i][0] + info[i][3]
    
  if info[i][1] < minY :
    minY = info[i][1]
    
  if info[i][1] + info[i][4] > maxY :
    maxY = info[i][1] + info[i][4]
    
  if info[i][2] < minX :
    minX = info[i][2]
    
  if info[i][2] + info[i][5] > maxX :
    maxX = info[i][2] + info[i][5]
    
print minZ
print maxZ

print minY
print maxY

print minX
print maxX

#for i in range( len(info) ) :
#  total = info[i][3] * info[i][4] * info[i][5] * cellSize
#  
#  data = np.fromfile(bin, dtype=np.float64, count=total)
#  data = data.reshape([info[i][5], info[i][4], info[i][3], cellSize]);
#  
#  print data[int(z),:,:,0]
#
#  xs = np.arange(0,blockInfo[3])*dx
#  ys = np.arange(0,blockInfo[4])*dy
#  
#  X,Y = np.meshgrid(xs,ys)
#  layer = data[int(z),:,:,0]
#  print X.shape, Y.shape, layer.shape
#  plt.pcolormesh(X, Y, layer)
#  plt.show()
