'''
convert: parse_tree -> operator_tree


# because list is changeable in python
# don't need change parent.children list

bug with python

'''
import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('tree_converter.py')
logger.setLevel(level=log_level)


def case_0(node):

    ''' Case when node have only one children.
    Only in that case node.visited changed.
    
    Example:
    T->[a] to a.'''

    parent = node.parent
    child = node.children[0]
    
    child.visited = True

    parent.replace_child(node, child)

    # return succ:
    return(parent)


def case_1(node):

    ''' Case when node have two children, one
    of which is operator, other not.
    In that case choice operator node as top node.
    
    Example:
    T->[a, *->[a]] to *->[a, a]'''

    op_node = node.find_op_child()
    unop_node = node.find_unop_child()

    op_node.add_child(unop_node)

    parent = node.parent
    if parent is not None:
        parent.replace_child(node, op_node)

        # return succ:
        return(parent)
    else:
        op_node.parent = parent
        # root node
        return(op_node)


def case_3_0(node):

    ''' Case when node have two children, one
    of which is brackets, other not (W->[a, )] or E->[(, a]).
    In that case it transform from:
    T->['(', H->[X, ')']]
    to
    br->['(', args->[X], ')']
    !Right branch is alvays second (from buttom)'''

    parent = node.parent
    grandparent = parent.parent

    br_r_node = node.find_br_child()
    # br_l_node = parent.find_br_child()
    # import pdb; pdb.set_trace()

    # cut right bracket from H:
    node.remove_child(br_r_node)

    # insert right bracket to br node (T)
    # (like T->['(', H->[X], ')']):
    parent.add_child(br_r_node)

    # rename H to args:
    node.name = 'args'
    node.visited = True

    # rename T to br:
    parent.name = 'br'
    parent.visited = True

    if grandparent is not None:
        # return succ:
        return(grandparent)
    else:
        # root node
        return(parent)


def case_3_1(node):

    ''' Case when node have two children, one
    of which is brackets, other not (W->[a, )] or E->[(, a]).
    In that case it transform from:
    T->['(', H->[args, ')']]
    to
    br->['(', args, ')']'''

    parent = node.parent
    grandparent = parent.parent
    
    arg_node = node.find_unbr_child()
    br_r_node = node.find_br_child()
    # br_l_node = parent.find_br_child()
    # import pdb; pdb.set_trace()
    node.remove_child(br_r_node)
    node.remove_child(arg_node)

    parent.remove_child(node)

    parent.add_child(arg_node)
    parent.add_child(br_r_node)
    parent.name = 'br'
    parent.visited = True

    if grandparent is not None:
        # return succ:
        return(grandparent)
    else:
        # root node
        return(parent)


def case_4_0(node):

    '''Case for function type of brackets with many
    arguments (like fa,a,a,)).

    From parent->[A1->[',', args->[a]]]
    To parent->args->[a]
    
    From parent->[A1->[',', X]]
    To parent->args->[X]
    '''
    
    parent = node.parent

    sp_node = node.find_sp_child()
    unsp_node = node.find_unsp_child()

    # from A1->[',', {arg, X}]
    # to A1->[{args, X}->[a]]
    node.remove_child(sp_node)

    if unsp_node.name == 'args':
        # from parent->[A1->[args->[a]]]
        # to parent->[args->[a]]
        parent.replace_child(node, unsp_node)
    else:
        # like parent->[A1->[X]]
        # to parent->[args->[X]]
        node.name = 'args'
        node.visited = True
    return(parent)


def case_4_1(node):

    '''Case for function type of brackets with many
    arguments (like fa,a,a,)).

    From A1->[X, args->[a]]
    To args->[X, a]'''

    parent = node.parent

    arg_node = node.find_arg_child()
    unarg_node = node.find_unarg_child()

    # from A1->[X, args->[a]]
    # to A1->[args->[X, a]]
    node.remove_child(unarg_node)
    arg_node.insert_child(unarg_node, 0)

    # from A1->[args->[X, a]]
    # to args->[X, a]
    parent.replace_child(node, arg_node)
    return(parent)


def case_2(node, op_nodes):

    ''' Case when node have only operator's like children.
    In that case choice operator with one node as top node.
    
    Example:
    E->[*->[a,a], +->[a]] to [+->[*->[a,a],a]]'''

    parent = node.parent

    # choice top_op_node:
    if len(op_nodes[0].children) in (0, 1):
        top_op_node = op_nodes[0]
        buttom_op_node = op_nodes[1]
    elif len(op_nodes[1].children) in (0, 1):
        top_op_node = op_nodes[1]
        buttom_op_node = op_nodes[0]
    else:
        import pdb; pdb.set_trace()
        raise(BaseException("case_2 no top node error"))

    top_op_node.add_child(buttom_op_node)

    # choice succ:
    if parent is not None:
        
        parent.replace_child(node, top_op_node)

        # return succ:
        return(parent)
    else:
        top_op_node.parent = parent
        # return succ
        return(top_op_node)


def convert(node, trace=0):
    
    '''Convert parse tree to operator's tree.'''
    
    if node.parent is None and node.visited:

        # end of algorithm:
        return(node)

    elif len(node.children) == 0 and not node.visited:
        node.visited = True
        succ = node.parent

    elif len(node.children) == 1 and not node.visited:
        # work with T->[a]
        logger.debug("case_0")
        succ = case_0(node)
    
    elif len(node.children) == 2:

        unvisited = node.get_unvisited()

        if len(unvisited) > 0:

            # pass farther:
            succ = unvisited[0]
        else:
            ops = node.get_operators()
            bps = node.get_brackets()
            sps = node.get_separators()
            ars = node.get_args()

            if len(bps) > 0 and len(ars) == 0:
                # work with F->['(', F1->[X, ')']]
                logger.debug("case_3_0")
                succ = case_3_0(node)
            elif len(bps) > 0 and len(ars) > 0:
                # work with F->['(', F1->[args, ')']]
                logger.debug("case_3_1")
                succ = case_3_1(node)

            elif len(sps) > 0:
                # work with A1->[',', arg]
                logger.debug("case_4_0")
                succ = case_4_0(node)
            elif len(ars) > 0:
                # work with A->[X, arg]
                logger.debug("case_4_1")
                succ = case_4_1(node)
                '''
                elif len(ops) == 0 and len(bps) != 0:
                    print("case_3")
                    succ = case_3(node)
                '''
            elif len(ops) == 0:  # and len(bps) == 0
                # work with T->[a]
                logger.debug("case_0")
                succ = case_0(node)
            elif len(ops) == 1:
                # work with T->[a, *->[a]]
                logger.debug("case_1")
                succ = case_1(node)
            elif len(ops) == 2:
                # work with E->[*->[a,a], +->[a]]:
                logger.debug("case_2")
                logger.debug("len(ops): %s" % (str(len(ops))))
                succ = case_2(node, ops)
    logger.debug("\nsucc:")
    logger.debug(succ)
    logger.debug("succ.visited: ")
    logger.debug(succ.visited)
    logger.debug("len(succ.children: )")
    logger.debug(len(succ.children))
    return(convert(succ))
