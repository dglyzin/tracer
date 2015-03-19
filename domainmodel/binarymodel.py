# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

import numpy as np
from regions import BoundRegion
from gridprocessing import *
from datetime import date, datetime
from temp_modifiers import *
import time
from block import Block
from interconnect import Interconnect
import copy

BOUND_SHIFT = 1 #we shift every bound index to add zero conditions
HEATSOURCE_SHIFT = 1 #and every heatsource index too
zerodate = date(1970,1,1)

def translateLiquidWaterPercentage(jsonPercentage):
    """
    json stores percents, we need fraction
    """
    binaryPercentage = jsonPercentage/100.0
    return binaryPercentage


def translateConductivity(jsonConductivity):
    """
    json stores in (J/s)/m/K, we need (kJ/day)/m/K 
    """
    binaryConductivity = 86.4*jsonConductivity
    return binaryConductivity

def translateHeatFlow(jsonHeatFlow):
    """
    json stores in (kJ/s)/m^2, we need (kJ/day)/m^2 
    """
    binaryHeatFlow = 86400*jsonHeatFlow
    return binaryHeatFlow




def translateRecConductivity(jsonRecConductivity):
    """
    json stores in 1 / [(J/s)/m/K], we need 1 / [(kJ/day)/m/K]
    """
    binaryRecConductivity = jsonRecConductivity/86.4
    return binaryRecConductivity



def getOffset(arr):
    offset = 0
    while arr[offset]<0:
        offset = offset+1            
    return offset

