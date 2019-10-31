from hybriddomain.envs.hs.model.model_main import ModelNet as Model
from hybriddomain.gens.hs.common.init_funcs_nums import InitFuncsNums


def test_1d(model='problems/test1d_two_blocks0'):

    # model:
    if type(model) == str:
        oModel = Model()
        oModel.io.loadFromFile(model)
        model = oModel
    else:
        model = model

    ifn = InitFuncsNums(model, model.blocks[0])

    return(ifn)


if __name__ == '__main__':
    test_1d()
