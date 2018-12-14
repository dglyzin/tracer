'''This class is extention of BaseDB for some specific task.
It contain methods that cannot be generalised, they are specific
for task environmant.
'''
# parser$ ~/anaconda3/bin/python3 -m translator.tokenizer.io.model.model_main

# import peewee as pw
from datetime import date

from translator.tokenizer.io.model.model_base import BaseDB
from translator.tokenizer.io.model.model_tables import create_dialect_table
from translator.tokenizer.io.model.model_tables import create_users_table


class TokenizerDB(BaseDB):

    '''
    db consist from one dialect table,
    composed from the entries.

    each entry must be:
    (term_name, template, grammar_type, pattern_type)
    where
       template
          either re or txt or ex template.

       grammar_type type is list like one of thats:

          ('br_left', [True, False, False])
          ('br_right', [True, False, False])
          ('br_mid', [False, True, False])
          ('a',)

       pattern_type is list like one of thats:

          ('re', [+ order])
          ('txt', [+ order])
          ('ex',)

          where order is optional pattern order.

    Examples:

        ('let', r"Let(${defs}in:${clauses}",
        ('br_left', [True, True, False]),
        ('txt',)

        ('func', r"${{pred}}\(${args}",
        ('br_left', [True, False, False]),
        ('re', 6.1))

        # x, xs, normal_form_0
        ('var', r"(?P<obj>[a-z|_|0-9]+)", ('a'),
        ('re', 2)),

        ('eq', "Eq(${eqs})Eq",
        ('a',), ('ex',)),
    '''
    def __init__(self, path="translator/tokenizer/io/model/demo_dialect.db"):
        
        BaseDB.__init__(self, path)

    def create_dialect_db(self):
        BaseDB.create_db(self, create_dialect_table,
                         create_users_table)

    def create_users_table(self):
       
        try:
            self.tables_dict
        except AttributeError:
            self.tables_dict = {}

        users_tables = self.load_users_tables(create_users_table)
        self.create_db_tables(users_tables)

    def create_model_table(self):

        try:
            self.tables_dict
        except AttributeError:
            self.tables_dict = {}

        model_tables = self.load_model_tables(create_dialect_table)
        self.create_db_tables(model_tables)

    def load_all_tables(self):

        BaseDB.load_tables(self, create_dialect_table,
                           create_users_table)

    def show_all_entries(self, table_name="dialect"):

        out = BaseDB.show_all_entries(self, table_name=table_name)
        return(out)

    def fill_dialect_db(self):
        
        db = self.db
        table = self.tables_dict["dialect"]

        db.connect()

        # create entry:
        table.create(term_name="let",
                     template=r"Let(${defs}in:${clauses}",
                     grammar_type="('br_left', [True, True, False])",
                     pattern_type="('txt',)")
        # expirydate=date(2100, 1, 1)

        db.close()
        
    def add_pattern(self, entry):
        
        '''
        - ``entry`` -- entry dict to be added in db.
        see descrition above.
        (see BaseDB.add_table_entry)

        Examples:

        entry = {"term_name": "let",
                 "template": r"Let(${defs}in:${clauses}",
                 "grammar_type": ('br_left', [True, True, False]),
                 "pattern_type": ('txt',)}
        '''
                      
        table = self.tables_dict["dialect"]

        if "created_date" in entry:
            entry.pop("created_date")

        self.add_table_entry(table, entry)

    def select_pattern(self, term_name):
        '''
        Select with term_name.
        (see BaseDB.select_table_entry)
        '''
        table = self.tables_dict["dialect"]
        res = self.select_table_entry(table, 'term_name', term_name)
        return(res)

    def edit_pattern(self, term_name, props):
        '''
        Edit  properties of pattern's with term_name.
        (see BaseDB.edit_table_entry)
        '''
        table = self.tables_dict["dialect"]
        if "created_date" in props:
            props.pop("created_date")

        self.edit_table_entry(table, 'term_name', term_name,
                              props)
        
    def del_pattern(self, term_name):
        '''
        Delete pattern with term_name.
        (see ``BaseDB.del_table_entry``)
        '''
        table = self.tables_dict["dialect"]
        self.del_table_entry(table, 'term_name', term_name)


def test_create():

    print("\ntest create db")

    agent = TokenizerDB()
    agent.create_dialect_db()
    agent.fill_dialect_db()

    agent.add_pattern({"term_name": "func",
                       "template": r"${{pred}}\(${args}",
                       "grammar_type": ('br_left', [True, False, False]),
                       "pattern_type": ('re', 6.1)})
                      
    # sin, abelian, a:
    agent.add_pattern({"term_name": "pred",
                       "template": r"(?P<obj>\w+)",
                       "grammar_type": ('part',),
                       "pattern_type": ('re',)})

    agent.edit_pattern("pred", {"grammar_type": ('a',)})

    agent.del_pattern("pred")
    
    agent.show_all_entries()

    return(agent)


def test_load():

    print("\ntest load tables")

    agent = TokenizerDB()
    agent.load_all_tables()
    
    agent.show_all_entries()

    return(agent)


def test_select():

    print("\ntest select:")

    agent = test_load()
    res = agent.select_pattern("let")
    
    print("\nresults count:")
    print(res.count)

    return(agent)


def test_create_user_table():

    agent = TokenizerDB()
    agent.create_users_table()
    data = {
        "username": "admin",
        "is_admin": True,
        "password": "13",
        "email": "email"}
    agent.create_new_user(data)
    userexist = agent.check_user_exist(data)
    print("\nuserexist:")
    print(userexist)

    checkuser = agent.check_user(data)
    print("\ncheckuser:")
    print(checkuser)

    agent.show_all_entries(table_name="user")

    
def test_show_all_entries_user():
    agent = TokenizerDB()
    agent.load_all_tables()
    agent.show_all_entries(table_name="user")


if __name__ == '__main__':

    # test_create()
    # test_create_user_table()
    test_load()
    test_select()
    test_show_all_entries_user()
