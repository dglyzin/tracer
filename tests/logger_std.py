import logging
import os


def create_logger(logerName, logFileName, consoleLevel='None'):
    '''
    DESCRIPTION:
    Create logger that use both steam and file.
    That settings will be irrelevant to modules structure.
    For example
    in module::

     logger = logging.getLogger('parentName')

    in submodule::

     logger = logging.getLogger('parentName.submoduleName')

    then logger in submodule will use same settings as
    parent.

    INPUT:
    consoleLevel - what will be printed (logger.infos,
                   logger.errors, logger.errors, ...)
    File level always ERROR

    See :
    tester.py.test_logger
    part_2_generators.test_loger

    BUG:
    Because of bug in logger consoleLevel param has no effect
    so see BUG tag in comments for more.

    See also
    https://docs.python.org/2.7/howto/logging-cookbook.html#using-logging-in-multiple-modules
    '''
    # clear log file
    if os.path.isfile(logFileName):
        os.remove(logFileName)
    
    # create logger with name logerName
    logger = logging.getLogger(logerName)

    # print
    if consoleLevel == 'None':
        consoleLevel = logging.NOTSET
    elif consoleLevel == 'INFO':
        consoleLevel = logging.INFO
    elif consoleLevel == 'WARNING':
        consoleLevel = logging.WARNING
    elif consoleLevel == 'DEBUG':
        consoleLevel = logging.DEBUG
    elif consoleLevel == 'ERROR':
        consoleLevel = logging.ERROR
    elif consoleLevel == 'CRITICAL':
        consoleLevel = logging.CRITICAL

    # for some bug in logger:
    logger.setLevel(logging.ERROR)  # consoleLevel

    # create file handler which logs even debug messages
    # errors included
    fh = logging.FileHandler(logFileName)
    fh.setLevel(logging.ERROR)

    # create console handler with a higher log level
    # BUG: it not work (because parent (logger) level is ERROR)
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return(logger)
