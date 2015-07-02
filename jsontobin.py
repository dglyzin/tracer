# -*- coding: utf-8 -*-
'''
Модуль импортирует входной json
Создает по нему модель (включая и задачу, и мэппинг узлов-девайсов)
Создает бинарный файл с геометрией и свойствами области (*.dom)
Создает файл с функциями задачи (*.so)

Файл с состоянием не создается, т.к. у нас имеются функции, которые может вызвать ядро
для заполнения начальных значений


model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''
import argparse
from domainmodel.model import Model
from domainmodel.binarymodel import BinaryModel
from domainmodel.decomposer import partitionAndMap

from fileUtils import getSortedBinFileList
import os

def createBinaries(inputFile, finishTimeProvided, finishTime, continueEnabled, continueFnameProvided, continueFileName):    
    projectDir = os.path.dirname(inputFile)
    projectName, _ = os.path.splitext(inputFile)   
    projectTitle = os.path.basename(projectName)
    if projectName == '':
        print "Bad file name"
        return

    OutputDataFile = projectName+".dom"
    OutputFuncFile = projectName+".cpp"
    OutputRunFile = projectName+".sh"

    #we want to find the last computed state to continue if user does not provide filename but tell us to continue
    print projectDir
    if continueEnabled and not continueFnameProvided:
        try:
            continueFileName = os.path.join(projectDir, getSortedBinFileList(projectDir, projectTitle)[-1])
        except:
            print "No bin file to continue from!"
            return
  
    model = Model()
    model.loadFromFile(inputFile)
    print "Max derivative order is ", model.getMaxDerivOrder()
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)

    bm = BinaryModel(partModel)
    bm.saveFuncs(OutputFuncFile)
    bm.saveDomain(OutputDataFile)
    bm.compileFuncs(OutputFuncFile)
    bm.createRunFile(OutputRunFile,OutputDataFile, finishTimeProvided, finishTime, continueEnabled, continueFileName)

                
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Processing json file on a remote cluster.', epilog = "Have fun!")
    #mandatory argument, json filename
    parser.add_argument('fileName', type = str, help = "local json file to process")
    #optional argument, exactly one float to override json finish time
    parser.add_argument('-finish', type=float, help = "new finish time to override json value")
    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    args = parser.parse_args()
  
    inputFile = args.fileName
    finishTime = args.finish
    finishTimeProvided = not (finishTime is None)
    continueFileName = args.cont  
    continueEnabled = not (continueFileName is None)
    continueFnameProvided = not (continueFileName == "/")
    print "jsontobin input!", inputFile, finishTimeProvided, finishTime, continueEnabled, continueFnameProvided, continueFileName
    createBinaries(inputFile, finishTimeProvided, finishTime, continueEnabled, continueFnameProvided, continueFileName)