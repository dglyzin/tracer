from hybriddomain.spaces.math_space.pde.regions import BoundRegion, EquationRegion
from hybriddomain.envs.hs.block.side.side_main import SideNet as Side
from hybriddomain.envs.hs.block.block_size import BlockSize
from hybriddomain.envs.hs.block.block_main import BlockNet as Block


def test_block_1d():
    # m = model.Model()
    # m.io.loadFromFile('tests/test1d_two_blocks0.json')
    # m.blocks[0].sides
    # m.blocks[1].sides
    # m.interconnects

    e0 = EquationRegion(dim=1, EquationNumber=1,
                        xfrom=0.1, xto=0.2)

    e1 = EquationRegion(dim=1, EquationNumber=2,
                        xfrom=0.2, xto=0.3)
    s = Side(2, eRegions=[e0], dim=1)
    
    size = BlockSize()
    size.set_default(dimension=1)
        
    b = Block(name="Block 1", size=size, sides=[s],
              eRegions=[e1])
    return(b)
    # m.editor.add_block(b)
    # ic = test_ic()
    # m.editor.add_ic(ic)


def test_block_2d():
    b00 = BoundRegion(BoundNumber=0, Side=0, dim=2,
                      xfrom=0, xto=0.5, yfrom=0, yto=0.5)
    b01 = BoundRegion(BoundNumber=1, Side=0, dim=2,
                      xfrom=0.5, xto=1, yfrom=0, yto=0.5)
    s0 = Side(0, bRegions=[b00, b01])
    # print("side 0:")
    # print(s0)

    b10 = BoundRegion(BoundNumber=0, dim=2, Side=1,
                      xfrom=0, xto=0.5, yfrom=0, yto=0.5)
    b11 = BoundRegion(BoundNumber=1, dim=2, Side=1,
                      xfrom=0.5, xto=1, yfrom=0, yto=0.5)
    s1 = Side(1, bRegions=[b10, b11])
    # print("side 1:")
    # print(s1)

    b20 = BoundRegion(BoundNumber=0, dim=2, Side=2,
                      xfrom=0, xto=0.5, yfrom=0, yto=0.5)
    b21 = BoundRegion(BoundNumber=1, dim=2, Side=2,
                      xfrom=0.5, xto=1, yfrom=0, yto=0.5)
    s2 = Side(2, bRegions=[b20, b21])
    # print("side 2:")
    # print(s2)

    b30 = BoundRegion(BoundNumber=0, dim=2, Side=3,
                      xfrom=0, xto=0.5, yfrom=0, yto=0.5)
    b31 = BoundRegion(BoundNumber=1, dim=2, Side=3,
                      xfrom=0.5, xto=1, yfrom=0, yto=0.5)
    s3 = Side(3, bRegions=[b30, b31])
    # print("side 3:")
    # print(s3)

    e0 = EquationRegion(dim=2, EquationNumber=1,
                        xfrom=0.1, xto=0.2,
                        yfrom=0.1, yto=0.2)
    size = BlockSize()
    size.set_default(dimension=2)
        
    b = Block(name="Block 1", size=size, sides=[s0, s1, s2, s3],
              eRegions=[e0])
    return(b)


def test_side():

    '''Use:
    >>> block.editor.add_or_edit_side(side)
    to add side to block.'''

    b00 = BoundRegion(Side=2, BoundNumber=0, dim=2,
                      xfrom=0, xto=0.3, yfrom=0, yto=0.5)
    b01 = BoundRegion(Side=2, BoundNumber=1, dim=2,
                      xfrom=0.3, xto=0.7, yfrom=0, yto=0.5)
    s0 = Side(2, bRegions=[b00, b01])
    
    return(s0)


def test_bound():
    b00 = BoundRegion(Side=0, BoundNumber=0, dim=2,
                      xfrom=0, xto=0, yfrom=0.3, yto=0.7)
    return(b00)

    
