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

Command:

hd$ python3 -m solvers.hs.remoterun.remoterun \
conn_file_name device_conf_file_name paths_file_name \
test_folder_relative_name

where

   conn_file_name is name of conn file in conn folder

   paths_file_name is name of paths file in paths folder
      deffault is ``paths_hs_base``

   device_conf_file_name is name of device_conf file in
      device_conf folder.

   test_folder_relative_name relative to hd name of folder,
      model .json file stored to.
      (ex: ``problems/1dTests/test_folder``)
      
Ex (from hd)::

 # 1d:
 python3 -m solvers.hs.remoterun.remoterun conn_base default paths_hs_base problems/1dTests/logistic_delays

 # 2d one block:
 python3 -m solvers.hs.remoterun.remoterun conn_base default paths_hs_base problems/2dTests/heat_block_1

 # 2d two blocks ics:
 python3 -m solvers.hs.remoterun.remoterun conn_base ics_other paths_hs_base problems/2dTests/heat_block_2_ics_other

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


def create_folder(client, folder):

    logger.info("Checking if folder "+folder+" exists...")
    cmd = 'test -d ' + folder
    stdin, stdout, stderr = client.exec_command(cmd)
    if stdout.channel.recv_exit_status():

        stdin, stdout, stderr = (client
                                 .exec_command("mkdir %s"
                                               % folder))
        err = stderr.read()
        if len(err) > 0:
            logger.info(err)
            raise(BaseException(err))
        else:
            logger.info("created folder %s" % folder)
    else:
        logger.info("folder %s alredy exist" % folder)


def copy_files(client, connection, hd_path, hs_path, name):
    
    '''To server'''

    # fix tilde bug:
    # hs_path = fix_tilde_bug(connection, hs_path, 'hs', name)
    # hd_path = fix_tilde_bug(connection, hd_path, 'hd', name)

    cftp = client.open_sftp()
    walk_gen = os.walk(hd_path)
    logger.info("copy %s files:" % name)
    for root, folders_names, file_names in walk_gen:
        for file_name in file_names:
            if file_name[-1] != '~':
                hd_file_name_full = os.path.join(hd_path, file_name)
                hs_file_name_full = os.path.join(hs_path, file_name)
                logger.info("copy " + hd_file_name_full)
                logger.info("to " + hs_file_name_full)
                cftp.put(hd_file_name_full, hs_file_name_full)
    cftp.close()
    logger.info("finished copy %s files" % name)


def copy_file_to_folder(client, hd_file_name_full, hs_path, name):
    
    '''To server'''

    # fix tilde bug:
    # hs_path = fix_tilde_bug(connection, hs_path, 'hs', name)
    # hd_path = fix_tilde_bug(connection, hd_path, 'hd', name)

    file_name = os.path.basename(hd_file_name_full)
    hs_file_name_full = os.path.join(hs_path, file_name)
    logger.info("copy " + hd_file_name_full)
    logger.info("to " + hs_file_name_full)
    cftp = client.open_sftp()
    cftp.put(hd_file_name_full, hs_file_name_full)
    cftp.close()
    logger.info("finished copy %s files" % name)


def copy_file(client, hd_file_name_full, hs_file_name_full):
    '''To server'''
    cftp = client.open_sftp()
    # 1 copy json to hs:
    cftp.put(hd_file_name_full, hs_file_name_full)
    cftp.close()
    logger.info("file copied")


def make_problems_as_workspace_link(client, hs_problems, workspace):
    '''
    command = (('file="%s" && [[ -d $file && -L $file ]]'
                % hs_problems)
               + ' && echo True || echo False')
    logger.info("check link command:")
    logger.info(command)
    stdin, stdout, stderr = client.exec_command(command)

    err = stderr.read()
    out = stdout.read()
    logger.info("finally")
    logger.info(stdout.read())
    logger.info("problems is link check stderr:")
    logger.info(err)
    logger.info("stderr END")

    if len(err) > 0:
        return()
    else:
        if not eval(out):
    '''

    # remove problems folder
    command = 'rm -R %s' % hs_problems
    stdin, stdout, stderr = client.exec_command(command)
    err = stderr.read()
    if len(err) > 0:
        logger.error("rm err:")
        logger.error(err)
        raise(BaseException(err))

    # make problems folder symbolic link:
    command = 'ln -s %s %s' % (workspace, hs_problems)
    stdin, stdout, stderr = client.exec_command(command)
    err = stderr.read()
    if len(err) > 0:
        logger.error("ln err:")
        logger.error(err)
        raise(BaseException(err))
    logger.info("link created")


