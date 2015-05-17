# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QIcon
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import arange, sin, pi
import re

class TextEquPanel(QtGui.QWidget):

    def __init__(self, parent=None):
        super(TextEquPanel, self).__init__(parent)
        self.parent = parent

        self.initUI()

    def initUI(self):

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        self.titleEqu = QtGui.QLabel(u'Введите систему')
        grid.addWidget(self.titleEqu, 0, 0)

##        runHelp = QtGui.QPushButton(QIcon("images/question.png".format("help")), '', self)
##        grid.addWidget(runHelp, 0, 1)

        f = open('textSecret.txt')
        textSecretLabel=f.read()
        f.close()

        self.setToolTip(textSecretLabel.decode('cp1251'))
        QtGui.QToolTip.setFont(QtGui.QFont('Arial', 10))

        self.textEqu = QtGui.QTextEdit()
        grid.addWidget(self.textEqu, 1, 0, 1, 2)
        self.textEqu.setFontWeight(14)
        self.textEqu.setText("U'=1+U^2*V-k1*U+a*(D[U,{x,2}]+D[U,{y,2}]) <br> V'=k2*U-U^2*V+a*(D[V,{x,2}]+D[V,{y,2}])")
##        self.connect(textEqu, QtCore.SIGNAL('textChanged()'),self.sintaxText)

        self.titleValue = QtGui.QLabel(u'Укажите пространственные переменные')
        grid.addWidget(self.titleValue, 2, 0, 1, 2)

        value=['x','y','z','']

        self.comboValue1 = QtGui.QComboBox(self)
        for elem in value:
            self.comboValue1.addItem(str(elem))
        self.comboValue1.setEditable(True)
        grid.addWidget(self.comboValue1, 3, 0)

        self.comboValue2 = QtGui.QComboBox(self)
        for elem in value:
            self.comboValue2.addItem(str(elem))
        self.comboValue2.setEditable(True)
        grid.addWidget(self.comboValue2, 3, 1)

        insertBu =  QtGui.QPushButton(u'Вставить элемент', self)
        grid.addWidget(insertBu, 4, 0)
        self.connect(insertBu, QtCore.SIGNAL('clicked()'),self.addtext)

        elemFunc=['acosh()','asinh()','atanh()','arccos(...)','arcsin(...)','arctan(...)','cos(...)','D[f[x], {x, n}]','exp()','log{a,b}','log10{b}','sin(...)','tan(...)','tanh(...)']
        self.comboAddText = QtGui.QComboBox(self)
        for elem in elemFunc:
            self.comboAddText.addItem(str(elem))
        grid.addWidget(self.comboAddText, 4, 1)

        runEqu = QtGui.QPushButton(u'Вычислить', self)
        grid.addWidget(runEqu, 5, 0, 1, 2)
        self.connect(runEqu, QtCore.SIGNAL('clicked()'),self.sintaxText)

        self.setLayout(grid)
        self.resize(350, 300)


##      Начало основного метода
    def sintaxText(self):
        textInput=self.textEqu.toPlainText()
        textInput = textInput.replace(' ','')
        equationArray = textInput.split('\n')
        equation=[]
        for line in equationArray:
            splitLine = line.split(';')
            for elem in splitLine:
##                print '=>', elem
                equation.append(elem)
        i=0
        while i < len(equation):
           if len(equation[i]) < 1:
	          del equation[i]
           else:
	          i += 1
        self.textEqu.clear()
        for elem in equation:
##            print elem, len(elem)
##            self.textEqu.append(elem)
            self.sintaxEquStage1(elem)

        self.runGenCfile()

#    Run gen C file
    def runGenCfile(self):
        listParamForTempl = ['$@sistemUpL@$','$@sistemUpC@$','$@sistemUpR@$',
                    '$@sistemCentrL@$','$@sistemCentrC@$','$@sistemCentrR@$',
                    '$@sistemDownL@$','$@sistemDownC@$','$@sistemDownR@$']
        listEquForTemplate = []

