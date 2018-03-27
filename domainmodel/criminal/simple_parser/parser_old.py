def parse(sent="U'=a+U*U*V-(b+1)*U+c*D[U,{x,2}]"):
    try:
        ''' For term "V(t-1.5,{x,1.3})" '''

        # 1.5 or 1:
        term_float = r"\d\.\d|\d"

        term_delay = r"(?P<delay>%s)" % (term_float)
        # t-1.5
        arg_time = r"[t]-%s" % (term_delay)

        # (?P<val_x>1.5)
        term_val = lambda x: r"(?P<val_%s>%s)" % (x, term_float)

        # pointer to term with x (?P=val_x)
        term_val_pointer = lambda x: r"(?P=val_%s>)" % (x)

        # x, 1.5 or y, 1.3
        # >>> re.search(arg_space("x"),"x,1.5").group()
        # 'x,1.5'
        arg_space = lambda x: r"%s(,%s)?" % (x, term_val(x))

        # >>> re.search(args_space, "x,1.5").group()
        # 'x,1.5'
        args_space = ("("
                      +reduce(lambda x, acc: acc+"|"+x,
                              [arg_space(x) for x in indep_vars],
                              "")
                      +")")

        # >>> re.search(bound_delay_point, "V(t-1.1,{x,1.3})").group()
        # 'V(t-1.1,{x,1.3})'
        bound_delay_point = r"^[%s]\(%s,\{%s\}\)" % (dep_vars, arg_time, args_space)
        res=re.search(bound_delay_point,
                      "V(t-1.5,{x,1.3})") 
    except:
        pass
