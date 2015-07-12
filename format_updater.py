#this script goes through every json file in specified folder, 
#and updates its format

from domainmodel.model import Model
import sys
import os
import filecmp


def constest(filename):
    model = Model()
    model.loadFromFileOld(filename)
    model.saveToFile(filename)    
  
        

if __name__=='__main__':
    if len(sys.argv)==1:
        print "Please specify folder"
    else:                
        path = sys.argv[1]  
        for root, dirs, files in os.walk(path):
            for jsonfile in files:
                if jsonfile.endswith(".json"):
                    print(os.path.join(root, jsonfile))
                    constest(os.path.join(root,jsonfile))
             
    
    
    
    
    


     
