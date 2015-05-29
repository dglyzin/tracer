# -*- coding: utf-8 -*-
import sys
import os
from numpy import arange, sin, pi
from model import *

#/////////////////////Работа с JSON////////////////////////////////////////////#
#Глобальные настройки
#dirSource, - рабочая директория
#inFile, - входной файл
#outFile - файл выхода
#Элементы JSON
#sistems, - система уравнений
#paramList, - список параметров
#paramValues, - список наборов параметров
#varList, - список переменных
#initals, - начальные функции
#bounds, - список наборов границ
#initialRegions-границы и выбор начальной функции
#boundRegions-метод расчета на границе

class JsonFileCreate:
    def __init__(self):
        self.model=Model()
        self.connection=Connection()
        #Глобальные настройки
        self.dirSource=''
        self.inFile=''
        self.outFile=''

        #Настройки запуска программы
        self.projectName=""
        self.startTime=0
        self.finishTime=0.5
        self.timeStep=0.02
        self.saveInterval=0.1
        self.gridStepDict={}
        self.gridStepValueList=[1, 1, 1]

        self.hardware=[{"Name": "cnode1","CpuCount": 1,"GpuCount": 3},{"Name": "cnode2","CpuCount": 1,"GpuCount": 3}]
        self.mapping={"IsMapped": "true","BlockMapping": [[0,"cpu",0]]}

        #Элементы JSON
        self.sistems = []
        self.paramList = []
        self.paramValues = [{}]
        self.varList = []
        self.equations=[]

        self.initals = [{}]
        self.bounds = [{}]
        self.initialRegions = [{}]
        self.boundRegions = [{}]
        self.interconnects=[]
        self.bloks=[]

    def defaultInit(self):
        #Глобальные настройки
        self.dirSource=''
        self.inFile="template2d.json"
        self.outFile="input.json"

        #Настройки запуска программы
        self.projectName="Input_Example"
        self.startTime=0.0
        self.finishTime=0.5
        self.timeStep=0.02
        self.saveInterval=0.1
        self.gridStepDict={"x": 0.025, "y": 0.025, "z": 1}
        self.gridStepValueList=[0.025, 0.025, 1]

        self.hardware=[{"Name": "cnode1","CpuCount": 1,"GpuCount": 3},{"Name": "cnode2","CpuCount": 1,"GpuCount": 3}]
        self.mapping={"IsMapped": "true","BlockMapping": [[0,"cpu",0]]}

        #Элементы JSON
        self.sistems = ["U'=1+U^2*V-k1*U+a*(D[U,{x,2}]+D[U,{y,2}])","V'=k2*U-U^2*V+a*(D[V,{x,2}]+D[V,{y,2}])"]
        self.paramList = ["k1","a","k2"]
        self.paramValues = [{"a": 2,"k2": 5,"k1": 3},{"a": 3,"k2": 7,"k1": 5}]
        self.varList = ["x","y"]
        self.equations=[{"Name": "Flat Brusselator", "Vars": self.varList, "System": self.sistems, "Params": self.paramList, "ParamValues": self.paramValues}]

        self.initals = [{"Name": "Initial values","Values": ["15.0","sin(x)*cos(y)"]},{"Name": "Something hot","Values": ["200.0","100.0"]}]
        bound1Init={"Name": "Dirichlet example","Type": 0,"Values": ["15.0","sin(t)"]}
        bound2Init={"Name": "Neumann example", "Type": 1,"Values": ["-10.0","cos(t)"]}
        self.bounds = [bound1Init,bound2Init]
        self.initialRegions = [{"InitialNumber": 1,"xfrom": 1.0,"xto": 2.0,"yfrom": 1.0,"yto": 2.0}]
        bound1={"BoundNumber": 0,"Side": 1,"xfrom": 0.0,"xto": 0.0, "yfrom": 0.0, "yto": 5.0}
        bound2={"BoundNumber": 1,"Side": 1,"xfrom": 0.0,"xto": 0.0,"yfrom": 5.0,"yto": 10.0}
        self.boundRegions = [bound1,bound2]
        self.bloks=[{"Name": "MainBlock", "Dimension": 2, "Offset": {"x": 0.0,"y": 0.0},"Size":{"x": 10.0,"y": 10.0},"DefaultEquation": 0, "DefaultInitial": 0, "BoundRegions": self.boundRegions, "InitialRegions": self.initialRegions}]
        self.interconnects={"Name": "y-halves connection", "Block1": 0, "Block2": 1, "Block1Side": 3, "Block2Side": 2}

        self.setSimpleValues(self.projectName,self.startTime,self.finishTime,self.timeStep,self.saveInterval,self.gridStepDict)
        self.setBlocks()
        self.addInterconnects(self.interconnects)
        self.setEquation()
        self.setBounds()
        self.setInitals()
        self.setCompnode()
        self.setMapping("true",[0,"cpu",0])
        self.setClusterConnect({"Host": "10.7.129.222", "Port": 22, "Username": "tester", "Password": "", "Workspace": "/home/tester/Tracer1", "SolverExecutable": "/home/dglyzin/hybridsolver/bin/HS"})

    def setGlobal(self,dirSource,inFile,outFile):
        self.dirSource=dirSource
        self.inFile=inFile
        self.outFile=outFile

    def setSimpleValues(self,projectName,startTime,finishTime,timeStep,saveInterval,Solver,SolverAbsTolerance,SolverRelTolerance,gridStepValueList):
        self.projectName=projectName
        self.startTime=startTime
        self.finishTime=finishTime
        self.timeStep=timeStep
        self.saveInterval=saveInterval

        projdict={}

        projdict["ProjectName"]=projectName
        projdict["StartTime"]=startTime
        projdict["FinishTime"]=finishTime
        projdict["TimeStep"]=timeStep
        projdict["SaveInterval"]=saveInterval
