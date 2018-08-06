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
        self.tracerFolder = (net.settings
                             .pathes['pathes_hs_base']['TracerFolder'])

        # where projects stored at server:
        self.projectDir = (self.net.settings
                           .pathes['hs']['out_folder'])
        # self.projectDir = (self.net.settings
        #                    .pathes['pathes_hs_base']['Workspace'])

        # title for postprocessing:
        self.title = self.net.settings.pathes['model']['name']

        # dom file at server:
        self.domFile = self.net.settings.pathes['hs']['dom_bin']

        self.solverExecutable = self.net.settings.pathes['hs']['solver']
        
        # postproc:
        self.postprocessor = self.net.settings.pathes['hs']['postproc']
        self.plot_params = self.net.settings.pathes['hs']['plot']

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

    def set_params(self, params):
        '''
        Set user's params.

        params can contain optional parameters:
        params['finish']
        params['cont']
        params['nortpng']
        params['partition']
        params['nodes']
        params['mpimap']
        params['affinity']
        
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

    def gen_sh(self, outputRunFile):
        '''
        Create sh file in outputRunFile.

        in this case we run only c mpi workers and then process results
        '''    
        logger.info("generating launcher script...")

        with open(outputRunFile, "w") as runFile:
            runFile.write("echo Welcome to generated kernel launcher!\n")

            runFile.write("export LD_LIBRARY_PATH=" + self.projectDir
                          + ":$LD_LIBRARY_PATH\n")

            # runFile.write("export OMP_NUM_THREADS=16\n")

            runFile.write("export GOMP_CPU_AFFINITY='"
                          + self.affinity + "'\n")

            runFile.write("salloc -N " + self.nodeCount
                          + " -n " + self.nodeCount
                          + " " + self.nodes + self.partition
                          + " mpirun " + self.mpimap
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

            runFile.write("srun -n1" + " " + self.nodes
                          + " " + self.partition
                          + " python " + self.postprocessor
                          + " " + self.projectDir+"/"
                          + " " + self.title
                          + " " + self.plot_params)
        runFile.close()
