from env.equation.data.terms.output.cpp.patterns.diff import Diff
from env.equation.data.terms.output.cpp.patterns.bdp import Bdp
from env.equation.data.terms.output.cpp.patterns.var import Var
from env.equation.data.terms.output.cpp.patterns.free_var import FreeVar
from env.equation.data.terms.output.cpp.patterns.diff_time_var import DiffTimeVar
from env.equation.data.terms.output.cpp.patterns.coeffs import Coeffs
from env.equation.data.terms.output.cpp.patterns.float import Float
from env.equation.data.terms.output.cpp.patterns.default import Default
from env.equation.data.terms.output.cpp.patterns.brackets.brackets_main import BracketsNet as BrTermsGens
from copy import deepcopy

# from translator.replacer.cpp.cpp_out import delay_postproc
from translator.replacer.replacer import Gen


import logging


# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
# logger = logging.getLogger('replacer_cpp')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('replacer_cpp')
logger.setLevel(level=log_level)


terms_gens_cls = [Diff, Bdp, Var, FreeVar, DiffTimeVar,
                  Coeffs, Float, Default]


class Out():
    pass


class CppGen(Gen):

    '''Node translator implementation for cpp'''

    def __init__(self):

        '''Set terms_gens and terms_br_gens dict
        of terms generator for generate term's output
        for node.
        Also extract some global data from all nodes in
        tree.
        '''
        Gen.__init__(self)

        # some global data to extract from all
        # nodes in tree:
        self.global_params.delays_owner_id = 0
        self.global_params.delays = {}
        
    def get_terms_gen_cls(self):
        return(terms_gens_cls)

    def get_terms_br_gen_cls(self):
        return(BrTermsGens)

    def postproc(self, node):
        ###delay_postproc(node)
        pass

    def init_output(self, nodes):

        '''For add out to nodes'''

        for node in nodes:
            try:
                node.output
            except AttributeError:
                node.output = Out()
            node.output.cpp = Out()
            node.output.cpp.global_data = {}

    def set_output_out(self, node, value):
        
        node.output.cpp.out = value

    def set_output_data(self, node, key, value):
        node.output.cpp.global_data[key] = value

    def get_params_field_name(self):
        return('term_print_cpp_params')

    # TODO: to preproc
    # FOR set preproc data
    def set_terms_data(self, **kwargs):
        for gen_id in self.terms_gens:
            self.terms_gens[gen_id].set_term_data(**kwargs)

    def set_dim(self, **kwargs):
        self.terms_gens['bdp'].set_dim(**kwargs)

    def set_shape(self, **kwargs):
        self.terms_gens['bdp'].set_shape(**kwargs)

    def set_blockNumber(self, **kwargs):
        self.terms_gens['diff'].set_blockNumber(**kwargs)
        self.terms_gens['bdp'].set_blockNumber(**kwargs)

    def set_diff_type(self, **kwargs):
        self.terms_gens['diff'].set_diff_type(**kwargs)

    def set_vars_indexes(self, **kwargs):
        # int: shift index for variable like
        # like (U,V)-> (source[+0], source[+1])
        self.terms_gens['diff'].set_vars_indexes(**kwargs)
        self.terms_gens['var'].set_vars_indexes(**kwargs)
        self.terms_gens['bdp'].set_vars_indexes(**kwargs)
        self.terms_gens['diff_time'].set_vars_indexes(**kwargs)

    def set_coeffs_indexes(self, **kwargs):
        # map  coeffs ot it's index
        # like (a,b)-> (params[+0], params[+1])
        self.terms_gens['coeffs'].set_coeffs_indexes(**kwargs)
    # END FOR

