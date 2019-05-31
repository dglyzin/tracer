import tornado
import tornado.ioloop
import tornado.web
import os
import json


class Handlers():

    def __init__(self, model):

        self.model = model
        self.create_base_handlers()
        self.create_path_handler()
        self.create_table_handler()
        self.create_login_handlers()

    def create_path_handler(self):

        BaseHandler = self.BaseHandler
        model = self.model
        global_self = self

        class PathHandler(BaseHandler):
            # @tornado.web.authenticated
            def get(self):

                '''Show path from db.'''

                # response = model.getUsers()
                print("FROM PathHandler.get")
                path_eqs = model.get_path_of_dialect_db("eqs")
                path_cs = model.get_path_of_dialect_db("cs")
                listdir_eqs = os.listdir(os.path.dirname(path_eqs))
                listdir_cs = os.listdir(os.path.dirname(path_cs))
                response = {"eqs": {"path": path_eqs, "listdir": listdir_eqs},
                            "cs": {"path": path_cs, "listdir": listdir_cs}}
                print(response)

                self.write(json.dumps(response))

            # @tornado.web.authenticated
            def post(self):
                
                '''Set path to model, then get it from model
                back.
                ``self.equation`` must be implemented in ancestors'''

                data_body = self.request.body
                data_json = json.loads(data_body)
                print("FROM PathHandler.post")
                print(data_json)

                # FOR data update:
                # TODO: set ``self.path_cs``, ``self.path_eqs``
                # with use of dialect key from ``data_json``?
                if "file_name" in data_json:
                    dirname = (os.path
                               .dirname(model
                                        .get_path_of_dialect_db(data_json["dialect_name"])))
                    path = os.path.join(dirname, data_json["file_name"])
                    model.change_path_of_dialect_db(data_json["dialect_name"],
                                                    path)

                    # show patterns:
                    global_self.get_parser_data(data_json["dialect_name"])
                # END FOR

                # send back new data:
                response = {"path": model.path}
                self.write(json.dumps(response))
        self.PathHandler = PathHandler

    def create_table_handler(self):

        BaseHandler = self.BaseHandler

        class TableHandler(BaseHandler):
            # @tornado.web.authenticated
            def get(self):

                '''Show data from db.'''

                # response = model.getUsers()
                print("FROM TableHandler.get")
                response = self.load_table()
                response = {"table": response}
                print(response)

                self.write(json.dumps(response))

            # @tornado.web.authenticated
            def post(self):
                
                '''Get data, define what to do (delete/update)
                return remained.'''

                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
                #model.addUser(data)
                # print(data)
                print("\nFROM TableHandler.post")
                print("\ndata_json:")
                print(data_json)

                # FOR data update:
                if data_json["action"] == "update":
                    # FOR update data
                    data_json = self.update_action(data_json["table"])
                elif data_json["action"] == "delete":
                    data_json = self.delete_action(data_json["table"])
                # END FOR

                # send back new data:
                response = {"table": data_json}
                self.write(json.dumps(response))
                
            def delete_action(self, data: dict)->dict:
                
                print("must be implemented")
                return(None)

            def update_action(self, data: dict):
                
                '''
                Inputs:

                - ``data`` -- data is dict

                Return:
                
                Result must be dict'''

                print("must be implemented")
                
                return(data)

            def load_table(self):

                '''Result must dict'''

                print("must be implemented")

                return({'table':
                        [{"id": 0, "ptype:": "Th", "name": "Th_1",
                          "kernel": "first theorem", "kop": ""},
                         {"id": 1, "ptype:": "Def", "name": "Def_1",
                          "kernel": "first def", "kop": ""}]})
        self.TableHandler = TableHandler

    def create_base_handlers(self):

        class BaseHandler(tornado.web.RequestHandler):
            
            def get_current_user(self):

                '''Redifenition of self.current_user
                cookie with name "username" must be setted
                with use of set_cookie("username", name)
                (in loggin or signup)
                
                # REF: https://www.tornadoweb.org/en/stable/web.html#cookies

                self.current_user name will be checked in
                all method where tornado.web.authenticated
                is used.
                
                security:
                about tornado.web.authenticated
                # REF: https://www.tornadoweb.org/en/stable/guide/
                security.html#user-authentication
                '''

                # return self.get_secure_cookie("username")
                return self.get_cookie("username")
        self.BaseHandler = BaseHandler

        class MainHandler(BaseHandler):
            # @tornado.web.authenticated
            def get(self):
                print("FROM MainHandler.get")
                print("self.current_user")
                print(self.current_user)
                try:
                    name = tornado.escape.xhtml_escape(self.current_user)
                    self.render("index.htm", title="", username=name)
                except TypeError:
                    print("self.current_user is None")
                    # TODO: users methods
                    self.render("index.htm", username="default")
                    # self.redirect("/login")

        self.MainHandler = MainHandler

    def create_login_handlers(self):
        '''
        security:
        about tornado.web.authenticated
        # REF: https://www.tornadoweb.org/en/stable/guide/
        security.html#user-authentication
        '''

        BaseHandler = self.BaseHandler
        TableHandler = self.TableHandler

        model = self.model
        
        class UsersTableHandler(TableHandler):

            def update_action(self, data: dict)->dict:

                '''Method for post'''

                for entry in data:
                    userexist = model.check_user_exist(entry)
                    
                    if not userexist:
                        model.create_new_user(dict([(key, entry[key])
                                                    for key in entry
                                                    if key != "id"]))
                    else:
                        model.edit_user(entry["username"],
                                        dict([(key, entry[key])
                                              for key in entry
                                              if key != "id"]))
                data = model.show_all_entries(table_name="user")
                return(data)

            def delete_action(self, data: dict)->dict:

                '''Method for post'''

                for entry in data:
                    model.del_user(entry["username"])

                data = model.show_all_entries(table_name="user")
                    
                return(data)

            def load_table(self):

                '''Method for get'''

                data = model.show_all_entries(table_name="user")
                return(data)
                '''
                return({'table':
                        [{"id": 0, "ptype:": "Th", "name": "Th_1",
                          "kernel": "first theorem", "kop": ""},
                         {"id": 1, "ptype:": "Def", "name": "Def_1",
                          "kernel": "first def", "kop": ""}]})
                '''

        self.UsersTableHandler = UsersTableHandler

        class SignUpHandler(BaseHandler):
            # @tornado.web.authenticated
            def get(self):

                '''Create Sign up form'''
                '''
                response = model.get_users()
                
                print("\nusers:")
                print(response)
                '''
                print("\nFROM SignUpHandler.get")
                # create form which action point to self.post
                self.write('<html><body><form action="/signup" method="post">'
                           'Name: <input type="text" name="username"><br>'
                           'Pass: <input type="password" name="password"><br>'
                           'Email: <input type="text" name="email"><br>'
                           '<input type="submit" value="Sign up">'
                           '</form></body></html>')
                # self.write(json.dumps(response))

            # @tornado.web.authenticated
            def post(self):
                '''
                Sign up user.
                '''
                print("FROM SignUpHandler.post")
                # data = self.get_argument('users', 'No data received')
                data_body = self.request.body
                data = {"username": self.get_argument("username"),
                        "password": self.get_argument("password"),
                        "email": self.get_argument("email")}
                
                # data_json = json.loads(data_body)
                #model.addUser(data)
                print("data:")
                print(data)

                # FOR update data
                response = self.create_user(data)
                print("response:")
                print(response)
                # response = model.get_users()
                # END FOR

                if response is None:
                    self.write('<html><body>'
                               '<p>Error during user creating</p>'
                               '<form action="/user" method="post">'
                               'Name: <input type="text" name="username"><br>'
                               'Pass: <input type="password" name="password"><br>'
                               'Email: <input type="text" name="email"><br>'
                               '<input type="submit" value="Sign up">'
                               '</form></body></html>')
                else:
                    # set up cookie with "username".
                    # For access to current_user, setted
                    # in MainHandler.get get_current_user method
                    self.set_cookie("username", response)
                    # self.get_argument("username")
                    self.redirect("/login")

                # send back new data:
                # self.write(json.dumps(response))

            def create_user(self, data):

                '''
                Inputs:

                - ``data`` -- in form
                {"username": username,
                 "password": password,
                 "email": email}

                Return:

                - ``res`` - str with ``username`` or ``None``
                If return None, error msg page will be created
                (see self.post above)
                '''
                # print("SignUpHandler.create_user must be implemented")
                res = model.create_new_user(data)
                return(res)
    
        self.SignUpHandler = SignUpHandler

        class SignInHandler(BaseHandler):
            def get(self):
                self.write('<html><body><form action="/login" method="post">'
                           'Name: <input type="text" name="username"><br>'
                           'Pass: <input type="password" name="password"><br>'
                           '<input type="submit" value="Sign in">'
                           '</form></body></html>')

            def post(self):
                print("FROM SignInHandler.post")
                data_body = self.request.body
                print("data_body:")
                print(data_body)
                data = {"username": self.get_argument("username"),
                        "password": self.get_argument("password")}
                # data_json = json.loads(data_body)
                #model.addUser(data)
                print("data:")
                print(data)
                accepted_name = self.check_user(data)
                if accepted_name is None:
                    self.write('<html><body>'
                               '<p>Error to login</p>'
                               '<form action="/login" method="post">'
                               'Name: <input type="text" name="username"><br>'
                               'Pass: <input type="password" name="password"><br>'
                               '<input type="submit" value="Sign in">'
                               '</form></body></html>')
                else:
                    # set up cookie with "username".
                    # For access to current_user, setted
                    # in MainHandler.get get_current_user method
                    self.set_cookie("username", accepted_name)
                    # self.get_argument("username")
                    # self.set_secure_cookie("username",
                    #                         self.get_argument("username"))
                    self.redirect("/")

            def check_user(self, data):
                
                '''
                Inputs:

                - ``data`` -- in form
                {"username": name, "password": password}


                Return:

                - ``res`` - str with user_name or None
                If return None, error msg page will be created
                (see self.post above)'''

                # print("LoginHandler.check_user must be implemented")
                res = model.check_user(data)
                return(res)

        self.SignInHandler = SignInHandler
        
        class LogoutHandler(BaseHandler):
            def get(self):
                self.clear_cookie("user")
                self.redirect("/")
        self.LogoutHandler = LogoutHandler
