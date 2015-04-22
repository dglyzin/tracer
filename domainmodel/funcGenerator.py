import numpy as np
from equationParser import Parser

# Purposes:
# 1'.Build the generator for arbitrary derivative order. (has done for orders < or = 4)
# 2.Build the generator for boundary function.
# We always create the string '\t int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;\n' in a same way.

class Generator:
    
    def __finit_difference_Generator(self,boundNumber,derivAtZero,varIndex,indepVar,indepVarIndex,order): 
        increment = 'D' + indepVar + 'M' + order
        stride = 'Block0Stride' + indepVar
        
        o = int(order)
        if boundNumber < 0:
            if o == 1:
                toLeft = 'suorce[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                toRight = 'source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                output = '0.5 * '+increment+' * '+'('+toRight+' - '+toLeft+')'
            elif o == 2:
                toRight = 'source[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                toLeft = 'source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                toCenter = '2.0 * source[idx + ' + str(varIndex) + ']'
                output = increment+' * '+'('+toRight+' + '+toLeft+' - '+toCenter+')'
            elif o == 3:
                toRight1 = 'source[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                toCenter = '3.0 * source[idx + ' + str(varIndex) + ']'
                toLeft1 = '3.0 * source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                toLeft2 = 'source[idx - 2.0 * '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                output = increment+' * '+'('+toRight1+' - '+toCenter+' + '+toLeft1+' - '+toLeft2+')'
            elif o == 4:
                toRight2 = 'source[idx + 2.0 * '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                toRight1 = '4.0 * source[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                toCenter = '6.0 * source[idx + ' + str(varIndex) + ']'
                toLeft1 = '4.0 * source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                toLeft2 = 'source[idx - 2.0 * '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                output = increment+' * '+'('+toRight2+' - '+toRight1+' + '+toCenter+' - '+toLeft1+' + '+toLeft2+')'
            else:
                raise SyntaxError("The highest derivative order of the system greater than 4! I don't know how to work with it!")
        else:
            if o == 1:
                if indepVarIndex == boundNumber:
                    output = 'bound_value'
                else:
                    toLeft = 'suorce[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                    toRight = 'source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                    output = '0.5 * '+increment+' * '+'('+toRight+' - '+toLeft+')'
            elif o == 2:
                if indepVarIndex == boundNumber:
                    toCenter = 'source[idx + ' + str(varIndex) + ']'
                    if derivAtZero > 0:
                        toRight = 'source[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                        output = '2.0 * '+increment+' * '+'('+toRight+' - '+toCenter+' - bound_value / Math.sqrt('+increment+'))'
                    else:
                        toLeft = 'source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                        output = '2.0 * '+increment+' * '+'('+toLeft+' - '+toCenter+' + bound_value / Math.sqrt('+increment+'))'
                else:
                    toRight = 'source[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                    toLeft = 'source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
                    toCenter = '2.0 * source[idx + ' + str(varIndex) + ']'
                    output = increment+' * '+'('+toRight+' + '+toLeft+' - '+toCenter+')'
            else:
                raise SyntaxError("The highest derivative order of the system greater than 2! I don't know how to generate boundary function in this case!")
        return output
    
#rightHandSide -- parsed string, which contain right hand side of equation. String array.
    def __rhs_gen(self,boundNumber,derivAtZero,lhs,rightHandSide,indepVrbls,vrbls,params):
        
        varIndex = vrbls.index(lhs)
        result = '\t result[idx + ' + str(varIndex) + '] = '
        
        deriv = ''
        strList = list([result])
        elemFuncsList = ['exp','sin','sinh','cos','tan','tanh','sqrt','log']
        for j,lst in enumerate(rightHandSide):
            if lst[0] == 'D[':
                deriv = lst
                varIndex = vrbls.index(deriv[1])
                indepVarIndex = indepVrbls.index(deriv[4])
                indepVar = deriv[4]
                order = deriv[6]
                strList.extend([self.__finit_difference_Generator(boundNumber,derivAtZero,varIndex,indepVar,indepVarIndex,order)])
            elif lst in vrbls:
                varIndex = vrbls.index(lst)
                strList.extend(['source[idx + ' + str(varIndex) + ']'])
            elif lst in params:
                parIndex = params.index(lst)
                strList.extend(['params[' + str(parIndex) + ']'])
            elif lst == '+' or lst == '-' or lst == '*' or lst == '/' or lst == '(' or lst == ')':
                strList.extend([str(lst)])
            
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

# if boundaryNumber <= 0, generate central function; else generate boundary Function with corresponding bound number
    def generate_c_func(self,boundNumber,derivAtZero,estrList,indepVrbls,params):
        signature = 'void Block0CentralFunction(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){\n'
        idx = '\t int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;\n'
        function = list([signature,idx])
        if boundNumber >= 0:
            function.extend(['\t double bound_value;\n','\t bound_value = -10.0;\n'])
            
        parser = Parser()
        rightHandSideList = parser.getRhsLst(estrList,params)
        vrbls = parser.getLhsList(estrList)
            
        for i,rhs in enumerate(rightHandSideList):
            function.extend([self.__rhs_gen(boundNumber,derivAtZero,vrbls[i],rhs,indepVrbls,vrbls,params)])
        function.extend(['}'])
    
        return ''.join(function) + '\n'