# -*- coding: utf-8 -*-
from domainmodel.model import Model
import filecmp
import sys
import json
from jsonschema import validate

def valid(inputFileName, schemaFileName):
    inputFile = open(inputFileName)
    schemaFile = open(schemaFileName)
    
    inputDict = json.loads(inputFile.read())
    schemaDict = json.loads(schemaFile.read())
    
    inputFile.close()
    schemaFile.close()
    
    validate(inputDict, schemaDict)
        

if __name__=='__main__':
    if len(sys.argv)==1:
        print "Please specify a json file to read"
    else:
        inputFileName = sys.argv[1]
        schemaFileName = sys.argv[2]  
        valid(inputFileName, schemaFileName)
  
  