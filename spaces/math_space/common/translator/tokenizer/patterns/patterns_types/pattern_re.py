# parser$ python3 -m translator.tokenizer.patterns.pattern_re

from translator.tokenizer.patterns.patterns_types.pattern_base import PatternBase
from translator.tokenizer.words import Word as WordDict

import re


class PatternRe(PatternBase):

    '''For storing re term'''
    '''For patterns re templates.
    Ex:: 
    
       func: r"${{pred}}\(${args}"
       predicat: r"(?P<obj>[a-z|A-Z|_|0-9]+)\("
       float: r"\d+\.\d+|\d+"

    see more examples in::

      ``parser/translator/tokenizer/tests/tests_list``

    '''

    def __init__(self, name, template, grammar_type,
                 grammar_signature=[]):

        PatternBase.__init__(self, template, grammar_type,
                             grammar_signature)

        self.name = name
        
        self.value_lex = None
                
        self.type = 're'

    def find_single(self, sent_str):
        res = self.search(sent_str)
        if res is not None:
            lhs, rhs = res.split(sent_str)
            self.convert_to_word()
            
    def map_ptw(self, part, found_res):
        
        '''Convert part to WordDict object and
        add some data to it.

        Params must exist:
        
        - ``self.map_ptg`` dict from
        ``self.set_grammar_parts``'''

        value = found_res.group()
        part_grammar_name = self.map_ptg[part]

        return(WordDict(part_grammar_name,
                        {"term_name": self.name,
                         "lex_value": value,
                         "lex_template": self.template,
                         "term_type": self.type,
                         "re_res": found_res}))

    def search_part(self, part_value, sent):
        
        '''

        Depricated, use split_part instead

        Find pattern (self.value) in sent.

        Return:

        - ``[found_res, splited sent]`` or ``None``
        '''
        
        # pattern_value = self.value_lex

        found_res = re.search(part_value, sent)

        if found_res is not None:
            splited_sent = re.split(part_value, sent)
            return((found_res, splited_sent))
        else:
            return(None)

    def split_part(self, part, sent):
        
        '''Split sent with ``part`` re pattern,
        even if ``part`` contain some parentheses
        (it's reason why re.split dont used),
        Each ocurance of ``part`` will be replaced
        with ``self.map_ptw`` function unicly (i.e. all
        contained data will be relative to found substr
        value).

        Example:

        split_part: part='[t](-(?P<delay>\d+\.\d+|\d+))?',
           sent='y(t-1.1) == z(t-1.2)'
              -> ['y(','a',') == z(','a',')']
                 where first a.groupdict() == {'delay': 1.1}
                    second a.groupdict() == {'delay': 1.2}

        Inputs:
        
        - ``part`` -- re expresion
        - ``sent`` -- string'''

        res = re.search(part, sent)

        if res is None:
            return([sent])

        if res.group() == '':
            msg = ("\nWrong reg_pattern '%s'" % (str(self.name))
                   + "\npart %s" % (str(part))
                   + " \nprabobly symbol ^ used."
                   + " In re expresion symbol ^ means"
                   + " begining of string."
                   + " So use slash instead: '\^'")
            raise(AttributeError(msg))

        # print("res.group():")
        # print(res.group())
        X = self.map_ptw(part, res)

        start_index = res.start()
        end_index = res.end()
        out = ([sent[:start_index]] + [X]
               + self.split_part(part, sent[end_index:]))
        return(out)
