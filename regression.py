'''
Created on June 21, 2016

@author: dglyzin
'''

import argparse
import sys
import os
from permafrost.coreinterface import *
from permafrost.domdefmodel.binarymodel import BinaryModel
from shared.base.model import Model
from permafrost.domdefmodel.compresources import CompNode, CompResources
from permafrost.domdefmodel.binlogger import ModelLogger, LL_DEVEL
from comparator import compareData
import json
from glob import glob

def testrun(inputFile, outfnBase, devices, fpDouble, logger):
    fullText = 0
    model = Model()
    model.loadFromFile(inputFile)    
    binModel = BinaryModel(model, logger, fpDouble)    
    
    node = CompNode()
    resources = CompResources()
    for device in devices:
        if device == 0:
            node.addCpu(device, 1)
        else:
            node.addCudaGpu(device-1, 1)
    resources.addNode(node)
    
    binModel.buildAndSave(outfnBase+".dom", outfnBase+"_0-generated.bin", resources)
       
    laputa = Dom3d()
    laputa.Load(outfnBase+".dom", outfnBase+"_0-generated.bin", loglevel=0)
    
        
    laputa.Save(outfnBase+"_1-resave", fullText)
    
    laputa.ProcessOneStep()    
    
    laputa.Save(outfnBase+"_2-onestep", fullText)
        
    finishTime = laputa.GetFinishTime()
    currentTime = laputa.GetTime()
    
    while laputa.GetTime()<currentTime+ (finishTime-currentTime)/2.0:
        #print "step {}".format(laputa.GetTime())
        laputa.ProcessOneStep()
    laputa.Save(outfnBase+"_3-half", fullText)
    while laputa.GetTime()<finishTime:
        laputa.ProcessOneStep()
    laputa.Save(outfnBase+"_4-final", fullText)
    laputa.ReleaseResources()
    
    laputa = Dom3d()
    laputa.Load(outfnBase+".dom", outfnBase+"_3-half.bin", loglevel=0)    
    laputa.Save(outfnBase+"_5-halfresave", fullText)    
    while laputa.GetTime()<finishTime:
        laputa.ProcessOneStep()
    laputa.Save(outfnBase+"_6-finalfromhalf", fullText)
    laputa.ReleaseResources()
    
    
def removeBinaries(path):
    for fileName in glob(os.path.join(path, "*.bin")):      
        os.remove(fileName)
    for fileName in glob(os.path.join(path, "*.dom")): 
        os.remove(fileName)

def constest(filename, noRun, keepBinaries):
    testdict = json.load(open(filename))
    folder = os.path.dirname(filename)
    project = os.path.join(folder, testdict["project"])
    fnBase, _ = os.path.splitext(project) #name without extension    
    logger = ModelLogger(LL_DEVEL, fnBase+".log")    
    logger.log("testing {}".format(filename), LL_DEVEL)
    if not noRun:
        print "Runs for {}".format(filename)
        for run in testdict["runs"]:        
            fpdouble = run["double"]
            title = run["name"]
            devices = run ["devices"]
            print "  running {}".format(title)
            testrun(project, fnBase+"_"+title, devices, fpdouble, logger)
            print "    done."
            
    testPassed = True    
    print "Tests for {}".format(filename)
    for test in testdict["tests"]:
        run1 = test["run1"]
        run2 = test["run2"]
        postfix1 = test["postfix1"]
        postfix2 = test["postfix2"]
        tolerances = test["tolerances"]    
        testPassed = compareData(fnBase+"_"+run1+".dom", fnBase+"_"+run2+".dom", fnBase+"_"+run1+"_"+postfix1+".bin", fnBase+"_"+run2+"_"+postfix2+".bin", tolerances, logger)
        if not testPassed:
            print "  {}_{} vs {}_{} failed! See log file for detais.".format(run1, postfix1, run2, postfix2)            
            break
        else:
            print "  {}_{} vs {}_{} passed.".format(run1, postfix1, run2, postfix2)
    
    logger.clean()
    if testPassed and not keepBinaries:
        removeBinaries(folder)
    return testPassed

def regtest(folder, specfile, noRun, keepBinaries):    
    result =constest(os.path.join(folder, specfile), noRun, keepBinaries) 
    if result:
        print "Test {} OK!\n".format(folder)
    else:
        print "Test {} FAILED!\n".format(folder)
    return result

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Tracer regression tester.', epilog = "Have fun!")    
    parser.add_argument('-folder', type = str, default="regression", help = "Folder to search tests in (including subfolders).")
    parser.add_argument('-keep', help="Do not remove binary files after testing.", action="store_true")
    parser.add_argument('-norun', help="Do not make runs, only compare existing date.", action="store_true")
    
    args = parser.parse_args()
    path = args.folder    
    allOK = True
    
    for root, dirs, files in os.walk(path):
        for jsonfile in files:
            if jsonfile.endswith("spec.test"):                
                print(os.path.join(root, jsonfile))
                if not regtest(root,jsonfile, args.norun, args.keep):
                    allOK = False
    if allOK:
        print "Tests finished successfully."
    else:
        print "WARNING!!! There were falied tests" 
    
