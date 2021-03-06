# -*- coding: utf-8 -*-
'''
один входной аргумент - json файл, для которого уже выполнены расчеты
рядом с этим файлом будет создана папка с такимо же именем, в которую
будут закачаны все вычисления, после чего будет для каждого файла
нарисована картинка, а затем все склеено в видеофайл.
'''

import argparse
import numpy as np
import sys
import subprocess
import functools

import getpass
# import paramiko, socket
import os
from os import listdir
import json

import multiprocessing as mp
from multiprocessing import Pool

import time

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm

import math

from collections import OrderedDict

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.postproc.video')

# if using directly uncoment that:
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('postproc.video')
logger.setLevel(level=log_level)

import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

folder = "video"
sourcedir = currentdir.split(folder)[0]
logger.info("postproc dir:")
logger.info(sourcedir)
if sourcedir not in sys.path:
    sys.path += [sourcedir]

# from domainmodel.model import Model

from utils.fileUtils import getSortedDrawBinFileList
from utils.fileUtils import drawExtension
from utils.fileUtils import defaultGeomExt
from utils.fileUtils import getPlotValList

from utils.binaryFileReader import readBinFile 
from utils.binaryFileReader import readDomFile
from utils.binaryFileReader import getDomainProperties

from mpl_toolkits.axes_grid1 import make_axes_locatable


class Params(dict):

    def has_param(self, key, source):
        try:
            self[key]
        except KeyError:
            raise(KeyError('for term %s dont have %s param' % (source, key)))
            

def calcMinMax(projectDir, binFileList, info,
               countZ, countY, countX,
               offsetZ, offsetY, offsetX,
               cellSize, block_idx):
    maxValue = []  # sys.float_info.min
    minValue = []  # sys.float_info.max

    for i in range(cellSize):
        maxValue.append(sys.float_info.min)
        minValue.append(sys.float_info.max)

    for idx, binFile in enumerate(binFileList):
        data = readBinFile(projectDir+"/"+binFile, info,
                           countZ, countY, countX,
                           offsetZ, offsetY, offsetX,
                           cellSize, block_idx)

        for i in range(cellSize):
            tmp = data[0, :, :, i]

            tmpMaxValue = np.max(tmp)
            tmpMinValue = np.min(tmp)

            if tmpMaxValue > maxValue[i]:
                maxValue[i] = tmpMaxValue

            if tmpMinValue < minValue[i]:
                minValue[i] = tmpMinValue

    for i in range(cellSize):
        if (maxValue[i] - minValue[i]) < 1e-300:
            maxValue[i] = maxValue[i] + 1
            minValue[i] = minValue[i] - 1

    logger.info(maxValue)
    logger.info(minValue)

    return maxValue, minValue


def savePng1D(filename, X, data, maxValue, minValue, currentTime, cellSize):

    '''Will place several images for each
    equation in system (cellSize) at same
    figure (same .png file)'''

    figure = Figure()
    canvas = FigureCanvas(figure)

    t = str(currentTime)

    row = round(math.sqrt(cellSize))
    column = math.ceil(cellSize / row)

    figure.suptitle(t)
    print("cellSize:")
    print(cellSize)
    print("maxValue:")
    print(maxValue)
    print("minValue:")
    print(minValue)

    for i in range(cellSize):
        m = 100 * row + 10 * column + i + 1
        axes = figure.add_subplot(m)
        # figure.subplots_adjust(right=0.8)
        # cbaxes = figure.add_axes([0.85, 0.15, 0.05, 0.5])

        cmap = cm.jet

        
        amp = maxValue[i] - minValue[i]

        minV = minValue[i] - amp/10
        maxV = maxValue[i] + amp/10

        layer = data[i]
        axes.set_ylim(minV, maxV)
        axes.set_xlim(X.min(), X.max())
        # axes.axis([X.min(), X.max(), minValue, maxValue])
        # a = np.arange(X.min(), X.max(), (X.max() - X.min()) / layer.size)
        # logger.info(a.size, layer.size)
        axes.plot(X, layer)

        # cb = axes.pcolormesh(X, Y, layer, vmin=minValue[i], vmax=maxValue[i])
        # axes.axis([X.min(), X.max(), minValue, maxValue])
        # figure.colorbar(cb, cax=cbaxes)

    ###
    canvas.draw()
    figure.savefig(filename, format='png')
    figure.clear()


