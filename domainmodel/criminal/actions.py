from pyparsing import ParseResults


class Actions():
    '''
    TODO:
    Use toks instead outList for eq like
    (sin(x)+cos(x)+...)^n (i.e. for composed
    patterns).
    '''
    def __init__(self, params, cppOut):
        self.cppOut = cppOut
        self.params = params
        self.outList = []
        self.out = None

        # for debugging:
        self.dbg = True
        self.dbgInx = 3

    def get_action_for_term(self, termName):
        actions = self.__class__.__dict__
        for actionName in actions.keys():
            actionTermName = actionName.split('_')[-1]
            if actionTermName == termName:
                return(actions[actionName](self))
        return(None)

    # ACTIONS FOR termBaseExpr
    def action_for_termBaseExpr(self):
        def convert_delay(val, delays):
            '''
            DESCRIPTION:
            Find index of floating delay val.
            independently of order.
            Value is only important for order:
            For ex:
            [5.1, 1.5, 2.7]->
            [3, 1, 2]
            '''
            delays.sort()

            # for debug
            self.print_dbg("delay_list:", delays)

            return(delays.index(val)+1)

        def action(termData,
                   _str, loc, toks):
            '''
            DESCRIPTION:
            If delay U(t-k) found, add k to delays
            where delays is global.
            Replace each occurrance of delay in 
            out stack to it value according 
            convert_delay function.
            Use dataTermVarsForDelay.
            Can work with system with vars U,V,...
            where more then one var has delays.

            termDataInner only for read.
            '''
            # for debug
            self.print_dbg("FROM action_for_termBaseExpr:")

            # for debug
            self.print_dbg("toks:", toks)
            self.print_dbg("type(toks)", type(toks))

            self.print_dbg("outList", self.outList)

            # if no out generate reduce return error
            if len(self.outList) == 0:
                self.print_dbg("len(outList)=0 =>",
                               " no output for expr %s found" % str(toks),
                               "and",
                               " reduce raise error")

            out = reduce(lambda x, y: x+y, self.outList)
            
            # change all founded delay marker to
            # delay
            for var in termData.keys():
                for delay in termData[var]:
                    # convert delays like:
                    # 1.1 -> 1 (see convert_delay)
                    delayConv = convert_delay(delay, termData[var])
                    out = out.replace("arg_delay_"+var+'_'+str(delay),
                                      str(delayConv))

            self.outList = [out]
            
            termData.clear()
            # self.actions.outList = []

        return(lambda str, loc, toks: action(self.cppOut.dataTermVarsForDelay,
                                             str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termPower
    def action_for_termPower(self):
        def action(termData, _str, loc, toks):
            # for debug
            self.print_dbg("FROM action_for_termPower")

            # for debug
            self.print_dbg("toks:", toks)
            self.print_dbg("_str:", _str)
            self.print_dbg("loc:", loc)
            self.print_dbg("outList", self.outList)
            
            # cut out from inner term X: X^power
            # from outList.
            innerTermOut = self.outList.pop()
            power = termData['real'][0]

            out = self.cppOut.get_out_for_termPower()
            out = out.replace("arg_val", innerTermOut)
            out = out.replace("arg_power", power)

            # clear subterm
            termData['real'] = []

            self.outList.append(out)

            '''
            self.print_dbg("toks.keys:", toks.keys())
            self.print_dbg("toks.values:", toks.values())
            self.print_dbg("toks.pop:", toks[0].pop(0))
            self.print_dbg("toks:", toks)
            '''

        return(lambda _str, loc, toks: action(self.cppOut.dataTermRealForPower,
                                              _str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termRealForPower
    def action_for_termRealForPower(self):
        def action(termData, _str, loc, toks):
            # for debug
            # self.print_dbg("FROM action_for_termRealForPower")

            # for debug
            # self.print_dbg("toks:", toks)
            termData['real'].append(toks[0])
        return(lambda _str, loc, toks: action(self.cppOut.dataTermRealForPower,
                                              _str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termBrackets
    def action_for_termBrackets(self):
        def action(_str, loc, toks):
            # for debug
            # self.print_dbg("FROM action_for_termBrackets")

            # for debug
            # self.print_dbg("toks:", toks)

            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termRealForUnary
    def action_for_termRealForUnary(self):
        def action(_str, loc, toks):
            # for debug
            self.print_dbg("FROM action_for_termRealForUnary")

            # for debug
            self.print_dbg("toks:", toks)

            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termArgsForUnary
    def action_for_termArgsForUnary(self):
        def action(termName, _str, loc, toks):
            # for debug
            self.print_dbg("FROM action_for_termArgsForUnary:")

            # for debug
            self.print_dbg("toks:", toks)

            out = self.cppOut.get_out_for_term(termName)
            out = out.replace("Arg",
                              str(toks[0]).upper())
            self.outList.append(out)
            self.print_dbg("success")
            #return(ParseResults([out]))

        return(lambda _str, loc, toks: action('termArgsForUnary',
                                              _str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termFunc
    def action_for_termFunc(self):
        def action(_str, loc, toks):
            self.print_dbg("FROM action_for_termFunc:")
            # for compatibility reason
            if self.cppOut.params.fromOld:
                self.print_dbg("from old error")
                raise(Exception)

            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termParam
    def action_for_termParam(self):
        def action(_str, loc, toks):
            # for debug
            self.print_dbg("FROM action_for_termParam:")

            # for debug
            self.print_dbg("parameters",
                           self.cppOut.params.parameters)
            # for debug
            self.print_dbg("toks",
                           toks)
            

            # get index of param
            parameter = toks[0]
            parameterInx = self.cppOut.params.parameters.index(parameter)

            # for debug
            self.print_dbg("parameterInx", parameterInx)

            # OUTPUT
            out = self.cppOut.get_out_for_termParam()
            out = out.replace("arg_param", str(parameterInx))
            self.outList.append(out)
            #return(ParseResults([out]))

        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS
    
    # ACTIONS FOR termUnary
    def action_for_termUnary(self):
        def action(_str, loc, toks):
            # for debug
            # self.print_dbg("FROM action_for_termUnary:")

            # for debug
            # self.print_dbg("toks:", toks)

            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termBinary
    def action_for_termBinary(self):
        def action(_str, loc, toks):
            # for debug
            # self.print_dbg("FROM action_for_termBinary:")

            # for debug
            # self.print_dbg("toks:", toks)

            self.outList.append(toks[0])
        return(lambda _str, loc, toks: action(_str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termDiff
    def action_for_termDiff(self):
        def action(termData, termName, _str, loc, toks):
            '''
            DESCRIPTION:
            Fill parameters from inner founded term
            and use it for diff out.

            TODO:
            Replace varIndex from string
            '''
            # for debug
            self.print_dbg("FROM action_for_termDiff:")

            # FOR unknownVarIndex
            # take indexes from global
            varIndexs = self.cppOut.dataTermVarsSimpleGlobal['varIndexs']

            # for debug
            self.print_dbg("varIndexs:", varIndexs)
            self.print_dbg("dataTermVarSimple",
                           self.cppOut.dataTermVarSimpleLocal)
            # find index of local var for shift
            # like (U,V)-> (source[+0], source[+1])
            try:
                varIndex = varIndexs.index(self.cppOut.dataTermVarSimpleLocal['varIndexs'][0])
            except:
                varIndex = varIndexs.index(self.cppOut.dataTermVarsSimpleIndep['varIndexs'][0])
            self.cppOut.params.unknownVarIndex = varIndex
            # END FOR

            # FOR diffType
            if len(termData['indepVar']) == 1:
                diffType = 'pure'
                self.cppOut.params.diffType = diffType
            else:
                diffType = 'mix'
                self.cppOut.params.diffType = diffType
            # END FOR

            # FOR userIndepVariables
            # self.cppOut.params.userIndepVariables = ['x', 'y']
            # END FOR

            # for debug
            self.print_dbg("termData:", termData)

            # FOR indepVarList
            # vars like ['x'] for which diff make's
            # also used for choice special or common in
            # bound and interconnect.
            indepVar = termData['indepVar']
            self.cppOut.params.indepVarList = indepVar
            # END FOR

            # FOR indepVarIndexList
            # for choicing diff type from parameters
            if diffType == 'pure':
                if indepVar[0] == 'x':
                    self.cppOut.params.indepVarList = ['x']
                else:
                    # y
                    self.cppOut.params.indepVarList = ['y']
            elif(diffType == 'mix'):
                self.cppOut.params.indepVarList = indepVar
            # END FOR

            # FOR derivOrder
            if diffType == 'pure':
                derivOrder = termData['order'][0]
            elif(diffType == 'mix'):
                derivOrder = sum([int(order)
                                  for order in termData['order']])
            self.cppOut.params.derivOrder = int(derivOrder)
            # END FOR

            # clear data
            termData['indepVar'] = []
            termData['order'] = []

            # take source[delay] from inner term
            # like termVarsDelay
            # and
            # remove last element out from stack
            # i.e. inner termVarsSimpleIndep
            # for ex: for "D[U,{x,2}]" remove
            # out for U.
            innerTermOut = self.outList.pop()

            # cut delay
            _from = innerTermOut.index('[')+1
            _to = innerTermOut.index(']')
            innerTermOutDelay = innerTermOut[_from:_to]

            # for debug
            self.print_dbg("innerTermOut:", innerTermOut)
            self.print_dbg("innerTermOutDelay:", innerTermOutDelay)

            # OUTPUT
            out = self.cppOut.get_out_for_term(termName)
            
            # change arg_delay to something
            # like arg_delay_U_1.1
            out = out.replace("arg_delay",
                              innerTermOutDelay)

            self.outList.append(out)
            #return(ParseResults([out]))
            # END OUTPUT
            
        return(lambda str, loc, toks: action(self.cppOut.dataTermOrder,
                                             'termDiff',
                                             str, loc, toks))
    # END ACTIONS
    
    # ACTIONS FOR termOrder
    def action_for_termOrder(self):
        def action(termData, _str, loc, toks):
            # for debug
            self.print_dbg("FROM action_for_termOrder:")

            # out = self.cppOut.get_out_for_term(termName)

            # for debug
            self.print_dbg("toks:", toks)

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
        '''
        DESCRIPTION:
        Add simple out for U.
        Add varInexes global and local

        Local will used for finding its index
        in global in action_generate_out_map

        varIndex usage:
        source[][idx+0] - x
        source[][idx+1] - y
        source[][idx+2] - z
        
        '''
        def action(termData, termDataLocal, termName, _str, loc, toks):
            # for debug
            self.print_dbg("FROM action_for_termVarsSimpleIndep:")

            out = self.cppOut.get_out_for_term(termName)

            # for debug
            self.print_dbg("toks:", toks)

            if toks[0] not in termData['varIndexs']:
                termData['varIndexs'].append(toks[0])
            if toks[0] not in termDataLocal['varIndexs']:
                termDataLocal['varIndexs'].append(toks[0])

            # for debug
            self.print_dbg("termDataLocal", termDataLocal)

            out = out.replace("arg_varIndex",
                              str(termData['varIndexs'].index(toks[0])))
 
            self.outList.append(out)
            #return(ParseResults([out]))
        return(lambda str, loc, toks: action(self.cppOut.dataTermVarsSimpleGlobal,
                                             self.cppOut.dataTermVarsSimpleIndep,
                                             'termVarsSimpleIndep',
                                             str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termVarsSimple
    def action_for_termVarsSimple(self):
        def action(termData, termDataLocal, termName, _str, loc, toks):
            '''
            DESCRIPTION:
            Collect variables indexes.
            '''
            # for debug
            self.print_dbg("FROM action_for_termVarsSimple:")

            # out = self.cppOut.get_out_for_term(termName)

            # for debug
            self.print_dbg("toks:", toks)

            if toks[0] not in termData['varIndexs']:
                termData['varIndexs'].append(toks[0])
            if toks[0] not in termDataLocal['varIndexs']:
                termDataLocal['varIndexs'].append(toks[0])
                
            # for debug
            self.print_dbg("termDataLocal", termDataLocal)
            
            # out = out.replace("arg_varIndex",
            #                   str(termData['varIndexs'].index(toks[0])))
            # self.outList.append(out)
        return(lambda str, loc, toks: action(self.cppOut.dataTermVarsSimpleGlobal,
                                             self.cppOut.dataTermVarSimpleLocal,
                                             'termVarsSimple',
                                             str, loc, toks))
    # END ACTIONS

    # ACTIONS FOR termVarsDelay
    def action_for_termVarsDelay(self):
        def action_add_delay(termName, termDataInner, termData,
                             _str, loc, toks):
            '''
            DESCRIPTION:
            If delay U(t-k) found, add k to delays
            where delays is global.
            Can work with system with vars U,V,...
            where more then one var has delays.

            termDataInner only for read.
            '''
            # for debug
            self.print_dbg("FROM action_for_termVarsDelay:")

            out = self.cppOut.get_out_for_term(termName)
            
            # for debug
            self.print_dbg("toks:", toks)

            var = toks.asList()[0][0]
            delay = float(toks.asList()[0][4])
            
            if var not in termData.keys():
                termData[var] = [delay]
            else:
                termData[var].append(delay)

            out = out.replace("arg_varIndex",
                              str(termDataInner['varIndexs'].index(toks[0][0])))

            # change arg_delay to something
            # like arg_delay_U_1.1
            out = out.replace("arg_delay",
                              "arg_delay_"+str(toks[0][0])+'_'+str(delay))

            # remove last element out
            # i.e. inner termVarsSimpleIndep
            # for ex: for "U(t-1.1)" remove
            # out for U.
            self.outList.pop()

            self.outList.append(out)
            #return(ParseResults([out]))
        return(lambda str, loc, toks: action_add_delay('termVarsDelay',
                                                       self.cppOut.dataTermVarsSimpleGlobal,
                                                       self.cppOut.dataTermVarsForDelay,
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

    def action_for_termParamForVarDelayX(self):
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

    def action_generate_out_map(self, termName, *args):
        '''
        DESCRIPTION:
        Add founded by patterns with termName
        arg's (like argi) to out string.
        Use out from cppOutsForTerms
        (so it should be here)

        dataTermVarSimpleLocal used for find var,
        founded by termArgForVarDelay.

        dataTermVarsSimpleGlobal used for find
        var index (i.e. shift).
        '''
        # for debug
        self.print_dbg("FROM action_generate_out_map:")

        # for debug
        self.print_dbg("toks", args[2])

        self.out = self.cppOut.get_out_for_term(termName)
     
        # for debug
        self.print_dbg("dataTermVarsPoint:",
                       self.cppOut.dataTermVarsPointDelay)

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

        # for debug
        self.print_dbg("varIndexs from global:",
                       varIndexs)

        # for debug
        self.print_dbg("varIndexs from local:",
                       self.cppOut.dataTermVarSimpleLocal['varIndexs'])

        # find index of local var
        var = self.cppOut.dataTermVarSimpleLocal['varIndexs'][0]
        varIndex = varIndexs.index(var)
        
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
        # for debug
        self.print_dbg("FROM action_add_args_map:")
     
        # for debug
        self.print_dbg("toks:", toks)

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
                # for debug
                self.print_dbg("parametersVal:",
                               self.cppOut.params.parametersVal)

                if toks[0] in self.cppOut.params.parametersVal.keys():
                    # if var like a
                    parametersVal = self.cppOut.params.parametersVal
                    val = parametersVal[toks[0]]
                else:
                    # if var like 0.3
                    val = toks[0]

                # for debug
                self.print_dbg("val:", val)

                if termData[-1][0] == 'arg_'+'X'+'_var':
                    data = str(int(float(val)*self.params.shape[0]))
                elif(termData[-1][0] == 'arg_'+'Y'+'_var'):
                    data = str(int(float(val)*self.params.shape[1]))
            termData[-1].append(data)
        # for debug
        self.print_dbg("termData:", termData)

    def action_add_args(self, termData, str, loc, toks):
        '''
        DESCRIPTION:
        Place all found args in termData
        in occurrance order.
                        
        '''
        # for debug
        self.print_dbg("FROM action_add_args:")

        # for debug
        self.print_dbg("toks:", toks)

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
        # for debug
        self.print_dbg("FROM action_add_args_spec:")

        # for debug
        self.print_dbg("toks:", toks)

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
        # for debug
        self.print_dbg("FROM action_generate_out:")

        self.out = self.cppOut.get_out_for_term(termName)
        # for debug
        self.print_dbg("dataTermVarsPoint:", self.cppOut.dataTermVarsPoint)

        for i in range(len(self.cppOut.dataTermVarsPoint)):
            self.out = self.out.replace("arg%d" % i,
                                        self.cppOut.dataTermVarsPoint[i])

    def print_dbg(self, *args):
        if self.dbg:
            for arg in args:
                print(self.dbgInx*' '+str(arg))
            print('')
