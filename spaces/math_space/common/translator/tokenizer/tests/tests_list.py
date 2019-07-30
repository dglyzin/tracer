'''
``tests_list_*`` for tests,
``*_asserted`` for tests result.
Don't forget add one's before
run tests'''


tests_dict_cs = {
    0: ["group(A) \\and abelian(A) => Eq(A = A_1 + ... + A_n)Eq"],
    1: ['group(A) \\and abelian(A) \\and finite(A) => sum_of_prime(A)'],
    2: ['(group(A) \\and abelian(A) \\and finite(A)) => sum_of_prime(A)'],

    3: ["group(A_i) \\where(A_i:(order(A_i, p,) \\and prime(p)))"],
    4: ["group(A_i) \\where A_i: order(A_i, p,) \\and prime(p)"],

    5: ["bilinear(f)=>Eq(f(x,y,)=g(x,y,)+h(x,y,))Eq"
        + "\\where (g: simmetric(g)) \\and (h: simplectic(h))"],

    6: ['(\\for_all x) \\in X: Eq(x(t-1.0) == y)Eq'],
    7: ['(\\for_all x) \\in (X: Eq(x(t-1.0) == y)Eq)'],
    8: ['((\\for_all x) \\in X): Eq(x(t-1.0) == y)Eq'],
    9: ['(\\for_all x) \\in X'],

    10: ['(((\\for_all x) \\in X: Eq(x(t-1.0) == y)Eq)',
         '\\and ((\\for_all y) \\in Y: Eq(y == z)Eq)',
         ')\\into group(x) \\and group(Y)'],

    11: ["(\\for_all x \\in X: group(A) \\and abelian(A) "
         + "\\and finite(A) => sum_of_prime(A))"],

    12: ["bilinear_form(f) => ((\\exist e1, e2, e3,):"
         + " Eq(g(x)=a0*x0^2+a1*x1^2+a2*x2^2)Eq)"],

    13: ["(\\exist e1, e2, e3,):"
         + " Eq(g(x)=a0*x0^2+a1*x1^2+a2*x2^2)Eq \\where g: map(f, g,)"],

    14: ["(\\exist e1, e2, e3,):"
         + " (Eq(g(x)=a0*x0^2+a1*x1^2+a2*x2^2)Eq \\where g: map(f, g,))"],

    15: ["Let(x: x \\in X, g: abelian(g) in:",
         "group(x) \\and subgroup(x, g,) => abelian(x)" + ",)"],
    16: ["Let(F: finite_field(F), E: finite_field(E),"
         + " G: galois_group(G, E, F,) in:"
         + " Eq([E:F]==k)Eq => is_cyclic(G) \\and order(G, k,),)"],
    17: ["Let(F: finite_field(F), E: finite_field(E),"
         + " G: galois_group(G, E, F,) in:"
         + " (\\exist k): Eq([E:F]==k)Eq"
         + " => is_cyclic(G) \\and order(G, k,),)"],
    18: ["Let(F: finite_field(F), E: finite_field(E),"
         + " G: galois_group(G, E, F,) in:"
         + " (\\exist k : Eq([E:F]==k)Eq"
         + " => is_cyclic(G) \\and order(G, k,)),)"],

    19: ["Let(G: group(G) in: abelian(G)=>commutative(G),"
         + " commutative(G)=>abelian(G),)"],

    # tests for misunderstanding
    # ["\\in", "("] as ["\\", "f"]:
    20: ["y \\in (Y)"],
    21: ["A \\and (B)"],
    22: ["abelian(G) \\and subgroup(H, G,) => abelian(H)"]}


