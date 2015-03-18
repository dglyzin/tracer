# -*- coding: utf-8 -*-
'''
Модуль импортирует входной json
Создает по нему модель (включая и задачу, и мэппинг узлов-девайсов)
Создает бинарный файл со свойствами области
Создает файл с функциями задачи

Файл с состоянием не создается, т.к. у нас имеются функции, которые может вызвать ядро 
для заполнения начальных значений
'''

from domainmodel.model import *
import sys
import filecmp

if __name__=='__main__':
    InputFile = "input_example2d.json"
    OutputDataFile = "example2d.dom"
    OutputFuncFile = "example2d.cpp"
    model = Model()
    model.loadFromFile(InputFile)            
    model.saveBinaryData(OutputDataFile, OutputFuncFile)
    
    