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
from functools import reduce


def get_fmw(ms=["eq", ["add", "sub"], "div", "mul"]):

    '''
    Create grammar, contained terms:
    term (variable): a
    prefix func (pred): f), f E ), f(E,E,)
    suffix func: ( E w,
    brackets: (E),{E},[E]
    middle terms: from ms (see desc below)

    Create grammar for middle terms ms.
    Order of terms in ms represent they rules order
    in grammar (i.e. priority of operations). Terms with
    equal order represented in list putted in according position.
    Priority increased with order.
    ex: see default values.

    Because of  performance economy there is
    restriction:

    1) x:x+y <-> x MID x P y no brackets needed
    1.1) x = x+y <-> x MID x P y no brackets needed

    2) (x \in X) ^ (y \in Y) <-> (x MID X) M (y MID Y)
    brackets needed

    3) x:(y\in Y(x)) <-> x MID (y MID Y(x)) brackets needed

    4) (Let x in: A(x)=>B(x), C(x)=>G(x))
    <-> LF x D A(x) MID B(x) D C(x) MID G(x) RF
    no brackets needed (because let is func)

    To allow using MID inside P and M without brackets,
    one must change rule:
    ('F', ('a')), -> ('F', ('E')), ('F', ('a')),
    but it will slow translation.
    '''
    '''
    grammar_fmw = [
        # FOR mid:
        # m -> e m e:
        ('E', ('E', 'MID', 'E')),
        
        # m -> (e m e):
        ('E', ('L', 'E', 'MM')),
        ('MM', ('MID', 'E', 'R')),
        # END FOR

        ('E', ('E', 'P', 'T')), ('E', ('T')),
       
        ('T', ('T', 'M', 'F1')), ('T', ('F1')),
        ('T', ('T', 'M', 'W')), ('T', ('W')),
        ('T', ('T', 'M', 'V')), ('T', ('V')),
                  
        ('F1', ('L', 'E', 'R')),
        ('W', ('LPOW', 'E', 'RPOW')),

        ('V', ('LF', 'E', 'RF')),
        ('V', ('LF', 'A', 'RF')),
        ('A', ('E', 'D', 'A')), ('A', ('E', 'D')),
        ('F1', ('a')),

        ('D', ','),
        ('MID', 'm'),
        ('M', (mul)), ('M', (div)),
        ('P', (add)), ('P', (sub)),
        ('L', ('(')), ('R', (')')),
        ('LPOW', ('(')), ('RPOW', ('w')),
        ('LF', ('f')), ('RF', (')'))]
    '''
    grammar_fmw = []
    
    last_elm_idx = len(ms)-1
    for i, elm in enumerate(ms):

        # if elm is list
        # (contained from elements equal to m):
        if type(elm) == list:
            m = elm[0]
            mlist = elm[1:]
        else:
            m = elm
            mlist = []

        if i != last_elm_idx:
            if i == 0:
                # add top rule (begin from M0):
                # (ex: ('E', ('E', 'P', 'T')), ('E', ('T')),)
                grammar_fmw.append(("E", ("E", m.upper(), "M"+str(i)+"_")))
                grammar_fmw.append(("E", ("M"+str(i)+"_",)))
            else:
                # add rule for each middle term:
                # (ex: (M0, (M0, ADD, M1)), (M0, M1)):
                grammar_fmw.append(("M"+str(i-1)+"_",
                                    ("M"+str(i-1)+"_", m.upper(), "M"+str(i)+"_")))
                grammar_fmw.append(("M"+str(i-1)+"_", ("M"+str(i)+"_",)))

        else:
            # add brackets terms to last mid rule:
            grammar_fmw.extend([
                ('M'+str(i-1)+"_", ('M'+str(i-1)+"_", m.upper(), 'F1')),
                ('M'+str(i-1)+"_", ('F1',)),

                ('M'+str(i-1)+"_", ('M'+str(i-1)+"_", m.upper(), 'W')),
                ('M'+str(i-1)+"_", ('W',)),

                ('M'+str(i-1)+"_", ('M'+str(i-1)+"_", m.upper(), 'V')),
                ('M'+str(i-1)+"_", ('V',)), ])

            grammar_fmw.extend([

                ('F1', ('L', 'E', 'R')),
                ('W', ('LPOW', 'E', 'RPOW')),

                ('V', ('LF', 'E', 'RF')),
                ('V', ('LF', 'A', 'RF')),
                ('A', ('E', 'D', 'A')), ('A', ('E', 'D')),
                ('F1', ('a',)),

                ('D', (',',)),
                ('L', ('(',)), ('R', (')',)),
                ('L', ('[',)), ('R', (']',)),
                ('L', ('{',)), ('R', ('}',)),
                ('LPOW', ('(',)), ('RPOW', ('w',)),
                ('LF', ('f',)), ('RF', (')',)), ])

        # FOR add rules like ("ADD", ("add",)):
        grammar_fmw.append((m.upper(), (m.lower(),)))

        # add all terminal elements,
        # equal to m (in sense of grammar priority)
        # to m rule:
        # (ex: ["add", "sub"]-> ("ADD", ("add",)), ("ADD", ("sub",)))
        for msimilar in mlist:
            grammar_fmw.append((m.upper(), (msimilar.lower(),)))
        # END FOR

    '''
    print("grammar_fmw:")
    for rule in grammar_fmw:
        print(rule)
    '''
    grammar_fmw = gm_to_cnf(grammar_fmw)
    return(grammar_fmw)

    
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

