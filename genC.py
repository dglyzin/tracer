# -*- coding: utf-8 -*-
import sys, os, json,datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import re
sys.path.insert(0, os.curdir+"/domainmodel")
import libGenerateC
import libGenerateJSON
import libSyntaxCheck
import libAnalysisSystem
import cluster_connection as cluster

class BaseWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.centralWidget = QtGui.QWidget()
        self.resize(800, 275)
        self.setWindowTitle(u'Создать решение системы')

        self.programDate={"dif":[],"var":[],"param":[],"system":[],
                            "Initials":[],"Blocks":[],"Bounds":[],"Interconnects":[],
                            "ProjectName":"New_project",
                            "StartTime": 0.0,"FinishTime": 0.5,
                            "TimeStep": 0.02,"SaveInterval": 0.1,"GridStep": {},
                            "Hardware": [{"Name": "cnode1", "CpuCount": 1, "GpuCount": 3}, {"Name": "cnode2", "CpuCount": 1, "GpuCount": 3}],
                            "Mapping": {"IsMapped": "true", "BlockMapping": [[0, "cpu", 0]]}}
        self.sisChanged=False
        self.tabControl=0

        #Создаем вкладки программы
        self.tabs = QTabWidget()
        self.tabs.blockSignals(True) #just for not showing the initial message
        self.tabs.currentChanged.connect(self.onChange) #changed!
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()
        self.tab7 = QWidget()
        self.tab8 = QWidget()
        self.mainWindow = QtGui.QVBoxLayout()
        self.mainWindow.addWidget(self.tabs, 1)
        self.tabs.addTab(self.tab1, u"Система")
        self.tabs.addTab(self.tab2, u"Параметры")
        self.tabs.addTab(self.tab4, u"Начальные условия")
        self.tabs.addTab(self.tab3, u"Области вычисления")
        self.tabs.addTab(self.tab5, u"Границы")
        self.tabs.addTab(self.tab6, u"Доп. усл. на области")
        self.tabs.addTab(self.tab7, u"Связь блоков")
        self.tabs.addTab(self.tab8, u"Настройки")
        self.centralWidget.setLayout(self.mainWindow)
        self.setCentralWidget(self.centralWidget)

        self.tabs.blockSignals(False) #now listen the currentChanged signal

        #Открываем файл настроек
        f = open(os.path.join("config","configGenC.txt"))
        self.dictConfig = json.loads(f.read())
        f.close()

##        print self.dictConfig

        self.setToolTip(self.dictConfig["helpTextList1"])
        QtGui.QToolTip.setFont(QtGui.QFont('Arial', 10))

#_______Первая вкладка <Система>
        self.list1 = QtGui.QGridLayout()
        self.updateList1()
        self.tab1.setLayout(self.list1)

#_______Вторая вкладка <Параметры>
        self.list2 = QtGui.QGridLayout()
        self.dictParam={}
        self.tab2.setLayout(self.list2)

#_______Третья вкладка <Области вычисления>
        self.list3 = QtGui.QGridLayout()
        self.dictBlocksXYZ={}
        self.tab3.setLayout(self.list3)

#_______Четвертая вкладка <Начальные значения>
        self.list4 = QtGui.QGridLayout()
        self.listCondition=[]
        self.tab4.setLayout(self.list4)

#_______Пятая вкладка <Границы>
        self.list5 = QtGui.QGridLayout()
        self.listBounds=[]
        self.tab5.setLayout(self.list5)

#_______Шестая вкладка <Доп. усл. на области>
        self.list6 = QtGui.QGridLayout()
        self.dictBlocksXYZSp={}
        self.dictInitXYZSp={}
        self.tab6.setLayout(self.list6)

#_______Седьмая вкладка <Связь блоков>
        self.list7 = QtGui.QGridLayout()
        self.dictGridStep={}
        self.tab7.setLayout(self.list7)

#_______Восьмая вкладка <Настройки>
        self.list8 = QtGui.QGridLayout()
        self.tab8.setLayout(self.list8)

    def onChange(self,i):
        if self.tabControl==0: self.sistemCheck()
        if self.tabControl==1: self.fillParam()
        if self.tabControl==2: self.fillBlocks()
        if self.tabControl==3: self.fillCondition()
        if self.tabControl==4: self.fillBound()
        if self.tabControl==5: self.fillInitSp()
        if self.tabControl==7: self.fillConfig()

        if i==0: self.setToolTip(self.dictConfig["helpTextList1"])
        if i==1:
            self.setToolTip(self.dictConfig["helpTextList2"])
            self.updateList2()
        if i==2:
            self.setToolTip(self.dictConfig["helpTextList3"])
            self.updateList3()
        if i==3:
            self.setToolTip(self.dictConfig["helpTextList4"])
            self.updateList4()
        if i==4:
            self.setToolTip(self.dictConfig["helpTextList5"])
            self.updateList5()
        if i==5:
            self.setToolTip(self.dictConfig["helpTextList6"])
            self.updateList6()
        if i==6:
            self.setToolTip(self.dictConfig["helpTextList7"])
            self.updateList7()
        if i==7:
            self.setToolTip(self.dictConfig["helpTextList8"])
            self.updateList8()

        print self.tabControl
        self.tabControl=i

