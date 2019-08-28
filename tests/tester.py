'''
DESCRIPTION:
run from hybriddomain:
python2 -m tests.tester

log file tests/tester.log

for html out run:
python2 -m tests.tester -html

log file tests/tester_raport*.html

TODO:
   Add 2d templats.
   Add mini_solver.

   Add python3

parametresed tests:
https://stackoverflow.com/a/22517624

'''

import unittest

# for parser
'''
from domainmodel.criminal.tests import ParserException
from domainmodel.criminal.tests import test_powers
from domainmodel.criminal.tests import test_diff_outs
from domainmodel.criminal.tests import test_diff_parser
from domainmodel.criminal.tests import test_bounds
'''

# for cpp generation
from tests.tests_common import test_cpp, GccException

# new
from gens.hs.tests.tests_gen_1d import test_gen_1d

# for logger
from tests.tests_common import test_logger as test_logger_from_submodule

from spaces.math_space.common.env.equation.tests import test_all as tests_equation

import os
import sys
import shutil
from settings.logger.logger_std import create_logger, get_logger_level
# from tests.logger_std import create_logger, get_logger_level

from tests.TextTestRunner import SimpleTextRunner
from tests.HTMLTestRunner import HTMLTestRunner

import traceback

import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
    
# hd_path = os.path.abspath('../..')
logFileName = os.path.join(currentdir, 'tester.log')
loggerName = 'tests.tester'  # __name__

# BUG: because of bug in logger this value has no effect:
log_level_console = 'INFO'
log_level_file = 'ERROR'
# file level always ERROR
logger = create_logger(loggerName, logFileName,
                       log_level_console, log_level_file)


def set_tests_for_class(_class, dim, genType='gen', singleModel=None):
    '''
    DESCRIPTION:
    Fill _class by tests from folder tests/{dim}dTests
    for each json file in that folder test_fileName method
    will be created in _class.
    After, these methods can be loaded by TestLoader.

    In _class a core function must exist and have only
    one parameter - path to json for test.

    INPUT:
    genType - 'old' or 'new' generator will be used.
    singeModel - name of particlular model in "dim + 'dTests'"
                 directory.
    '''
    logger.debug("FROM set_tests_for_class")

    # FOR choice generator type:
    if genType == 'eqs':
        pass
    elif genType == 'gen':

        # FOR rename cpp:
        # os.rename(model_old_name, model_new_name)
        # END FOR
        
        if dim in [1]:
            _class.generator = (lambda _self, modelFileName:
                                test_gen_1d(modelFileName))
        else:
            raise BaseException("for genType='new' only dim {1,} supported")
    else:
        raise BaseException("genType must be 'old' or 'new'")
    # END FOR

    # FOR remove all tests from class (from previus
    # usage)
    methodsN = _class.__dict__.keys()
    tests = [mn for mn in methodsN if mn[:5] == 'test_']
    for test in tests:
        delattr(_class, test)
    # END FOR

    # FOR get tests names from json file names in *dTests folder
    curDir = os.getcwd()

    # assuming that this file launched from hybriddomain
    curDir = os.path.join(curDir, 'problems')
    problemsFolder = 'problems'

    testFolder = str(dim)+'dTests'
    # list of all test for dimension dim
    ds = os.listdir(os.path.join(problemsFolder, testFolder))

    if len(ds) == 0:
        raise BaseException("test folder for dimension %d is empty" % dim)

    if singleModel is not None:
        # use single test
        if len(singleModel.split('.')) == 1:
            singleModel = singleModel + '.json'
        modelsP = dict([(singleModel.split('.')[0],
                         os.path.join(curDir, testFolder, singleModel))])
    else:
        # remove all except .json
        # and add full path
        '''
        modelsP = dict([(d.split('.')[0], os.path.join(curDir, testFolder, d))
                        for d in ds if d.split('.')[-1] == 'json'])
        '''
        modelsP = dict([(d, os.path.join(problemsFolder, testFolder, d))
                        for d in ds])

    logger.debug("modlels paths = %s" % str(modelsP))
    # END FOR

    # logger.debug("class before")
    # logger.debug(str(_class.__dict__))

    # FOR add new methods (tests) in class
    for modelName in modelsP.keys():
        testName = 'test_' + modelName
        
        mNameE = modelsP[modelName]
        modelFunc = lambda _self, mNameI = mNameE: _class.core(_self, mNameI)
        # mNameE - is global name
        # while mNameI is local name in lambda
        # that used because otherwise all methods
        # would have same model path.

        setattr(_class, testName, modelFunc)
    # END FOR

    # logger.debug("after")
    # logger.debug(str(_class.__dict__))

    
