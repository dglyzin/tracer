# -*- coding: utf-8 -*-
'''
Аргументы:
1. json-файл подключения
2. json-файл проекта
3. -jobId=
уникальный id задачи, если параметра нет, то работаем без базы
и без питоновского мастер-процесса в mpi
работа с базой возможна только если запись номер jobId
была предварительно создана веб-сервером

4.
Если этот аргумент не указан, то вычисления начинаются с нуля
иначе продолжается либо с последнего существующего, либо с явно указанного
-cont
-cont=<bin state filename to continue>
5. 
-finish=255
время для окончания вычислений, замещает время из json


Модуль импортирует входной json
Покдлючается к удаленной машине
Копирует туда этот же json и напускает на него jsontobin
Запускает решатель

model -> mapped model -> domain.dom+funcs.cpp+run.sh

Command::

 hd$ ~/anaconda3/bin/./python3 -m solvers.hs.remoterun.remoterun \
conn_file_rpath device_conf_file_rpath paths_file_rpath \
test_folder_relative_name

where

   conn_file_rpath is relative path of conn file in ``hybriddomain/settings``
      (ex: ``conn/conn_base.json``)

   paths_file_rpath is relative path of paths file in ``hybriddomain/settings`` folder
      (ex: ``paths/paths_hs_base``)

   device_conf_file_rpath is relative path of device_conf file in ``hybriddomain/settings`` folder
      (ex: ``device_conf/default.json`` folder.

   test_folder_relative_name relative to hd repository folder (where hd folder is lokated)
      name of folder, model .json file stored to.
      (ex: ``hybriddomain/problems/1dTests/logistic_delays``)

Ex (from pf):

# 1d::
 ~/anaconda3/bin/./python3 -c "import hybriddomain.solvers.hs.remoterun.remoterun as ts; ts.run()"  connection_acchome.json devices_acchome.json connection_acchome.json ~/Documents/projects/projectsNew/lab/project_folder/problems/logistic_delays1

      
Ex (from hd):

# 1d::

 hybriddomain$ ~/anaconda3/bin/./python3 -m hybriddomain.solvers.hs.remoterun.remoterun conn/conn_base.json device_conf/default.json paths/paths_hs_base.json hybriddomain/problems/1dTests/logistic_delays

# or::

 ~/anaconda3/bin/./python3 -m hybriddomain.solvers.hs.remoterun.remoterun conn_cluster1 default paths_hs_cluster1 problems/1dTests/logistic_delays

# 2d one block::

 ~/anaconda3/bin/./python3 -m hybriddomain.solvers.hs.remoterun.remoterun conn/conn_base.json device_conf/default.json paths/paths_hs_base.json hybriddomain/problems/2dTests/heat_block_1

# 2d two blocks ics::

 ~/anaconda3/bin/./python3 -m hybriddomain.solvers.hs.remoterun.remoterun conn/conn_base.json device_conf/ics_other.json paths/paths_hs_base.json hybriddomain/problems/2dTests/heat_block_2_ics_other

'''
#remoteRunScriptName='project.sh'
#remoteProjectFileName='project.json'
#remoteMp4Name = 'project.mp4'
from __future__ import print_function

import os
import socket
import paramiko
import argparse

from hybriddomain.solvers.hs.remoterun.io_routine import IORoutine
from hybriddomain.solvers.hs.remoterun.runner import Runner

from hybriddomain.settings.settings_main import Settings
from hybriddomain.envs.hs.model.model_main import ModelNet as Model

# import logging
from hybriddomain.settings.logger.logger_std import create_logger, get_logger_level

# FOR logger:

import inspect
currentdir = os.getcwd()
# print("currentdir:")
# print(currentdir)
# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
hd_dir = currentdir.split("solvers")[0]
logFileName = os.path.join(hd_dir, 'remoterun.log')
loggerName = 'remoterun'  # __name__

log_level_console = 'INFO'
log_level_file = 'DEBUG'
# print("logFileName:")
# print(logFileName)
logger = create_logger(loggerName, logFileName,
                       log_level_console, log_level_file)

# END FOR

import logging
logging.getLogger("paramiko").setLevel(logging.WARNING)
logging.getLogger("peewee").setLevel(logging.WARNING)

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('remoterun')
# logger.setLevel(level=logging.INFO)  # logging.DEBUG
# if using directly uncoment that:

