'''
DESCRIPTION:
For undirect changes in original scheme.

'''
from domainmodel.criminal.params import Params
from domainmodel.criminal.cppOutsForTerms import CppOutsForTerms
from domainmodel.criminal.patterns import Patterns
from domainmodel.criminal.actions import Actions


class Parser():
    '''
    DESCRIPTION:
    If You want only parse string, use
    parseMathExpression method.
    Out will be in parser.out

    Use one general pattern for all parsing.
    This pattern composed from local patterns,
    each of which can be replaced by .cpp string
    (from CppOutsForTerms) by actions (from Actions).

    So for each new pattern
    You need to create:
       pattern in Patterns
              (for example: termArgBeter)
       outs in cppOutsForTerms
              (for example get_out_for_termArgBeter)
       actions in Actions
              (for example: actions_for_termArgBeter)
       params (only if they used in three previus)
              (for example: param_for_termArgBeter)
    ! name is important
    Then parser.__init__ will loads all needed params,
    find all outs and actions and replace patterns by
    outs.

    Some .cpp strings can contain
    elements (argi) for replacing it by founded values (like
    variables names, they values and so on)
    (see Action.action_add_args).
    In that case arg1 means first added args by some
    local pattern, arg2 -second and so on.
    FOR EXAMPLE:
    IF pattern looks like:
    termDemo = Group(termLocPatt1.setParseAction()
                     + termLocPatt2.setParseAction(action_add_args))
    AND actions looks like:
    action_for_termDemo = action_generate_out('termDemo', *args)
    actions_for_termLocPatt1 = action_add_args(cppOut.dataTermDemo, *args)
    actions_for_termLocPatt2 = action_add_args(cppOut.dataTermDemo, *args)
    AND
    outForTerm in cppOut looks like
       def get_out_for_termDemo():
           return('source[arg1][arg2]')
    THEN
    arg1 will be arg, corresponded to termLocPatt1
    arg2 will be arg, corresponded to termLocPatt2

    TODO:
    Can load .cpp paterns form .json config file
    (like outForTerm.. ).
    Can load terms and actions from extern files.
    '''
    def __init__(self):
        # blockNumber=None, dim='1D'
        '''
        TODO:
        self.real.copy()
        '''

        # INIT PARAMS
        self.params = Params()
        # self.params.init_params_general(blockNumber, dim)

        # params for termVarsDelay
        self.params.delays = []
        # END PARAMS

        # LOAD CPP OUT
        self.cppOut = CppOutsForTerms(self.params)

        # LOAD PATTERNS
        self.patterns = Patterns()

        # LOAD ACTIONS
        self.actions = Actions(self.params, self.cppOut)

        self.set_action_for_all_terms()

    def set_action_for_all_terms(self):
        '''
        DESCRIPTION:
        For each term in patterns (i.e name
        begin with "term")
        find action in actions (whose name end
        with term name).
        And then use term.setParseAction.

        EXAMPLE:
        For term:
           patterns.termArgs
        actions must be:
           actions.action_for_termArgs
        
        '''
        patterns = self.patterns.__dict__
        termsNames = [o for o in patterns.keys()
                      if "term" in o]
        self.mapTermsToActions = dict()
        for term in termsNames:
            action = self.actions.get_action_for_term(term)
            if action is not None:
                patterns[term].setParseAction(action)
                self.mapTermsToActions[term] = action

    def parseMathExpression(self, expr):
        self.clear_data()
        try:
            parsedExpression = self.patterns.eqExpr.parseString(expr)
        except:
            print("expr is not a equation")
            parsedExpression = self.patterns.baseExpr.parseString(expr)
        self.out = self.actions.out
        
        return(parsedExpression)

    def clear_data(self):
        '''
        DESCRIPTION:
        Clear terms data for reusing.
        '''
        self.cppOut.dataTermVarsPoint = []
        self.cppOut.dataTermVarsPointDelay = []

    def test(self):
        eqStrList = [u"U'=D[U(t-1.1),{y,1}]+D[U(t-5.9),{y,2}]+U(t-1)",
                     u"U'=a*(D[U,{y,2}])+U(t-3)",
                     u"U'=a*(D[U(t-2),{y,3}])+U(t-3)",
                     u"U'=a*(D[U(t-1),{y,2}] + D[U(t-5),{x,1}])"]
        for eq in eqStrList:
            print("eq = %s" % eq)
            print(self.parseMathExpression(eq))
