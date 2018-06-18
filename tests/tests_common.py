from envs.hs.model.model_main import ModelNet as Model

import os
import subprocess
import shutil

import logging


# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('tests.tester.tests_common')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('tests_common.py')
logger.setLevel(level=log_level)
'''


def test_logger():
    '''
    DESCRIPTION:
    For demonstration. See tests/tester.py
    Call from tester.py  will use
    it as parent. (because of name in getLogger)
    See:
    https://docs.python.org/2.7/howto/logging-cookbook.html#using-logging-in-multiple-modules
    '''
    logger.info("logger info")
    logger.debug("logger debug")
    logger.error("logger error")


def get_model_for_tests(modelFile="tests/test1d_two_blocks0.json"):
    '''
    DESCRIPTION:
    What is model.
    Create model for all tests.
    '''
    model = Model()
    model.io.loadFromFile(modelFile)
    return(model)


def to_file(out, fileName, ext='.cpp', rm=True):

    '''fileName Used to create folder in
    tests/src folder and put output here
    (ex: out.cpp)'''
    
    folderName = fileName.split('.')[0]
    fileName = folderName + ext
    folder = os.path.join('tests', 'src',
                          'generated', folderName)
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        if rm:
            shutil.rmtree(folder)
            os.makedirs(folder)
    
    path = os.path.join(folder, fileName)
    logger.debug("path =")
    logger.debug(path)
    
    f = open(path, 'w')
    f.write(out)
    f.close()

    pathFrom = os.path.join('tests', 'src', 'libs', 'libuserfuncs.so')
    shutil.copy2(pathFrom, folder)

    pathFrom = os.path.join('tests', 'src', 'libs', 'userfuncs.h')
    shutil.copy2(pathFrom, folder)
    return(path)


def test_cpp(fileName, _stderr=None):
    '''
    DESCRIPTION:
    Test generated file by gcc.
    File should be in "/hybriddomain/tests/src"
    folder and libuserfuncs.so, userfuncs.h also
    '''
    logger.debug("FROM test_cpp")
    curDir = os.getcwd()

    # assuming that this file launched from hybriddomain
    folderName = fileName.split('.')[0]
    path = os.path.join(curDir, 'tests', 'src',
                        'generated', folderName)
    cpp = os.path.join(path, fileName)
    lib = os.path.join(path, 'libuserfuncs.so')

    # change bad path
    '''
    f = open(cpp)
    data = f.read()
    f.close()
    data = data.replace("prepr_folder_path/doc/userfuncs.h", "userfuncs.h")
    f = open(cpp, 'w')
    f.write(data)
    f.close()
    '''

    # call gcc
    cmd = ['gcc', cpp, '-shared', '-O3', '-o',
           lib, '-fPIC']
    logger.debug("cmd = %s" % str(cmd))

    '''
    stdout and stderr PIPE means
    that new child stream will be created
    so standart output will be unused.
    See:
    https://docs.python.org/2.7/library/subprocess.html#frequently-used-arguments
    https://docs.python.org/2.7/library/subprocess.html#subprocess.Popen.communicate
    '''
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    # byte to str:
    out = out.decode("utf-8")
    err = err.decode("utf-8")

    if (err is not None and len(err) > 0):
        if _stderr is None:
            raise(GccException(err))
        else:
            return(err)
    
    if _stderr is not None:
        logger.info("out")
        logger.info(out)
        logger.info("err")
        logger.info(err)
    if err is None or len(err) == 0:
        return(True)


class GccException(Exception):
    '''
    DESCRIPTION:
    For cathing error of gcc.
    For tests cases in tester.py.
    '''
    def __init__(self, err):
        self.err = err
        logger.error(self.err)
