import abc


class Gen():
    metaclass = abc.ABCMeta

    # this function work with lexems in postprocessing:
    # in that case it just return lexem original value
    # because Word.lex = [lexem, re.math object]
    def __call__(self, term):

        '''Check if term is Word and if it is, call
        add_out_to method for simple nodes,
        translate_brackets for brackets.

        Input:
           term must be of type Word
        Return:
           cpp(term) if type(term) == Word (like 'D[U,{x,3}]')'''

        if(term.name == 'br'):  # type(term.name) == Word and
            # for branches (a+...)^3 or sin(a+...):
            leftb = term.children[0]
            rightb = term.children[-1]
            leftb, rightb = self.translate_brackets(leftb, rightb)
            X = (leftb, rightb)
        elif type(term.name) == str:
            # if term is not in lexem:
            X = term
        elif(term.name != 'br'):  # type(term.name) == Word and
            # if term is type(Word)
            # it can be branch too
            # (in case of one argument
            # like (a)^3 or sin(a)):
            X = self.add_out_to(term)

        return(X)
 
    @abc.abstractmethod
    def add_out_to(self, term):
        raise(BaseException(('add_out_to method of Gen class'
                             + ' must be implemented')))

    @abc.abstractmethod
    def translate_brackets(self, left_term, right_term):
        raise(BaseException(('translate_brackets method of Gen class'
                             + ' must be implemented')))
