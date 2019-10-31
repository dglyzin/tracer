import re
from collections import OrderedDict

# map: str -> list:


class PatternBase():
    
    ''' 
    For compiling terms:
    
    Each term (ex: '\\for_all {$in}')can be either complex (like )
    
    For subterms extraction and replacement.

    Subterm:

    t = '${subterm}' where t in template.
    t is called subterm cell.

    (Example: template = 'for all ${x} in ${list}' \
     subterms is x, list.)
        

    Params:

    - ``self.grammar_type`` -- type of grammar term, pattern
    represent which. Can be either 'br' or 'a':
    ('br': 'br_left', 'br_right', 'br_mid'), ('a')

    - ``self.template`` -- store template
    (Ex: '\{${var},${order}\}' for re, '{${var},${order}}' \
     for text)
    
    - ``delimiter`` -- is symbol prefix before first left
    subterm cell bracket. ``default`` is '$'

    - ``delimiter_fix`` -- is delimiter fixed for use in re.
    (Ex: for '$' is '\$')

    - ``subterm_pattern_group`` -- is subterm re group with
    "(?P<group_name>(group_pattern))" pattern. ``default``
    is r"(?P<subterm>[a-z|A-Z|_|0-9]+)".
    (Warning: donot use capturing parentheses in pattern here
    i.e. r"(?P<subterm>([a-z|A-Z|_|0-9])+) or will meet
    re bug in re.split, re.findall)

    - ``subterm_pattern_cell`` -- is subterm cell pattern.
    '''

    def __init__(self, template, grammar_type,
                 grammar_signature=[]):

        self.grammar_type = grammar_type

        self.value_lex_single = False

        if grammar_type == 'a':
            self.grammar_signature = []

            # indicate that term maked as single
            # (with compile_as_single function):
            self.value_lex_single = True

        elif grammar_type == 'br_mid':
            self.grammar_signature = [False, True, True]
        else:
            if grammar_signature == []:
                self.grammar_signature = [True, True, True]
            else:
                self.grammar_signature = grammar_signature

        # that will be changed in compile_parts:
        self.template = template

        # that will remaine same:
        self.template_original = template

        self.delimiter = r"$"
        self.delimiter_fix = r"\$"
        self.subterm_pattern = r"[a-z|A-Z|_|0-9]+"
        self.subterm_pattern_group = (r"(?P<subterm>%s)"
                                      % (self.subterm_pattern))
        self.subterm_pattern_cell = (r"%s\{%s\}"
                                     % (self.delimiter_fix,
                                        self.subterm_pattern))
        self.subterm_pattern_cell_group = (r"%s\{%s\}"
                                           % (self.delimiter_fix,
                                              self.subterm_pattern_group))
        self.subpart_pattern_group = (r"(?P<subpart>%s)"
                                      % (self.subterm_pattern))
        self.subpart_pattern_cell = (r"%s\{\{%s\}\}"
                                     % (self.delimiter_fix,
                                        self.subterm_pattern))
        self.subpart_pattern_cell_group = (r"%s\{\{%s\}\}"
                                           % (self.delimiter_fix,
                                              self.subpart_pattern_group))

    def split(self, sent_list, parts=None):

        '''Split sent_list at pattern.parts and replace
        each found part value to ``WordDict`` object
        recursively. WordDict onject will be contain
        some data (see ``self.map_ptg``).

        Before this ``self.set_grammar_parts`` must be used for
        adding.
        
        Example::
    
        split: ['\\for_all x \in X: x == y'
             ' and \\for_all y \in Y: y == z'] ->
           ['f(', ' x \\in X', ',', ' x == y and ',
            'f(', ' y \\in Y', ',', ' y == z']
        '''

        if parts is None:
            try:
                parts = self.parts
            except AttributeError:
                msg = "use self.set_grammar_parts first"
                raise(AttributeError(msg))
            
        if len(parts) == 0:
            return(sent_list)

        first, rest = parts[0], parts[1:]
        
        out = sum([self.filter(self.split_part(first, sent))
                   for sent in sent_list], [])
        # out = sum([self.split_sent_part(first, sent)
        #            for sent in sent_list], [])
        # print("split_out:")
        # print(out)
        return(self.split(out, parts=rest))
    
    def filter(self, sent_list):
        
        '''Remove some elements from result'''
        
        '''
        # remove None:
        splited_sent = list(filter(lambda elm: elm is not None,
                                   splited_sent))
        '''

        # remove '':
        out = list(filter(lambda elm: elm != '', sent_list))
        return(out)

    def split_sent_part(self, part, sent):
        
        '''
        Depricated, use split_part from ancestor instead.

        Split ``sent`` with ``part`` of this pattern.
        Result will be list in which subsent, according to part,
        will be replaced with Word(map_ptg(part)).
        
        Example::

           split_sent_part: "\for_all",
                "\\for_all x \in X: x == y" ->
              ['f(', ' x \\in X: x == y']
        '''
        
        res = self.search_part(part, sent)
        if res is None:
            return([sent])
        
        found_value, splited_sent = res

        X = self.map_ptw(part, found_value)
        # X = self.map_ptg[part]

        # print('search_part res:')
        # print(res)

        # remove None:
        splited_sent = list(filter(lambda elm: elm is not None,
                                   splited_sent))

        # print('search_part not None res:')
        # print(res)

        # replace part with X in sent:
        # subst X instead of part:
        out = [[r, X] for r in splited_sent]
        out = sum(out, [])[:-1]

        # remove '':
        out = list(filter(lambda elm: elm != '', out))
        return(out)

    def set_grammar_parts(self, grammar_parts):
        
        '''If single term then only part is
        ``self.value_lex`` (of ``self.value_lex_single``
        in that case) so add it to ``self.parts`` and
        it's grammar representation to ``self.map_ptg``
        dict. For ``self.value_lex`` in case of single
        ``self.compile_as_single`` method must be used
        first.

        If complex term then subdivide it into
        parts (using ``self.get_splited``), collect
        them in ``self.parts``, find grammar for
        each to ``self.map_ptg`` dict'''

        if self.value_lex_single:
            a_grammar_parts = grammar_parts['a']
            self.parts = [self.value_lex]
            self.map_ptg = {self.parts[0]: a_grammar_parts}
    
        else:
            self.parts = self.get_splited(group=False)
            self.parts = list(filter(lambda elm: elm != '',
                                     self.parts))
            self.map_ptg = {}
            
            # FOR choice parts content:
            if self.grammar_type in ['br_left', 'br_right']:
                
                if self.grammar_signature == [True, True, True]:
                    left, mids, right = (self.parts[0], self.parts[1:-1],
                                         self.parts[-1])
                elif self.grammar_signature == [True, True, False]:
                    left, mids, right = (self.parts[0], self.parts[1:],
                                         None)
                elif self.grammar_signature == [True, False, True]:
                    left, mids, right = (self.parts[0], None,
                                         self.parts[-1])
                elif self.grammar_signature == [False, True, True]:
                    left, mids, right = (None, self.parts[0:-1],
                                         self.parts[-1])
                elif self.grammar_signature == [True, False, False]:
                    left, mids, right = (self.parts[0], None,
                                         None)
                elif self.grammar_signature == [False, True, False]:
                    left, mids, right = (None, self.parts[:],
                                         None)
                elif self.grammar_signature == [False, False, True]:
                    left, mids, right = (None, None,
                                         self.parts[-1])             
                else:
                    raise(BaseException("Unsuported signature for %s"
                                        % (self.grammar_type)))
            elif self.grammar_type == 'br_mid':
                left, mids, right = (None, self.parts[:], None)
            else:
                raise(BaseException("Unsuported grammar_type %s"
                                    % (self.grammar_type)))
            # END FOR

            # FOR map:
            if self.grammar_type in ['br_left', 'br_right']:
                if self.grammar_type == 'br_left':
                    br_grammar_parts = grammar_parts['br']['br_left']
                elif self.grammar_type == 'br_right':
                    br_grammar_parts = grammar_parts['br']['br_right']
                if left is not None:
                    self.map_ptg[left] = br_grammar_parts['left']
                if mids is not None:
                    for part in mids:
                        self.map_ptg[part] = br_grammar_parts['mid']
                if right is not None:
                    self.map_ptg[right] = br_grammar_parts['right']

            elif self.grammar_type == 'br_mid':
                br_grammar_parts = grammar_parts['br']['br_mid']
                if mids is not None:
                    for part in mids:
                        self.map_ptg[part] = br_grammar_parts['mid']
            else:
                raise(BaseException("Unsuported grammar_type %s"
                                    % (self.grammar_type)))
            # END FOR

    def get_vector(self, subterms_grammar_values):
        
        '''Transform template to list, first element of
        is a term name, others is subterms grammar names.
        (ex: '\for_all ${x}, ${y}'
                |-> ['for_all', 'x', 'y'])

        Inputs:

        - ``subterms_grammar_values`` -- map from subterm_name to
        grammar's value, type of that value Word,
        contained all subterm info (for transforming to tree).

        Return:

        - list of values, first of which is term name, other
        is subterms.
        '''
        
        if self.value_lex_single:
            raise(BaseException("single pattern donot converted into"
                                + " function, they represented like term"))
        
        subterms = self.get_subterms()
        vector = []
        vector.append(self.name)
        for i, sterm in enumerate(subterms):
            vector.append(subterms_grammar_values[sterm])
        return(vector)

    def get_splited(self, group=True):
        
        '''Split term into grammar's parts with subterms
        pattern cell (which is re for all type of terms).
        (ex: '\for_all ${x}, ${y};'
                |-> ['\for_all', ',', ';'])'''
        
        if self.value_lex_single:
            raise(BaseException("single pattern donot converted into"
                                + " function, they represented like term"))
        
        if group:
            subterm_pattern_cell = self.subterm_pattern_cell_group
        else:
            subterm_pattern_cell = self.subterm_pattern_cell

        out = re.split(subterm_pattern_cell, self.template)
        return(out)

    def get_subterms(self, template=None):
        
        ''' Find all subterms in self.template

        ``re.findall(r'\$\{(?P<subterm>([a-z|A-Z|0-9])+)\}', \
        'a+${stiV123}+xxx+${si3}')``'''

        if template is None:
            template = self.template
        found_subterms = re.findall(self.subterm_pattern_cell_group,
                                    template)
        out = found_subterms
        # out = [subterm_value for (subterm_value, _) in found_subterms]
        
        # remove dublicates:
        out = list(dict(zip(out, out)).keys())
        return(out)

    def get_subparts(self, template=None):
        
        ''' Find all subparts in self.template

        ``re.findall(r'\$\{(?P<subterm>([a-z|A-Z|0-9])+)\}', \
        'a+${stiV123}+xxx+${si3}')``'''

        if template is None:
            template = self.template
        found_subterms = re.findall(self.subpart_pattern_cell_group,
                                    template)
        out = found_subterms
        # out = [subterm_value for (subterm_value, _) in found_subterms]
        
        # remove dublicates:
        out = list(dict(zip(out, out)).keys())
        return(out)

    def sub_parts_cells_with_names(self, template=None):

        ''' Sub to self.template: ${{[part_name}} |-> term_name.

        ``re.sub(r'\$\{\{(?P<subterm>([a-z|A-Z|0-9])+)\}\}', \
        r'\g<subterm>','a+${{stiV123}}(x)+${{si3}(y)}')``'''
        
        if template is None:
            template = self.template

        out = re.sub(self.subpart_pattern_cell_group, r'\g<subpart>',
                     template)
        self.value_lex = out
        return(out)

    def sub_parts_cells_with_values(self, subterms_values, template=None):

        ''' Sub to self.template:
           ${{[part_name}} |-> subterms_values[part_name].
        '''
        if template is None:
            template = self.template

        res = re.search(self.subpart_pattern_cell_group, template)

        if res is None:
            self.value_lex = template
            self.template = template
            return(template)

        subpart = res.groupdict()['subpart']
        template = (template[:res.start()]
                    + subterms_values[subpart]
                    + template[res.end():])
        return(self.sub_parts_cells_with_values(subterms_values,
                                                template=template))

    def compile_parts(self, subparts_values, template=None):

        ''' Sub to self.template all subterms recursively:
              ${{part_name}} |-> subterms_values[term_name].

        ``re.sub(r'\$\{\{(?P<subterm>([a-z|A-Z|0-9])+)\}\}', \
        r'\g<subterm>','a+${{stiV123}}(x)+${{si3}}(y)')``'''

        return(self.sub_parts_cells_with_values(subparts_values,
                                                template))
        '''
        # This code below is depricated because
        # in order to replace only one subpart
        # on a time for prevent replace part
        # of alredy replaced part of previus
        # (for iteration) subpart.
        # Ex: template = r"(?P<delay>${{arg_float}}) + ${{float}}"
        # where
        #   subpart arg_float = r"(?:${{float}})"
        #   subpart float = r"\d+\.\d+|\d+"
        # after self.sub_parts_cells_with_names it will lock's like:
        # r"(?P<delay>arg_float) + float"
        # and after subs of arg_float it will lock's like
        # r"(?P<delay>(?:${{float}})) + float"
        # but after subs of float (in ``for`` interation) it
        # will lock's like:
        # r"(?P<delay>(?:${{\d+\.\d+|\d+}})) + \d+\.\d+|\d+"
        # and that is wrong.

        if template is None:
            # in order to find patterns like
            # arg_float before patterns like float:
            subparts_values = self.sort_subparts_dict(subparts_values)

        subparts = self.get_subparts(template)

        if len(subparts) == 0:
            # if nothing to substitute:

            # self.value_lex_single = True
            if template is None:
                self.value_lex = self.template
                return(self.template)
            else:

                self.value_lex = template
                self.template = template
                return(template)

        template_as_complex = self.sub_parts_cells_with_names(template)
        out = template_as_complex

        for subpart in subparts:
            out = out.replace(subpart, subparts_values[subpart])
        
        return(self.compile_parts(subparts_values, template=out))
        '''

    def sort_subparts_dict(self, subparts_values):

        '''Replace ``subparts_values`` dict
        with same but whose keys is sorted  according they
        self-containess (like "arg_float" < "float")
        (see ``self.sort_subparts_keys``)'''

        keys = list(subparts_values.keys())
        keys_sorted = self.sort_subparts_keys(keys)
        ordered = OrderedDict([(key, subparts_values[key])
                               for key in keys_sorted])
        # print("\nordered:")
        # print(ordered)
        return(ordered)

    def sort_subparts_keys(self, keys):

        '''Sort keys according they
        self-containess (like "arg_float" < "float")'''

        if len(keys) in (0, 1):
            return(keys)
        
        first, rest = keys[0], keys[1:]
        
        prefix = [other for other in rest
                  if first in other]
        suffix = [other for other in rest
                  if first not in other]
        return(self.sort_subparts_keys(prefix)
               + [first]
               + self.sort_subparts_keys(suffix))

