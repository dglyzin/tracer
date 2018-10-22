class DiffSympy():
    
    def make_diff_pattern(self, var, free_vars):
        out = "diff(%s," % (var)
        # out = "sympy.diff(%s," % (var)
        for free_var in free_vars:
            order = free_vars[free_var]
            out += "%s, %s" % (free_var, order)
        out += ")"
        return(out)
