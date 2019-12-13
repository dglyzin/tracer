import os
import shutil
import json

from scipy.misc import imread
from scipy.misc import imsave
import base64

data_folder = os.path.join(os.getcwd(), "model/data")
templates_path = os.path.join(os.getcwd(), "model/templates")
tree_file_name = "treemetafile"
print("os.getcwd():")
print(os.getcwd())


class FilesystemDatastore():
    def __init__(self):
        self.data_folder = data_folder
        # root_folder = os.path.dirname(os.getcwd())
        # self.data_folder = os.path.join(root_folder, "model", "data")
        self.models_root_title = "models_envs"
        self.templates_path = templates_path
        self.env_content_list = ["bounds", "centrals",
                                 "initials", "equations"]
        self.env_content_list_for_imgs = ["bounds", "centrals", "initials"]
        self.metafile = os.path.join(data_folder, tree_file_name)

    def rename(self, data_input):
        di = data_input
        path = self.get_parent_full_path(di)
        path_src = os.path.join(path, di["node"]["title"])
        print("path_src:")
        print(path_src)

        path_dst = os.path.join(path, di["node_data"]["title"])
        print("path_dst:")
        print(path_dst)
        if self.path_exist(path_dst):
            raise(BaseException("path_dst alredy exist: %s"
                                % path_dst))
        os.rename(path_src, path_dst)

    def save_content(self, data_input):

        '''save node["node_data"][{"canvas_source"/"canvas_img"}]
        to env folder for
           node["node"]["title"]+_{src.json/img.png}
        name.'''
        
        di = data_input
        if di["node"]["title"] == "equations":
            node_data = di["node"]["node_data"]
            table = node_data["table"]
            parent_path = self.get_parent_full_path(di)  # , node_name="parent"
            print("parent_path:")
            print(parent_path)
            print("table:")
            print(table)
        else:
            parent_path = self.get_parent_full_path(di)  # , node_name="parent"
            node_data_file = os.path.join(parent_path,
                                          di["node"]["title"]+"_src.json")
            print("node_data_file:")
            print(node_data_file)

            node_img_file = os.path.join(parent_path,
                                         di["node"]["title"]+"_img.png")
            print("node_img_file:")
            print(node_img_file)

            node_data = json.loads(data_input["node"]["node_data"])
            print("di[node][node_data][eqs_table]")
            print(node_data["eqs_table"])

            node_data_src = node_data["canvas_source"]
            node_data_img = node_data["canvas_img"]

            # save json data:
            with open(node_data_file, "w") as f:
                f.write(node_data_src)
                # f.write(json.dumps(node_data_src,
                #                    sort_keys=False, indent=4))

            img_orign = node_data_img.split(",")[1]
            print("img_orign:")
            print(img_orign)

            # save img data:
            with open(node_img_file, "wb") as f:
                # imsave(img_orign, node_img_file, format='jpeg')
                f.write(base64.decodebytes(img_orign.encode("utf-8")))
                # f.write(base64.decodebytes(node_data_img.encode("utf-8")))
            img = imread(node_img_file, mode="L")

            print("img array:")
            print(img)

            # tree_data_src = data_input["tree"]

        # self.update_tree(tree_data_src)
        print("done")

    def update_tree(self, tree_data_src):

        with open(self.metafile, "w") as f:
            f.write(tree_data_src)

    def mk_env(self, path):

        '''Create env folder and copy some data
        here from templates folder'''

        print("mk_env:")
        print(path)
        self.mk_folder(path)

        for name in self.env_content_list_for_imgs:
            shutil.copy2(os.path.join(self.templates_path,
                                      name+"_src.json"),
                         path)

    def mk_folder(self, path):
        # os.mkdir(path)
        print("mk_folder path:")
        print(path)
        os.mkdir(path)

    def path_exist(self, path):
        '''model.path_exist'''
        return(os.path.exists(path))

    def rm_node(self, path):
        '''model.remove_node'''
        print("from rm_node:")
        print(path)
        shutil.rmtree(path)
        # tree_data_src = data_input["tree"]
        # self.update_tree(tree_data_src)

    def load_content(self, data_input):

        '''Collect content (like boards, centrals, initials)
        from model_folder/content_src.json file
        for canvas_src.
        This will load env content data
        model.load_content'''

        di = data_input
        content = di["node"]["title"]
        out = {"content_type": content}
        if content == "equations":
            out["table"] = [
                ["U'=a*U+b*U*((U)^2+(V)^2)+c*D[U,{x,2}]\n"
                 + "V'=a*V+b*V*((U)^2+(V)^2)+c*D[V,{x,2}]\n"],
                ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])\n"],
                ["U'= a*(b-U(t-1))*U\n"]
            ]
            out["table"] = 3*out["table"]
        else:
            # this will return /path/to/model:
            model_folder_full_path = self.get_parent_full_path(di)
            content_img_src_data_file = os.path.join(model_folder_full_path,
                                                     content+"_src.json")
            with open(content_img_src_data_file) as f:
                content_img_data_src = f.read()
            out["canvas_src"] = content_img_data_src
        return(out)

    def get_node_full_path(self, data_input, node_name="node"):
        '''Return full path of given node

        - ``node_name`` -- name of node to be used for
        title extraction (either "node" or "parent")'''

        parent_path = self.get_parent_full_path(data_input)
        path = os.path.join(parent_path,
                            data_input[node_name]["title"])
        return(path)

    def get_parent_full_path(self, data_input):
        '''Get full path of parent node (which is parent folder)'''
        di = data_input
        models_root_idx = (di["parents_list"]
                           .index(self.models_root_title))
        local_path = os.path.sep.join(di["parents_list"][models_root_idx+1:])
        parent_full_path = os.path.join(self.data_folder, local_path)
        return(parent_full_path)

    def ls_folder(self, path):
        '''Get only top folders inside path folder.
        And group result at folder / envs where env
        is a folder with .json file contained in.
        model.ls_dirs'''

        gen = os.walk(path)
        top_folders = next(gen)[1]
        print("top_folders:")
        print(top_folders)

        print([os.listdir(os.path.join(path, folder))
               for folder in top_folders])
        '''
        groups = (
            groupby([(folder, os.listdir(os.path.join(path, folder)))
                     for folder in top_folders],
                    lambda item: any([".json" in name
                                      for name in item[1]])))
        print("groups:")
        print(groups)
        # print(list(groups[True]))
        folders = dict(groups[False]).keys() if False in groups else []
        print("folders:")
        print(folders)

        envs = dict(groups[True]).keys() if True in groups else []
        print("envs:")
        print(envs)
        '''
        folders = []
        envs = []
        for folder in top_folders:
            listdir = os.listdir(os.path.join(path, folder))
            if any([".json" in name
                    for name in listdir]):
                envs.append(folder)
            else:
                folders.append(folder)
        print("folders:")
        print(folders)

        print("envs:")
        print(envs)

        nodes_folders = self.applay_node(folders, "folder",
                                         folder=True)

        nodes_envs = self.applay_node(envs, "env",
                                      folder=False)
        return(nodes_folders, nodes_envs)

    def applay_node(self, names, nodes_type, folder=False):

        '''Convert list of names to nodes dict'''

        return([{"title": name, "type": nodes_type,
                 "folder": folder}
                for name in names])
