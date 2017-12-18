# -*- coding: utf-8 -*-
'''
Модуль импортирует входной json
Создает по нему модель (включая и задачу, и мэппинг узлов-девайсов)
Создает бинарный файл с геометрией и свойствами области (*.dom)
Создает файл с функциями задачи (*.so)

Файл с состоянием не создается, т.к. у нас имеются функции, которые может вызвать ядро
для заполнения начальных значений


model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''


from domainmodel.enums import *
import argparse
from domainmodel.model import Model
from domainmodel.binarymodel import BinaryModel
from domainmodel.decomposer import partitionAndMap

from fileUtils import getSortedLoadBinFileList
import os


def createBinaries(params):

    projectDir = os.path.dirname(params["fileName"])
    inProjectName, _ = os.path.splitext(params["fileName"])
    if params["outFileName"] is None:
        outProjectTitle = os.path.basename(inProjectName)
    else:
        outProjectTitle = params["outFileName"]
    if inProjectName == '':
        print "Bad input file name"
        return

    OutputDomFile = os.path.join(projectDir, outProjectTitle) + ".dom"
    OutputFuncFile = os.path.join(projectDir, outProjectTitle) + ".cpp"
    OutputRunFile =  os.path.join(projectDir, outProjectTitle) + ".sh"
    OutputSpmdFile = os.path.join(projectDir, outProjectTitle) + ".spmd"

    #we want to find the last computed state to continue if user does not provide filename but tell us to continue
    print projectDir
    if params["cont"] is None:
        params["cont"] = "n_a"
    if params["cont"] == '/':
        try:
            params["cont"] = os.path.join(projectDir, getSortedLoadBinFileList(projectDir, outProjectTitle)[-1])
        except:
            print "No bin file to continue from!"
            return
  
    model = Model()
    model.loadFromFile(params["fileName"])
    
    print "\nMax derivative order is ", model.getMaxDerivOrder()
    
    #something not to be done here
    #model.delay_lst = model.determineDelay()
    #model.isdelay = bool(model.delay_lst)
    #print 'There is a delay?', model.isdelay
    #print 'Delays:', model.delay_lst, '\n'
   
    
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)
    
    bm = BinaryModel(partModel)
    delays = bm.saveFuncs(OutputFuncFile, params["tracerFolder"],params["nocppgen"])
    bm.saveDomain(OutputDomFile, delays)
    bm.compileFuncs(OutputFuncFile)
    
    print "jobID:", params["jobId"]

    bm.createCOnlyRunFile(OutputRunFile, projectDir, outProjectTitle, OutputDomFile, params)
    
    
                
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Processing json file on a remote cluster.', epilog = "Have fun!")
    #mandatory argument, json filename
    parser.add_argument('fileName', type = str, help = "local json file to process")
    parser.add_argument('tracerFolder', type = str, help = "Tracer Folder")
    
    #optional argument, unique job Id for identification in database 
    #if no id provided, db is not used and separate python mpi process is not included 
    parser.add_argument('-jobId', type = int, help = "unique job ID")

    #optional argument, exactly one float to override json finish time
    parser.add_argument('-finish', type=float, help = "new finish time to override json value")

    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    parser.add_argument('-outFileName', type = str, help="specify output project filename (fileName is default)")
    parser.add_argument('-nortpng', help="add this flag to avoid creating png in real time", action="store_true")
    parser.add_argument('-nocppgen', help="add this flag to avoid cpp generation", action="store_true")

    # partition to run on
    parser.add_argument('-p', type=str, help="slurm partition")
    # also node
    parser.add_argument('-w', type=str, help="slurm nodes")
    # also affinnity
    parser.add_argument('-aff', type=str, help="GOMP_CPU_AFFINITY='?' ")
    # also mapby
    parser.add_argument('-mpimap', type=str, help="mpirun --map-by argument")

    args = parser.parse_args()
  
    print "jsontobin input:", args


    params = {
        "fileName": args.fileName,
        "tracerFolder": args.tracerFolder,
        "jobId": args.jobId,
        "finish": args.finish,
        "cont": args.cont,
        "nortpng": args.nortpng,
        "outFileName": args.outFileName,
        "nocppgen": args.nocppgen,
        "partition": args.p,
        "nodes": args.w,
        "affinity": args.aff,
        "mpimap": args.mpimap
    }

    createBinaries(params)
