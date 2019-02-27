from gui.web.server.server_handlers_base import Handlers
import json

from translator.tokenizer.patterns.patterns_list.tests.dialects import cs, eqs

from translator.grammar.grammars import get_fmw
from translator.main.parser_general import ParserGeneral
from translator.sampling.vars.vars_extractor import Extractor
import translator.sampling.vars.vars_maps as vms

from functools import reduce


class DialectHandlers(Handlers):

    def __init__(self, model):
        
        Handlers.__init__(self, model)

        self.create_dialect_handlers()
        # self.create_dialect_login_handlers()

    def create_dialect_handlers(self):
        
        TableHandler = self.TableHandler
        model = self.model

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

                data = self.parse(data_json["dialect"], [data_json["text"]])
                print("\ndata_to_send:")
                print(data)

                # data = {"lex": "hello from lex", "net": "hello from net"}
                # END FOR
                
                # send back new data:
                response = data  # {"": data_json}
                self.write(json.dumps(response))

            def parse(self, dialect_name, sent_list):
                
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
                elif dialect_name == "cs":
                    grammar_fmw = get_fmw(ms=[["clause_where", "clause_for",
                                               "clause_into"],
                                              "def_0", "in_0",
                                              ["if", "if_only", "if_def"],
                                              "clause_or", "conj"])

                # choice patterns for dialect:
                if dialect_name == "eqs":
                    dialect_patterns = eqs
                elif dialect_name == "cs":
                    dialect_patterns = cs

                # choice ops for dialect:
                if dialect_name == "eqs":
                    node_data = {"ops": ['add', 'sub', 'mul', 'div', 'eq', ]}

                elif dialect_name == "cs":
                    node_data = {"ops": ["clause_where", "clause_for",
                                         "clause_into",
                                         "def_0", "in_0",
                                         "if", "if_only", "if_def",
                                         "clause_or", "conj"]}

                parser = ParserGeneral(dialect_patterns, grammar_fmw,
                                       node_data)
                parser.parse(sent_list)

                vars_extractor = Extractor(dialect_name)
                net_vars = vms.get_args(str(["s"]), parser.net_out,
                                        vars_extractor)

                print("\nget_args:")
                print(net_vars)
                # print('D.node[str(["s"])]["vars"]')
                # print(D.node[str(["s"])]["vars"])
                if dialect_name == "eqs":
                    vms.subs(parser.net_out, net_vars, a=7, c=8)
                elif dialect_name == "cs":
                    vms.subs(parser.net_out, net_vars, G="s(3)")

                # generate json out again:
                json_out = parser.net_to_json(parser.net_out)
                print("\nparser.json_out:")
                print(parser.json_out)

                # print("\nparser.json_out:")
                # print(parser.json_out)
                return({"lex": reduce(lambda acc, x: acc + " " + str(x),
                                      parser.lex_out, ""),
                        "net": parser.json_out,
                        "vars": net_vars})

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
                self.render("index_net.html", username="default")
                # self.redirect("/login")

        self.NetHandler = NetHandler

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
