# -*- coding: utf-8 -*-
from os import listdir
import numpy as np

defaultProjFname = 'project'
defaultProjFexp = '.dbin'
  
def getSortedBinFileList(projectDir, title):
    #get sorted binary file list
    unsortedBinFileList =  [ f for f in listdir(projectDir) if f.endswith(defaultProjFexp) ]
    binTime = np.array([float(f.split(defaultProjFexp)[0].split(title+'-')[1])  for f in unsortedBinFileList])
    return [ unsortedBinFileList[idx] for idx in np.argsort(binTime)]  