#_______Первая вкладка <Система>
    def updateList1(self):
        self.titleEqu = QtGui.QLabel(u'Введите систему')
        self.list1.addWidget(self.titleEqu, 0, 0,1,1)

        #Выбор уравнения из списка примеров
        self.comboEqu = QtGui.QComboBox(self)
        iter=0
        self.comboEqu.addItem(u'')

        list=os.listdir("config")
        lenList=str(list).count("example_")
        print lenList

        for elem in range(lenList):
            iter+=1
            self.comboEqu.addItem(u'Пример '+str(iter))
        self.list1.addWidget(self.comboEqu, 0, 1,1,1)
        self.comboEqu.currentIndexChanged['QString'].connect(self.useTemplate)

        #Введеная система
        self.textInputSystem = QtGui.QTextEdit()
        self.list1.addWidget(self.textInputSystem, 1, 0, 1, 2)
        self.textInputSystem.setFontWeight(14)
        self.textInputSystem.setText(self.comboEqu.currentText())

        self.titleValue = QtGui.QLabel(u'Укажите переменные через запятую')
        self.list1.addWidget(self.titleValue, 2, 0, 1, 1)

        #Список переменных
        value=['x,y','x,y,z','']
        self.comboValue = QtGui.QComboBox(self)
        for elem in value:
            self.comboValue.addItem(str(elem))
        self.comboValue.setEditable(True)
        self.list1.addWidget(self.comboValue, 2, 1,1,1)

		#кнопка добавления шаблона функции
        self.insertTemplate =  QtGui.QPushButton(u'Вставить элемент', self)
        self.list1.addWidget(self.insertTemplate, 4, 0)
        self.insertTemplate.setEnabled(False)
        self.connect(self.insertTemplate, QtCore.SIGNAL('clicked()'),self.addtext)

        #список функций подстановки
        elemFunc=['','acosh(...)','asinh(...)','atanh(...)','acos(...)','asin(...)','atan(...)','cos(...)','D[f[x], {x, n}]','exp(...)','log(a,b)','log10(b)','sin(...)','tan(...)','tanh(...)']
        self.comboAddFunc = QtGui.QComboBox(self)
        for elem in elemFunc:
            self.comboAddFunc.addItem(str(elem))
        self.list1.addWidget(self.comboAddFunc, 4, 1)
        self.comboAddFunc.currentIndexChanged['QString'].connect(self.addTextButton)

        value=['Вычислить локально','Вычислить на кластере']
        self.comboRunValue = QtGui.QComboBox(self)
        for elem in value:
            self.comboRunValue.addItem(str(elem).decode('utf-8'))
        self.list1.addWidget(self.comboRunValue, 5, 1, 1, 1)

        #кнопка вызова основного метода
        runEqu = QtGui.QPushButton(u'Вычислить', self)
        self.list1.addWidget(runEqu, 5, 0, 1, 1)
        self.connect(runEqu, QtCore.SIGNAL('clicked()'),self.mainCode)


#_______Вторая вкладка <Параметры>
    def updateList2(self):
        for i in reversed(range(self.list2.count())):
            self.list2.itemAt(i).widget().setParent(None)

        pos=0
        self.titleDialog = QtGui.QLabel(u'Определите значения параметров')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list2.addWidget(self.titleDialog, pos, 0,1,1)

        self.dictParam={}
        if len(self.programDate["param"])>0:
            for key, value in self.programDate["param"][0].items():
                pos+=1
                self.nameParam = QtGui.QLabel(str(key))
                self.nameParam.setAlignment(QtCore.Qt.AlignLeft)
                self.list2.addWidget(self.nameParam, pos, 0)

                self.textParam = QtGui.QLineEdit()
                self.textParam.setValidator(QtGui.QDoubleValidator())
                self.textParam.setAlignment(QtCore.Qt.AlignLeft)
                self.textParam.setText(str(value))
                self.list2.addWidget(self.textParam, pos, 1)
                self.dictParam[str(self.nameParam.text())]=self.textParam

###############################################################################################
#_______Третья вкладка <Области вычисления>
    def updateList3(self):
        for i in reversed(range(self.list3.count())):
            self.list3.itemAt(i).widget().setParent(None)

        self.titleDialog = QtGui.QLabel(u'Определите границы области')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list3.addWidget(self.titleDialog, 0, 0)

        pos=1
        self.title = QtGui.QLabel(u'Имя области')
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.list3.addWidget(self.title, pos, 0, 1, 1)

        self.textBlockName = QtGui.QLineEdit()
        self.list3.addWidget(self.textBlockName, pos, 1, 1, 1)

        pos+=1
        self.dictBlocksXYZ={}
        for i in range(len(self.programDate["var"])):
            self.labelV = QtGui.QLabel(self.programDate["var"][i])
            self.labelV.setAlignment(QtCore.Qt.AlignLeft)
            self.list3.addWidget(self.labelV, pos, 0,1,1)

            self.textBlockSt = QtGui.QLineEdit()
            self.list3.addWidget(self.textBlockSt, pos, 1, 1, 1)

            self.textBlockEnd = QtGui.QLineEdit()
            self.list3.addWidget(self.textBlockEnd, pos, 2, 1, 1)
            self.dictBlocksXYZ[str(self.labelV.text())]=[self.textBlockSt,self.textBlockEnd]
            pos+=1

        pos+=1
        self.label = QtGui.QLabel(u"Начальное условие")
        self.label.setAlignment(QtCore.Qt.AlignLeft)
        self.list3.addWidget(self.label, pos, 0,1,1)

        self.comboInitials = QtGui.QComboBox(self)
        for elem in self.programDate["Initials"]:
            self.comboInitials.addItem(elem["Name"].decode('utf-8'))    #+str(elem["Values"][:]).replace("u'","'")
        self.comboInitials.setEditable(False)
        self.list3.addWidget(self.comboInitials, pos, 1,1,1)

        pos+=1
        self.insertCondition =  QtGui.QPushButton(u'Добавить область для расчета', self)
        self.list3.addWidget(self.insertCondition, pos, 0, 1, 3)
        self.insertCondition.setEnabled(True)
        self.connect(self.insertCondition, QtCore.SIGNAL('clicked()'),self.addBlocks)

        pos+=1
        self.label = QtGui.QLabel(u'Редактор областей для расчета')
        self.label.setAlignment(QtCore.Qt.AlignLeft)
        self.list3.addWidget(self.label, pos, 0, 1, 3)

        pos+=1
        self.textFullBlocks = QtGui.QTextEdit()
        self.textFullBlocks.setText(str(self.programDate["Blocks"][:])[1:-1].replace("u'","'"))
        self.list3.addWidget(self.textFullBlocks, pos, 0, 1, 3)