#       Список всех ключевых букв
        dif,value,param=self.returnOutEquation()

        rezDif=self.FindZamena(dif,value)

        for i in range(9):
            listEquForTemplate.append(rezDif[i]+';\n  '+rezDif[i+9]+';')
            print rezDif[i]+rezDif[i+9]
##            listEquForTemplate.append(str(i))
##            print listEquForTemplate[i]

        f = open('brusTemplate.c')
        fout = open("brus.c", "wt")
        textTemplateC=f.read()
        f.close()
##        print textTemplateC, len(textTemplateC)

        strParam=''
        for i in param:
            strParam+='#define ' + i + ' 4.4 \n'
        textTemplateC=textTemplateC.replace('$@param@$',strParam)

        for i in range(len(listEquForTemplate)):
##            print listParamForTempl[i],listEquForTemplate[i]
            textTemplateC=textTemplateC.replace(listParamForTempl[i],listEquForTemplate[i])

        fout.write(textTemplateC)
        fout.close()

#       Возвращаем внутрение строчки для замены в шаблоне
#       Дифференциал
#       [A-Za-z]\'
#       Одна буква не берем D отдельно обрабатываем начало и конец строки
#       [^A-Za-z][A-CE-Za-ce-z][^A-Za-z]
#       Производная
#       D\[[A-Za-z0-9,.{}()\^\\\*\+-]+\]
    def returnOutEquation(self):
        textInput=str(self.textEqu.toPlainText())
        dif=[]
        value=[]
        param=[]
        dif = re.findall("[A-Za-z]\'",textInput)
        for i in dif: print i, len(dif)

        param = re.findall("[^A-Za-z]?[A-CE-Za-ce-z][^A-Za-z]",textInput)
        for i in range(len(param)):
            print 'write ',param[i]
            if str(param[i])[-1:].isdigit():
                param[i]=str(param[i])[-2:]
            else:
                param[i]=str(param[i])[-2:-1]

##        print textInput[0]
        if (str(textInput[0]).isalpha() and str(textInput[1]).isalpha()==False and textInput[0]!='D'):
##            print 'tgggg', textInput[0]
            param.append(textInput[0])

        print textInput[len(str(textInput))-1]
        lastSim=len(str(textInput))-1
        if (str(textInput[lastSim]).isalpha() and str(textInput[lastSim-1]).isalpha()==False and textInput[lastSim]!='D'):
##            print 'tqqqq', textInput[lastSim]
            param.append(textInput[lastSim])

##        for i in param: print 'param1', i, len(param)

        val1=str(self.comboValue1.currentText())
        val2=str(self.comboValue2.currentText())
        if val1!='':
            value.append(val1)

        if val2!='' and val1!=val2:
            value.append(val2)

        while param.count(val1)>=1: param.remove(val1)
        while param.count(val2)>=1: param.remove(val2)
        for i in dif:
            while param.count(i[0])>=1: param.remove(i[0])

        for i in param:
            while param.count(i)>1: param.remove(i)

##        for i in dif: print 'dif', i, len(dif)
##        for i in value: print 'value', i, len(value)
        for i in param: print 'param2', i, len(param)

        return dif,value,param

#       Создаем уравнения для замены
    def FindZamena(self,dif,value):
        returnEqu=[]
        textInput=str(self.textEqu.toPlainText())
        equationArray = textInput.split('\n')
        for equ in equationArray:
            for i in range(len(dif)):
                equ=equ.replace(dif[i],'$'+str(i))    # $ - r[idx]
                equ=equ.replace(str(dif[i])[0],'%'+str(i))    # % - s[idx]

            finalEqu=[equ]*9

            proizv = re.findall("D\[[A-Za-z0-9$%,.{}()\^\\\*\+-]+\]",equ)
            for iProizv in proizv:
                print iProizv
                stepen=0
                valueStepen=''
                valueProiz1 = re.findall("{.+?}",iProizv)
                for j in valueProiz1:
