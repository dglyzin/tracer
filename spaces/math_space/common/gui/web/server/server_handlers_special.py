from gui.web.server.server_handlers_base import Handlers
import json

from translator.tokenizer.patterns.patterns_list.tests.dialects import cs, eqs
from translator.grammar.grammars import get_fmw

from translator.main.parser_general import ParserGeneral
from env.equation_net.equation import Equation
from env.equation.data.terms.output.cpp.postproc import delay_postproc

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

    def create_dialect_handlers(self):
        
        TableHandler = self.TableHandler
        model = self.model
        global_self = self

        mid_terms = ["clause_where", "clause_for", "clause_into",
                     "def_0", "in_0",
                     "if", "if_only", "if_def",
                     "clause_or", "conj"]
        vars_terms = ["set", "var"]

        self.sampler = sm.ValTableSampling(None, None,
                                           stable, stable_fixed,
                                           mid_terms, vars_terms)

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
                    grammar_fmw = get_fmw()
                    dialect_patterns = eqs
                    node_data = {"ops": ['add', 'sub', 'mul', 'div', 'eq', ]}
                    eq = Equation(sent_list[0])
                    eq.parser.parse()
            
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

                    eq.replacer.cpp.make_cpp()
                    nodes = [[node for node in eq.get_all_nodes()]]
                    replacers = [eq.replacer.cpp.gen]
                    delay_postproc(replacers, nodes)

                    eq.replacer.sympy.make_sympy()

                    net_out = eq.net_out
                    lex_out = eq.parser.parsers["wolfram"].lex_out

                elif dialect_name == "cs":
                    grammar_fmw = get_fmw(ms=[["clause_where", "clause_for",
                                               "clause_into"],
                                              "def_0", "in_0",
                                              ["if", "if_only", "if_def"],
                                              "clause_or", "conj"])
                    dialect_patterns = cs
                    node_data = {"ops": ["clause_where", "clause_for",
                                         "clause_into",
                                         "def_0", "in_0",
                                         "if", "if_only", "if_def",
                                         "clause_or", "conj"]}

                    parser = ParserGeneral(dialect_patterns, grammar_fmw,
                                           node_data)
                    parser.parse(sent_list)
                    net_out = parser.net_out
                    global_self.sampler.set_parsed_net(net_out)
                    net_out, nodes_idds = global_self.sampler.editor_step()
                    vtable_skeleton = global_self.sampler.get_vtable_skeleton(nodes_idds)
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
                    json_out = eq.parser.parsers["wolfram"].net_to_json(net_out)
                elif dialect_name == "cs":
                    json_out = parser.net_to_json(net_out)
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

        class SamplingHandler(self.BaseHandler):
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
                self.render("index_sampling.htm", username="default")
                # self.redirect("/login")

        self.SamplingHandler = SamplingHandler

        class SamplingDeskHandler(self.BaseHandler):
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
                self.render("index_sampling_desk.htm", username="default")
                # self.redirect("/login")

        self.SamplingDeskHandler = SamplingDeskHandler

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
