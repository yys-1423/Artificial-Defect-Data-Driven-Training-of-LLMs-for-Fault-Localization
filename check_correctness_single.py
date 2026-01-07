import json
import re
import os
from helper.get_bug_info import get_bug_info
from helper.get_answer import get_answer
p,b,_,_,_ = get_bug_info()
from collections import Counter
from helper.get_base_dir import get_base_dir

project_basic_dir = get_base_dir()

def get_buggy_rank(sorted_methods, buggy_class, buggy_method, buggy_line):
    """
    Finds the minimum rank of the actual buggy method in the sorted fault localization results.

    Parameters:
      sorted_methods: List of sorted methods, each as [Classname, MethodName, Lineno].
      buggy_class: List of buggy class names.
      buggy_method: List of buggy method names.
      buggy_line: List of buggy line numbers.

    Returns:
      Minimum rank of the buggy method in sorted_methods (1-based index). If no match, returns None.
    """

    # Convert buggy info into a list of tuples
    buggy_methods = []
    for cls, method, line in zip(buggy_class, buggy_method, buggy_line):
        if method == "@@" and line == "@@":
            # Bug of omission: Only match the class name
            buggy_methods.append((cls, None, None))
        else:
            # Normal case: Match full class, method, and line number
            buggy_methods.append((cls, method, str(line)))  # Normalize line number as string

    # Find the minimum rank
    min_rank = 100

    for rank, method in enumerate(sorted_methods, start=1):  # 1-based index
        class_name, method_name, line_no = method
        line_no = str(line_no)  # Normalize line number

        for buggy_cls, buggy_mtd, buggy_ln in buggy_methods:
            if buggy_mtd is None and buggy_ln is None:
                # Bug of omission case: Only class name needs to match
                if class_name == buggy_cls:
                    min_rank = min(min_rank, rank)
            else:
                # Normal case: Full match required
                if class_name == buggy_cls and method_name == buggy_mtd and line_no == buggy_ln:
                    min_rank = min(min_rank, rank)

    return min_rank  # Return None if no match found



def sort_fault_localization(parsed_result, parsed_second_result, all_methods):
    """
    Sorts the fault localization methods as follows:
      1. Uses the original fault localization result (parsed_result) in the order given.
      2. Appends methods from the second result (parsed_second_result) that are not already in parsed_result,
         ordering them by their order in all_methods.
    
    Parameters:
      parsed_result: list of lists, where each inner list is a run (list of [Classname, MethodName, Lineno])
                     representing the original fault localization results.
      parsed_second_result: same structure as parsed_result, representing the secondary results.
      all_methods: list of all methods in the project in the form [Classname, MethodName, Lineno],
                   which defines the overall order.
      
    Returns:
      A list of methods (each method as [Classname, MethodName, Lineno]) with the original results first,
      followed by any additional methods from the second result (ordered according to all_methods).
    """
    # Since there is only a single run, take the first (and only) parsed_result as the primary list.
    primary_methods = parsed_result[0] if parsed_result else []
    
    # Build a set of keys (class, method, line) from the primary methods
    primary_set = {(m[0], m[1], str(m[2])) for m in primary_methods}
    #print(primary_set)
    # From parsed_second_result, take the first run and filter out methods already in primary_methods.
    second_methods_raw = parsed_second_result[0] if parsed_second_result else []
    second_methods = [
        m for m in second_methods_raw
        if (m[0], m[1], str(m[2])) not in primary_set
    ]
    
    # Create a ranking for methods based on their order in all_methods.
    # Note: all_methods comes from extract_parts so its line numbers are strings.
    method_to_rank = {}
    for rank, method in enumerate(all_methods):
        key = (method[0], method[1], method[2])
        if key not in method_to_rank:
            method_to_rank[key] = rank

    # Sort the second methods according to the order in all_methods.
    second_methods_sorted = sorted(
        second_methods,
        key=lambda m: method_to_rank.get((m[0], m[1], str(m[2])), float('inf'))
    )
    #print(primary_methods)
    #print()
    #print(second_methods_sorted)
    # Concatenate the primary methods with the sorted additional methods.
    sorted_methods = primary_methods + second_methods_sorted
    return sorted_methods


def parse_class_methods(data):
    result = []
    
    for class_data in data:
        class_full_name, methods_str = class_data
        class_name = class_full_name.split('.')[-1]  # Extract the class name
        
        # Extract method@line patterns using regex
        method_lines = re.findall(r'([a-zA-Z0-9_]+)@([0-9]+)', methods_str)
        
        for method, line in method_lines:
            result.append([class_name, method, int(line)])
    
    return result

