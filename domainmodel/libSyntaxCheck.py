# -*- coding: utf-8 -*-
import sys
import os
from numpy import arange, sin, pi
import re
import filecmp

funcList='acosh','asinh','atanh','acos','asin','atan','cos','exp','log','log10','sin','tan','tanh'
funcListReplace='acosh','asinh','atanh','acos','asin','atan','cos','exp','log','log10','sin','tan','tanh'

#//////////////////////////////////////////////////////////////////////////////#
#/////////////////Часть кода связанная с проверкой синтаксиса//////////////////#
#//////////////////////////////////////////////////////////////////////////////#

def syntaxCheck(self,fullText):
    print u'Начало проверки синтаксиса'
    exitText=''     #выходная строка
    correct=True    #Корректность системы
    correctArray=[] #Корректность отдельного уравнения
    specialMessage=''   #сообщение об исключительной ситуации
    equation=parseEqu(self,fullText)
    #0-стадия отдельная обработка для символов <>" т.к. они есть в html тэге
    out=re.search(u"[А-Яа-я]",fullText)
    if '<' in fullText or '>' in fullText or '"' in fullText or out:
        return '',False, u'001 Не используйте буквы русского алфавита, а так же символы < > "'
    i=0
    for equ in equation:
        i+=1
        stroka,boolVal,errorText=sintaxEqu(self,equ)     #проверяем синтаксис уравнения
        exitText=exitText+stroka+'<br>'
        correctArray.append(boolVal)
        if errorText!='':
            specialMessage=unicode(specialMessage)+u'002 В '+unicode(str(i))+u' уравнении '+unicode(errorText)+u'<br>'
    if(correctArray.count(False)>0):    #если одно из уравнений некорректно
        correct=False
    return exitText, correct, specialMessage

#вызываем для каждого уравнения отдельно, анализируем и возвращаем
def sintaxEqu(sef,equ):
    correct=True
    errorText=''
    exitEqu=equ[:]
    #1-стадия корректность символов
    equ,exitEqu,flagVal=replaceTextAndSyntaxHighlight(u"[^A-Za-z0-9,.{}\[\]()='\^\\\*\+-]",equ,exitEqu)
    if flagVal==False:
        correct=False
    #конец 1 стадии
    #2-стадия проверяем синтаксис уравнения
    #-------проверяем единственность знака =
    if(equ.count('=')!=1):
        correct = False
        iterator =re.finditer('[=][^"]', str(equ))
        for match in iterator:
##            print match.group()
            exitEqu=exitEqu.replace(match.group(),'<font color="red">'
                                +match.group()[0]+'</font>'+match.group()[1])
    #-------проверяем ситуации связаные с знаком =
    equ,exitEqu,flagVal=replaceTextAndSyntaxHighlight(u"[^A-Za-z0-9'\]})]+[=]+[^A-Za-z0-9\[{(-]+|[^A-Za-z0-9'>\]})]+[=]+|[=]+[^A-Za-z0-9\[{(-]+",equ,exitEqu)
    if flagVal==False:
        correct=False
    #знак . в начале и в конце строчки
    if equ[0]=='=':
        exitEqu='<font color="red">'+'='+'</font>'+exitEqu[1:]
        correct=False
    if equ[-1]=='=':
        exitEqu=exitEqu[:-1]+'<font color="red">'+'='+'</font>'
        correct=False
    #-------проверяем знак .
    equ,exitEqu,flagVal=replaceTextAndSyntaxHighlight(u"[^0-9][.][^0-9]|[^0-9][.]|[.][^0-9]",equ,exitEqu)
    if flagVal==False:
        correct=False
    #знак . в начале и в конце строчки
    if equ[0]=='.' and str(equ[1]).isdigit():
        exitEqu='<font color="red">'+'.'+'</font>'+exitEqu[1:]
        correct=False
    if equ[-1]=='.' and str(equ[-2]).isdigit():
        exitEqu=exitEqu[:-1]+'<font color="red">'+'.'+'</font>'
        correct=False
    #-------проверяем знак '
    equ,exitEqu,flagVal=replaceTextAndSyntaxHighlight(u"[^A-Za-z']['][A-Za-z0-9|[{(]|[^A-Za-z'][']|['][A-Za-z0-9|[{(]",equ,exitEqu)
    if flagVal==False:
        correct=False
    if equ[0]=="'":
        exitEqu='<font color="red">'+"'"+'</font>'+exitEqu[1:]
        correct=False
    #-------проверяем знаки ^\*+- ({[ ]}) ,
    #ситуация два знака ^\*+- подряд
    equ,exitEqu,flagVal=replaceTextAndSyntaxHighlight(u"[\\\*\^+-]+[\\\*\^+-]+",equ,exitEqu)
    if flagVal==False:
        correct=False
    #ситуации ({[ и ^\*+- и ]}) или ({[ и знак ^\*+ или знак ^\*+ и ]})
    equ,exitEqu,flagVal=replaceTextAndSyntaxHighlight(u"[\(\{\[]+[\\\*\^+-]+[\)\}\]]+|[\(\{\[]+[\\\*\^+]+|[\\\*\^+]+[\]\)\}]+",equ,exitEqu)
    if flagVal==False:
        correct=False
    #ситуации ({[ и ]})
    equ,exitEqu,flagVal=replaceTextAndSyntaxHighlight(u"[\(\{\[]+[\)\}\]]+",equ,exitEqu)
    if flagVal==False:
        correct=False
    #ситуации ({[^\*+- и , и ]})^\*+- или ({[^\*+- и , или , и ]})^\*+-
    equ,exitEqu,flagVal=replaceTextAndSyntaxHighlight(u"[\(\{\[\\\*\^+-]+[,]+[\]\)\}\\\*\^+-]+|[\(\{\[\\\*\^+-]+[,]+|[,]+[\]\)\}\\\*\^+-]+",equ,exitEqu)
    if flagVal==False:
        correct=False
    #проверка на ^\*+-, в начале и конце строки
    #используем exitEqu по причине возможной ошибки для вариантов ^* в начале или конце строки
    #данная ситуация обрабатывается другим условием и происходит вложенное тэгирование
    if exitEqu[0]=="^" or exitEqu[0]=="\\" or exitEqu[0]=="*" or exitEqu[0]=="+" or exitEqu[0]=="-":
        exitEqu='<font color="red">'+exitEqu[0]+'</font>'+exitEqu[1:]
        correct=False
    if exitEqu[-1]=="^" or exitEqu[-1]=="\\" or exitEqu[-1]=="*" or exitEqu[-1]=="+" or exitEqu[-1]=="-":
        exitEqu=exitEqu[:-1]+'<font color="red">'+exitEqu[-1]+'</font>'
        correct=False
    #отсутствие ситуации буква+скобка, за исключением элементарных функций
    out=re.sub(u'(acosh|asinh|atanh|arccos|arcsin|arctan|cos|exp|log|log10|sin|tan|tanh)[\[({]','',str(equ))
    rezalt = re.findall(u"[A-CE-Za-ce-z0-9][\[({]|[A-Za-z][({]|[\])}][A-Za-z0-9]",out)
    if rezalt:
        correct=False
        outReport="'"
        for i in rezalt:
            outReport=outReport+i+"' "
        return exitEqu,correct,u"некорректное выражение "+outReport
    #конец 2 стадии
    #3-стадия логическая целостность уравнения
    #проверяем скобки
    errorText=analysisLineOnBrackets(equ)
    #конец 3 стадии
    return exitEqu,correct,errorText

