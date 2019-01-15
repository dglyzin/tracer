from translator.tokenizer.patterns.patterns_types.pattern_base import PatternBase
from translator.tokenizer.words import Word as WordDict


class PatternEx(PatternBase):

    '''For patterns ex templates.
    Content of this pattern will be ignored,
    and replaced entaerly with grammar_part (like 'a').

    Ex::
    
       eq: "Eq(${eqs})Eq"

    see more examples in::

      ``parser/translator/tokenizer/tests/tests_list``

    '''

    def __init__(self, name, template):

        PatternBase.__init__(self, template, 'a',
                             grammar_signature=[])

        self.value_lex_single = False

        self.name = name
        
        self.value_lex = None

        self.type = 'ex'

    def split(self, sent_list):

        sent = "".join(sent_list)
        
        left = self.parts[0]
        right = self.parts[1]

        found_left = sent.find(left)
        found_right = sent.find(right)

        if not (found_left < 0 or found_right < 0):
            
            content = sent[found_left+len(left):found_right]
            X = self.map_ptw(content)
            out = [sent[:found_left]] + [X] + [sent[found_right+len(right):]]
            return(out)

        elif not found_left < 0:
            raise(BaseException(("right part %s of"
                                 + " ex tern %s not found")
                                % (self.parts[1], self.name)))
        elif not found_right < 0:
            raise(BaseException(("left part %s of"
                                 + " ex tern %s not found")
                                % (self.parts[0], self.name)))
        else:
            # if nothing found:
            return(sent_list)

    def map_ptw(self, content):
        part_grammar_name = self.map_ptg
                
        return(WordDict(part_grammar_name,
                        {"term_name": self.name,
                         "content": content,
                         "lex_template": self.template,
                         "term_type": self.type}))

    def set_grammar_parts(self, grammar_parts):
        
        self.parts = self.get_splited(group=False)
        self.map_ptg = grammar_parts['a']

    def compile_parts(self, subterms_values):
        pass
