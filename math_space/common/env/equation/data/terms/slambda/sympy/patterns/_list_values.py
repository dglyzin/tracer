import sympy

terms_gens_value = dict([
    ('+', lambda L, R: L.__add__(R)),
    ('*', lambda L, R: L.__mul__(R)),
    ('-', lambda L, R: R.__add__(-L)),
    ('/', lambda L, R: R.__div__(L)),
    ('=', lambda L, R: sympy.Eq(R, L)),  # ('=', lambda L, R: L.__eq__(R)),
    ('=-', lambda L, R: sympy.Eq(R, -L))  # ('=-', lambda L, R: L.__eq__(-R))
])
