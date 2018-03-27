'''
Contain some grammars for parser.

Function gm_to_cnf gransform grammar to Chomsky normal form (CNF)
for cyk algorithm.
'''
'''
FOR
   E -> E{+-}T|T
   T->T{*/}F|T{*/}W|T{*/}V|F
   W -> (E)^
   V -> f(E)
   F->(E)|a
'''
grammar_pow_f = [('E', ('E', 'P', 'T')), ('E', ('T')),
                 ('T', ('T', 'M', 'F')), ('T', ('F')),
                 ('T', ('T', 'M', 'W')), ('T', ('W')),
                 ('T', ('T', 'M', 'V')), ('T', ('V')),

                 ('F', ('L', 'E', 'R')),
                 ('W', ('LPOW', 'E', 'RPOW')),
                 ('V', ('LF', 'E', 'RF')),
                 ('F', ('a')),
                 
                 ('M', ('*')), ('M', ('/')),
                 ('P', ('+')), ('P', ('-')),
                 ('L', ('(')), ('R', (')')),
                 ('LPOW', ('(')), ('RPOW', ('w')),
                 ('LF', ('f')), ('RF', (')'))]


def rtp(rule, _id, others):

    '''Transform rules like ('E', ('T', 'P', 'F')) to
    ('E', ('T', 'E1')), ('E1', ('P', 'F')) '''

    if len(rule[1]) > 2:
        unterm = rule[0] + str(_id)
        _id += 1
        new_rule_l = (rule[0], (rule[1][0], unterm))
        new_rule_r = (unterm, rule[1][1:])
        others.append(new_rule_l)
        return(rtp(new_rule_r, _id, others))
    else:
        others.append(rule)
        return(others)


def find_rules_for(rule_name, rules):

    '''Find rule[1]
    where rule ('A', ('B', 'C'))
    for rule_name = 'A'
    '''

    found_rules = []
    for rule in rules:
        if rule[0] == rule_name:
            found_rules.append(rule[1])
    return(found_rules)


def gm_to_cnf(grammar):

    '''Transform grammar to Chomsky normal form (CNF)'''

    new_rules = []

    # FOR remove more then two term rules:
    for rule in grammar:
        if len(rule[1]) > 2:
            new_rules.extend(rtp(rule, 1, []))
        else:
            new_rules.append(rule)
    # END FOR

    rules = new_rules
    new_rules = []

    # FOR remove one term rules:
    rules.reverse()
    new_rules = []
    for rule in rules:
        # if single untermenal:
        if len(rule[1]) == 1 and rule[1].isupper():
            # subs it from it's rule:
            found_rules = find_rules_for(rule[1], new_rules)
            # note: searched in alredy found rules

            for found_rule in found_rules:
                new_rules.append((rule[0], found_rule))
        else:
            # unchange:
            new_rules.append(rule)
    # END FOR
    return(new_rules)


if __name__ == '__main__':
    grammar = grammar_pow_f
    print("\ninput:")
    for rule in grammar:
        print(rule)

    print('\nout:')
    g = gm_to_cnf(grammar)
    for rule in g:
        print(rule)