'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('remoterun')
logger.setLevel(level=log_level)

'''
# paramiko.util.log_to_file(os.path.join(os.getcwd(), "tests", "paramiko.log"))


class Remoterun():

    def __init__(self, io, runner):
        self.io = io
        self.runner = runner
      
    def run(self, settings, dimension, notebook=None, model=None,
            log_level_console="INFO", log_level_file="DEBUG",
            remove_old=True,):
        '''
        Run hs with settings:
        1) Create folders at hs/workspace for model and settings
        2) Copy json files of model, device_conf, paths to hs
        3) Generate .sh, .cpp, .dom .so files for hs
        4) Run .sh
        5) Getting hs statuses and progress
           TODO: hs is running
        6) Clearing previus results
        7) Getting back result (.mp3, .out)

        Inputs:

        - ``settings`` - Settings object, contained info about paths
                  device_conf and connection in.
            # make settings:
            model = Model()
            model.io.loadFromFile(modelFileName)
            settings = Settings(model, conn_name, device_conf_name, paths_name)


        params: # TODO: remove desc to other place
                        make settings file

          :param continueEnabled: true if user wants to continue
              from computed file

          :param continueFnameProvided: true if user wants to continue from
              specific file,
              false if the last computed file to be used

          :param continueFileName: ?
           jobId: id of the task in the db

          :param finishTimeProvided: true if user wants to override json value for
              finish time
          :param finishTime:
          :param debug: true if user wants to run small problem (10 min. max)
          :param nortpng: ?

        :param device_conf_name: name of config file in settings/device_conf
         or pf/settings folder.

        see also:
         'hd/settings/settings_main.py'
         'hd/gens/hs/gen_sh.py'
        '''

        # prepare command line argumetnts for preprocessor

        # FOR logger:
        log_level_console = get_logger_level(log_level_console)
        logger.setLevel(log_level_console)
        log_level_file = get_logger_level(log_level_file)
        logger.handlers[0].setLevel(log_level_file)
        # END FOR

        # FOR paths:
        paths = settings.paths
        connection = settings.connection
        workspace = paths['Workspace']
        # workspace = fix_tilde_bug(connection, workspace,
        #                           'hs', 'workspace')
        # tracer_folder = paths['TracerFolder']
        # tracer_folder = fix_tilde_bug(connection, tracer_folder,
        #                               'hs', 'tracer_folder')

        project_name = paths['model']['name']
        project_path = paths['model']['path']
        logger.debug("project_path")
        logger.debug(project_path)
        # END FOR

        # for device_conf:
        device_conf = settings.device_conf

        # get project file name without extension
        logger.debug("project_name")
        logger.debug(project_name)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # print conn.host, conn.username, passwd, conn.port
        try:
            logger.info('\nconnect ...')
            client.connect(hostname=connection.host,
                           username=connection.username,
                           password=connection.password,
                           port=connection.port)
            logger.info('\nconnection established')

            io = self.io
            io.set_logger(logger)
            io.set_client(client)

            # clear old results:
            if remove_old:
                io.remove_old_results(paths)

            # FOR copy/create files/folders:
            # io routine:
            logger.info('\nfiles/folders routine')
            # create global folders:
            io.create_common_folders(paths, device_conf)

            logger.debug('\ncopy files')
            logger.debug(io.__class__.__module__)

            io.copy_common_files(paths)
            io.copy_model_files(paths)
            logger.info('\nfiles/folders routine completed')
            # END FOR

            runner = self.runner
            runner.set_logger(logger)
            runner.set_client(client)

            #3 Run preprocessor on json
            runner.run_preprocessor(settings, connection, paths,
                                    workspace, dimension, notebook)

            #4 Run Solver binary on created files
            runner.run_solver(paths, notebook)

            # get resulting files
            io.get_resulting_files(paths, notebook)

            # FOR adding path to model:
            if model is not None:
                io.add_paths_to_model(paths, model)
            # END FOR

        #Обрабатываю исключения
        except paramiko.ssh_exception.AuthenticationException as e:
            logger.error(u'Неверный логин или пароль')
            logger.error(e)
            return u'Неверный логин или пароль'
        except socket.error as e:
            logger.error(u'Указан неправильный адрес или порт')
            logger.error(e)
            return u'Указан неправильный адрес или порт'
        except paramiko.ssh_exception.SSHException as e:
            logger.error(u'Ошибка в протоколе SSH')
            logger.error(e)
            return u'Ошибка в протоколе SSH'
        '''
        except BaseException as e:
            logger.error("base exception")
            logger.error(e)
            return()
        '''
        
               
def remoteProjectRun(settings, dimension, notebook=None, model=None,
                     log_level_console="INFO", log_level_file="DEBUG",
                     remove_old=True, den='hd', sn='hs'):

    io = IORoutine(den=den, sn=sn)
    runner = Runner(den=den, sn=sn)

    remoterun = Remoterun(io, runner)
    remoterun.run(settings, dimension, notebook=notebook, model=model,
                  log_level_console=log_level_console,
                  log_level_file=log_level_file,
                  remove_old=remove_old)


def finalParseAndRun(settings, dimension, model=None):
    '''
    continueFileName = args.cont
    continueEnabled = not (continueFileName is None)
    continueFnameProvided = (not (continueFileName == "/")
                             if continueEnabled else False)
    # logger = Logger(args.verbose, logAPI=False, logFileName=None)

    params = {
        "continueEnabled": continueEnabled,
        "continueFnameProvided": continueFnameProvided,
        "continueFileName": continueFileName,
        "jobId": args.jobId,
        "finish": args.finish,
        "partition": args.p,
        "nodes": args.w,
        "affinity": args.aff,
        "mpimap": args.mpimap,
        "nortpng": args.nortpng,
        "nocppgen": args.nocppgen
    }
    '''
    remoteProjectRun(settings, dimension, notebook=None, model=model)
    # remoteProjectRun(settings, params, notebook=None)
    # logger.clean()


def run():
    desc = 'Processing json file on a remote cluster.'
    parser = argparse.ArgumentParser(description=desc, epilog="Have fun!")
    parser.add_argument('conn_name', type=str,
                        help=("local json file name (without extension)"
                              + " from hybriddomain/settings/conn folder"))

    # device_conf:
    parser.add_argument('device_conf_name', type=str,
                        help=("name of json file in"
                              + " settings/device_conf folder"))
    # paths_name:
    parser.add_argument('paths_name', type=str,
                        help=("name of json file in"
                              + " settings/paths folder"))

    # mandatory argument, json filename:
    parser.add_argument('projectFileName', type=str,
                        help="local json file to process")


    '''
    # optional argument, unique job Id for identification in database
    parser.add_argument('-jobId', type=int, help="unique job ID")

    # optional argument, exactly one float to override json finish time:
    parser.add_argument('-finish', type=float,
                        help="new finish time to override json value")
    # optional argument with one or no argument,
    # filename to continue computations from
    # if no filename is provided with this option,
    # the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str,
                        help=("add this flag if you want to continue"
                              + " existing solution.\n Provide"
                              + " specific remote filename or the"
                              + " last one will be used. "))
    # partition to run on:
    parser.add_argument('-p', type=str, help="slurm partition")

    # also node:
    parser.add_argument('-w', type=str, help="slurm nodes")

    # also affinnity:
    parser.add_argument('-aff', type=str, help="GOMP_CPU_AFFINITY='?' ")

    # also mapby:
    parser.add_argument('-mpimap', type=str, help="mpirun --map-by argument")

    parser.add_argument('-nortpng',
                        help="add this flag to avoid runtime png creation",
                        action="store_true")
    parser.add_argument("-v", "--verbose", dest="verbose",
                        action="count", default=1,
                        help="set verbosity level [default: %(default)s]")
    desc = ("add this flag to use pre-generated cpp with"
            + " the same baseneame as .json")
    parser.add_argument('-nocppgen', help=desc, action="store_true")
    '''
    args = parser.parse_args()
    
    conn_name = args.conn_name
    modelFileName = args.projectFileName
    device_conf_name = args.device_conf_name
    paths_name = args.paths_name

    # make settings:
    model = Model()
    model.io.loadFromFile(modelFileName)

    settings = Settings(model, conn_name, device_conf_name, paths_name)

    finalParseAndRun(settings, model.dimension, model=model)


if __name__ == '__main__':
    
    run()