def parse_fault_localization(output: str):
    """
    Parses fault localization output to extract class names, method names, and line numbers.

    :param output: Multi-line string containing fault localization data.
    :return: List of dictionaries with extracted information.
    """
    parsed_methods = []
    lines = output.strip().split("\n")

    for line in lines:
        match = re.match(r'(\w+)@(\w+)@(\d+)', line.strip())
        if match:
            class_name = match.group(1)  # Extract class name
            method_name = match.group(2)  # Extract method name
            line_number = int(match.group(3))  # Extract line number as an integer

            parsed_methods.append([
                class_name,
                method_name,
                line_number
                ])

    return parsed_methods

def extract_parts(s):
    parts = s.split("#")  # Split at '#'
    a, b = parts[0].split(".")  # Split at '.'
    c = parts[1]  # The number part after '#'
    return [a, b, c]

def check_correctness(project_name, bug_id,bug_dir,index):
    # Load the correct answer from the JSON file
    answer_path = f"{project_basic_dir}data/{project_name}/data/{project_name}_{bug_id}/snippet.json"
    
    all_methods = []
    with open(answer_path, 'r') as file:
        data = json.load(file)
        for d in data:
            all_methods.append(extract_parts(d["name"]))

    buggy_class, buggy_method, buggy_line = get_answer(project_name, bug_id)
    buggy_class = [a.split('.')[-2] for a in buggy_class]
    result = []
    second_result = []
   
    ###
    ###
    ###
    json_path = f"{bug_dir}log_{index}.json"

    with open(json_path, "r") as f:
        data = json.load(f)
    #print(data[-1][-1])   
    if isinstance(data[0], str):
        return -1
    if len(data)==0:
        return -1
    elif len(data)==1:
        if len(data[0])==1:
            return -2
        elif len(data[0])==2:
            return -3
    result.append(data[-1][-1])
            
    second_result.append([[item[-2],item[-1]] for item in data if len(item) == 3])
        
    parsed_result = []
    
    parsed_second_result = []
    for s in second_result:
        parsed_second_result.append(parse_class_methods(s))
    #print(result)
    for r in result:
        parsed_answer = parse_fault_localization(r)
        parsed_result.append(parsed_answer)
    
    #print(parsed_result)
    #print()
    #print(parsed_second_result)
    #print()
    sorted_methods = sort_fault_localization(parsed_result, parsed_second_result, all_methods)
    #for m in sorted_methods:
    #    print(m)
    return get_buggy_rank(sorted_methods,buggy_class,buggy_method,buggy_line)

def get_acc(counts,acc):
    result = 0
    for i in range(0,acc):
        result+=counts[i+1]
    return result

def check_correctness_main(base_dir,index):
    
    result_counts = Counter()
    results = []  # List to store results

    for i in range(len(p)):
        bug_dir = f"{base_dir}{p[i]}_{b[i]}/"
        if os.path.isdir(bug_dir):
            try:
                result = check_correctness(p[i], b[i], bug_dir,index)
            except Exception as e:
                result = -2  # Store -2 in case of an exception
            results.append((p[i], b[i], result))
            result_counts[result] +=1
            #print(p[i], b[i], ":", result)
    # Save results to a file
    result_filepath = f"{base_dir}result.txt"
    with open(result_filepath, "w") as f:
    # Write accuracy scores first
        f.write(f"Acc@1: {get_acc(result_counts,1)}\n")
        f.write(f"Acc@3: {get_acc(result_counts,3)}\n")
        f.write(f"Acc@5: {get_acc(result_counts,5)}\n\n")

        # Write results
        for p_val, b_val, res in results:
            f.write(f"{p_val} {b_val} : {res}\n")

    # Write result counts at the end
        f.write("\nResult counts:\n")
        #for res, count in result_counts.items():
        #    f.write(f"{res}: {count}\n")
    print("Acc@1 : ",get_acc(result_counts,1))
    print("Acc@3 : ",get_acc(result_counts,3))
    print("Acc@5 : ",get_acc(result_counts,5))
    # Print all counts
    print("Result counts:", result_counts)






##check_correctness("Closure","1",f"{project_basic_dir}/mem_log/v0/log_013/Closure_1/",3)
