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
from replacer_cpp import CppGen


def convert_tree(op_tree, lex_replacer):
    if len(op_tree.children) == 0:
        # finish:
        X = lex_replacer(op_tree.name)
        return([X])

    elif len(op_tree.children) == 2:
        # main:

        left = convert_tree(op_tree.children[1], lex_replacer)
        X = lex_replacer(op_tree.name)
        right = convert_tree(op_tree.children[0], lex_replacer)

        return(left+[X]+right)

    elif(len(op_tree.children) == 4):
        # if brackets:

        leftb = op_tree.children[-1].name
        left = convert_tree(op_tree.children[1], lex_replacer)
        X = lex_replacer(op_tree.name)
        right = convert_tree(op_tree.children[0], lex_replacer)
        rightb = op_tree.children[-2].name
        leftb, rightb = lex_replacer([leftb, rightb])
        
        return([leftb]+left+[X]+right+[rightb])


def convert(o, lex_replacer):

    if type(o) == list:
        # for case goal_sent = a (like s='U'):
        out = lex_replacer(o[0])
    else:
        # for other:
        out = convert_tree(o, lex_replacer)

    out = lex_replacer.postproc(out)
    # lex_replacer
    return(out)
