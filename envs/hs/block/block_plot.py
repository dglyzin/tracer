import matplotlib.pyplot as plt
import matplotlib.patches as pchs
from pandas import DataFrame


class BlockPlotter():

    def __init__(self, net):
        self.net = net
        self.set_default()

    def set_default(self):
        self.scale = 10

        self.color_block = 0.3
        self.color_regions = 0.3
        self.color_sides = 0.3

        self.side_border = 3.0

    def plot(self, show_vertexs=True):
        dim = self.net.size.dimension
        if dim == 1:
            return(self._plot_1d())
        elif dim == 2:
            return(self._plot_2d(show_vertexs))

    def _plot_1d(self):
        # range:
        side = list(self.net.sides.values())[0]
        rs = [0]
        rs.extend([list(i) for i in side.interval])
        rs.append('sizeX')

        # bound/eq:
        l_vertex = self.net.vertexs['[0]']
        r_vertex = self.net.vertexs['[1]']
        ns = [(l_vertex.boundNumber, l_vertex.equationNumber)]
        ns.extend([(i.name['b'], i.name['e'])
                   for i in side.interval])
        ns.append((r_vertex.boundNumber, r_vertex.equationNumber))

        columns = [i for i in range(len(rs))]
        columns[0] = 'left vertex'
        columns[-1] = 'right vertex'
        out = DataFrame([ns, rs], index=['bound/eq', 'range'],
                        columns=columns)
        return(out)

    def _plot_2d(self, show_vertexs=True):

        block = self.net
        scale = self.scale
        side_border = self.side_border

        # window frame:
        xlim = [-2*side_border, block.size.sizeX*scale+2*side_border]
        ylim = [-block.size.sizeY*scale-4.5*side_border, 0+side_border]

        plt_1, ax = self._plot_2d_init(plt, xlim, ylim)
        plt_1, ax = self._plot_2d_block(plt_1, ax, self.scale)
        plt_1, ax = self._plot_2d_regions(plt_1, ax)
        plt_1, ax = self._plot_2d_sides(plt_1, ax)
        if show_vertexs:
            plt_1, ax = self._plot_2d_vertexs(plt_1, ax)

        plt_1.annotate('$ \omega= \leq = \{(x,y)|x\leq y\}$',
                       xy=(4, 7))
        
        return(plt_1)

    def _plot_2d_init(self, plt, xlim, ylim):
        
        '''Init plot and set window frame'''

        # init plot
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        # set window frame:
        plt.xlim(*xlim)
        plt.ylim(*ylim)

        return(plt, ax)

    def _plot_2d_block(self, plt, ax, scale, orign=[], color=None):

        # draw block
        block = self.net
        if color is None:
            color = self.color_block

        width_x = block.size.sizeX * scale
        height_y = block.size.sizeY * scale

        if len(orign) == 0:
            orign_x = 0
            orign_y = -height_y
        else:
            orign_x = orign[0]
            orign_y = orign[1]
        color = 1.0 if color > 1 else color
        r = pchs.Rectangle((orign_x, orign_y), width=width_x, height=height_y,
                           color=[color, 0.1, 0.1], alpha=0.7)  # 'green'
        ax.add_patch(r)
        
        return(plt, ax)

    def _plot_2d_regions(self, plt, ax):

        scale = self.scale
        block = self.net
        color = self.color_regions

        # FOR draw equation regions
        for eRegion in block.equationRegions:

            width_x = eRegion.xto-eRegion.xfrom
            width_x = width_x * scale

            height_y = eRegion.yto-eRegion.yfrom
            height_y = height_y * scale

            orign_x = eRegion.xfrom
            orign_x = orign_x * scale

            orign_y = -eRegion.yfrom * scale - height_y

            equation_text = 'e %s' % str(eRegion.equationNumber)
            # equation_text = model.equations[eRegion.equationNumber].system

            color = 1.0 if color > 1 else color

            # add rectangle at scen
            ax.add_patch(
                pchs.Rectangle((orign_x, orign_y),
                               width=width_x, height=height_y,
                               color=[0.1, 0.1, color], alpha=0.4))

            # add equation text
            plt.annotate(equation_text,
                         xy=(orign_x + width_x/2.0,
                             orign_y + height_y/2.0))
            if color < 1:
                color += 0.1
        # END FOR
        return(plt, ax)

    def _plot_2d_sides(self, plt, ax):

        scale = self.scale
        block = self.net
        color = self.color_sides
        side_border = self.side_border
        
        # FOR draw sides
        for side_num in block.sides:
            side = block.sides[side_num]
            for interval in side.interval:
                # default text
                equation_text = str(interval.name)

                if side.side_num == 0:

                    width_x = side_border

                    height_y = interval[1] - interval[0]
                    height_y = height_y * scale

                    orign_x = -side_border

                    orign_y = -interval[0] * scale - height_y

                if side.side_num == 1:

                    width_x = side_border
                    height_y = interval[1] - interval[0]
                    height_y = height_y * scale
                    orign_x = block.size.sizeX * scale
                    orign_y = -interval[0] * scale - height_y

                if side.side_num == 2:

                    width_x = interval[1] - interval[0]
                    width_x = width_x * scale
                    height_y = side_border
                    orign_x = interval[0] * scale
                    orign_y = 0

                    equation_text = 'b: %s \n' % str(interval.name['b'])
                    equation_text += 'e: %s' % str(interval.name['e'])

                if side.side_num == 3:

                    width_x = interval[1] - interval[0]
                    width_x = width_x * scale
                    height_y = side_border
                    orign_x = interval[0] * scale
                    orign_y = -block.size.sizeY * scale - side_border

                    equation_text = 'b: %s \n' % str(interval.name['b'])
                    equation_text += 'e: %s' % str(interval.name['e'])

                if color < 1.0:
                    color += 0.05
                color = 1.0 if color > 1 else color
                # add rectangle at scen
                ax.add_patch(
                    pchs.Rectangle((orign_x, orign_y),
                                   width=width_x, height=height_y,
                                   color=[0.1, color, 0.1], alpha=0.4))
                # add equation text
                plt.annotate(equation_text,
                             xy=(orign_x + width_x/2.0,
                                 orign_y + height_y/2.0))
        # END FOR
        
        return(plt, ax)

    def _plot_2d_vertexs(self, plt, ax):

        scale = self.scale
        side_border = self.side_border
        block = self.net

        # FOR draw vertex
        # vertex_border = 1.0
        sizeX = block.size.sizeX
        sizeY = block.size.sizeY
        for vertex in self.net.vertexs.values():

            if vertex.sides_nums == [0, 2]:
                orign_x = -side_border
                orign_y = side_border
            elif(vertex.sides_nums == [2, 1]):
                orign_x = sizeX * scale + side_border/2.0
                orign_y = side_border
            elif(vertex.sides_nums == [1, 3]):
                orign_x = sizeX * scale + side_border
                orign_y = -sizeY * scale - 3.7*side_border

            elif(vertex.sides_nums == [3, 0]):
                orign_x = - side_border
                orign_y = -sizeY * scale - 3.7*side_border

            equation_text = 'v: %s \n' % str(vertex.sides_nums)
            equation_text += 'b: %s \n' % str(vertex.boundNumber)
            equation_text += 'e: %s' % str(vertex.equationNumber)

            # add equation text
            plt.annotate(equation_text,
                         xy=(orign_x,
                             orign_y))
        # END FOR
        return(plt, ax)