###############################################################################################

#_______Четвертая вкладка <Начальные значения>
    def updateList4(self):
        for i in reversed(range(self.list4.count())):
            self.list4.itemAt(i).widget().setParent(None)

        self.titleDialog = QtGui.QLabel(u'Определите начальные значения')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list4.addWidget(self.titleDialog, 0, 0)

        pos=1
        self.title = QtGui.QLabel(u'Имя')
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.list4.addWidget(self.title, pos, 0, 1, 1)

        self.textConditionName = QtGui.QLineEdit()
        self.list4.addWidget(self.textConditionName, pos, 1, 1, 1)

        pos+=1
        self.listCondition=[]
        for i in range(len(self.programDate["system"])):
            self.label = QtGui.QLabel(u'Начальное условие для уравнения '+str(i+1))
            self.label.setAlignment(QtCore.Qt.AlignLeft)
            self.list4.addWidget(self.label, pos, 0,1,1)

            self.textCond = QtGui.QLineEdit()
            self.listCondition.append(self.textCond)
            self.list4.addWidget(self.textCond, pos, 1, 1, 1)
            pos+=1

        self.insertCondition =  QtGui.QPushButton(u'Добавить условие', self)
        self.list4.addWidget(self.insertCondition, pos+1, 0, 1, 2)
        self.insertCondition.setEnabled(True)
        self.connect(self.insertCondition, QtCore.SIGNAL('clicked()'),self.addCondition)

        self.label = QtGui.QLabel(u'Редактор начальных значений')
        self.label.setAlignment(QtCore.Qt.AlignLeft)
        self.list4.addWidget(self.label, pos+2, 0, 1, 1)

        self.textFullCondition = QtGui.QTextEdit()
        self.textFullCondition.setText(str(self.programDate["Initials"][:])[1:-1].replace("u'","'"))
        self.list4.addWidget(self.textFullCondition, pos+3, 0, 1, 2)

#_______Пятая вкладка <Границы>
    def updateList5(self):
        for i in reversed(range(self.list5.count())):
            self.list5.itemAt(i).widget().setParent(None)

        self.titleDialog = QtGui.QLabel(u'Определите граничные условия')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list5.addWidget(self.titleDialog, 0, 0)

        pos=1
        self.title = QtGui.QLabel(u'Имя')
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.list5.addWidget(self.title, pos, 0, 1, 1)

        self.textBoundsName = QtGui.QLineEdit()
        self.list5.addWidget(self.textBoundsName, pos, 1, 1, 1)

        pos+=1
        self.listBounds=[]
        for i in range(len(self.programDate["var"])):
            self.labelB = QtGui.QLabel(u'Граничное условие по '+self.programDate["var"][i])
            self.labelB.setAlignment(QtCore.Qt.AlignLeft)
            self.list5.addWidget(self.labelB, pos, 0,1,1)

            self.textBound = QtGui.QLineEdit()
            self.list5.addWidget(self.textBound, pos, 1, 1, 1)

            self.listBounds.append(self.textBound)
            pos+=1

        pos+=1
        self.comboBoundCondition = QtGui.QComboBox(self)
        value=['Дирихле','Нейман']
        for elem in value:
            self.comboBoundCondition.addItem(elem.decode('utf-8'))
        self.comboBoundCondition.setEditable(False)
        self.list5.addWidget(self.comboBoundCondition, pos, 0,1,1)

        pos+=1
        self.insertBound =  QtGui.QPushButton(u'Добавить граничное условие', self)
        self.list5.addWidget(self.insertBound, pos, 0, 1, 3)
        self.insertBound.setEnabled(True)
        self.connect(self.insertBound, QtCore.SIGNAL('clicked()'),self.addBound)

        pos+=1
        self.label = QtGui.QLabel(u'Редактор краевых условий')
        self.label.setAlignment(QtCore.Qt.AlignLeft)
        self.list5.addWidget(self.label, pos, 0, 1, 3)

        pos+=1
        self.textFullBound = QtGui.QTextEdit()
        self.textFullBound.setText(str(self.programDate["Bounds"][:])[1:-1].replace("u'","'"))
        self.list5.addWidget(self.textFullBound, pos, 0, 1, 3)

