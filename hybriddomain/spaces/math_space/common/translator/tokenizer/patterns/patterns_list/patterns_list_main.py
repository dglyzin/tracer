from translator.tokenizer.patterns.patterns_types.pattern_re import PatternRe
from translator.tokenizer.patterns.patterns_types.pattern_txt import PatternTxt
from translator.tokenizer.patterns.patterns_types.pattern_ex import PatternEx
from translator.tokenizer.patterns.patterns_list.patterns_list_sorter import Sorter


class Patterns():

    '''Storing and sorting patterns.
    (see ``patterns_list_sorter.py``
     for sorting)'''

    def __init__(self):
        
        '''If entry in patterns_list used only as part
        of other pattern, then pattern object for this
        will not be created.

        Example:

        # in that br term parts composed from other 'part'
        # that indicated with '${{}}':
        #  'a[i,j,]'
        ('idx', r"${{pred}}\[${args}\]",
        ('br_left', [True, False, True]),
        ('re',))
        '''

        self.sorter = Sorter(self)

    def compile_patterns(self, grammar_parts):
        
        '''Complite term's subterms parts (like ${{pred}},
        ${{arg_space}}, ${{float}}) and separate term into
        grammars parts with add replacement for them from
        ``grammar_parts``'''

        subterms_values = self.patterns_src
        for pattern in self.patterns_list_objs:
            oPattern = pattern[1]
            oPattern.compile_parts(subterms_values)
            oPattern.set_grammar_parts(grammar_parts)

    def make_patterns(self, dialect):

        self.patterns_list_entrys = dialect

        '''
        self.patterns_list_cs = dialect

        self.patterns_list_eq = dialect

        if dialect == 'cs':
            self.patterns_list_entrys = self.patterns_list_cs
        elif dialect == 'eqs':
            self.patterns_list_entrys = self.patterns_list_eq
        '''

        # map: term_name -> pattern:
        self.patterns_src = dict([(pattern[0], pattern[1])
                                  for pattern in self.patterns_list_entrys])


        '''
        # map: grammars term type -> grammars term names:
        self.gtn = dict([('br', 'f('),
                         ('a', 'a')])

        # map: term_name -> patterns grammar types:
        self.pgt = dict([(term_name, grammar_name)
                         for (term_name, _,
                              grammar_name) in self.patterns_list])

        '''

        self.patterns_list_objs = []
        self.patterns_dict_objs = {}

        for data in self.patterns_list_entrys:
            term_name = data[0]
            term_pattern = data[1]
            grammar_type = data[2]
            pattern_type = data[3]
            '''
            print("term_name, term_pattern,"
                  + " grammar_type, pattern_type:")
            print(str((term_name, term_pattern,
                       grammar_type, pattern_type)))
            '''
            if pattern_type[0] == 're':
                if grammar_type[0] in ('br', 'br_left', 'br_mid', 'br_right'):
                    oPattern = PatternRe(term_name, term_pattern,
                                         grammar_type[0], grammar_type[1])
                elif grammar_type[0] == 'a':
                    oPattern = PatternRe(term_name, term_pattern,
                                         grammar_type[0])
                elif grammar_type[0] == 'part':
                    continue
            elif pattern_type[0] == 'txt':
                if grammar_type[0] in ('br', 'br_left', 'br_mid', 'br_right'):
                    oPattern = PatternTxt(term_name, term_pattern,
                                          grammar_type[0], grammar_type[1])
                elif grammar_type[0] == 'a':
                    oPattern = PatternTxt(term_name, term_pattern,
                                          grammar_type[0])
                elif grammar_type[0] == 'part':
                    continue
            elif pattern_type[0] == 'ex':
                oPattern = PatternEx(term_name, term_pattern)

            entry = (term_name, oPattern, data)
            self.patterns_list_objs.append(entry)
            self.patterns_dict_objs[term_name] = entry

    def map_ptg(self, term_name):

        term_names = [entry[0] for entry in self.patterns_list]
        term_idx = term_names.index(term_name)
        grammar_type = self.patterns_grammar
        pattern_str = self.patterns_list[term_idx][1]
        
        if grammar_type == 'br':
            
            pass
