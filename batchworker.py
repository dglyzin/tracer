#!/usr/local/bin/python2.7
# encoding: utf-8
'''
parameterscan -- shortdesc

parameterscan is a description

It defines classes_and_methods

@author:     dglyzin

@copyright:  2017 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import errno
from glob import glob
import multiprocessing as mp



from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from remoterun import getConnection, remoteProjectRun
import json
from numpy import arange
from domainmodel.model import Model

from domainmodel.logger import Logger, LL_USER, LL_DEVEL, LL_API 

__all__ = []
__version__ = 0.1
__date__ = '2017-07-10'
__updated__ = '2017-07-10'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class BatchWork(object):
    def __init__(self, fileName):
        with open(fileName,"r") as batchFile:    
            self.batchDict = json.loads(batchFile.read())
    
    

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def paramGenerator(fixedParams, paramRanges):
    '''
    input: list of parameter ranges
    result: linearized parameters
    '''
    if paramRanges == []:
        yield fixedParams
    else:
        curRangeDict = paramRanges[0]
        curRange = arange(curRangeDict["Start"], curRangeDict["End"], curRangeDict["Step"])
        for value in curRange:
            newFixedParam = [{"Name":curRangeDict["Param"], "Value": value}]
            nextLevelGenerator = paramGenerator(fixedParams + newFixedParam, paramRanges[1:])            
            for item in nextLevelGenerator:
                yield item 

def pathifyParams(paramSet):
    res = ''
    for param in paramSet:
        res = res + "-"+ param["Name"] + "=" + str(param["Value"])
    return res


def checkOutfilesExists(projectFileNamePath):
    '''
    input: json file name     
    output: true if complete set of results present else otherwise    
    '''
    model = Model()
    model.loadFromFile(projectFileNamePath)
    #print(projectFileNamePath)
    #print(os.path.splitext(projectFileNamePath))
    baseFileNamePath, _ = os.path.splitext(projectFileNamePath)
    for plotIdx in range(len(model.plots)):
        fileName = baseFileNamePath+"-plot" + str(plotIdx) + ".mp4"
        if not (os.path.isfile(fileName)):
            return False 

    for resIdx in range(len(model.results)):
        fileName = baseFileNamePath+"-res" + str(resIdx) + ".out"
        if not (os.path.isfile(fileName)):
            return False

    return True

def launchJob( (paramSet, conn, problemFileNamePath, baseProblemNamePath, mainLogger, jobIdx, jobCount) ):
    '''
        returns  base path and filename:  
    '''
    
    #+ str(paramSet)
    mainLogger.log("Job {} of {} started".format(jobIdx+1, jobCount), LL_USER)
    #1. generate file
    newProjectFileNamePath = baseProblemNamePath + pathifyParams(paramSet)  + ".json"
    model = Model()
    model.loadFromFile(problemFileNamePath)
    model.applyParams(paramSet)
    model.saveToFile(newProjectFileNamePath) 
    #2. run it
    logFileName = baseProblemNamePath + pathifyParams(paramSet)  + ".log" 
    #we have to check somehow if there is a file with results or we have to compute it
    if not checkOutfilesExists(newProjectFileNamePath):
        jobLogger = Logger(LL_DEVEL, logAPI = False, logFileName = logFileName)
        remoteProjectRun(conn, newProjectFileNamePath, False, False, None, None, False, None, False, True, None, jobLogger)
        jobLogger.clean()
        
    mainLogger.log("Job {} of {} finished".format(jobIdx+1, jobCount), LL_USER)
    return paramSet, baseProblemNamePath + pathifyParams(paramSet)

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by dglyzin on %s.
  Copyright 2017 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('connFileNamePath', type = str, help = "local json file with connection info")    
        parser.add_argument('batchFileNamePath', type = str, help = "local json batch file")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=1, help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-retry', help="continue failed run", action="store_true")
        
        # Process arguments
        args = parser.parse_args()
        #main logger for all batch   
        mainLogger = Logger(args.verbose, logAPI = False, logFileName = None)
        
        conn = getConnection(args.connFileNamePath)
        mainLogger.log("connecting to: "+ conn.host, LL_USER)
        batch = BatchWork(args.batchFileNamePath)
        
        problemFileName = batch.batchDict["ProblemFile"]
        
        mainLogger.log("base file for batch work is " + problemFileName, LL_USER)
        
        batchFolder = os.path.splitext(args.batchFileNamePath)[0]        
        mainLogger.log("batch folder is " + batchFolder, LL_USER)
        
        problemFileNamePath = os.path.join(os.path.split(args.batchFileNamePath)[0], problemFileName) 
        baseProblemNamePath = os.path.join(batchFolder, os.path.splitext(problemFileName)[0] )
        
        try:
            os.makedirs(batchFolder)
            mainLogger.log("created batch folder", LL_USER)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise   
            if args.retry:
                mainLogger.log("Continuing computation using existing files", LL_USER)
            else:
                mainLogger.log("batch folder exists, cleaning", LL_USER)
                for fn in glob(os.path.join(batchFolder,'*')):
                    os.remove(fn)         
        
        paramQueue = paramGenerator([], batch.batchDict["ParamRanges"]) 
        #for paramSet in paramQueue:
        #    launchJob( (paramSet, conn, problemFileNamePath, baseProblemNamePath) )
        paramQueueList = list(paramQueue) 
        jobCount = len(paramQueueList) 
        paramQueue = paramGenerator([], batch.batchDict["ParamRanges"])
        
        pool = mp.Pool(processes=8)
        paramResultFiles = pool.map(launchJob, [( paramSet, conn, problemFileNamePath, baseProblemNamePath, mainLogger, jobIdx, jobCount) for jobIdx, paramSet in enumerate(paramQueue) ] )
        
        
        #now we have all out files in folder and can combine them into parametric picture or text file
        
        #open base model and find requested results there
        model = Model()
        model.loadFromFile(problemFileNamePath)
        
        argNamesList = []
        for result in model.results:
            #mainLogger.log(str(result), LL_USER)
            argNamesList.append(result["Name"])
        #for every parameter combination
        
        paramNames = " ".join([rng["Param"] for rng in batch.batchDict["ParamRanges"]])
        
        batchOuts = {op["Name"]:["#" + paramNames+ " "+ op["Name"] + "\n"] for op in batch.batchDict["Output"] }
        
        for params, pathBase in paramResultFiles:
            #mainLogger.log("Params: "+str(params), LL_USER)                            
            #load every result into corresponding variables
            varDict = {}
            for idx, reqResult in enumerate(model.results):
                resName = reqResult["Name"]
                postfix = "-res"+str(idx)+".out"
                fileName = pathBase+postfix
                resVal = []
                with open(fileName,'r') as f:
                    for line in f:
                        resVal.append(float(line.split(": ")[1].split("\n")[0]   ) )                
                varDict.update({resName:resVal})
                #mainLogger.log(resName+ "=" + str(resVal) , LL_USER)                
            #2. create batch results
            paramsLine = " ".join([str(param["Value"]) for param in params])
            
            for output in batch.batchDict["Output"]:
                funcLine = "lambda "+ ",".join(argNamesList) + " : " + output["Expression"]                
                evaledfunc = eval(funcLine)
                #mainLogger.log("Computing "+funcLine, LL_USER)
                #mainLogger.log( str(evaledfunc(**varDict)), LL_USER)
                
                resultLine = paramsLine +" " + str(evaledfunc(**varDict)) + "\n"
                
                batchOuts[output["Name"]].append(resultLine)
        #save all results to files    
        for opName in batchOuts:
            fileName = batchFolder + "-" + opName+".out"
            with open(fileName, 'w') as f:
                for line in batchOuts[opName]:
                    f.write(line) 
        
        
        
        
        
        
        
        mainLogger.clean()
        
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2
    
if __name__ == "__main__":
    if DEBUG:
        #sys.argv.append("-h")
        sys.argv.append("-vvvv")        
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'parameterscan_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())