#_______Шестая вкладка <Доп. усл. на области>
    def updateList6(self):
        for i in reversed(range(self.list6.count())):
            self.list6.itemAt(i).widget().setParent(None)

        pos=1
        self.titleDialog = QtGui.QLabel(u'Выбирите блок')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list6.addWidget(self.titleDialog, pos, 0,1,1)

        self.comboBlockCondition = QtGui.QComboBox(self)
        for elem in self.programDate["Blocks"]:
            self.comboBlockCondition.addItem(elem["Name"])
        self.list6.addWidget(self.comboBlockCondition, pos, 1,1,1)

        pos+=1
        self.title = QtGui.QLabel(u'Выбирите граничное условие')
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.list6.addWidget(self.title, pos, 0,1,1)

        self.comboBoundCond = QtGui.QComboBox(self)
        for elem in self.programDate["Bounds"]:
            self.comboBoundCond.addItem(elem["Name"])
        self.list6.addWidget(self.comboBoundCond, pos, 1,1,1)

        pos+=1
        self.title = QtGui.QLabel(u'Выбирите сторону')
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.list6.addWidget(self.title, pos, 0,1,1)

        self.comboSideCondition = QtGui.QComboBox(self)
        value=[u'Левая грань',u'Верхняя грань',u'Правая грань',u'Нижняя грань']
        for elem in value:
            self.comboSideCondition.addItem(elem)
        self.list6.addWidget(self.comboSideCondition, pos, 1,1,1)

        self.dictBlocksXYZSp={}
        for i in range(len(self.programDate["var"])):
            pos+=1
            self.labelV = QtGui.QLabel(self.programDate["var"][i])
            self.labelV.setAlignment(QtCore.Qt.AlignLeft)
            self.list6.addWidget(self.labelV, pos, 0,1,1)

            self.textBlockStSp = QtGui.QLineEdit()
            self.list6.addWidget(self.textBlockStSp, pos, 1, 1, 1)

            self.textBlockEndSp = QtGui.QLineEdit()
            self.list6.addWidget(self.textBlockEndSp, pos, 2, 1, 1)
            self.dictBlocksXYZSp[str(self.labelV.text())]=[self.textBlockStSp,self.textBlockEndSp]

        pos+=1
        self.insertBoundSp =  QtGui.QPushButton(u'Определить граничные условия для блока', self)
        self.list6.addWidget(self.insertBoundSp, pos, 0, 1, 3)
        self.connect(self.insertBoundSp, QtCore.SIGNAL('clicked()'),self.addBlockSp)

        pos+=1
        self.title = QtGui.QLabel(u'Выбирите начальное условие')
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.list6.addWidget(self.title, pos, 0,1,1)

        self.comboInitCond = QtGui.QComboBox(self)
        for elem in self.programDate["Initials"]:
            self.comboInitCond.addItem(elem["Name"])
        self.list6.addWidget(self.comboInitCond, pos, 1,1,1)

        self.dictInitXYZSp={}
        for i in range(len(self.programDate["var"])):
            pos+=1
            self.labelI = QtGui.QLabel(self.programDate["var"][i])
            self.labelI.setAlignment(QtCore.Qt.AlignLeft)
            self.list6.addWidget(self.labelI, pos, 0,1,1)

            self.textInitStSp = QtGui.QLineEdit()
            self.list6.addWidget(self.textInitStSp, pos, 1, 1, 1)

            self.textInitEndSp = QtGui.QLineEdit()
            self.list6.addWidget(self.textInitEndSp, pos, 2, 1, 1)
            self.dictInitXYZSp[str(self.labelI.text())]=[self.textInitStSp,self.textInitEndSp]

        pos+=1
        self.insertInitSp =  QtGui.QPushButton(u'Определить начальные условия для блока', self)
        self.list6.addWidget(self.insertInitSp, pos, 0, 1, 3)
        self.connect(self.insertInitSp, QtCore.SIGNAL('clicked()'),self.addInitSp)

        pos+=1
        self.label = QtGui.QLabel(u'Редактор особых условий')
        self.label.setAlignment(QtCore.Qt.AlignLeft)
        self.list6.addWidget(self.label, pos, 0, 1, 3)

        pos+=1
        self.textFullBoundSp = QtGui.QTextEdit()
        self.textFullBoundSp.setText(str(self.programDate["Blocks"][:])[1:-1].replace("u'","'"))
        self.list6.addWidget(self.textFullBoundSp, pos, 0, 1, 3)

#_______Седьмая вкладка <Связь блоков>
    def updateList7(self):
        for i in reversed(range(self.list7.count())):
            self.list7.itemAt(i).widget().setParent(None)

        pos=1
        self.title = QtGui.QLabel(u'Имя')
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.list7.addWidget(self.title, pos, 0, 1, 1)

        self.textUnionName = QtGui.QLineEdit()
        self.list7.addWidget(self.textUnionName, pos, 1, 1, 2)

        pos+=1
        self.title = QtGui.QLabel(u'Выбирите два связанных блока')
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.list7.addWidget(self.title, pos, 0,1,1)

        self.comboBlockConditionList7_1 = QtGui.QComboBox(self)
        self.comboBlockConditionList7_2 = QtGui.QComboBox(self)
        for elem in self.programDate["Blocks"]:
            self.comboBlockConditionList7_1.addItem(elem["Name"])
            self.comboBlockConditionList7_2.addItem(elem["Name"])
        self.list7.addWidget(self.comboBlockConditionList7_1, pos, 1,1,1)
        self.list7.addWidget(self.comboBlockConditionList7_2, pos, 2,1,1)

        pos+=1
        self.title = QtGui.QLabel(u'Выбирите стороны')
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.list7.addWidget(self.title, pos, 0,1,1)

        self.comboSideConditionList7_1 = QtGui.QComboBox(self)
        self.comboSideConditionList7_2 = QtGui.QComboBox(self)
        value=[u'Левая грань',u'Верхняя грань',u'Правая грань',u'Нижняя грань']
        for elem in value:
            self.comboSideConditionList7_1.addItem(elem)
            self.comboSideConditionList7_2.addItem(elem)
        self.list7.addWidget(self.comboSideConditionList7_1, pos, 1,1,1)
        self.list7.addWidget(self.comboSideConditionList7_2, pos, 2,1,1)

        pos+=1
        self.unionBlockButton =  QtGui.QPushButton(u'Добавить связь блоков', self)
        self.list7.addWidget(self.unionBlockButton, pos, 0, 1, 3)
        self.connect(self.unionBlockButton, QtCore.SIGNAL('clicked()'),self.addUnionBlock)

        pos+=1
        self.label = QtGui.QLabel(u'Редактор связей')
        self.label.setAlignment(QtCore.Qt.AlignLeft)
        self.list7.addWidget(self.label, pos, 0, 1, 3)

        pos+=1
        self.textFullUnion = QtGui.QTextEdit()
        self.textFullUnion.setText(str(self.programDate["Interconnects"][:])[1:-1].replace("u'","'"))
        self.list7.addWidget(self.textFullUnion, pos, 0, 1, 3)

