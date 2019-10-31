import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.func')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Func():
    
    '''for f (left=f right=))'''
    
    def __init__(self, net):
        self.net = net
        self.gnet = self.net.net

        # this mean left_term.name == 'f'
        # right_node.name == ')'
        self.id = 'l:f|r:)'

    def __call__(self, node_br):
        
        '''Add cpp out to brackets'''

        successors = self.gnet.get_successors(node_br)
        
        left_node = successors[0]
        right_node = successors[-1]

        args_node = successors[1]

        # get node data:
        self.get_node_data(left_node, right_node)
        
        # transform to cpp:
        left_out, right_out = self.print_out()

        self.gnet.set_output_out(left_node, left_out)
        self.gnet.set_output_out(right_node, right_out)

    def get_node_data(self, left_node, right_node):

        '''Used for fill local data'''

        self.func_name = self.gnet.get_term_value(left_node)
        
    def print_out(self):
        
        left = self.func_name
        right = ")"
        return(left, right)
