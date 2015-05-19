# -*- coding: utf-8 -*-
import sys
import os
from numpy import arange, sin, pi
import re
#from model import *
import json

funcList='acosh','asinh','atanh','acos','asin','atan','cos','exp','log','log10','sin','tan','tanh'
funcListReplace='acosh','asinh','atanh','acos','asin','atan','cos','exp','log','log10','sin','tan','tanh'

class RunGCFILE:
    def __init__(self):
        self.dirFile="" ##../File
        self.dirSourse="Source"
        self.InputFile = "input.json"
        runGenCfile(self,self.dirSourse,self.dirFile,self.InputFile)

#    Run gen C file
def runGenCfile(self,dirSourse,dirFile,InputFile):
    #model = Model()
    if dirFile!="":
        dirFile=dirFile+"/"

    projectFile = open(os.path.join(dirFile,InputFile))
    initDict = json.loads(projectFile.read())
    projectFile.close()

    #model.loadFromFile(os.path.join(dirFile,InputFile))
    #initDict = model.toDict()

    cFileName = os.path.join(dirFile,"funcOut.c")
    generateCfromDict(initDict, cFileName)

def generateCfromDict(modelDict, cFileName):
    dirSourse = os.path.join(os.path.abspath(os.path.dirname(__file__)),"Source")

    k=0
    for i in modelDict:
##        print k,i,modelDict[i]
        k=k+1

    #Достаем данные из JSON
    equ=modelDict['Equations'][0]['System']
    equForReplace=equ[:]
    equOut=[]
    var = modelDict['Equations'][0]['Vars']

    dif=findDif(equ)
##    print 'findDif(equ)',dif[:]

    param=modelDict['Equations'][0]['Params']
    initials=modelDict['Initials'][:]
    boundRegions=modelDict['Blocks'][0]['BoundRegions'][:]
    bounds=modelDict['Bounds'][:]
    initOffset=modelDict['Blocks'][0]['Offset']
    initSize=modelDict['Blocks'][0]['Size']
    initSizeList=[]
    for i in var:
        initSizeList.append(initOffset[i])
        initSizeList.append(initSize[i])


    global funcList
    returnEqu=[]
    #список ключевых слов для замены
    listParamForTempl = ['$@sistemUpL@$','$@sistemUpC@$','$@sistemUpR@$',
                '$@sistemCentrL@$','$@sistemCentrC@$','$@sistemCentrR@$',
                '$@sistemDownL@$','$@sistemDownC@$','$@sistemDownR@$']
    listEquForTemplate = []
    forNeiman=""
    listForNeimanProizv=[]

    #Заменяем в уравнениях U' на $i - r[idx] U на %i - s[idx]
    for x in equForReplace:
        for i in range(len(dif)):
            x=x.replace(dif[i]+"'",'$'+str(i))    # $ - r[idx]
            x=x.replace(dif[i],'%'+str(i))    # % - s[idx]
        #Заменяем параметры на param[]
        x=replaceParam(x,param)
        equOut.append(x)

    #Вычленяем в уравнениях производную
    for equ in equOut:
        proizv = re.findall("D\[[A-Za-z0-9$%,.{}()\^\\\*\+-]+\]",equ)
        arrayFunc=[]
        arrayDegree=[]
        listEquForReplace=[equ]*9
        for iProizv in proizv:
            #получаем список из производных переменных и их степеней
            func,varProizv,degProizv=replaceForProizv(None,iProizv)
            for x in varProizv:
                if x not in var:
                    #добавляем неуказанные пользователем переменные
                    var.append(x)
            degProizvTotal=0
            for x in degProizv:
                degProizvTotal+=int(x)  #Общая степень производной

            spisokProizv=FindZamena(None,dif,func,varProizv,var,degProizv,dirSourse)
            if len(spisokProizv)>0:
                for i in range(len(spisokProizv)):
                    listEquForReplace[i]=listEquForReplace[i].replace(iProizv,spisokProizv[i])
                listForNeimanProizv.append(spisokProizv[5])

        for i in listEquForReplace:
            i=i.replace('$0','result[idx]')    # $ - r[idx]
            i=i.replace('%0','source[idx]')    # % - s[idx]

            i=i.replace('$1','result[idx+1]')    # $ - r[idx+1]
            i=i.replace('%1','source[idx+1]')    # % - s[idx+1]

            i=i.replace('$2','result[idx+2]')    # $ - r[idx+2]
            i=i.replace('%2','source[idx+2]')    # % - s[idx+2]

            #Приводим 1,1 к 1.1
            p=re.findall("[0-9][,][0-9]",i)
            if p:
                for elem in p:
                    i=i.replace(elem,elem[0]+'.'+elem[-1])

            i=replacePow(i)

            #Заменяем переменные на idx, но это не совсем корректно
            #======================================================
            i=replaceVar(i,var)
            #======================================================

            returnEqu.append(i)

