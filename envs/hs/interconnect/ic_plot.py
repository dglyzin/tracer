import matplotlib.pyplot as plt
import matplotlib.patches as pchs


class icPlotter():

    def __init__(self, net):
        self.net = net
        
        self.scale = 10

    def plot(self):
        model = self.net.model
        dim = model.dimension
        if dim == 1:
            return(self._plot_1d(model))
        elif dim == 2:
            return(self._plot_2d(model))

    def _plot_1d(self, model):
        plt_1 = model.blocks[self.net.block1].plotter.plot()
        plt_2 = model.blocks[self.net.block2].plotter.plot()
        if self.net.block1Side <= self.net.block2Side:
            return([plt_1, plt_2])
        else:
            return([plt_2, plt_1])
    
    def _plot_2d(self, model):
        
        '''offsetX1 and offsetX2 must be either both 0,
        or some > 0  but not both > 0. Same for Y.'''
        
        # init plot
        scale = self.scale

        # draw block
        block_1 = model.blocks[self.net.block1]
        block_2 = model.blocks[self.net.block2]

        width_x_1 = block_1.size.sizeX * scale
        height_y_1 = block_1.size.sizeY * scale
        print("b1: %s" % (str([width_x_1, height_y_1])))

        width_x_2 = block_2.size.sizeX * scale
        height_y_2 = block_2.size.sizeY * scale
        print("b2: %s" % (str([width_x_2, height_y_2])))

        # scene rectangle:
        width_x_s = 2*max(width_x_1, width_x_2)
        height_y_s = 2*max(height_y_1, height_y_2)
        print("s: %s" % (str([width_x_s, height_y_s])))

        # size of window
        xlim = [-width_x_s, width_x_s]
        ylim = [-height_y_s, height_y_s]

        plt_1, ax = block_1.plotter._plot_2d_init(plt, xlim, ylim)
        '''
        # add rectangle at scen
        ax.add_patch(
            pchs.Rectangle((0, -height_y_s),
                           width=width_x_s, height=height_y_s,
                           color='green', alpha=0.4))
        # add equation text
        plt_1.annotate("scene",
                       xy=(width_x_s + width_x_s/2.0,
                           -height_y_s + height_y_s/2.0))
        '''
        offsetX1 = block_1.size.offsetX*scale
        offsetY1 = block_1.size.offsetY*scale
        
        offsetX2 = block_2.size.offsetX*scale
        offsetY2 = block_2.size.offsetY*scale

        # either offsetX1!=0 or offsetX2!=0 or some = 0
        # but not both != 0:
        if offsetX1 > 0 and offsetX2 > 0:
            raise(BaseException("impasable cases for offsetX"))

        # either offsetY1!=0 or offsetY2!=0 or some = 0
        # but not both != 0:
        if offsetY1 > 0 and offsetY2 > 0:
            raise(BaseException("impasable cases for offsetY"))

        # main block is always that which in 0
        if self.net.block1Side == 0 and self.net.block2Side == 1:
            print("case 0: block1Side 0, block2Side 1")
            
            # main in center:
            orign_1 = [0, 0]  # -height_y_1

            # other:
            common_orign_y = -height_y_2+height_y_1
            orign_2 = [-width_x_2, common_orign_y+offsetY2-offsetY1]

        elif self.net.block1Side == 1 and self.net.block2Side == 0:
            print("case 1: block1Side 1, block2Side 0")

            # main in center:
            orign_2 = [0, 0]
            
            # other:
            common_orign_y = -height_y_1+height_y_2
            orign_1 = [-width_x_1, common_orign_y+offsetY1-offsetY2]

        elif self.net.block1Side == 2 and self.net.block2Side == 3:
            print("case 2: block1Side 2, block2Side 3")
            print("offset relative block 1")

            # main in center:
            orign_1 = [0, -height_y_1]

            # other:
            orign_2 = [offsetX1-offsetX2, 0]

        elif self.net.block1Side == 3 and self.net.block2Side == 2:
            print("case 3: block1Side 3, block2Side 2")
            print("offset relative to block 2")

            # main in center:
            orign_2 = [0, -height_y_2]
            
            # other:
            orign_1 = [offsetX2-offsetX1, 0]
       
        print("orign_1: %s" % str(orign_1))
        print("orign_2: %s" % str(orign_2))

        plt_1, ax = block_1.plotter._plot_2d_block(plt_1, ax, scale,
                                                   orign=orign_1, color=0.3)
        plt_1.annotate("block_1", xy=orign_1)
        plt_2, ax = block_2.plotter._plot_2d_block(plt_1, ax, scale,
                                                   orign=orign_2, color=0.7)
        plt_2.annotate("block_2", xy=orign_2)

        # add info:
        info = (("block 1\n blockNumber %s\n"
                 + " sizeX %s\n sizeY %s\n"
                 + " offsetX %s\n offsetY %s")
                % (str(block_1.blockNumber),
                   str(width_x_1), str(height_y_1),
                   str(offsetX1), str(offsetY1)))
        info += "\n"
        info += (("block 2\n blockNumber %s\n"
                  + " sizeX %s\n sizeY %s\n"
                  + " offsetX %s\n offsetY %s")
                 % (str(block_2.blockNumber),
                    str(width_x_2), str(height_y_2),
                    str(offsetX2), str(offsetY2)))

        plt_2.annotate(info, xy=(-width_x_s, -height_y_s))

        return(plt_2)
