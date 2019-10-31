from hybriddomain.solvers.hs.postproc.utils.fileUtils import getSortedLoadBinFileList

import os

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.gen_sh')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('blocks_filler_1d')
logger.setLevel(level=log_level)
'''


class GenSH():

    '''
    Generate sh file.
    '''

    def __init__(self, net):
        
        self.net = net

        # where hybridsolver at server:
        self.tracerFolder = (net.settings.paths['TracerFolder'])

        # where projects stored at server:
        self.projectDir = (self.net.settings
                           .paths['hs']['out_folder'])
        # self.projectDir = (self.net.settings
        #                    .paths['Workspace'])

        # title for postprocessing and cont:
        self.title = self.net.settings.paths['model']['name']

        # dom file at server:
        self.domFile = self.net.settings.paths['hs']['dom_bin']

        self.solverExecutable = self.net.settings.paths['hs']['solver']
        
        # postproc:
        python_running_script = ("import hybriddomain.solvers"
                                 + ".hs.postproc.video.postprocessor as ps;"
                                 + " ps.run()")
        self.postprocessor = " -c " + '"' + python_running_script + '"'
        # self.postprocessor = self.net.settings.paths['hs']['postproc']
        self.plot_params = self.net.settings.paths['hs']['plot']

    def set_params_default(self):
        self.flag = '0'
        self.finishTime = '-1.1'
        self.cont = 'n_a'
        self.nortpng = None
        self.partition = ""
        self.nodes = self.net.model.device.getNodeSpec()
        self.mpimap = ''
        self.affinity = '0-15'

        self.nodeCount = str(self.net.model.device.getNodeCount())
        self.taskCountPerNode = "1"

        self.hd_python = "python3"
        self.exclusive = ""

    def set_params(self, params):
        '''
        Set user's params.

        params can contain optional parameters::

           params['finish']
           params['cont']
           params['taskCountPerNode']
           params['nortpng']
           params['partition']
           params['nodes']
           params['mpimap']
           params['affinity']
           params['hs_python']
        
        if some missing, default values will be used.
        '''
        # set base params:
        self.set_params_default()

        # refill base params:
        flag = 0

        if "finish" in params.keys():
            flag += 1
            self.finishTime = params["finish"]
        else:
            self.finishTime = str(-1.1)

        if "cont" in params.keys():
            flag += 2
            if params["cont"] == '/':
                try:
                    last = getSortedLoadBinFileList(self.projectDir,
                                                    self.title)[-1]
                    params["cont"] = os.path.join(self.projectDir, last)
                except:
                    raise(BaseException("No bin file to continue from!"))

            self.cont = params["cont"]
        else:
            params["cont"] = "n_a"
        
        if "nortpng" in params.keys():
            flag += 4
            self.nortpng = params["nortpng"]
        else:
            self.nortpng = ""
        self.flag = str(flag)

        self.nodeCount = str(self.net.model.device.getNodeCount())
        
        if "taskCountPerNode" in params.keys():
            self.taskCountPerNode = params["taskCountPerNode"]
        else:
            self.taskCountPerNode = "1"

        if "partition" in params.keys():
            if params["partition"] == '':
                self.partition = ""
            else:
                self.partition = " -p " + params["partition"] + " "
        else:
            self.partition = " "

        if "nodes" in params.keys():
            self.nodes = "-w "+params["nodes"]
        else:
            self.nodes = self.net.model.device.getNodeSpec()

        if not ("mpimap" in params.keys()):
            self.mpimap = ''
        elif params["mpimap"] == '/':
            self.mpimap = '--map-by ppr:1:node:pe=16'
        elif params["mpimap"] == '':
            self.mpimap = ''
        else:
            self.mpimap = '--map-by ' + params["mpimap"]

        if "affinity" in params.keys():
            self.affinity = params["affinity"]
        else:
            self.affinity = '0-15'

        if "hs_python" in params.keys():
            self.hs_python = params["hs_python"]

        if "exclusive" in params.keys():
            if params["exclusive"]:
                self.exclusive = "--exclusive"

    def gen_sh(self, outputRunFile):
        '''
        Create sh file in ``outputRunFile``.

        in this case we run only c mpi workers and then process results
        '''    
        logger.info("generating launcher script...")

        with open(outputRunFile, "w") as runFile:
            runFile.write("echo Welcome to generated kernel launcher!\n")

            runFile.write("export LD_LIBRARY_PATH=" + self.projectDir
                          + ":$LD_LIBRARY_PATH\n")

            # runFile.write("export OMP_NUM_THREADS=16\n")

            #runFile.write("export GOMP_CPU_AFFINITY='"
            #              + self.affinity + "'\n")

            runFile.write("srun -N " + self.nodeCount
                          + " -n " + self.taskCountPerNode
                          + " " + self.nodes + self.partition
                          + " " + self.exclusive
                          #+ " mpirun " + self.mpimap
                          + " " + self.solverExecutable
                          + " " + self.domFile
                          + " " + self.flag
                          + " " + self.finishTime
                          + " " + self.cont + "\n")
            '''
            runFile.write("srun -N "+str(nodeCount) + " " + partitionOption
                          + " " + solverExecutable+" "+DomFileName
                          + " " +str(flag)
                          + " " + str(finishTime)+" "+continueFileName+"\n")
            '''

            hs_python = self.hs_python
            # "~/anaconda3/bin/python3 "

            runFile.write("srun -n 1" + " " + self.nodes
                          + " " + self.partition
                          + " " + self.exclusive
                          + " " + hs_python + " " + self.postprocessor
                          + " " + self.projectDir+"/"
                          + " " + self.title
                          + " " + self.plot_params)
        runFile.close()
