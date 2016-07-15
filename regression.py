# -*- coding: utf-8 -*-
'''
Created on June 21, 2016

@author: dglyzin
скрипт для локального запуска на кластере тестов регрессии

параметры:
-folder 
запуск тестов из подпапки, по умолчанию выполняются все тесты из regression/

-nodecount=4
будут запущены только те тесты, для которых требуется меньше или равно nodecount узлов

идем по всем папкам в folder
запускаем localrun на все проекты с параметрами из спека 
запускаем компаратор -> лог сравнений
'''

import argparse
#import sys
import os
from fileDiff import compareData
import json
#from glob import glob
import logging
from localrun import finalParseAndRun
from domainmodel.binaryFileReader import getBinaryData


def regrun(run, folder):
    """
    run: description of run from test spec
    folder: working folder where spec was found
    """
    projectFileName = run["project"]
    paramString = run["params"]
    paramList = []
    if paramString !="":
        paramList = paramString.split(" ") 
            
    postfix = run["postfix"]
    outFileName, _ = os.path.splitext(projectFileName)
    if postfix != "":
        outFileName = outFileName + "-" + postfix
    paramList += ["-outFileName", outFileName]
    
    logging.info("  running {} with params {} in the folder {} into {}".format(projectFileName, paramString, folder, outFileName))
    #2. parse parameters
    lineParser = argparse.ArgumentParser()
    lineParser.add_argument('-jobId', type = int, help = "unique job ID") 
    #optional argument, exactly one float to override json finish time
    lineParser.add_argument('-finish', type=float, help = "new finish time to override json value")
    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    lineParser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    lineParser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
    lineParser.add_argument('-outFileName', type = str, help="specify output project filename (fileName is default)")
    args = lineParser.parse_args(paramList)
    args.debug = True
    #print "ARGS TO PASS TO JSONTOBIN ", args
    #print "PARAMLIST:", paramList
    #localrun
    return finalParseAndRun(os.path.join(folder, projectFileName), args)

 
def regtest(specfile, noRun, nodeCount, debugQueue):
    testdict = json.load(open(specfile))
    folder = os.path.dirname(specfile)
        
    logging.info("Testing {}".format(specfile))    
    testPassed = True
    
    if not noRun:
        logging.info("Runs for {}".format(specfile))
        for run in testdict["runs"]:
            #1. get project filename            
            projectFileName = run["project"]
            projectDict = json.load(open(os.path.join(folder, projectFileName) ))            
            #if project needs more nodes than available, skip the test
            requiredNodes = len(projectDict["Hardware"])
            if requiredNodes <= nodeCount:
                runOk = regrun(run, folder)
                if not runOk:
                    testPassed = False 
                    logging.error("  Run {} failed.".format(projectFileName))           
            else:
                logging.warning("  Test skipped. Project requires more nodes than provided")
            
            logging.info("  done.")
            
        
    logging.info("Tests for {}".format(folder) )
    for test in testdict["tests"]:
        run1 = test["run1"]
        run2 = test["run2"]
        timestamp1 = test["timestamp1"]
        timestamp2 = test["timestamp2"]
        tolerances = test["tolerances"] 
        fnBase1 = os.path.join(folder, run1)
        fnBase2 = os.path.join(folder, run2)
        
        logging.info("  Testing {}_{} vs {}_{}.".format(run1, timestamp1, run2, timestamp2) )
        
        data1 = getBinaryData(fnBase1+".dom", fnBase1+"-"+timestamp1+".lbin")
        data2 = getBinaryData(fnBase1+".dom", fnBase2+"-"+timestamp2+".lbin")
      
        testPassed = compareData(data1, data2, tolerances)
        if not testPassed:
            logging.error("  {}_{} vs {}_{} failed! See log file for detais.".format(run1, timestamp1, run2, timestamp2) )            
        else:
            logging.info("  {}_{} vs {}_{} passed.".format(run1, timestamp1, run2, timestamp2) )
    
    
    if testPassed:
        logging.info("Test {} OK!\n".format(folder))
    else:
        logging.error("Test {} FAILED!\n".format(folder))
    return testPassed

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Tracer regression tester.', epilog = "Have fun!")        
    parser.add_argument('-nodecount', type = int, default=4, help = "Number of available nodes to run tests on.")    
    parser.add_argument('-folder', type = str, default="regression", help = "Folder to search tests in (including subfolders).")    
    parser.add_argument('-norun', help="Do not make runs, only compare existing data.", action="store_true")
    parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
    
    args = parser.parse_args()
    path = args.folder    
    allOK = True
       
    logging.basicConfig(filename=os.path.join(path,'regression.log'), filemode='w', level=logging.DEBUG)
    logging.info("Regression tests started")
    
    for root, dirs, files in os.walk(path):
        for specfile in files:
            if specfile.endswith("test.spec"):                
                print(os.path.join(root, specfile))
                if not regtest(os.path.join(root, specfile), args.norun, args.nodecount, args.debug):
                    allOK = False
    if allOK:
        print "Tests finished successfully."
    else:
        print "WARNING!!! There were falied tests"