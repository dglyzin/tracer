import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.pow')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Pow():
    
    '''for pow (left=( right=w)'''
    
    def __init__(self, net):
        self.net = net
        self.gnet = self.net.net
        # this mean rigth_term.name == 'w'
        # left_term.name == '('
        self.id = 'l:(|r:w'

    def __call__(self, node_br):

        '''Add cpp out to brackets'''

        successors = self.gnet.get_successors(node_br)
        
        left_node = successors[0]
        right_node = successors[-1]

        args_node = successors[1]
        
        # get term data:
        self.get_node_data(left_node, right_node)
        
        # transform to cpp:
        left_out, right_out = self.print_out()

        self.gnet.set_output_out(left_node, left_out)
        self.gnet.set_output_out(right_node, right_out)

    def get_node_data(self, left_node, right_node):

        '''Used for fill local data'''

        self.set_pow_degree(right_node)

    def set_pow_degree(self, node):
        # try:
        # if name is a Word
        right = self.gnet.get_term_value(node)
        # except AttributeError:
        #     # if name is a str
        #     right = term.name

        self.degree = right.split('^')[1]
        
    def print_out(self):
        
        degree = str(self.degree)
        left = "pow("
        right = "," + degree + ")"
        return(left, right)
