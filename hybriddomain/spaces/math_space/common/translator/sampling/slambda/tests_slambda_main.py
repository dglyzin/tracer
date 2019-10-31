# parser$ python3 -m translator.sampling.slambda.tests_slambda_main
from translator.sampling.slambda import slambda_main as sm

from translator.sampling.slambda.data.stable import stable_fixed
from translator.sampling.slambda.data.stable import stable
from translator.tree.tests_map import test

subgroup_idd = "['s', 1, 0, 0]"
abelian_idd = "['s', 1, 1, 0]"


# create value entry:
test_ventries = [

    # both H and G are given
    # => just check target proposal:
    {"H": ("(2,4)(3,5)",),
     "G": ("(2,4)(3,5)", "(2,5,4,3)"),
     "idd": str(["se"]), "successors_count": 0},

    # G is not given
    # => must be generating during sampling
    {"H": ("(2,3)(4,5)",),

     # subgroup_idd: True, abelian_idd: True,

     "idd": str(["s"]), "successors_count": 0},

    # H is not ginven
    # => must be generating during sampling
    {"G": ("(1,2)(3,5)", "(1,5,2,3)"),

     # subgroup_idd: True, abelian_idd: True,

     "idd": str(["s"]), "successors_count": 0},
    {"G": ("(1,4)(2,3)", "(1,3)(2,4)"),
     abelian_idd: True, subgroup_idd: True,
     "idd": str(["s"]), "successors_count": 0},
    
    {abelian_idd: True, subgroup_idd: True,
     "idd": str(["s"]), "successors_count": 0}
]


def test_slambda_main(proposal_id=22, init_ventry_id=3):
    mid_terms = ["clause_where", "clause_for", "clause_into",
                 "def_0", "in_0",
                 "if", "if_only", "if_def",
                 "clause_or", "conj"]
    vars_terms = ["set", "var"]
    init_ventry = test_ventries[init_ventry_id]
    parsed_net = test("cs", proposal_id)

    sampler = sm.ValTableSampling(parsed_net, init_ventry,
                                  stable, stable_fixed,
                                  mid_terms, vars_terms)
    out = sampler.run()
    print("\nsampling json (for cy) result:")
    print(out)
    
    print("\nsampling successors:")
    print(sampler.successes)
    

if __name__ == "__main__":

    print("target proposal:")
    print("abelian(G) \\and subgroup(H, G,) => abelian(H)")
    test_slambda_main(proposal_id=22, init_ventry_id=4)
