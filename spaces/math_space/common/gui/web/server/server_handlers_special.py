from gui.web.server.server_handlers_base import Handlers
import json

from translator.tokenizer.patterns.patterns_list.tests.dialects import cs, eqs
from translator.grammar.grammars import get_fmw

from translator.main.parser_general import ParserGeneral
from env.equation_net.equation import Equation
from env.equation.data.terms.output.cpp.postproc import delay_postproc
from env.clause.clause_main import Clause

from translator.sampling.vars.vars_extractor import Extractor
import translator.sampling.vars.vars_maps as vms

from translator.sampling.slambda import slambda_main as sm
from translator.sampling.slambda.data.stable import stable_fixed
from translator.sampling.slambda.data.stable import stable

from functools import reduce


class DialectHandlers(Handlers):

    def __init__(self, model):
        
        Handlers.__init__(self, model)

        self.create_dialect_handlers()
        # self.create_dialect_login_handlers()

    def get_parser_data(self, dialect_name):
        if dialect_name == "eqs":
            self.equation.parser.show_patterns()
        elif dialect_name == "cs":
            self.clause.parser.show_patterns()

    def create_dialect_handlers(self):
    
        # self.path_cs = "env/clause/data/terms/input/demo_dialect.db"
        # self.path_eqs = "env/equation_net/data/terms/input/demo_dialect.db"

        TableHandler = self.TableHandler
        model = self.model
        global_self = self
        
        # FOR parsers (for get_parser_data in other handlers besides parser):
        
        global_self.equation = Equation("2+2=4", db=global_self.model)
        global_self.clause = Clause("paralelogram(A) \\and romb(A) => square(A)",
                                    db=global_self.model)
        # END FOR

        # FOR replacers:
        global_self.replacer_sources = {}
        # END FOR

        # FOR sampler:
        mid_terms = ["clause_where", "clause_for", "clause_into",
                     "def_0", "in_0",
                     "if", "if_only", "if_def",
                     "clause_or", "conj"]
        vars_terms = ["set", "var"]

        self.sampler = sm.ValTableSampling(None, None,
                                           stable, stable_fixed,
                                           mid_terms, vars_terms)
        # END FOR

        class DialectTableHandler(TableHandler):

            def update_action(self, data: dict)->dict:

                '''Method for post'''

                for entry in data:
                    selected = model.select_pattern(entry["term_name"])
                    
                    if selected.count == 0:
                        model.add_pattern(dict([(key, entry[key])
                                                for key in entry
                                                if key != "id"]))
                    elif selected.count == 1:
                        model.edit_pattern(entry["term_name"],
                                           dict([(key, entry[key])
                                                 for key in entry
                                                 if key != "id"]))
                    else:
                        raise(BaseException("Too many elements with"
                                            + " same term_name in table"))

                data = model.show_all_entries()

                # delete entries, not contained in data
                # for entry in data[]:
                    
                return(data)

            def delete_action(self, data: dict)->dict:

                '''Method for post'''

                for entry in data:
                    model.del_pattern(entry["term_name"])

                data = model.show_all_entries()
                    
                return(data)

            def load_table(self):

                '''Method for get'''

                data = model.show_all_entries()
                return(data)
                '''
                return({'table':
                        [{"id": 0, "ptype:": "Th", "name": "Th_1",
                          "kernel": "first theorem", "kop": ""},
                         {"id": 1, "ptype:": "Def", "name": "Def_1",
                          "kernel": "first def", "kop": ""}]})
                '''

        self.DialectTableHandler = DialectTableHandler

        
        class NetHandlerParsing(self.BaseHandler):
            # @tornado.web.authenticated
            def post(self):
                
                '''Get data, define what to do (delete/update)
                return remained.'''

                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
           
                print("\nFROM NetHandlerParsing.post")
                print("\ndata_json_recived:")
                print(data_json)
                
                # FOR data update:

                global_self.get_parser_data(data_json["dialect"])

                data = self.parse(data_json["dialect"], [data_json["text"]],
                                  data_json["params"])
                print("\ndata_to_send:")
                print(data)

                # data = {"lex": "hello from lex", "net": "hello from net"}
                # END FOR
                
                # send back new data:
                response = data  # {"": data_json}
                self.write(json.dumps(response))

            def parse(self, dialect_name, sent_list, params):
                
                '''Parse data from client with use of ParserGeneral.
                
                Inputs:
                
                - ``dialect_name`` -- either "eqs" or "cs". Will be
                used for both lex pattern and grammar_fmw choicing.
                
                - ``sent_list`` list< containing one sent to parse.

                Outputs:
                
                out["lex"] is result of lex step.
                out["net"] serializable net data.
                '''

                # choice grammar for dialect:
                if dialect_name == "eqs":
                    
                    # in case it was chenged:
                    global_self.model.change_dialect_db(dialect_name)

                    # parse and save:
                    eq = Equation(sent_list[0], db=global_self.model)
                    eq.parser.parse()
                    self.equation = eq
            
                    # FOR params:
                    eq.replacer.cpp.editor.set_default()
                    print("params")
                    print(params)

                    eq.replacer.cpp.editor.set_dim(dim=int(params["dim"]))
                    eq.replacer.cpp.editor.set_blockNumber(blockNumber=int(params["blockNumber"]))

                    vidxs = eval(params["vars_idxs"])
                    eq.replacer.cpp.editor.set_vars_indexes(vars_to_indexes=vidxs)

                    coeffs = eval(params["coeffs"])
                    eq.replacer.cpp.editor.set_coeffs_indexes(coeffs_to_indexes=coeffs)

                    params["btype"] = int(params["btype"])
                    params["side"] = int(params["side"])
                    params["vertex_sides"] = eval(params["vertex_sides"])
                    params["firstIndex"] = int(params["firstIndex"])
                    params["secondIndexSTR"] = int(params["secondIndexSTR"])
                    eq.replacer.cpp.editor.set_diff_type(**params)
                    shape = eval(params["shape"])
                    eq.replacer.cpp.editor.set_shape(shape=shape)
                    # END FOR

                    # because we don't use system here,
                    # delays raplacment complying manualy:
                    eq.replacer.cpp.make_cpp()
                    nodes = [[node for node in eq.get_all_nodes()]]
                    replacers = [eq.replacer.cpp.gen]
                    delay_postproc(replacers, nodes)

                    eq.replacer.sympy.make_sympy()

                    net_out = eq.net_out
                    lex_out = eq.lex_out

                elif dialect_name == "cs":
                    parser = self.parse_cs(sent_list)
                    net_out = parser.net_out

                    # for vtable:
                    global_self.sampler.set_parsed_net(net_out)
                    net_out, nodes_idds = global_self.sampler.editor_step()
                    vtable_skeleton = global_self.sampler.get_vtable_skeleton(nodes_idds)
                    
                    # lex_out = parser.parsers["hol"].lex_out
                    lex_out = parser.lex_out
                    
                vars_extractor = Extractor(dialect_name)
                net_vars = vms.get_args(str(["s"]), net_out,
                                        vars_extractor)

                print("\nget_args:")
                print(net_vars)
                # print('D.node[str(["s"])]["vars"]')
                # print(D.node[str(["s"])]["vars"])
                if dialect_name == "eqs":
                    vms.subs(net_out, net_vars, a=7, c=8)
                elif dialect_name == "cs":
                    vms.subs(net_out, net_vars, G="s(3)")

                # generate json out again:
                if dialect_name == "eqs":
                    json_out = eq.json_out
                elif dialect_name == "cs":
                    json_out = parser.json_out
                print("\nparser.json_out:")
                print(json_out)

                # print("\nparser.json_out:")
                # print(parser.json_out)
                out = {"lex": reduce(lambda acc, x: acc + " " + str(x),
                                     lex_out, ""),
                       "net": json_out,
                       "vars": net_vars}

                # add replacer data:
                if dialect_name == "eqs":
                    out["eq_cpp"] = eq.replacer.cpp.get_cpp()
                    out["eq_sympy"] = eq.eq_sympy
                
                out["slambda"] = {}
                # add slambda data:
                if dialect_name == "cs":
                    out["slambda"]["vtable_skeleton"] = vtable_skeleton
                return(out)

            def parse_cs(self, sent_list):
                global_self.model.change_dialect_db("cs")

                '''
                dialect_patterns = global_self.model.get_entries_to_list()
                # dialect_patterns = cs

                grammar_fmw = get_fmw(ms=[["clause_where", "clause_for",
                                           "clause_into"],
                                          "def_0", "in_0",
                                          ["if", "if_only", "if_def"],
                                          "clause_or", "conj"])
                                
                node_data = {"ops": ["clause_where", "clause_for",
                                     "clause_into",
                                     "def_0", "in_0",
                                     "if", "if_only", "if_def",
                                     "clause_or", "conj"]}

                parser = ParserGeneral(dialect_patterns, grammar_fmw,
                                       node_data)
                '''
                clause = Clause(sent_list[0], db=global_self.model)
                clause.parser.parse()
                self.clause = clause
                return(clause)

        self.NetHandlerParsing = NetHandlerParsing

        class NetHandler(self.BaseHandler):
            # @tornado.web.authenticated
            def get(self):
                print("FROM NetHandler.get")
                print("self.current_user")
                print(self.current_user)
                # try:
                #     name = tornado.escape.xhtml_escape(self.current_user)
                #     self.render("index_net.html", title="", username=name)
                # except TypeError:
                print("self.current_user is None")
                # TODO: users methods
                self.render("index_net.htm", username="default")
                # self.redirect("/login")

        self.NetHandler = NetHandler

        class SamplingHandler(self.NetHandlerParsing):

            # @tornado.web.authenticated
            def post(self):
                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
           
                print("\nFROM SamplingHandler.post")
                print("\ndata_json_recived:")
                print(data_json)
                
                # FOR data update:
                mode = data_json["mode"]
                if mode == "parse":
                    global_self.sent_list = [data_json["text"]]
                    data = self.parse(data_json["dialect"], [data_json["text"]],
                                      data_json["params"])
                    
                    stable = global_self.sampler.stable
                    stable_send = {}
                    for entry_key in stable:
                        stable_send[entry_key] = [str(sign)
                                                  for sign in stable[entry_key]]
                    data["slambda"]["stable"] = stable_send
                    
                elif mode == "sampling":
                    print("data_json")
                    print(data_json)

                    # FOR reinit net_out and nodes_idds:
                    parser = self.parse_cs(global_self.sent_list)
                    net_out = parser.net_out
                    global_self.sampler.set_parsed_net(net_out)
                    net_out, nodes_idds = global_self.sampler.editor_step()
                    # END FOR

                    # data = self.run_sampling(data_json[""])
                    vtnames = data_json["vtnames"]
                    vtvalues = data_json["vtvalues"]
                    init_ventry = dict([(vtnames[idx], eval(vtvalues[idx]))
                                        if vtvalues[idx] != ""
                                        else (vtnames[idx], None)
                                        for idx in range(len(vtnames))])
                    print("init_ventry:")
                    print(init_ventry)
                    global_self.sampler.set_init_ventry(init_ventry)
                    out = global_self.sampler.run()
                    # print("\nsampling json (for cy) result:")
                    # print(out)
    
                    print("\nsampling successors:")
                    print(global_self.sampler.successes)

                    data = {}
                    # transform values to str:
                    successors = [dict([(idx, str(successor[idx]))
                                        for idx in successor])
                                  for successor in global_self.sampler.successes]
                    data["successors"] = successors
                    data["vesnet"] = out
                else:
                    print("unknown mode")
                # END FOR

                # send back new data:
                # print("\ndata_to_send:")
                # print(data)
                response = data  # {"": data_json}
                self.write(json.dumps(response))

            # @tornado.web.authenticated
            def get(self):

                print("FROM SamplingHandler.get")
                print("self.current_user")
                print(self.current_user)
                # try:
                #     name = tornado.escape.xhtml_escape(self.current_user)
                #     self.render("index_net.html", title="", username=name)
                # except TypeError:
                print("self.current_user is None")
                # TODO: users methods
                self.render("index_sampling.htm", username="default")
                # self.redirect("/login")
                
        self.SamplingHandler = SamplingHandler

        class SamplingDeskHandler(self.BaseHandler):
            # @tornado.web.authenticated
            def get(self):
                print("FROM SamplingDeskHandler.get")
                print("self.current_user")
                print(self.current_user)
                # try:
                #     name = tornado.escape.xhtml_escape(self.current_user)
                #     self.render("index_net.html", title="", username=name)
                # except TypeError:
                print("self.current_user is None")
                # TODO: users methods
                self.render("index_sampling_desk.htm", username="default")
                # self.redirect("/login")

        self.SamplingDeskHandler = SamplingDeskHandler

        class ReplacerHandler(self.BaseHandler):

            # @tornado.web.authenticated
            def post(self):
                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
           
                print("\nFROM ReplacerHandler.post")
                print("\ndata_json_recived:")
                print(data_json)
                
                # FOR data update:
                action = data_json["action"]
                dialect_name = data_json["dialect_name"]

                # like ('br_left', [True, False, False]) |-> True:
                brackets = eval(data_json["brackets"])[0] in ["br_left", "br_right"]
                # print("brackets:")
                # print(brackets)

                term_name = data_json["term_name"]
                replacer = global_self.equation.replacer

                if action == "set":
                    code = data_json["code"]
                    replacer.set_pattern(dialect_name, term_name,
                                         code, brackets)
                    sources = replacer.load_patterns_source(dialect_name, brackets)
                    global_self.replacer_sources[(dialect_name, brackets)] = sources
                    term_source = sources[term_name]

                elif action == "load":
                    # check if alredy loaded:
                    if (dialect_name, brackets) in global_self.replacer_sources:
                        sources = global_self.replacer_sources[(dialect_name, brackets)]
                    else:
                        sources = replacer.load_patterns_source(dialect_name, brackets)
                        global_self.replacer_sources[(dialect_name, brackets)] = sources
                    term_source = sources[term_name]

                elif action == "remove":
                    replacer.remove_patterns(dialect_name, [term_name])
                    sources = replacer.load_patterns_source(dialect_name, brackets)
                    global_self.replacer_sources[(dialect_name, brackets)] = sources
                    term_source = "# term %s removed successfuly\n" % (term_name)
                    term_source += "# check terms list for shure"

                else:
                    print("no such action: %s" % (action))

                print("aveilable_terms:")
                aveilable_terms = list(sources.keys())
                print(list(sources.keys()))
                available_terms_str = " ".join(aveilable_terms)
                if brackets:
                    available_terms_str += " (for brackets only)"
                data = {"source": term_source,
                        "available_terms": available_terms_str}
                # END FOR

                # send back new data:
                # print("\ndata_to_send:")
                # print(data)
                response = data  # {"": data_json}
                self.write(json.dumps(response))

            # @tornado.web.authenticated
            def get(self):
                # not used

                print("FROM ReplacerHandler.get")

                data = {}
                response = data  # {"": data_json}
                self.write(json.dumps(response))
                
        self.ReplacerHandler = ReplacerHandler

        class LexTut0Handler(self.BaseHandler):
            # @tornado.web.authenticated
            def get(self):
                print("FROM LexTut0Handler.get")
                print("self.current_user")
                print(self.current_user)
                # try:
                #     name = tornado.escape.xhtml_escape(self.current_user)
                #     self.render("index_net.html", title="", username=name)
                # except TypeError:
                print("self.current_user is None")
                # TODO: users methods
                self.render("index_tut_replacer.htm", username="default",
                            var="{{var}}", int="{{int}}",
                            base_dep_vars="{{base_dep_vars}}", arg_time="{{arg_time}}")
                # self.redirect("/login")

        self.LexTut0Handler = LexTut0Handler
        
    '''
    def create_dialect_login_handlers(self):
        
        SignUpHandler = self.SignUpHandler
        model = self.model

        class DialectSignUpHandler(SignUpHandler):
            
            def create_user(self, data):

                print("FROM DialectSignUpHandler.create_user")
                res = model.create_new_user(data["table"])
                return(res)

        self.DialectSignUpHandler = DialectSignUpHandler

        SignInHandler = self.SignInHandler
        model = self.model

        class DialectSignInHandler(SignInHandler):
            
            def check_user(self, data):
                
                print("FROM DialectSignInHandler.check_user")
                res = model.check_user(data["table"])
                return(res)

        self.DialectSignInHandler = DialectSignInHandler
    '''