class BinaryModel(object):
    def __init__(self, model):
        print "Welcome to the binary model saver!"
        self.model = model
        self.extendedBlocks = model.blocks     #these two arrays will be replaced in case of cutting the block        
        self.extendedIC = copy.copy(model.interconnects) #into pieces for concurrent processing on different devices
        #shallow copy, we can edit list but should not edit copied interconnects
        self.blockCount = len(self.extendedBlocks)
        self.dxMax = 10000.0
        self.dyMax = 10000.0
        self.dzMax = 10000.0


        
    def getBinarySettings(self):
        self.domName = self.model.commonSettings.title
        self.versionarr_bin = np.zeros(4, dtype=np.uint8)
        self.versionarr_bin[0] = 253
        self.versionarr_bin[1] = 2
        self.versionarr_bin[2] = 0
        self.versionarr_bin[3] = 1 #generated(1) or computed(0)
        
        self.versionarr_dom = np.zeros(3, dtype=np.uint8)
        self.versionarr_dom[0] = 254
        self.versionarr_dom[1] = 2
        self.versionarr_dom[2] = 0
        
        startTime  = datetime.strptime(self.model.commonSettings.startTime, '%d.%m.%Y').date()
        finishTime = datetime.strptime(self.model.commonSettings.finishTime, '%d.%m.%Y').date()
        startTimeInt  = (startTime - zerodate).days
        finishTimeInt = (finishTime - zerodate).days
          
        self.timearr = np.zeros(1, dtype=np.float64)
        self.timearr[0] = startTimeInt
        
        self.params = np.zeros(7, dtype=np.float32)        
        self.params[0] = float(finishTimeInt)
        self.params[1] = self.model.commonSettings.timeStep
        self.params[2] = self.model.commonSettings.savesPerMonth
        self.params[3] = self.model.commonSettings.iceSpecHeat
        self.params[4] = self.model.commonSettings.waterSpecHeat
        self.params[5] = self.model.commonSettings.waterLatentHeat
        self.params[6] = self.model.commonSettings.iceVolumetricExpansion
        


    ##############################   GRID    ###################################
    def generateGlobalGrid(self):
         '''
         we need a grid that contains all nodes from every block
         it should include every point of soil, bound or source change
         then it should be refine not ot exceed dxMax-dyMax-dzMax
         then for every block we'll include nodes that are inside that block into the binary description 
         '''
         
         
         for block in self.extendedBlocks:
              if self.dxMax>block.dx: self.dxMax=block.dx
              if self.dyMax>block.dy: self.dyMax=block.dy
              if self.dzMax>block.dz: self.dzMax=block.dz       
              print "loaded block", block.x, block.y, block.z, block.offsetx, block.offsety, block.offsetz
         baseGrid = getAXpoints(self.model)
         #print "base points:", baseGrid
                  
         #refine
         baseGrid[0] = maxgraining(baseGrid[0], self.dxMax)
         baseGrid[1] = maxgraining(baseGrid[1], self.dyMax)
         baseGrid[2] = maxgraining(baseGrid[2], self.dzMax)
         
         baseGrid[0] = progressiongraining(baseGrid[0], 2)
         baseGrid[1] = progressiongraining(baseGrid[1], 2)
         baseGrid[2] = progressiongraining(baseGrid[2], 2)
         
         
         refinedGrid = baseGrid
         #print "refined points:", refinedGrid
         
         #store global grid
         self.globalGridSize = np.zeros(3, dtype=np.int32)
         self.globalGrid = [] 
         for coord in [0,1,2]:
             self.globalGridSize[coord] = len(refinedGrid[coord])
             points = np.zeros(self.globalGridSize[coord],dtype=np.float32)
             self.globalGrid.append(points)
             for idx in range(self.globalGridSize[coord]):
                points[idx]=refinedGrid[coord][idx]
         
         
    def generateBlocksGrid(self):    
         #now for every block select only points inside it
         blockPoints = [] #every element will contain 3 arrays of points of respective block
         #and meanwhile save offsets
         self.offsetArrays = []
         for blockIdx in range(self.blockCount):
             block = self.extendedBlocks[blockIdx]
             
             blockX = [point - block.offsetx  for point in self.globalGrid[0]]
             intoffsetX = getOffset(blockX)             
             blockX = [point for point in blockX if (point>=0) and (point<=block.x ) ]              
             blockY = [point - block.offsety  for point in self.globalGrid[1]]
             intoffsetY = getOffset(blockY)
             blockY = [point for point in blockY if (point>=0) and (point<=block.y ) ] 
             blockZ = [point - block.offsetz  for point in self.globalGrid[2]]
             intoffsetZ = getOffset(blockZ)
             blockZ = [point for point in blockZ if (point>=0) and (point<=block.z ) ]
             blockPoints.append([blockX, blockY, blockZ])
             #print "block #", blockIdx, ":", blockPoints[blockIdx]
             offsetArray = np.zeros(3, dtype=np.int32)
             offsetArray[0] = intoffsetX
             offsetArray[1] = intoffsetY
             offsetArray[2] = intoffsetZ
             self.offsetArrays.append(offsetArray)
         
         self.sizeArrays = [] #every element will contain array of 3 numbers - grid size of respective block
         
         self.blockGridSteps = [] #every element will contain 3 arrays of volume sizes of respective block         
         self.mainArraySizes = [] #every element will contain count of volumes in every block
         for blockIdx in range(self.blockCount):
             points = blockPoints[blockIdx]
             xvolumes = getVolumesFromNodes(points[0])
             yvolumes = getVolumesFromNodes(points[1])
             zvolumes = getVolumesFromNodes(points[2])
             self.blockGridSteps.append([xvolumes, yvolumes, zvolumes])
             #print "block #", blockIdx
             #print "X volumes are:"+str( xvolumes )
             #print "Y volumes are:"+str( yvolumes )
             #print "Z volumes are:"+str( zvolumes )
             sizearray = np.zeros(3, dtype=np.int32)           
             sizearray[0] = xvolumes.size
             sizearray[1] = yvolumes.size
             sizearray[2] = zvolumes.size
             self.sizeArrays.append(sizearray)
           
             self.mainArraySizes.append(xvolumes.size*yvolumes.size*zvolumes.size)

    
    
    ##############################   SOILS    ###################################
    def getBinarySoils(self):        
        self.soilTypeCount = len(self.model.soils)
        self.soilCountArr = np.zeros(1, dtype=np.int32)
        self.soilCountArr[0] = self.soilTypeCount     
      
        #Fill soil type arrays      
        self.frozenSoilConductivity = np.zeros(self.soilTypeCount, dtype=np.float32)
        self.thawedSoilConductivity = np.zeros(self.soilTypeCount, dtype=np.float32)
        self.drySoilSpecHeat = np.zeros(self.soilTypeCount, dtype=np.float32)
        self.frozenSoilVolHeat = np.zeros(self.soilTypeCount, dtype=np.float32)
        self.thawedSoilVolHeat = np.zeros(self.soilTypeCount, dtype=np.float32)
        self.drySoilDensity = np.zeros(self.soilTypeCount, dtype=np.float32)
        self.waterPerDrySoilMass = np.zeros(self.soilTypeCount, dtype=np.float32)
        self.phaseTransitionPoint = np.zeros(self.soilTypeCount, dtype=np.float32)  
        self.liquidWaterGraphLengths = np.zeros(self.soilTypeCount, dtype=np.int32)
      
        for soilidx in range(self.soilTypeCount):
            Soil = self.model.soils[soilidx]
            self.frozenSoilConductivity[soilidx] = translateConductivity(Soil.frozenSoilConductivity)
            self.thawedSoilConductivity[soilidx] = translateConductivity(Soil.thawedSoilConductivity)
            self.drySoilSpecHeat[soilidx] = Soil.thawedSoilVolumetricHeat/Soil.drySoilDensity-Soil.waterPerDrySoilMass * self.params[5] #water specific heat
            self.frozenSoilVolHeat[soilidx] = Soil.frozenSoilVolumetricHeat
            self.thawedSoilVolHeat[soilidx] = Soil.thawedSoilVolumetricHeat
            self.drySoilDensity[soilidx] = Soil.drySoilDensity
            self.waterPerDrySoilMass[soilidx] = Soil.waterPerDrySoilMass
            self.phaseTransitionPoint[soilidx] = Soil.phaseTransitionPoint      
            self.liquidWaterGraphLengths[soilidx] = len(Soil.liquidWaterGraph)

        #Liquid water graphs
        totalgraphelements = 0
        for count in self.liquidWaterGraphLengths:
            totalgraphelements = totalgraphelements + count
        totalgraphelements = totalgraphelements * 2
  
        self.liquidWaterGraphs = np.zeros(totalgraphelements, dtype=np.float32)

        currp = 0
        for soilidx in range(self.soilTypeCount):
            Soil = self.model.soils[soilidx]
            for idx in range(self.liquidWaterGraphLengths[soilidx]):
                Point = Soil.liquidWaterGraph[idx] 
                self.liquidWaterGraphs[currp+2*idx ] =  Point[0]
                self.liquidWaterGraphs[currp+2*idx +1] = translateLiquidWaterPercentage(Point[1]) 
            currp = currp+2*self.liquidWaterGraphLengths[soilidx]  

  
    ####################BOUNDARIES##################################
    def getBinaryBounds(self):
        
        ## Fill boundary values arrays
        #we need default zero flow condition here
        boundCount = len(self.model.bounds)+1           
        self.boundCountArr  = np.zeros(1, dtype=np.int32)        
        self.boundCountArr[0] = boundCount         
        self.boundType  = np.zeros(boundCount, dtype=np.int32)
        self.tempLag    = np.zeros(12*boundCount, dtype=np.float32)
        self.alphaConv  = np.zeros(12*boundCount, dtype=np.float32)
        self.boundValue = np.zeros(12*boundCount, dtype=np.float32)
                 
                 
        #fill default zero        
        boundIdx = 0
        self.boundType[boundIdx] = 2
        for month in range(12):
            self.boundValue[boundIdx*12+month] = 0.0
         
         
        
        #wind_by_month, 
        #albedo, latitude, 
        #infiltration_correction

        #Fill boundary type arrays
        for boundIdx in range(1,boundCount):
            bound = self.model.bounds[boundIdx-1]
            if bound.kind == 1:
                bt = 1
                data1 = bound.temperature
            elif bound.kind == 2:
                bt = 2
                data1 = [translateHeatFlow(x) for x in bound.heatFlowDensity ]
            elif bound.kind == 3:
                bt = 3
                data1 = air_temperature(bound.temperature, bound.summerStart, bound.winterStart,
                                        bound.insolationMod, bound.infiltrationMod,
                                        bound.windSpeed, bound.albedo, bound.latitude,
                                        bound.infiltration)
                print "Bound", boundIdx-1, "corrected temperature:"
                print data1
                data2 = [translateRecConductivity(x) for x in bound.tempLag ]
                print "Bound", boundIdx-1, "T_lag:"
                print data2
                alpha = [translateConductivity(x) for x in bound.alphaConvection ]                 
                data3 = heat_exchange_coeff_alpha(alpha, bound.windSpeed, 
                              np.array(bound.snowDensity), np.array(bound.snowThickness),
                              bound.summerStart, bound.winterStart,
                              bound.isNatural )
                print "Bound", boundIdx-1, "alpha:"
                print data3
            else:
                print "Bound processing error!"
            self.boundType[boundIdx] = bt
            for month in range(12):
                self.boundValue[boundIdx*12+month] = data1[month]
                if bt==3:  
                    self.tempLag[boundIdx*12+month] = data2[month]
                    self.alphaConv[boundIdx*12+month] = data3[month]                 
  
 
    ##################  interconnects  ###############################      
    def getBinaryInterconnects(self):
        #for every interconnect we find adjanced zone and mark 
        #these volume sizes 
        icCount = len(self.extendedIC)
        self.icCountArr  = np.zeros(1, dtype=np.int32)
        self.icCountArr[0] = 2*icCount
        
        self.icOwner = np.zeros(2*icCount, dtype=np.int32)
        self.icSource = np.zeros(2*icCount, dtype=np.int32)
        self.icSourceSide = np.zeros(2*icCount, dtype=np.int32)
        self.icSourceH = np.zeros(2*icCount, dtype=np.float32)
        self.icSourceMshift = np.zeros(2*icCount, dtype=np.int32)
        self.icSourceNshift = np.zeros(2*icCount, dtype=np.int32)
        ## owner[i][j] <-> source[i+Mshift][j+Nshift]
        
        for icIdx in range(icCount):
            ic = self.extendedIC[icIdx]
            self.icOwner[2 * icIdx]      = ic.block1idx
            self.icOwner[2 * icIdx + 1]  = ic.block2idx
            self.icSource[2 * icIdx]     = ic.block2idx
            self.icSource[2 * icIdx + 1] = ic.block1idx
            self.icSourceSide[2 * icIdx]     = ic.block2Side
            self.icSourceSide[2 * icIdx + 1] = ic.block1Side
            #we already know grid now
            #and can find H and shifts            
            ## owner (1) [i][j] <-> source (2) [i+Mshift][j+Nshift]
            h1, h2, m, n = getH1H2MN(ic, self.blockGridSteps[ic.block1idx], self.blockGridSteps[ic.block2idx],
                                   self.offsetArrays[ic.block1idx], self.offsetArrays[ic.block1idx])
            self.icSourceH[2 * icIdx] = h2
            self.icSourceH[2 * icIdx + 1] = h1
            self.icSourceMshift[2 * icIdx] = m
            self.icSourceNshift[2 * icIdx] = n
            self.icSourceMshift[2 * icIdx + 1] = -m
            self.icSourceNshift[2 * icIdx + 1] = -n
          
        
        
    ##################  heat sources  ###############################  
    def getBinarySources(self):
        
        sourcecount = len(self.model.sources) + 1
        self.sourceCountArr  = np.zeros(1, dtype=np.int32)
        self.sourceCountArr[0] = sourcecount
      
        self.sourceData = np.zeros(self.sourceCountArr[0]*12, dtype=np.float32)
        #1. fake 0th source meaning no source
        for month in range(12):
            self.sourceData[12*0+month] = 0.0
        for sourceIdx in range(self.sourceCountArr[0]-1):
            source = self.model.sources[sourceIdx]
            monthDensity = source.heatDensity
            for month in range(12):
                self.sourceData[12*(sourceIdx+1)+month] = translateConductivity(monthDensity[month])
                
                
    ##################  caverns  ###############################  
    def getBinaryCaverns(self):       
        caverncount = len(self.model.caverns) 
        self.cavernCountArr  = np.zeros(1, dtype=np.int32)
        self.cavernCountArr[0] = caverncount
      
        self.cavernBoundLinkArr = np.zeros( 6 * self.cavernCountArr[0], dtype=np.int32)
        for cavernIdx in range(self.cavernCountArr[0]):
            cavern = self.model.caverns[cavernIdx]
            for bIdx in range(6):
                self.cavernBoundLinkArr[cavernIdx*6 + bIdx] = cavern.boundList[bIdx]+ BOUND_SHIFT
      
      
    ####################BLOCKS######################################
    #State and soil-cavern Regions (domain body)
    def fillBlockSoil(self, blockIdx, defaultSoilNum, defTemp ):        
        SoilOrCavernIndex = np.zeros(self.mainArraySizes[blockIdx], dtype=np.uint16)      
        Temperature = np.zeros(self.mainArraySizes[blockIdx], dtype=np.float32)     
        Enthalpy = np.zeros(self.mainArraySizes[blockIdx], dtype=np.float32)
        AtPhaseTransition = np.zeros(self.mainArraySizes[blockIdx], dtype=np.uint8)
        LiquidWaterPercentage = np.zeros(self.mainArraySizes[blockIdx], dtype=np.float32)
        
        #DEFAULT FILL
        #for idx in range(self.mainArraySizes[blockIdx]):
        #    SoilOrCavernIndex[idx] = defaultSoilNum*2 + 0 #means this is soil and its number is defaultSoilNum
        #    Temperature[idx] = defTemp            
        SoilOrCavernIndex.fill(defaultSoilNum*2 + 0)
        Temperature.fill(defTemp)            
        
        block = self.extendedBlocks[blockIdx]
        print "Updating soil regions and temperature"        
        for soilRegion in block.soilRegions:
            soilIdx = soilRegion.soilNumber
            soilTemp = soilRegion.temperature
            soil = self.model.soils[soilIdx] 
            
            #get rects corresponding to this soil            
            x1,x2,y1,y2,z1,z2 = getrectcoord(soilRegion)
            print "found rectangle", x1,x2,y1,y2,z1,z2
            #find blocks corresponding to the rectangle            
            ix1,ix2 = getIntIndices(self.blockGridSteps[blockIdx][0], self.sizeArrays[blockIdx][0], x1, x2)
            iy1,iy2 = getIntIndices(self.blockGridSteps[blockIdx][1], self.sizeArrays[blockIdx][1], y1, y2)
            iz1,iz2 = getIntIndices(self.blockGridSteps[blockIdx][2], self.sizeArrays[blockIdx][2], z1, z2)
            print "updating with", soilIdx, soilTemp
            
            #for idx in range(ix1,ix2):
            #    for idy in range(iy1,iy2):
            #        for idz in range(iz1,iz2):
            #            index = self.sizeArrays[blockIdx][1]* self.sizeArrays[blockIdx][0]* idz + self.sizeArrays[blockIdx][0]*idy + idx
            #            SoilOrCavernIndex[index] = soilIdx*2 + 0 #means this is soil and its number is soilIdx
            #            Temperature[index] = soilTemp
            
            SoilOrCavernIndex3D = SoilOrCavernIndex.reshape(self.sizeArrays[blockIdx][2], self.sizeArrays[blockIdx][1], 
                                             self.sizeArrays[blockIdx][0])
            Temperature3D = Temperature.reshape(self.sizeArrays[blockIdx][2], self.sizeArrays[blockIdx][1], 
                                             self.sizeArrays[blockIdx][0])
            SoilOrCavernIndex3D[iz1:iz2, iy1:iy2, ix1:ix2] = soilIdx*2 + 0
            Temperature3D[iz1:iz2, iy1:iy2, ix1:ix2] = soilTemp
            
            print (ix2-ix1)*(iy2-iy1)*(iz2-iz1), "volumes updated"
            
            
        print "Updating cavern regions"        
        for cavernRegion in block.cavernRegions:
            cavernIdx = cavernRegion.cavernNumber            
            cavern = self.model.caverns[cavernIdx]             
            #get rects corresponding to this soil            
            x1,x2,y1,y2,z1,z2 = getrectcoord(cavernRegion)
            print "found rectangle", x1,x2,y1,y2,z1,z2
            #find blocks corresponding to the rectangle            
            ix1,ix2 = getIntIndices(self.blockGridSteps[blockIdx][0], self.sizeArrays[blockIdx][0], x1, x2)
            iy1,iy2 = getIntIndices(self.blockGridSteps[blockIdx][1], self.sizeArrays[blockIdx][1], y1, y2)
            iz1,iz2 = getIntIndices(self.blockGridSteps[blockIdx][2], self.sizeArrays[blockIdx][2], z1, z2)
            print "updating with", cavernIdx
            volcount = 0;
            for idx in range(ix1,ix2):
                for idy in range(iy1,iy2):
                    for idz in range(iz1,iz2):
                        index = self.sizeArrays[blockIdx][1]* self.sizeArrays[blockIdx][0]* idz + self.sizeArrays[blockIdx][0]*idy + idx
                        SoilOrCavernIndex[index] = cavernIdx*2 + 1 #means this is a cavern and its number is cavernIdx                        
                        volcount = volcount+1
            print volcount, "volumes updated"
        #soil or cavern regions
        self.soilOrCavernIndices.append(SoilOrCavernIndex)
        #state
        self.temperatures.append(Temperature)
        self.enthalpies.append(Enthalpy)
        self.atPhaseTransitions.append(AtPhaseTransition)
        self.liquidWaterPercentages.append(LiquidWaterPercentage)
        
      
    #SOURCE Regions
    def fillBlockSources(self, blockIdx):
        sourceIndex = np.zeros(self.mainArraySizes[blockIdx], dtype=np.uint16)        
        block = self.extendedBlocks[blockIdx]        
        
        print "Updating heat source info"
        
        for heatSourceRegion in block.heatSourceRegions:
            heatSourceIdx = heatSourceRegion.heatSourceNumber
            x1,x2,y1,y2,z1,z2 = getrectcoord(heatSourceRegion)
            print "found rectangle", x1,x2,y1,y2,z1,z2 
            #find blocks corresponding to the rectangle        
            ix1,ix2 = getIntIndices(self.blockGridSteps[blockIdx][0], self.sizeArrays[blockIdx][0], x1, x2)
            iy1,iy2 = getIntIndices(self.blockGridSteps[blockIdx][1], self.sizeArrays[blockIdx][1], y1, y2)
            iz1,iz2 = getIntIndices(self.blockGridSteps[blockIdx][2], self.sizeArrays[blockIdx][2], z1, z2)

            volCount = 0;
            for idx in range(ix1,ix2):
                for idy in range(iy1,iy2):
                    for idz in range(iz1,iz2):
                         index = self.sizeArrays[blockIdx][1]* self.sizeArrays[blockIdx][0]* idz + self.sizeArrays[blockIdx][0]*idy + idx
                         sourceIndex[index] = heatSourceIdx + HEATSOURCE_SHIFT #this is because 0 is reserved for no source
                         volCount = volCount+1
            print volCount, "volumes updated"
              
        self.sourceIndices.append(sourceIndex)
      
    #BOUND regions
    def processBoundLocation(self, location, blockIdx, boundIdx, boundZ0, boundZmax, boundY0, boundYmax, boundX0, boundXmax):
        block = self.extendedBlocks[blockIdx]                        
        x1,x2,y1,y2,z1,z2 = getrectcoord(location)
        print "Processing bound or interconnect", boundIdx
        print "found rectangle", x1,x2,y1,y2,z1,z2, "in block", blockIdx
        #find blocks corresponding to the rectangle
        if (location.side == ZSTART) or (location.side == ZEND):
            ix1,ix2 = getIntIndices(self.blockGridSteps[blockIdx][0], self.sizeArrays[blockIdx][0], x1, x2)
            iy1,iy2 = getIntIndices(self.blockGridSteps[blockIdx][1], self.sizeArrays[blockIdx][1], y1, y2)          
            surfCount = 0;
            for idx in range(ix1,ix2):
                for idy in range(iy1,iy2):              
                    index = self.sizeArrays[blockIdx][0]*idy + idx                
                    if location.side == ZSTART:
                        boundZ0[index] = boundIdx
                    else:
                        boundZmax[index] = boundIdx
                    surfCount = surfCount+1
            print surfCount, "surfaces updated"
        
        elif (location.side == YSTART) or (location.side == YEND): 
            ix1,ix2 = getIntIndices(self.blockGridSteps[blockIdx][0], self.sizeArrays[blockIdx][0], x1, x2)
            iz1,iz2 = getIntIndices(self.blockGridSteps[blockIdx][2], self.sizeArrays[blockIdx][2], z1, z2)          
            surfCount = 0;
            for idx in range(ix1,ix2):
                for idz in range(iz1,iz2):              
                    index = self.sizeArrays[blockIdx][0]*idz + idx                
                    if (location.side == YSTART):
                        boundY0[index] = boundIdx
                    else:
                        boundYmax[index] = boundIdx
                    surfCount = surfCount+1
            print surfCount, "surfaces updated"
        
        elif (location.side == XSTART) or (location.side == XEND):
            iy1,iy2 = getIntIndices(self.blockGridSteps[blockIdx][1], self.sizeArrays[blockIdx][1], y1, y2)
            iz1,iz2 = getIntIndices(self.blockGridSteps[blockIdx][2], self.sizeArrays[blockIdx][2], z1, z2)          
            surfCount = 0;
            for idy in range(iy1,iy2):
                for idz in range(iz1,iz2):              
                    index = self.sizeArrays[blockIdx][1]*idz + idy                
                    if location.side == XSTART:
                        boundX0[index] = boundIdx
                    else:
                        boundXmax[index] = boundIdx
                    surfCount = surfCount+1
            print surfCount, "surfaces updated"
        else:
            print "bound processing failed!"
    
    #interconnect regions
    def getIcLocations(self, icIdx):
        """
        for every interconnect there are 2 2d locations to be updated
        the first one is for interconnect block1
        the second one is for interconnect block2
        for x=c plane: m<->z, n<->y
        for y=c plane: m<->z, n<->x
        for z=c plane: m<->y, n<->x    
        """        
        
        interconnect = self.extendedIC[icIdx]
        block1 = self.extendedBlocks[interconnect.block1idx]
        block2 = self.extendedBlocks[interconnect.block2idx]
        
        print "from block", interconnect.block1Side, "to block", interconnect.block2Side
        b1x1 = b1x2 = b1y1 = b1y2 = b1z1 = b1z2 = 0
        b2x1 = b2x2 = b2y1 = b2y2 = b2z1 = b2z2 = 0
        if ((interconnect.block1Side == XSTART) and (interconnect.block2Side == XEND)
         or (interconnect.block1Side == XEND) and (interconnect.block2Side == XSTART)):
            if block1.offsety<=block2.offsety:
                b1y1 = block2.offsety - block1.offsety
                b1y2 = min(block1.y, b1y1 + block2.y)
                b2y1 = 0
                b2y2 = min(block2.y, block1.y - b1y1)
            else:
                b2y1 = block1.offsety - block2.offsety
                b2y2 = min(block2.y, b2y1 + block1.y)
                b1y1 = 0
                b1y2 = min(block1.y, block2.y - b2y1)
            if block1.offsetz<=block2.offsetz:
                b1z1 = block2.offsetz - block1.offsetz
                b1z2 = min(block1.z, b1z1 + block2.z)
                b2z1 = 0
                b2z2 = min(block2.z, block1.z - b1z1)
            else:
                b2z1 = block1.offsetz - block2.offsetz
                b2z2 = min(block2.z, b2z1 + block1.z)
                b1z1 = 0
                b1z2 = min(block1.z, block2.z - b2z1)
            if (interconnect.block1Side == XSTART) and (interconnect.block2Side == XEND):    
                b1side = XSTART
                b2side = XEND
            else: 
                b1side = XEND
                b2side = XSTART
        
        elif ((interconnect.block1Side == YSTART) and (interconnect.block2Side == YEND)
          or (interconnect.block1Side == YEND) and (interconnect.block2Side == YSTART)):
            if block1.offsetx<=block2.offsetx:
                b1x1 = block2.offsetx - block1.offsetx
                b1x2 = min(block1.x, b1x1 + block2.x)
                b2x1 = 0
                b2x2 = min(block2.x, block1.x - b1x1)
            else:
                b2x1 = block1.offsetx - block2.offsetx
                b2x2 = min(block2.x, b2x1 + block1.x)
                b1x1 = 0
                b1x2 = min(block1.x, block2.x - b2x1)
            if block1.offsetz<=block2.offsetz:
                b1z1 = block2.offsetz - block1.offsetz
                b1z2 = min(block1.z, b1z1 + block2.z)
                b2z1 = 0
                b2z2 = min(block2.z, block1.z - b1z1)
            else:
                b2z1 = block1.offsetz - block2.offsetz
                b2z2 = min(block2.z, b2z1 + block1.z)
                b1z1 = 0
                b1z2 = min(block1.z, block2.z - b2z1)
            if (interconnect.block1Side == YSTART) and (interconnect.block2Side == YEND):    
                b1side = YSTART
                b2side = YEND            
            else: 
                b1side = YEND
                b2side = YSTART
                
        elif ((interconnect.block1Side == ZSTART) and (interconnect.block2Side == ZEND)
          or (interconnect.block1Side == ZEND) and (interconnect.block2Side == ZSTART)):
            if block1.offsetx<=block2.offsetx:
                b1x1 = block2.offsetx - block1.offsetx
                b1x2 = min(block1.x, b1x1 + block2.x)
                b2x1 = 0
                b2x2 = min(block2.x, block1.x - b1x1)
            else:
                b2x1 = block1.offsetx - block2.offsetx
                b2x2 = min(block2.x, b2x1 + block1.x)
                b1x1 = 0
                b1x2 = min(block1.x, block2.x - b2x1)
            if block1.offsety<=block2.offsety:
                b1y1 = block2.offsety - block1.offsety
                b1y2 = min(block1.y, b1y1 + block2.y)
                b2y1 = 0
                b2y2 = min(block2.y, block1.y - b1y1)
            else:
                b2y1 = block1.offsety - block2.offsety
                b2y2 = min(block2.y, b2y1 + block1.y)
                b1y1 = 0
                b1y2 = min(block1.y, block2.y - b2y1)
            if (interconnect.block1Side == ZSTART) and (interconnect.block2Side == ZEND):
                b1side = ZSTART
                b2side = ZEND           
            else: 
                b1side = ZEND
                b2side = ZSTART
        
        loc1 = BoundRegion(interconnect.block1idx, b1side, b1x1, b1x2, b1y1, b1y2, b1z1, b1z2)
        loc2 = BoundRegion(interconnect.block2idx, b2side, b2x1, b2x2, b2y1, b2y2, b2z1, b2z2)
        return loc1, loc2
    
    def fillBlockBounds(self, blockIdx):
        block = self.extendedBlocks[blockIdx]
      
        zplanesurfcount = self.sizeArrays[blockIdx][1]*self.sizeArrays[blockIdx][0]
        yplanesurfcount = self.sizeArrays[blockIdx][2]*self.sizeArrays[blockIdx][0]
        xplanesurfcount = self.sizeArrays[blockIdx][2]*self.sizeArrays[blockIdx][1]
        
        #zero is default bound index 0*2 + 0 
        boundZ0 = np.zeros(zplanesurfcount, dtype=np.uint16)
        boundZmax = np.zeros(zplanesurfcount, dtype=np.uint16)
        boundY0 = np.zeros(yplanesurfcount, dtype=np.uint16)
        boundYmax = np.zeros(yplanesurfcount, dtype=np.uint16)
        boundX0 = np.zeros(xplanesurfcount, dtype=np.uint16)
        boundXmax = np.zeros(xplanesurfcount, dtype=np.uint16)
        
                
        #correct non-default bounds        
        for boundRegion in block.boundRegions:
            #shift by one to accomodate default zero 
            boundIdx = boundRegion.boundNumber + BOUND_SHIFT
            #get rects corresponding to this bound      
            self.processBoundLocation(boundRegion, blockIdx, 2*boundIdx + 0, boundZ0, boundZmax, boundY0, boundYmax, boundX0, boundXmax)

        #correct bounds that are in fact interconnects
        for icIdx in range(len(self.extendedIC)):
            interconnect = self.extendedIC[icIdx]            
            if interconnect.block1idx == blockIdx:	      
              #get rects corresponding to this bound      
              directedIcIdx = 2*icIdx
              print "Parsing interconnect", icIdx, "direction 1"
              loc1, loc2 =  self.getIcLocations(icIdx)
              self.processBoundLocation(loc1, blockIdx, directedIcIdx*2 + 1, boundZ0, boundZmax, boundY0, boundYmax, boundX0, boundXmax)
                                                        ##this means: interconnect (not bound) number directedIcIdx
            elif interconnect.block2idx == blockIdx:
              directedIcIdx = 2*icIdx + 1
              print "Parsing interconnect", icIdx, "direction 2"
              loc1, loc2 =  self.getIcLocations(icIdx)
              self.processBoundLocation(loc2, blockIdx, directedIcIdx*2 + 1, boundZ0, boundZmax, boundY0, boundYmax, boundX0, boundXmax)       
                                                        ##this means: interconnect (not bound) number directedIcIdx
            
        self.boundZ0s.append(boundZ0)
        self.boundZmaxs.append(boundZmax)
        self.boundY0s.append(boundY0)
        self.boundYmaxs.append(boundYmax)
        self.boundX0s.append(boundX0)
        self.boundXmaxs.append(boundXmax)

      
    def getBinaryBlocks(self):      
        #now fill big arrays for every block
        self.soilOrCavernIndices = []
        self.temperatures = []
        self.enthalpies = []
        self.atPhaseTransitions = []
        self.liquidWaterPercentages = []
      
        self.sourceIndices = []
 
        self.boundZ0s = []
        self.boundZmaxs = []
        self.boundY0s = []
        self.boundYmaxs = []
        self.boundX0s = []
        self.boundXmaxs = []
      
        for blockIdx in range(self.blockCount):
            print "BLOCK #", blockIdx 
            print "sizes are: ", self.sizeArrays[blockIdx][0], self.sizeArrays[blockIdx][1], self.sizeArrays[blockIdx][2]
            print "mainarraysize=", self.mainArraySizes[blockIdx]           
            #find a default soil      
            block = self.extendedBlocks[blockIdx]
            defaultSoilNum = block.defaultSoil        
            if defaultSoilNum==None:            
                print "No default soil for block ", blockIdx, "!. Processing failed."            
            else:
                print  "Default soil number is ", defaultSoilNum
                defTemp = block.defaultTemperature                
                
            #3d BODY regions (soils and caverns)
            time1 = time.time()
            self.fillBlockSoil(blockIdx, defaultSoilNum, defTemp)
            time2 = time.time()
            print "Soil blocks filled in", time2-time1
            #3d regions of heat sources
            time1 = time.time()
            self.fillBlockSources(blockIdx)
            time2 = time.time()
            print "Sources filled in", time2-time1
            #2d regions of bounds and interconnects
            time1 = time.time()
            self.fillBlockBounds(blockIdx)
            time2 = time.time()
            print "Borders filled in", time2-time1

    
    def getBinaryBlockCount(self):
        self.blockCountArr = np.zeros(1, dtype=np.int32)
        self.blockCountArr[0] =  self.blockCount
         
         
    def applyPartition(self, partition):
        #divide!
        newBlockCount = len(partition)
        totalPower = 0
        for idx in range(newBlockCount): 
            totalPower += partition[idx][1]
        zStepCount = len(self.globalGrid[2]) - 1
        
        partCounts = []
        for idx in range(newBlockCount-1):
            power = partition[idx][1]
            partCounts.append( int(round(zStepCount*power/totalPower)) )
        #we get number of steps for every block except the last
        #translate it into z interval sizes
        print "Partcounts:", partCounts
        
        partitionZ = [] 
        counter = 0
        for idx in range(newBlockCount - 1):
             partitionZ.append( self.globalGrid[2][partCounts[idx]+counter] )
             counter += partCounts[idx]
        
        print "Partition:", partitionZ
        
        self.extendedBlocks = self.model.blocks[0].generatePartitionZ(partitionZ)    
        self.blockCount = newBlockCount
        #add new interconnects
        
        for idx in range(self.blockCount-1):
            newIc = Interconnect(idx, idx+1, ZEND, ZSTART)             
        self.extendedIC.append(newIc)
        
        

    def setSimpleMapping(self, device):
        self.archMappings = [] ##map blocks onto computing nodes and devices
        for idx in range(self.blockCount):
            mapping = np.zeros(2, dtype=np.int32)           
            mapping[0] = 0 #node
            mapping[1] = device             
            self.archMappings.append(mapping)
            
    def setMapping(self, mappingLst):  
        self.archMappings = [] ##map blocks onto computing nodes and devices
        for idx in range(self.blockCount):
            mapping = np.zeros(2, dtype=np.int32)
            mapping[0] = mappingLst[idx][0]
            mapping[1] = mappingLst[idx][1]
            self.archMappings.append(mapping)        
            
         
    def generateBinaryData(self, mappingType, device = 0, mapping = [], partition = []):
        '''
          if partition is not empty and only one block is present, 
          we divide this block according to partition and map partitions
          partition is a list of pairs [device number, processing power]
        '''
        #create all necessary arrays
        self.getBinarySettings();       
        self.generateGlobalGrid()
        
        if mappingType == 0:
            #everything goes to single device
            self.setSimpleMapping(device)
            
        elif mappingType == 1:
            self.setMapping(mapping)
        else:
            #we have just one block and want to partition it 
            #now we can decide how to divide our block if necessary
            if (self.blockCount == 1) and not (partition == []):                
                self.applyPartition(partition)                            
                #just do it again for new blocks
                self.generateGlobalGrid()
                mapping = [ [0,idx]  for  [idx,share] in partition ]
                self.setMapping(mapping)            
            else:
                print "Mapping error! Everything mapped to CPU!"
                self.setSimpleMapping(0)
                
        ## process soils, bounds, INTERCONNECTS, etc
       
        self.getBinarySoils()
        self.getBinaryBounds()
        self.getBinaryCaverns()
        self.getBinarySources()
        
        time1 = time.time()
        self.generateBlocksGrid()
        self.getBinaryInterconnects()   
        self.getBinaryBlocks()
        time2 = time.time()
        
        print "Blocks generated in", time2-time1
        self.getBinaryBlockCount()           
       
        
    

    def saveDomFile(self, fileName):
        domfile = open(fileName, "wb")        
        self.versionarr_dom.tofile(domfile)
        self.params.tofile(domfile)           
        #2.1 Save global Grid
        self.globalGridSize.tofile(domfile)
        self.globalGrid[0].tofile(domfile)
        self.globalGrid[1].tofile(domfile)
        self.globalGrid[2].tofile(domfile)
        
        #3. Save blocks
        self.blockCountArr.tofile(domfile)
        for idx in range(self.blockCount):
            self.archMappings[idx].tofile(domfile) 
            self.offsetArrays[idx].tofile(domfile)
            self.sizeArrays[idx].tofile(domfile)
            self.blockGridSteps[idx][0].tofile(domfile)
            self.blockGridSteps[idx][1].tofile(domfile)
            self.blockGridSteps[idx][2].tofile(domfile)
            self.soilOrCavernIndices[idx].tofile(domfile)
            self.sourceIndices[idx].tofile(domfile)
            self.boundX0s[idx].tofile(domfile)
            self.boundXmaxs[idx].tofile(domfile)        
            self.boundY0s[idx].tofile(domfile)
            self.boundYmaxs[idx].tofile(domfile)
            self.boundZ0s[idx].tofile(domfile)
            self.boundZmaxs[idx].tofile(domfile)
        print "saved", self.blockCountArr[0], "blocks"    
        
        #4. Save soils
        self.soilCountArr.tofile(domfile)
        self.frozenSoilConductivity.tofile(domfile) 
        self.thawedSoilConductivity.tofile(domfile) 
        self.drySoilSpecHeat.tofile(domfile) 
        self.frozenSoilVolHeat.tofile(domfile) 
        self.thawedSoilVolHeat.tofile(domfile) 
        self.drySoilDensity.tofile(domfile) 
        self.waterPerDrySoilMass.tofile(domfile) 
        self.phaseTransitionPoint.tofile(domfile) 
        self.liquidWaterGraphLengths.tofile(domfile) 
        self.liquidWaterGraphs.tofile(domfile)
        print "saved", self.soilCountArr[0], "soils"
        
        #5. Save caverns
        self.cavernCountArr.tofile(domfile)
        self.cavernBoundLinkArr.tofile(domfile) 
        print "saved", self.cavernCountArr[0], "caverns"
                
        #6, Save boundaries (and interconnects)                
        self.boundCountArr.tofile(domfile)
        self.boundType.tofile(domfile)        
        self.tempLag.tofile(domfile)  
        self.alphaConv.tofile(domfile)
        self.boundValue.tofile(domfile)
        print "saved", self.boundCountArr[0], "boundary conditions (including default)"
        
        self.icCountArr.tofile(domfile)
        for idx in range(self.icCountArr[0]):
            np.array([ self.icOwner[idx] ]).tofile(domfile)
            np.array([ self.icSource[idx] ]).tofile(domfile)
            np.array([ self.icSourceSide[idx] ]).tofile(domfile)
            np.array([ self.icSourceH[idx] ]).tofile(domfile)
            np.array([ self.icSourceMshift[idx] ]).tofile(domfile)
            np.array([ self.icSourceNshift[idx] ]).tofile(domfile)
        print "saved", self.icCountArr[0], "interconnects (directed)"
        
        #7. Save heat sources        
        self.sourceCountArr.tofile(domfile)
        print "saved", self.sourceCountArr[0], "sources (including default)"
        self.sourceData.tofile(domfile)
        
        
        domfile.close()   
    
    def saveBinFile(self, fileName):    
        binfile = open(fileName, "wb")        
        #1. Save common settings        
        self.versionarr_bin.tofile(binfile)        
        self.timearr.tofile(binfile)                   
        for idx in range(self.blockCount):
            self.temperatures[idx].tofile(binfile)
            self.enthalpies[idx].tofile(binfile)
            self.atPhaseTransitions[idx].tofile(binfile)
            self.liquidWaterPercentages[idx].tofile(binfile)      
        binfile.close()
        
    '''
    def saveToFile(self, fileNameBase, device): 
        time1 = time.time()
        self.generateBinaryData()
        time2 = time.time()
        self.setSimpleMapping(device)
        time3 = time.time()
        self.saveDomFile(fileNameBase+".dom")
        time4 = time.time()
        self.saveBinFile(fileNameBase+".bin")
        time5 = time.time()
        
        print "Data generated in ", time2-time1
        print "Mapping set in ", time3-time2
        print "Dom file saved in ", time4-time3
        print "Bin file saved in ", time5-time4
    ''' 
    
    #mapping type can be 0 (device number provided), 1 (explicit mapping specified) 
    #or 2 (only one block will be partitioned and parts are mapped)
    def buildAndSave(self, domFileName, binFileName,  mappingType, device = 0, mapping = [], partition = []): 
        time1 = time.time()
        self.generateBinaryData(mappingType, device, mapping, partition)
        time2 = time.time()                
        self.saveDomFile(domFileName)
        time3 = time.time()
        self.saveBinFile(binFileName)
        time4 = time.time()        
        print "Data generated in ", time2-time1        
        print "Dom file saved in ", time3-time2
        print "Bin file saved in ", time4-time3
        
        
    def buildAndSaveContinue(self, domFileName, mappingType, device = 0, mapping = [], partition = []): 
        time1 = time.time()
        self.generateBinaryData(mappingType, device, mapping, partition)
        time2 = time.time()                
        self.saveDomFile(domFileName)
        time3 = time.time()        
        print "Data generated in ", time2-time1        
        print "Dom file saved in ", time3-time2
        