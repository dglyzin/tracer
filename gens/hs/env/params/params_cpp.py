from gens.hs.env.base.base_common import Params


class GenCpp():
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_parameters(self, model):
        '''
        DESCRIPTION::

        Fill parameters for .cpp.

        for ``cppOutsForGenerators.get_out_for_parameters``

        USED PARAMETERS::

        ``model.params``
        ``model.paramValues``
        '''
        self.net.params.parameters = model.params
        self.net.params.parametersVal = model.paramValues[model.defaultParamsIndex]
