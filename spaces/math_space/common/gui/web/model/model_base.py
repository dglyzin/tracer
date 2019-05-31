import peewee as pw
import json
import os

# name and key for config patterns db:
config_file_name = "configs/config_patterns_db.json"
config_path_key = "paths_db_patterns"

# prefix for hd:
config_file_prefix = "spaces/math_space/common"


class BaseDB():

    def __init__(self, dialect_name):

        self.change_dialect_db(dialect_name)
        
    # FOR paths:
    def change_path_of_dialect_db(self, dialect_name, path):

        '''Change path and update current db.
        '''

        self.reload_db(path)

        self.path = path
        self.save_path(dialect_name, path)
        return(path)

    def get_path_of_dialect_db(self, dialect_name):
        
        '''Just load and print path in ``config.json``
        (do not check if it is differ from currently used
         (for ex: when it was changed manualy))'''
        
        path = self.load_paths()[dialect_name]
        return(path)

    def change_dialect_db(self, dialect_name):

        '''Change path according to ``dialect_name``
        (if it exist in ``config.json``) and
        update the curent db.'''

        path = self.get_path_of_dialect_db(dialect_name)

        self.path = path
        
        self.reload_db(path)
        return(self.path)

        '''
        # if self.path not initiated yet:
        try:
            self.path
        except:
            # create it:
            self.path = path

        # if path was changed in json
        # or other dialect was used:
        if self.path != path:
            # change it:

            # self.set_path(path, dialect_name)
        '''

    def reload_db(self, path=None):
       
        '''Reload db with use of ``path`` or ``self.path``,
        if no specified.
        ``self.load_all_tables`` must be implemented in
        ancestors.'''

        if path is None:
            path = self.path

        if not os.path.exists(path):
            path = os.path.join(config_file_prefix, path)

        self.db = pw.SqliteDatabase(path)
        self.load_all_tables()

        # update path only when db successfuly
        # reloaded:
        if path is not None:
            self.path = path
        return(path)

    def save_path(self, dialect_name, path):

        '''Save path by modifying according entry in config.'''

        data = self.load_config()
        data[config_path_key][dialect_name] = path
        data_json = json.dumps(data, sort_keys=False, indent=4)
        with open(config_file_name, 'w') as config_file:
            config_file.write(data_json)
        
    def load_paths(self):

        '''Load paths from config.json.
        Names ``config_file_name`` and ``config_path_key``
        must be defined'''
        
        data = self.load_config()
        try:
            paths = data[config_path_key]
        except:
            raise(BaseException("\npatterns db: .json path key error"
                                + "\nconfig_path_key: " + config_path_key))
        return(paths)

    def load_config(self):
        
        '''Load config.json.
        Name ``config_file_name`` must be defined.'''
        
        data = None
        try:
            with open(config_file_name) as config_file:
                data = json.loads(config_file.read())
        except FileNotFoundError:
            fixed_path = os.path.join(config_file_prefix, config_file_name)
            with open(fixed_path) as config_file:
                data = json.loads(config_file.read())
        if data is None:
            raise(BaseException("\npatterns db: .json load db error"
                                + "\nconfig_file_name: " + config_file_name))
        return(data)
    # END FOR

    def load_all_tables(self):
        raise(BaseException("load_all_tables must be implemented"
                            + " in ancestor"))

    def create_db(self, model_tables_gen, users_tables_gen):
        
        '''Create all tables.

        Input:

        - ``tables_gen`` -- tables generator that is
        function which get's db and return table with
        all tables classes. (see ``model_tables.py``)'''
        
        tables = self.load_tables(model_tables_gen, users_tables_gen)
        self.create_db_tables(tables)

    def create_db_tables(self, tables):
        
        '''Examples:

        # for creating users tables only:
        users_tables = self.load_users_tables(users_tables_gen)
        create_db_tables(users_tables)

        # for creating model tables only:
        model_tables = self.load_model_tables(model_tables_gen)
        create_db_tables(model_tables)

        where ``users_tables_gen`` and ``model_tables_gen``
           - tables generators from model_tables.py
        '''
        
        db = self.db

        db.connect()
        # tables = [Dialect]
        try:
            db.create_tables(tables)
        except pw.OperationalError:
            db.drop_tables(tables)
            db.create_tables(tables)
        db.close()
        
    def load_tables(self, model_tables_gen, users_tables_gen):
    
        # self.tables_dict will be used in both
        # load_model_tables and load_users_tables:
        try:
            self.tables_dict
            print("tables_dict exist")
        except AttributeError:
            self.tables_dict = {}

        model_tables = self.load_model_tables(model_tables_gen)
        users_tables = self.load_users_tables(users_tables_gen)
        # Dialect = self.create_dialect_table()
        tables = users_tables + model_tables

        self.tables = tables
        return(tables)

    def load_users_tables(self, users_tables_gen):
        
        db = self.db
        users_tables_dict = users_tables_gen(db)
        users_tables = list(users_tables_dict.values())

        self.tables_dict.update(users_tables_dict)
        # self.users_tables_dict = users_tables_dict
        
        return(users_tables)

    def load_model_tables(self, model_tables_gen):
        
        db = self.db

        model_tables_dict = model_tables_gen(db)
        model_tables = list(model_tables_dict.values())

        self.tables_dict.update(model_tables_dict)
        # self.model_tables_dict = model_tables_dict

        return(model_tables)

    def show_all_entries(self, table_name="dialect", silent=False):

        if not silent:
            print("\nFROM BaseDB.show_all_entries")

        db = self.db
        table = self.tables_dict[table_name]
        table_field_names = table._meta.sorted_field_names
        if not silent:
            print("\n table_sorted_field_names: %s" % (table_field_names))

        qs = db.execute_sql("select * from %s" % (table_name,))
        if not silent:
            print("\n %s db entries:" % table_name)
        out = []
        for q in qs:
            if not silent:
                print(q)
            out.append(dict(zip(table_field_names, q)))
        return(out)

    def add_table_entry(self, table, entry: dict):
        
        '''

        Inputs:

        - ``table`` -- peewee table to be edit

        - ``entry`` -- entry dict to be added in db.
        see descrition above.
        
        Examples:

        entry = {"term_name": "let",
                 "template": r"Let(${defs}in:${clauses}",
                 "grammar_type": ('br_left', [True, True, False]),
                 "pattern_type": ('txt',)}
        '''                
        print("\nFROM add_table_entry:")
        print("\nentry:")
        print(entry)

        new_id = table.insert(**entry).execute()

        print("\ninserted:")
        print(new_id)
        '''
        for query in res:
            print(query)
        '''

    def select_table_entry(self, table,
                           filter_field_name: str,
                           filter_field_value: str):
        
        '''
        Select entry if entries ``filter_field_name``
        has ``filter_field_value``.

        Inputs:

        - ``table`` -- peewee table to be used.

        - ``filter_field_name`` -- name of entry's
        field to check for selecting.

        - ``filter_field_value`` -- value of field in which case
        according entry will be selected.
        '''
        print("FROM del_table_entry:")

        res = (table.select()
               .filter(**{filter_field_name: filter_field_value})
               .execute())
        return(res)
        
    def edit_table_entry(self, table,
                         filter_field_name: str,
                         filter_field_value: str,
                         props):
        
        '''
        Edit properties of entry if entries
        ``filter_field_name`` has ``filter_field_value``.

        Inputs:

        - ``table`` -- peewee table to be edit

        - ``filter_field_name`` -- name of entry's
        field to check for editing.

        - ``filter_field_value`` -- value of field in which case
        according entry will be edit.

        - ``props`` -- must be dict like
        {"template": r"Let(${defs}in:${clauses}",
         "grammar_type": ('br_left', [True, True, False]),}'''

        print("FROM edit_table_entry:")

        # convert all to str:
        for prop_name in props:
            props[prop_name] = str(props[prop_name])

        print("\nprops:")
        print(props)
        res = (table.update(**props)
               .filter(**{filter_field_name: filter_field_value})
               .execute())

        print("\nupdated:")
        print(res)
        '''
        for query in res:
            print(query)
        '''
        
    def clear_all_entries(self, table):
        res = table.delete().execute()
        print("\ndeleted:")
        print(res)

    def del_table_entry(self, table,
                        filter_field_name: str,
                        filter_field_value: str):
        
        '''
        Delete entry if entries ``filter_field_name``
        has ``filter_field_value``.

        Inputs:

        - ``table`` -- peewee table to be used.

        - ``filter_field_name`` -- name of entry's
        field to check for deleting.

        - ``filter_field_value`` -- value of field in which case
        according entry will be deleted.
        '''
        print("FROM del_table_entry:")

        res = (table.delete()
               .filter(**{filter_field_name: filter_field_value})
               .execute())

        print("\ndeleted:")
        print(res)
        '''
        for query in res:
            print(query)
        '''

    def get_users(self):

        print("\nFROM get_users")
        user_table = self.tables_dict["user"]
        users = user_table.select()
        # users = user_table.select().where(not user_table.is_admin)
        response = []
        for user in users:
            userdict = {"username": user.username,
                        "password": user.password,
                        "email": user.email,
                        "comment": user.comment}
            response.append(userdict)
        print("\nresponse:")
        print(response)
        return response

    def check_user(self, data):
        '''
        Inputs:

        - ``data`` -- dats =  {
        "username": self.get_argument("username"),
        "password": self.get_argument("password")}
        
        Return: data["username"] if user exist and password
        correct, else None
        '''
        # user_table = self.tables_dict["user"]
        users = self.get_users()
        print("users:")
        print(users)
        for user_data in users:
            if data["username"] == user_data["username"]:
                if data["password"] == user_data["password"]:
                    return(data["username"])
        return(None)
    
    def check_user_exist(self, data: dict)->bool:
        '''
        Inputs:

        - ``data`` -- dats =  {
        "username": self.get_argument("username"),
        
        '''
        # user_table = self.tables_dict["user"]
        users = self.get_users()
        for user_data in users:
            if data["username"] == user_data["username"]:
                return(True)
        return(False)
    
    def create_new_user(self, data):

        '''Create new user with only
        uniqueness checking.

        Inputs:

        - ``data`` -- data = {
        "username": self.get_argument("username"),
        "password": self.get_argument("password"),
        "email": self.get_argument("email")}

        Return: if user exist return None,
        else return data["username"].
        '''
        print("\nFROM create_new_user")
        if "is_admin" in data:
            try:
                data["is_admin"] = int(data["is_admin"])
            except:
                print("not admin")
                data["is_admin"] = 0
        user_exist = self.check_user_exist(data)
        if user_exist:
            print("user exist:")
            print(data)
            return(None)
        else:
            user_table = self.tables_dict["user"]
            res = self.add_table_entry(user_table, data)
            users = self.get_users()
            print("users:")
            print(users)
            return(data["username"])

    def edit_user(self, username, props):
        '''
        Edit  properties of user with username.
        (see BaseDB.edit_table_entry)
        '''
        table = self.tables_dict["user"]
        if "created_date" in props:
            props.pop("created_date")

        self.edit_table_entry(table, 'username', username,
                              props)
        
    def del_user(self, username):
        '''
        Delete user with username.
        (see ``BaseDB.del_table_entry``)
        '''
        table = self.tables_dict["user"]
        self.del_table_entry(table, 'username', username)