##        projdict["GridStep"]=gridStepValueList
        projdict["Solver"]=Solver
        projdict["SolverAbsTolerance"]=SolverAbsTolerance
        projdict["SolverRelTolerance"]=SolverRelTolerance
        projdict["GridStep"]={}
        projdict["GridStep"]["x"]=1
        projdict["GridStep"]["y"]=1
        projdict["GridStep"]["z"]=1
        for key, value in gridStepValueList.items():
            projdict["GridStep"][key]=value
##        if len(self.gridStepValueList)>=1:
##            projdict["GridStep"]["x"]=gridStepValueList[0]
##            projdict["GridStep"]["y"]=1
##            projdict["GridStep"]["z"]=1
##        elif len(self.gridStepValueList)>=2:
##            projdict["GridStep"]["y"]=gridStepValueList[1]
##        elif len(self.gridStepValueList)>=3:
##            projdict["GridStep"]["z"]=gridStepValueList[2]

        self.model.setSimpleValues(projdict)

    def addBlocks(self,sName,iDimension,dOffset,dSize,iDefaultEquation,iDefaultInitial,lBoundRegions,lInitialRegions):
        blok={"Name": sName, "Dimension": iDimension, "Offset": dOffset,"Size":dSize,"DefaultEquation": iDefaultEquation, "DefaultInitial": iDefaultInitial, "BoundRegions": lBoundRegions, "InitialRegions": lInitialRegions}
        self.model.addBlock(blok)

    def setBlocks(self):
        self.model.deleteAllBlocks()
        for i in self.bloks:
            self.model.addBlock(i)

    def setBlocks1(self,bloksList):
        self.model.deleteAllBlocks()
        for i in bloksList:
            self.model.addBlock(i)

    def addInterconnects(self,dInterconnects):
        if dInterconnects<>{}:
            self.model.addInterconnect(dInterconnects)

    def addEquation(self,eDict):
        self.model.addEquation(eDict)

    def addEquation1(self,sName,lVars,lSystem,lParams,ldParamValues):
        eDict={"Name": sName, "Vars": lVars, "System": lSystem, "Params": lParams, "ParamValues": [ldParamValues]}
        self.model.addEquation(eDict)

    def setEquation(self):
        self.model.deleteAllEquations()
        for i in self.equations:
            self.model.addEquation(i)

    def setEquation1(self,lEquation):
        self.model.deleteAllEquations()
        for i in lEquation:
            self.model.addEquation(i)

    def addBounds(self,bDict):
        self.model.addBound(bDict)

    def addBounds1(self,BoundNum,Side,xfrom,xto,yfrom,yto):
        bound={"BoundNumber": BoundNum,"Side": Side,"xfrom": xfrom,"xto": xto, "yfrom": yfrom, "yto": yto}
        self.model.addBound(bound)

    def setBounds(self):
        self.model.deleteAllBounds()
        for i in self.bounds:
            self.model.addBound(i)

    def addInitals(self,iDict):
        self.model.addInitial(iDict)

    def addInitals1(self,Name,Values):
        iDict={"Name": Name,"Values": Values}
        self.model.addInitial(iDict)

    def setInitals(self):
        self.model.deleteAllInitials()
        for i in self.initals:
            self.model.addInitial(i)

    def setInitals1(self,initalsList):
        self.model.deleteAllInitials()
        out=''
        for i in range(len(initalsList)):
            if i==0:
                out='{"Name": "Initial values","Values": '+str(initalsList[i])+'}'
            if i>0:
                out=out+',{"Name": "Something hot","Values": '+str(initalsList[i])+'}'
        out='['+out+']'
        self.initals=out
        for i in self.initals:
            self.model.addInitial(i)

    def setInitals2(self,initalsListDict):
        self.model.deleteAllInitials()
        for i in initalsListDict:
            self.model.addInitial(i)


    def addCompnode(self,cDict):
        self.model.addCompnode(cDict)

    def addCompnode1(self,Name,CpuCount,GpuCount):
        cDict={"Name": Name, "CpuCount": int(CpuCount), "GpuCount": int(GpuCount)}
        self.model.addCompnode(cDict)

    def setCompnode(self):
        self.model.deleteAllCompnodes()
        for i in self.hardware:
            self.model.addCompnode(i)

    def setCompnode1(self,hardware):
        self.model.deleteAllCompnodes()
        for i in hardware:
            self.model.addCompnode(i)

    def setMapping(self,isMapped,mapping):
        self.model.isMapped=str(isMapped)
        self.model.mapping=[mapping]

    def setClusterConnect(self,dConnection):
        self.connection.fromDict(dConnection)
        self.model.connection=self.connection

    def Create_json(self,dir,OutputFile):
        if dir!="":
            dir=dir+"/"
        self.model.saveToFile(os.path.join(dir,OutputFile))


if  __name__ =='__main__':
    objName = JsonFileCreate()
    objName.defaultInit()
    objName.Create_json('','projectOut.json')


##    model = Model()
##    model.loadFromFile(os.path.join("","input.json"))
##    initDict= model.toDict()
##    k=0
##    for i in initDict:
##        print k,i,initDict[i]
##        k=k+1