##    print returnEqu[:]

    for i in range(9):
        if len(equOut)==1:
            listEquForTemplate.append(returnEqu[i]+';\n  ')
        if len(equOut)==2:
            listEquForTemplate.append(returnEqu[i]+';\n  '+returnEqu[i+9]+';')
        if len(equOut)==3:
            listEquForTemplate.append(returnEqu[i]+';\n  '+returnEqu[i+9]+';\n  '+returnEqu[i+18]+';')

    forNeiman=listEquForTemplate[4]

    #Создаем файл основного кода программы
    f = open(os.path.join(dirSourse,"func2DTemplate.c"))
    textTemplateC=f.read()
    f.close()
    ftemp = open(os.path.join(dirSourse,"replaceTemplate.txt"))
    temp=ftemp.read()
    ftemp.close()
    tempList=temp.split('%')
    tempDict={}
    for i in range(int(len(tempList)/2)):
        tempDict[tempList[i*2]]=tempList[i*2+1]
##    for i in tempDict:
##        print i,tempDict[i]

    textTemplateC=(textTemplateC).decode('utf-8')

    #Создаем и вставляем блок со значением параметра
    paramValues=modelDict['Equations'][0]['ParamValues']
    outReplace=''
    for index, element in enumerate(param):
        outReplace=outReplace+"(*pparams)["+str(index)+"] = "+str(paramValues[0][element])+";\n"
    textTemplateC=textTemplateC.replace('$initParams$',outReplace)

    #Создаем и вставляем блоки с начальными условиями
    initBlok=tempDict['$Block0Initial$']
    outReplace=''
    for i in range(len(initials)):
        t=initBlok.replace('$v0$',str(i))
        rpl=""
        iter=0
        for j in initials[i]['Values']:
            rpl=rpl+"result[idx+"+str(iter)+"] = "+j+";\n"
            iter+=1
        t=t.replace('$v1$',rpl)
        outReplace=outReplace+t

    textTemplateC=textTemplateC.replace('$Block0Initial$',outReplace)

    #Добавляем вызов начальных условий
    initBlok=tempDict['$Block0InitialFill$']
    outReplace=''
    for i in range(len(initials)):
        t=initBlok.replace('$v0$',str(i))
        outReplace=outReplace+t
    textTemplateC=textTemplateC.replace('$Block0InitialFill$',outReplace)

    #Блоки краевых условий

##    print 'forNeiman',forNeiman,initSizeList

    textTemplateC=replaceBounds(bounds,boundRegions,tempDict,textTemplateC,initSizeList,forNeiman)

    for i in range(len(listEquForTemplate)):
        textTemplateC=str(textTemplateC.encode('ascii', 'ignore')).replace(listParamForTempl[i],listEquForTemplate[i])

##    print textTemplateC
##    path=os.path.join(os.getcwd(),"File")
##    fout = open(os.path.join(path,cFileName), "wt")
    fout = open(cFileName, "wt")
    fout.write(textTemplateC)   ##.encode(encoding='UTF-8')
    fout.close()

#Блоки краевых условий
def replaceBounds(bounds,boundRegions,tempDict,text,initSizeList,forNeiman):
    varIter=8
    varI=0
    strNeiman=''
    strRplOption=''
    for i in boundRegions:
        varIter+=1
        nBounds=i['BoundNumber']
        nSide=i['Side']
        xfrom=i['xfrom']
        xto=i['xto']
        yfrom=i['yfrom']
        yto=i['yto']
        nType=bounds[nBounds]['Type']
        lValues=bounds[nBounds]['Values']
