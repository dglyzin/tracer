import re


class Extractor():

    '''Contain some methods for variable recognition
    and extraction for different dialects.

    - ``*_terms_spec``-- contain terms, that must be ignored
    (i.e. never been var or has val)
    
    - ``*_terms_vars`` -- dict for vars terms.
    if for some term there is no key in this dict
    then it is not a var.
    if there is a key, but with empty value list
    then this term is always a var
    if value list not empty, then it interpreted as
    regular expresion for val, and if all
    of them is fail, that it is not var but it's val.
    (like sin, cos is "val" of term "func" while f is a "var")
        
    - ``*_map_lex_to_vars`` -- if term from *_terms_vars not here
    then lex_value used as var, else use function from this
    dict as replacer.
    '''

    def __init__(self, dialect):
        self.dialect = dialect

        self.cs_terms_spec = ["let", "clause_where", "clause_for",
                              "clause_into", "clause_or",
                              "if", "if_only", "if_def",
                              "for_all", "exist", "exist_single",
                              "eq"]
        
        self.cs_terms_vars = {
            "pred": [],  # all var
            "var": [],  # all var
            "set": [r"^[A-Z]$"]}  # var only for single capital letters.

        # if term from cs_terms_vars not here
        # then lex_value used as var:
        self.cs_maps_lex_to_vars = {"pred": lambda lex_value: lex_value[:-1]}

        self.eqs_terms_spec = ["pow", "unary_div", "diff",
                               "bound", "diff_time_var"]

        self.eqs_terms_vars = {
            "dot": [],  # all var
            "idx": [],  # all var
            "func": ["^[a-z]$"],  # var only for single uncapital letters.
            "var": [],  # all var
            "free_var": [],  # all var
            "time": [],  # all var
            "coeffs": []}  # all var

        # if term from eqs_terms_vars not here
        # then lex_value used as var:
        self.eqs_maps_lex_to_vars = {
            "dot": lambda lex_value: lex_value.split(".")[0],
            "idx": lambda lex_value: lex_value.split("[")[0],
            "func": lambda lex_value: lex_value[:-1]}

    def is_var_or_val(self, term_name, var_or_val):
        
        '''
        Return True if:
        1) terms_vars[term_name] is empty list
        2) terms_vars[term_name] is not empty but
        3) re.search of some of it's elements for
           var_or_val is not None
        
        Return False if:
        1) term_name not in terms_vars
        2) re.search for all of it's elements for
        var_or_val is None
        '''

        if self.dialect == "cs":
            terms_vars = self.cs_terms_vars
        elif self.dialect == "eqs":
            terms_vars = self.eqs_terms_vars

        if term_name not in terms_vars:
            return(False)

        if len(terms_vars[term_name]) == 0:
            return(True)

        for pattern in terms_vars[term_name]:
            out = re.search(pattern, var_or_val)
            if out is not None:
                return(True)
        return(False)

    def get_terms_spec(self):
        
        '''Get terms, that must be ignored.'''

        if self.dialect == "cs":
            return(self.cs_terms_spec)
        elif self.dialect == "eqs":
            return(self.eqs_terms_spec)

    def get_terms_vars(self):
        if self.dialect == "cs":
            return(self.cs_terms_vars)
        elif self.dialect == "eqs":
            return(self.eqs_terms_vars)

    def map_ltv(self, term_name, term_lex_value):

        '''Map lex to var: lex_value |-> var
        (ex: "sin("|-> "sin")
        '''

        if self.dialect == "cs":
            map_dict = self.cs_maps_lex_to_vars
        elif self.dialect == "eqs":
            map_dict = self.eqs_maps_lex_to_vars

        if term_name not in map_dict:
            return(term_lex_value)
        
        else:
            return(map_dict[term_name](term_lex_value))
