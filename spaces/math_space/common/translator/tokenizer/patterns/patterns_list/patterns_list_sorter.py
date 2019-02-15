class Sorter():

    '''
    Methods for sorting patterns.
    For preventing write smaller
    patterns before bigger one, contained
    smaller in.
    (Ex:
       ('diff', r"D\[${{var}},${{arg_space_diff}}\]")
     contained
       ('var',
       r"(?P<val>[${{base_dep_vars}}](\(${{arg_time}}\))?)")
    but can be used also as 'a' term in same sent.)
    '''
    def __init__(self, net):
        
        self.net = net

    def sort(self, patterns=None):
        
        '''Sort pattern recursively:
        put more complex patterns toward begining
        using either parts compatibility
        (see ``self.has_part_in``) or used-defined
        order (see ``self.has_orders``
        and ``self.use_orders``)'''

        if patterns is None:
            patterns = self.net.patterns_list_objs
            
        if len(patterns) == 1:
            return([patterns[0]])
        elif len(patterns) == 0:
            return([])

        # print("patterns:")
        # print(patterns)
        first, rest = (patterns[0], patterns[1:])
        
        prefix = [other for other in rest
                  if self.choice_order(other, first)]
        suffix = [other for other in rest
                  if not self.choice_order(other, first)]
        return(self.sort(prefix) + [first] + self.sort(suffix))
            
    def choice_order(self, pattern_0, pattern_1):
        
        '''return True if p0 < p1 otherwise False'''

        if self.is_ex(pattern_0):
            return(True)
        elif self.is_ex(pattern_1):
            return(False)
        if self.has_orders(pattern_0, pattern_1):
            # using patterns orders for sorting:
            # print("using patterns orders for sorting")

            if self.use_orders(pattern_0, pattern_1):
                # p0 < p1

                if self.has_part_in(pattern_0, pattern_1):
                    # p1 < p0

                    self.raise_exception_0(pattern_0, pattern_1)
                else:
                    return(True)
            else:
                # p1 < p0

                if (self.has_part_in(pattern_1, pattern_0)):
                    # and not self.is_both_re(pattern_0, pattern_1)):
                    # p0 < p1

                    self.raise_exception_0(pattern_1, pattern_0)
                else:
                    return(False)
        else:
            # using patterns parts for sorting:
            # print("using patterns parts for sorting")

            if self.has_part_in(pattern_0, pattern_1):
                # p1 < p0

                if self.has_part_in(pattern_1, pattern_0):
                    # p0 < p1

                    self.raise_exception_1(pattern_0, pattern_1)
                else:
                    return(False)

            if self.has_part_in(pattern_1, pattern_0):
                # p0 < p1

                if self.has_part_in(pattern_0, pattern_1):
                    # p1 < p0

                    self.raise_exception_1(pattern_1, pattern_0)
                else:
                    return(True)

    def is_both_re(self, pattern_0, pattern_1):
        oPattern_0 = pattern_0[1]
        oPattern_1 = pattern_1[1]

        if oPattern_0.type == oPattern_1.type == "re":
            return(True)
        else:
            return(False)

    def is_ex(self, pattern):
        return(True if pattern[1].type == 'ex' else False)

    def raise_exception_1(self, pattern_0, pattern_1):
        
        '''Both patterns contain part that is part
        of some part of other pattern.
        (ex: p0:('in','which is:'), p1:('in:', 'which is')
        in sent0: "a, b in a+b=b+a which is: commutativety"
        must use p0 first
        but
        in sent1: "a in: G(a) which is group(a)"
        must use p1 first
        so cannot decide which of pattern (p0 or p1) is first in queue)'''
        
        oPattern_0 = pattern_0[1]
        oPattern_1 = pattern_1[1]

        part_00, part_01 = self.has_part_in(pattern_0, pattern_1)
        part_10, part_11 = self.has_part_in(pattern_1, pattern_0)

        raise(BaseException(("\n\nPart '%s' of pattern ('%s': %s)"
                             % (part_00, oPattern_0.name,
                                oPattern_0.template_original))
                            + "\ncontained in\n"
                            + (" part '%s' of pattern ('%s': %s) \nbut\n"
                               % (part_01, oPattern_1.name,
                                  oPattern_1.template_original))
                            + (" part '%s' of pattern ('%s': %s)"
                               % (part_10, oPattern_0.name,
                                  oPattern_0.template_original))
                            + "\ncontained in\n"
                            + (" part '%s' of pattern ('%s': %s)\n"
                               % (part_11, oPattern_1.name,
                                  oPattern_1.template_original))
                            + "\nand that is contradictonary"))

    def raise_exception_0(self, pattern_0, pattern_1):
        
        '''Given order contradict with part order i.e.
        order in which one pattern contain part that is
        part of some part of other pattern, in that case
        contained pattern must preside that whose part
        contain in.
        (ex: ('sin(', 1), ('sin', 0) contradicts)'''

        oPattern_0 = pattern_0[1]
        oPattern_1 = pattern_1[1]

        part_0, part_1 = self.has_part_in(pattern_0, pattern_1)

        raise(BaseException(("\n\nOrders of pattern ('%s': %s)"
                             % (oPattern_0.name,
                                oPattern_0.template_original))
                            + " set to be less then\n"
                            + (" that of pattern ('%s': %s) \nbut\n"
                               % (oPattern_1.name,
                                  oPattern_1.template_original))
                            + (" part '%s' of pattern ('%s': %s)"
                               % (part_0, oPattern_0.name,
                                  oPattern_0.template_original))
                            + "\ncontained in\n"
                            + (" part '%s' of pattern ('%s': %s)\n"
                               % (part_1, oPattern_1.name,
                                  oPattern_1.template_original))
                            + "\nand that is contradictonary"))

    def has_part_in(self, pattern_0, pattern_1):

        '''True if part in pattern_1.parts for some
        part in pattern_0.parts,
        which means pattern_1 < pattern_0
        
        Return:

        if True return (part_0, part_1) else
        False'''

        oPattern_0 = pattern_0[1]
        oPattern_1 = pattern_1[1]
        
        for part_0 in oPattern_0.parts:
            for part_1 in oPattern_1.parts:
                if part_0 in part_1:
                    return((part_0, part_1))
        return(False)
            
    def use_orders(self, pattern_0, pattern_1):
        
        '''True if pattern_0.num < pattern_1.num
        which means pattern_0 < pattern_1

        Example:
        
        False for

        pattern_0:
        # sin0(, abelian_prim(, a(:
        ('pred', r"(?P<obj>[a-z|A-Z|_|0-9]+)\(",
         ('re', 0))
        <
        pattern_1:
        # x, xs, normal_form_0
        ('var', r"(?P<obj>[a-z|_|0-9]+)",
         ('re', 2))'''

        data_0 = pattern_0[-1]
        data_1 = pattern_1[-1]

        pattern_type_0 = data_0[3]
        pattern_type_1 = data_1[3]

        return(True if pattern_type_0[1] < pattern_type_1[1]
               else False)

    def has_orders(self, pattern_0, pattern_1):

        '''if pattern_types of patterns has special
        orders in them, use it.
        
        Example:

        pattern:
        # sin0(, abelian_prim(, a(:
        ('pred', r"(?P<obj>[a-z|A-Z|_|0-9]+)\(",
         ('re', 0))
        has order 0.
        '''

        data_0 = pattern_0[-1]
        data_1 = pattern_1[-1]

        pattern_type_0 = data_0[3]
        pattern_type_1 = data_1[3]

        return(True if (len(pattern_type_0) > 1
                        and len(pattern_type_1) > 1)
               else False)
                
        
