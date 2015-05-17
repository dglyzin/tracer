# -*- coding: utf-8 -*-
import sys
import os
from numpy import arange, sin, pi
import re
import filecmp

funcList='acosh','asinh','atanh','acos','asin','atan','cos','exp','log','log10','sin','tan','tanh'
funcListReplace='acosh','asinh','atanh','acos','asin','atan','cos','exp','log','log10','sin','tan','tanh'

#/////////////////Находим переменые, дифференциалы и константы/////////////////#
class analysisSystem:
    def __init__(self):
        self.text=''
        self.dif=[]
        self.var=[]
        self.param=[]
        self.system=[]

    def setOutOfTheSystemComponents(self,text,varText):
        text=str(text)
        self.text=text
        self.system=parseEqu(self,text)
        global funcList
        #вычленяем переменные
        var=str(varText).split(',')
        while var.count('')>=1: var.remove('')
        #вычленяем дифференциалы
        dif=[]
        difSearch = re.findall("[A-Za-z]+\'",text)
        for i in difSearch:
            dif.append(i[:-1])
        #вычленяем переменные
        #общий список переменных
        paramVal=re.findall("[A-Za-z0-9]+",text)
        #список позиций для удаления
        listDVal=[]
        i=0
        for y in paramVal:
            #добавляем в список удаления значения находящиеся в списке переменных
            if var.count(y)>0: listDVal.append(i)
            #добавляем в список удаления значения находящиеся в списке дифференциалов
            if dif.count(y)>0: listDVal.append(i)
            #добавляем в список удаления значения находящиеся в списке функций
            if funcList.count(y)>0: listDVal.append(i)
            #добавляем в список удаления символ D, обрабатываем его потом отдельно
            if y=='D': listDVal.append(i)
            #есть ли у параметра хоть одна буква в названии
            if re.findall('[A-Za-z]',y):
                pass
            else:
                listDVal.append(i)
            i+=1
        #обрабатываем символ D
        if text.count('D[')!=text.count('D') and text.count('D[')>0:
            paramVal.append('D')

        #создаем список listForDel и в него добавляем элементы списка listDVal без повторений
        listForDel=[]
        for x in listDVal:
            if x not in listForDel:
                listForDel.append(x)

        listForDel.sort()   #сортируем
        listForDel.reverse()    #переворачиваем сортированый список

        #удаляем из списка paramVal значения на позициях из списка listForDel
        for x in listForDel:
            paramVal.pop(x)

        #создаем список param и в него добавляем элементы списка paramVal без повторений
        param=[]
        for x in paramVal:
            if x not in param:
                param.append(x)

        print dif[:],var[:],param[:]
        self.dif,self.var,self.param=dif[:],var[:],param[:]

def parseEqu(self,text):
    text = text.replace(' ','')     #очищаем от пробелов
    equationArray = text.split('\n')    #режем текст на уравнения
    equation=[]     #Список уравнений
    for line in equationArray:
        splitLine = line.split(';')
        for elem in splitLine:
            if len(elem)>1:     #проверка на пустоту или символ ;
                equation.append(elem)
    return equation

if  __name__ =='__main__':
    objRun = analysisSystem()
    objRun.setOutOfTheSystemComponents("U'=1+U^2*V-k1*U+a*(D[U,{x,2}]+D[U,{y,2}])\nV'=k2*U-U^2*V+a*(D[V,{x,2}]+D[V,{y,2}])",["x","y"])
    print objRun.dif,objRun.var,objRun.param,objRun.system,objRun.text
