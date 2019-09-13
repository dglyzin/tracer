from gens.hs.gen_env.cpp.env.bounds.common \
                                   .bounds_common_cpp import GenCppCommon as GenCommonBound
from gens.hs.gen_env.cpp.env.centrals.cent_common import GenCommon as GenCommonCent

from spaces.math_space.common.env.system.sys_main import sysNet as System
from spaces.some_space.someFuncs import determineNameOfBoundary

from gens.hs.gen_env.postproc.postproc_main import Postproc

from copy import deepcopy


class GenEqs(GenCommonCent, GenCommonBound):
    '''
        ::

              ***x->
              *  
              |  ---side 2---
              y  |          |
                 s          s
                 i          i
                 d          d
                 e          e
                 0          1
                 |          |
                 ---side 3---
    '''
    def __init__(self, net):
        self.net = net
        self.postproc = Postproc(self)

    def set_params_for_eqs(self, model, blockNumber, func_dict, params):

        params.vertexs = []
        params.bounds = []
        params.centrals = []
        params.namesAndNumbers = {blockNumber: []}

        for sys_eq_num in func_dict:
            sys_data = func_dict[sys_eq_num]
            # eSystem = System(system=sys_data["system"])
            # print("eSystem:")
            # print(eSystem.eqs)

            # for borders:
            if "bound_values" in sys_data:
                eSystem = System(system=sys_data["system"])
                print("bound_values:")
                print(sys_data["bound_values"])
                bParam = Params()
                bParam.equation = eSystem
                bParam.blockNumber = blockNumber
                bParam.btype = sys_data["btype"]
                bParam.bound_values = sys_data["bound_values"]
                bParam.side_num = sys_data["side_num"]
                bParam.boundName = determineNameOfBoundary(bParam.side_num)
                bParam.funcName = self.get_func_name(bParam.btype,
                                                     bParam.blockNumber,
                                                     bParam.side_num,
                                                     sys_eq_num)
                parsed, bv_parsed = self.parse_equations(eSystem, model,
                                                         bParam.blockNumber,
                                                         bParam.btype,
                                                         bParam.side_num,
                                                         bParam.bound_values)
                bParam.parsedValues = parsed
                bParam.border_values_parsed = bv_parsed
                bParam.original = [e.sent for e in eSystem.eqs]
                params.bounds.append(bParam)
                params.namesAndNumbers[blockNumber].append(bParam.funcName)
                
                # for vertexs:
                if "vertex_values" in sys_data:

                    print("vertex_values:")
                    print(sys_data["vertex_values"])
                    # eSystem = System(system=sys_data["system"])
                    
                    # here eSystem and vParam.equation dont used
                    # because dont used delays/dirichlet postproc for them
                    vParam = Params()
                    vParam.blockNumber = bParam.blockNumber
                    vParam.btype = bParam.btype
                    vParam.bound_values = bParam.bound_values
                    # vParam = deepcopy(bParam)

                    vParam.boundName = "vertex " + str(sys_data["sides"])
                    vParam.funcName = ("vertex_eq_" + str(sys_eq_num)
                                       + "_sides_%d_%d" % tuple(sys_data["sides"]))
                    vParam.parsedValues = self.get_vertex_parsedValues(sys_data["vertex_values"])
                    # vParam.parsedValues remained from deepcopy
                    params.vertexs.append(vParam)
                    params.namesAndNumbers[blockNumber].append(vParam.funcName)

            # for centrals:
            cParam = Params()
            eSystem = System(system=sys_data["system"])
            cParam.equation = eSystem
            cParam.dim = model.dimension
            cParam.blockNumber = blockNumber
            cParam.funcName = ('Block%dCentralFunction_Eqn%d'
                               % (blockNumber, sys_eq_num))
            cParam.parsedValues = self._get_eq_cpp(eSystem, cParam)
            cParam.original = [e.sent for e in eSystem.eqs]

            params.centrals.append(cParam)
            params.namesAndNumbers[blockNumber].append(cParam.funcName)
        
        print("namesAndNumbers:")
        print(params.namesAndNumbers)

        ### FOR delays:
        # use gen_bounds.params.bounds in order to replace
        # delays in both bounds_edges and bounds_vertex:
        delays = self.postproc.postporc_delays([params.centrals,
                                                params.bounds])
        '''
        for vertex in gen_bounds.params.bounds_vertex:
            print("vertex.parsedValues:")
            print(vertex.parsedValues)
        '''
        print("delays:")
        print(delays)
        sizes_delays = dict([(len(delays[var]), delays[var])
                             for var in delays])
        try:
            max_delays_seq = sizes_delays[max(sizes_delays)]
            self.delays = max_delays_seq
            print("max_delays_seq:")
            print(max_delays_seq)
        except ValueError:
            self.delays = []
        ### END FOR

        ### FOR Dirichlet:
        # only after for delays (because postporc_delays rewrite output)
        self.postproc.postproc_dirichlet([params.bounds])
        ### END FOR

    def get_vertex_parsedValues(self, vertex_values):
        return(["result[idx + %d]=%s" % (idx, value)
                for idx, value in enumerate(vertex_values)])

    def get_func_name(self, btype, blockNumber, side_num,
                      equationNumber):

        btype_name = "Neumann" if btype == 1 else "Dirichlet"
        funcName = ("Block" + str(blockNumber)
                    + btype_name + str(side_num)
                    # + "_bound" + str(boundNumber)
                    + "__Eqn" + str(equationNumber))
        return(funcName)


class Params():
    pass
