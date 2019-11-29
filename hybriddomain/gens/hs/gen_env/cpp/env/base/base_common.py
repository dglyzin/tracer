from hybriddomain.spaces.some_space.someClasses import Params


class GenBaseCommon():

    '''Base for all common objects methods'''

    def set_eq_base_params(self, eSystem, dim, blockNumber, parameters):
        eSystem.cpp.parse()

        # print("eSystem:")
        # print(eSystem)
        # print("eSystem.eq_tree")
        # for eq in eSystem.eqs:
        #     print(eq.eq_tree)

        eSystem.cpp.set_default()
        eSystem.cpp.set_dim(dim=dim)
        eSystem.cpp.set_blockNumber(blockNumber)
        # ['a', 'b'] -> [('a',0), ('b', 1)]
        coeffs_to_indexes = [(param, idx)
                             for idx, param in enumerate(parameters)]
        eSystem.cpp.set_coeffs_indexes(coeffs_to_indexes=coeffs_to_indexes)

    def get_eq_cpp(self, eSystem):
        return([eq.replacer.cpp.make_cpp() for eq in eSystem.eqs])
        # return([eq.flatten('cpp') for eq in eSystem.eqs])

    def fill_func_names_stack(self, funcNamesStack,
                              funcNamesStackLocal):

        '''fill ``self.funcNamesStack`` that will be used
        for ``funcNames`` in cpp templates and for indexes
        in dom file'''

        # check if funcNamesStack alredy exist:
        # if 'funcNamesStack' in self.net.params.__dict__:

        for funcName in funcNamesStackLocal:
            # remove duplicates:
            if funcName not in funcNamesStack:
                funcNamesStack.append(funcName)
        
        self.net.params.funcNamesStack = funcNamesStack

        # self.net.params.funcNamesStack.extend(funcNamesStackLocal)

        # remove duplicates:
        # self.net.params.funcNamesStack = list(set(self.funcNamesStack))

