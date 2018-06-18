from gens.hs.cpp.common.base import GenBase


class Gen(GenBase):

    def get_out_for_bounds(self, params):
        template = self.env.get_template('bound_conditions.template')

        args = {
            'bounds': self.make_bounds_unique(params.bounds),
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

    def set_params_for_bounds_2d(self, model):
        '''
        DESCRIPTION:
        Fill params for bound 2d template.
        '''

        # FOR FILL params.bounds
        self.bounds = []

        # FOR helpful functions:
        # templates for funcName
        tFuncName = Template('''Block${blockNumber}${btype}${side}_${boundNumber}__Eqn${equationNumber}''')
        tFuncNameDefault = Template('''Block${blockNumber}DefaultNeumann__Bound${side}__Eqn${equationNumber}''')
        tFuncNameVertex = Template('''Block${blockNumber}Default_Vertex${side_0}_${side_1}__Eqn${equationNumber}''')

        def get_btype_name(boundNumber):
            '''
            DESCRIPTION:
            Get string name of bound type for funcName.
            '''
            btype = model.bounds[boundNumber].btype
            if btype == 1:
                return("Neumann__Bound")
            elif(btype == 0):
                return("Dirichlet__Bound")

        def make_bounds(side):
            '''
            DESCRIPTION:
            Create funcName, outputValues and equation (for parser)
            boundName for comment.
            side is out of transform_side
            side =
            {'side': side,
             'blockNumber': block.blockNumber,
             'side_data': oIntervals}
               where oIntervals =
                     {Interval([x, y], name={'b': bval, 'e', eval})}
            '''
            bounds = []
            for region in side['side_data']:

                bound = Bound()
                bound.name = 'sides bound'
                bound.side = side['side']
                bound.blockNumber = side['blockNumber']
                bound.boundNumber = region.name['b']
                bound.equationNumber = region.name['e']
                bound.region = region

                if bound.boundNumber is not None:
                    make_bounds_for_region(bound)
                else:
                    make_bounds_for_default(bound)
                bounds.append(bound)
            return(bounds)

        def make_bounds_for_region(bound):
            '''
            DESCRIPTION:
            Make
            bound.funcName,
            bound.values,
            bound.equation (for parser)
            bound.boundName for comment.

            Bound must contain:
            blockNumber,
            side,
            boundNumber,
            equationNumber.
            '''
            bNumber = bound.boundNumber

            # FOR make funcName from template
            funcName = tFuncName.substitute(blockNumber=bound.blockNumber,
                                            btype=get_btype_name(bNumber),
                                            side=bound.side,
                                            boundNumber=bNumber,
                                            equationNumber=bound.equationNumber)
            bound.funcName = funcName
            # END FOR

            # FOR equation

            equation = model.equations[bound.equationNumber]
            bound.equation = equation
            # END FOR

            # FOR make outputValues

            btype = model.bounds[bNumber].btype
            bound.btype = btype
            
            if btype == 0:
                # for Dirichlet bound
                outputValues = list(model.bounds[bNumber].derivative)
            else:
                # for Neumann bound
                outputValues = list(model.bounds[bNumber].values)

                # special for Neumann bound
                if bound.side == 0 or bound.side == 2:
                    for idx, value in enumerate(outputValues):
                        outputValues.pop(idx)
                        outputValues.insert(idx, '-(' + value + ')')

            bound.values = outputValues
            # END FOR

            # for comment
            bound.boundName = determineNameOfBoundary(bound.side)

            return(bound)

        def make_bounds_for_default(bound):
            '''
            DESCRIPTION:
            Make
            bound.funcName,
            bound.values,
            bound.equation (for parser)
            bound.boundName for comment.

            Bound must contain:
            blockNumber,
            side,
            boundNumber,
            equationNumber.
            '''
            
            # FOR make funcName for defaults
            funcName = tFuncNameDefault.substitute(blockNumber=bound.blockNumber,
                                                   side=bound.side,
                                                   equationNumber=bound.equationNumber)
            bound.funcName = funcName
            # END FOR

            bound.btype = 0

            # for equation
            bound.equation = model.equations[bound.equationNumber]
            
            # for values
            # bound.values = len(bound.equation.system) * ['0.0']
            block = model.blocks[bound.blockNumber]
            try:
                bound.values = list(model.bounds[block.defaultBound].values)
            except:
                raise BaseException(".json file has no DefaultBound key")
            # for comment
            bound.boundName = determineNameOfBoundary(bound.side)
            
            return(bound)

        def make_vertex(vertex, bounds):
            '''
            DESCRIPTION:
            Create funcName, outputValues and equation (for parser)
            boundName for comment.
            vertex is out of transform_vertex
            vertex =
            {'sides': [2, 1],
             'blockNumber': block.blockNumber,
             'vertex_data': vertex_data,
             'side_left': side_left,
             'side_right': side_right}
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
            # find bound for left side:
            bound_side = [bound for bound in bounds
                          if bound.side == vertex.side_left.side_num[0]
                          and bound.blockNumber == vertex.block.blockNumber
                          and bound.region == vertex.region][0]
            # END FOR

            bound = Bound()
            bound.name = 'vertex bound'
            bound.sides = [vertex.side_left.side_num,
                           vertex.side_right.side_num]
            bound.blockNumber = vertex.block.blockNumber

            # data of left side (with index 0)
            bound.boundNumber = vertex.boundNumber
            bound.equationNumber = vertex.equationNumber

            bound.bound_side = bound_side

            # FOR make funcName for defaults
            funcName = tFuncNameVertex.substitute(blockNumber=bound.blockNumber,
                                                  side_0=bound.sides[0],
                                                  side_1=bound.sides[1],
                                                  equationNumber=bound.equationNumber)
            bound.funcName = funcName
            # END FOR

            # FOR PARSER
            bound.btype = bound_side.btype
            bound.equation = bound_side.equation
            bound.values = bound_side.values
            # END FOR
            
            return(bound)

        def check_interconnect_exist(self, side, blockNumber):
            '''
            DESCRIPTION:
            Check if interconnect for this side exist in ics.
            
            '''
            
            if 'ics' in self.__dict__.keys():
                icSides = [ic.side for ic in self.ics
                           if ic.blockNumber == blockNumber]
                if side in icSides:
                    # if exist then no boundary needed
                    #logger.debug('icSides = %s' % str(icSides))
                    #logger.debug('blockNumber = %s' % str(blockNumber))
                    #logger.debug('side = %s' % str(side))
                    return(True)
                else:
                    return(False)

        # END FOR

        # main code:
        # make long necessary obvious thing:
        for blockNumber, block in enumerate(model.blocks):
            block.blockNumber = blockNumber

        # transform sides to regions like list
        new_sides = [side.split_side()
                     for block in model.blocks
                     for side in block.sides]
        #             if not check_interconnect_exist(self, side,
        #                                             block.blockNumber)]

        '''
        new_sides = [transform_side(side, block)
                     for block in model.blocks
                     for side in [2, 3, 0, 1]]
        
        #             if not check_interconnect_exist(self, side,
        #                                             block.blockNumber)]
        '''
        '''
        for blockNumber, block in enumerate(model.blocks):

            sides = [2, 3, 0, 1]

            for side in sides:

                # check if interconnect for this side exist
                if check_interconnect_exist(self, side,  blockNumber):
                    # if exist then no boundary needed
                    continue

                # FOR region bounds
                
                new_side = transform_side(side, block)
                new_sides.append(new_side)
        '''

        self.new_sides = new_sides
        
        # make bounds for side
        self.bounds.extend([bound for side in new_sides
                            for bound in make_bounds(side)
                            if bound not in self.bounds])
        '''
        # transform vertex:
        new_vertexs = [transform_vertex(vertex, new_sides, block)
                       for block in model.blocks
                       for vertex in [[0, 2], [2, 1], [1, 3], [3, 0]]]
        
        # main code:
        for blockNumber, block in enumerate(model.blocks):

            vertexs = [[0, 2], [2, 1], [1, 3], [3, 0]]

            for vertex in vertexs:

                # FOR region bounds
                
                new_vertex = transform_vertex(vertex, new_sides, block)
                self.new_vertexs.append(new_vertex)
        
        self.new_vertexs = new_vertexs
        '''

        # make bounds for vertex
        self.bounds_vertex = [make_vertex(vertex, self.bounds)
                              for vertex in self.new_vertexs]
        # END FOR FILL
        
        # FOR FuncArray
        funcNamesStack = [bound.funcName for bound in self.bounds]
        funcNamesStack.extend([bound.funcName for bound in self.bounds_vertex])

        # check if funcNamesStack alredy exist:
        if 'funcNamesStack' in self.__dict__:
            '''
            for funcName in funcNamesStack:
                if funcName not in self.funcNamesStack:
                    self.funcNamesStack.append(funcName)
            '''
            self.funcNamesStack.extend(funcNamesStack)
        else:
            self.funcNamesStack = funcNamesStack
        # END FOR
