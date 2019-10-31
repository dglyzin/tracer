# parser$ python3 -m translator.sampling.slambda.data.gens.algebra.groups

import random

# format: (gen(group), gen(subgroup)):
subgroups = [
    # 31 entries
    # FOR abelian, abelian:
    (("(2,4)(3,5)", "(2,5,4,3)"), ("(2,4)(3,5)",)),

    (("(1,2)(3,5)", "(1,5,2,3)"), ("(1,2)(3,5)", "(1,5,2,3)")),
    (("(1,2)(3,5)", "(1,5,2,3)"), ("(1,2)(3,5)",)),

    (("(2,3)(4,5)", "(2,4)(3,5)"), ("(2,4)(3,5)", "(2,3)(4,5)")),
    (("(2,3)(4,5)", "(2,4)(3,5)"), ("(2,3)(4,5)",)),
    (("(2,3)(4,5)",), ("(2,3)(4,5)",)),

    (("(1,4)(2,3)", "(1,3)(2,4)"), ("(1,3)(2,4)", "(1,4)(2,3)")),
    (("(1,4)(2,3)", "(1,3)(2,4)"), ("(1,2)(3,4)",)),
    (("(1,2)(3,4)",), ("(1,2)(3,4)",)),

    (("(1,3)(2,5)", "(1,5,3,2)"), ("(1,3)(2,5)", "(1,5,3,2)")),
    (("(1,3)(2,5)", "(1,5,3,2)"), ("(1,3)(2,5)",)),

    (("(1,4)(2,3)", "(1,3,4,2)"), ("(1,4)(2,3)", "(1,3,4,2)")),
    # END FOR

    # FOR not_abelian, abelian:
    (("(1,3,5)", "(1,3)"), ("(1,3,5)",)),

    (("(3,4,5)", "(4,5)"), ("(3,4,5)",)),
    (("(3,4,5)", "(4,5)"), ("(4,5)",)),

    (("(2,4,5)", "(2,5)"), ("(4,5)",)),
    (("(2,4,5)", "(2,5)"), ("(2,4,5)",)),

    (("(1,2,4)", "(2,4)"), ("(1,2,4)",)),
    (("(1,2,4)", "(2,4)"), ("(2,4)",)),

    (("(3,4,5)", "(1,2)(4,5)"), ("(1,2)(3,4)",)),
    (("(3,4,5)", "(1,2)(4,5)"), ("(1,2)(3,5)",)),
    (("(3,4,5)", "(1,2)(4,5)"), ("(3,4,5)",)),
    # END FOR

    # FOR not_abelian, not_abelian:
    (("(1,3,5)", "(1,3)"), ("(1,3,5)", "(3,5)")),
    (("(1,2,5)", "(1,2)"), ("(1,2,5)", "(2,5)")),
    (("(1,4,5)", "(1,5)(2,3)"), ("(1,4,5)", "(2,3)(4,5)")),
    (("(3,4,5)", "(4,5)"), ("(3,4,5)", "(4,5)")),
    (("(2,4,5)", "(2,5)"), ("(2,4,5)", "(4,5)")),
    (("(1,4,5)", "(1,5)"), ("(1,4,5)", "(4,5)")),
    (("(2,3,4)", "(3,4)"), ("(2,3,4)", "(3,4)")),
    (("(1,3,4)", "(3,4)"), ("(1,3,4)", "(3,4)")),
    (("(2,3,5)", "(1,4)(2,3)"), ("(2,3,5)", "(1,4)(3,5)")),
    (("(1,2,4)", "(2,4)(3,5)"), ("(1,2,4)", "(2,4)(3,5)")),
    # END FOR
]


# for test purpose this list contain
# only some of groups from subgroups list
# and some, that is not in subgroups:
abelian = [

    # FOR exist as X in subgroups(X, Y):
    # (1/6)
    ("(1,3,5)",),
    ("(3,4,5)",),
    ("(2,4,5)",),
    ("(2,4)(3,5)",),
    ("(2,4)(3,5)", "(2,3)(4,5)"),
    ("(1,2)(3,5)",),
    ("(1,3)(2,4)", "(1,4)(2,3)"),
    ("(1,2)(3,4)",),
    # END FOR

    # FOR exist as Y in subgroups(X, Y):
    # (1/24)
    ("(2,4)(3,5)", "(2,5,4,3)"),
    ("(2,3)(4,5)", "(2,4)(3,5)"),
    ("(1,4)(2,3)", "(1,3)(2,4)"),
    # END FOR

    # FOR exist as both (X, Y) in subgroups(X, Y):
    # (1/24)
    ("(1,2)(3,5)", "(1,5,2,3)"),
    ("(2,3)(4,5)",),
    # END FOR

    # FOR not exist in subgroups:
    # (2/3)

    ("(4,5)", "(1,2,3)"),
    ("(2,5)", "(1,4)"),
    ("(2,5)", "(1,3,4)"),
    ("(1,3)", "(2,4,5)"),
    ("(2,4)", "(1,3,5)"),
    ("(1,4)", "(2,3,5)"),
    ("(1,5)", "(2,3,4)"),
    ("(2,3)", "(1,4,5)"),
    ("(3,5)", "(1,2,4)"),
    ("(1,2)", "(3,4,5)"),
    
    ("(2,4)", "(1,3)"),
    ("(2,3)", "(1,5)"),
    ("(2,4)", "(1,5)"),
    ("(3,4)", "(1,2,5)"),

    ("(1,2)",),
    ("(1,2,3)",),
    ("(1,2,3,4)",),
    ("(1,2,3,4,5)",)
    # END FOR
]