#_______Восьмая вкладка <Настройки>
    def updateList8(self):
        for i in reversed(range(self.list8.count())):
            self.list8.itemAt(i).widget().setParent(None)

        pos=1
        self.titleDialog = QtGui.QLabel(u'Имя проекта')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list8.addWidget(self.titleDialog, pos, 0,1,1)

        self.textProject = QtGui.QLineEdit()
        self.textProject.setText(str(self.programDate["ProjectName"]))
        self.list8.addWidget(self.textProject, pos, 1, 1, 1)

        pos+=1
        self.titleDialog = QtGui.QLabel(u'Время начала расчета')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list8.addWidget(self.titleDialog, pos, 0,1,1)

        self.textStartTime = QtGui.QLineEdit()
        self.textStartTime.setText(str(self.programDate["StartTime"]))
        self.list8.addWidget(self.textStartTime, pos, 1, 1, 1)

        pos+=1
        self.titleDialog = QtGui.QLabel(u'Время конца расчета')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list8.addWidget(self.titleDialog, pos, 0,1,1)

        self.textFinishTime = QtGui.QLineEdit()
        self.textFinishTime.setText(str(self.programDate["FinishTime"]))
        self.list8.addWidget(self.textFinishTime, pos, 1, 1, 1)

        pos+=1
        self.titleDialog = QtGui.QLabel(u'Временной шаг')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list8.addWidget(self.titleDialog, pos, 0,1,1)

        self.textTimeStep = QtGui.QLineEdit()
        self.textTimeStep.setText(str(self.programDate["TimeStep"]))
        self.list8.addWidget(self.textTimeStep, pos, 1, 1, 1)

        pos+=1
        self.titleDialog = QtGui.QLabel(u'Интервал сохранения')
        self.titleDialog.setAlignment(QtCore.Qt.AlignLeft)
        self.list8.addWidget(self.titleDialog, pos, 0,1,1)

        self.textSaveInterval = QtGui.QLineEdit()
        self.textSaveInterval.setText(str(self.programDate["SaveInterval"]))
        self.list8.addWidget(self.textSaveInterval, pos, 1, 1, 1)

        self.dictGridStep={}
        for i in range(len(self.programDate["var"])):
            pos+=1
            self.labelI = QtGui.QLabel(u'Шаг по '+self.programDate["var"][i])
            self.labelI.setAlignment(QtCore.Qt.AlignLeft)
            self.list8.addWidget(self.labelI, pos, 0,1,1)

            self.textGridStep = QtGui.QLineEdit()
            self.list8.addWidget(self.textGridStep, pos, 1, 1, 1)
            if self.programDate["var"][i] in self.programDate["GridStep"]:
                self.textGridStep.setText(str(self.programDate["GridStep"][self.programDate["var"][i]]))
            else:
                self.textGridStep.setText("1")
            self.dictGridStep[self.programDate["var"][i]]=self.textGridStep

