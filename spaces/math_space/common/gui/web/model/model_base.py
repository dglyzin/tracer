import peewee as pw


class BaseDB():

    def __init__(self, path="gui/web/model/demo_dialect.db"):

        self.db = pw.SqliteDatabase(path)
        self.path = path
        self.path_default = path

    def set_path(self, path):
        self.db = pw.SqliteDatabase(path)
        self.path = path
        return(path)

    def set_path_default(self):
        path = self.path_default
        self.db = pw.SqliteDatabase(path)
        self.path = path
        return(path)

    def get_path(self):
        return(self.path)

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

    def show_all_entries(self, table_name="dialect"):

        print("\nFROM BaseDB.show_all_entries")

        db = self.db
        table = self.tables_dict[table_name]
        table_field_names = table._meta.sorted_field_names
        print("\n table_sorted_field_names: %s" % (table_field_names))

        qs = db.execute_sql("select * from %s" % (table_name,))
        print("\n %s db entries:" % table_name)
        out = []
        for q in qs:
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

