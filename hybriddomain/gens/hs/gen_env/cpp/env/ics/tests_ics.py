# python3 -m gens.hs.gen_env.cpp.env.ics.tests_ics
from hybriddomain.gens.hs.gen_env.cpp.env.ics.ics_main import GenD2
from hybriddomain.envs.hs.model.model_main import ModelNet as Model
from hybriddomain.gens.hs.gen_env.cpp.env.array.array_main import Gen as GenArr
from hybriddomain.gens.hs.gen_env.fm.d2.fm_d2 import GenFmD2


def test_ics_gen_2d(model='problems/2dTests/tests_2d_two_blocks0'):
    '''tests_2d_two_blocks0'''
    # model:
    if type(model) == str:
        oModel = Model()
        oModel.io.loadFromFile(model)
        model = oModel
    else:
        model = model

    funcNamesStack = []
    
    gen = GenD2()
    gen.common.set_params_for_interconnects(model, funcNamesStack)
    print("funcNamesStack:")
    print(funcNamesStack)

    out = ''
    out += gen.cpp_render.get_out_for_interconnects()

    print("\nout:")
    print(out)

    gen_array = GenArr()
    gen_array.common.set_params_for_array(funcNamesStack)
    namesAndNumbers = gen_array.params.namesAndNumbers

    print("\nnamesAndNumbers:")
    print(namesAndNumbers)

    functionMaps = {0: {}, 1: {}}
    fm_gen = GenFmD2()

    # for edges:
    params_intervals = [interval for block in model.blocks
                        for side_num in block.sides
                        for interval in block.sides[side_num].intervals
                        if 'fm' in interval.name.keys()]
    fm_gen.gen_fm_for_edges(params_intervals, model,
                            functionMaps, namesAndNumbers)

    '''
    gen.dom.set_params_for_dom_interconnects(model, namesAndNumbers,
                                             functionMaps)
    '''
    print("\nfunctionMaps:")
    print(functionMaps)

    return(model)


if __name__ == '__main__':
    test_ics_gen_2d()