#Методы_Первая вкладка <Система>
    def sistemCheck(self):
        statusSystem=True   #Проверяем корректно ли продолжать работу программы
        textInput=self.textInputSystem.toPlainText()
        self.textInputSystem.clear()

        if textInput<>'':
            #Анализ введеной системы
            out,flagSyntax,message=libSyntaxCheck.syntaxCheck(self,textInput)

            #Обработка результатов проверки синтаксиса
            if message!='':
                statusSystem=False
                if message[:3]=='001':      #В зависимости от кода ошибки обрабатываем выход по разному
                    self.textInputSystem.insertPlainText (textInput)
                    QtGui.QMessageBox.warning (self, u'Предупреждение',unicode(message), QtGui.QMessageBox.Ok)
                else:
                    self.textInputSystem.insertHtml(out)
                    QtGui.QMessageBox.warning (self, u'Предупреждение',unicode(message), QtGui.QMessageBox.Ok)
            else:
                self.textInputSystem.insertHtml(out)
                if flagSyntax==False:
                    statusSystem=False
                    QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введена некорректная система", QtGui.QMessageBox.Ok)
            #проверим список определенных переменных
            checkText=str(self.comboValue.currentText())
            listText=checkText.split(',')
            #введено число
            for i in listText:
                if i.isdigit():
                    statusSystem=False
                    QtGui.QMessageBox.warning (self, u'Предупреждение',
                u"Число не может быть переменной", QtGui.QMessageBox.Ok)
                elif str(textInput).count(i)==0:
                    QtGui.QMessageBox.warning (self, u'Предупреждение',
                u"Данная переменная не используется "+i, QtGui.QMessageBox.Ok)
            #введен некорректный символ
            if re.findall('[^A-Za-z0-9,]',checkText):
                statusSystem=False
                QtGui.QMessageBox.warning (self, u'Предупреждение',
                u"Введен неправильнай список переменных", QtGui.QMessageBox.Ok)

            if statusSystem:
                analSys=libAnalysisSystem.analysisSystem()
                analSys.setOutOfTheSystemComponents(textInput,checkText)
                self.programDate["dif"]=analSys.dif
                self.programDate["var"]=analSys.var
                for i in analSys.param:
                    if len(self.programDate["param"])>0:
                        if i in self.programDate["param"][0]:
                            pass
                        else:
                            self.programDate["param"][0][i]=1
                    else:
                        self.programDate["param"].append({})
                        self.programDate["param"][0][i]=1
                self.programDate["system"]=analSys.system
                print self.programDate

    def useTemplate(self):
        out=self.comboEqu.currentIndex()
        if out==0:
            self.programDate={"dif":[],"var":[],"param":[],"system":[],
                "Initials":[],"Blocks":[],"Bounds":[],"Interconnects":[],
                "ProjectName":"New_project",
                "StartTime": 0.0,"FinishTime": 0.5,
                "TimeStep": 0.02,"SaveInterval": 0.1,"GridStep": {},
                "Hardware": [{"Name": "cnode1", "CpuCount": 1, "GpuCount": 3}, {"Name": "cnode2", "CpuCount": 1, "GpuCount": 3}],
                "Mapping": {"IsMapped": "true", "BlockMapping": [[0, "cpu", 0]]}}
            self.textInputSystem.setText("")
        else:
            if os.path.isfile(os.path.join("config","example_"+str(out)+".json")):
                f=open(os.path.join("config","example_"+str(out)+".json"))
                jOut=json.loads(str(f.read()))
                f.close()
                self.programDate["param"]=jOut["Equations"][0]["ParamValues"]
                self.programDate["system"]=jOut["Equations"][0]["System"]
                self.programDate["Initials"]=jOut["Initials"]
                self.programDate["Blocks"]=jOut["Blocks"]
                self.programDate["Bounds"]=jOut["Bounds"]
                self.programDate["Interconnects"]=jOut["Interconnects"]
                self.programDate["ProjectName"]=jOut["ProjectName"]
                self.programDate["StartTime"]=jOut["StartTime"]
                self.programDate["FinishTime"]=jOut["FinishTime"]
                self.programDate["TimeStep"]=jOut["TimeStep"]
                self.programDate["SaveInterval"]=jOut["SaveInterval"]
                self.programDate["GridStep"]=jOut["GridStep"]
                out=''
                for i in self.programDate["system"]:
                    out+=i+'\n'
                self.textInputSystem.setText(out)

    def addtext(self):
        self.textInputSystem.insertPlainText(str(self.comboAddFunc.currentText()))

    def addTextButton(self):
        if self.comboAddFunc.currentText()=='':
            self.insertTemplate.setEnabled(False)
        else:
            self.insertTemplate.setEnabled(True)

#Методы_Вторая вкладка <Параметры>
    def fillParam(self):
        if len(self.programDate["param"])>0:
            self.programDate["param"][0]={}
            for key, value in self.dictParam.items():
                self.programDate["param"][0][key]=str(value.text())

#Методы_Третья вкладка <Области вычисления>
    def addBlocks(self):
        t=datetime.datetime.now()
        out=str(self.textBlockName.text())
        if out=="":
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введите уникальное имя", QtGui.QMessageBox.Ok)
            return
        if len(self.programDate["Blocks"])>0:
            for i in self.programDate["Blocks"]:
                if out==i["Name"]:
                    QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введите уникальное имя", QtGui.QMessageBox.Ok)
                    return
        dictBlocks={"Name": out, "Dimension": len(self.programDate["var"]), "Offset": {}, "Size": {}, "DefaultEquation": 0, "DefaultInitial": 0, "BoundRegions": [], "InitialRegions": []}
        for key, value in self.dictBlocksXYZ.items():
            dictBlocks["Offset"][key]=str(value[0].text())
            dictBlocks["Size"][key]=str(value[1].text())
        dictBlocks["DefaultInitial"]=str(self.comboInitials.currentText())
        if self.textFullBlocks.toPlainText()=="":
            self.textFullBlocks.setText(str(dictBlocks))
        else:
            self.textFullBlocks.setText(str(self.textFullBlocks.toPlainText())+','+str(dictBlocks))
        self.fillBlocks()

    def fillBlocks(self):
        try:
            if str(self.programDate["Blocks"][:])<>str("["+str(self.textFullBlocks.toPlainText())+"]"):
                out=str("["+str(self.textFullBlocks.toPlainText())+"]").replace("'",'"')
                print out
                self.programDate["Blocks"]=json.loads(out.replace('u"','"'))
        except:
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Границы решения заданы неверно", QtGui.QMessageBox.Ok)

#Методы_Четвертая вкладка <Начальные значения>
    def addCondition(self):
        out=str(self.textConditionName.text())
        if out=="":
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введите уникальное имя", QtGui.QMessageBox.Ok)
            return
        if len(self.programDate["Initials"])>0:
            for i in self.programDate["Initials"]:
                if out==i["Name"]:
                    QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введите уникальное имя", QtGui.QMessageBox.Ok)
                    return

        dictCond={"Name": out, "Values": []}
        for i in self.listCondition:
            if i.text()<>'': dictCond["Values"].append(str(i.text()))
            else: dictCond["Values"].append('0')
        if self.textFullCondition.toPlainText()=="":
            self.textFullCondition.setText(str(dictCond))
        else:
            self.textFullCondition.setText(str(self.textFullCondition.toPlainText())+','+str(dictCond))
        self.fillCondition()

    def fillCondition(self):
        try:
            if str(self.programDate["Initials"][:])<>str("["+str(self.textFullCondition.toPlainText())+"]"):
                out=str("["+str(self.textFullCondition.toPlainText())+"]").replace("'",'"')
                self.programDate["Initials"]=json.loads(out.replace('u"','"'))
        except:
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введены неправильные начальные условия", QtGui.QMessageBox.Ok)

