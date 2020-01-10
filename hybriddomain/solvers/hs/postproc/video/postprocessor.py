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
'''
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

folder = "video"
sourcedir = currentdir.split(folder)[0]
logger.info("postproc dir:")
logger.info(sourcedir)
if sourcedir not in sys.path:
    sys.path += [sourcedir]
'''
# from domainmodel.model import Model

from hybriddomain.solvers.hs.postproc \
        .utils.fileUtils import getSortedDrawBinFileList
from hybriddomain.solvers.hs.postproc \
        .utils.fileUtils import drawExtension
from hybriddomain.solvers.hs.postproc \
        .utils.fileUtils import defaultGeomExt
from hybriddomain.solvers.hs.postproc \
        .utils.fileUtils import getPlotValList

from hybriddomain.solvers.hs.postproc \
        .utils.binaryFileReader import readBinFile 
from hybriddomain.solvers.hs.postproc \
        .utils.binaryFileReader import readDomFile
from hybriddomain.solvers.hs.postproc \
        .utils.binaryFileReader import getDomainProperties

from mpl_toolkits.axes_grid1 import make_axes_locatable


def get_img_filename(projectName, plotIdx, timeIdx):

    '''For savePlots1D, savePlots2D and therefore
    wSavePlots1D, wSavePlots2D, saveResultFunc funcs'''

    return(projectName+"-plot"
           + str(plotIdx) + "-time"+str(timeIdx) + ".png")


def get_img_filename_avconv(projectName, plotIdx):
    '''For createVideoFile func'''
    return(projectName+"-plot"
           + str(plotIdx) + "-time" + "%d.png")


def get_mp4_filename(plotName):
    '''For createVideoFile func'''
    return(plotName+ ".mp4")


def get_result_filename(resName):
    '''For createResultFile func.'''
    return(resName+".out")


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

    # logger.info(maxValue)
    # logger.info(minValue)

    return maxValue, minValue


def savePng1D(filename, X, data, maxValue, minValue,
              currentTimeStr, cellSize):

    '''Will place several images for each
    equation in system (cellSize) at same
    figure (same .png file)'''

    figure = Figure()
    canvas = FigureCanvas(figure)

    t = str(currentTimeStr)

    row = round(math.sqrt(cellSize))
    column = math.ceil(cellSize / row)

    figure.suptitle(t)
    # print("cellSize:")
    # print(cellSize)
    # print("maxValue:")
    # print(maxValue)
    # print("minValue:")
    # print(minValue)

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


def savePng2D(filename, X, Y, data, maxValue, minValue,
              currentTimeStr, cellSize):

    '''Will place several images for each
    equation in system (cellSize) at same
    figure (same .png file)'''

    figure = Figure()
    canvas = FigureCanvas(figure)

    t = str(currentTimeStr)

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


def savePlots1D(projectDir, projectName, data, time_str,
                countZ, countY, countX,
                offsetZ, offsetY, offsetX,
                cellSize, maxValue, minValue,
                dx, dy, timeIdx, percent, plotIdx):
    # for idx, binFile in enumerate(binFileList):
    # data = readBinFile(projectDir+"/"+binFile, info,
    #                    countZ, countY, countX,
    #                    offsetZ, offsetY, offsetX,
    #                    cellSize)
    xs = np.arange(0, countX)*dx
    # dictfun = {}
    # for numitem, item in enumerate(namesEquations):
    #     dictfun[item] = data[0, 0, :, numitem]

    filename = os.path.join(projectDir,
                            get_img_filename(projectName, plotIdx, timeIdx))

    # fix bug with cellsize:
    cellSize = len(data)
    # logger.info("cellsize as len(data):")
    # logger.info(cellSize)

    savePng1D(filename, xs, data, maxValue, minValue, time_str, cellSize)
    # logger.info("produced png: "+ filename)
    # return "produced png: " + filename
    return("produced png: " + percent)


def savePlots2D(projectDir, projectName, data, time_str,
                countZ, countY, countX,
                offsetZ, offsetY, offsetX,
                cellSize, maxValue, minValue,
                dx, dy, timeIdx, percent, plotIdx):
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
    filename = os.path.join(projectDir,
                            get_img_filename(projectName, plotIdx, timeIdx))
    # plt.savefig(filename, format='png')
    # logger.info 'save #', idx, binFile, "->", filename
    # plt.clf()

    # t = binFile.split("-")[1]
    # equal to
    # t = binFile.split("-")[1]
    # Ex (binFile): heat_block_0-0.05300000-2.dbin
    # t = t.split(drawExtension)[0]

    # fix bug with cellsize:
    cellSize = len(data)
    # logger.info("cellsize as len(data):")
    # logger.info(cellSize)

    savePng2D(filename, X, Y, data, maxValue, minValue, time_str, cellSize)
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
               cellSize, nameEquations, resultExpressions,
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
    if type(resultExpressions) != list:
        res = eval(resultExpressions, dictfun)
    else:
        res = []
        for resultExpression in resultExpressions:
            res.append(eval(resultExpression, dictfun))
    # filename = os.path.join(projectDir, (projectName+"-res"
    #                                      + str(resIdx) + postfix + ".txt"))

    t = binFile.split("-")[-2]

    # t = t.split(drawExtension)[0]
    # with open(filename, "w") as f:
    #    f.write(t)
    # savePng1D(filename, xs, data, maxValue, minValue, t, cellSize)
    # logger.info("produced png: "+ filename)
    return t, np.array(res)  # "produced text result: "+ filename


