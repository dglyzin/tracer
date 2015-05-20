# -*- coding: utf-8 -*-
from domainmodel.model import Model
import filecmp
import sys

def compare(InputFile):      
    OutputFile = InputFile.split('.json')[0]+"_re.json"     
    model = Model()
    model.loadFromFile(InputFile)    
    model.saveToFile(OutputFile)
    
    if filecmp.cmp(InputFile, OutputFile, shallow=False):
        print "Test OK!"
    else:
        print "TEST FAILED. Files are different."
        
        

if __name__=='__main__':
    if len(sys.argv)==1:
        print "Please specify a json file to read"
    else:
        InputFile = sys.argv[1]  
        compare(InputFile)
  
  