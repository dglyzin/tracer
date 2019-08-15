import tornado
import tornado.ioloop
import tornado.web
import os
import shutil
import json
import inspect

currentdir = os.path.dirname(os.path
                             .abspath(inspect
                                      .getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
path_to_save = os.path.join(parentdir, "model/data")
tree_file_name = "treemetafile"


class Handlers():
    def __init__(self):
        
        global_self = self

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

                print("\nFROM MainHandler.post")
                print("\ndata_json_recived:")
                print(data_json)

                # FOR data update:
                img_src = data_json["canvas_img"]
                print(img_src)
                data = {"models_id": ["mod0", "mod1", "mod2"]}
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

        class TreeHandler(self.BaseHandler):

            def __init__(self, *args):
                global_self.BaseHandler.__init__(self, *args)
                self.metafile = os.path.join(path_to_save, tree_file_name)

            # @tornado.web.authenticated
            def post(self):
                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
                print("\nFROM TreeHandler.post")
                print("\ndata_json_recived:")
                print(data_json)
                data_input = data_json

                # FOR data update:
                
                data_output = {}
                if (data_input["mode"] == "init"):
                    if os.path.exists(self.metafile) and len(os.listdir()) > 1:
                        with open(self.metafile) as f:
                            data_output["tree"] = json.loads(f.read())
                    else:
                        data_output["tree"] = [
                            {"title": "available", "key": "0", "folder": True,
                             "children": []}]
                        '''
                             "children": [
                                 {"title": "models_editor", "key": "3"},
                                 {"title": "patterns_editor", "key": "4"}
                              ]}]
                        '''
                elif(data_input["mode"] == "load"):
                    
                    node_path = os.path.join(path_to_save,
                                             data_input["node_name"])
                    node_data_file = os.path.join(node_path, "src.json")
                    with open(node_data_file) as f:
                        node_data_src = f.read()
                    data_output["canvas_src"] = node_data_src
                       
                elif(data_input["mode"] == "remove"):
                    node_name = data_input["node_name"]
                    node_path = os.path.join(path_to_save, node_name)
                    
                    # remove not empty dir:
                    shutil.rmtree(node_path)

                    tree_data_src = data_input["tree"]
                    self.update_tree(tree_data_src)
                    
                elif(data_input["mode"] == "add"):
                    node_path = os.path.join(path_to_save,
                                             data_input["node_name"])
                    if os.path.exists(node_path):
                        print("ERROR: path s% already exist" % node_path)
                    else:
                        os.mkdir(node_path)
                        node_data_file = os.path.join(node_path, "src.json")
                        node_img_file = os.path.join(node_path, "img.jpeg")
                        node_data = json.loads(data_input["node_data"])
                        node_data_src = node_data["canvas_source"]
                        node_data_img = node_data["canvas_img"]

                        # save json data:
                        with open(node_data_file, "w") as f:
                            f.write(node_data_src)
                            # f.write(json.dumps(node_data_src,
                            #                    sort_keys=False, indent=4))

                        # save img data:
                        with open(node_img_file, "w") as f:
                            f.write(node_data_img)
                            
                        tree_data_src = data_input["tree"]
                        
                        self.update_tree(tree_data_src)
                        print("done")

                    data_output["result"] = "added"
                
                # img_src = data_json["canvas_img"]
                # print(img_src)
                # data = {"models_id": ["mod0", "mod1", "mod2"]}
                # END FOR
                
                # send back new data:
                # print("\ndata_to_send:")
                # print(data)
                response = data_output  # {"": data_json}
                self.write(json.dumps(response))

            def update_tree(self, tree_data_src):
                    
                with open(self.metafile, "w") as f:
                    f.write(tree_data_src)

            # @tornado.web.authenticated
            def get(self):
                # not used

                print("FROM TreeHandler.get")

                data = {}
                response = data  # {"": data_json}
                self.write(json.dumps(response))
                
        self.TreeHandler = TreeHandler
