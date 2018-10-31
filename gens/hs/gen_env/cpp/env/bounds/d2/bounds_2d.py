from gens.hs.gen_env.cpp.env.base.base_common import GenBaseCommon
from gens.hs.gen_env.cpp.env.bounds.common.bounds_common_cpp import GenCppCommon

from spaces.some_space.someClasses import Params
from spaces.some_space.someFuncs import determineNameOfBoundary
# from spaces.math_space.common.env.equation.equation import Equation


class GenCommon(GenBaseCommon, GenCppCommon):
    '''
    :doc:` overview <overview>`
   
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
        self.net.params = Params()

    def set_params_for_bounds(self, model, funcNamesStack,
                              ics=[]):
        '''
        DESCRIPTION:

        Collect bounds params for cpp template and dom files
        for all 2d blocks:

        - ``self.net.params.bounds`` -- all bounds
        - ``self.net.params.bounds_edges`` -- bounds
        for edges
        - ``self.net.params.bounds_vertex`` -- bounds
        for vertexs.

        ics used for checking if interconnect for
        this side exist. So this function must be used
        after set_params_for_dom_interconnects.

        Also add ``bound.funcName`` to ``funcNameStack``
        '''
        # main code:

        # sides:
        sides = [block.sides[side_num]
                 for block in model.blocks
                 for side_num in block.sides]
        #        if not self.check_ic_exist(side_num,
        #                                   block.blockNumber, ics)]

        '''
        new_sides = [transform_side(side, block)
                     for block in model.blocks
                     for side in [2, 3, 0, 1]]
        
        #             if not check_interconnect_exist(self, side,
        #                                             block.blockNumber)]
        '''

        # TODO: unite side and params_edges
        # or disunite them in bounds 1d.
        self.sides = sides
        
        # make bounds for side
        params_edges = [bParams for side in sides
                        for bParams in self.make_bounds_for_edges(model, side)]
        #                     if bound not in self.bounds]
        '''
        # transform vertex:
        new_vertexs = [transform_vertex(vertex, new_sides, block)
                       for block in model.blocks
                       for vertex in [[0, 2], [2, 1], [1, 3], [3, 0]]]
        '''

        # make bounds for vertex
        params_vertex = [self.make_bounds_for_vertex(block.vertexs[k_vertex],
                                                     params_edges)
                         for block in model.blocks
                         for k_vertex in block.vertexs]
        params_vertex = [param for param in params_vertex
                         if param is not None]
        # END FOR FILL

        self.net.params.bounds = Params()
        self.net.params.bounds_edges = Params()
        self.net.params.bounds_vertex = Params()

        self.net.params.bounds.extend(params_edges)
        self.net.params.bounds.extend(params_vertex)
        self.net.params.bounds_edges.extend(params_edges)
        self.net.params.bounds_vertex.extend(params_vertex)

        # print("params_vertex[0].parsedValues")
        # print(self.net.params.bounds_vertex[0].parsedValues)

        # FOR FuncArray
        funcNamesStackLocal = [bound.funcName
                               for bound in self.net.params.bounds]

        self.fill_func_names_stack(funcNamesStack, funcNamesStackLocal)
        # END FOR

    def make_bounds_for_edges(self, model, side):
        '''
        DESCRIPTION:

        Collect this parameters for template:
        
        - ``bParams.name``
        - ``bParams.side_num``
        - ``bParams.blockNumber``
        - ``bParams.boundNumber``
        - ``bParams.equationNumber``
        
        - ``bParams.funcName`` -- func name in cpp
        - ``bParams.btype`` -- Dirichlet 0, Neumann 1
        - ``bParams.equation`` -- system of equations
        SysNet object
        - ``bParams.parsedValues``
        - ``bParams.original`` -- original for comment
        - ``bParams.boundName`` -- bound name for comment

        This parameters also collected for dom:
        
        - ``bParams.blockNumber``
        - ``bParams.side_num``
        - ``bParams.funcName`` -- for defining func index in
        namesAndNumbers dict.
        - ``bParams.region``
        
        Inputs:

        - ``side`` -- is ``Side`` object::

        side:

         - ``side_num``,

         - ``block.blockNumber``,

         - ``interval`` -- of type oIntervals

           where oIntervals =
                 [Interval([x, y], name={'b': bval, 'e', eval})]
        '''
        bounds = []
        for interval in side.intervals:
            
            # if interconnect then continue:
            try:
                interval.name['i']
                continue
            except KeyError:
                pass

            bParams = Params()
            bParams.name = 'sides bound'
            bParams.side_num = side.side_num
            bParams.blockNumber = side.block.blockNumber
            bParams.boundNumber = interval.name['b']
            bParams.equationNumber = interval.name['e']
            bParams.interval = interval

            eSystem = model.equations[bParams.equationNumber].copy()

            if bParams.boundNumber is not None:

                # FOR set up funcName and border values:
                args = (model, bParams.blockNumber, bParams.side_num,
                        bParams.boundNumber, bParams.equationNumber)

                btype = model.bounds[bParams.boundNumber].btype

                # for Dirichlet bound
                if btype == 0:
                    func = self.get_func_for_dirichlet(*args)

                # for Neumann bound
                elif btype == 1:
                    func = self.get_func_for_neumann(*args)

                funcName = func[0]
                border_values = list(func[1])

            else:

                btype = 0
                args = (eSystem, bParams.blockNumber, bParams.side_num,
                        bParams.equationNumber)
                func = self.get_func_default(*args)

                funcName = func[0]
                border_values = func[1]

            args = (eSystem, model, bParams.blockNumber, btype,
                    bParams.side_num, border_values)
            parsed = self.parse_equations(*args)

            bParams.funcName = funcName
            bParams.btype = btype
            bParams.equation = eSystem
            bParams.parsedValues = parsed
            bParams.original = [e.sent for e in eSystem.eqs]

            # for comment
            bParams.boundName = determineNameOfBoundary(bParams.side_num)

            # collect for functionMaps:
            interval.name['fm'] = bParams

            bounds.append(bParams)
        return(bounds)

    def make_bounds_for_vertex(self, vertex, params_edges):
        '''
        DESCRIPTION:

        If vertex left edge closest region has ic value
        (i.e. this region donot exist in params_edges)
        then
        if right edge closest region has no ic value,
        use this region
        else
        use ic data (todo).

        Collect this parameters for template:

        - ``vParams.name``
        - ``vParams.sides_nums``
        - ``vParams.blockNumber``
        - ``vParams.boundNumber``
        - ``vParams.equationNumber``

        - ``vParams.funcName``
        - ``vParams.bound_side``
        - ``vParams.btype``
        - ``vParams.equation`` -- equation from left
        edge.

        - ``vParams.parsedValues``
        - ``vParams.original``

        This parameters also collected for dom:
        
        - ``bParams.blockNumber``
        - ``bParams.side_num``
        - ``bParams.funcName`` -- for defining func index in
        namesAndNumbers dict.
        - ``bParams.interval``
        
        Inputs:

        - ``vertex`` -- is ``Vertex`` object::
            
        vertex:
        
        - ``boundNumber`` -- of left edge (side)
        - ``equationNumber`` -- of left edge (side)
        - ``sides_nums`` -- like [0, 2]
        - ``interval`` -- of left edge (side)

        - ``params_edges`` -- out of make_bounds_for_edges.
        Used for side data for vertex.
        '''
        # find bound for left edge:
        left_edges = [bParams for bParams in params_edges
                      if bParams.side_num == vertex.sides_nums[0]
                      and bParams.blockNumber == vertex.block.blockNumber
                      and bParams.interval == vertex.left_interval]
        # if interconnect exist for left edges
        # (so there is no region in params_edges)
        # use right:
        try:
            vertex_edge = left_edges[0]
        except IndexError:
            right_edges = [bParams for bParams in params_edges
                           if bParams.side_num == vertex.sides_nums[1]
                           and bParams.blockNumber == vertex.block.blockNumber
                           and bParams.interval == vertex.right_interval]
            # if interconnect exist for left and right
            # (so there is no region in params_edges)
            try:
                vertex_edge = right_edges[0]
            except IndexError:
                # TODO: add ic to vertex
                raise(BaseException("Case when vertex has ic regions"
                                    + " from both sides is not"
                                    + " implemented yet"))
                return(None)
        # END FOR

        vParams = Params()
        vParams.name = 'vertex bound'
        vParams.sides_nums = vertex.sides_nums
        vParams.blockNumber = vertex.block.blockNumber

        # data of left side (with index 0)
        vParams.boundNumber = vertex.boundNumber
        vParams.equationNumber = vertex.equationNumber

        # for make funcName for defaults
        funcName = self.get_vertex_funcName(vertex)

        vParams.funcName = funcName
        vParams.bound_side = vertex_edge
        vParams.btype = vertex_edge.btype
        vParams.equation = vertex_edge.equation  # .copy()

        # use result[something] = source[0][something];
        parsedValues = self.parse_equations_vertex(vertex_edge.parsedValues)
        vParams.parsedValues = parsedValues
        # vParams.parsedValues = vertex_edge.parsedValues

        # print("parsedValues")
        # print(vParams.parsedValues)
        vParams.original = vertex_edge.original

        return(vParams)

    def get_vertex_funcName(self, vertex):
        blockNumber = vertex.block.blockNumber
        tFuncNameVertex = ('Block'+str(blockNumber)+'Default_Vertex'
                           + str(vertex.sides_nums[0])
                           + '_'+str(vertex.sides_nums[1])
                           + '__Eqn'+str(vertex.equationNumber))
        return(tFuncNameVertex)
