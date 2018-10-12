# python3 -m gens.hs.env.bounds.tests_bounds
from gens.hs.env.bounds.bounds_main import GenD2
from envs.hs.model.model_main import ModelNet as Model
from gens.hs.env.array.array_main import Gen as GenArr
from gens.hs.env.common.d2.fm import GenFmD2


def test_gen_2d(model='problems/2dTests/test2d_for_intervals_single_delay'):
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
    gen.common.set_params_for_bounds(model, funcNamesStack)
    print("funcNamesStack:")
    print(funcNamesStack)

    out = ''
    out += gen.cpp_render.get_out_for_bounds()
    out += gen.cpp_render.get_out_for_bounds(vertex=True)

    print("out:")
    print(out)

    gen_array = GenArr()
    gen_array.common.set_params_for_array(funcNamesStack)
    namesAndNumbers = gen_array.params.namesAndNumbers

    print("\nnamesAndNumbers:")
    print(namesAndNumbers)

    functionMaps = {0: {}, 1: {}}
    fm_gen = GenFmD2()
    fm_gen.gen_fm_for_edges(model, functionMaps, namesAndNumbers)
    fm_gen.gen_fm_for_vertexs(gen.params.bounds_vertex, functionMaps,
                              namesAndNumbers)
    '''
    gen.dom.set_params_for_dom_bounds(model, namesAndNumbers,
                                      functionMaps)
    '''
    print("\nfunctionMaps:")
    print(functionMaps)

    return(model)


if __name__ == '__main__':
    test_gen_2d(model=('problems/2dTests/tests_2d_two_blocks0'))