##                    print j
                    stepen+=int(j[3])
                    valueStepen+=j[1]
                valueProiz2 = re.findall(",[A-Za-z]",iProizv)
                for j in valueProiz2:
##                    print j
                    stepen+=1
                    valueStepen+=j[1]
                print u'Степень', stepen, valueStepen, len(valueStepen)

#
#               Написать вариацию для производной по x^2, y^2, x, y
#

                if stepen==2 and len(valueStepen)==1:
                    valueProiz3 = re.findall("%[0-9]",iProizv)
                    if valueStepen==value[0]: # т.е. производная {x,2}
                        for k in valueProiz3:
                            print k
                            if k=='%0':
                                spisokProizv=[
                                '(N-1)*(s[idx+2*N]+s[idx+2]- 2.0*s[idx])',
                                '(N-1)*(s[idx+2*N]+s[idx+2]- 2.0*s[idx])',
                                '(N-1)*(s[idx+2*N]+s[idx-2]- 2.0*s[idx])',
                                '(N-1)*(s[idx+2*N]+s[idx+2]- 2.0*s[idx])',
                                '(N-1)*(s[idx+2*N]+s[idx+2]- 2.0*s[idx])',
                                '(N-1)*(s[idx+2*N]+s[idx-2]- 2.0*s[idx])',
                                '(N-1)*(s[idx-2*N]+s[idx+2]- 2.0*s[idx])',
                                '(N-1)*(s[idx-2*N]+s[idx+2]- 2.0*s[idx])',
                                '(N-1)*(s[idx-2*N]+s[idx-2]- 2.0*s[idx])'
                                ]
                            else:
                                if k=='%1':
                                    spisokProizv=[
                                    '(N-1)*(s[idx+2*N+1]+s[idx+2+1]- 2.0*s[idx+1])',
                                    '(N-1)*(s[idx+2*N+1]+s[idx+2+1]- 2.0*s[idx+1])',
                                    '(N-1)*(s[idx+2*N+1]+s[idx-2+1]- 2.0*s[idx+1])',
                                    '(N-1)*(s[idx+2*N+1]+s[idx+2+1]- 2.0*s[idx+1])',
                                    '(N-1)*(s[idx+2*N+1]+s[idx+2+1]- 2.0*s[idx+1])',
                                    '(N-1)*(s[idx+2*N+1]+s[idx-2+1]- 2.0*s[idx+1])',
                                    '(N-1)*(s[idx-2*N+1]+s[idx+2+1]- 2.0*s[idx+1])',
                                    '(N-1)*(s[idx-2*N+1]+s[idx+2+1]- 2.0*s[idx+1])',
                                    '(N-1)*(s[idx-2*N+1]+s[idx-2+1]- 2.0*s[idx+1])'
                                    ]
                    else:
                        if valueStepen==value[1]: # т.е. производная {y,2}
                            for k in valueProiz3:
                                print k
                                if k=='%0':
                                    spisokProizv=[
                                    '(N-1)*(s[idx+2*N]+s[idx+2]- 2.0*s[idx])',
                                    '(N-1)*(s[idx+2*N]+s[idx-2]- 2.0*s[idx])',
                                    '(N-1)*(s[idx+2*N]+s[idx-2]- 2.0*s[idx])',
                                    '(N-1)*(s[idx-2*N]+s[idx+2]- 2.0*s[idx])',
                                    '(N-1)*(s[idx-2*N]+s[idx-2]- 2.0*s[idx])',
                                    '(N-1)*(s[idx-2*N]+s[idx-2]- 2.0*s[idx])',
                                    '(N-1)*(s[idx-2*N]+s[idx+2]- 2.0*s[idx])',
                                    '(N-1)*(s[idx-2*N]+s[idx-2]- 2.0*s[idx])',
                                    '(N-1)*(s[idx-2*N]+s[idx-2]- 2.0*s[idx])'
                                    ]
                                else:
                                    if k=='%1':
                                        spisokProizv=[
                                        '(N-1)*(s[idx+2*N+1]+s[idx+2+1]- 2.0*s[idx+1])',
                                        '(N-1)*(s[idx+2*N+1]+s[idx-2+1]- 2.0*s[idx+1])',
                                        '(N-1)*(s[idx+2*N+1]+s[idx-2+1]- 2.0*s[idx+1])',
                                        '(N-1)*(s[idx-2*N+1]+s[idx+2+1]- 2.0*s[idx+1])',
                                        '(N-1)*(s[idx-2*N+1]+s[idx-2+1]- 2.0*s[idx+1])',
                                        '(N-1)*(s[idx-2*N+1]+s[idx-2+1]- 2.0*s[idx+1])',
                                        '(N-1)*(s[idx-2*N+1]+s[idx+2+1]- 2.0*s[idx+1])',
                                        '(N-1)*(s[idx-2*N+1]+s[idx-2+1]- 2.0*s[idx+1])',
                                        '(N-1)*(s[idx-2*N+1]+s[idx-2+1]- 2.0*s[idx+1])'
                                        ]

                    for z in range(len(spisokProizv)):
                        finalEqu[z]=finalEqu[z].replace(iProizv,spisokProizv[z])

            for i in finalEqu:
                i=i.replace('$0','r[idx]')    # $ - r[idx]
                i=i.replace('%0','s[idx]')    # % - s[idx]

                i=i.replace('$1','r[idx+1]')    # $ - r[idx+1]
                i=i.replace('%1','s[idx+1]')    # % - s[idx+1]
