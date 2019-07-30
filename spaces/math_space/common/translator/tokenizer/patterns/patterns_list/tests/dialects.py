'''
all m patterns used as
(for ex \\for)::

   A(x)=>B(x) \\for x \\in X
   A(x)=>B(y) \\for(x \\in X, y \\in Y)
   (A(x)=>B(x), C(y)=>E(y))\\for(x \\in X, y \\in Y)

'''
cs = [
    ('let', r"Let(${defs}in:${clauses}",
     ('br_left', [True, True, False]),
     ('txt',)),

    # FOR clauses:

    # use as A(x)=>B(x) \\where x \\in X
    # or A(x)=>B(y) \\where(x \\in X, y \\in Y)
    # or (A(x)=>B(x), C(y)=>E(y))\\where(x \\in X, y \\in Y)
    ('clause_where', "${clauses}\\where${defs}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    # use as A(x)=>B(x) \\for x \\in X
    # or A(x)=>B(y) \\for(x \\in X, y \\in Y)
    # or (A(x)=>B(x), C(y)=>E(y))\\for(x \\in X, y \\in Y)
    ('clause_for', "${clauses}\\for${defs}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    # use as x \\in X \\into A(x)=>B(x)
    # or x \\in X \\into(A(x)=>B(x), C(y)=>E(y))
    # or (x \\in X, y \\in Y)\\into(A(x)=>B(x), C(y)=>E(y))
    ('clause_into', "${defs}\\into${clauses}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('clause_or', "${clauses}\\or${clauses}",
     ('br_mid', [False, True, False]),
     ('txt',)),
    # END FOR

    # FOR if:
    ('if', r"${clauses}=>${clauses}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('if_only', r"${clauses}<=>${clauses}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('if_def', r"${clauses}<=${clauses}",
     ('br_mid', [False, True, False]),
     ('txt',)),
    # END FOR

    ('conj', "${pred}\\and${pred}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    # sin0(, abelian_prim(, a(:
    ('pred', r"(?P<obj>[a-z|A-Z|_|0-9]+)\(",
     ('br_left', [True, False, False]),
     ('re', 0.1)),

    ('def_0', "${kvs}:${args}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    # order used because in case with brackets
    # this can be interperated as pred
    # (like \\in(X:...)):
    ('in_0', "${kvs}\\in${args}",
     ('br_mid', [False, True, False]),
     ('txt', 0)),

    # FOR kv:
    ('for_all', "(\\for_all${x}",
     ('br_left', [True, False, False]),
     ('txt',)),

    ('exist', "(\\exist${x}",
     ('br_left', [True, False, False]),
     ('txt',)),

    ('exist_single', "(\\exist\\single${x}",
     ('br_left', [True, False, False]),
     ('txt',)),
    # END FOR

    # x, xs, normal_form_0
    ('var', r"(?P<obj>[a-z|_|0-9]+)", ('a',),
     ('re', 2)),

    # match all words which begin with capital letter
    # but not with not capital letter, '_' or number.
    # (ex: match Abelian, XXnew1, X1, X but not
    # abelianGroup0, xXs, X_0, X_f, engine_vector,
    # engine_vectorX, engine_vector_X, engine_vector_X0):
    # r"(?P<set>(?<![a-z|_|A-Z|0-9])([A-Z]+)([a-z]+)?([0-9]+)?)"

    ('set', r"(?P<set>(?<![a-z|_|A-Z|0-9])([A-Z]+)(${{var}}?))",
     ('a',), ('re', 1)),

    ('eq', "Eq(${eqs})Eq",
     ('a',), ('ex',)), ]


eqs = [
    # find a.t, a.t(), a.t(), a.t().c(), a.t(arg)
    # but not a.1(), a.1:
    ('dot',
     r"${{pred}}(\.([a-zA-Z])+${{call}})+",
     ('a',), ('re', 2)),

    ('call', "(?P<call>\(${{dot_arg}}\))?",
     ('part',), ('re',)),

    ('dot_arg', "(?P<arg>\w+)?",
     ('part',), ('re',)),

    # in that br term parts composed from other 'part'
    # that indicated with '${{}}':
    #  'a[i,j,]'
    ('idx', r"${{pred}}\[${ints}\]",
     ('br_left', [True, False, True]), ('re', 4)),
    # r"${{pred}}\[(?P<idx>((\d)+|((\d)+,)+))\]"

    ('func', r"${{pred}}\(${args}",
     ('br_left', [True, False, False]),
     ('re', 6.1)),

    # (-a) or (-(a)):
    ('unary_div', r"(-${args}",
     ('br_left', [True, False, False]),
     ('txt',)),

    ('pow', r"${args}\)\^${{arg_float}}",
     ('br_right', [False, False, True]),
     ('re', 10)),
    # ('pow', r"${args}\^${args_degree}",
    #  ('br_mid', [False, True, False]),
    #  ('re', 10)),

    # sin, abelian, a:
    ('pred', r"(?P<obj>\w+)",
     ('part',), ('re',)),

    ('bdp', r"${{var_bdp}}\(${{arg_time}},${{arg_space_bound}}\)",
     ('a',), ('re', 1)),

    ('arg_space_bound', ("((\\{x,(?P<val_x>${{arg_float}})\\})?"
                         + "(\\{y,(?P<val_y>${{arg_float}})\\})?"
                         + "(\\{z,(?P<val_z>${{arg_float}})\\})?)"),
     ('part',), ('re',)),
    # ('arg_space_bound', r"(\{${{free_var}},${{arg_float}}\})+",
    # ('part',), ('re',)),

    ('var_bdp', r"(?P<val>[${{base_dep_vars}}])",
     ('part',), ('re',)),

    ('diff', r"D\[${{var}},${{arg_space_diff}}\]",
     ('a',), ('re', 0)),

    ('arg_space_diff', ("((\\{x,(?P<val_x>${{arg_int}})\\})?"
                        + "(\\{y,(?P<val_y>${{arg_int}})\\})?"
                        + "(\\{z,(?P<val_z>${{arg_int}})\\})?)"),
     ('part',), ('re',)),
    # ('arg_space_diff',
    #  r"(?P<arg_space_diff>(\{${{free_var}},${{arg_int}}\})+)",
    #  ('part',), ('re',)),

    ('diff_time',
     "(?P<val>[${{base_dep_vars}}](\(${{arg_time}}\))?)\'",
     ('a',), ('re', 5)),

    ('var',
     r"(?P<val>[${{base_dep_vars}}](\(${{arg_time}}\))?)",
     ('a',), ('re', 6)),

    ('arg_time', r"[${{base_time}}](-${{arg_delay}})?",
     ('part',), ('re',)),
    ('arg_delay', r"(?P<delay>${{arg_float}})",
     ('part',), ('re',)),

    ('free_var', r"(?P<free_var>[${{base_indep_vars}}])",
     ('a',), ('re', 7)),

    ('time', r"[${{base_time}}]", ('a',), ('re', 8)),
    ('coeffs', r"[${{base_coeffs}}]", ('a',), ('re', 9)),

    ('arg_float', r"(?:${{float}})", ('part',), ('re',)),
    ('arg_int', r"(?:${{int}})", ('part',), ('re',)),

    ('float', r"\d+\.\d+|\d+", ('a',), ('re', 11)),
    ('int', r"\d+", ('part',), ('re',)),
    
    ('base_dep_vars', r"A-Z",
     ('part',), ('re',)),

    ('base_indep_vars', r"x-z",
     ('part',), ('re',)),

    ('base_time', r"t",
     ('part',), ('re',)),

    ('base_coeffs', r"a-s|u-w",
     ('part',), ('re',)),

    ('add', r"${something}+${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('mul', r"${something}*${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('sub', r"${something}-${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('div', r"${something}/${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),
    
    ('eq', r"${something}=${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('eq_bool', r"${something}==${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('uneq', r"${something}!=${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('le', r"${something}<=${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('lt', r"${something}<${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('ge', r"${something}>=${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),

    ('gt', r"${something}>${something}",
     ('br_mid', [False, True, False]),
     ('txt',)),
]


