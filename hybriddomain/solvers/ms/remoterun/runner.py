from hybriddomain.solvers.hs.remoterun.runner import Runner
from hybriddomain.solvers.hs.remoterun.progresses.progress_main import StdoutProgresses


class MSRunner(Runner):

    def run_preprocessor(self, settings, connection, paths,
                         workspace, dimension, notebook):
            
        client = self.client
        logger = self.logger
        
        logger.info('\nRunning solver:')

        hd_python = settings.device_conf["hd_python"]
        sn_model_path = paths[self.sn]['project_path_absolute']
        sn_out_folder = paths[self.sn]['out_folder']
        steps = settings.device_conf["steps"]

        'srun -n 1   -p all  --exclusive  /acchome/valdecar/anaconda3/envs/hd/bin/./python3 -u -c "import hybriddomain.solvers.ms.python.solver as ts; ts.run()" -model lab/hybriddomain/hybriddomain/gui/2d/web/model/data/physics/n-body/test0 -steps 4 -log_level debug -plot False'
        # " ~/anaconda3/bin/python3 "
        python_running_script = (
            '"import'
            + ' hybriddomain.solvers.ms.python.solver as ts;'
            + ' ts.run()"')
        command = ("srun -n 1 -p all --exclusive "
                   + hd_python + " "
                   + '-u '
                   + '-c ' + python_running_script
                   + ' -model ' + sn_out_folder
                   + ' -steps ' + steps
                   + ' -log_level info -plot False'
                   + " 2>&1")
        logger.info("command:")
        logger.info(command)
    
        stdin, stdout, stderr = client.exec_command(command)
        '''
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
        '''
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
 
    def run_solver(self, paths, notebook):
        pass
