from gens.hs.env.bounds.bounds_main import GenD2
from envs.hs.model.model_main import ModelNet as Model


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

    return(model)


if __name__ == '__main__':
    test_gen_2d()
