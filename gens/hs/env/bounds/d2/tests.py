from gens.hs.env.bounds.d2.bounds_2d import GenCommon
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

    class Tmp():
        pass
    tmp_net = Tmp()

    gen = GenCommon(tmp_net)

    funcNamesStack = []
    gen.set_params_for_bounds(model, funcNamesStack)
    print("funcNamesStack")
    print(funcNamesStack)
    return(model)


if __name__ == '__main__':
    test_gen_2d()
