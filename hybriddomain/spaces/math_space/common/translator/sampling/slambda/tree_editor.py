from translator.replacer.net_replacer import NetGen

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.tester.gen_1d')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('tree_editor')
logger.setLevel(level=log_level)


class TreeEditor(NetGen):
    
    '''Set ``node["data"]["slambda"]`` attribute

    with vtname value, representing ``vtable_name`` of
    node (which is either ``node[name]`` or it ``node[idd]``,
    depending on existence of ``node[name]`` in ``vars_terms``.

    with args value, representing ``arg_node["data"]["slambda"]["name"]``
    of node.args.
    This attribute will be used in choosing of node's generator
    signature.
    Order of args must be same as in stable.

    with vsname value, representing ``stable_name`` of node
    (which is always is name (in difference with vtname))
    Example:

    {'slambda':
     {'args': ['H', 'G', "['s', 1, 0, 0]"], 'name': "['s', 1, 0, 0]"}
    
    You can see from this example that names of some terms is, in fact,
    it's idd. It is because of some predicates ("subgroup", for example),
    can appeare several times in one proposal.
    
    But all global variables (like "H" and "G" in this example) must be
    same in whole proposal.

    TODO: generalize net methods.
    '''
    
    def get_terms_gen_cls(self):
        return(None)

    def get_terms_br_gen_cls(self):
        return(None)

    def set_mid_terms(self, mid_terms):
        self.mid_terms = mid_terms

    def set_vars_terms(self, vars_terms):
        self.vars_terms = vars_terms

    def set_stable_names(self, stable_names):
        self.stable_names = stable_names

    def __call__(self, node_idd):
        
        '''Set up node value_table name and args
        in node["slambda"] attribute and return it,
        if node is appropriate, else return None.
        '''
        
        vt_name = self.get_vt_name(node_idd)
        if node_idd == str(["s", 1]):
            # import pdb; pdb.set_trace()
            pass

        if vt_name is not None:
            self.set_node_args(node_idd)
        return(vt_name)
        
    def get_vt_name(self, node_idd, err=False):
        
        node = self.get_node(node_idd)
        vt_name = None
        if node["name"] == "br":
            vt_name = self.get_node_br_vtable_name(node_idd)
            if vt_name is None:
                vt_name = self.set_node_br_slambda_names(node_idd)
        elif node["name"] == "a" or node["name"] in self.mid_terms:
            # import pdb; pdb.set_trace()
            vt_name = self.get_node_vtable_name(node_idd)
            if vt_name is None:
                vt_name = self.set_node_slambda_names(node_idd)
            # if node_idd == str(["s", 1]):
            #     print(" s")
        if vt_name is None and err:
            print(node)
            raise(BaseException("in current implementation sampling "
                                + "only work when args is either pred "
                                + "or a terms (like X, ...)"))
        return(vt_name)

    def get_node_br_vtable_name(self, node_br_idd):
        
        successes = self.get_successors(node_br_idd)
        left_node_idd = successes[0]
        vt_node = self.get_node_vtable_name(left_node_idd)
        return(vt_node)

    def get_node_vtable_name(self, node_idd):
        node = self.get_node(node_idd)
        if "data" in node:
            data = node["data"]
            if data is not None:
                if "slambda" in data:
                    slambda = data["slambda"]
                    if "vtname" in slambda:
                        return(slambda["vtname"])
        return(None)
    
    def set_node_slambda_names(self, node_idd):

        node = self.get_node(node_idd)
        name = node["name"]
        idd = node_idd

        # FOR mid term:
        if name in self.stable_names:
            if node["data"] is None:
                node["data"] = {}
            node["data"]["slambda"] = {"vtname": idd,
                                       "stname": name}
            return(idd)
        # END FOR

        if node["data"] is None:
            return(None)

        name = node["data"]["term_name"]

        if name in self.vars_terms:
            name = node["data"]["lex_value"]
            node["data"]["slambda"] = {"vtname": name,
                                       "stname": name}
            return(name)
        print("no generator for: ", name)
        return(None)

    def set_node_br_slambda_names(self, node_br_idd):

        successes = self.get_successors(node_br_idd)
        left_node_idd = successes[0]
        args_node_idd = successes[1]

        left_node = self.get_node(left_node_idd)

        # if no data for term (like in case: ()):
        if left_node["data"] is None:
            return(None)
            
        # if alredy exist:
        if "slambda" in left_node["data"]:
            return(left_node["data"]["slambda"])

        name = left_node["data"]["term_name"]
        if name in ("pred", "func"):
            name = left_node["data"]["lex_value"][:-1]
            if name in self.stable_names:
                left_node["data"]["slambda"] = {"vtname": left_node_idd,
                                                "stname": name}
                return(left_node_idd)
            elif name in self.vars_terms:
                left_node["data"]["slambda"] = {"vtname": name,
                                                "stname": name}
                return(name)
            else:
                print("no generator for: ", name)
                return(None)
        else:
            return(None)

    def set_node_args(self, node_idd):
        '''
        todo: for case,  when one of arg is br like (f((a+b), c,))
        If args is br (f() \\and g()): take left_node.vtable_name
        (for f, g),
        else (f(x,y,)): take node.vtable_name
        (for x, y).
        '''
        node = self.get_node(node_idd)
        successes = self.get_successors(node_idd)

        # FOR choosing node_args:
        logger.debug(successes)
        logger.debug(node_idd)
        node_args = successes
        if node["name"] == "br":
            left_node = self.get_node(successes[0])
            if left_node["name"] is None:
                return(None)
            # node_args: br.args.successors:
            node_args = self.get_successors(successes[1])
        elif node["name"] not in self.mid_terms:
            # ["f", "args", ")"]
            return(None)
        # END FOR

        # FOR args:
        _args = []
        for a_node_idd in node_args:
            vt_name = self.get_vt_name(a_node_idd, err=True)
            _args.append(vt_name)
        # END FOR

        # FOR self:
        # import pdb; pdb.set_trace()
        self_vt_name = self.get_vt_name(node_idd, err=True)
        _args.append(self_vt_name)
        # END FOR

        # use f in br: f, args, r:
        if node["name"] == "br":
            left_node = self.get_node(successes[0])
            left_node["data"]["slambda"]["args"] = _args
        else:
            node = self.get_node(node_idd)
            node["data"]["slambda"]["args"] = _args
            
        return(_args)