#проверяем все моменты связаные с скобками
def analysisLineOnBrackets(text):
    outLine=''
    flagA=False
    flagB=False
    flagC=False
    valList=text.split('=')
    for val in valList:
        if val.count('[')!=val.count(']'):
            flagA=True
        if val.count('{')!=val.count('}'):
            flagB=True
        if val.count('(')!=val.count(')'):
            flagC=True
    if flagA: outLine+=' []'
    else:
        if lookingForOpenBrackets(val,'[',']'):
            outLine+=' []'
    if flagB: outLine+=' {}'
    else:
        if lookingForOpenBrackets(val,'{','}'):
            outLine+=' {}'
    if flagC: outLine+=' ()'
    else:
        if lookingForOpenBrackets(val,'(',')'):
            outLine+=' ()'
    if outLine!='':
        outLine=u'неправильно расставлены скобки'+outLine
    return outLine

#проверяем правильно раставлены скобки(побочный метод analysisLineOnBrackets)
def lookingForOpenBrackets(line,bracketOpen,bracketClose):
    balance=0
    for i in line:
        if i == bracketOpen:
            balance+=1
        if i == bracketOpen:
            balance-=1
        if balance<0:
            return True # неправильно расставлены скобки
    if balance>0:
            return True # неправильно расставлены скобки
    else:
        return False

#Ищем в textForSeach подстроки совпадающие с mask и делаем замену в textForReplace (вспомогательный метод)
def replaceTextAndSyntaxHighlight(mask,textForSeach,textForReplace):
    boolVal=True
    out = re.findall(mask,textForSeach)
    if out:
        boolVal = False
        for i in out:
            textForReplace=textForReplace.replace(i,'<font color="red">'+i+'</font>')
    else:
        pass
    return textForSeach,textForReplace,boolVal

#Достаем из текста уравнения (вспомогательный метод)
def parseEqu(self,text):
    text = text.replace(' ','')     #очищаем от пробелов
    equationArray = text.split('\n')    #режем текст на уравнения
    equation=[]     #Список уравнений
    for line in equationArray:
        splitLine = line.split(';')
        for elem in splitLine:
            if len(elem)>1:     #проверка на пустоту или символ ;
##                print unicode('=>' + elem)
                equation.append(elem)
##    print len(equation)
    return equation

#//////////////////////////////////////////////////////////////////////////////#
#/////////////////////Окончание метода проверки синтаксиса/////////////////////#
#//////////////////////////////////////////////////////////////////////////////#
