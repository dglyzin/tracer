# -*- coding: utf-8 -*-
import numpy as np
from eqParser import *

#Сделать генератор для производной любого порядка.
#Строка '\t int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;\n' всегда генерируется единообразно.

#varIndex - индекс компоненты искомой функции в массиве этих компонент
#indepVarIndex - индекс независимой переменной в массиве этих переменных
def finit_difference_Generator(varIndex,indepVarIndex): 
    #increment = 'D' + indepVrbls[indepVarIndex] + 'M2'
    #stride = 'Block0Stride' + indepVrbls[indepVarIndex] -- желательно, но пока

    if indepVarIndex == 0:
        increment = 'DXM2'
        stride = 'Block0StrideX'
    elif indepVarIndex == 1:
        increment = 'DYM2'
        stride = 'Block0StrideY'

    toRight = 'source[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
    toLeft = 'source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
    toCenter = '2.0 * source[idx]'

    output = increment+' * '+'('+toRight+' + '+toLeft+' - '+toCenter+')'
    return output

#Подумать, как можно упростить следующий код!
#rightHandSide -- распарсенная строка, содержащая правую часть уравнения, т.е. массив строк.
def rhs_gen(lhs,rightHandSide,indepVrbls,vrbls,params):
    
    varIndex = vrbls.index(lhs)
    result = '\t result[idx + ' + str(varIndex) + '] = '
    
    deriv = ''
    strList = list([result])
    elemFuncsList = ['exp','sin','sinh','cos','tan','tanh','sqrt','log']
    for j,lst in enumerate(rightHandSide):
        if lst[0] == 'D' and lst[1] == '[':
            deriv = lst
            varIndex = vrbls.index(deriv[2])
            indepVarIndex = indepVrbls.index(deriv[5])
            strList.extend([finit_difference_Generator(varIndex,indepVarIndex)])
        elif lst in vrbls:
            varIndex = vrbls.index(lst)
            strList.extend(['source[idx + ' + str(varIndex) + ']'])
        elif lst in params:
            parIndex = params.index(lst)
            strList.extend(['params[' + str(parIndex) + ']'])
        elif lst == '+' or lst == '-' or lst == '*' or lst == '/' or lst == '(' or lst == ')':
            strList.extend([str(lst)])
        #Если есть возведение в степень, то в нее возводится то, что было записано в strList в последний раз.
        elif lst[0] == '^':
            power = int(lst[1])
            if rightHandSide[j-1] != ')':
                strToPower = strList.pop()
                poweredStr = strToPower
                for i in np.arange(1,power):
                    poweredStr = poweredStr + ' * ' + strToPower
            else:
                strToPower = list([strList.pop()])
                count = 1
                while count != 0:
                    helpStr = strList.pop()
                    if helpStr == ')':
                        count = count + 1
                    elif helpStr == '(':
                        count = count - 1
                    strToPower.extend([helpStr])
                strToPower = ''.join(strToPower[::-1])
                poweredStr = strToPower
                for i in np.arange(1,power):
                    poweredStr = poweredStr + ' * ' + strToPower
            strList.extend([poweredStr])
            
        elif lst in elemFuncsList:
            strList.extend(['Math.' + lst])
        else:
            strList.extend(lst)

    string = ''.join(strList) + ';\n'
    return string

def generate_c_func(estrList,indepVrbls,params):
    signature = 'void Block0CentralFunction(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){\n'
    idx = '\t int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;\n'

    rightHandSideList = getRhsLst(estrList,params) 
    vrbls = getLhsList(estrList)
    
    function = list([signature,idx])
    for i,rhs in enumerate(rightHandSideList):
        function.extend([rhs_gen(vrbls[i],rhs,indepVrbls,vrbls,params)])
    function.extend(['}'])

    return ''.join(function) + '\n'
