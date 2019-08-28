import logging
import os


def create_logger(loggerName, logFileName,
                  log_level_console='INFO', log_level_file='DEBUG'):
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
    logger = logging.getLogger(loggerName)
    log_level_console = get_logger_level(log_level_console)
    logger.setLevel(log_level_console)
    # print
    # for some bug in logger:
    # logger.setLevel(logging.ERROR)  # consoleLevel

    # create file handler which logs even debug messages
    # errors included
    '''
    with open(logFileName, "w") as f:
        f.write("init logger file\n")
    '''
    fh = logging.FileHandler(logFileName)
    log_level_file = get_logger_level(log_level_file)
    fh.setLevel(log_level_file)

    '''
    # create console handler with a higher log level
    # BUG: it not work (because parent (logger) level is ERROR)
    ch = logging.StreamHandler()
    log_level_console = get_logger_level(log_level_console)
    ch.setLevel(log_level_console)
    '''

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    # logger.addHandler(ch)

    return(logger)


def get_logger_level(log_level):
    
    if log_level == 'None':
        log_level = logging.NOTSET
    elif log_level == 'INFO':
        log_level = logging.INFO
    elif log_level == 'WARNING':
        log_level = logging.WARNING
    elif log_level == 'DEBUG':
        log_level = logging.DEBUG
    elif log_level == 'ERROR':
        log_level = logging.ERROR
    elif log_level == 'CRITICAL':
        log_level = logging.CRITICAL

    return(log_level)