class GenTestCases(unittest.TestCase):
    '''
    DESCRIPTION:
    Test cases for generate cpp.
    '''
    
    def setUp(self):
        '''
        DESCRIPTION:
        Called automatically before all tests.
        '''
        pass

    def tearDown(self):
        '''
        DESCRIPTION:
        Called automatically after all tests.
        '''
        pass

    def core(self, modelFileName):
        '''
        DESCRIPTION:
        Core for all tests of this class.
        From that core tests created in
        set_tests_for_class method.

        This function generate json to cpp and
        run gcc at it.

        success:
        if generator or test_cpp generate no error
        fail:
        if generator or test_cpp generate some error
        error:
        if some error in parser arrive.


        It is beter to writing exception for each
        test that needed and cath them here.
        If No exception arrive then test passed
        else then logging them and call assertTrue(False)
        for saving it with test name in result.
        
        Also it is better to add DESCRIPTION tag for
        each except block.

        INPUT:
        modelFileName is path to test. It used for
                      model creating and for name of
                      method generated by
                      set_tests_for_class for this class.

        '''
        try:
            # generate
            modelName = self.generator(modelFileName)

            logger.debug("modelName = %s" % str(modelName))

            # gcc
            # test_cpp(modelName)
                        
            # tell that test successful
            self.assertTrue(True)

        except GccException as e:
            '''
            DESCRIPTION:
            Exception in gcc command.
            '''
            logger.error("FROM gcc")
            logger.error(e.err)

            # tell that test failure
            self.assertTrue(False)  # msg
            
        except BaseException as be:
            '''
            DESCRIPTION:
            All other exceptions
            '''
            msg = (("\n FOR model %s \n"
                    + "EXCEPTION: \n %s")
                   % (modelFileName, str(be.args)))
            logger.error("unknown error")
            logger.error(msg)
            logger.error(traceback.format_exc())

            # tell that test failure
            self.assertTrue(False)  # msg


class ParserTestCases(unittest.TestCase):
    '''
    DESCRIPTION:
    Test cases for new parser.
    '''
    
    def setUp(self):
        '''
        DESCRIPTION:
        Called automatically before all tests.
        '''
        pass

    def tearDown(self):
        '''
        DESCRIPTION:
        Called automatically after all tests.
        '''
        pass

    def test_powers(self):
        self.core(test_powers)
        
    def test_diff_outs(self):
        self.core(test_diff_outs)

    def test_diff_parser(self):
        self.core(test_diff_parser)

    def test_bounds(self):
        self.core(test_bounds)
    
    def core(self, test_func):
        '''
        DESCRIPTION:
        Core for all tests of this class.

        This function launch test test_func.

        success:
        if test_func generate no error
        fail:
        if test_func generate some error
        error:
        if some error in parser arrive.

        It is beter to writing exception for each
        test that needed and cath them here.
        If No exception arrive then test passed
        else then logging them and call assertTrue(False)
        for saving it with test name in result.
        
        Also it is better to add DESCRIPTION tag for
        each except block.

        INPUT:
        test_func - test to launch.
        '''
        try:
            test_func()
                        
            # tell that test successful
            self.assertTrue(True)

        except ParserException as e:
            '''
            DESCRIPTION:
            Exception in parser.
            '''
            # tell that test failure
            self.assertTrue(False)  # msg
            
        except BaseException as be:
            '''
            DESCRIPTION:
            All other exceptions
            '''
            logger.error("unknown error in some of parser tests")


