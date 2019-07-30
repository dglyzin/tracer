'''This class replace str object to Word.
It can be used for storage addition data in parser
for each word.
Function replace_lex
'''


class Word(str):
    '''Replacer for strings. Has lex - addition parameter for lex data.'''
    def __new__(cls, val, lex=[]):
        obj = str.__new__(cls, val)
        obj.lex = lex
        return(obj)
    
    def replace_lex(self, lex_replacer=lambda x: x):
        return(lex_replacer(self.lex))


simple_words = [Word(char) for char in '(a+a)*a']
