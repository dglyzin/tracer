import tornado
import tornado.ioloop
import tornado.web
import os
import shutil
import json
import inspect

from model.model_main import FilesystemDatastore

currentdir = os.path.dirname(os.path
                             .abspath(inspect
                                      .getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)


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

                self.db = FilesystemDatastore()

            # @tornado.web.authenticated
            def post(self):
                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
                print("\nFROM TreeHandler.post")
                print("\ndata_json_recived:")
                print(data_json)
                data_input = data_json
                di = data_input

                # FOR data update:
                
                data_output = {}
                if (data_input["mode"] == "init"):
                    folders, envs = self.db.ls_folder(self.db.data_folder)
                    print("folders+envs:")
                    print(folders+envs)

                    data_output["tree"] = [{
                        "title": "available", "key": "0", "folder": True,
                        "type": "root",
                        "children": [
                            {"title": self.db.models_root_title, "key": "3",
                             "type": "envs_root",
                             "children": folders+envs},
                            {"title": "patterns_editor", "key": "4",
                             "type": "board"}
                        ]}]
                    # children = os.listdir(data_folder)
                    '''
                    if os.path.exists(self.metafile) and len(os.listdir()) > 1:
                        with open(self.metafile) as f:
                            data_output["tree"] = json.loads(f.read())
                    else:
                        data_output["tree"] = [
                            {"title": "available", "key": "0", "folder": True,
                             "children": []}]
                    '''
                elif(data_input["mode"] == "activate"):
                    print("di['node']:")
                    print(di["node"])
                    if di["node"]["type"] == "envs_root":
                        # return folders from data_folder:

                        path = self.db.data_folder
                        folders, envs = self.db.ls_folder(path)
                        data_output["out"] = folders + envs

                    elif di["node"]["type"] == "folder":
                        # return folders inside folder:

                        path = self.db.get_node_full_path(di)
                        folders, envs = self.db.ls_folder(path)
                        data_output["out"] = folders + envs
                    elif di["node"]["type"] == "env":
                        # return contents list of
                        # env folder (if exist):

                        path = self.db.get_node_full_path(di)
                        if self.db.path_exist(path):
                            content = self.db.env_content_list
                            data_output["out"] = (self.db
                                                  .applay_node(content,
                                                               "env_content",
                                                               folder=False))
                        else:
                            raise(BaseException("test path not exist:\n"
                                                + path))
                    elif di["node"]["type"] == "env_content":
                        data_output["out"] = self.db.load_content(di)

                    '''
                    elif(data_input["mode"] == "load"):

                        node_path = os.path.join(data_folder,
                                                 data_input["node_name"])
                        node_data_file = os.path.join(node_path, "src.json")
                        with open(node_data_file) as f:
                            node_data_src = f.read()
                        data_output["canvas_src"] = node_data_src
                    '''
                elif(data_input["mode"] == "remove"):
                    if di["node"]["type"] == "env":
                        path = self.db.get_node_full_path(di)
                    elif di["node"]["type"] == "folder":
                        path = self.db.get_node_full_path(di)
                        sub_folders, sub_envs = self.db.ls_folder(path)
                        if len(sub_folders+sub_envs) > 0:
                            raise(BaseException("folder %s not empty: %s"
                                                % (di["node"]["title"],
                                                   str(sub_folders+sub_envs))))
                    else:
                        raise(BaseException("Cannot remove node with type %s"
                                            % di["node"]["type"]))
                    self.db.rm_node(path)
                    
                elif(data_input["mode"] == "save"):
                    if (di["node"]["type"] == "env_content"):
                        self.db.save_content(di)
                    else:
                        raise(BaseException("cannot save type: %s"
                                            % di["node"]["type"]))

                elif(data_input["mode"] == "add"):
                    
                    if di["parent"]["type"] == "envs_root":
                        # get root path:
                        path = os.path.join(self.db.data_folder,
                                            di["node"]["title"])

                    elif di["parent"]["type"] == "folder":
                        # in that case We have only parent's path
                        # (because node will only been created):
                        parent_path = (self.db
                                       .get_node_full_path(di,
                                                           node_name="parent"))
                        path = os.path.join(parent_path,
                                            di["node"]["title"])
                    else:
                        raise(BaseException("cannot add for type: %s"
                                            % di["node"]["type"]))

                    if self.db.path_exist(path):
                        raise(BaseException("ERROR: path s% already exist"
                                            % path))
                    
                    if di["node"]["type"] == "folder":
                        # for folders and envs_root only:
                        self.db.mk_folder(path)
                    elif(di["node"]["type"] == "env"):
                        self.db.mk_env(path)
                    data_output["result"] = "added"
                elif(data_input["mode"] == "rename"):
                    if di["node"]["type"] not in ["env", "folder"]:
                        raise(BaseException("cannot rename node with type: %s"
                                            % di["node"]["type"]))
                    self.db.rename(di)
                # img_src = data_json["canvas_img"]
                # print(img_src)
                # data = {"models_id": ["mod0", "mod1", "mod2"]}
                # END FOR
                
                # send back new data:
                print("\ndata_to_send:")
                print(data_output)
                
                response = data_output  # {"": data_json}
                self.write(json.dumps(response))

            # @tornado.web.authenticated
            def get(self):
                # not used

                print("FROM TreeHandler.get")

                data = {}
                response = data  # {"": data_json}
                self.write(json.dumps(response))
                
        self.TreeHandler = TreeHandler