cs_asserted = {
    0: ['f(', 'a', ')', 'conj', 'f(', 'a', ')', 'if', 'a'],
    1: ['f(', 'a', ')', 'conj', 'f(', 'a', ')',
        'conj', 'f(', 'a', ')', 'if', 'f(', 'a', ')'],
    2: ['(', 'f(', 'a', ')', 'conj', 'f(', 'a', ')',
        'conj', 'f(', 'a', ')', ')',
        'if', 'f(', 'a', ')'],
    3: ['f(', 'a', ')', 'clause_where', '(', 'a',
        'def_0', '(', 'f(', 'a', ',', 'a', ',', ')',
        'conj', 'f(', 'a', ')', ')', ')'],
    4: ['f(', 'a', ')', 'clause_where', 'a',
        'def_0', 'f(', 'a', ',', 'a', ',', ')',
        'conj', 'f(', 'a', ')'],

    5: ['f(', 'a', ')', 'if', 'a', 'clause_where', '(', 'a',
        'def_0', 'f(', 'a', ')', ')',
        'conj', '(', 'a', 'def_0', 'f(', 'a', ')', ')'],

    6: ['f(', 'a', ')', 'in_0', 'a', 'def_0', 'a'],
    7: ['f(', 'a', ')', 'in_0', '(', 'a', 'def_0', 'a', ')'],

    8: ['(', 'f(', 'a', ')', 'in_0', 'a', ')', 'def_0', 'a'],

    9: ['f(', 'a', ')', 'in_0', 'a'],

    10: ['(', '(', 'f(', 'a', ')', 'in_0', 'a', 'def_0', 'a', ')',
         'conj', '(', 'f(', 'a', ')', 'in_0', 'a', 'def_0', 'a', ')', ')',
         'clause_into', 'f(', 'a', ')', 'conj', 'f(', 'a', ')'],

    11: ['f(', 'a', 'in_0', 'a', 'def_0', 'f(', 'a', ')',
         'conj', 'f(', 'a', ')', 'conj', 'f(', 'a', ')',
         'if', 'f(', 'a', ')', ')'],
    12: ['f(', 'a', ')', 'if', '(', 'f(', 'a', ',', 'a', ',', 'a', ',', ')',
         'def_0', 'a', ')'],
    13: ['f(', 'a', ',', 'a', ',', 'a', ',', ')', 'def_0', 'a',
         'clause_where', 'a', 'def_0', 'f(', 'a', ',', 'a', ',', ')'],
    14: ['f(', 'a', ',', 'a', ',', 'a', ',', ')',
         'def_0', '(', 'a', 'clause_where', 'a',
         'def_0', 'f(', 'a', ',', 'a', ',', ')', ')'],
    15: ['f(', 'a', 'def_0', 'a', 'in_0', 'a', ',', 'a',
         'def_0', 'f(', 'a', ')', ',', 'f(', 'a', ')',
         'conj', 'f(', 'a', ',', 'a', ',', ')',
         'if', 'f(', 'a', ')', ',', ')'],
    16: ['f(', 'a', 'def_0', 'f(', 'a', ')', ',', 'a',
         'def_0', 'f(', 'a', ')', ',', 'a',
         'def_0', 'f(', 'a', ',', 'a', ',', 'a', ',', ')',
         ',', 'a', 'if', 'f(', 'a', ')',
         'conj', 'f(', 'a', ',', 'a', ',', ')', ',', ')'],
    17: ['f(', 'a', 'def_0', 'f(', 'a', ')', ',', 'a',
         'def_0', 'f(', 'a', ')', ',', 'a',
         'def_0', 'f(', 'a', ',', 'a', ',', 'a', ',', ')',
         ',', 'f(', 'a', ')', 'def_0', 'a', 'if', 'f(', 'a', ')',
         'conj', 'f(', 'a', ',', 'a', ',', ')', ',', ')'],
    18: ['f(', 'a', 'def_0', 'f(', 'a', ')', ',', 'a',
         'def_0', 'f(', 'a', ')', ',', 'a',
         'def_0', 'f(', 'a', ',', 'a', ',', 'a', ',', ')',
         ',', 'f(', 'a', 'def_0', 'a', 'if', 'f(', 'a', ')',
         'conj', 'f(', 'a', ',', 'a', ',', ')', ')', ',', ')'],
    19: ['f(', 'a', 'def_0', 'f(', 'a', ')', ',', 'f(', 'a', ')',
         'if', 'f(', 'a', ')', ',', 'f(', 'a', ')',
         'if', 'f(', 'a', ')', ',', ')'],
    20: ['a', 'in_0', '(', 'a', ')'],
    21: ['a', 'conj', '(', 'a', ')'],
    22: []}


