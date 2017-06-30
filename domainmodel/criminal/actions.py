class Actions():
    def __init__(self, params, cppOut):
        self.cppOut = cppOut
        self.params = params
        self.outList = []
        self.out = None

    def get_action_for_term(self, termName):
        actions = self.__class__.__dict__
        for actionName in actions.keys():
            actionTermName = actionName.split('_')[-1]
            if actionTermName == termName:
                return(actions[actionName](self))
        return(None)

    # ACTIONS FOR termBrackets
    def action_for_termBrackets(self):
        def action(_str, loc, toks):
            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termRealForUnary
    def action_for_termRealForUnary(self):
        def action(_str, loc, toks):
            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termArgsForUnary
    def action_for_termArgsForUnary(self):
        def action(_str, loc, toks):
            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termFunc
    def action_for_termFunc(self):
        def action(_str, loc, toks):
            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termUnary
    def action_for_termUnary(self):
        def action(_str, loc, toks):
            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termBinary
    def action_for_termBinary(self):
        def action(_str, loc, toks):
            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termDiff
    def action_for_termDiff(self):
        def action(termData, termName, _str, loc, toks):
            # FOR unknownVarIndex
            # take indexes from global
            varIndexs = self.cppOut.dataTermVarsSimpleGlobal['varIndexs']
            print("varIndexs")
            print(varIndexs)
            # find index of local var for shift
            # like (U,V)-> (source[+0], source[+1])
            varIndex = varIndexs.index(self.cppOut.dataTermVarSimpleLocal['varIndexs'][0])
            self.cppOut.params.unknownVarIndex = varIndex
            # END FOR

            # FOR userIndepVariables
            self.cppOut.params.userIndepVariables = ['x', 'y']
            # END FOR

            print("termData")
            print(termData)
            # FOR indepVarList
            # vars like ['x'] for which diff make's
            indepVar = termData['indepVar']
            self.cppOut.params.indepVarList = indepVar
            # END FOR

            # FOR indepVarIndexList
            # for choicing diff type from parameters
            if indepVar[0] == 'x':
                self.cppOut.params.indepVarIndexList = [0]
            else:
                # y
                self.cppOut.params.indepVarIndexList = [1]
            # END FOR

            # FOR derivOrder
            # vars like ['x'] for which diff make's
            derivOrder = termData['order'][0]
            self.cppOut.params.derivOrder = int(derivOrder)
            # END FOR

            termData['indepVar'] = []
            termData['order'] = []
            out = self.cppOut.get_out_for_term(termName)
            self.outList.append(out)
            
            '''
            print("toks")
            print(toks)
            if toks[0] not in termData['varIndexs']:
                termData['varIndexs'].append(toks[0])
            if toks[0] not in termDataLocal['varIndexs']:
                termDataLocal['varIndexs'].append(toks[0])
            print('termDataLocal')
            print(termDataLocal)
            
            out = out.replace("arg_varIndex",
                              str(termData['varIndexs'].index(toks[0])))
            if len(self.outList) == 0:
                self.outList.append(out)
            else:
                self.outList.append('+'+out)
            '''
        return(lambda str, loc, toks: action(self.cppOut.dataTermOrder,
                                             'termDiff',
                                             str, loc, toks))
    # END ACTIONS
    
    # ACTIONS FOR termOrder
    def action_for_termOrder(self):
        def action(termData, _str, loc, toks):
            # out = self.cppOut.get_out_for_term(termName)
            print("toks")
            print(toks)
            if toks[1] not in termData['indepVar']:
                termData['indepVar'].append(toks[1])
                termData['order'].append(toks[3])
            
            # out = out.replace("arg_varIndex",
            #                   str(termData['varIndexs'].index(toks[0])))
            # self.outList.append(out)
        return(lambda str, loc, toks: action(self.cppOut.dataTermOrder,
                                             str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termVarsSimpleIndep
    def action_for_termVarsSimpleIndep(self):
        def action(termData, termDataLocal, termName, _str, loc, toks):
            out = self.cppOut.get_out_for_term(termName)
            print("toks")
            print(toks)
            if toks[0] not in termData['varIndexs']:
                termData['varIndexs'].append(toks[0])
            if toks[0] not in termDataLocal['varIndexs']:
                termDataLocal['varIndexs'].append(toks[0])
            print('termDataLocal')
            print(termDataLocal)
            
            out = out.replace("arg_varIndex",
                              str(termData['varIndexs'].index(toks[0])))
            
            self.outList.append(out)
        return(lambda str, loc, toks: action(self.cppOut.dataTermVarsSimpleGlobal,
                                             self.cppOut.dataTermVarsSimpleIndep,
                                             'termVarsSimpleIndep',
                                             str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termVarsSimple
    def action_for_termVarsSimple(self):
        def action(termData, termDataLocal, termName, _str, loc, toks):
            # out = self.cppOut.get_out_for_term(termName)
            print("toks")
            print(toks)
            if toks[0] not in termData['varIndexs']:
                termData['varIndexs'].append(toks[0])
            if toks[0] not in termDataLocal['varIndexs']:
                termDataLocal['varIndexs'].append(toks[0])
            print('termDataLocal')
            print(termDataLocal)
            
            # out = out.replace("arg_varIndex",
            #                   str(termData['varIndexs'].index(toks[0])))
            # self.outList.append(out)
        return(lambda str, loc, toks: action(self.cppOut.dataTermVarsSimpleGlobal,
                                             self.cppOut.dataTermVarSimpleLocal,
                                             'termVarsSimple',
                                             str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termVarPoint
    def action_for_termVarsPoint(self):
        
        return(lambda *args: self.action_generate_out('termVarsPoint', *args))

    def action_for_termRealForVarPointX(self):
        return(lambda str, loc, toks: self.action_add_args(self.cppOut.dataTermVarsPoint,
                                                           str, loc, toks))

    def action_for_termArgForVarPointX(self):

        return(lambda str, loc, toks: self.action_add_args(self.cppOut.dataTermVarsPoint,
                                                           str, loc, toks))
        
    def action_for_termArgForVarPointT(self):
        return(lambda str, loc, toks: self.action_add_args(self.cppOut.dataTermVarsPoint,
                                                           str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termVarPointDelay
    def action_for_termVarsPointDelay(self):
        return(lambda *args: self.action_generate_out_map('termVarsPointDelay', *args))

    def action_for_termRealForVarDelayT(self):
        return(lambda str, loc, toks: self.action_add_args_map(self.cppOut.dataTermVarsPointDelay,
                                                               str, loc, toks))

    def action_for_termRealForVarDelayX(self):
        return(lambda str, loc, toks: self.action_add_args_map(self.cppOut.dataTermVarsPointDelay,
                                                               str, loc, toks))

    def action_for_termArgForVarDelayX(self):
        return(lambda str, loc, toks: self.action_add_args_map(self.cppOut.dataTermVarsPointDelay,
                                                               str, loc, toks))
        
    def action_for_termArgForVarDelayT(self):
        return(lambda str, loc, toks: self.action_add_args_map(self.cppOut.dataTermVarsPointDelay,
                                                               str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termVarsDelay
    def action_for_termVarsDealy(self):
        return(lambda str, loc, toks: self.action_add_delay(str, loc, toks))
    # END ACTIONS

    def action_add_delay(self, str, loc, toks):
        '''
        DESCRIPTION:
        If delay U(t-k) found, add k to delays
        where delays is global.
        Cannot work with system with vars U,V,...
        where more then one var has delays.
        '''
        # print("toks=")
        # print(toks)
        delay = float(toks.asList()[0][4])
        self.delays.append(delay)

    def action_generate_out_map(self, termName, *args):
        '''
        DESCRIPTION:
        Add founded by paterns with termName
        arg's (like argi) to out string.
        Use out from cppOutsForTerms
        (so it should be here)
        '''
        self.out = self.cppOut.get_out_for_term(termName)
        print("dataTermVarsPoint =")
        print(self.cppOut.dataTermVarsPointDelay)
        # vars = ['arg_T_var', 'arg_X_var', 'arg_Y_var']
        # varsVal = ['arg_T_val', 'arg_X_val', 'arg_Y_val']
        # for case like [['arg_T_var'], ['arg_X_var', '0.7']]
        if len(self.cppOut.dataTermVarsPointDelay[0]) == 1:
            self.cppOut.dataTermVarsPointDelay.pop(0)

        varsVal = dict(self.cppOut.dataTermVarsPointDelay)

        # for case with no delay
        if 'arg_T_var' not in varsVal.keys():
            self.out = self.out.replace("arg_T_var", "0")

        for var in varsVal.keys():
            self.out = self.out.replace(var, varsVal[var])

        # take indexes from global
        varIndexs = self.cppOut.dataTermVarsSimpleGlobal['varIndexs']
        print("varIndexs")
        print(varIndexs)
        # find index of local var
        varIndex = varIndexs.index(self.cppOut.dataTermVarSimpleLocal['varIndexs'][0])
        
        self.out = self.out.replace('arg_varIndex', str(varIndex))
        self.outList.append(self.out)

        # for multiply using in tests
        self.cppOut.dataTermVarsPointDelay = []
        self.cppOut.dataTermVarSimpleLocal['varIndexs'] = [] 

    def action_add_args_map(self, termData, _str, loc, toks):
        '''
        DESCRIPTION:
        For U(t-1.1,{x,0.3})
        add [['T', 1],['X', 0.3]]
        to termData.
        '''
        
        # print(termData)
        if toks[0] in "txyz":
            data = toks[0].upper()
            termData.append(['arg_'+data+'_var'])
        else:
            # if value for T
            if termData[-1][0] == 'arg_'+'T'+'_var':
                # cut int from time delay
                data = toks[0].split('.')[0]
            else:
                # value for space
                if termData[-1][0] == 'arg_'+'X'+'_var':
                    data = str(int(float(toks[0])*self.params.shape[0]))
                elif(termData[-1][0] == 'arg_'+'Y'+'_var'):
                    data = str(int(float(toks[0])*self.params.shape[1]))
            termData[-1].append(data)
    
    def action_add_args(self, termData, str, loc, toks):
        '''
        DESCRIPTION:
        Place all found args in termData
        in occurrance order.
                        
        '''
        # print("toks = ")
        # print(toks)
        if toks[0] in "xyz":
            data = toks[0].upper()
        else:
            data = toks[0]
        termData.append(data)
    
    def action_add_args_spec(self, termData, str, loc, toks):
        '''
        DESCRIPTION:
        Place all found args in termData
        in occurrance order.
        Spec for delays.
                        
        '''
        print("toks = ")
        print(toks)
        data = toks[0].split('.')[0]
        termData.append(data)
    
    def action_generate_out(self, termName, *args):
        '''
        DESCRIPTION:
        Add founded by paterns with termName
        arg's (like argi) to out string.
        Use out from cppOutsForTerms
        (so it should be here)
        '''
        self.out = self.cppOut.get_out_for_term(termName)
        print("dataTermVarsPoint =")
        print(self.cppOut.dataTermVarsPoint)
        for i in range(len(self.cppOut.dataTermVarsPoint)):
            self.out = self.out.replace("arg%d" % i,
                                        self.cppOut.dataTermVarsPoint[i])

