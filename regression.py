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
import sys
import os
from comparator import compareData
import json
from glob import glob
import logging
from remoterun import getConnection, remoteProjectRun, finalParseAndRun

def constest(filename, connection, noRun, nodeCount, debugQueue):
    testdict = json.load(open(filename))
    folder = os.path.dirname(filename)
    project = os.path.join(folder, testdict["project"])
    fnBase, _ = os.path.splitext(project) #name without extension    
    logging.info("testing {}".format(filename))    
    if not noRun:
        print "Runs for {}".format(filename)
        for run in testdict["runs"]:
            #1. get project filename            
            projectFileName = run["project"]
            paramString = run["params"]
            postfix = run["postfix"]
            projectFolder, _ = os.path.splitext(projectFileName)
            if postfix != "":
                projectFolder = projectFolder + "-" + postfix
            print "  running {} with params {} in the folder {}".format(title, paramString, folder)
            #2. parse parameters
            lineParser = argparse.ArgumentParser()
            parser.add_argument('-jobId', type = int, help = "unique job ID") 
            #optional argument, exactly one float to override json finish time
            parser.add_argument('-finish', type=float, help = "new finish time to override json value")
            #optional argument with one or no argument, filename to continue computations from
            #if no filename is provided with this option, the last state is taken
            parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
            parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
            args = parser.parse_args(paramString.split(" "))
            
            finalParseAndRun(connection, projectFileName, args, ProjectFolder)
            print "    done."
            
    testPassed = True    
'''    print "Tests for {}".format(filename)
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
'''    
    
    return testPassed

def regtest(folder, specfile, connection, noRun, nodeCount, debugQueue):    
    result = constest(os.path.join(folder, specfile), connection, noRun, nodeCount, debugQueue) 
    if result:
        print "Test {} OK!\n".format(folder)
    else:
        print "Test {} FAILED!\n".format(folder)
    return result

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Tracer regression tester.', epilog = "Have fun!") 
    parser.add_argument('connFileName', type = str, help = "local json file with connection info")    
    parser.add_argument('-nodecount', type = int, default=4, help = "Number of available nodes to run tests on.")    
    parser.add_argument('-folder', type = str, default="regression", help = "Folder to search tests in (including subfolders).")    
    parser.add_argument('-norun', help="Do not make runs, only compare existing data.", action="store_true")
    parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
    
    args = parser.parse_args()
    path = args.folder    
    allOK = True
       
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
    logging.info("Regression tests started")
   
    getGonnection(connFileName)
    
    for root, dirs, files in os.walk(path):
        for jsonfile in files:
            if jsonfile.endswith("spec.test"):                
                print(os.path.join(root, jsonfile))
                if not regtest(root,jsonfile, connection, args.norun, args.nodecount, args.debug):
                    allOK = False
    if allOK:
        print "Tests finished successfully."
    else:
        print "WARNING!!! There were falied tests"