##        print "nType",nType,lValues
        if nType==0:
            initBlok=tempDict['$Dirichlet$']
            rpl=""
            iter=0
            for j in lValues:
                rpl=rpl+"result[idx+"+str(iter)+"] = "+j+";\n"
                iter+=1
            t=initBlok.replace('$v1$',rpl)
            text=text.replace('$Dirichlet$',t)
            strRplOption=strRplOption+"pFuncs["+str(varIter)+"] = Block0Bound1;\n"

        elif nType==1:
            initBlok=tempDict['$Neiman$']
            t=''
            forNeimanList=forNeiman.split('\n')
            for j in lValues:
                rpl="bound_value = $v$;\n $nonexistent1$\n $sistemGx1$\n"
                rpl=rpl.replace("$v$",j)
                sistem=forNeimanList[lValues.index(j)]
                rpl=NeimanNonexistent(nSide,xfrom,xto,yfrom,yto,initSizeList,sistem,rpl)
                t=t+rpl
            t=initBlok.replace('$v1$',t)
            rpl=t.replace('$v0$',str(varI))
            strNeiman=strNeiman+rpl
            strRplOption=strRplOption+"pFuncs["+str(varIter)+"] = Block0Bound0_"+str(varI)+";\n"

    text=text.replace('$Neiman$',strNeiman)
    text=text.replace('$Dirichlet$',"")
    text=text.replace('$pFuncs$',strRplOption)
    return text

#Граничные условия Неймана
def NeimanNonexistent(nSide,xfrom,xto,yfrom,yto,initSizeList,sistem,textRpl):
    #initSizeList - содержит начало x, отступ x, начало y, отступ
    if nSide==0 or nSide==2:
        rpl1='+'
        rpl2='-'
    elif nSide==1 or nSide==3:
        rpl1='-'
        rpl2='+'

    nonexistent=["nonexistent0X = source[idx"+rpl1+"Block0StrideX*CELLSIZE]"+rpl2+"2.0 * bound_value * DX2;\n",
                "nonexistent1X = source[idx"+rpl1+"Block0StrideX*CELLSIZE+1]"+rpl2+"2.0 * bound_value * DX2;\n",
                "nonexistent2X = source[idx"+rpl1+"Block0StrideX*CELLSIZE+2]"+rpl2+"2.0 * bound_value * DX2;\n",
                "nonexistent0Y = source[idx"+rpl1+"Block0StrideY*CELLSIZE]"+rpl2+"2.0 * bound_value * DY2;\n",
                "nonexistent1Y = source[idx"+rpl1+"Block0StrideY*CELLSIZE+1]"+rpl2+"2.0 * bound_value * DY2;\n",
                "nonexistent2Y = source[idx"+rpl1+"Block0StrideY*CELLSIZE+2]"+rpl2+"2.0 * bound_value * DY2;\n"]

    if nSide==0:
        forReplace="source[idx-Block0StrideX*CELLSIZE]"
        if sistem.find(forReplace)==-1: nonexistent[0]='//'+nonexistent[0]
        sistem=sistem.replace(forReplace,"nonexistent0X")
        forReplace="source[idx-Block0StrideX*CELLSIZE+1]"
        if sistem.find(forReplace)==-1: nonexistent[1]='//'+nonexistent[1]
        sistem=sistem.replace(forReplace,"nonexistent1X")
        forReplace="source[idx-Block0StrideX*CELLSIZE+2]"
        if sistem.find(forReplace)==-1: nonexistent[2]='//'+nonexistent[2]
        sistem=sistem.replace(forReplace,"nonexistent2X")
        nonexistent[3]='//'+nonexistent[3]
        nonexistent[4]='//'+nonexistent[4]
        nonexistent[5]='//'+nonexistent[5]
    elif nSide==1:
        forReplace="source[idx+Block0StrideX*CELLSIZE]"
        if sistem.find(forReplace)==-1: nonexistent[0]='//'+nonexistent[0]
        sistem=sistem.replace(forReplace,"nonexistent0X")
        forReplace="source[idx+Block0StrideX*CELLSIZE+1]"
        if sistem.find(forReplace)==-1: nonexistent[1]='//'+nonexistent[1]
        sistem=sistem.replace(forReplace,"nonexistent1X")
        forReplace="source[idx+Block0StrideX*CELLSIZE+2]"
        if sistem.find(forReplace)==-1: nonexistent[2]='//'+nonexistent[2]
        sistem=sistem.replace(forReplace,"nonexistent2X")
        nonexistent[3]='//'+nonexistent[3]
        nonexistent[4]='//'+nonexistent[4]
        nonexistent[5]='//'+nonexistent[5]
    elif nSide==2:
        nonexistent[0]='//'+nonexistent[0]
        nonexistent[1]='//'+nonexistent[1]
        nonexistent[2]='//'+nonexistent[2]
        forReplace="source[idx-Block0StrideY*CELLSIZE]"
        if sistem.find(forReplace)==-1: nonexistent[3]='//'+nonexistent[3]
        sistem=sistem.replace(forReplace,"nonexistent0Y")
        forReplace="source[idx-Block0StrideY*CELLSIZE+1]"
        if sistem.find(forReplace)==-1: nonexistent[4]='//'+nonexistent[4]
        sistem=sistem.replace(forReplace,"nonexistent1Y")
        forReplace="source[idx-Block0StrideY*CELLSIZE+2]"
        if sistem.find(forReplace)==-1: nonexistent[5]='//'+nonexistent[5]
        sistem=sistem.replace(forReplace,"nonexistent2Y")
    elif nSide==3:
        nonexistent[0]='//'+nonexistent[0]
        nonexistent[1]='//'+nonexistent[1]
        nonexistent[2]='//'+nonexistent[2]
        forReplace="source[idx+Block0StrideY*CELLSIZE]"
        if sistem.find(forReplace)==-1: nonexistent[3]='//'+nonexistent[3]
        sistem=sistem.replace(forReplace,"nonexistent0Y")
        forReplace="source[idx+Block0StrideY*CELLSIZE+1]"
        if sistem.find(forReplace)==-1: nonexistent[4]='//'+nonexistent[4]
        sistem=sistem.replace(forReplace,"nonexistent1Y")
        forReplace="source[idx+Block0StrideY*CELLSIZE+2]"
        if sistem.find(forReplace)==-1: nonexistent[5]='//'+nonexistent[5]
        sistem=sistem.replace(forReplace,"nonexistent2Y")

    textRpl=textRpl.replace('$nonexistent1$',nonexistent[0]+nonexistent[1]+nonexistent[2]+nonexistent[3]+nonexistent[4]+nonexistent[5])

