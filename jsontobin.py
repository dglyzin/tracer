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
import sys
from domainmodel.model import Model
from domainmodel.binarymodel import BinaryModel
from domainmodel.decomposer import partitionAndMap

def createBinaries(InputFile):    
    projectName = InputFile.split('.json')[0]
    if projectName == '':
        print "Bad file name"
        return

    OutputDataFile = projectName+".dom"
    OutputFuncFile = projectName+".cpp"
    OutputRunFile = projectName+".sh"
    model = Model()
    model.loadFromFile(InputFile)
    print "Max derivative order is ", model.getMaxDerivOrder()
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)

    bm = BinaryModel(partModel)
    bm.saveFuncs(OutputFuncFile)
    bm.saveDomain(OutputDataFile)
    bm.compileFuncs(OutputFuncFile)
    bm.createRunFile(OutputRunFile,OutputDataFile)

                
if __name__=='__main__':
    if len(sys.argv)==1:
        print "Please specify a json file to read"
    else:
        InputFile = sys.argv[1]  
        createBinaries(InputFile)