def savePng2D(filename, X, Y, data, maxValue, minValue, currentTime, cellSize):

    '''Will place several images for each
    equation in system (cellSize) at same
    figure (same .png file)'''

    figure = Figure()
    canvas = FigureCanvas(figure)

    t = str(currentTime)

    row = round(math.sqrt(cellSize))
    column = math.ceil(cellSize / row)

    figure.suptitle(t)

    for i in range(cellSize):
        m = 100 * row + 10 * column + i + 1
        axes = figure.add_subplot(m)
        figure.subplots_adjust(right=0.8)
        # cbaxes = figure.add_axes([0.85, 0.15, 0.05, 0.5])

        cmap = cm.jet

        layer = data[i]
        # layer = data[0, :, :, i]

        cb = axes.pcolormesh(X, Y, layer, vmin=minValue[i], vmax=maxValue[i])

        axes.axis([X.min(), X.max(), Y.min(), Y.max()])
        axes.set_aspect('equal')
        figure.colorbar(cb, ax=axes, fraction=0.046, pad=0.04)

    ###
    if cellSize > 1:
        figure.tight_layout()

    canvas.draw()
    figure.savefig(filename, format='png')
    figure.clear()


def saveTxt2D(filename, X, Y, data, maxValue, minValue, currentTime, cellSize):
    txtFile = open(filename, "w")

    t = str(currentTime)

    _, m, n, _ = data.shape

    line = "Y X values \n"

    txtFile.write(line)

    for i in range(m):
        for j in range(n):
            line = "{0} {1} ".format(str(Y[i, j]), str(X[i, j]))
            for k in range(cellSize):
                line = line + str(data[0, i, j, k]) + " "
            line = line+"\n"
            txtFile.write(line)
    txtFile.close()


def savePlots1D(projectDir, projectName, data, t,
                countZ, countY, countX,
                offsetZ, offsetY, offsetX,
                cellSize, maxValue, minValue,
                dx, dy, postfix, percent, plotIdx):
    # for idx, binFile in enumerate(binFileList):
    # data = readBinFile(projectDir+"/"+binFile, info,
    #                    countZ, countY, countX,
    #                    offsetZ, offsetY, offsetX,
    #                    cellSize)
    xs = np.arange(0, countX)*dx
    # dictfun = {}
    # for numitem, item in enumerate(namesEquations):
    #     dictfun[item] = data[0, 0, :, numitem]

    filename = os.path.join(projectDir, (projectName+"-plot"
                                         + str(plotIdx) + str(postfix) + ".png"))
    savePng1D(filename, xs, data, maxValue, minValue, t, cellSize)
    # logger.info("produced png: "+ filename)
    # return "produced png: " + filename
    return("produced png: " + percent)


def savePlots2D(projectDir, projectName, data, t,
                countZ, countY, countX,
                offsetZ, offsetY, offsetX,
                cellSize, maxValue, minValue,
                dx, dy, postfix, percent, plotIdx):
    '''
    # for idx, binFile in enumerate(binFileList):
    data = readBinFile(projectDir+"/"+binFile, info,
                       countZ, countY, countX, offsetZ, offsetY, offsetX,
                       cellSize)
    '''
    xs = np.arange(0, countX)*dx
    ys = np.arange(0, countY)*dy

    X, Y = np.meshgrid(xs, ys)

    # plt.pcolormesh(X, Y, layer, vmin=minValue, vmax=maxValue)
    # plt.colorbar()

    # TODO 1: separate plotIdx from postfix:
    filename = os.path.join(projectDir, (projectName+"-plot"
                                         + str(plotIdx)+str(postfix) + ".png"))
    # plt.savefig(filename, format='png')
    # logger.info 'save #', idx, binFile, "->", filename
    # plt.clf()

    # t = binFile.split("-")[1]
    # equal to
    # t = binFile.split("-")[1]
    # Ex (binFile): heat_block_0-0.05300000-2.dbin
    # t = t.split(drawExtension)[0]

    savePng2D(filename, X, Y, data, maxValue, minValue, t, cellSize)
    # if saveText:
    #    filenameTxt = projectDir+projectName+"-txtFile-" + str(idx) + ".txt"
    #    saveTxt2D(filenameTxt, X, Y, data, maxValue, minValue, t, cellSize)

    # logger.info("produced png: "+ filename)
    return("produced png: " + percent)
    # return "produced png: " + filename


