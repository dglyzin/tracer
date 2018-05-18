import envs.hs.model.model_main as model
from envs.hs.interconnect.ic_main import icMain as interconnect


def test_ic():
    m = model.ModelNet()
    m.io.loadFromFile('tests/test2d_two_blocks0.json')
    # m.interconnects[0].plotter.plot().show()

    ic = interconnect("1", model=m,
                      blockNumber1=0, blockNumber2=1,
                      block1Side=0, block2Side=1)
    ic.plotter.plot().show()
