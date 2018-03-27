from words import Word
import abc


class Gen():
    metaclass = abc.ABCMeta

    # this function work with lexems in postprocessing:
    # in that case it just return lexem original value
    # because Word.lex = [lexem, re.math object]
    def __call__(self, term):

        '''Check if term is Word and if it is, call
        add_out_to method.

        Return:
           term if type(term) == str (like '+')
           cpp(term) if type(term) == Word (like 'D[U,{x,3}]')
           [cpp(tm) for tm in term] if type(term) == list.
                                       (like ['(', 'w']
                                        or ['f',')']'''

        if type(term) == str:
            # if term is not in lexem:
            X = term
        elif(type(term) == Word):
            # if term is type(Word)
            # it can be branch too
            # (in case of one argument
            # like (a)^3 or sin(a)):
            X = self.add_out_to(term)
        elif(type(term) == list):
            # for branches (a+...)^3 or sin(a+...):
            X = []
            for tm in term:
                if type(tm) == Word:
                    # for )^n and sin(:
                    X.append(self.add_out_to(tm))
                else:
                    # for ():
                    X.append(tm)
        return(X)
 
        @abc.abstractmethod
        def add_out_to(self, term):
            raise(BaseException(('add_out_to method of Gen class'
                                 + ' must be implemented')))
