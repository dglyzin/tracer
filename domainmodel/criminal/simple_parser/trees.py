'''
convert: parse_tree -> operator_tree


# because list is changeable in python
# don't need change parent.children list

bug with python

'''


def py_bug_fix(node):

    '''For strange python bug'''

    node.children = [child for child in node.children]


def case_0(node):

    ''' Case when node have only one children.
    Only in that case node.visited changed.'''

    parent = node.parent
    child = node.children[0]
    node_id = parent.find_child(node)
    
    # remove node from parent
    parent.children.pop(node_id)

    child.parent = parent
    child.visited = True

    # add child to parent as new child
    py_bug_fix(parent)
    parent.children.insert(node_id, child)
    
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

    # add unop_node to op_node as child
    unop_node.parent = op_node
    # import pdb; pdb.set_trace()
    py_bug_fix(op_node)
    op_node.children.append(unop_node)

    parent = node.parent
    if parent is not None:
        node_id = parent.find_child(node)

        # remove node from parent
        parent.children.pop(node_id)

        # add op_node to parent as new child
        op_node.parent = parent
        py_bug_fix(parent)
        parent.children.insert(node_id, op_node)
    
        # return succ:
        return(parent)
    else:
        op_node.parent = parent
        # root node
        return(op_node)


def case_3(node):

    ''' Case when node have two children, one
    of which is brackets, other not (W->[a, )] or E->[(, a]).
    In that case choice not brackets node as top node.'''

    term_node = node.find_term_child()
    br_node = node.find_br_child()

    # import pdb; pdb.set_trace()
    
    # add br_node to term_node as child
    br_node.parent = term_node
    # import pdb; pdb.set_trace()
    py_bug_fix(term_node)
    term_node.children.append(br_node)

    parent = node.parent
    if parent is not None:
        node_id = parent.find_child(node)

        # remove node from parent
        parent.children.pop(node_id)

        # add term_node to parent as new child
        term_node.parent = parent
        py_bug_fix(parent)
        parent.children.insert(node_id, term_node)
    
        # return succ:
        return(parent)
    else:
        term_node.parent = parent
        # root node
        return(term_node)


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

    # add buttom_node to top_op_node as child
    buttom_op_node.parent = top_op_node
    py_bug_fix(top_op_node)
    top_op_node.children.append(buttom_op_node)

    # choice succ:
    if parent is not None:

        # remove node from parent
        node_id = parent.find_child(node)
        parent.children.pop(node_id)
        
        # add op_node to parent as new child
        top_op_node.parent = parent
        py_bug_fix(parent)
        parent.children.insert(node_id, top_op_node)

        # return succ:
        return(parent)
    else:
        top_op_node.parent = parent
        # return succ
        return(top_op_node)


def convert(node):
    
    '''Convert parse tree to operator's tree.'''
    
    if node.parent is None and node.visited:

        # end of algorithm:
        return(node)

    elif len(node.children) == 0 and not node.visited:
        node.visited = True
        succ = node.parent

    elif len(node.children) == 1 and not node.visited:
        print("case_0")
        succ = case_0(node)
    
    elif len(node.children) == 2:

        unvisited = node.get_unvisited()

        if len(unvisited) > 0:

            # pass farther:
            succ = unvisited[0]
        else:
            ops = node.get_operators()

            if len(ops) == 0:
                print("case_3")
                succ = case_3(node)
            elif len(ops) == 1:
                print("case_1")
                succ = case_1(node)
            else:
                print("case_2")
                print("len(ops): %s"%(str(len(ops))))
                succ = case_2(node, ops)
    print("\nsucc:")
    print(succ)
    print("succ.visited: ", succ.visited)
    print("len(succ.children: )", len(succ.children))
    return(convert(succ))
