from env.equation.data.terms.output.cpp.patterns.base import Base
from env.equation.data.terms.output.cpp.patterns.base import Params


class Default(Base):
    
    '''work with mid terms
    (like "eq", "add", "sub")
    '''
    
    def __init__(self, net):
        Base.__init__(self, net)
        self.id = 'default'

    def get_node_data(self, node):

        '''Replace mid term with its value
        from ``self.net.mid_replacers`` if term is mid.
        ``replacer.set_mid_replacers`` method must be used first.
        (ex mid_replacers: {"eq": "="})'''
        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''

        # params = Params()

        # FOR mid_replacers:
        mid_replacers = self.net.mid_replacers
        node_mid_name = self.net.get_node_type(node)
        if node_mid_name in mid_replacers:
            value = mid_replacers[node_mid_name]
        else:
            value = self.net.get_term_value(node)
        # END FOR

        self.params['value'] = value
        # self.params['value'] = node.name.lex[0]
        
        # params['value'] = value
        # self.net.set_output_data(node, self.net.get_params_field_name(),
        #                          params)
        
    def print_out(self):
    
        '''For generate node out'''
        self.params.has_param('value', 'Default')
        return(self.params['value'])
