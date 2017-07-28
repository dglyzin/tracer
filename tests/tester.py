'''
DESCRIPTION:
parametresed tests:
https://stackoverflow.com/a/22517624
'''

import unittest

# for parser
from domainmodel.criminal.tests import ParserException
from domainmodel.criminal.tests import test_powers
from domainmodel.criminal.tests import test_diff_outs
from domainmodel.criminal.tests import test_diff_parser
from domainmodel.criminal.tests import test_bounds

# for cpp generation
from introduction.part_2_generators import test_cpp, GccException
# old
from introduction.part_2_generators import test_model_create_cpp
# new
from domainmodel.criminal.tests_gen import test_templates_1d

# for logger
from introduction.part_2_generators import test_logger as test_logger_from_submodule

import os
import sys
import logger_std

from TextTestRunner import SimpleTextRunner
import HTMLTestRunner

logFileName = 'tests/tester.log'
loggerName = __name__

logger = logger_std.create_logger(loggerName, logFileName, 'CRITICAL')
    

def set_tests_for_class(_class, dim, genType='old', singleModel=None):
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

    # FOR change generator type:
    if genType == 'old':
        _class.cpp_generator = (lambda _self, modelFileName:
                                test_model_create_cpp(modelFileName))
    elif genType == 'new':
        _class.cpp_generator = (lambda _self, modelFileName:
                                test_templates_1d(modelFileName))
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

    # FOR get tests names from json file names
    curDir = os.getcwd()

    # assuming that this file launched from domainmodel
    curDir = os.path.join(curDir, 'tests')

    testFolder = str(dim)+'dTests'
    # list of all test for dimension dim
    ds = os.listdir(os.path.join(curDir, testFolder))

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
        modelsP = dict([(d.split('.')[0], os.path.join(curDir, testFolder, d))
                        for d in ds if d.split('.')[-1] == 'json'])

    logger.debug("modlels paths = %s" % str(modelsP))
    # END FOR

    # logger.debug("class before")
    # logger.debug(str(_class.__dict__))

    # FOR add new methods (tests) in class
    for modelName in modelsP.keys():
        testName = 'test_' + modelName
        
        # mNameE - is global name
        # while mNameI is local name in lambda
        mNameE = modelsP[modelName]
        modelFunc = lambda _self, mNameI = mNameE: _class.core(_self, mNameI)
        setattr(_class, testName, modelFunc)
    # END FOR

    # logger.debug("after")
    # logger.debug(str(_class.__dict__))

    
class CppGenTestCases(unittest.TestCase):
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
        if cpp_generator or test_cpp generate no error
        fail:
        if cpp_generator or test_cpp generate some error
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
            # generate cpp
            self.cpp_generator(modelFileName)
            modelName = os.path.basename(modelFileName).split('.')[0]+'.cpp'

            logger.debug("modelName = %s" % str(modelName))
            logger.debug("modelFileName = %s" % str(modelFileName))

            # gcc
            gccOut = test_cpp(modelName)
                        
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


def run_to_file(dim=1, genType='old', singleModel=None):

    set_tests_for_class(CppGenTestCases, dim, genType, singleModel)

    _suite = unittest.TestLoader().loadTestsFromTestCase(CppGenTestCases)

    result = SimpleTextRunner(verbosity=3, buffer=True).run(_suite)

    return(result)


def run_to_html(dim=1, genType='old', singleModel=None):
    set_tests_for_class(CppGenTestCases, dim, genType, singleModel)
    _suite = unittest.TestLoader().loadTestsFromTestCase(CppGenTestCases)
    
    buf = open('tests/tester_raport.html', 'w')
    runner = HTMLTestRunner.HTMLTestRunner(
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

    logger.info("logger info")
    logger.debug("logger debug")
    logger.error("logger error")

    # add log from submodule
    test_logger_from_submodule()


if __name__ == '__main__':
    suite().run(unittest.defaultTestResult)