tests_dict_eqs = {
    0: ["a[i,j,] = a[j,i,]"],
    1: ["a.transpose().conjugate()"],
    2: ["a.t(p).s()"],
    3: ["a.t.r()"],
    4: ["a.t().s()"],
    5: ["a.t(s)"],
    6: ["a.t() = a"],
    7: ['x(t-1.0) == y'],
    8: ['y == z'],
    9: ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])"],
    10: ["f(x, y,)*t"],
    11: ["U'=a+U+U*U*V-(b+1)*U+c*D[U,{x,2}]"],
    12: ["U"],
    13: ["U'=2.0 - V"],
    14: ["cos(U-c*D[U,{x,2}])"],

    15: ["(V(t-1.1, {x, 0.7}{y, 0.7}))^(3)"],
    16: ["U'=a*(sin(a+b)+(U)^(3))"],
    17: ["a^3"],

    18: ["((-V)+U)"],
    19: ["(-(V+U))"],
    20: ["U'=(-(U(t-1.1)+V))"],
    21: ["U'=((-U(t-1.1))+V)"],
    22: ["U'=(-U(t-1.1))+V"],

    23: ["f(x, y,)+g(y,z,)+h(x,z,)"],
    24: ["exp(t)"],
    25: ["(U(t, {x, 0.7}{y, 0.3}))"]}


eqs_asserted = {
    0: ['f(', 'a', ',', 'a', ',', ')',
        'eq', 'f(', 'a', ',', 'a', ',', ')'],
    1: ['a'],
    2: ['a'],
    3: ['a'],
    4: ['a'],
    5: ['a'],
    6: ['a', 'eq', 'a'],
    7: ['f(', 'a', 'sub', 'a', ')', 'eq_bool', 'a'],
    8: ['a', 'eq_bool', 'a'],
    9: ['a', 'eq', 'a', 'mul', '(', 'a', 'add', 'a', ')'],
    10: ['f(', 'a', ',', 'a', ',', ')', 'mul', 'a'],
    11: ['a', 'eq', 'a', 'add', 'a', 'add', 'a',
         'mul', 'a', 'mul', 'a',
         'sub', '(', 'a', 'add', 'a', ')',
         'mul', 'a', 'add', 'a', 'mul', 'a'],
    12: ['a'],
    13: ['a', 'eq', 'a', 'sub', 'a'],
    14: ['f(', 'a', 'sub', 'a', 'mul', 'a', ')'],
    15: ['(', 'a', ')', 'pow', '(', 'a', ')'],
    16: ['a', 'eq', 'a', 'mul', '(', 'f(', 'a', 'add', 'a', ')',
         'add', '(', 'a', ')', 'pow', '(', 'a', ')', ')'],
    17: ['a', 'pow', 'a'],

    18: ['(', 'f(', 'a', ')', 'add', 'a', ')'],
    19: ['f(', '(', 'a', 'add', 'a', ')', ')'],
    20: ['a', 'eq', 'f(', '(', 'a', 'add', 'a', ')', ')'],
    21: ['a', 'eq', '(', 'f(', 'a', ')', 'add', 'a', ')'],
    22: ['a', 'eq', 'f(', 'a', ')', 'add', 'a'],

    23: ['f(', 'a', ',', 'a', ',', ')',
         'add', 'f(', 'a', ',', 'a', ',', ')',
         'add', 'f(', 'a', ',', 'a', ',', ')'],

    24: ['f(', 'a', ')'],
    25: ['a']}
