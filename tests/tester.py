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
from domainmodel.criminal.tests import ParserException
from domainmodel.criminal.tests import test_powers
from domainmodel.criminal.tests import test_diff_outs
from domainmodel.criminal.tests import test_diff_parser
from domainmodel.criminal.tests import test_bounds

# for cpp generation
from .introduction.part_2_generators import test_cpp, GccException
# old
from .introduction.part_2_generators import test_model_create_cpp
# new
from domainmodel.criminal.tests_gen import test_templates_1d
from domainmodel.criminal.tests_gen import test_templates_2d
from domainmodel.criminal.tests_gen import test_domain_1d

# for logger
from introduction.part_2_generators import test_logger as test_logger_from_submodule

import os
import sys
from logger_std import create_logger

from TextTestRunner import SimpleTextRunner
from HTMLTestRunner import HTMLTestRunner

logFileName = 'tests/tester.log'
loggerName = __name__

logger = create_logger(loggerName, logFileName, 'CRITICAL')
    

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

    # FOR choice generator type:
    if genType == 'old':
        _class.cpp_generator = (lambda _self, modelFileName:
                                test_model_create_cpp(modelFileName))
    elif genType == 'new':

        def generate_and_rename(modelFileName, dim):

            # generate cpp
            if dim == 1:
                test_templates_1d(modelFileName)
            else:
                test_templates_2d(modelFileName)

            # FOR rename cpp:
            cur_dir = os.getcwd()
            path_to_src = os.path.join(cur_dir, 'tests',
                                       'introduction', 'src')

            file_name_old = 'from_test_template_%dd.cpp' % (dim)

            # name like Brusselator1d.cpp:
            file_name_new = os.path.basename(modelFileName).split('.')[0]+'.cpp'
            
            model_old_name = os.path.join(path_to_src, file_name_old)
            model_new_name = os.path.join(path_to_src, file_name_new)
            
            logger.debug("model_old_name: " + model_old_name)
            logger.debug("model_new_name: " + model_new_name)

            os.rename(model_old_name, model_new_name)
            # END FOR
        
        if dim in [1, 2]:
            _class.cpp_generator = (lambda _self, modelFileName:
                                    generate_and_rename(modelFileName, dim))

            # _class.cpp_generator = (lambda _self, modelFileName:
            #                         test_templates_1d(modelFileName))
        else:
            raise BaseException("for genType='new' only dim {1, 2} supported")
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
        # that used because otherwise all methods
        # would have same model path.
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


class DomGenTestCases(unittest.TestCase):
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

        This function generate functionMaps by
        old and new methods and compare them.

        success:
        if domain generated by cpp_generator()[0] return
        same result as test_domain_1d
        ! cpp_generator in that case is test_model_create_cpp
        ! so set_tests_for_class genType must be 'old'
        fail:
        if new and old results differ
        error:
        if some error in test arrive.

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
            # generate functionMaps by old
            fmo = self.cpp_generator(modelFileName)[0]
            
            # generate functionMaps by new
            fmn = test_domain_1d(modelFileName)

            if fmo == fmn:
                # success
                self.assertTrue(True)
            else:
                # failure
                logger.error("for model %s" % modelFileName)
                logger.error("fmo = %s" % str(fmo))
                logger.error("fmn = %s" % str(fmn))
                
                self.assertTrue(False)

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

'''
not ready yet.
def run_tests_for_dom():
    # create method and
    # fill DomGenTestCases.cpp_generator by test_model_create_cpp
    # for each model in 'tests/1dTests' folder
    set_tests_for_class(DomGenTestCases, 1, "old")

    _suite = unittest.TestLoader().loadTestsFromTestCase(DomGenTestCases)

    result = SimpleTextRunner(verbosity=3, buffer=True).run(_suite)

    return(result)
'''


def clear_previus():
    # FOR remove previus results:
    curDir = os.getcwd()

    # assuming that this file launched from domainmodel
    path = os.path.join(curDir,
                        'tests',
                        'introduction',
                        'src')
    cpps = os.listdir(path)
    for cpp in cpps:
        if cpp.split('.')[1] in ('cpp', 'so'):
            cpp_path = os.path.join(path, cpp)

            # remove previus results:
            try:
                os.remove(cpp_path)
            except:
                logger.debug("os.remove: nothing to remove")
    # END FOR


def run_to_file(dim=1, genType='old', singleModel=None):

    # clear previus files:
    clear_previus()

    set_tests_for_class(CppGenTestCases, dim, genType, singleModel)

    _suite = unittest.TestLoader().loadTestsFromTestCase(CppGenTestCases)

    result = SimpleTextRunner(verbosity=3, buffer=True).run(_suite)

    return(result)


def run_to_html(dim=1, genType='old', singleModel=None):
    '''
    DESCRIPTION:
    For html out.
    '''
    set_tests_for_class(CppGenTestCases, dim, genType, singleModel)
    _suite = unittest.TestLoader().loadTestsFromTestCase(CppGenTestCases)

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

    logger.info("logger info")
    logger.debug("logger debug")
    logger.error("logger error")

    # add log from submodule
    test_logger_from_submodule()


if __name__ == '__main__':
    
    if '-html' in sys.argv:
        runner = run_to_html
    else:
        runner = run_to_file
    
    # suite().run(unittest.defaultTestResult)
    print("Test new parser:")
    run_tests_for_parser()
    print("\n#############\n")
    
    print("\nTest generation code from templates 1d:")
    runner(genType="new")
    # run_to_file(genType="new")
    # run_to_html(genType="new")
    print("#############\n")

    print("\nTest generation code old 1d:")
    runner(genType="old")
    # run_to_file(genType="old")
    # run_to_html(genType="old")

    print("\nTest generation code old 2d:")
    runner(dim=2, genType="old")
    # run_to_file(dim=2, genType="old")
    # run_to_html(dim=2, genType="old")
    
    print("\nTest generation code new 2d:")
    runner(dim=2, genType='new')
    # run_to_file(dim=2, genType='new')
    
