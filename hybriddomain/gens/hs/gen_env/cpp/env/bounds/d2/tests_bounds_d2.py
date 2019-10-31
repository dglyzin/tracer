from hybriddomain.gens.hs.gen_env.cpp.env.bounds.d2.bounds_2d import GenCommon
from hybriddomain.gens.hs.gen_env.cpp.env.array.array_main import Gen as GenArr
from hybriddomain.gens.hs.gen_env.cpp.env.bounds.d2.bounds_d2_dom import GenDomD2

from hybriddomain.envs.hs.model.model_main import ModelNet as Model


def test_gen_2d(model='problems/2dTests/test2d_for_intervals_single_delay'):
    '''tests_2d_two_blocks0'''
    # model:
    if type(model) == str:
        oModel = Model()
        oModel.io.loadFromFile(model)
        model = oModel
    else:
        model = model

    class Tmp():
        pass
    tmp_net = Tmp()

    gen = GenCommon(tmp_net)

    funcNamesStack = []
    gen.set_params_for_bounds(model, funcNamesStack)
    print("funcNamesStack")
    print(funcNamesStack)

    gen_array = GenArr()
    gen_array.common.set_params_for_array(funcNamesStack)
    namesAndNumbers = gen_array.params.namesAndNumbers
    print("namesAndNumbers:")
    print(namesAndNumbers)
    
    gen_dom = GenDomD2(tmp_net)
    functionMap = {0: {}, 1: {}}
    gen_dom.set_params_for_dom_bounds(model, namesAndNumbers,
                                      functionMap)
    print("functionMap:")
    print(functionMap)
    return(model)


if __name__ == '__main__':
    test_gen_2d()
