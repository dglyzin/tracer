import envs.hs.model.model_main as model
from envs.hs.interconnect.ic_main import icMain as interconnect


def test_ic():
    m = model.ModelNet()
    m.io.loadFromFile('problems/2dTests/tests_2d_two_blocks0')
    # m.interconnects[0].plotter.plot().show()
    # ic.set_model if model is not exist yet
    ic = interconnect("1", model=m,
                      blockNumber1=0, blockNumber2=1,
                      block1Side=0, block2Side=1)
    ic.plotter.plot().show()


if __name__ == '__main__':
    
    test_ic()
