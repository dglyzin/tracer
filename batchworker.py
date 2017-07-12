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



def launchJob( (paramSet, conn, problemFileNamePath, baseProblemNamePath, mainLogger, jobIdx, jobCount) ):
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
    jobLogger = Logger(LL_DEVEL, logAPI = False, logFileName = logFileName)
    remoteProjectRun(conn, newProjectFileNamePath, False, False, None, None, False, None, False, True, None, jobLogger)
    jobLogger.clean()
    mainLogger.log("Job {} of {} finished".format(jobIdx+1, jobCount), LL_USER)
    

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
        
        # Process arguments
        args = parser.parse_args()
        #main logger for all batch   
        mainLogger = Logger(args.verbose, logAPI = False, logFileName = None)
        
        conn = getConnection(args.connFileNamePath)
        print("connecting to: "+ conn.host)
        batch = BatchWork(args.batchFileNamePath)
        
        problemFileName = batch.batchDict["ProblemFile"]
        
        print("base file for batch work is " + problemFileName)
        
        batchFolder = os.path.splitext(args.batchFileNamePath)[0]        
        print("batch folder is " + batchFolder)
        
        problemFileNamePath = os.path.join(os.path.split(args.batchFileNamePath)[0], problemFileName) 
        baseProblemNamePath = os.path.join(batchFolder, os.path.splitext(problemFileName)[0] )
        
        try:
            os.makedirs(batchFolder)
            print("created batch folder")
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise   
            print("batch folder exists, cleaning")
            for fn in glob(os.path.join(batchFolder,'*')):
                os.remove(fn)         
        
        paramQueue = paramGenerator([], batch.batchDict["ParamRanges"]) 
        #for paramSet in paramQueue:
        #    launchJob( (paramSet, conn, problemFileNamePath, baseProblemNamePath) )
        
        jobCount = len(list(paramQueue)) 
        paramQueue = paramGenerator([], batch.batchDict["ParamRanges"])
        
        pool = mp.Pool(processes=8)
        log = pool.map(launchJob, [( paramSet, conn, problemFileNamePath, baseProblemNamePath, mainLogger, jobIdx, jobCount) for jobIdx, paramSet in enumerate(paramQueue) ] )
        
        #for element in log:
        #    print element
        
        
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