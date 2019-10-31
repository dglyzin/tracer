from translator.tokenizer.words import Word as WordDict
from translator.tokenizer.patterns.patterns_types.pattern_re import PatternRe


class PatternTxt(PatternRe):

    '''For patterns txt templates.
    Ex::
    
       let: r"Let(${defs}in:${clauses}",
       if_then: r"${clauses}=>${clauses}",
       for_all: r"(\\for_all${x}"

    see more examples in::

      ``parser/translator/tokenizer/tests/tests_list``

    '''

    def __init__(self, name, template, grammar_type,
                 grammar_signature=[]):

        PatternRe.__init__(self, name, template, grammar_type,
                           grammar_signature)
        self.type = 'txt'

    def split_part(self, part, sent):
        
        '''Split sent with ``part`` re pattern,
        even if ``part`` contain some parentheses
        (it's reason why re.split dont used),
        Each ocurance of ``part`` will be replaced
        with ``self.map_ptw`` function unicly (i.e. all
        contained data will be relative to found substr
        value).

        Example:

        split_part: part='\in',
           sent='x \in X'
              -> ['x', ')f(', 'X']
                 where ')f(' is WordDict object,
                    contained some data.

        Inputs:
        
        - ``part`` -- string to find
        - ``sent`` -- string'''

        res = sent.find(part)

        if res < 0:
            return([sent])

        X = self.map_ptw(part)

        splited_sent = sent.split(part)
        
        # replace part with X in sent:
        # subst X instead of part:
        out = [[r, X] for r in splited_sent]
        out = sum(out, [])[:-1]

        return(out)

    def map_ptw(self, part):
        
        '''Convert part to WordDict object and
        add some data to it.

        Params must exist:
        
        - ``self.map_ptg`` dict from
        ``self.set_grammar_parts``'''

        value = part
        part_grammar_name = self.map_ptg[part]

        return(WordDict(part_grammar_name,
                        {"term_name": self.name,
                         "lex_value": value,
                         "lex_template": self.template,
                         "term_type": self.type,
                         "re_res": None}))
