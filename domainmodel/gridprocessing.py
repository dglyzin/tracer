import numpy as np
from settings import *

def appendGoodPoints(item, ax, points):
    if item["Location"] != "default" :
        for rect in item["Rectangles"]:
            if (rect[ax+"from"] != "start")and(rect[ax+"from"] != "end"):
                points.append(float(rect[ax+"from"]))
            if (rect[ax+"to"] != "end")and(rect[ax+"to"] != "start"):
                points.append(float(rect[ax+"to"]))

def getAXpoints(model):
    '''
    collects points from soil change, bound change and heat change
    '''
    #1. block bounds
    pointsX = [block.offsetx for block in model.blocks] + [block.offsetx+block.x for block in model.blocks]
    pointsY = [block.offsety for block in model.blocks] + [block.offsety+block.y for block in model.blocks]
    pointsZ = [block.offsetz for block in model.blocks] + [block.offsetz+block.z for block in model.blocks]
    #2. soil and bound changes        
    for block in model.blocks:
        regions = block.soilRegions + block.cavernRegions + block.boundRegions + block.heatSourceRegions
        pointsX = pointsX + [block.offsetx + location.x1 for location in regions ]
        pointsX = pointsX + [block.offsetx + location.x2 for location in regions ]
      
        pointsY = pointsY + [block.offsety + location.y1 for location in regions ]
        pointsY = pointsY + [block.offsety + location.y2 for location in regions ]
      
        pointsZ = pointsZ + [block.offsetz + location.z1 for location in regions ]
        pointsZ = pointsZ + [block.offsetz + location.z2 for location in regions ]
  
    return [sorted(list(set(pointsX))), sorted(list(set(pointsY))), sorted(list(set(pointsZ)))]
  
    
def getVolumesFromNodes(points):
    result = np.zeros(len(points)-1, dtype=np.float32)
    for idx in range(len(points)-1):
        result[idx]=points[idx+1]-points[idx]
    return result


#######Graining#############
def maxgraining(points, maxw):
    #1. make every width less than maxw
    res1 = [points[0]]
    for idx in range(len(points)-1):
        width = points[idx+1]-points[idx]
        if width>maxw:
            frac = int(round(width/maxw))
            if width-frac*maxw<0.0001:
                num = int(frac)
            else:
                num = int(frac) + 1
            length = width/num
            for idx2 in range(num-1):
                res1.append(points[idx]+(idx2+1)*length)
        
        res1.append(points[idx+1])    
    return res1
 
def leftpartition(p1,p2,p3):
    res = []
    dx1 = p2-p1 #to be partitioned
    dx2 = p3-p2
   
    while dx1>4*dx2:
        dx2 = dx2*2
        dx1 = dx1-dx2
        res.insert(0,p1+dx1)
    if dx1 > 2* dx2:
        res.insert(0,p1+dx1/2)
    res.insert(0,p1)  
    return res

def centerpartition(p1,p2,p3,p4):
    dxleft = p2-p1
    dxright = p4-p3
    dx = p3-p2 #to be partitioned
    pleft = p2
    pright = p3
    res1 =[pleft]
    res2 = []

    while dx > 4* min([dxleft,dxright]):
        if dxleft<dxright:
            dxleft = dxleft*2
            dx = dx - dxleft
            pleft = pleft+dxleft 
            res1.append(pleft)      
        else:
            dxright = dxright*2
            dx = dx - dxright
            pright = pright-dxright 
            res2.insert(0,pright)
    if dx> 2*min([dxleft,dxright]):    
        res1.append(pleft+dx/2)
      
    return  res1+res2
  
def rightpartition(p1,p2,p3):
    res = [p2]
    dx1 = p2-p1 
    dx2 = p3-p2 #to be partitioned
   
    while dx2>4*dx1:
        dx1 = dx1*2
        dx2 = dx2-dx1
        res.append(p2+dx1)
    if dx2 > 2* dx1:
        res.append(p3-dx2/2)
    res.append(p3)    
    return res
  
def progressiongraining(points, factor):
    #2. make partitioning more uniform
    #2.1 partition first block if needed
    length = len(points)
    if length >2:
        res2 = leftpartition(points[0], points[1], points[2])
    else:
        res2 = points
    #2.2 partition all center blocks
    if length>3:
        for idx in range(len(points)-3):
            res2=res2+centerpartition(points[idx], points[idx+1], points[idx+2], points[idx+3])
  
    #2.3 partition last block if needed
    if length>2:
        res2 = res2+rightpartition(points[length-3], points[length-2], points[length-1])

    return res2


#######################Locations##########################
def getrectcoord(location):
    x1 = location.x1
    x2 = location.x2
    y1 = location.y1
    y2 = location.y2
    z1 = location.z1
    z2 = location.z2
    return x1,x2,y1,y2,z1,z2

def getIntIndices(volumes, size, p1, p2):
    #print volumes, size, p1, p2
    ix1 = 0
    coord =0.0
    while coord+volumes[ix1]/2 < p1:
        coord = coord+volumes[ix1]
        ix1 = ix1+1
    ix2 = ix1
    while (ix2<size) and (coord+volumes[ix2]/2 < p2):
        coord = coord+volumes[ix2]
        ix2 = ix2+1
    return ix1, ix2


######################Interconnect processing##################
def getH1H2MN(interconnect, sizeArray1, sizeArray2, offsetArray1, offsetArray2):
    """
    returns adjacent h from sizearray1 and sizearray2
    returns m and n
    for x=c plane: m<->z, n<->y
    for y=c plane: m<->z, n<->x
    for z=c plane: m<->y, n<->x
    owner (1) [i][j] <-> source (2) [i+Mshift][j+Nshift]
    """    
    if (interconnect.block1Side == XSTART) and (interconnect.block2Side == XEND):
        h1 = sizeArray1[0][0]
        h2 = sizeArray2[0][-1]
        m = offsetArray1[2] - offsetArray2[2]
        n = offsetArray1[1] - offsetArray2[1]
    elif (interconnect.block1Side == XEND) and (interconnect.block2Side == XSTART):
        h1 = sizeArray1[0][-1]
        h2 = sizeArray2[0][0]
        m = offsetArray1[2] - offsetArray2[2]
        n = offsetArray1[1] - offsetArray2[1]
    elif (interconnect.block1Side == YSTART) and (interconnect.block2Side == YEND):
        h1 = sizeArray1[1][0]
        h2 = sizeArray2[1][-1]
        m = offsetArray1[2] - offsetArray2[2]
        n = offsetArray1[0] - offsetArray2[0]
    elif (interconnect.block1Side == YEND) and (interconnect.block2Side == YSTART):
        h1 = sizeArray1[1][-1]
        h2 = sizeArray2[1][0]
        m = offsetArray1[2] - offsetArray2[2]
        n = offsetArray1[0] - offsetArray2[0]
    elif (interconnect.block1Side == ZSTART) and (interconnect.block2Side == ZEND):
        h1 = sizeArray1[2][0]
        h2 = sizeArray2[2][-1]
        m = offsetArray1[1] - offsetArray2[1]
        n = offsetArray1[0] - offsetArray2[0]
    elif (interconnect.block1Side == ZEND) and (interconnect.block2Side == ZSTART):
        h1 = sizeArray1[2][-1]
        h2 = sizeArray2[2][0]
        m = offsetArray1[1] - offsetArray2[1]
        n = offsetArray1[0] - offsetArray2[0]
         
    else:
      print "Interconnect processing failed!!"
      return 0.0, 0.0, 0, 0
  
    return h1, h2, m, n