#Методы_Пятая вкладка <Границы>
    def addBound(self):
        t=datetime.datetime.now()
        out=str(self.textBoundsName.text())
        if out=="":
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введите уникальное имя", QtGui.QMessageBox.Ok)
            return
        if len(self.programDate["Bounds"])>0:
            for i in self.programDate["Bounds"]:
                if out==i["Name"]:
                    QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введите уникальное имя", QtGui.QMessageBox.Ok)
                    return
        if self.comboBoundCondition.currentText()==u'Дирихле':
            dictBound={"Name": out, "Type": 0, "Values": []}
        else:
            dictBound={"Name": out, "Type": 1, "Values": []}
        for i in self.listBounds:
            if i.text()<>'': dictBound["Values"].append(str(i.text()))
            else: dictBound["Values"].append('0')
        if self.textFullBound.toPlainText()=="":
            self.textFullBound.setText(str(dictBound))
        else:
            self.textFullBound.setText(str(self.textFullBound.toPlainText())+','+str(dictBound))
        self.fillBound()

    def fillBound(self):
        try:
            if str(self.programDate["Bounds"][:])<>str("["+str(self.textFullBound.toPlainText())+"]"):
                out=str("["+str(self.textFullBound.toPlainText())+"]").replace("'",'"')
                self.programDate["Bounds"]=json.loads(out.replace('u"','"'))
        except:
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введены неправильные граничные условия", QtGui.QMessageBox.Ok)

#Методы_Шестая вкладка <Доп. усл. на области>
    def addBlockSp(self):
        dictBlockSpBounds={"BoundNumber": 0,"Side": 1}
        dictBlockSpBounds["BoundNumber"]=str(self.comboBoundCond.currentText())
        out=self.comboSideCondition.currentText()
        if out==u'Левая грань': dictBlockSpBounds["Side"]=0
        elif out==u'Правая грань': dictBlockSpBounds["Side"]=1
        elif out==u'Нижняя грань': dictBlockSpBounds["Side"]=2
        elif out==u'Верхняя грань': dictBlockSpBounds["Side"]=3
        for key, value in self.dictBlocksXYZSp.items():
            if str(value[0].text())=="": dictBlockSpBounds[str(key)+"from"]=str("0")
            else: dictBlockSpBounds[str(key)+"from"]=str(value[0].text())
            if str(value[1].text())=="": dictBlockSpBounds[str(key)+"to"]=str("0")
            else: dictBlockSpBounds[str(key)+"to"]=str(value[1].text())
        for i in self.programDate["Blocks"]:
            if i["Name"]==self.comboBlockCondition.currentText():
                i["BoundRegions"].append(dictBlockSpBounds)
        self.textFullBoundSp.setText(str(self.programDate["Blocks"][:])[1:-1])
        self.fillBlocksSp()

    def fillBlocksSp(self):
        try:
            if str(self.programDate["Blocks"][:])<>str("["+str(self.textFullBoundSp.toPlainText())+"]"):
                out=str("["+str(self.textFullBoundSp.toPlainText())+"]").replace("'",'"')
                print out
                self.programDate["Blocks"]=json.loads(out.replace('u"','"'))
        except:
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Границы условия заданы неверно", QtGui.QMessageBox.Ok)

    def addInitSp(self):
        dictInitSpBounds={"InitialNumber": 0}
        dictInitSpBounds["InitialNumber"]=str(self.comboInitCond.currentText())
        for key, value in self.dictInitXYZSp.items():
            if str(value[0].text())=="": dictInitSpBounds[str(key)+"from"]=str("0")
            else: dictInitSpBounds[str(key)+"from"]=str(value[0].text())
            if str(value[1].text())=="": dictInitSpBounds[str(key)+"to"]=str("0")
            else: dictInitSpBounds[str(key)+"to"]=str(value[1].text())
        for i in self.programDate["Blocks"]:
            if i["Name"]==self.comboBlockCondition.currentText():
                i["InitialRegions"].append(dictInitSpBounds)
        self.textFullBoundSp.setText(str(self.programDate["Blocks"][:])[1:-1])
        self.fillInitSp()

    def fillInitSp(self):
        try:
            if str(self.programDate["Blocks"][:])<>str("["+str(self.textFullBoundSp.toPlainText())+"]"):
                out=str("["+str(self.textFullBoundSp.toPlainText())+"]").replace("'",'"')
                print out
                self.programDate["Blocks"]=json.loads(out.replace('u"','"'))
        except:
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Начальные условия заданы неверно", QtGui.QMessageBox.Ok)

