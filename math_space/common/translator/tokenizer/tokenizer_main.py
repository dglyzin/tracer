'''
! input sent must not have spaces.
 
Examples:

>>> import lex
>>> goal = lex.lex('D[U,{x, 3}]+sin(x+y)');goal
['a', '+', 'f', 'x', '+', 'y', ')']

>>> goal[0].lex
['D[U,{x,3}]', <_sre.SRE_Match object; span=(0, 10), match='D[U,{x,3}]'>]

'''
import re
from translator.tokenizer.words import Word


class LexNetTokenizer():
    
    def __init__(self, lexNet):

        self.lexNet = lexNet

    def preproc(self, sent):
        sent = sent.replace(" ", "")

    def lex(self, sent="a+U*U*V+D[V,{y,1}]-c*D[U,{x,2}]"):

        ''' Lexical analysis of sent.

        lex sent =
          case find_pattern(sent, patterns) of
               [left, pattern, right] -> lex(left)+Word(pattern)+lex(right)
               [left, pattern] -> lex(left)+Word(pattern)
               [pattern, right] -> Word(pattern)+lex(right)
               otherwise -> list(sent)
          where
                -- return list of remained words:
                find_pattern sent [] = [Word(char) for char in sent]

                -- return res or try with others patterns:
                find_pattern sent [x:xs] = if res=re.find(x, sent) then res
                                              else find_pattern sent xs

        Input: string without spaces.

        Return: list[elms] where elems is Word
                if pattern found then
                   elms.lex = ['found lexem', re.match object]
                else then elms.lex = [elms.name] where name is original char.
        Tests:
        >>> t = lex("a+U*U*V+D[V,{y,1}]-c*D[U,{x,2}]");t
        ['a', '+', 'a', '*', 'a', '*', 'a', '+', 'a', '-', 'a', '*', 'a']
        >>> type(t[0])
        Word
        >>> t[8].lex[1].group()
        'D[V,{y,1}]'
        '''

        lps = self.lexNet

        # check all patterns:
        for pattern_name, pattern_value in lps.patterns:
            res = re.search(pattern_value, sent)

            if res is not None:
                # recursively transform all word's:

                # first is found element (implementation of pattern),
                # rest is, splited with first, sent:
                first = res.group()
                rest = self.split(sent, res)

                if len(rest) == 2:
                    left = self.lex(rest[0])
                    X = [Word(lps.map_ptg[pattern_name],
                              [first, res, pattern_name])]
                    right = self.lex(rest[1])

                    # [left, X, right]
                    return(left + X + right)

                elif(len(rest) == 1):
                    if res.start == 0:
                        X = [Word(lps.map_ptg[pattern_name],
                                  [first, res, pattern_name])]
                        right = self.lex(rest[0])

                        # [X, right]
                        return(X + right)
                    else:
                        left = self.lex(rest[0])
                        X = [Word(lps.map_ptg(pattern_name),
                                  [first, res, pattern_name])]

                        # [left, X]
                        return(left + X)
        # if no pattern found split remained:
        # return(list(sent))
        return([Word(char, [char, None, None]) for char in sent])

    def split(self, sent, re_search_out):

        '''Split but only one occurrence'''

        start_index = re_search_out.start()
        end_index = re_search_out.end()
        return([sent[:start_index], sent[end_index:]])

