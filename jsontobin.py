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
    InputFile = "brusselator_2block.json"
    OutputDataFile = "brusselator_2block.dom"
    OutputFuncFile = "example2d.cpp"
    model = Model()
    model.loadFromFile(InputFile)
    
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)
    
    bm = BinaryModel(partModel)
    bm.saveDomain(OutputDataFile)
    bm.saveFuncs(OutputFuncFile)
    #model.saveBinaryData(OutputDataFile, OutputFuncFile)
    
    