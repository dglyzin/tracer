# python3 -m gens.hs.gen_env.cpp.env.bounds.tests_bounds
from gens.hs.gen_env.cpp.env.bounds.bounds_main import GenD2
from envs.hs.model.model_main import ModelNet as Model
from gens.hs.gen_env.cpp.env.array.array_main import Gen as GenArr
from gens.hs.gen_env.fm.d2.fm_d2 import GenFmD2


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

    # for edges:
    params_intervals = [interval for block in model.blocks
                        for side_num in block.sides
                        for interval in block.sides[side_num].intervals
                        if 'fm' in interval.name.keys()]
    print("\nparams_intervals:\n")
    
    for side_num in model.blocks[1].sides:
        for interval in model.blocks[1].sides[side_num].intervals:
            if 'fm' in interval.name.keys():
                print("side_num: %s" % (str(side_num)))
                print("interval: %s" % (str(interval)))

    fm_gen.gen_fm_for_edges(params_intervals, model,
                            functionMaps, namesAndNumbers)

    print("\nvertexs:\n")
    for vertex in gen.params.bounds_vertex:

        print("blockNumber: %s" % str(vertex.blockNumber))
        print("sides: %s" % str(vertex.sides_nums))
        print("bound_side.interval: %s"
              % str(vertex.bound_side.interval))
        print("bound_side.side_num: %s"
              % str(vertex.bound_side.side_num))
        
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
