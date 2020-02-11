import os
import functools

from hybriddomain.solvers.hs.remoterun.progresses.progress_cmd import progress_cmd
from hybriddomain.solvers.hs.postproc.results.results_main import ResultPostprocNet as ResultPostproc


class IORoutine():
    
    def __init__(self, den='hd', sn='hs'):
        
        # domain editor name:
        self.den = den

        # solver name
        self.sn = sn

    def set_logger(self, logger):
        self.logger = logger

    def set_client(self, client):
        self.client = client

    def remove_old_results(self, paths):
        logger = self.logger

        hd_out_folder = paths[self.den]['out_folder']

        try:
            logger.debug("\nRemoving old results ...")
            for filename in sorted(os.listdir(hd_out_folder)):
                if filename.endswith('mp4') or filename.endswith('out'):
                    os.remove(os.path.join(hd_out_folder, filename))
            logger.debug("\nOld results removed")
        except:
            logger.debug("\nOld results removing error:"
                         + " probaply there was none.")

    def add_paths_to_model(self, paths, model):

        logger = self.logger

        hd_out_folder = paths[self.den]['out_folder']
    
        result_postproc = ResultPostproc("", hd_out_folder=hd_out_folder)
        result_postproc.get_results_filespaths(model)

        logger.info("\nPlots:")
        if "plots_paths" in dir(model):
            logger.info(model.plots_paths)
        else:
            logger.info("no model.plots_paths")

        logger.info("\nResults:")
        if "results_paths" in dir(model):
            logger.info(model.results_paths)
        else:
            logger.info("no model.results_paths")

    def get_resulting_files(self, paths, notebook):
    
        client = self.client
        logger = self.logger

        hd_out_folder = paths[self.den]['out_folder']
        hs_out_folder = paths[self.sn]['out_folder']
        
        logger.info("Downloading results...")
        logger.debug("from:")
        logger.debug(hs_out_folder)

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
            
                # cftp.get(projFolder+"/"+remoteMp4Name,
                #          projectPathName+"-plot"+str(plotIdx)+".mp4")
        cftp.close()
        logger.info("Done!")
        client.close()
        
    def create_common_folders(self, paths, device_conf):

        workspace = paths['Workspace']

        hs_project_folder = paths[self.sn]['project_path_absolute']
        hs_project_path_relative = paths[self.sn]['project_path_relative']
        hs_out_folder = paths[self.sn]['out_folder']

        self.create_main_folders(workspace,
                                 hs_project_folder, hs_project_path_relative,
                                 hs_out_folder, device_conf)

        hs_settings = paths[self.sn]['settings']
        hs_paths = paths[self.sn]['paths']
        hs_dev_conf = paths[self.sn]['device_conf']
        self.create_settings_folders(hs_settings, hs_paths, hs_dev_conf)

    def create_main_folders(self, workspace,
                            hs_project_folder, hs_project_path_relative,
                            hs_out_folder, device_conf):

        client = self.client
        logger = self.logger

        logger.debug("Checking if folder "+workspace+" exists...")
        cmd = 'test -d '+workspace
        stdin, stdout, stderr = client.exec_command(cmd)
        if stdout.channel.recv_exit_status():
            logger.error("Please create workspace folder and put hybriddomain"
                         + " preprocessor into it")
            return
        else:
            logger.debug("Workspace OK.")

        # FOR creating/cleaning project folder
        logger.debug("Creating/cleaning project folder: ")
        stdin, stdout, stderr = client.exec_command('test -d  '
                                                    + hs_project_folder)
        if stdout.channel.recv_exit_status():

            # create projects folder:
            tmp_project_folder = workspace
            project_path_folders = hs_project_path_relative.split(os.path.sep)

            for folder in project_path_folders:
                tmp_project_folder = os.path.join(tmp_project_folder, folder)
                self.create_folder(tmp_project_folder)

            # create out folder:
            self.create_folder(hs_out_folder)

            logger.debug("projects folders created.")
        else:
            stdin, stdout, stderr = client.exec_command('test -d  '
                                                        + hs_out_folder)
            if stdout.channel.recv_exit_status():
                # create out folder:
                self.create_folder(hs_out_folder)
                logger.debug("out folder created inside project folder.")
            if ("cont" not in device_conf
                or ("cont" in device_conf
                    and device_conf["cont"] == "n_a")):
                cmd = 'rm -rf ' + hs_out_folder+'/*'
                stdin, stdout, stderr = client.exec_command(cmd)
                logger.debug(hs_out_folder)
                logger.debug(stdout.read())
                logger.debug("Folder cleaned.")
            else:
                logger.debug("Folder exists, no cleaning needed.")

                # now check if file to continue from exists
                if "continueFileName" in device_conf:
                    logger.debug("Checking if file to continue from  ("
                                 + device_conf["continueFileName"]
                                 + ") exists...")
                    cmd = 'test -f '+device_conf["continueFileName"]
                    stdin, stdout, stderr = client.exec_command(cmd)

                    if stdout.channel.recv_exit_status():
                        logger.error("File not found, please specify existing"
                                     + " file to continue")
                        return
                    else:
                        logger.debug("File OK.")
        # END FOR

    def create_settings_folders(self, hs_settings, hs_paths, hs_dev_conf):

        client = self.client
        logger = self.logger

        # FOR create settings folders:
        # create settings folders:
        logger.debug("Creating settings folders: ")
        self.create_folder(hs_settings)
        self.create_folder(hs_paths)
        self.create_folder(hs_dev_conf)
        logger.debug("settings folders created")
        # END FOR

    def copy_model_files(self, paths):
        
        logger = self.logger

        # 1 copy json to hs:
        hd_json = paths[self.den]['json']
        hs_json = paths[self.sn]['json']

        logger.debug("hd_json:")
        logger.debug(hd_json)
        logger.debug("hs_json:")
        logger.debug(hs_json)
        self.copy_file(hd_json, hs_json)

    def copy_common_files(self, paths):

        logger = self.logger
        hd_dev_conf = paths[self.den]['device_conf']
        hs_dev_conf = paths[self.sn]['device_conf']
        hd_paths = paths[self.den]['paths']
        hd_paths = paths[self.den]['paths']
        hs_paths = paths[self.sn]['paths']

        # 2 copy device_conf to hs:
        # if settings.use_pf_prefix:
        logger.debug("hd_dev_conf:")
        logger.debug(hd_dev_conf)
        logger.debug("hs_dev_conf:")
        logger.debug(hs_dev_conf)
        self.copy_file_to_folder(hd_dev_conf, hs_dev_conf,
                                 "dev_conf")
        # else:
        #     copy_files(client, connection, hd_dev_conf, hs_dev_conf,
        #                'dev_conf')

        # 2.1 copy paths to hs:
        # if settings.use_pf_prefix:
        logger.debug("hd_paths:")
        logger.debug(hd_paths)
        logger.debug("hs_paths:")
        logger.debug(hs_paths)
        self.copy_file_to_folder(hd_paths, hs_paths, "paths")
        # else:
        # copy_files(client, connection, hd_paths, hs_paths, 'paths')
        '''
        # 2.2 make problems folder link:
        hs_problems = os.path.join(hs_hd, 'problems')
        # hs_problems = fix_tilde_bug(connection, hs_problems,
        #                             self.sn, 'problems')
        if not hs_problems == workspace:
            make_problems_as_workspace_link(client, hs_problems, workspace)
        else:
            create_folder(client, hs_problems)
        '''

    def create_folder(self, folder):
        client = self.client
        logger = self.logger

        logger.debug("Checking if folder "+folder+" exists...")
        cmd = 'test -d ' + folder
        stdin, stdout, stderr = client.exec_command(cmd)
        if stdout.channel.recv_exit_status():

            stdin, stdout, stderr = (client
                                     .exec_command("mkdir %s"
                                                   % folder))
            err = stderr.read()
            if len(err) > 0:
                logger.error(err)
                raise(BaseException(err))
            else:
                logger.info("created folder %s" % folder)
        else:
            logger.debug("folder %s alredy exist" % folder)

    def copy_files(self, hd_path, hs_path, name):
    
        '''To server'''

        client = self.client
        logger = self.logger

        # fix tilde bug:
        # hs_path = fix_tilde_bug(connection, hs_path, self.sn, name)
        # hd_path = fix_tilde_bug(connection, hd_path, self.den, name)

        cftp = client.open_sftp()
        walk_gen = os.walk(hd_path)
        logger.debug("copy %s files:" % name)
        for root, folders_names, file_names in walk_gen:
            for file_name in file_names:
                if file_name[-1] != '~' and "checkpoint" not in file_name:
                    hd_file_name_full = os.path.join(hd_path, file_name)
                    hs_file_name_full = os.path.join(hs_path, file_name)
                    logger.debug("copy " + hd_file_name_full)
                    logger.debug("to " + hs_file_name_full)
                    cftp.put(hd_file_name_full, hs_file_name_full)
        cftp.close()
        logger.debug("finished copy %s files" % name)

    def copy_file_to_folder(self, hd_file_name_full, hs_path, name):

        '''To server'''
    
        client = self.client
        logger = self.logger

        # fix tilde bug:
        # hs_path = fix_tilde_bug(connection, hs_path, self.sn, name)
        # hd_path = fix_tilde_bug(connection, hd_path, self.den, name)

        file_name = os.path.basename(hd_file_name_full)
        hs_file_name_full = os.path.join(hs_path, file_name)
        logger.debug("copy " + hd_file_name_full)
        logger.debug("to " + hs_file_name_full)
        cftp = client.open_sftp()
        cftp.put(hd_file_name_full, hs_file_name_full)
        cftp.close()
        logger.debug("finished copy %s files" % name)

    def copy_file(self, hd_file_name_full, hs_file_name_full):
        '''To server'''
        
        client = self.client
        logger = self.logger

        cftp = client.open_sftp()
        # 1 copy json to hs:
        cftp.put(hd_file_name_full, hs_file_name_full)
        cftp.close()
        logger.debug("file copied")

    def make_problems_as_workspace_link(self, hs_problems, workspace):

        client = self.client
        logger = self.logger

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
        logger.debug("link created")

