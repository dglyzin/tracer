import tornado
import tornado.ioloop
import tornado.web
# import os
import json


class Handlers():
    def __init__(self):
        
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

        class MainHandler(self.BaseHandler):

            # @tornado.web.authenticated
            def post(self):
                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)

                print("\nFROM ReplacerHandler.post")
                print("\ndata_json_recived:")
                print(data_json)

                # FOR data update:
                img_src = data_json["img"]
                print(img_src)
                data = {"result": "success"}
                # END FOR

                # send back new data:
                # print("\ndata_to_send:")
                # print(data)
                response = data  # {"": data_json}
                self.write(json.dumps(response))

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
                    self.render("index.htm", title="models 2d editor",
                                username="default")
                    # self.redirect("/login")

        self.MainHandler = MainHandler