def remoteProjectRun(settings, dimention, notebook=None):
    '''
    Run hs with settings:
    1) Create folders at hs/workspace for model and settings
    2) Copy json files of model, device_conf, paths to hs
    3) Generate .sh, .cpp, .dom .so files for hs
    4) Run .sh
    5) Getting hs statuses and progress
       TODO: hs is running
    6) Getting back result (.mp3, .out)

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

    # FOR paths:
    paths = settings.paths
    connection = settings.connection
    workspace = paths['Workspace']
    # workspace = fix_tilde_bug(connection, workspace,
    #                           'hs', 'workspace')

    tracer_folder = paths['TracerFolder']
    # tracer_folder = fix_tilde_bug(connection, tracer_folder,
    #                               'hs', 'tracer_folder')

    project_name = paths['model']['name']
    project_path = paths['model']['path']
    logger.info("project_path")
    logger.info(project_path)
    hs_project_path_relative = paths['hs']['project_path_relative']
    project_path_folders = hs_project_path_relative.split(os.path.sep)

    hs_hd = paths['hs']['hd']
    # hs_hd = fix_tilde_bug(connection, hs_hd,
    #                       'hs', 'hd')

    hs_solver = paths['hs']['solver']

    hs_settings = paths['hs']['settings']
    
    hs_dev_conf = paths['hs']['device_conf']
    # hs_dev_conf = fix_tilde_bug(connection, hs_dev_conf,
    #                             'hs', 'dev_conf')

    hs_paths = paths['hs']['paths']

    hs_project_folder = paths['hs']['project_path_absolute']
    # hs_project_folder = fix_tilde_bug(connection, hs_project_folder,
    #                                   'hs', 'projects_folder')

    hs_out_folder = paths['hs']['out_folder']
    # hs_out_folder = fix_tilde_bug(connection, hs_out_folder,
    #                               'hs', 'out_folder')

    hs_json = paths['hs']['json']
    # hs_json = fix_tilde_bug(connection, hs_json, 'hs', 'json')

    hs_sh = paths['hs']['sh']
    # hs_sh = fix_tilde_bug(connection, hs_sh, 'hs', 'sh')

    hs_cpp = paths['hs']['cpp']
    # hs_cpp = fix_tilde_bug(connection, hs_cpp, 'hs', 'cpp')

    hd_dev_conf = paths['hd']['device_conf']
    hd_paths = paths['hd']['paths']

    hd_out_folder = paths['hd']['out_folder']
    hd_json = paths['hd']['json']
    # hd_json = fix_tilde_bug(connection, hd_json, 'hd', 'json')

    hd_cpp = paths['hd']['cpp']
    # hd_cpp = fix_tilde_bug(connection, hd_cpp, 'hd', 'cpp')

    # END FOR

    # FOR device_conf:
    device_conf = settings.device_conf
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

        # FOR creating/cleaning project folder
        logger.info("Creating/cleaning project folder: ")
        stdin, stdout, stderr = client.exec_command('test -d  '
                                                    + hs_project_folder)
        if stdout.channel.recv_exit_status():

            # create projects folder:
            tmp_project_folder = workspace
            for folder in project_path_folders:
                tmp_project_folder = os.path.join(tmp_project_folder, folder)
                create_folder(client, tmp_project_folder)

            # create out folder:
            create_folder(client, hs_out_folder)

            logger.info("projects folders created.")
        else:
            stdin, stdout, stderr = client.exec_command('test -d  '
                                                        + hs_out_folder)
            if stdout.channel.recv_exit_status():
                # create out folder:
                create_folder(client, hs_out_folder)
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
        # END FOR

        # FOR create settings folders:
        # create settings folders:
        logger.info("Creating settings folders: ")
        create_folder(client, hs_settings)
        create_folder(client, hs_paths)
        create_folder(client, hs_dev_conf)
        logger.info("settings folders created")
        # END FOR

        # FOR copy files:
        
        # 1 copy json to hs:
        logger.info("hd_json:")
        logger.info(hd_json)
        logger.info("hs_json:")
        logger.info(hs_json)
        copy_file(client, hd_json, hs_json)
        
        # 2 copy device_conf to hs:
        if settings.use_pf_prefix:
            copy_file_to_folder(client, hd_dev_conf, hs_dev_conf,
                                "dev_conf")
        else:
            copy_files(client, connection, hd_dev_conf, hs_dev_conf,
                       'dev_conf')

        # 2.1 copy paths to hs:
        if settings.use_pf_prefix:
            copy_file_to_folder(client, hd_paths, hs_paths, "paths")
        else:
            copy_files(client, connection, hd_paths, hs_paths, 'paths')
        # END FOR

        '''
        # 2.2 make problems folder link:
        hs_problems = os.path.join(hs_hd, 'problems')
        # hs_problems = fix_tilde_bug(connection, hs_problems,
        #                             'hs', 'problems')
        if not hs_problems == workspace:
            make_problems_as_workspace_link(client, hs_problems, workspace)
        else:
            create_folder(client, hs_problems)
        '''

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

        '''
        # move current directly to hd:
        command = "cd " + hs_hd
        client.exec_command(command)
        '''
        
        # go to hs_hd dirrectory, show it
        # and run source generator:
        command = ("cd " + hs_hd + " &&"
                   + " pwd &&"
                   + (" python3 "
                      + ("-m gens.hs.tests.tests_gen_%dd"
                         % dimention))
                   + ' -t ' + hs_project_folder
                   + ' -d ' + settings.device_conf_name
                   + ' -p ' + settings.paths_name
                   + ' -w ' + workspace
                   + ' -u ' + connection.username)

        '''
        command = ("cd " + hs_hd + " &&"
                   + " pwd &&"
                   + (" python3 "
                      + ("-m gens.hs.tests.tests_gen_%dd"
                         % dimention))
                   + ' -t ' + project_name
                   + ' -d ' + settings.device_conf_name)
        '''
        # command = command + optionalArgs
        logger.info("command:")
        logger.info(command)

        stdin, stdout, stderr = client.exec_command(command)

        stdout_out = stdout.read()
        stderr_out = stderr.read()
        
        if notebook is None:
            logger.info("finally")

            logger.info("jdontobin stdout:")

            stdout_out = stdout_out.decode()

            stdout_out = stdout_out.split("\n")
            for line in stdout_out:
                logger.info(line)
            logger.info("stdout END")

            logger.info("jsontobin stderr:")

            stderr_out = stderr_out.decode()

            stderr_out = stderr_out.split("\n")
            for line in stderr_out:
                logger.info(line)
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
        success = False
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
                    success = True
                    break
                else:
                    # print(line)
                    progress.show_stdout_progresses(line)
            except:
                logger.info("Wrong symbol")
                break

        if success:
            # progress.re_pattern = "(?P<val>[\d]+)\.png"
            progress.set_prefix("composing")
            for line in iter(lambda: stdout.readline(2048), ""):
                cond = ("Done" in line
                        or 'error' in line or 'Error' in line
                        or 'errors' in line or 'Errors' in line)
                progress.show_stdout_progresses(line)

                if "Creating" in line:
                    logger.info(line)
                
                if cond:
                    break


        stdout_out = stdout.read()
        stderr_out = stderr.read()
        
        if notebook is None:

            logger.info("stdout:")
            logger.info(stdout_out)

            # because \n stand with each word
            # in stdout, this code is not used:
            '''
            stdout_out = stdout.read()
            stdout_out = stdout_out.decode()

            stderr_out = stdout_out.split("\n")
            for line in stdout_out:
                logger.info(line)
            '''
            logger.info("stdout END")

            logger.info("stderr:")
            logger.info(stderr_out)

            # because \n stand with each word
            # in stdout, this code is not used:
            '''
            stderr_out = stderr.read()
            stderr_out = stderr_out.decode()

            stderr_out = stderr_out.split("\n")
            for line in stderr_out:
                logger.info(line)
            '''
            logger.info("stderr END")

        #get resulting files
        logger.info("Downloading results...")
        logger.info("from:")
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


def finalParseAndRun(settings, dimention):
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
    remoteProjectRun(settings, dimention, notebook=None)
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

    finalParseAndRun(settings, model.dimension)
