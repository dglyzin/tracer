'''Convert operator tree to out

Function lex_replacer must be given by user
it transform Word's object to what it shuld be.
If no given, it transform itro original lexems.
This because of type is Word for each node.name in op_tree,
so it contain lex atribute:
   Word.lex = [lexem, re.math object]
function lambda x:x[1] return original sent.

'''

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


def map_tree(tree, node_replacer):

    '''Use node_raplacer for each node to add cpp
    output'''

    if len(tree.children) == 0:
        # finish:
        node_replacer(tree)
        
    elif tree.name != 'br':
        # main:

        map_tree(tree.children[1], node_replacer)
        node_replacer(tree)
        map_tree(tree.children[0], node_replacer)

    elif(tree.name == 'br'):
        # if brackets:
    
        # work with brackets itself:
        node_replacer(tree)

        # work with brackets args:
        for _id, arg in enumerate(tree.children[1].children):
            map_tree(arg, node_replacer)
    return(tree)
    

def map_tree_postproc(mapped_tree, node_replacer):
    node_replacer.postproc(mapped_tree)
    return(mapped_tree)
