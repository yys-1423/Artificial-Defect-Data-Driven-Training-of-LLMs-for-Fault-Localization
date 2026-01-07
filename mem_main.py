import os
import json
import time

from prompts.fl_mem_v3 import refine
from helper.get_bug_info import get_bug_info
from helper.helpers import create_log_directory
from helper.get_base_dir import get_base_dir

project_basic_dir = get_base_dir()

p,b,_,_,_ = get_bug_info()

def mem_main(repeat):
    
    log_dir = create_log_directory(f"{project_basic_dir}update_log/03_06")
    if log_dir == None:
        return -1
    count = 0
    time_log_path = os.path.join(log_dir, 'time.txt')

    for i in range(len(p)):
        count+=1
        path = os.path.join(log_dir, f"{p[i]}_{b[i]}")
        
        os.makedirs(path, exist_ok = True)

        
        j = 0
        scores = []
        results = []
        while j<repeat:
            mem_path = f"{project_basic_dir}data/{p[i]}/memory/fl_test_5/fold_1/stage_3/"

            start = time.time()
            try:
                return_value, model, log, result = refine(p[i], b[i], mem_path, verbose=False)
            except Exception as e:
                print(str(e))
                log = [str(e)]
            elapsed = time.time() - start

            with open(time_log_path, 'a') as time_file:
                time_file.write(f"{elapsed}\n")

            results.append(result)

            file_name = f"{path}/log_{j}.json"

            with open(file_name, "w") as file:
                json.dump(log, file, indent=4)

            j+=1



if __name__ == "__main__":
    mem_main(1)