##    print 'textRpl',textRpl,sistem

    textRpl=textRpl.replace('$sistemGx1$',sistem)

    return textRpl

#заменяем переменные на idx
def replaceVar(equ,var):
    equ=' '+equ+' '
    for i in range(len(var)):
        if i==0:
            step=''
        else:
            step='+'+str(i)
        out = re.findall("[^A-Za-z]{1}"+var[i]+"[^A-Za-z]{1}",equ)
        for elem in out:
            equ=equ.replace(elem,elem[0]+'idx'+step+elem[2])
    return equ[1:-1]

#заменяем параметры на param[i]
def replaceParam(equ,param):
    equ=' '+equ+' '
    for i in range(len(param)):
        out = re.findall("[^A-Za-z]{1}"+param[i]+"[^A-Za-z]{1}",equ)
        for elem in out:
            equ=equ.replace(elem,elem[0]+'params['+str(i)+']'+elem[-1])
    return equ[1:-1]

#Ищем ^ и заменяем на pow(подметод вызываем в runGenCfile)
#Проблемма!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#a^b^c^d -обрабатывает криво
def replacePow(text):
    #смотрим есть ли в уравнении ^
    while text.find('^')>0:
        #делим уравнение на части по символу ^
        sSplit=text.split('^')
        s=[]    #список из двух частей разделенные последним знаком ^
        strLeftLastPow=''
        for elem in sSplit[:-1]:
            strLeftLastPow=strLeftLastPow+elem+'^'
##        print 'strLeftLastPow',strLeftLastPow
        s.append(strLeftLastPow[:-1])   #левая часть от последнего знака ^
        s.append(sSplit[-1])    #правая часть от последнего знака ^
        spisokPow=[]
        i=0
##        print 's=',s[:]
        #проходим по всем частям начиная с последней части
        while i<len(s):
            strEndToBeg=s[-i-1]  #текущая часть(идем с конца)
            #для всех частей за исключением первой(т.е. последней) мы обрабатываем посимвольно конец части
            if i>0:
                outf=0  #флаг выхода по скобкам
                out=''  #a или b из pow(a,b)
                j=len(strEndToBeg)-1 #индекс последнего символа в части
                while j>=0: #идем с конца в начало части
                    out=strEndToBeg[j]+out   #добавили символ в начало out
                    if strEndToBeg[-1]==')':
                        #----->выход по (=)
                        if strEndToBeg[j]=='(':
                            outf+=1
                            if outf==0:
                                spisokPow.append(out)
                                break
                        #----->выход по (=)
                        if strEndToBeg[j]==')':
                            outf-=1
                            if outf==0:
                                spisokPow.append(out)
                                break
                    else:
                        #----->выход по ()=0 и текущий символ =^\\*+-
                        #дополнение символы ( и )
                        if outf==0 and (strEndToBeg[j]=='=' or strEndToBeg[j]=='('  or strEndToBeg[j]=='(' or strEndToBeg[j]=='^' or strEndToBeg[j]=='\\' or strEndToBeg[j]=='*' or strEndToBeg[j]=='+' or strEndToBeg[j]=='-'):
