from translator.replacer.replacer import Gen
from translator.tree.nodes import NodeCommon
from env.equation.data.terms.args._list_nodes_editor import terms_for_args

import logging

# create logger
log_level = logging.INFO  # logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger('extractor.py')
logger.setLevel(level=log_level)


class ArgsGen(Gen):
    
    def __init__(self):
        self.args = []

    def translate_brackets(self, node_br):
 
        left_node = node_br[0]
        right_node = node_br[-1]
        
        self.translate(left_node)
        self.translate(right_node)

    def translate(self, node):

        self.separate_arg(node)

        try:
            node.args
        except AttributeError:
            logger.debug("no args for node:")
            logger.debug(self.get_term_value(node))
            self.get_args(node)

        args_exist = [arg for arg in self.args
                      if node.args['id'] == arg['id']]
        if len(args_exist) > 0:
            arg_exist = args_exist[0]
            arg_exist['nodes'].append(node)
        else:
            self.args.append({'id': node.args['id'], 'nodes': [node]})
    
    def separate_arg(self, node):

        '''Separate node from its arg:
        Ex: node: a.t() -> node: .t(), child a'''

        term_id = self.get_term_id(node)

        if term_id in terms_for_args and len(node) == 0:
            arg = terms_for_args[term_id]
            arg_node = NodeCommon(arg['child_name'](node),
                                  arg['child_term_id'])
            node.add_child(arg_node)
            
            # fix value:
            terms_for_args[term_id]['editor'](self, node)

    def postproc(self, node):
        pass
    
