class LexMixTokenizer():

    '''Mix tokenizer for replacing bracket (br)
    patterns as well as unbracket (a) ones.
    also work simultaneously with re and txt
    patterns templates.
    Replace found in ``sent`` patterns with
    type(WordDict) object, contained data about pattern.
    (see ``self.lex_br`` method)
    
    Examples::
    
       sent:

          "group(A) \\and abelian(A) => Eq(A = A_1 + ... + A_n)Eq"

       will be replaced with:

          ['f(', 'a', ')', 'm', 'f(', 'a', ')', 'm', 'a']

       where ``grammar_parts`` represented with
        ``WordDict`` objects:
          
         'f(' - br_left (pred: "group(arg)")
         'a' - a (set: "A", eq: "Eq(A = A_1 + ... + A_n)Eq")
         'm' br_mid (conj: "\\and", if: "=>")
         all others ("(" in that case) remained type(str).

    see more examples in::

       ``parser/translator/tokenizer/tests/tests_list``
    '''

    def __init__(self):
        pass

    def set_patterns_list(self, patterns_list):

        '''Used before ``self.lex_br``
        patterns type must be one of supported
        (PatternRe, PatternTxt, PatternEx)
        All patterns must be maked and compiled
        and ``pattern.set_grammar_parts`` must
        be used before use this method.
        (see ``tests_tokenizer_mix.py`` for examples)'''

        self.patterns = patterns_list

    def lex_br(self, sent_list, patterns=None):

        '''Map each pattern in each element of sent_list
        to it's grammar pattern and split remained so output
        is also a list.

        Example:
        
        (see tests)
        '''

        if patterns is None:
            patterns = self.patterns
            
        if len(patterns) == 0:
            return(sent_list)

        first, rest = patterns[0], patterns[1:]

        out = sum([first.split([sent])
                   if type(sent) == str
                   else [sent]
                   for sent in sent_list], [])
        # Check type(sent) == str needed to prevent
        # replacement of 'a', when 'a' is type Word,
        # which is id for special type of grammars terms.

        return(self.lex_br(out, patterns=rest))
