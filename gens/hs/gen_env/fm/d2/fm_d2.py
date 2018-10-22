from spaces.some_space.someFuncs import getRangesInClosedInterval


class GenFmD2():

    '''Extract ``functionMaps`` for edges and vertexs
    of bounds or ic intervals. For 2d.'''
    
    def gen_fm_for_vertexs(self, vertexs, functionMaps,
                           namesAndNumbers):

        '''Use only after ``set_params_for_bounds``'''

        for vertex in vertexs:
            # for compatibility with old version of saveDomain
            sides_nums = vertex.sides_nums
            if sides_nums in [[2, 1], [3, 0]]:
                vertexName = 'v%d%d' % (sides_nums[1], sides_nums[0])
            else:
                vertexName = 'v%d%d' % (sides_nums[0], sides_nums[1])

            eq_num = (namesAndNumbers[vertex.blockNumber]
                      .index(vertex.funcName))
            (functionMaps[vertex.blockNumber]
             .update({vertexName: eq_num}))

    def gen_fm_for_edges(self, intervals, model,
                         functionMaps, namesAndNumbers):

        '''Use only after ``set_params_for_bounds``
        or ``set_params_for_interconnects``
        or both. They create 'fm' key with needed
        data in interval.name dict.'''

        for interval in intervals:
            # if interval has no fm data generated:
            try:
                fm_params = interval.name['fm']
            except KeyError:
                continue

            sideName = "side"+str(fm_params.side_num)

            #print("sideName")
            #print(sideName)

            #print("fm_params.funcName")
            #print(fm_params.funcName)

            # count of interconnects for each block
            idx = (namesAndNumbers[fm_params.blockNumber]
                   .index(fm_params.funcName))

            #print("idx")
            #print(idx)

            if model.dimension == 1:
                value_to_update = idx

            elif model.dimension == 2:

                value_to_update = self.get_idx(model, interval,
                                               fm_params,
                                               namesAndNumbers)

            #print("value_to_update")
            #print(value_to_update)

            blockNumber = fm_params.blockNumber

            # update functionMaps:
            if sideName not in functionMaps[blockNumber].keys():
                functionMaps[blockNumber].update({sideName:
                                                  [value_to_update]})
            else:
                (functionMaps[blockNumber][sideName]
                 .append(value_to_update))

    def get_idx(self, model, interval, fm_params, namesAndNumbers):
        '''
        DESCRIPTION:

        Get idx for interval from side, defined with
        ``fm_params.side_num``.
        
        Inputs:

        - ``interval`` -- interval for which ranges will
        be generated.

        - ``fm_params`` -- contain funcName, blockNumber,
        side_num.
        
        - ``namesAndNumbers`` -- used to find func index
        from it's name.


        RETURN:

        [equation number, xfrom, xto, yfrom, yto]
        '''
        eq_num = (namesAndNumbers[fm_params.blockNumber]
                  .index(fm_params.funcName))

        block = model.blocks[fm_params.blockNumber]

        ranges = self.get_ragnes(model, block,
                                 fm_params.side_num,
                                 interval)
        idx = [eq_num] + ranges
        return(idx)

    def get_ragnes(self, model, block, side_num, interval):

        '''Create ranges from interval
        (with use of ``model.grid data``)::

           [1.5, 2.0] -> [150, 201] for gridStep=0.01
        '''

        if side_num == 0:
            xfrom = 0
            xto = 0
            yfrom = interval[0]
            yto = interval[1]

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because xfrom == xto == 0
            # and Im(xfrom) == 0 and Im(xto) == 1
            # make Im(xto) = 0 (==Im(xfrom))
            # ranges[1] = ranges[0]

        elif(side_num == 1):
            xfrom = block.size.sizeX
            xto = block.size.sizeX
            yfrom = interval[0]
            yto = interval[1]

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because xfrom == xto == sizeX
            # and Im(xfrom) == Im(sizeX) and Im(xto) == Im(sizeX)+1
            # make Im(xfrom) = Im(sizeX)+1 (==Im(xto))
            # ranges[0] = ranges[1]

        elif(side_num == 2):
            xfrom = interval[0]
            xto = interval[1]
            yfrom = 0
            yto = 0

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because yfrom == yto == 0
            # and Im(yfrom) == 0 and Im(yto) == 1
            # make Im(yto) = 0 (==Im(yfrom))
            # ranges[3] = ranges[2]

        elif(side_num == 3):
            xfrom = interval[0]
            xto = interval[1]
            yfrom = block.size.sizeY
            yto = block.size.sizeY

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because yfrom == yto == sizeY
            # and Im(yfrom) == Im(sizeY) and Im(yto) == Im(sizeY)+1
            # make Im(yfrom) = Im(sizeY)+1 (==Im(yto))
            # ranges[2] = ranges[3]

        return(ranges)

