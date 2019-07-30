import random


def func_gen():
    return(str(random.choice(['sin', 'cos'])))


def free_var_gen():
    return(float("%.3f" % random.random()))

    
def coeffs_gen():
    return(float("%.3f" % random.random()))


terms_gens = dict([
    ('func', func_gen),
    ('free_var', free_var_gen),
    ('coeffs', coeffs_gen)])
