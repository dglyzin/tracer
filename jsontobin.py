# -*- coding: utf-8 -*-
'''
Модуль импортирует входной json
Создает по нему модель (включая и задачу, и мэппинг узлов-девайсов)
Создает бинарный файл со свойствами области
Создает файл с функциями задачи

Файл с состоянием не создается, т.к. у нас имеются функции, которые может вызвать ядро 
для заполнения начальных значений


model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''

from domainmodel.model import Model
from domainmodel.binarymodel import BinaryModel
from domainmodel.decomposer import partitionAndMap

if __name__=='__main__':
    projectName = "brusselator_1block"
    InputFile = projectName+".json"
    OutputDataFile = projectName+".dom"
    OutputFuncFile = projectName+".cu"
    model = Model()
    model.loadFromFile(InputFile)
    print "Max derivative order is ", model.getMaxDerivOrder()
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)
    
    bm = BinaryModel(partModel)
    bm.saveDomain(OutputDataFile)
    bm.saveFuncs(OutputFuncFile)
    bm.compileFuncs(OutputFuncFile)
    #model.saveBinaryData(OutputDataFile, OutputFuncFile)
    
    