##                print 'equ', i
                returnEqu.append(i)

        for i in returnEqu:
            print 'equ', i

        return returnEqu

#Производная
#D\[[A-Za-z0-9,.{}()\^\\\*\+-]+\]
#Не правильный символ
#[^A-Za-z0-9,.{}\[\]()='\^\\\*\+-]
#      Проверка на некорректные символы и правильное расположение знаков
    def sintaxEquStage1(self,equ):
##        badSimbol = re.compile("[^A-Za-z0-9,.{}\[\]()='\^\\\*\+-]")
##        erText = badSimbol.search(equ)
        erText = re.findall("[^A-Za-z0-9,.{}\[\]()='\^\\\*\+-]",equ)
        if erText:
            for i in erText:
                equ=equ.replace(i,'<font color="red">'+i+'</font>')
            self.textEqu.append(equ)
            QtGui.QMessageBox.warning (self, u'Предупреждение',
            u"Введена некорректная система", QtGui.QMessageBox.Ok)
        else:
            if equ.count('=')==1:
                erText1 = re.findall("[^A-Za-z0-9'})\]]+=",equ)
                erText2 = re.findall("=[{\[(-]*[^A-Za-z0-9]+",equ)
                #Поправить правило erText2
                if erText1 or erText2:
                    equ=equ.replace('=','<font color="red">=</font>')
                    self.textEqu.append(equ)
                    QtGui.QMessageBox.warning (self, u'Предупреждение',
                    u"Введена некорректная система", QtGui.QMessageBox.Ok)
                else:
                    self.textEqu.append(equ)
                    self.sintaxEquStage2(equ)
            else:
                self.textEqu.append(equ)
                QtGui.QMessageBox.warning (self, u'Предупреждение',
                    u"Введена некорректная система", QtGui.QMessageBox.Ok)

#Нужны проверки:
#элементарных функций
#правильное расположение знаков(+-*\=',()[]
    def sintaxEquStage2(self,equ):
        letter = re.compile("[A-Za-z]+")
        simbols = letter.findall(equ)
        for i in simbols:
            print i     #проверка элементарных функций, проверка на одно равно(не первым и не последним символом)

#Вставка текста
    def addtext(self):
        self.textEqu.insertPlainText(str(self.comboAddText.currentText()))

def main():

    app = QtGui.QApplication(sys.argv)
    ex = TextEquPanel()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