gm_pow_f_args = [('E', ('E', 'P', 'T')), ('E', ('T')),
                 ('T', ('T', 'M', 'F')), ('T', ('F')),
                 ('T', ('T', 'M', 'W')), ('T', ('W')),
                 ('T', ('T', 'M', 'V')), ('T', ('V')),

                 ('F', ('L', 'E', 'R')),
                 ('W', ('LPOW', 'E', 'RPOW')),

                 ('V', ('LF', 'E', 'RF')),
                 ('V', ('LF', 'A', 'RF')),
                 ('A', ('E', 'D', 'A')), ('A', ('E', 'D')),
                 ('F', ('a')),
                 
                 ('D', ','),
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


def find_rules_for(rule_name, rules, rexcept=None):

    '''Find rule[1]
    where rule ('A', ('B', 'C'))
    for rule_name = 'A'
    '''

    found_rules = []
    for rule in rules:
        if rule[0] == rule_name and rule != rexcept:
            found_rules.append(rule[1])
    return(found_rules)


def remove_one_term_rules(rules):
    '''Replace one term rule like ("E", ("T",))
    with it's children rules like
       ("E", ("T", "S")), ("E", ("F",))
          for T: ("T", ("T", "S")), ("T", ("F",))
    Unterm rules like ("E", ("a",)) and two term rules
    like ("E", ("E", "E1")) remain untoched
    
    If correct order of rules was choiced
    it will result in beter performance.
    (for ex: [("E", ("T",)),("T", ("T", "S")), ("T", ("F",))]
     will have to change from rule ("T", ("F",)) twice (first
     replace in "E", then in "T")
     but for reverse order of same rules it will be only once
     (for that case rule ("T", ("F",)) have alredy be replaced
      with rule ("F", (something)) when arraive to "E"))
    '''

    for i, rule in enumerate(rules):
        isunterm = rule[1][0][0].isupper()
        '''
        try:
            test = rule[1].isupper()
        except AttributeError:
            test = rule[1][0].isupper()
        '''
        # if single untermenal:
        if len(rule[1]) == 1 and isunterm:
            # subs it from it's rule:
            found_rules = find_rules_for(rule[1][0], rules)

            new_rules_for_rule = [(rule[0], found_rule)
                                  for found_rule in found_rules]
            # print("new_rules:")
            # print(new_rules_for_rule)

            # for speed up (in las for loop) unkown rules
            # (like rules[i+1:]) lead known
            # (like rules[:i], for which no replacement needed):
            return(remove_one_term_rules(new_rules_for_rule
                                         + rules[i+1:] + rules[:i]))
            # break
    return(rules)


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

    # FOR remove one term rules:
    # speed up if user choice correct order:
    rules.reverse()
    new_rules = remove_one_term_rules(rules)
    # END FOR

    # remove duplicates:
    f = lambda acc, x: acc+[x] if (x not in acc) else acc
    new_rules = list(reduce(f, new_rules, []))
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