def wGetResults(args):
    return(getResults(*args))


def wSavePlots1D(args):
    return(savePlots1D(*args))


def wSavePlots2D(args):
    return(savePlots2D(*args))


def createResultFile(projectDir, resName, resLog):
    logger.info("Creating out file: %s" % (resName))

    outfileNamePath = (projectDir
                       + get_result_filename(resName))

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


def createVideoFile(projectDir, projectName, plotName, plotIdx):
    logger.info("Creating video file: %s" % (str(plotIdx)))
    # TODO 2: separate plotIdx from postfix:
    command = ("avconv -r 5 -loglevel panic -i "+projectDir
               + get_img_filename_avconv(projectName, plotIdx)
               + " -pix_fmt yuv420p -b:v 1000k -c:v libx264 "
               + projectDir+get_mp4_filename(plotName))
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

    # names for eval:
    dep_vars_names = [eq[:eq.find("'")] for eq in mParams['namesEquations']]
    # for numitem, item in enumerate(mParams['namesEquations']):
    #     mParams['namesEquations'][numitem] = item[:item.find("'")]
    # logger.info(plotFileLists)
    # plotList = model.plots

    for plotIdx in range(pCount):
        # for plotIdx, plot in enumerate(mParams['plotList']):
        # t1 = time.time()
        #TODO iterate through blocks to combine whole domain
        block_idx = 0
        
        out = getDomainProperties(info, block_idx)
        countZ, countY, countX, offsetZ, offsetY, offsetX = out
        
        plot = mParams['plotList'][plotIdx]
        # t2 = time.time()
        # logger.info("Расчет минимума / максимума: ", t2 - t1)
        logger.info('plot["Value"]')
        logger.info(plot['Value'])
        #logger.info(type(plot['Value']))
        pool = mp.Pool(processes=16)
        # saveResultFunc = savePlots1D
        if dimension == 1:
            saveResultFunc = wSavePlots1D  # savePlots1D
        if dimension == 2:
            saveResultFunc = wSavePlots2D

        logger.info("plot[value]:")
        logger.info(plot["Value"])

        #we combine multiple plots on one screen if required
        logger.info("Creating images for block %s value %s"
                    % (str(block_idx), str(plot["Value"])))

        vals = plot["Value"] if type(plot["Value"]) == list else [plot["Value"]]

        arg_list = [(projectDir, projectName,
                     binFile, info, dimension,
                     countZ, countY, countX,
                     offsetZ, offsetY, offsetX, cellSize,
                     dep_vars_names, vals, block_idx)
                    for idx, binFile in enumerate(
                            plotFileLists[plotIdx])]
        results = pool.map(wGetResults, arg_list) #pairs of t, value where value is a list of arrays (possibly of 1 array)

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
        dataVals = []
        dataTime = []
        for res in results:
            dataTime.append(res[0])
            dataVals.append(res[1])
        dataVals = np.array(dataVals) #major axis is time, next axis is variable number, then data axes

        # picCount = len(plot["Value"])
        logger.info("logData:")
        logger.info(len(dataVals))
        logger.info("namesEquations:")
        logger.info(mParams['namesEquations'])
        
        outCellSize = len(vals)
        dataListMin = [np.min(dataVals[:,idx]) for idx in range(outCellSize)]
        dataListMax = [np.max(dataVals[:,idx]) for idx in range(outCellSize)]        
        
        logger.info("dataListMin:")
        logger.info(dataListMin)
        logger.info("len(dataVals):")
        logger.info(len(dataVals))
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
        total_time = dataTime[-1]
        logger.info("total_time:")
        logger.info(total_time)
        arg_list = [(projectDir, projectName, val,
                     # title:
                     (plot["Title"]+"\n"
                      # + equations_str + "\n"
                      + " ".join(plot["Value"])
                      + " t = " + str(dataTime[timeIdx])),

                     countZ, countY, countX,
                     offsetZ, offsetY, offsetX,
                     cellSize,
                     dataListMax, dataListMin, dx, dy,
                     timeIdx,
                     ("-"
                      + str(int(float(dataTime[timeIdx])
                                / float(total_time)*100))
                      + "% "+str(dataTime[timeIdx])+" "+str(total_time)),
                     plotIdx)
                    for timeIdx, val in enumerate(dataVals)]

        log = pool.map(saveResultFunc, arg_list)

        for element in log:
            logger.info(element)

        createVideoFile(projectDir, projectName, plot["Name"], plotIdx)


    for result_idx in range(rCount):
        # TODO iterate through blocks to combine whole domain
        block_idx = 0

        out = getDomainProperties(info, block_idx)
        countZ, countY, countX, offsetZ, offsetY, offsetX = out

        resultItem = mParams['resultList'][result_idx]

        resultValues = resultItem["Value"]# can be one element or can be list
        pool = mp.Pool(processes=16)
        # here plotFileLists is list, generated
        # by solver, and extracted with getBinFilesByPlot:
        arg_list = [(projectDir, projectName,
                     binFile, info, dimension,
                     countZ, countY, countX,
                     offsetZ, offsetY, offsetX, cellSize,
                     dep_vars_names,
                     resultValues, block_idx)
                    for idx, binFile in enumerate(
                            plotFileLists[pCount + result_idx])]
        results = pool.map(wGetResults, arg_list)
        logger.info('skks:')
        logger.info(projectDir)
        logger.info(resultItem)
        logger.info(resultValues)
        createResultFile(projectDir, resultItem["Name"], results)

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


def run():
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


if __name__ == "__main__":
    
    run()
