import sys
import filecmp
import numpy as np
import logging

from domainmodel.binaryFileReader import getBinaryData

compareFailed = False
compareOk = True

def compareData(data1, data2, tolerances):
    '''
        comparing states from data1 and data2 with given tolerances	
	'''
    avetol = tolerances["ave"]
    maxtol = tolerances["max"]
    
    if data1.size != data2.size:
        logging.error("    data sizes do not match")
        return compareFailed

    if data1.shape != data2.shape:
        logging.error("    data shapes do not match")
        return compareFailed

    count = data1.size
    absdiff = np.abs( data1.reshape(count) -  data2.reshape(count) )
    diffsum = np.sum( absdiff )
    average = diffsum / count
    if average > avetol:
        logging.error("    average tolerance not met! computed value: {}, reference value: {}".format(average, avetol) )
        return compareFailed
    else: 
        logging.info("    average tolerance ok")
        
    maxdiff = np.max(absdiff)
        
    if maxdiff > maxtol:
        logging.error("    maximum tolerance not met! computed value: {}, reference value: {}".format(maxdiff, maxtol))
        return compareFailed
    else: 
        logging.info("    maximum tolerance ok")
    
    return compareOk



if __name__ == "__main__":
    '''
       simple bytewise comparison
    '''
    argc = len(sys.argv)
    if ((argc < 7) or (argc % 2 != 1)):
        print "Arguments error.\nave tolerance, max tolerance, dom, bin, dom, bin [, dom, bin]"
        exit(0)
    
    dataList = []
    
    for i in range(3, argc - 1, 2):
        data = getBinaryData(sys.argv[i], sys.argv[i+1]);
        dataList.append(data);

    for i in range(0, len(dataList)):
        for j in range(i + 1, len(dataList)):
            #if filecmp.cmp(sys.argv[i], sys.argv[j], shallow=False):
            if compareData(dataList[i], dataList[j], {"ave" : sys.argv[1], "max" : sys.argv[2]}):
                print "Test OK! " + sys.argv[2*i + 4] + " " + sys.argv[2*j + 4]
            else:
                print "TEST FAILED! " + sys.argv[2*i + 4] + " " + sys.argv[2*j + 4]
