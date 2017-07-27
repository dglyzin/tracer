from abstractGenerator import BoundCondition, Connection
from someFuncs import determineNameOfBoundary
from someFuncs import getCellCountInClosedInterval


class Params():
    '''
    DESCRIPTION:
    If string for cpp out (from cppOutsForTerms.py)
    contain some params or
    If actions in Actions.py contain some params
    that params must be there initiated.
    Or they must be added in parser.__init__ method in
    according section.
    '''
    def __init__(self):
        # for comment before each central function
        self.hatCf = dict()
        
        # for name of central functions
        self.namesCf = dict()

        # for compatibility reason
        # cannot work with terms like
        # sin(a*x+b)
        self.fromOld = False

    
    def set_params_for_definitions(self, model):
        '''
        DESCRIPTION:
        Fill params for definitions 1d template.
        '''

        # FOR addition parameters
        gridStep = [model.gridStepX, model.gridStepY, model.gridStepZ]

        # count of equation in each cell
        # (storage of each cell is count of equations in block)
        eqs = model.equations

        def get_cell_size(block):
            return(len(eqs[block.defaultEquation].system))

        def get_grid_offsets(block):
            return([block.offsetX, 0, 0])

        def get_grid_sizes(block):
            return([block.sizeX, 0, 0])
        # END FOR addition parameters

        # FOR ERRORS
        if len(gridStep) < 3:
            raise AttributeError("A list 'gridStep' should be consist of"
                                 + " values for ALL independent variables!"
                                 + " x, y, z")
        # END FOR ERRORS

        class Args():
            '''
            DESCRIPTION:
            Class for storage args data
            for code simplification reason.
            '''
            def __init__(self):
                pass

        defaultIndepVars = ['x', 'y', 'z']

        # FOR gridArgs
        gridArgs = []
        for i in range(len(gridStep)):
            gridArg = Args()
            gridArg.indepVar = defaultIndepVars[i]
            d = gridStep[i]
            gridArg.d = d
            gridArg.d2 = d * d
            gridArg.dm1 = round(1 / d)
            gridArg.dm2 = round(1 / (d * d))
            gridArgs.append(gridArg)
        # END FOR gridArgs

        # FOR define block (mainly with stride and counts)
        blocksArgs = []
        for blockNumber, block in enumerate(model.blocks):
           
            blockArgs = Args()
            blockArgs.blockNumber = blockNumber
            blockArgs.cellsize = get_cell_size(block)

            # for each var in vars grid step exist
            countOfVars = len(gridStep)

            # for counts
            counts = []
            for i in range(countOfVars):
                d = gridStep[i]
                sizeForIndepVar = get_grid_sizes(block)[i]
                countOfGridStepsInVar = getCellCountInClosedInterval(sizeForIndepVar, d)
                counts.append(countOfGridStepsInVar)

            # for strides
            strides = []
            for i in range(countOfVars):
                if i == 0:
                    stride = 1
                elif i == 1:
                    stride = counts[0]
                else:
                    # if i == 2
                    stride = counts[0] * counts[1]
                strides.append(stride)

            blockArgs.indepVars = defaultIndepVars
            blockArgs.counts = counts
            blockArgs.strides = strides
            blockArgs.offsets = get_grid_offsets(block)

            blocksArgs.append(blockArgs)
        # END FOR stride and counts

        self.gridArgs = gridArgs
        self.blocksArgs = blocksArgs
        self.paramsLen = len(model.params)
        
    def set_params_for_centrals(self, model):
        '''
        DESCRIPTION:
        Fill params for centrals 1d template.
        
        TODO:
        Fill parsedValues from parser.
        '''
        # FOR FILL params.equations
        equations = []

        for blockNumber, block in enumerate(model.blocks):
            reservedSpace = 0

            # collect all equations for block
            # equationRegions should be sorted
            for eqRegion in block.equationRegions:
                reservedSpace += eqRegion.xto - eqRegion.xfrom

                # for removing trivial cases
                cond = (eqRegion.xfrom == eqRegion.xto
                        and
                        (eqRegion.xto == 0.0 or eqRegion.xto == block.sizeX))

                numsForSystems = [eq.number for eq in equations]
                if eqRegion.equationNumber not in numsForSystems and not cond:
                    equation = model.equations[eqRegion.equationNumber]
                    equation.number = eqRegion.equationNumber
                    equation.blockNumber = blockNumber
                    equations.append(equation)

            # add default equation at remaining regions.
            if block.sizeX > reservedSpace:
                equation = model.equations[block.defaultEquation]
                equation.number = block.defaultEquation
                equation.blockNumber = blockNumber
                equations.append(equation)


        self.equations = equations
        # END FOR FILL

        # FOR FuncArray
        funcNamesStack = [('Block' + str(equation.blockNumber)
                           + 'CentralFunction'
                           + str(equation.number)) for equation in equations]
    
        # check if funcNamesStack alredy exist:
        if 'funcNamesStack' in self.__dict__:
            self.funcNamesStack.extend(funcNamesStack)
        else:
            self.funcNamesStack = funcNamesStack
        # END FOR

        # FOR parsing
        for eq in equations:
            eq.values = eq.system

    def set_params_for_interconnects(self, model):
        '''
        DESCRIPTION:
        Fill params for interconnects 1d template.
        
        TODO:
        Fill parsedValues from parser.
        '''
        # FOR FILL params.ics
        ics = []

        def choice_equation_num(test, block):
            '''
            DESCRIPTION:
            Choice equation number from equationRegions
            if any satisfy the test, else choice default.
            '''
            for eqRegion in block.equationRegions:
                if test(eqRegion):
                    equationNum = eqRegion.equationNumber
                    break
            else:
                equationNum = block.defaultEquation
            return(equationNum)

        for blockNumber, block in enumerate(model.blocks):
            for iconn in model.interconnects:
                # for closed block
                if iconn.block1 == blockNumber and iconn.block2 == blockNumber:

                    # choice left or right side of block
                    # i.e. 0.0 or block.sizeX
                    Range1 = (iconn.block1Side == 1) * block.sizeX
                    Range2 = (iconn.block2Side == 1) * block.sizeX

                    # return either xfrom or xto for block
                    coord1 = lambda region: ((iconn.block1Side == 0) * region.xfrom
                                             + (iconn.block1Side == 1) * region.xto)
                    coord2 = lambda region: ((iconn.block2Side == 0) * region.xfrom
                                             + (iconn.block2Side == 1) * region.xto)

                    # find equation
                    # for first block (one side of closed block)
                    side_test = lambda eqRegion: coord1(eqRegion) == Range1
                    equationNum1 = choice_equation_num(side_test, block)

                    # find equation
                    # for second block (other side of closed block)
                    side_test = lambda eqRegion: coord2(eqRegion) == Range2
                    equationNum2 = choice_equation_num(side_test, block)

                    equation1 = model.equations[equationNum1]
                    equation2 = model.equations[equationNum2]

                    funcName1 = ("Block" + str(blockNumber) + "Interconnect__Side"
                                 + str(iconn.block1Side) + "_Eqn" + str(equationNum1))
                    funcName2 = ("Block" + str(blockNumber) + "Interconnect__Side"
                                 + str(iconn.block2Side) + "_Eqn" + str(equationNum2))

                    ic1 = Connection(0, '0', iconn.block2Side, [],
                                     equationNum2, equation2, funcName2)
                    ic1.boundName = determineNameOfBoundary(iconn.block2Side)
                    ic1.blockNumber = blockNumber

                    ic2 = Connection(1, '0', iconn.block1Side, [],
                                     equationNum1, equation1, funcName1)
                    ic2.boundName = determineNameOfBoundary(iconn.block1Side)
                    ic2.blockNumber = blockNumber

                    ics.append(ic1)
                    ics.append(ic2)
                    continue

                # for differ blocks
                elif blockNumber in [iconn.block1, iconn.block2]:
                    if iconn.block1 == blockNumber and iconn.block2 != blockNumber:
                        # case differ 1
                        side = iconn.block1Side
                    elif iconn.block2 == blockNumber and iconn.block1 != blockNumber:
                        # case differ 2
                        side = iconn.block2Side

                    firstIndex = len(ics)
                    Range = (side == 1) * block.sizeX
                    coord = lambda region: (side == 0) * region.xfrom + (side == 1) * region.xto

                    # find equation for block
                    side_test = lambda eqRegion: coord(eqRegion) == Range
                    equationNum = choice_equation_num(side_test, block)

                    equation = model.equations[equationNum]

                    funcName = ("Block" + str(blockNumber) + "Interconnect__Side"
                                + str(side) + "_Eqn" + str(equationNum))
                    ic = Connection(firstIndex, '0', side, [],
                                    equationNum, equation, funcName)
                    ic.boundName = determineNameOfBoundary(side)
                    ic.blockNumber = blockNumber
                    ics.append(ic)
                else:
                    continue

        self.ics = ics
        # END FOR FILL

        # FOR FuncArray
        funcNamesStack = [ic.funcName for ic in ics]

        # check if funcNamesStack alredy exist:
        if 'funcNamesStack' in self.__dict__:
            self.funcNamesStack.extend(funcNamesStack)
        else:
            self.funcNamesStack = funcNamesStack
        # END FOR

    def set_params_for_bounds(self, model):
        '''
        DESCRIPTION:
        Fill params for bound 1d template.
        
        TODO:
        Fill parsedValues from parser.
        '''

        # FOR FILL params.bounds
        self.bounds = []

        def test(region):
            '''
            DESCRIPTION:
            Test if region exist for this side.
            '''
            if side == 0:
                # test for left side
                return(region.xfrom == 0.0)
            else:
                # test for right side
                return(region.xto == block.sizeX)

        for blockNumber, block in enumerate(model.blocks):

            sides = [0, 1]
            for side in sides:
                # find equation number for side or use default
                regsEqNums = [eqReg.equationNumber for eqReg in block.equationRegions
                              if test(eqReg)]
                equationNum = regsEqNums[0] if len(regsEqNums) > 0 else block.defaultEquation
                equation = model.equations[equationNum]

                # find bound region for side or use default
                regionsForSide = [bRegion for bRegion in block.boundRegions
                                  if bRegion.side == side]
                if len(regionsForSide) > 0:
                    # if exist special region for that side
                    region = regionsForSide[0]
                    boundNumber = region.boundNumber
                    btype = model.bounds[boundNumber].btype
                    if btype == 0:
                        # for Dirichlet bound
                        funcName = ("Block" + str(blockNumber) + "Dirichlet__Bound"
                                    + str(side) + "_" + str(boundNumber) + "__Eqn" + str(equationNum))
                        outputValues = list(model.bounds[boundNumber].derivative)
                    elif btype == 1:
                        # for Neumann bound
                        funcName = ("Block" + str(blockNumber) + "Neumann__Bound"
                                    + str(side) + "_" + str(boundNumber) + "__Eqn" + str(equationNum))
                        outputValues = list(model.bounds[boundNumber].values)
                        
                        # special for Neumann bound
                        if side == 0 or side == 2:
                            for idx, value in enumerate(outputValues):
                                outputValues.pop(idx)
                                outputValues.insert(idx, '-(' + value + ')')
                    values = list(outputValues)
                else:
                    # if not, use default
                    funcName = ("Block" + str(blockNumber) + "DefaultNeumann__Bound"
                                + str(side) + "__Eqn" + str(equationNum))
                    values = len(equation.system) * ['0.0']
                    btype = 1
                    boundNumber = -1
                bound = BoundCondition(values, btype, side, [], boundNumber,
                                       equationNum, equation, funcName,
                                       block, blockNumber = blockNumber)
                bound.boundName = determineNameOfBoundary(side)
                self.bounds.append(bound)
        # END FOR FILL
        
        # FOR FuncArray
        funcNamesStack = [bound.funcName for bound in self.bounds]
        
        # check if funcNamesStack alredy exist:
        if 'funcNamesStack' in self.__dict__:
            self.funcNamesStack.extend(funcNamesStack)
        else:
            self.funcNamesStack = funcNamesStack
        # END FOR

    def set_params_for_parameters(self, model):
        '''
        DESCRIPTION:
        Fill parameters for .cpp.
        for cppOutsForGenerators.get_out_for_parameters

        USED PARAMETERS:
        model.params
        model.paramValues
        '''
        self.parameters = model.params
        self.parametersVal = model.paramValues[model.defaultParamsIndex]

    def set_params_for_initials(self, model):
        '''
        DESCRIPTION:
        Fill parameters for .cpp initial and Dirichlet functions.
        for cppOutsForGenerators.get_out_for_initials

        USED PARAMETERS:
        model.blocks
        model.initials
        model.bounds
        '''
        # FOR FILL model.blocks
        for block in model.blocks:

            # for Dirichlet
            # set() used for removing duplicates
            fDirichletIndexes = list(
                set(
                    [bR.boundNumber for bR in block.boundRegions
                     if (model.bounds[bR.boundNumber] == 0)]))
            block.fDirichletIndexes = fDirichletIndexes

            # for initials
            block.initialIndexes = [iR.initialNumber for iR in block.initialRegions
                                    if iR.initialNumber != block.defaultInitial]
            block.initials = [model.initials[idx] for idx in block.initialIndexes]
            block.bounds = [model.bounds[idx] for idx in block.fDirichletIndexes]
        self.blocks = model.blocks
        # END FOR FILL

    def init_params_general(self, blockNumber, dim):
        # parameters fill
        self.dim = dim
        if blockNumber is not None:
            self.blockNumber = blockNumber
        else:
            self.blockNumber = 0
        self.dim = dim
            
    def set_hat_for_all_cf(self, blockNumber):
        '''
        USED FUNCTIONS:
        blockNumber
        '''
        self.cf_hat_common = ('\n//========================='
                              + 'CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER '
                              + str(blockNumber)
                              + '========================//\n\n')
    
    def set_stride_map(self, blockNumber):
        '''
        USED FUNCTIONS:
        blockNumber
        self.dim
        '''
        self.strideMap = dict()
        vars = 'xyz'
        for i in range(int(self.dim[0])):
            var = vars[i]
            self.strideMap[var] = ('Block' + str(blockNumber)
                                   + 'Stride' + var.upper())
        
    def get_hat_for_cf(self, blockNumber, eqNumber):
        '''
        USED FUNCTIONS
        blockNumber
        equationNumber
        self.dim
        '''
        text = ('//'+str(eqNumber)
                + ' central function for '
                + str(self.dim)
                + 'd model for block with number '
                + str(blockNumber)
                + '\n')

        self.hatCf[(blockNumber, eqNumber)] = text
        return(text)

    def get_cf_name(self, blockNumber, eqNumber):
        text = ('Block' + str(blockNumber)
                + 'CentralFunction'
                + str(eqNumber))  # numsForEquats[num]
        self.namesCf[(blockNumber, eqNumber)] = text
        return(text)

    def get_cf_signature(self, blockNumber, name):
        '''
        USED FUNCTIONS:
        self.dim
        blockNumber
        name - function name
        '''
        signatureStart = 'void ' + name + '(double* result, double** source, double t,'
        signatureMiddle = ''
        vars = 'xyz'
        for i in range(int(self.dim[0])):
            var = vars[i]
            signatureMiddle = signatureMiddle + ' int idx' + var.upper() + ','
        signatureEnd = ' double* params, double** ic){\n'

        signature = signatureStart + signatureMiddle + signatureEnd
          
        idx = '\t int idx = ('
        vars = 'xyz'
        for i in range(int(self.dim[0])):
            var = vars[i]
            idx = idx + ' + idx' + var.upper() + ' * ' + self.strideMap[var]
        idx = idx + ') * Block' + str(blockNumber) + 'CELLSIZE;\n'
        
        return list([signature, idx])
    
    def rest(self):
        delays = []
                
        equationRightHandSide = parser.parseMathExpression(equationString, variables,
                                                           self.params, self.userIndepVars,
                                                           delays)
        function.extend([
            b.generateRightHandSideCodeDelay(blockNumber, variables[i],
                                             equationRightHandSide,
                                             self.userIndepVars, variables,
                                             self.params, list(),
                                             delays)])
        # for setDomain
        if len(delays) > 0:
            self.delays.extend(delays)
            
        function.extend(['}\n\n'])
        
        return ''.join(function), arrWithFuncName
