import gens.hs.tests.tests_1d_dom as ts
import gens.hs.arrays_filler.filler_main as fm


def test_1d():
    m = ts.get_model_for_tests()
    nAn, fM = ts.test_domain_1d()
    fr = fm.Filler(m, fM)
    fr.fill_arrays()
    return(fr)
