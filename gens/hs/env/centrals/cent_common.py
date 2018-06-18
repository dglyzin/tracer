from gens.hs.env.base.base_common import GenBaseCommon
from gens.hs.env.base.base_common import Params

from string import Template

import logging

from copy import deepcopy as copy
from copy import copy as weak_copy


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.cent_common')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('cent_common')
logger.setLevel(level=log_level)
'''


class GenCommon(GenBaseCommon):
    
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_centrals(self, model, funcNamesStack):
        '''
        DESCRIPTION:
        Collect this parameters for template:
        
        equation.blockNumber
        equation.eqautionNumber
        equation.dim
        equation.funcName
        equation.parsedValues
        '''
        dim = model.dimension


        sFuncName = '''Block${blockNumber}CentralFunction_Eqn${equationNumber}'''
        tFuncName = Template(sFuncName)

        # FOR FILL params.equations
        self.net.params = Params()
        eParams = self.net.params

        for blockNumber, block in enumerate(model.blocks):
            reservedSpace = self._init_acc(dim)

            # collect all equations for block
            # equationRegions should be sorted
            for eRegion in block.equationRegions:
                reservedSpace = self._acc(dim, eRegion, reservedSpace)

                # for removing trivial cases
                cond = (eRegion.xfrom == eRegion.xto
                        and
                        (eRegion.xto == 0.0 or eRegion.xto == block.sizeX))

                # numsForSystems = [eq.number for eq in equations]
                # if eRegion.equationNumber not in numsForSystems and not cond:
                if not cond:
                    eParam = self._collect_eq_from_region(model, eRegion,
                                                          dim, blockNumber,
                                                          tFuncName)
                    if eParam.funcName not in [e.funcName for e in eParams]:
                        eParams.append(eParam)

            # add default equation at remaining regions.
            if self._do_generate_default(dim, reservedSpace, block):
                eParam = self._collect_eq_default(model, block, dim,
                                                  blockNumber, tFuncName)

                if eParam.funcName not in [e.funcName for e in eParams]:
                    eParams.append(eParam)

        # self.net.params = eParams
        # END FOR FILL

        # FOR FuncArray
        funcNamesStackLocal = [eParam.funcName for eParam in eParams]
        self.fill_func_names_stack(funcNamesStack, funcNamesStackLocal)
        # END FOR

        # FOR parsing
        # for eq in equations:
        #     eq.values = eq.eqs
        # END FOR

    def _collect_eq_from_region(self, model, eRegion, dim,
                                blockNumber, tFuncName):
        # equation = copy(model.equations[eRegion.equationNumber])
        eParam = Params()
        eSystem = model.equations[eRegion.equationNumber]

        eParam.equationNumber = eRegion.equationNumber
        eParam.eRegion = eRegion
        eParam.dim = dim
        eParam.blockNumber = blockNumber
        eParam.funcName = tFuncName.substitute(blockNumber=blockNumber,
                                               equationNumber=eRegion.equationNumber)
        
        eParam.default = False

        eParam.parsedValues = self._get_eq_cpp(eSystem, eParam)
        eParam.original = [e.sent for e in eSystem.eqs]

        logger.debug("parsedValues")
        logger.debug(eParam.parsedValues)

        logger.debug('blockNumber eqReg=%s' % str(blockNumber))
        return(eParam)

    def _collect_eq_default(self, model, block, dim, blockNumber, tFuncName):
        # model.equations is a list of equation systems

        # equation = copy(model.equations[block.defaultEquation])
        eSystem = model.equations[block.defaultEquation]
        eParam = Params()

        eParam.equationNumber = block.defaultEquation
        eParam.eRegion = None
        eParam.dim = dim
        eParam.blockNumber = blockNumber
        eParam.funcName = tFuncName.substitute(blockNumber=blockNumber,
                                               equationNumber=block.defaultEquation)
        eParam.default = True

        eParam.parsedValues = self._get_eq_cpp(eSystem, eParam)
        eParam.original = [e.sent for e in eSystem.eqs]

        logger.debug("parsedValues")
        logger.debug(eParam.parsedValues)

        logger.debug('blockNumber revSp=%s' % str(blockNumber))
        return(eParam)

    def _get_eq_cpp(self, eSystem, eParam):

        eSystem.cpp.set_default()
        eSystem.cpp.set_dim(eParam.dim)
        eSystem.cpp.set_blockNumber(eParam.blockNumber)
        eSystem.cpp.set_diff_type_common(diffType='pure', diffMethod='common')

        return([eq.flatten('cpp') for eq in eSystem.eqs])
    
    def _init_acc(self, dim):
        if dim == 1:
            return(0)
        elif dim == 2:
            return([0, 0])

    def _acc(self, dim, eRegion, reservedSpace):
        '''
        DESCRIPTION:
        Accumulate equation regions area for checking
        either it enough or use default eqation.
        '''
        if dim == 1:
            reservedSpace += eRegion.xto - eRegion.xfrom
        elif dim == 2:
            reservedSpace[0] += eRegion.xto - eRegion.xfrom
            reservedSpace[1] += eRegion.yto - eRegion.yfrom
        return(reservedSpace)

    def _do_generate_default(self, dim, reservedSpace, block):
        '''
        DESCRIPTION:
        Check use default or not.
        '''
        if dim == 1:
            return(block.size.sizeX > reservedSpace)
        elif dim == 2:
            return(block.size.sizeX > reservedSpace[0]
                   or
                   block.size.sizeY > reservedSpace[1])
