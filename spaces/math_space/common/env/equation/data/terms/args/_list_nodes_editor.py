'''For extracting arg in separate node for some nodes:
Ex: node: a.t() -> node: .t(), child a'''


def dot_editor(self, node):

    '''remove arg from node (a.t -> .t)
    for output generator'''

    val = node.name.lex[0]
    obj = node.name.lex[1].group('obj')
    node.name.lex[0] = val.replace(obj, "")


def idx_editor(self, node):

    '''remove arg from node (a[1, 2, ] -> .[1,2, ])
    for output generator'''

    pass


terms_for_args = {'dot':
                  {'child_name': lambda node: node.name.lex[1].group('obj'),
                   'child_term_id': 'free_var',
                   'editor': dot_editor},}

'''
                  'idx':
                  {'child_name': lambda node: node.name.lex[1].group('obj'),
                   'child_term_id': 'free_var'},
                  'editor': idx_editor}
'''
