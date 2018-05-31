from gens.hs.cpp.common.base import GenBase, Params
from math_space.common.someFuncs import determineNameOfBoundary
from math_space.common.equation.equation import Equation


class Gen(GenBase):
    '''
    Fill self.params for bound 1d template:
    (see self.set_params_for_bounds)

    Generate cpp:
    (see get_out_for_bounds)
    '''
    def get_out_for_bounds(self):
        template = self.env.get_template('bound_conditions.template')

        args = {
            'bounds': self.make_bounds_unique(self.params),
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def make_bounds_unique(self, bounds):
        def unique_generator(bounds):
            unique = []
            for bound in bounds:
                if bound.funcName not in unique:
                    unique.append(bound.funcName)
                    yield(bound)
        return([bound for bound in unique_generator(bounds)])

    def set_params_for_bounds(self, model, ics=[]):
        '''
        DESCRIPTION:
        Collect this parameters for template:

            bound.blockNumber,
            bound.boundName,
            bound.funcName,
            bound.parsedValues

        Collect this parameters for dom:

            bound.dim
            bound.btype = btype
            bound.side = side_num
            bound.boundNumber = boundNumber
            bound.equationNumber = equationNum
            bound.equation = eSystem
            bound.block = block
            bound.blockNumber = blockNumber

        ics used for checking if interconnect for
        this side exist. So this function must be used
        after set_params_for_dom_interconnects.
        '''
        self.params = []

        for blockNumber, block in enumerate(model.blocks):
            # side: <0 -----side 2------ 1>

            # sides_nums = [0, 1]
            for side_num in [0, 1]:
                # side = block.sides[2]

                # check if interconnect for this side exist
                # if 'ics' in self.__dict__.keys():
                if len(ics) > 0:
                    icSides = [ic.side for ic in ics
                               if ic.blockNumber == blockNumber]
                    if side_num in icSides:
                        # if exist then no boundary needed
                        #logger.debug('icSides = %s' % str(icSides))
                        #logger.debug('blockNumber = %s' % str(blockNumber))
                        #logger.debug('side_num = %s' % str(side_num))
                        continue

                # find equation number for side or use default
                regsEqNums = [eqReg.equationNumber
                              for eqReg in block.equationRegions
                              if self.test(block, eqReg, side_num)]
                equationNum = (regsEqNums[0] if len(regsEqNums) > 0
                               else block.defaultEquation)
                eSystem = model.equations[equationNum]

                # find bound region for side or use default
                regionsForSide = [bRegion
                                  for k in block.boundRegions
                                  for bRegion in block.boundRegions[k]
                                  if bRegion.side_num == side_num]

                # if exist special region for that side
                if len(regionsForSide) > 0:
                    region = regionsForSide[0]
                    boundNumber = region.boundNumber
                    bound = model.bounds[boundNumber]
                    
                    # for Dirichlet bound
                    if bound.btype == 0:
                        args = (model, blockNumber, side_num,
                                boundNumber, equationNum)
                        func = self._get_func_for_dirichlet(*args)
                    
                    # for Neumann bound
                    elif bound.btype == 1:
                        args = (model, blockNumber, side_num,
                                boundNumber, equationNum)
                        func = self._get_func_for_neumann(*args)

                    funcName = func[0]
                    border_values = list(func[1])
                    btype = bound.btype
                else:
                    # if not, use default

                    args = (eSystem, blockNumber, side_num,
                            equationNum)
                    func = self._get_func_default(*args)

                    funcName = func[0]
                    border_values = func[1]
                    btype = 1
                    boundNumber = -1

                # set up equation:
                self._set_eq_base_params(eSystem, model.dimension,
                                         blockNumber)
                self._set_eq_spec_params(model, block, eSystem, btype,
                                         side_num, border_values)
                parsed = self._get_eq_cpp(eSystem)

                # FOR collect template data:
                bParams = Params()
                bParams.dim = model.dimension
                bParams.values = border_values
                bParams.btype = btype
                bParams.side = side_num
                bParams.boundNumber = boundNumber
                bParams.equationNumber = equationNum
                bParams.equation = eSystem
                bParams.funcName = funcName
                bParams.block = block
                bParams.blockNumber = blockNumber

                # in comment
                bParams.boundName = determineNameOfBoundary(side_num)
                bParams.parsedValues = parsed
                bParams.original = [e.sent for e in eSystem.eqs]
                self.params.append(bParams)
                # END FOR
        
        # FOR FuncArray
        funcNamesStack = [bound.funcName for bound in self.params]
        self.fill_func_names_stack(funcNamesStack)
        # END FOR

    def test(self, block, region, side_num):
        '''
        DESCRIPTION:
        Test if region exist for this side.
        '''
        if side_num == 0:
            # test for left side
            return(region.xfrom == 0.0)
        else:
            # test for right side
            return(region.xto == block.size.sizeX)

    def _get_func_for_dirichlet(self, model, blockNumber, side_num,
                                boundNumber, equationNumber):
        
        '''Generate func names and get values for Dirichlet'''

        funcName = ("Block" + str(blockNumber)
                    + "Dirichlet__Bound" + str(side_num)
                    + "_" + str(boundNumber)
                    + "__Eqn" + str(equationNumber))

        outputValues = list(model.bounds[boundNumber].derivative)

        return((funcName, outputValues))

    def _get_func_for_neumann(self, model, blockNumber, side_num,
                              boundNumber, equationNumber):

        '''Generate func names and get values for Neumann'''

        funcName = ("Block" + str(blockNumber)
                    + "Neumann__Bound" + str(side_num)
                    + "_" + str(boundNumber)
                    + "__Eqn" + str(equationNumber))
        outputValues = list(model.bounds[boundNumber].values)
            
        # special for Neumann bound
        if side_num == 0 or side_num == 2:
            for idx, value in enumerate(outputValues):
                outputValues.pop(idx)
                outputValues.insert(idx, '-(' + value + ')')

        return((funcName, outputValues))

    def _get_func_default(self, equation, blockNumber, side_num,
                          equationNumber):

        '''Generate func names and get values for default'''

        funcName = ("Block" + str(blockNumber)
                    + "DefaultNeumann__Bound"
                    + str(side_num)
                    + "__Eqn" + str(equationNumber))
        values = len(equation.eqs) * ['0.0']
        return((funcName, values))

    def _set_eq_base_params(self, eSystem, dim, blockNumber):
        eSystem.cpp.parse()
        eSystem.cpp.set_default()
        eSystem.cpp.set_dim(dim=dim)
        eSystem.cpp.set_blockNumber(blockNumber)
        
    def _set_eq_spec_params(self, model, block, eSystem, btype,
                            side_num, border_values):
        '''parse border values:
        for derivOrder = 1:
           du/dx = bound.value[i]
        for derivOrder = 2:
           left border
              ddu/ddx = 2*(u_{1}-u_{0}-dy*bound.value[i])/(dx^2)
           right border
              ddu/ddx = 2*(u_{n-1}-u_{n}-dy*bound.value[i])/(dx^2)
        '''

        cellsize = block.size.get_cell_size(model)
        shape = [cellsize/float(model.grid.gridStepX),
                 cellsize/float(model.grid.gridStepY),
                 cellsize/float(model.grid.gridStepZ)]
        dim = block.size.dimension
        
        # parse border values:
        for i, bv in enumerate(border_values):
            ebv = Equation(bv)
            ebv.parse()
            ebv.set_default()
            ebv.set_dim(dim=dim)
            ebv.set_shape(shape=shape)
            ebv_cpp = ebv.flatten('cpp')
            eSystem.eqs[i].set_diff_type(diffType='pure',
                                         diffMethod='special',
                                         btype=btype, side=side_num,
                                         func=ebv_cpp)
            
    def _get_eq_cpp(self, eSystem):
        return([eq.flatten('cpp') for eq in eSystem.eqs])
                
