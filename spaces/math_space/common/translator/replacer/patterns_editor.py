# parser$ python3 -m translator.replacer.patterns_editor
import abc
import json

import logging


# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
# logger = logging.getLogger('replacer_cpp.brackets_main')

# if using directly uncoment that:


# create logger
log_level = logging.WARNING  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('patterns_editor')
logger.setLevel(level=log_level)

import os
import inspect
currentdir = (os.path
              .dirname(os.path
                       .abspath(inspect.getfile(inspect.currentframe()))))


class PatternsEditor():

    '''
    {"entries":
     [
      {"term": term_name,
       "brackets": brackets,
       "dialect": dialect_name,
       "outputs": [],
       "source": code_list}
    ]}
    '''

    def __init__(self):
        self.patterns_json = "env/equation_net/data/terms/output/patterns.json"
        # fix notebooks path bug:
        self.patterns_json_hd_fixed = (os.path
                                       .join(currentdir.split("translator")[0],
                                                   ("env/equation_net/data/terms/"
                                                    + "output/patterns.json")))
        '''
        self.patterns_json_hd_fixed = ("spaces/math_space/common/env/"
                                       + "equation_net/data/terms/output/"
                                       + "patterns.json")
        '''

        self.compile_errors_file = (os.path
                                    .join(currentdir.split("translator")[0],
                                          ("env/equation_net/data/terms/"
                                           + "output/compile_log.txt")))

        # self.compile_errors_file = "env/equation_net/data/terms/output/compile_log.txt"
        self.exception_terms = ["base", "brackets_main"]

    def remove_patterns(self, dialect_name, term_names):

        '''Remove entries with name from term_names list

        - ``term_names`` -- list of terms names for removing.
        '''

        data = self.open_patterns()
        '''
        with open(self.patterns_json) as f:
            data = json.loads(f.read())
        '''

        terms_names_exist = dict([(entry["term"], idx)
                                  for idx, entry in enumerate(data["entries"])
                                  if entry["dialect"] == dialect_name])
        # remove all:
        for term_name in term_names:
            try:
                term_idx = terms_names_exist[term_name]
            except KeyError:
                logger.warning("remove_patterns:"
                               + " term ``%s`` not exist" % (term_name))
                continue
            data["entries"].pop(term_idx)

        self.open_patterns(data)
        '''
        with open(self.patterns_json, "w") as f:
            f.write(json.dumps(data))
        '''

    def load_patterns(self, dialect_name, brackets=True):

        '''Load all patterns to dict with term_name as keys
        transform source: list |-> str |-> python object
        i.e python class mast exist and been last defined variable
        in source'''

        data = self.open_patterns()
        '''
        with open(self.patterns_json) as f:
            data = json.loads(f.read())
        '''

        modules = dict([(entry["term"],
                         compile("".join(entry["source"]),
                                 self.compile_errors_file, "exec"))
                        for entry in data["entries"]
                        if entry["dialect"] == dialect_name
                        if entry["brackets"] == brackets])

        patterns = {}
        # supposed here that globals is mutable
        # inside eval and exec
        # in that case Base will be aveilable to all terms
        # no mather of patterns order.
        # (when it will be used)
        glob = {}
        for term_name in modules:
            exec(modules[term_name], glob)
            term_cls = eval(modules[term_name].co_names[-1], glob)

            if term_name not in self.exception_terms:
                patterns[term_name] = term_cls
            # print(modules[term_name].co_names)

            # add all globals:
            for name in modules[term_name].co_names:
                # TODO: test restriction, maybe change:
                if name[0].isupper() and name not in ("INFO", "DEBUG"):
                    glob[name] = eval(name, glob)
            # glob[modules[term_name].co_names[-1]] = patterns[term_name]
            
        self.patterns = patterns
        return(patterns)

    def load_patterns_source(self, dialect_name, brackets=True):

        '''Load all patterns to dict with term_name as keys
        transform source: list |-> str |-> python object
        i.e python class mast exist and been last defined variable
        in source'''

        data = self.open_patterns()
        '''
        with open(self.patterns_json) as f:
            data = json.loads(f.read())
        '''
        modules = dict([(entry["term"],
                         "".join(entry["source"]))
                        for entry in data["entries"]
                        if entry["dialect"] == dialect_name
                        if entry["brackets"] == brackets])
        patterns = modules
        '''
        patterns = {}

        for term_name in modules:
            source = modules[term_name]

            if term_name not in self.exception_terms:
                patterns[term_name] = source
        '''
        self.patterns = patterns
        return(patterns)

    def set_pattern(self, dialect_name, term_name, code, brackets=False):
        
        '''load patterns, set or create new entry with
        term_name, code as source, brackets; and save

        - ``code`` -- string with code
        '''

        data = self.open_patterns()
        '''
        with open(self.patterns_json) as f:
            data = json.loads(f.read())
        '''

        terms_names_exist = dict([(entry["term"], idx)
                                  for idx, entry in enumerate(data["entries"])
                                  if entry["dialect"] == dialect_name])
        # transform string to list
        code_list = code.split("\n")
        code_list = [line + "\n" for line in code_list]

        if term_name in terms_names_exist:
            term_entry = data["entries"][terms_names_exist[term_name]]
            term_entry["source"] = code_list
                
        else:
            term_entry = {"term": term_name,
                          "brackets": brackets,
                          "dialect": dialect_name,
                          "outputs": [],
                          "source": code_list}
            data["entries"].append(term_entry)
            terms_names_exist[term_name] = len(data["entries"])-1

        self.open_patterns(data)
        '''
        with open(self.patterns_json, "w") as f:
            f.write(json.dumps(data))
        '''

    def open_patterns(self, data=None):

        '''For work from parser as well as from hd.'''

        if data is not None:
            try:
                with open(self.patterns_json, "w") as f:
                    f.write(json.dumps(data))
            except FileNotFoundError:
                with open(self.patterns_json_hd_fixed, "w") as f:
                    f.write(json.dumps(data))
        else:
            try:
                with open(self.patterns_json) as f:
                    data = json.loads(f.read())
            except FileNotFoundError:
                with open(self.patterns_json_hd_fixed) as f:
                    data = json.loads(f.read())
        return(data)


if __name__ == "__main__":
    editor = PatternsEditor()
    # editor.remove_patterns(["brackets_main", "base"], "cpp")
    editor.set_pattern("cpp", "diff", "x = 3")
    patterns = editor.load_patterns("cpp", brackets=False)
    print("\nload_patterns:")
    for term_name in patterns:
        print("\nterm:######################")
        print(term_name)
        print("\ncode:")
        print(patterns[term_name])
    print("Diff('net'):")
    print(patterns["diff"]("net").diff())
    
