from spaces.math_space.common.env.equation.equation import Equation

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('bounds.bounds_common_dom')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('bounds_common_dom')
logger.setLevel(level=log_level)
'''


class GenCppCommon():

    def check_ic_exist(self, side_num, blockNumber, ics):
        '''
        DESCRIPTION:

        Check if interconnect for this side exist in ics.
        '''
        
        # if 'ics' in self.__dict__.keys():
        if len(ics) > 0:
            ics_sides = [ic.side_num for ic in ics
                         if ic.blockNumber == blockNumber]
            if side_num in ics_sides:
                # if exist then no boundary needed
                # logger.debug('icSides = %s' % str(icSides))
                # logger.debug('blockNumber = %s' % str(blockNumber))
                # logger.debug('side_num = %s' % str(side_num))

                return(True)
            else:
                return(False)
        return(False)
        
    def get_func_for_dirichlet(self, model, blockNumber, side_num,
                               boundNumber, equationNumber):
        
        '''Generate func names and get values for Dirichlet'''

        btype = 0
        funcName = self.get_func_name(btype, blockNumber, side_num,
                                      boundNumber, equationNumber)

        outputValues = list(model.bounds[boundNumber].derivative)

        return((funcName, outputValues))

    def get_func_for_neumann(self, model, blockNumber, side_num,
                             boundNumber, equationNumber):

        '''Generate func names and get values for Neumann'''

        btype = 1
        funcName = self.get_func_name(btype, blockNumber, side_num,
                                      boundNumber, equationNumber)
        outputValues = list(model.bounds[boundNumber].values)
            
        # special for Neumann bound
        if side_num == 0 or side_num == 2:
            for idx, value in enumerate(outputValues):
                outputValues.pop(idx)
                outputValues.insert(idx, '-(' + value + ')')

        return((funcName, outputValues))

    def get_func_default(self, equation, blockNumber, side_num,
                         equationNumber):

        '''Generate func names and get values for default'''

        funcName = ("Block" + str(blockNumber)
                    + "DefaultNeumann__side"
                    + str(side_num)
                    + "__Eqn" + str(equationNumber))
        values = len(equation.eqs) * ['0.0']
        return((funcName, values))

    def get_func_name(self, btype, blockNumber, side_num,
                      boundNumber, equationNumber):

        btype_name = self.get_btype_name(btype, boundNumber)
        funcName = ("Block" + str(blockNumber)
                    + btype_name + str(side_num)
                    + "_bound" + str(boundNumber)
                    + "__Eqn" + str(equationNumber))
        return(funcName)

    def get_btype_name(self, btype, boundNumber):
        '''
        DESCRIPTION::

        Get string name of bound type for ``funcName``.
        '''
        # btype = model.bounds[boundNumber].btype
        if btype == 1:
            return("Neumann__side")
        elif(btype == 0):
            return("Dirichlet__side")

    def parse_equations(self, eSystem, model, blockNumber,
                        btype, side_num, border_values):

        # set up equation:
        self.set_eq_base_params(eSystem, model.dimension,
                                blockNumber)
        block = model.blocks[blockNumber]
        self.set_eq_spec_params(model, block, eSystem, btype,
                                side_num, border_values)
        parsed = self.get_eq_cpp(eSystem)
        return(parsed)
        
    def set_eq_spec_params(self, model, block, eSystem, btype,
                           side_num, border_values):
        '''parse border values:

        for derivOrder = 1:

        .. math:: du/dx = bound.value[i]

        for derivOrder = 2:

           left border:

        .. math:: ddu/ddx = 2*(u_{1}-u_{0}-dy*bound.value[i])/(dx^2)
           
           right border:

        .. math:: ddu/ddx = 2*(u_{n-1}-u_{n}-dy*bound.value[i])/(dx^2)
        '''

        cellsize = block.size.get_cell_size(model)
        shape = [cellsize/float(model.grid.gridStepX),
                 cellsize/float(model.grid.gridStepY),
                 cellsize/float(model.grid.gridStepZ)]
        dim = block.size.dimension
        
        # parse border values:
        for i, bv in enumerate(border_values):
            ebv = Equation(bv)
            ebv.parser.parse()
            ebv.replacer.cpp.editor.set_default()
            ebv.replacer.cpp.editor.set_dim(dim=dim)
            ebv.replacer.cpp.editor.set_shape(shape=shape)

            # make cpp for border values:
            ebv_cpp = ebv.replacer.cpp.make_cpp()

            # set eq parameters (including of border values):
            editor = eSystem.eqs[i].replacer.cpp.editor
            editor.set_diff_type(diffType='pure',
                                 diffMethod='special',
                                 btype=btype, side=side_num,
                                 func=ebv_cpp)
