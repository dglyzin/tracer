'''Convert operator tree to out

Function lex_replacer must be given by user
it transform Word's object to what it shuld be.
If no given, it transform itro original lexems.
This because of type is Word for each node.name in op_tree,
so it contain lex atribute:
   Word.lex = [lexem, re.math object]
function lambda x:x[1] return original sent.

'''

import logging


# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
# logger = logging.getLogger('replacer_cpp')

# if using directly uncoment that:

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('maps')
logger.setLevel(level=log_level)

'''
def replace(term, lex_replacer):

    ''Replace term with lex_replacer function.
    If term is not of type Word then return term.''

    if type(term) == str:
        # if term is not in lexem:
        X = term
    else:
        # if term is type(Word)
        X = term.replace_lex(lex_replacer)
    return(X)
'''


def map_tree(tree, node_editor):

    '''Use node_raplacer for each node to add cpp
    output'''

    if len(tree.children) == 0:
        # finish:
        node_editor(tree)

        # in case node_editor added new
        # children:
        if len(tree.children) > 0:
            for child_node in tree.children:
                map_tree(child_node, node_editor)

    elif tree.name != 'br':
        # main:

        if len(tree.children) == 2:
            map_tree(tree.children[1], node_editor)
        node_editor(tree)
        map_tree(tree.children[0], node_editor)

    elif(tree.name == 'br'):
        # if brackets:
    
        # work with brackets itself:
        node_editor(tree)

        # work with brackets args:
        for _id, arg in enumerate(tree.children[1].children):
            map_tree(arg, node_editor)
    return(tree)
    

def map_tree_postproc(mapped_tree, node_editor):
    node_editor.postproc(mapped_tree)
    return(mapped_tree)
