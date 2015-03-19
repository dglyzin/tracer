# -*- coding: utf-8 -*-
from domainmodel.model import Model
import filecmp

if __name__=='__main__':
    InputFile = "input_example2d.json"
    OutputFile = "input_example_re.json"
    model = Model()
    model.loadFromFile(InputFile)    
    model.saveToFile(OutputFile)
    
    if filecmp.cmp(InputFile, OutputFile, shallow=False):
        print "Test OK!"
    else:
        print "TEST FAILED. Files are different."