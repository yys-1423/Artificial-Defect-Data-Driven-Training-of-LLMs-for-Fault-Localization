import os
import glob
import json
import re

from parse_failing_test import parse_failing_tests

def extract_relevant_stack_trace(stack_trace, method_name):
    lines = stack_trace.strip().split('\n')
    
    # Find the last line index that contains the method_name
    last_index = -1
    for i, line in enumerate(lines):
        if method_name in line:
            last_index = i
    
    # If method_name not found, return the full trace
    if last_index == -1:
        print("not found")
        return -1
    
    # Return trace up to and including the last line with method_name
    relevant_lines = lines[:last_index + 1]
    return '\n'.join(relevant_lines)

def parse_line(line):
    #pattern = r'at\s+([\w\.]+)\.([\w]+)\.([\w]+)\(([\w\.]+):(\d+)\)'
    pattern = r'at\s+([\w\.\$]+)\.([\w\$]+)\.([\w\$]+)\(([\w\.]+):(\d+)\)'

    match = re.match(pattern, line.strip())
    
    if not match:
        return None  # Or raise an error if you'd prefer
    
    package = match.group(1)
    test_class = match.group(2)
    test_method = match.group(3)
    file = match.group(4)
    lineno = int(match.group(5))

    return {
        'package': package,
        'test_class': test_class,
        'test_method': test_method,
        'file': file,
        'lineno': lineno
    }

def extract_test_code(original_test_function, parsed_line):
    methods = original_test_function["methods"]
    #print(parsed_line)   
    target_method = parsed_line["test_method"]
    lineno = parsed_line["lineno"]

    for method in methods:
        if method["name"]==target_method and method["startLine"]<=lineno and method["endLine"]>=lineno:
            return method["snippet"]

    return -1



def extract_test_function(original_test_function, class_name, method_name,stack_trace ):
    lines = stack_trace.strip().split('\n')
    
    test_codes = []
    for line in lines:
        #print(line)
        if class_name in line:
            parsed_line = parse_line(line.strip())
            #print(parsed_line)
            test_code = extract_test_code(original_test_function, parsed_line)
            if test_code!=-1:
                test_codes.append(test_code)

    return test_codes[-4:]

def extract_test_prompt(p, bug_report,total):
    [class_name, method_name], error_message, stack_trace = bug_report
    class_name = class_name.split('.')[-1]
    path = f"/home/yinseok/lorafl/data_preprocess/data_original/{p}/output_test"

    stack_trace = extract_relevant_stack_trace(stack_trace, method_name)

    # Find all matching files
    matching_files = sorted(glob.glob(os.path.join(path, f"{class_name}_*.json")))
    
    if not matching_files:
        print("No bug_report_###.json file found.")
        return None
    
    first_file = matching_files[0]
    print(f"Opening file: {first_file}")
    
    with open(first_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    test_codes = extract_test_function(data,class_name,method_name,stack_trace)
    
    test_codes = list(reversed(test_codes))

    prompt = f"""
==== TEST FAILURE REPORT ====

### Test classes that have discovered the target bug : <{total}>


### Primary Failing Test: <{class_name}::{method_name}>


--- Stack Trace ---
{error_message}
{stack_trace}

--- Test Method Code that reported failure---
{test_codes[0]}

===========================
"""
    #--- Related Methods ---
    #{"\n\n".join(test_codes[1:])}
    #print(prompt)
    return prompt


    

#bug_reports = parse_failing_tests("/home/yinseok/lorafl/mutation_data/results/failing_tests__com.google.javascript.jscomp.NameAnalyzer__32")


#extract_test_prompt("Closure",bug_reports[0])
