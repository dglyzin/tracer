import numpy as np
from equationParser import Parser

# Purposes:
# 1'.Build the generator for arbitrary derivative order. (has done for orders < or = 4)
# 2.Build the generator for boundary function.
# We always create the string '\t int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;\n' in a same way.

class Generator:
    
    def __finit_difference_Generator(self,varIndex,indepVar,order): 
        increment = 'D' + indepVar + 'M' + order
        stride = 'Block0Stride' + indepVar
        
        o = int(order)
        if o == 1:
            toLeft = 'suorce[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
            toRight = 'source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
            output = increment+' * '+'('+toRight+' - '+toLeft+')'
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
        return output
    
#     def __finit_difference_Generator(self,varIndex,indepVarIndex): 
#         #increment = 'D' + indepVrbls[indepVarIndex] + 'M2'
#         #stride = 'Block0Stride' + indepVrbls[indepVarIndex] -- desirable, but
#     
#         if indepVarIndex == 0:
#             increment = 'DXM2'
#             stride = 'Block0StrideX'
#         elif indepVarIndex == 1:
#             increment = 'DYM2'
#             stride = 'Block0StrideY'
#     
#         toRight = 'source[idx + '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
#         toLeft = 'source[idx - '+stride+' * CELLSIZE'+' + '+str(varIndex)+']'
#         toCenter = '2.0 * source[idx + ' + str(varIndex) + ']'
#     
#         output = increment+' * '+'('+toRight+' + '+toLeft+' - '+toCenter+')'
#         return output

# Simplify the next code
#rightHandSide -- parsed string, which contain right hand side of equation. String array.
    def __rhs_gen(self,lhs,rightHandSide,indepVrbls,vrbls,params):
        
        varIndex = vrbls.index(lhs)
        result = '\t result[idx + ' + str(varIndex) + '] = '
        
        deriv = ''
        strList = list([result])
        elemFuncsList = ['exp','sin','sinh','cos','tan','tanh','sqrt','log']
        for j,lst in enumerate(rightHandSide):
            if lst[0] == 'D[':
                deriv = lst
                varIndex = vrbls.index(deriv[1])
#                 indepVarIndex = indepVrbls.index(deriv[4])
                indepVar = deriv[4]
                order = deriv[6]
                strList.extend([self.__finit_difference_Generator(varIndex,indepVar,order)])
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

    def generate_c_func(self,estrList,indepVrbls,params):
        signature = 'void Block0CentralFunction(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){\n'
        idx = '\t int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;\n'
        
        parser = Parser()
        rightHandSideList = parser.getRhsLst(estrList,params) 
        vrbls = parser.getLhsList(estrList)
        
        function = list([signature,idx])
        for i,rhs in enumerate(rightHandSideList):
            function.extend([self.__rhs_gen(vrbls[i],rhs,indepVrbls,vrbls,params)])
        function.extend(['}'])
    
        return ''.join(function) + '\n'