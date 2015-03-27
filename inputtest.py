# -*- coding: utf-8 -*-
from domainmodel.model import Model
import filecmp

if __name__=='__main__':
    InputFile = "brusselator_2block.json"
    OutputFile = "brusselator_2block_re.json"
    model = Model()
    model.loadFromFile(InputFile)    
    model.saveToFile(OutputFile)
    
    if filecmp.cmp(InputFile, OutputFile, shallow=False):
        print "Test OK!"
    else:
        print "TEST FAILED. Files are different."