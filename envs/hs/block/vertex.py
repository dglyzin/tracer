class Vertex():
    def __init__(self, sides_nums, sides, block):
        self.block = block
        self.sides_nums = sides_nums
        dim = self.block.size.dimension
        if dim == 1:
            side = list(sides.values())[0]
            self._set_vertex_1d(side)
        elif dim == 2:
            self._set_vertex_2d(sides)

    def _set_vertex_1d(self, side):
        if self.sides_nums[0] == 0:
            vertex_data = side.interval[0].name
        elif self.sides_nums[0] == 1:
            vertex_data = side.interval[-1].name

        self.boundNumber = vertex_data['b']
        self.equationNumber = vertex_data['e']
        
    def _set_vertex_2d(self, sides):

        '''Add vertex ([0, 2]), side_left/side_right,
        boundNumber and equationNumber (from left side),
        region'''
        
        sides_nums = self.sides_nums

        side_left = [sides[side_num] for side_num in sides
                     if (side_num == sides_nums[0])][0]
        self.side_left = side_left

        side_right = [sides[side_num] for side_num in sides
                      if (side_num == sides_nums[1])][0]
        self.side_right = side_right

        # choice first or last region of side
        # according vertex position in block
        # for find bound side for vertex left side (always)
        # i.e. for [2, 1] use bound side 2 data
        if sides_nums == [0, 2]:
            # vertex in [0, 0]
            vertex_data = [side_left.interval[0].name,
                           side_right.interval[0].name]

            # first region of side 0
            region = side_left.interval[0]
                
        if sides_nums == [2, 1]:
            # vertex in [x_max, 0]
            vertex_data = [side_left.interval[-1].name,
                           side_right.interval[0].name]
            
            # last region of side 2
            region = side_left.interval[-1]

        if sides_nums == [1, 3]:
            # vertex in [x_max, y_max]
            vertex_data = [side_left.interval[-1].name,
                           side_right.interval[-1].name]
            
            # last region of side 1
            region = side_left.interval[-1]

        if sides_nums == [3, 0]:
            # vertex in [0, y_max]
            vertex_data = [side_left.interval[0].name,
                           side_right.interval[-1].name]
            
            # first region of side 3
            region = side_left.interval[0]

        # data of left side (with index 0)
        self.boundNumber = vertex_data[0]['b']
        self.equationNumber = vertex_data[0]['e']
        self.region = region