def getResults(projectDir, projectName, binFile,
               info, dimension,
               countZ, countY, countX,
               offsetZ, offsetY, offsetX,
               cellSize, nameEquations, resultExpression,
               block_idx):
    '''
        returns time and requested value from state file binfile
    '''
    # dictfunc = {u'U':0, u'V':1}
    data = readBinFile(projectDir + "/" + binFile, info,
                       countZ, countY, countX,
                       offsetZ, offsetY, offsetX,
                       cellSize, block_idx)

    # xs = np.arange(0, countX)*dx
    # U -> data
    dictfun = {}
    for numitem, item in enumerate(nameEquations):
        if dimension == 1:
            dictfun[item] = data[0, 0, :, numitem]
        elif dimension == 2:
            dictfun[item] = data[0, :, :, numitem]
    # if countfun in dictfunc:
    #    idx = dictfunc[countfun]
    # else:
    #    idx = 0
    # res = data[0,0,:,idx]
    # res = dictfun[countfun]
    res = eval(resultExpression, dictfun)
    # filename = os.path.join(projectDir, (projectName+"-res"
    #                                      + str(resIdx) + postfix + ".txt"))

    t = binFile.split("-")[-2]

    # t = t.split(drawExtension)[0]
    # with open(filename, "w") as f:
    #    f.write(t)
    # savePng1D(filename, xs, data, maxValue, minValue, t, cellSize)
    # logger.info("produced png: "+ filename)
    return t, res  # "produced text result: "+ filename


def wGetResults(args):
    return(getResults(*args))


def wSavePlots1D(args):
    return(savePlots1D(*args))


def wSavePlots2D(args):
    return(savePlots2D(*args))


def createResultFile(projectDir, projectName, resIdx, resLog):
    logger.info("Creating out file: %s" % (str(resIdx)))

    outfileNamePath = projectDir+projectName+"-res"+str(resIdx)+".out"

    # for removing truncation (like: [1, ..., 3]):
    np.set_printoptions(threshold=np.inf)

    with open(outfileNamePath, "w") as f:
        for _time, item in resLog:
            f.write(str(_time)+": " + str(item)+"\n")

    # infileNamePath  = (projectDir+projectName+"-plot"
    #                    +str(resIdx)+"-final-%d.png")

    # PIPE = subprocess.PIPE
    # proc = subprocess.Popen(command, shell=True, stdin=PIPE,
    #                         stdout=PIPE, stderr=subprocess.STDOUT)
    # proc.wait()
    # subprocess.call(command, shell=True)
    # logger.info("Done")


def createVideoFile(projectDir, projectName, plotIdx):
    logger.info("Creating video file: %s" % (str(plotIdx)))
    # TODO 2: separate plotIdx from postfix:
    command = ("avconv -r 5 -loglevel panic -i "+projectDir+projectName
               + "-plot"+str(plotIdx)+"%d.png -b:v 1000k "
               + projectDir+projectName+"-plot"+str(plotIdx)+".mp4")
    logger.info(command)
    # PIPE = subprocess.PIPE
    # proc = subprocess.Popen(command, shell=True, stdin=PIPE,
    #                         stdout=PIPE, stderr=subprocess.STDOUT)
    # proc.wait()
    subprocess.call(command, shell=True)
    # logger.info("Done")


def plot_contains(idx, val):
    plotcode = 1 << (idx+1)
    return(val & plotcode)


def getBinFilesByPlot(binFileList, plotValList, plotCount):

    '''separate binFileList into sublists according to plotValList'''
    '''binFileList - binary files names
    plotValList - list of integers (62)
                  whose binary representation (111110)
                  contain info about data, that stored in
                  given binary file (plot with indexes: 0, 1, 2, 3, 4
                  because bin(2**(i+1)) & 111110 is true for i in [0-4]).'''
    '''    
    step 1):
       transform all plotValList into binary
       plotFileLists |-> [bin(plotVal) for plotVal in plotFileLists]
       Ex: [9] |-> [1001]

    step 2):
       transform range(plotCount) into binary
       plotCount |-> [bin(2**(plotVal+1)) for plotVal in range(plotCount)]
       Ex: [0, 1, 2] |-> [10, 100, 1000]

    step 3): compare each bit of bin(plotVar) with corresponding bit from
             step 1 (i.e. use bitwise and: &)
       out(step 1) as os_1, out(step 2) as os_2 |->
          [[bool(out_1 & out_2)
            for out_2 in os_2] for out_1 in os_1]
       Ex:
          [1001], [10, 100, 1000] |->
            [[False, False, True]]

    step 3): factorize images names into plotCount classes
       binFileList, range(plotCount), out(step 3) as os_3|->
          result[plotIdx] = [fileName
                             for fileName in binFileList
                              if os_3[plotVarIndex][plotIdx] == True]
            where plotIdx from range(plotCount)
                  plotVarIndex = index(plotFileLists) = index(binFileList)
       Ex:
          ['file_1'], [0, 1, 2], [[False, True, False]] |->
             [0: [], 1: [], 2: ['file_1']]
    '''

    result = []
    for _ in range(plotCount):
        result.append([])
    for fileName, plotVal in zip(binFileList, plotValList):
        for plotIdx in range(plotCount):
            if plot_contains(plotIdx, plotVal):
                result[plotIdx].append(fileName)
    return result