#Методы_Седьмая вкладка <Связь блоков>
    def addUnionBlock(self):
        dictUnionBlock={"Name": "", "Block1": 0, "Block2": 1, "Block1Side": 3, "Block2Side": 2}

        out=str(self.textUnionName.text())
        if out=="":
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введите уникальное имя", QtGui.QMessageBox.Ok)
            return
        if len(self.programDate["Interconnects"])>0:
            for i in self.programDate["Interconnects"]:
                if out==i["Name"]:
                    QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введите уникальное имя", QtGui.QMessageBox.Ok)
                    return

        dictUnionBlock["Name"]=out

        out=self.comboSideConditionList7_1.currentText()
        if out==u'Левая грань': dictUnionBlock["Block1Side"]=0
        elif out==u'Правая грань': dictUnionBlock["Block1Side"]=1
        elif out==u'Нижняя грань': dictUnionBlock["Block1Side"]=2
        elif out==u'Верхняя грань': dictUnionBlock["Block1Side"]=3

        out=self.comboSideConditionList7_2.currentText()
        if out==u'Левая грань': dictUnionBlock["Block2Side"]=0
        elif out==u'Правая грань': dictUnionBlock["Block2Side"]=1
        elif out==u'Нижняя грань': dictUnionBlock["Block2Side"]=2
        elif out==u'Верхняя грань': dictUnionBlock["Block2Side"]=3

        dictUnionBlock["Block1"]=str(self.comboBlockConditionList7_1.currentText())
        dictUnionBlock["Block2"]=str(self.comboBlockConditionList7_2.currentText())

        if self.textFullUnion.toPlainText()=="":
            self.textFullUnion.setText(str(dictUnionBlock))
        else:
            self.textFullUnion.setText(str(self.textFullUnion.toPlainText())+','+str(dictUnionBlock))
        self.fillBound()
        self.fillUnionBlock()

    def fillUnionBlock(self):
        try:
            if str(self.programDate["Interconnects"][:])<>str("["+str(self.textFullUnion.toPlainText())+"]"):
                out=str("["+str(self.textFullUnion.toPlainText())+"]").replace("'",'"')
                print out
                self.programDate["Interconnects"]=json.loads(out.replace('u"','"'))
        except:
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Связи между блоками заданы неверно", QtGui.QMessageBox.Ok)

#Методы_Восьмая вкладка <Настройки>
    def fillConfig(self):
        self.programDate["ProjectName"]=str(self.textProject.text())
        self.programDate["StartTime"]=float(self.textStartTime.text())
        self.programDate["FinishTime"]=float(self.textFinishTime.text())
        self.programDate["TimeStep"]=float(self.textTimeStep.text())
        dict={}
        self.programDate["SaveInterval"]=float(self.textSaveInterval.text())
        for key, value in self.dictGridStep.items():
            dict[str(key).replace("u'","'")]=float(str(value.text()))
        self.programDate["GridStep"]=dict
        print self.programDate

#_______Начало основного метода
    def mainCode(self):
        self.sistemCheck()
        print self.programDate

        if self.textInputSystem.toPlainText()=="":
            QtGui.QMessageBox.warning (self, u'Предупреждение',u"Введите систему", QtGui.QMessageBox.Ok)
            return
        else:
            if len(self.programDate["Initials"])>0:
                pass
            else:
                QtGui.QMessageBox.warning (self, u'Предупреждение',u"Необходимо задать начальные условия", QtGui.QMessageBox.Ok)
                return
            if len(self.programDate["Blocks"])>0:
                pass
            else:
                QtGui.QMessageBox.warning (self, u'Предупреждение',u"Необходимо задать область вычисления", QtGui.QMessageBox.Ok)
                return

        for i in self.programDate["Blocks"]:
            for j in i["BoundRegions"]:
                for n, k in enumerate(self.programDate["Bounds"]):
                    print n,k,j
                    if unicode(j["BoundNumber"])==unicode(k["Name"]):
                        print 'tut'
                        j["BoundNumber"]=n
            for j in i["InitialRegions"]:
                for n, k in enumerate(self.programDate["Initials"]):
                    if unicode(j["InitialNumber"])==unicode(k["Name"]):
                        j["InitialNumber"]=n

        print "self.programDate",self.programDate

        initJson=libGenerateJSON.JsonFileCreate()
        print 'self.programDate', self.programDate["GridStep"]
        initJson.setSimpleValues(self.programDate["ProjectName"],self.programDate["StartTime"],self.programDate["FinishTime"],self.programDate["TimeStep"],self.programDate["SaveInterval"],self.programDate["GridStep"])
        initJson.setBlocks1(self.programDate["Blocks"])
        for i in self.programDate["Interconnects"]: initJson.addInterconnects(i)
        initJson.addEquation1("Flat Brusselator",self.programDate["var"],self.programDate["system"],self.programDate["param"][0].keys(),self.programDate["param"][0])
        for i in self.programDate["Bounds"]: initJson.addBounds(i)
        initJson.setInitals2(self.programDate["Initials"])
        initJson.setCompnode1(self.programDate["Hardware"])
        initJson.setMapping("true",self.programDate["Mapping"]["BlockMapping"])
        outPath=os.path.join(os.getcwd(),"File")
        initJson.Create_json(outPath,"input.json")

##        f=open(os.path.join(".\hybriddomain\domainmodel","input.json"))
##        jOut=json.loads(str(f.read()))
##        f.close()
##        print "initJson",jOut
        dirSourse="./domainmodel/Source"
        libGenerateC.runGenCfile(self,dirSourse,outPath,"input.json")



        self.runConnect()

    #Вызов окна подключения
    def runConnect(self):
        #dim_str, lexp_str, steps_str, iters_str, work_port, mainnode, procnum, login,password,ip,port,mode
        #"640", "10", "1000", "5", "15561", "cnode1", "16", "tester","tester","corp7.uniyar.ac.ru","2222",'command'
        if self.comboRunValue.currentText()==u'Вычислить на кластере':
            out=self.dictConfig
            conCluster=cluster.OnClickConnect(out["dim_str"],out["lexp_str"],out["steps_str"],out["iters_str"],out["work_port"],out["mainnode"],out["procnum"],out["login"],out["password"],out["ip"],out["port"],'funcOut.c')
            QtGui.QMessageBox.warning (self, u'Предупреждение',
                conCluster, QtGui.QMessageBox.Ok)
        else:
            out=libGenerateC.CompliteClient(self,os.getcwd()+"/File",'funcOut.c')
            QtGui.QMessageBox.warning (self, u'Предупреждение',
                out, QtGui.QMessageBox.Ok)
            pass



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = BaseWindow()
    window.show()
    sys.exit(app.exec_())