##                                print 'out1',strEndToBeg[j],strEndToBeg[j-3:j]
                                if  strEndToBeg[j-3:j]=='idx' and (strEndToBeg[j]=='+' or strEndToBeg[j]=='-'):
                                    pass
                                else:
                                    out=out[1:]
                                    spisokPow.append(out)
                                    break
                    #смотрим следующший символ
                    j-=1
                #просмотрели всю строку
                if out==strEndToBeg:
                    spisokPow.append(out)
            #для всех частей за исключением последней(т.е. первой) мы обрабатываем посимвольно начало части
            if i<len(s)-1:
                outf=0  #флаг выхода по скобкам
                out=''  #a или b из pow(a,b)
                j=0 #индекс последнего символа в части
                while j<len(strEndToBeg): #идем с начала в конец части
                    out+=strEndToBeg[j]   #добавили символ в конец out
                    if strEndToBeg[0]=='(':
                        #----->выход по (=)
                        if strEndToBeg[j]=='(':
                            outf+=1
                            if outf==0:
                                spisokPow.append(out)
                                break
                        #----->выход по (=)
                        if strEndToBeg[j]==')':
                            outf-=1
                            if outf==0:
                                spisokPow.append(out)
                                break
                    else:
                        #----->выход по ()=0 и текущий символ =^\\*+-
                        #дополнение символы ( и )
                        if outf==0 and (strEndToBeg[j]=='=' or strEndToBeg[j]=='('  or strEndToBeg[j]=='(' or strEndToBeg[j]=='^' or strEndToBeg[j]=='\\' or strEndToBeg[j]=='*' or strEndToBeg[j]=='+' or strEndToBeg[j]=='-'):
##                                print 'out2',strEndToBeg[:],strEndToBeg[j],strEndToBeg[j-3:j]
                                if  strEndToBeg[j-3:j]=='idx' and (strEndToBeg[j]=='+' or strEndToBeg[j]=='-'):
                                    pass
                                elif strEndToBeg[j-3:j+1]=='pow(' or strEndToBeg[j-1:j+1]==',(':
                                    pass
                                else:
                                    out=out[:-1]
                                    spisokPow.append(out)
                                    break
                    #смотрим следующший символ
                    j+=1
                #просмотрели всю строку
                if out==strEndToBeg:
                    spisokPow.append(out)
            #смотрим следующую часть
            i+=1
        #заменяем a^b на a*...*a b раз или pow(a,b)
        iter=0
        while iter<len(spisokPow):
##            print 'spisokPow',spisokPow
            textRepl=''
            if str(spisokPow[iter]).isdigit():
                for i in range(int(spisokPow[iter])):
                    textRepl+=str(spisokPow[iter+1])+'*'
##                    print 'text',spisokPow[iter],textRepl
                text=text.replace(spisokPow[iter+1]+'^'+spisokPow[iter],'('+textRepl[:-1]+')')
            elif str(spisokPow[iter])[:-1].isdigit() and str(spisokPow[iter])[-1]==')':
                for i in range(int(str(spisokPow[iter])[:-1])):
                    textRepl+=str(spisokPow[iter+1])+'*'
                text=text.replace(spisokPow[iter+1]+'^'+spisokPow[iter],textRepl[:-1]+')')
            else:
                text=text.replace(spisokPow[iter+1]+'^'+spisokPow[iter],"pow("+spisokPow[iter+1]+','+spisokPow[iter]+")")
            iter+=2
    return text

