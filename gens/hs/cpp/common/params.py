from gens.hs.cpp.common.base import GenBase


class Gen(GenBase):

    def get_out_for_parameters(self):
        template = self.env.get_template('params.template')
        params = self

        args = {
            'params': params.parameters,
            'paramValues': params.parametersVal,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def set_params_for_parameters(self, model):
        '''
        DESCRIPTION:
        Fill parameters for .cpp.
        for cppOutsForGenerators.get_out_for_parameters

        USED PARAMETERS:
        model.params
        model.paramValues
        '''
        self.parameters = model.params
        self.parametersVal = model.paramValues[model.defaultParamsIndex]