def createMovie(projectDir, projectName, modelParamsPath):
    '''
    projectDir: ~/projects/lab/hybriddomain/problems/1dTests/
                 two_blocks0_delays/out/
    projectName: two_blocks0_delays
    modelParamsPath: ~/projects/lab/hybriddomain/problems/1dTests/
                      two_blocks0_delays/out/params_plot.txt
    '''
    saveText = False

    path = os.path.join(projectDir, projectName + defaultGeomExt)
    logger.info("path")
    logger.info(path)
    info, cellSize, dx, dy, dz, dimension = readDomFile(path)

    command = ("rm " + projectDir + projectName + "-final-*.png "
               + projectDir + projectName + "-plot*.mp4 " + projectDir
               + projectName + "-res*.txt " + projectDir
               + projectName + "-res*.out")
    logger.info("command")
    logger.info(command)
    subprocess.call(command, shell=True)

    # list with file names:
    binFileList = getSortedDrawBinFileList(projectDir, projectName)

    # list of values each binary representation
    # of which contain info about file content:
    # (see getBinFilesByPlot)
    plotValList = getPlotValList(binFileList)

    # model params:
    mParams = get_model_params(modelParamsPath)

    pCount = mParams['plotCount']
    # pCount = len(info)
    rCount = mParams['resCount']
    oCount = pCount + rCount
    # pCount = mParams['plotCount'] + mParams['resCount']

    # factorize images into pCount classes:
    plotFileLists = getBinFilesByPlot(binFileList, plotValList, oCount)
                                      
    logger.debug('len(binFileList):')
    logger.debug(len(binFileList))
    logger.debug('len(plotValList):')
    logger.debug(len(plotValList))
    logger.debug("len(plotFileLists):")
    logger.debug(len(plotFileLists))

    equations_str = ("\n".join(mParams["namesEquations"])
                     if len(mParams["namesEquations"]) <= 3
                     else ("system with %s equations"
                           % (str(len(mParams["namesEquations"])))))

    for numitem, item in enumerate(mParams['namesEquations']):
        mParams['namesEquations'][numitem] = item[:item.find("'")]
    # logger.info(plotFileLists)
    # plotList = model.plots

    for plotIdx in range(pCount):
        # for plotIdx, plot in enumerate(mParams['plotList']):
        # t1 = time.time()
        block_idx = plotIdx
        
        out = getDomainProperties(info, block_idx)
        countZ, countY, countX, offsetZ, offsetY, offsetX = out
        
        plot = mParams['plotList'][plotIdx]
        '''
        maxValue, minValue = calcMinMax(projectDir, plotFileLists[plotIdx],
                                        info, countZ, countY, countX,
                                        offsetZ, offsetY, offsetX,
                                        cellSize, block_idx)
        '''
        # t2 = time.time()
        # logger.info("Расчет минимума / максимума: ", t2 - t1)
        plotType = type(plot['Value'])
        logger.info('plot["Value"]')
        logger.info(plot['Value'])
        logger.info(type(plot['Value']))
        pool = mp.Pool(processes=16)
        # saveResultFunc = savePlots1D
        if dimension == 1:
            saveResultFunc = wSavePlots1D  # savePlots1D
        if dimension == 2:
            saveResultFunc = wSavePlots2D
        if plotType == str:
            logger.info("Creating images for block %s value %s"
                        % (str(block_idx), plot["Value"]))
            # TODO: this code is particular case of plotType == list
            # with plotList = ['U'] and can be removed
            arg_list = [(projectDir, projectName, binFile,
                         info, dimension,
                         countZ, countY, countX,
                         offsetZ, offsetY, offsetX,
                         cellSize, mParams['namesEquations'],
                         plot['Value'], block_idx)
                        for idx, binFile in enumerate(plotFileLists[plotIdx])]
            logData = pool.map(wGetResults, arg_list)

            dataListMin = [min([i[1].min() for i in logData])]
            dataListMax = [max([i[1].max() for i in logData])]
            logger.info('min:')
            logger.info(dataListMin)
            # picCount = 1
            total_time = logData[-1][0]
            logger.info("total_time:")
            logger.info(total_time)

            arg_list = [(projectDir, projectName,
                         [dataNum[1]],
                         
                         # title:
                         (equations_str+"\n"+plot["Value"]
                          + " "+str(dataNum[0])),

                         countZ, countY, countX,
                         offsetZ, offsetY, offsetX,
                         cellSize,
                         dataListMax, dataListMin, dx, dy, Idx,
                         ("-"+str(int(float(dataNum[0])/float(total_time)*100))
                          + "% "+str(dataNum[0])+" "+str(total_time)),
                         block_idx)
                        for Idx, dataNum in enumerate(logData)]
            log = pool.map(saveResultFunc, arg_list)

        if plotType == list:
            logger.info('ЛИСТ! Ы')
            logData = []
            logger.info("plot[value]:")
            logger.info(plot["Value"])
            for elemPlot in plot["Value"]:
                logger.info("Creating images for block %s value %s"
                            % (str(block_idx), elemPlot))

                arg_list = [(projectDir, projectName,
                             binFile, info, dimension,
                             countZ, countY, countX,
                             offsetZ, offsetY, offsetX, cellSize,
                             mParams['namesEquations'], elemPlot, block_idx)
                            for idx, binFile in enumerate(
                                    plotFileLists[plotIdx])]
                dataAny = pool.map(wGetResults, arg_list)

                logger.debug("len(plotFileLists)")
                logger.debug(len(plotFileLists))
                '''
                for binFile in plotFileLists[plotIdx]:
                    path = projectDir + "/" + binFile
                    # logger.info("path:")
                    # logger.info(path)
                    data = readBinFile(path, info,
                                       countZ, countY, countX,
                                       offsetZ, offsetY, offsetX,
                                       cellSize, block_idx)
                    # logger.info("data:")
                    # logger.info(data)
                '''
                dataNum = []
                dataTime = []
                for i in dataAny:
                    dataTime.append(i[0])
                    dataNum.append(i[1])
                logData.append(np.array(dataNum))
            # picCount = len(plot["Value"])
            logger.info("logData:")
            logger.info(len(logData))
            logger.info("namesEquations:")
            logger.info(mParams['namesEquations'])
            dataListMin = [min([i.min() for i in j]) for j in logData]
            dataListMax = [max([i.max() for i in j]) for j in logData]
            logger.info("dataListMin:")
            logger.info(dataListMin)
            logger.info("len(logData):")
            logger.info(len(logData))
            logger.info("len(dataTime):")
            logger.info(len(dataTime))
            
            # logDataNp[value{U,V}][time]
            # logDataNp[value{U,V}, time ]
            # logDataNp[:, Idx] gets data for all
            # variables (U, V), for fixed time Idx
            # saveResultFunc save all variables (U, V) data
            # in some image for current time.
            # pool.map means call saveResultFunc for all times
            # that will generate images with variables (U, V)
            # for all times in time interval
            logDataNp = np.array(logData)
            # logger.info(logDataNp[:, 0])
            total_time = dataTime[-1]
            logger.info("total_time:")
            logger.info(total_time)
            arg_list = [(projectDir, projectName, logDataNp[:, Idx],

                         # title:
                         (equations_str + "\n"
                          + " ".join(plot["Value"])
                          + " " + str(dataTime[Idx])),

                         countZ, countY, countX,
                         offsetZ, offsetY, offsetX,
                         cellSize,
                         dataListMax, dataListMin, dx, dy,
                         Idx,
                         ("-"
                          + str(int(float(dataTime[Idx])
                                    / float(total_time)*100))
                          + "% "+str(dataTime[Idx])+" "+str(total_time)),
                         block_idx)
                        for Idx, itemd in enumerate(logDataNp[0])]
            log = pool.map(saveResultFunc, arg_list)
        for element in log:
            logger.info(element)

        createVideoFile(projectDir, projectName, plotIdx)

    # U and V
    # TODO get result all list U or V
    # resIdx = 0
    # logger.info('aaaa ', resultlistname)
    for result_idx in range(rCount):
        block_idx = result_idx

        out = getDomainProperties(info, block_idx)
        countZ, countY, countX, offsetZ, offsetY, offsetX = out

        resultItem = mParams['resultList'][result_idx]
        for resultValue in resultItem["Value"]:

            pool = mp.Pool(processes=16)
            arg_list = [(projectDir, projectName,
                         binFile, info, dimension,
                         countZ, countY, countX,
                         offsetZ, offsetY, offsetX, cellSize,
                         mParams['namesEquations'],
                         resultValue, block_idx)
                        for idx, binFile in enumerate(
                                plotFileLists[pCount + result_idx])]
            resuls = pool.map(wGetResults, arg_list)
            logger.info('skks:')
            logger.info(projectDir)
            logger.info(resultItem)
            logger.info(resultValue)
            createResultFile(projectDir, projectName,
                             str(result_idx)+'-'+resultValue,
                             resuls)
        # resIdx += 1
    logger.info(mParams['namesEquations'])
    logger.info("Done")