def clear_previus():
    # FOR remove previus results:
    curDir = os.getcwd()

    # assuming that this file launched from domainmodel
    path = os.path.join(curDir,
                        'tests',
                        'src',
                        'generated')
    cpps = os.listdir(path)

    logger.debug("removing folders:")
    logger.debug(cpps)

    for cpp in cpps:
        shutil.rmtree(os.path.join(path, cpp))
        # logger.debug("os.remove: nothing to remove")
    # END FOR


def run_to_file(dim=1, genType='old', singleModel=None):

    # clear previus files:
    clear_previus()

    set_tests_for_class(GenTestCases, dim, genType, singleModel)

    _suite = unittest.TestLoader().loadTestsFromTestCase(GenTestCases)

    result = SimpleTextRunner(verbosity=3, buffer=True).run(_suite)

    return(result)


def run_to_html(dim=1, genType='old', singleModel=None):
    '''
    DESCRIPTION:
    For html out.
    '''
    set_tests_for_class(GenTestCases, dim, genType, singleModel)
    _suite = unittest.TestLoader().loadTestsFromTestCase(GenTestCases)

    buf = open('tests/tester_raport_dim_%d_genType_%s.html' % (dim, genType),
               'w')
    runner = HTMLTestRunner(
        stream=buf,
        title='<Demo Test>',
        description='This demonstrates the report output by HTMLTestRunner.'
    )
    runner.run(_suite)
    buf.close()

    
def run_tests_for_parser():

    _suite = unittest.TestLoader().loadTestsFromTestCase(ParserTestCases)

    result = SimpleTextRunner(verbosity=3, buffer=True).run(_suite)

    return(result)


def test_exception_inner():
    try:
        fifo(x)
    except:
        raise(TestException(name='test'))


def test_exception():
    try:
        test_exception_inner()
    except TestException as e:
        print(e.name)
        print(e.data)


class TestException(Exception):
    '''
    DESCRIPTION:
    For cathing error of gcc.
    For tests cases in tester.py.
    '''
    def __init__(self, name):
        self.name = name
        self.data = sys.exc_info()


def test_logger():
    '''
    DESCRIPTION:
    Write log into console and
    file "tests/tester.log"
    It also cath loger from submodule
    and write it data if needed.
    See:
    https://docs.python.org/2.7/howto/logging-cookbook.html#using-logging-in-multiple-modules
    '''
    print("loggerName")
    print(loggerName)
    print("\nlog_level_console")
    print(log_level_console)
    print("log_level_file")
    print(log_level_file)
    logger.info("logger info first")
    logger.debug("logger debug first")
    logger.error("logger error first")

    log_level_file_new = "ERROR"
    logger.handlers[0].setLevel(get_logger_level(log_level_file_new))
    print("\nlog_level_file_new")
    print(log_level_file_new)
    logger.info("logger info second")
    logger.debug("logger debug second")
    logger.error("logger error second")
    
    print("/ntests submodule:")
    # add log from submodule
    test_logger_from_submodule()


def test_equations(genType=None):
    tests_equation()


if __name__ == '__main__':

    test_logger()
    
    '''
    if '-html' in sys.argv:
        runner = run_to_html
    elif '-eq' in sys.argv:
        runner = test_equations
    else:
        runner = run_to_file
    
    # suite().run(unittest.defaultTestResult)
    # print("Test new parser:")
    # run_tests_for_parser()
    # print("\n#############\n")
    
    print("\nTest generation code from templates 1d:")
    runner(genType="gen")
    # run_to_file(genType="gen")
    # run_to_html(genType="gen")
    print("loggerName")
    print(loggerName)
    '''
    
