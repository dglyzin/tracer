# -*- coding: utf-8 -*-
from os import listdir
import numpy as np

defaultGeomExt = '.dom'
drawExtension = '.dbin'
loadExtension = '.lbin'
  

def getSortedFileList(projectDir, title, extension):
    
    '''get sorted binary file list'''

    unsortedBinFileList = [f for f in listdir(projectDir)
                           if (f.endswith(extension) and f.startswith(title))]
    binTime = np.array([float((f.split(extension)[0])
                              .split(title+'-')[1].split('-')[0])
                        for f in unsortedBinFileList])
    return([unsortedBinFileList[idx] for idx in np.argsort(binTime)])


def getPlotValList(fileList):
   
    '''get ints after - and before extension'''

    '''
    getPlotValList:
    If
       fileList = ['two_blocks0_delays-0.00000000-62.dbin']
    then
       getPlotValList: fileList |-> 62'''

    return([int(f.split('-')[-1].split('.')[0]) for f in fileList])

  
def getSortedDrawBinFileList(projectDir, title):
    return(getSortedFileList(projectDir, title, drawExtension))


def getSortedLoadBinFileList(projectDir, title):
    return(getSortedFileList(projectDir, title, loadExtension))