def sub_X_Y_out(args, previus_states):

    '''
    X - subgroup of group Y.

    Inputs:

    - ``previus_states`` -- used for eliminating repetition
    during sampling for all signatures with type ``rand``

    Return:

    When return (*, None) this means unchacked states ended,
    and further sampling useless.
    '''
    
    _, _, out = args

    states = subgroups
    if len(previus_states) > 0:
        states = list(set(subgroups).difference(set(previus_states)))
        if len(states) == 0:
            return(None, None)

    if out:
        Y, X = random.choice(states)
        previus_states.append((Y, X))
        return((X, Y, out), previus_states)
    return(None, previus_states)


def sub_x_Y_out(args, previus_states):

    '''
    x - subgroup of group Y.

    Inputs:

    - ``previus_states`` -- used for eliminating repetition
    during sampling for all signatures with type ``rand``

    Return:

    When return (*, None) this means unchacked states ended,
    and further sampling useless.
    '''
    
    x, _, out = args

    states = subgroups
    if len(previus_states) > 0:
        states = list(set(states).difference(set(previus_states)))
        if len(states) == 0:
            return(None, None)
        
    if out:
        Y, X = random.choice(states)

        # if x subgroup Y:
        pairs_Y_subgroupY = list(filter(lambda pair: pair[0] == Y, states))
        xs = map(lambda pair: pair[1], pairs_Y_subgroupY)
        if x in xs:
            previus_states.append((Y, x))
            return((x, Y, out), previus_states)
        else:
            # if x not found in xs, add whole xs to checked:
            previus_states.extend(pairs_Y_subgroupY)

    return(None, previus_states)


def sub_X_y_out(args, previus_states):
    
    '''
    X - subgroup of group y.

    Inputs:

    - ``previus_states`` -- used for eliminating repetition
    during sampling for all signatures with type ``rand``

    Return:

    When return (*, None) this means unchacked states ended,
    and further sampling useless.
    '''
    
    _, y, out = args

    states = subgroups
    if len(previus_states) > 0:
        states = list(set(states).difference(set(previus_states)))
        if len(states) == 0:
            return(None, None)
    if out:
        Y, X = random.choice(states)

        # if X subgroup y:
        pairs_Y_subgroupX = list(filter(lambda pair: pair[1] == X, states))
        ys = map(lambda pair: pair[0], pairs_Y_subgroupX)

        if y in ys:
            previus_states.append((y, X))
            return((X, y, out), previus_states)
        else:
            # if x not found in xs, add whole xs to checked:
            previus_states.extend(pairs_Y_subgroupX)

    return(None, previus_states)


def sub_x_y_Out(args):
    '''
    x - subgroup of group y.
    '''
    x, y, Out = args

    return((x, y, (y, x) in subgroups))


def sub_x_y_out(args):
    '''
    x - subgroup of group y.
    '''
    x, y, out = args
    if ((y, x) in subgroups) == out:
        return((x, y, out))
    else:
        return(None)


def abelian_X_out(args, previus_states):
    '''
    Inputs:

    - ``previus_states`` -- used for eliminating repetition
    during sampling for all signatures with type ``rand``

    Return:

    When return (*, None) this means unchacked states ended,
    and further sampling useless.
    '''
    
    _, out = args

    states = abelian
    if len(previus_states) > 0:
        states = list(set(states).difference(set(previus_states)))
        if len(states) == 0:
            return(None, None)
    if out:
        X = random.choice(states)
        previus_states.append(X)
        return((X, out), previus_states)

    return(None, previus_states)


def abelian_x_Out(args):
    x, out = args

    if out and (x in abelian):
        return((x, x in abelian))
    elif not out and (x not in abelian):
        return((x, x not in abelian))
    else:
        return(None)


if __name__ == "__main__":
    
    N = 10

    # FOR subgroup:
    print("\ntest sub_X_Y_out:")
    previus_states = []
    for i in range(N):
        result = sub_X_Y_out((None, None, True), previus_states)
        print("\nresult:")
        print(result)

    x = ("(2,4)(3,5)", "(2,3)(4,5)")
    print("\ntest sub_x_Y_out:")
    print("for given group x find group Y, with x contained in")
    print("for x: ", str(x))
    previus_states = []
    for i in range(N):
        result = sub_x_Y_out((x, None, True), previus_states)
        print("\nresult:")
        print(result)
        if result[0] is not None:
            break

    y = ("(2,3)(4,5)", "(2,4)(3,5)")
    print("\ntest sub_X_y_out:")
    print("for finding subgroup X of given group y")
    print("for y: ", str(y))
    previus_states = []
    for i in range(N):
        result = sub_X_y_out((None, y, True), previus_states)
        print("\nresult:")
        print(result)
        if result[0] is not None:
            break

    x = ("(2,4)(3,5)", "(2,3)(4,5)")
    y = ("(2,3)(4,5)", "(2,4)(3,5)")
    print("\ntest sub_x_y_out:")
    print("for x,y: ", str(x), " ", str(y))
    previus_states = []
    result = sub_x_y_Out((x, y, True))
    print("\nresult:")
    print(result)
    # END FOR

    # FOR abelian:
    print("\ntest abelian_X_out:")
    previus_states = []
    for i in range(N):
        result = abelian_X_out((None, True), previus_states)
        print("\nresult:")
        print(result)

    x = ("(1,2)(3,5)", "(1,5,2,3)")
    print("\ntest abelian_x_Out:")
    print("for x: ", str(x))
    previus_states = []
    result = abelian_x_Out((x, None))
    print("\nresult:")
    print(result)
    # END FOR