#получаем из производной информацию о переменных по которым она находится и её степени (вспомогательный метод)
def replaceForProizv(self,text):
    i=0
    flagFunc=False
    flagDegree=False
    func=''
    degree=''
    while i<len(text)-1:
        i+=1
        if(text[i-1]=='['):
            flagFunc=True
        if i<len(text)-1:
            if text[i]==','  and (text[i-1].isdigit()==False or text[i+1].isdigit()==False):
                flagFunc=False
                flagDegree=True
        if flagFunc:
            func+=text[i]
        if flagDegree:
            degree+=text[i]
    var=[]
    deg=[]
    p=re.findall('{[^}]+}',degree)
    for iter in p:
        var.append(iter[1:-3])
        #искуственное ограничение на 9 производную
        deg.append(iter[-2])
    p=re.findall(',[^{},\]+]',degree)
    for iter in p:
        if iter[1:].isdigit():
            pass
        else:
            var.append(iter[1:])
            deg.append('1')
    return func,var[:],deg[:]

#подбераем замену для производной
#пока можно найти для 1-3 производной по 1-3 переменым 1-3 дифференцируемых функций
def FindZamena(self,dif,func,varProizv,var,degree,dirSource):
    #Выходной список
    spisokProizv=[]
    #Полная степень производной
    fullDegree=0
    #Находим Полную степень производной
    for i in degree: fullDegree+=int(i)
    #Вид производной т.е. U'x или V''yx
    strOut=''
    #Определяем производящую функцию
    if func=='%0':      strOut='U'
    elif func=='%1':    strOut='V'
    else:               strOut='W'
    #Добавляем количество ' равное общей степени производной
    for i in range(int(fullDegree)): strOut+="'"
    #Добавляем производящие переменные
    for i in range(len(varProizv)):
        if len(var)>=3:
            if varProizv[i]==var[2]:
                for i in range(int(degree[i])): strOut+="z"
            elif varProizv[i]==var[1]:
                for i in range(int(degree[i])): strOut+="y"
            else:
                for i in range(int(degree[i])): strOut+="x"
        elif len(var)==2:
            if varProizv[i]==var[1]:
                for i in range(int(degree[i])): strOut+="y"
            else:
                for i in range(int(degree[i])): strOut+="x"
        else:
            for i in range(int(degree[i])): strOut+="x"

    #Сортируем производящие переменные по убыванию в таком ввиде они указаны в файлах
    if len(strOut)==5:
        strOut=strOut[:3]+''.join(sorted(strOut[-2:]))[::-1]
    elif len(strOut)==7:
        strOut=strOut[:4]+''.join(sorted(strOut[-3:]))[::-1]

    print 'difpo',strOut

    #Общий файл с заменами
    file = open(os.path.join(dirSource,"difAll.txt"))
    t=file.read()
    zamena=t.split('@$next$@')
    file.close()
    #Текс файла полученый как список, преобразуем и ищем нужную часть
    for z in zamena:
        z=z.strip(' ')
        z=z.strip('\n')
        if z[:len(strOut)]==strOut:
            spisokProizv=z.splitlines() #Режем найденный текст в список
##    print spisokProizv
    #Первый элемент описание его не передаем
    return spisokProizv[1:]

def CompliteClient(self,dirFileRun,fileName):
##    print 'cl Source\\'+fileName
    if dirFileRun!="":
        dirFileRun=dirFileRun+"/"
    stdin, stdout, stderr=os.popen3('cl '+dirFileRun+fileName)
    out=stderr.read()
    if out=='':
        return u'VC: Файл скомпилирован в каталоге: '+dirFileRun
    else:
        stdin, stdout, stderr=os.popen3('g++ -c '+dirFileRun+fileName)
        out=stderr.read()
        if out=='':
            return u'MinGW: Файл скомпилирован в каталоге: '+dirFileRun
        else:
            return u'Ошибка компиляции: '+str(out).decode('utf-8')

#Вспомогательный метод
def parseEqu(self,text):
    text = text.replace(' ','')     #очищаем от пробелов
    equationArray = text.splitlines()    #режем текст на уравнения
    equation=[]     #Список уравнений
    for line in equationArray:
        splitLine = line.split(';')
        for elem in splitLine:
            if len(elem)>1:     #проверка на пустоту или символ ;
                equation.append(elem)
    return equation

#вычленяем дифференцируемые функции
def findDif(equ):
    #вычленяем дифференциалы
    dif=[]
    difSearch = re.findall("[A-Za-z]+\'",str(equ))
    for i in difSearch:
        dif.append(i[:-1])
    seen = set()
    result = []
    for x in dif:
        if x in seen:
            continue
        seen.add(x)
        result.append(x)
    return result

if __name__=='__main__':
    rgFile=RunGCFILE()

