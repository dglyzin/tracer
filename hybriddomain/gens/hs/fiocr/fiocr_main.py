import os
import subprocess
import shutil

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.fiocr_main')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('fiocr_main')
logger.setLevel(level=log_level)
'''


class Fiocr():

    '''File Input Output Compilation Routine'''

    def create_out(self, out_path, userfuncs, rm=True):

        '''Create folder for out. Cleare if exist.
        Copy userfuncs.h here.

        INPUTS:

        - ``out_path`` -- path out be generated to

        :param str out_path: path out be generated to

        :param str userfuncs: path to userfuncs.h
        (default is ``hd/gens/hs/src``)
        '''

        folder = out_path
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            if rm:
                shutil.rmtree(folder)
                os.makedirs(folder)

        # pathFrom = os.path.join('tests', 'src', 'libs', 'libuserfuncs.so')
        # shutil.copy2(pathFrom, folder)

        shutil.copy2(userfuncs, folder)

    def to_file(self, out, fileName, ext='.cpp', rm=True):

        '''fileName Used to create folder in
        ``tests/src`` folder and put output here

        (ex: out.cpp)'''

        with open(fileName, 'w') as f:
            f.write(out)

    def make_gcc_so(self, cpp_file, so_file, _stderr=None):
        '''
        DESCRIPTION::

            Generate ``libuserfuncs.so`` file by gcc.
            cpp and ``userfuncs.h`` files needed.
        '''
        logger.debug("FROM make_gcc_so")
        # curDir = os.getcwd()

        # assuming that this file launched from hybriddomain
        '''
        folderName = fileName.split('.')[0]
        path = os.path.join(curDir, 'tests', 'src',
                            'generated', folderName)
        cpp = os.path.join(path, fileName)
        lib = os.path.join(path, 'libuserfuncs.so')
        '''

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
        cmd = ['gcc', cpp_file, '-shared', '-O3', '-o',
               so_file, '-fPIC']
        logger.debug("cmd = %s" % str(cmd))

        '''
        stdout and stderr PIPE means
        that new child stream will be created
        so standart output will be unused.
        See:
        https://docs.python.org/2.7/library/subprocess.html#frequently-used-arguments
        https://docs.python.org/2.7/library/subprocess.html#subprocess.Popen.communicate
        '''
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
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
    DESCRIPTION::

    For cathing error of gcc.
    For tests cases in tester.py.
    '''
    def __init__(self, err):
        self.err = err
        logger.error(self.err)

        
