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

Ex (from hd):
python3 -m solvers.hs.remoterun.remoterun conn_base default problems/1dTests/logistic_delays

'''
#remoteRunScriptName='project.sh'
#remoteProjectFileName='project.json'
#remoteMp4Name = 'project.mp4'
from __future__ import print_function

import os
import socket
import paramiko
import argparse
import functools

from settings.settings_main import Settings
from envs.hs.model.model_main import ModelNet as Model

from solvers.hs.remoterun.progresses.progress_main import StdoutProgresses
from solvers.hs.remoterun.progresses.progress_cmd import progress_cmd

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.tester.gen_1d')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('remoterun')
logger.setLevel(level=log_level)

# paramiko.util.log_to_file(os.path.join(os.getcwd(), "tests", "paramiko.log"))


def remoteProjectRun(settings, notebook=None):
    '''
    Run hs with settings:
    1) Copy json files of model, device_conf to hs
    2) Create folders at hs for model
    3) Generate .sh, .cpp, .dom .so files for hs
    4) Run .sh
    5) Getting hs statuses and progress
       TODO: hs is running
    6) Getting back result (.mp3, .out)

    Inputs:

    - ``settings`` - Settings object, contained info about pathes
              device_conf and connection in.
                # make settings:
                settings = Settings()
                model = Model()
                model.io.loadFromFile(modelFileName)
                settings.make_all_pathes(model)
                settings.make_connection(name=conn_name)
                settings.set_device_conf(device_conf_name)

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
    
    :param device_conf_name: name of config file in settings/device_conf folder
    '''
    
    # prepare command line argumetnts for preprocessor
    optionalArgs = ''

    '''
    MOVED TO settings/device_conf/default.json
    if not (params["jobId"] is None):
        optionalArgs += " -jobId "+str(params["jobId"])
    
    if not (params["finish"] is None):
        optionalArgs += " -finish "+str(params["finishTime"])
    if params["continueEnabled"]:
        optionalArgs += " -cont"
        if params["continueFnameProvided"]:
            optionalArgs += " "+params["continueFileName"]
    if params["nortpng"]:
        optionalArgs += " -nortpng"

    if not (params["partition"] is None):
        optionalArgs += " -p "+str(params["partition"])
    if not (params["nodes"] is None):
        optionalArgs += " -w " + str(params["nodes"])
    if not (params["affinity"] is None):
        optionalArgs += " -aff " + str(params["affinity"])
    if not (params["mpimap"] is None):
        optionalArgs += " -mpimap " + str(params["mpimap"])
    '''

    # FOR pathes:
    pathes = settings.pathes
    connection = settings.connection
    workspace = pathes['pathes_hs_base']['Workspace']
    tracer_folder = pathes['pathes_hs_base']['TracerFolder']

    project_name = pathes['model']['name']

    hs_hd = pathes['hs']['hd']
    hs_solver = pathes['hs']['solver']

    hs_dev_conf = pathes['hs']['device_conf']

    hs_project_folder = pathes['hs']['project_path']
    hs_out_folder = pathes['hs']['out_folder']
    hs_json = pathes['hs']['json']
    hs_sh = pathes['hs']['sh']
    hs_cpp = pathes['hs']['cpp']

    hd_dev_conf = pathes['hd']['device_conf']

    hd_out_folder = pathes['hd']['out_folder']
    hd_json = pathes['hd']['json']
    hd_cpp = pathes['hd']['cpp']
    # END FOR

    # FOR device_conf:
    device_conf = settings.device_conf[settings.device_conf_name]
    # END FOR

    # get project file name without extension
    logger.info("project_name")
    logger.info(project_name)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # print conn.host, conn.username, passwd, conn.port
    try:
        client.connect(hostname=connection.host,
                       username=connection.username,
                       password=connection.password,
                       port=connection.port)

        logger.info("Checking if folder "+workspace+" exists...")
        cmd = 'test -d '+workspace
        stdin, stdout, stderr = client.exec_command(cmd)
        if stdout.channel.recv_exit_status():
            logger.info("Please create workspace folder and put hybriddomain"
                        + " preprocessor into it")
            return
        else:
            logger.info("Workspace OK.")

        logger.info("Creating/cleaning project folder: ")
        stdin, stdout, stderr = client.exec_command('test -d  '
                                                    + hs_project_folder)
        if stdout.channel.recv_exit_status():

            # create project folder:
            stdin, stdout, stderr = client.exec_command('mkdir  '
                                                        + hs_project_folder)

            # create out folder:
            stdin, stdout, stderr = client.exec_command('mkdir  '
                                                        + hs_out_folder)
            logger.info("Folders created.")
        else:
            stdin, stdout, stderr = client.exec_command('test -d  '
                                                        + hs_out_folder)
            if stdout.channel.recv_exit_status():
                # create out folder:
                stdin, stdout, stderr = client.exec_command('mkdir  '
                                                            + hs_out_folder)
                logger.info("out folder created inside project folder.")
            if ("cont" not in device_conf
                or ("cont" in device_conf
                    and device_conf["cont"] == "n_a")):
                cmd = 'rm -rf ' + hs_out_folder+'/*'
                stdin, stdout, stderr = client.exec_command(cmd)
                stdout.read()
                logger.info("Folder cleaned.")
            else:
                logger.info("Folder exists, no cleaning needed.")

                # now check if file to continue from exists
                if "continueFileName" in device_conf:
                    logger.info("Checking if file to continue from  ("
                                + device_conf["continueFileName"]
                                + ") exists...")
                    cmd = 'test -f '+device_conf["continueFileName"]
                    stdin, stdout, stderr = client.exec_command(cmd)

                    if stdout.channel.recv_exit_status():
                        logger.info("File not found, please specify existing"
                                    + " file to continue")
                        return
                    else:
                        logger.info("File OK.")

        # 1 copy json to hs:
        # fix paramiko bug:
        hs_json = hs_json.replace("~", "/home/" + connection.username)
        logger.info("hs_json fixed:")
        logger.info(hs_json)

        cftp = client.open_sftp()
        logger.info("hd_json:")
        logger.info(hd_json)

        cftp.put(hd_json, hs_json)
        cftp.close()

        # 2 copy device_conf to hs:
        # fix paramiko and walk bug:
        hs_dev_conf = hs_dev_conf.replace("~", "/home/" + connection.username)
        hd_dev_conf = hd_dev_conf.replace("~", "/home/" + connection.username)
        logger.info("hs_dev_conf fixed:")
        logger.info(hs_dev_conf)
        logger.info("hd_dev_conf fixed:")
        logger.info(hd_dev_conf)

        cftp = client.open_sftp()
        walk_gen = os.walk(hd_dev_conf)
        logger.info("copy device_conf files:")
        for root, folders_names, file_names in walk_gen:
            for file_name in file_names:
                if file_name[-1] != '~':
                    hd_file_name_full = os.path.join(hd_dev_conf, file_name)
                    hs_file_name_full = os.path.join(hs_dev_conf, file_name)
                    logger.info("copy " + hd_file_name_full)
                    logger.info("to " + hs_file_name_full)
                    cftp.put(hd_file_name_full, hs_file_name_full)
        cftp.close()
        logger.info("finished copy device_conf files")
        
        #3 Run preprocessor on json
        logger.info('\nRunning preprocessor:')
        
        '''
        if params["nocppgen"]:
            optionalArgs += ' -nocppgen'

            # also put cpp from local machine
            cftp = client.open_sftp()
            cftp.put(hd_cpp, hs_cpp)
            cftp.close()
        '''

        # fix paramiko bug:
        hs_hd = hs_hd.replace("~", "/home/" + connection.username)
        logger.info("hs_hd fixed:")
        logger.info(hs_hd)

        # fix paramiko and walk bug:
        hs_dev_conf = hs_dev_conf.replace("~", "/home/" + connection.username)
        logger.info("hs_dev_conf fixed:")
        logger.info(hs_dev_conf)

        '''
        # move current directly to hd:
        command = "cd " + hs_hd
        client.exec_command(command)
        '''

        # go to hs_hd dirrectory, show it
        # and run source generator:
        command = ("cd " + hs_hd + " &&"
                   + " pwd &&"
                   + " python3 " + "-m gens.hs.tests.tests_gen_1d"
                   + ' -t ' + project_name
                   + ' -d ' + settings.device_conf_name)

        # command = command + optionalArgs
        logger.info("command:")
        logger.info(command)
        stdin, stdout, stderr = client.exec_command(command)
        
        logger.info("finally")
        logger.info(stdout.read())
        logger.info("jsontobin stderr:")
        logger.info(stderr.read())
        logger.info("stderr END")

        #4 Run Solver binary on created files
        logger.info("Checking if solver executable at "
                    + hs_solver
                    + " exists...")

        stdin, stdout, stderr = client.exec_command('test -f ' + hs_solver)
        if stdout.channel.recv_exit_status():
            logger.info("Please provide correct path to"
                        + " the solver executable.")
            return
        else:
            logger.info("Solver executable found.")

        # stdin, stdout, stderr = client.exec_command('sh ' + hs_sh, get_pty=True)
        # redirect stderr to stdout (2>&1):
        stdin, stdout, stderr = client.exec_command('sh ' + hs_sh
                                                    + " 2>&1")
        progress = StdoutProgresses(notebook=notebook)
        for line in iter(lambda: stdout.readline(2048), ""):
            try:
                # show progress and key points:
                postproc = 'Creating pictures and a movie for a given folder.'
                cond = ("Performance" in line
                        or "Done!" in line
                        or postproc in line
                        or 'error' in line or 'Error' in line
                        or 'errors' in line or 'Errors' in line)
                if cond:
                    logger.info(line)
                else:
                    progress.show_stdout_progresses(line)
            except:
                logger.info("Wrong symbol")
        logger.info(stdout.read())
        logger.info(stderr.read())
        
        #get resulting files
        logger.info("Downloading results...")

        # fix paramiko bug:
        hs_out_folder = hs_out_folder.replace("~",
                                              "/home/" + connection.username)
        logger.info("hs_out_folder fixed:")
        logger.info(hs_out_folder)

        cftp = client.open_sftp()
        cftp.chdir(hs_out_folder)
        for filename in sorted(cftp.listdir()):
            if filename.endswith('mp4') or filename.endswith('out'):

                if notebook is None:
                    progress = functools.partial(progress_cmd, prefix=filename,
                                                 is_sleep=False)
                else:
                    progress = None
                if not os.path.exists(hd_out_folder):
                    os.makedirs(hd_out_folder)
                cftp.get(filename, os.path.join(hd_out_folder, filename),
                         callback=progress)
            
                # cftp.get(projFolder+"/"+remoteMp4Name, projectPathName+"-plot"+str(plotIdx)+".mp4")            
        cftp.close()
        logger.info("Done!")
        client.close()

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
    except BaseException as e:
        logger.error("base exception")
        logger.error(e)
        return()


def finalParseAndRun(settings):
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
    remoteProjectRun(settings, notebook=None)
    # remoteProjectRun(settings, params, notebook=None)
    # logger.clean()


if __name__ == '__main__':

    desc = 'Processing json file on a remote cluster.'
    parser = argparse.ArgumentParser(description=desc, epilog="Have fun!")
    parser.add_argument('conn_name', type=str,
                        help=("local json file name (without extension)"
                              + " from hybriddomain/settings/conn folder"))

    # device_conf:
    parser.add_argument('device_conf_name', type=str,
                        help=("name of json file in"
                              + " settings/device_conf folder"))

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

    # make settings:
    settings = Settings()
    model = Model()
    model.io.loadFromFile(modelFileName)
    settings.make_all_pathes(model)
    settings.make_connection(name=conn_name)
    settings.set_device_conf(device_conf_name)

    finalParseAndRun(settings)
