from translator.tokenizer.io.server.server_handlers_base import Handlers


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
