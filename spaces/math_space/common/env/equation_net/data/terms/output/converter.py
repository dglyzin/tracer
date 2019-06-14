# convert terms from .py files into json.
#  python3 -m env.equation_net.data.terms.output.converter -path "env/equation/data/terms/output/cpp/patterns" -dialect "cpp" -brackets False
# 
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
import sys
import json
import os
patterns_json = "env/equation_net/data/terms/output/patterns.json"

if __name__ == "__main__":
    
    if '-path' in sys.argv:
        path = sys.argv[sys.argv.index('-path') + 1]
    else:
        raise(BaseException("-path needed"))

    if '-dialect' in sys.argv:
        dialect_name = sys.argv[sys.argv.index('-dialect') + 1]
    else:
        raise(BaseException("-dialect needed"))

    if '-brackets' in sys.argv:
        brackets = eval(sys.argv[sys.argv.index('-brackets') + 1])
    else:
        raise(BaseException("-brackets needed"))

    # get json:
    if not os.path.exists(patterns_json):
        with open(patterns_json, "w") as f:
            f.write(json.dumps({"entries": []}))
        
    with open(patterns_json) as f:
        data = json.loads(f.read())
        
    terms_names_exist = dict([(entry["term"], idx)
                              for idx, entry in enumerate(data["entries"])
                              if entry["dialect"] == dialect_name])

    files_names = os.listdir(path)
    for file_name in files_names:
        if ".py" in file_name and "~" not in file_name:
    
            # get term:
            with open(os.path.join(path, file_name)) as f:
                code = f.read()
        
            code_list = code.split("\n")
            code_list = [line + "\n" for line in code_list]
            
            term_name = file_name.split(".")[0]
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
    
    # write back:
    with open(patterns_json, "w") as f:
        f.write(json.dumps(data))
    
