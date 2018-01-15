'''
Created on Dec 26, 2015

@author: dglyzin
'''
from __future__ import print_function

#log verbatim levels

LL_BASIC = 0 #only absolutely unavoidable info, should not be used normally
LL_USER = 1 #useful info for user at every run
LL_DEVEL = 2 #useful info for developer at every run
LL_DEBUG1 = 3
LL_DEBUG2 = 4
LL_DEBUG3 = 3 #etc
LL_API = 100 #info needed to feed to backend

class Logger(object):
    def __init__(self, logLevel = 0, logAPI = False, logFileName = None):
        '''
          if filename is not specified, stdout is used
        ''' 
        self.logLevel = logLevel
        self.logAPI = logAPI
        self.stdout = True
        if not (logFileName is None):
            self.file = open(logFileName, "w")
            self.stdout = False
            
        
    def clean(self):
        if not self.stdout:
            self.file.close()
        
    def log(self, message, messageLevel, end = "\n"):
        if (messageLevel <= self.logLevel) or  (messageLevel == LL_API) and self.logAPI:
            if self.stdout:
                print(message, end=end)
            else:
                self.file.write(message+"\n")
                
