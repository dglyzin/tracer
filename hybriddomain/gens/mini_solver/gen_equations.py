from hybriddomain.gens.hs.gen_env.cpp.env.bounds.common \
                                   .bounds_common_cpp import GenCppCommon as GenCommonBound
from hybriddomain.gens.hs.gen_env.cpp.env.centrals.cent_common import GenCommon as GenCommonCent

from hybriddomain.spaces.math_space.common.env.system.sys_main import sysNet as System
from hybriddomain.spaces.some_space.someFuncs import determineNameOfBoundary

from hybriddomain.gens.hs.gen_env.postproc.postproc_main import Postproc

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

    def fix_indexes(self, funcIdxs, eqs_dict, bs_dict):
        '''Create new funcIdxs, eqs_dict, bs_dict with
        new indexes. All indexes begining from 0 with step 1 and
        order as sotred old indexes.
        Indexes of eqs and bs is independent, eqs is everywhere used only
        in central_region, while bs is used only in sides, so even if indexes
        is same, they will not intersects.
 
        Examples:
        map bs = {0: ..., 164: ..., 183: ..., 135: ..., 73: ...}
        to 0->0, 73->1, 135->2, 164->3, 183->3
        map eqs = {0: ..., 75: ..., 164: ...,}
        to 0->0, 75->1, 164->2
        map same indexes in funcIdxs (sides like bs, centrals like eqs)

        Inputs:
        
        - ``funcIdxs`` -- array with old indexes (gray color variation)
        side{0,1,2,3} will be used only for bounds, central_region only for
        centrals.
        - ``eqs_dict`` -- dict with old indexes as keys (as in funcIdxs)
        - ``bs_dict`` -- dict with old indexes as keys (as in funcIdxs)

        Output:
        Same as input but with new indexes.
        '''
        img_width, img_height = map(lambda size: size-1, funcIdxs.shape)

        # FOR create new funcIdxs:
        new_funcIdxs = funcIdxs.copy()

        side0 = funcIdxs[:, 0]
        side1 = funcIdxs[:, img_width]
        side2 = funcIdxs[0, :]
        side3 = funcIdxs[img_height, :]
        central_region = funcIdxs[0: img_height, 0: img_width]

        new_side0 = new_funcIdxs[:, 0]
        new_side1 = new_funcIdxs[:, img_width]
        new_side2 = new_funcIdxs[0, :]
        new_side3 = new_funcIdxs[img_height, :]
        new_central_region = new_funcIdxs[0: img_height, 0: img_width]
        # END FOR

        # FOR new bs idxs:
        bs_idxs = list(bs_dict.keys())
        bs_idxs.sort()
        new_bs_dict = dict([(new_idx, bs_dict[old_idx])
                            for new_idx, old_idx in enumerate(bs_idxs)])
        print("new_bs_dict:")
        print(new_bs_dict)

        for new_idx, old_idx in enumerate(bs_idxs):
            new_side0[side0 == old_idx] = new_idx
            new_side1[side1 == old_idx] = new_idx
            new_side2[side2 == old_idx] = new_idx
            new_side3[side3 == old_idx] = new_idx
        # END FOR
        
        # FOR new eqs idxs:
        eqs_idxs = list(eqs_dict.keys())
        eqs_idxs.sort()
        new_eqs_dict = dict([(new_idx, eqs_dict[old_idx])
                             for new_idx, old_idx in enumerate(eqs_idxs)])
        print("new_eqs_dict:")
        print(new_eqs_dict)
        for new_idx, old_idx in enumerate(eqs_idxs):
            new_central_region[central_region == old_idx] = new_idx
        # END FOR

        return((new_funcIdxs, new_eqs_dict, new_bs_dict))

    def create_bs_sides(self, img):

        '''Create bs_sides dict i.e. factorize bounds
        indexes at sides. Used for parse (eq, bound, side) (because
        side needed for parser with bounds)'''

        img_width, img_height = map(lambda size: size-1, img.shape)

        bs_sides = {0: [], 1: [], 2: [], 3: []}

        # side 0:
        for bidx in img[:, 0]:
            if bidx not in bs_sides[0]:
                bs_sides[0].append(bidx)
        # side 1:
        for bidx in img[:, img_width]:
            if bidx not in bs_sides[1]:
                bs_sides[1].append(bidx)
        # side 2:
        for bidx in img[0, :]:
            if bidx not in bs_sides[2]:
                bs_sides[2].append(bidx)
        # side 3:
        for bidx in img[img_height, :]:
            if bidx not in bs_sides[3]:
                bs_sides[3].append(bidx)
        return(bs_sides)

    def set_params_for_bounds(self, model, blockNumber,
                              eqs_dict, bs_dict, bs_sides, params):
        '''for each equation in eqs and for each bound in bounds
        create dict {(eq_num, bound_num): func_name}
        '''
        params.equations_bounds = []
        functionMap = {}

        for eq_num in eqs_dict:
            for side_num in bs_sides:
                for bound_num in bs_sides[side_num]:
                    
                    eq_data = eqs_dict[eq_num]
                    bound_data = bs_dict[bound_num]
                    print("bound_num:")
                    print(bound_num)
                    eSystem = System(system=eq_data["system"])
                    # bSystem = System(system=bound_data["system"])
                
                    eqbParam = Params()
                    eqbParam.equation = eSystem
                    eqbParam.dim = model.dimension
                    eqbParam.blockNumber = blockNumber
                    eqbParam.funcName = ('Block%dEquation%dBound%dSide%d'
                                         % (blockNumber, eq_num,
                                            bound_num, side_num))
                    eqbParam.btype = bound_data["btype"]
                    parsedValues, bv_parsed = self.parse_equations(eSystem, model,
                                                                   blockNumber,
                                                                   bound_data["btype"],
                                                                   side_num,
                                                                   bound_data["system"])
                    eqbParam.parsedValues = parsedValues
                    eqbParam.border_values_parsed = bv_parsed
                    eqbParam.eq_original = [e.sent for e in eSystem.eqs]
                    eqbParam.bound_original = [sent for sent in bound_data["system"]]
                    params.equations_bounds.append(eqbParam)
                    functionMap[(eq_num, bound_num)] = "p_" + eqbParam.funcName
        params.functionMap = functionMap

    def set_params_for_eqs(self, model, blockNumber, func_dict, params):

        params.vertexs = []
        params.bounds = []
        params.centrals = []
        params.namesAndNumbers = {blockNumber: []}
        # new_func_dict = {}
        # new_idx = 0

        for sys_eq_num in func_dict:
            sys_data = func_dict[sys_eq_num]
            
            # new funcIdxs with new idxs:
            # new_func_dict[new_idx] = sys_data
            # sys_data["old_idx"] = sys_eq_num
            # new_idx += 1

            # eSystem = System(system=sys_data["system"])
            # print("eSystem:")
            # print(eSystem.eqs)

            '''
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
            '''
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

    def apply_postproc(self, params):

        ### FOR delays:
        # use gen_bounds.params.bounds in order to replace
        # delays in both bounds_edges and bounds_vertex:
        delays = self.postproc.postporc_delays([params.centrals,
                                                params.equations_bounds])
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
        self.postproc.postproc_dirichlet([params.equations_bounds])
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