def get_model_params(modelParamsPath):

    with open(modelParamsPath) as f:
        modelParams = eval(f.read())

    params = Params()

    # model.plots:
    params['plotList'] = modelParams['plots']
    params['plotCount'] = len(params['plotList'])

    # model.results:
    params['resultList'] = modelParams['results']
    params['resCount'] = len(params['resultList'])
    
    # model.equation[0].system
    params['namesEquations'] = modelParams['namesEquations']
    return(params)


def test():
    
    '''
    In [15]: import solvers.hs.postproc.video.postprocessor as ps
    In [15]: data = ps.test()
    In [15]: plt.imshow(data[0][0,:,:,0])
    plt.show()
    In [15]: plt.imshow(data[1][0,:,:,0])
    plt.show()

    '''
    '''
    pf = ("/home/valdecar/Documents/projects/projectsNew/"
          + "lab/hybriddomain/problems/2dTests/"
          + "heat_block_0_ics_other_offsets/out")
    pn = "heat_block_0_ics_other_offsets"
    '''
    pf = ("/home/valdecar/Documents/projects/projectsNew/"
          + "lab/hybriddomain/problems/1dTests/"
          + "Brusselator1d/out")
    pn = "Brusselator1d"

    path = os.path.join(pf, pn + defaultGeomExt)

    info, cellSize, dx, dy, dz, dimension = readDomFile(path)

    binFileList = getSortedDrawBinFileList(pf, pn)
    plotValList = getPlotValList(binFileList)
    
    mpp = ("/home/valdecar/Documents/projects/projectsNew"
           + "/lab/hybriddomain/problems/2dTests/"
           + "heat_block_0_ics_other_offsets/out/params_plot.txt")
    mParams = get_model_params(mpp)
    pCount = len(info)
    plotFileLists = getBinFilesByPlot(binFileList, plotValList, pCount)
    print("plotFileLists")
    print(plotFileLists)
    # get sizes from block 1
    block_idx = 1
    out = getDomainProperties(info, block_idx)
    countZ, countY, countX, offsetZ, offsetY, offsetX = out
    print("countZ, countY, countX")
    print([countZ, countY, countX])
    print("offsetZ, offsetY, offsetX")
    print([offsetZ, offsetY, offsetX])

    block_idx = -2
    data = readBinFile(pf + "/" + plotFileLists[0][1], info,
                       countZ, countY, countX,
                       offsetZ, offsetY, offsetX,
                       cellSize, block_idx)
    
    return(data)
    # return(data[0, :, :, 0])


if __name__ == "__main__":
    t1 = time.time()

    desc = 'Creating pictures and a movie for a given folder.'
    parser = argparse.ArgumentParser(description=desc, epilog="Have fun!")

    # mandatory argument, project folder:
    parser.add_argument('projectDir', type=str,
                        help="local folder to process")

    # mandatory argument, project name without extension:
    parser.add_argument('projectName', type=str,
                        help="project name without extension")

    # model's params for postproc video:
    parser.add_argument('modelParams', type=str,
                        help="model's params for postproc video")

    args = parser.parse_args()

    createMovie(args.projectDir, args.projectName, args.modelParams)

    t2 = time.time()

    logger.info("Postprocessor running time: %s" % (t2 - t1))

