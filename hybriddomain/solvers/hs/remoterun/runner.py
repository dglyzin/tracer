from hybriddomain.solvers.hs.remoterun.progresses.progress_main import StdoutProgresses


class Runner():

    def __init__(self, den='hd', sn='hs'):
        
        # domain editor name:
        self.den = den

        # solver name
        self.sn = sn

    def set_logger(self, logger):
        self.logger = logger

    def set_client(self, client):
        self.client = client

    def run_preprocessor(self, settings, connection, paths,
                         workspace, dimention, notebook):

        client = self.client
        logger = self.logger
        hs_dev_conf_file = paths[self.sn]['device_conf_file']
        hs_project_folder = paths[self.sn]['project_path_absolute']
        hs_paths_file = paths[self.sn]['paths_file']

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
        logger.debug("hs_dev_conf_file:")
        logger.debug(hs_dev_conf_file)
        
        logger.debug("hs_dev_conf_file:")
        logger.debug(hs_dev_conf_file)
        
        hd_python = settings.device_conf["hd_python"]
        # " ~/anaconda3/bin/python3 "
        python_running_script = (
            '"import'
            + (' hybriddomain.gens.hs.tests.tests_gen_%dd as ts;'
               % dimention)
            + ' ts.run()"')
        command = (hd_python + " "
                   + '-c ' + python_running_script
                   + ' -t ' + hs_project_folder
                   + ' -d ' + hs_dev_conf_file
                   + ' -p ' + hs_paths_file
                   + ' -w ' + workspace
                   + ' -u ' + connection.username
                   + " 2>&1")
        '''
        # go to hs_hd dirrectory, show it
        # and run source generator:
        # (stderr to stdout)
        command = ("cd " + hs_hd + " &&"
                   + " pwd &&"
                   + (hd_python + " "
                      + ("-m gens.hs.tests.tests_gen_%dd"
                         % dimention))
                   + ' -t ' + hs_project_folder
                   + ' -d ' + settings.device_conf_rpath
                   + ' -p ' + settings.paths_rpath
                   + ' -w ' + workspace
                   + ' -u ' + connection.username
                   + " 2>&1")
        '''
        logger.info("command:")
        logger.info(command)

        stdin, stdout, stderr = client.exec_command(command)

        stdout_out = stdout.read()
        stderr_out = stderr.read()
        
        stdout_out = stdout_out.decode()
        stderr_out = stderr_out.decode()

        if ("error" in stdout_out or "Error" in stdout_out):
            logger.error("preprocessor errors:")
            logger.error(stdout_out)
            raise(BaseException("preprocessor error"))
        if ("error" in stderr_out or "Error" in stderr_out):
            logger.error("preprocessor errors:")
            logger.error(stderr_out)
            raise(BaseException("preprocessor error"))

        if notebook is None:
            logger.info("finally")

            logger.info("preprocessor stdout:")

            stdout_out = stdout_out.split("\n")
            for line in stdout_out:
                logger.info(line)
            logger.info("stdout END")

            stderr_out = stderr_out.split("\n")
            if len(stderr_out) > 0:
                logger.error("preprocessor stderr:")
                for line in stderr_out:
                    logger.error(line)
                logger.error("stderr END")
    
    def run_solver(self, paths, notebook):
        
        client = self.client
        logger = self.logger
    
        hs_solver = paths[self.sn]['solver']
        hs_sh = paths[self.sn]['sh']
    
        logger.info('\nRunning solver:')
        logger.debug("Checking if solver executable at "
                     + hs_solver
                     + " exists...")

        stdin, stdout, stderr = client.exec_command('test -f ' + hs_solver)
        if stdout.channel.recv_exit_status():
            logger.error("Please provide correct path to"
                         + " the solver executable.")
            return
        else:
            logger.debug("Solver executable found.")

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
                        or postproc in line)
                cond_error = ('error' in line or 'Error' in line
                              or 'errors' in line or 'Errors' in line)
                if cond_error:
                    logger.error("solver errors:")
                    logger.error(line)
                    raise(BaseException("solver error"))
                    
                if cond:
                    logger.info(line)
                    success = True
                    break
                else:
                    # print(line)
                    progress.show_stdout_progresses(line)
            except:
                logger.error("Wrong symbol")
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
            stdout_out = stdout_out.decode()

            if len(stdout_out) > 0:
                logger.info("stdout:")
                logger.info(stdout_out)
                logger.info("stdout END")
            # because \n stand with each word
            # in stdout, this code is not used:
            '''
            stdout_out = stdout.read()
            stdout_out = stdout_out.decode()

            stderr_out = stdout_out.split("\n")
            for line in stdout_out:
                logger.info(line)
            '''
            stderr_out = stderr_out.decode()
            if len(stderr_out) > 0:
                
                logger.error("stderr:")
                logger.error(stderr_out)
                logger.error("stderr END")
            # because \n stand with each word
            # in stdout, this code is not used:
            '''
            stderr_out = stderr.read()
            stderr_out = stderr_out.decode()

            stderr_out = stderr_out.split("\n")
            for line in stderr_out:
                logger.info(line)
            '''
 
