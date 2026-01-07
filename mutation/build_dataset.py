import csv

from generate_classes_summary_prompt import generate_prompt_1,generate_prompt_2

from generate_memory_fl_prompt import generate_prompt_2_1, generate_prompt_2_2

from parse_failing_test import parse_failing_tests
from extract_test_prompt import extract_test_prompt



import glob
import os


MAX_TOKEN = 3000

def find_matching_file(p, target_class):
    target_class = target_class.split(".")[-1]
    source_code_path = f"/home/yinseok/lorafl/data_preprocess/data_original/{p}/output_source/"
    pattern = f"{target_class}_*.json"
    matching_files = glob.glob(os.path.join(source_code_path, pattern))

    # Filter only files where the suffix after class name is a number
    for file in matching_files:
        filename = os.path.basename(file)
        suffix = filename.removeprefix(f"{target_class}_").removesuffix(".json")
        if suffix.isdigit():
            return file  # Return first match
    return None

def parse_log_data(log_data):
    try:
        left, mutated_code = log_data.split('|==>')
        parts = left.split(':')

        if len(parts) != 7:
            raise ValueError("Log format error: Expected 7 parts before '|==>'")
                                                                                                                               
        return {
            'ID': parts[0].strip(),
            'Type': parts[1].strip(),
            'original_operator': parts[2].strip(),
            'mutated_operator': parts[3].strip(),
            'location': parts[4].strip(),
            'lineno': int(parts[5].strip()),
            'original_code': parts[6].strip(),
            'mutated_code': mutated_code.strip()
        }
    except Exception as e:
        print(f"Failed to parse log: {e}")
        return None


def reset(p):
    if p=="Closure":
        project_path = "/home/yinseok/lorafl/temp/Closure_1/Closure_1_fixed"
        original_path = "/home/yinseok/ttr_1/temp/Closure_1/Closure_1_fixed"

    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

    # Copy everything from original_path to project_path
    for item in os.listdir(original_path):
        s = os.path.join(original_path, item)
        d = os.path.join(project_path, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)



def apply_mutation(target_file_path: str, parsed: dict) -> None:
    """
    Applies a mutation to a file based on provided details.
    Parameters:
    target_file_path (str): The path to the file to be mutated.
    parsed (dict): A dictionary containing keys:
          - 'lineno': The 1-indexed line number at which to apply the mutation.
          - 'original_code': The substring in the target line that is expected to be replaced.
          - 'mutated_code': The new code to insert in place of the original.
    Raises:
      ValueError: If the provided line number is out of range or if the original code is not found in the target line.
    """
    # Read all the lines in the target file.
    with open(target_file_path, "r") as file:
        lines = file.readlines()
    # Convert the 1-indexed line number to 0-indexed.
    line_index = parsed.get("lineno") - 1
    original_code = parsed.get("original_code")
    mutated_code = parsed.get("mutated_code")

    # Check if the given line number is valid.
    if line_index < 0 or line_index >= len(lines):
        raise ValueError(f"Line number {parsed.get('lineno')} is out of range for file with {len(lines)} lines.")

    # Check if the original code is present in the target line.
    if original_code not in lines[line_index]:
        raise ValueError(f"Original code '{original_code}' not found in line {parsed.get('lineno')}: {lines[line_index].strip()    }")

    if mutated_code == "<NO-OP>":
        # Comment out the original line
        lines[line_index] = "// " + lines[line_index].rstrip() + "  // <no-op>\n"
    else:
        # Replace original code with mutated code
        lines[line_index] = lines[line_index].replace(original_code, mutated_code)

    # Write the modified lines back to the file.
    with open(target_file_path, "w") as file:
        file.writelines(lines)


import math
import re

def approx_token_count(text: str,
                       avg_chars_per_token: float = 4.0) -> int:
    """
    Approximate the number of LLaMA‑3 tokens in `text` by:
      1) taking its character length divided by avg_chars_per_token, AND
      2) making sure we never undercount very short strings.

    Args:
      text: your prompt + completion string
      avg_chars_per_token: empirical average chars per token (~3.7–4.2).
                           4.0 is a safe default.
    Returns:
      An integer estimate of token count.
    """
    # 1) Base on raw character count
    char_based = len(text) / avg_chars_per_token

    # 2) Also consider splitting on whitespace to catch very short strings
    word_count = len(re.findall(r"\S+", text))  # every non‑space chunk
    word_based = word_count * 0.75               # ~0.75 tokens per word

    # Use the larger estimate (safer upper bound), round up
    return math.ceil(max(char_based, word_based, 1.0))



def build_dataset(p, data_list, choice,choices_count,coverage_data, file_path):
    """
    Generate a dataset dictionary for training prompt generation.

    Parameters:
        p : Project Name ( Closure, Chart, etc)

        data_list (List): A list from dataset.csv
        
        choice (int): Determines the stage of prompt generation.
            - choice == 1 : Generate prompt for Stage 1 (File level FL)
            - choice != 1 : Generate prompt for Stage 2 (Method level FL)
        choice_count(int): Determine the 'choice count'
    Returns:
        dict: A dictionary containing processed information from data_list and file content.
              The exact keys and values depend on the implementation and choice parameter.

    """
    #Paths Declaration
    base_path = "/home/yinseok/lorafl"
    

    #Parsing input list
    target_class = data_list[0]
    number = data_list[1]
    ft_file_path = data_list[2]
    bug_index = int(data_list[3])
    test_name = data_list[4]

    #Opening data from 'failing_tests'
    if p not in ft_file_path:
        parts = ft_file_path.split('/')
        new_parts = []
        for i, part in enumerate(parts):
            new_parts.append(part)
            if part == 'mutation_data':
                new_parts.append(f'{p}/')

        ft_file_path = "/".join(new_parts)


    parsed_ft = parse_failing_tests(ft_file_path)
    target_ft = parsed_ft[bug_index]
    
    my_set = set()   # create empty set

    for parsed in parsed_ft:
        my_set.add(parsed[0][0].split(".")[-1])  # add element to set

    total = ",".join(my_set)  # join set elements with comma


    ft,_,index = ft_file_path.split("/")[-1].split("__")    
    index = int(index)


    #Opening data from 'mutants.log'
    log_file_path = base_path + f"/mutation_data/{p}/log/mutants.{target_class}.log"
    
    try:
        with open(log_file_path, 'r') as f:
            log_file_content = f.readlines()
    except Exception as e:
        print(e)
        return -1,-1

    parsed_log = parse_log_data(log_file_content[index-1])

    if int(parsed_log["ID"])!= index:
        print("index not same")
        return -1,-1
    
    
    #Generating test_prompt
    test_prompt = extract_test_prompt(p,target_ft,total)

    #Function level FL, need < 1. Related Class , 2. Buggy Class>
    if choice==1:
        

        
        #print(parsed_log["location"])
        #print(target_ft[0][0])
        #print(target_ft[0][1])
        
        class_prompt,coverage_data, file_path = generate_prompt_1(p,parsed_log["location"], target_ft[0][0], target_ft[0][1],coverage_data, file_path)
        answer_prompt, coverage_data, file_path = generate_prompt_2(p,parsed_log["location"], target_ft[0][0], target_ft[0][1], choices_count, coverage_data, file_path)

        if choices_count==1:
            input_prompt = f"""
You are a debugging assistant. After reviewing the failing test case that exposed the bug, and a list of class summaries, select a class that might have caused the bug and need further investigation. Since your answer will be automatically handled, output ONLY the name of the classes, with the format specified below.

Output format example (replace with actual class names):
1.<className>

Failing test case that triggered the bug:
{test_prompt}


Summary of each class in the project (shuffled; order does not indicate importance):
{class_prompt}

List 1 class that need further investigation:
"""
        else:
            input_prompt = f"""
You are a debugging assistant. After reviewing the failing test case that exposed the bug, and a list of class summaries, I want you to select {choices_count} classes that might have caused the bug and need further investigation. Since your answer will be automatically handled, output ONLY the name of the classes, with the format specified below.

Output format example (replace with actual class names):
{chr(10).join(f"{i+1}.<class{i+1}>" for i in range(choices_count))}


Failing test case that triggered the bug:
{test_prompt}


Summary of each class in the project (shuffled; order does not indicate importance):
{class_prompt}

List {choices_count} number of classes that need further investigation, ordered from most likely to be related to the bug:
"""
        #print(class_prompt)
        if class_prompt == (-1,-1) or answer_prompt==(-1,-1):
            print(parsed_log["location"])
            print(target_ft[0][0])
            print(target_ft[0][1])
        return input_prompt, answer_prompt,coverage_data, file_path



    #Method level FL, need < 1. Target Class Code, 2. Related Methods, 3. Buggy Method >
    elif choice==2:
        
        
        source_code_file_path = find_matching_file(p,target_class)

        with open(source_code_file_path, 'r') as f:
            source_data = json.load(f)
        
        if "@" not in parsed_log["location"]:
            print("Mutation not located within method")
            return -1





        exclude = 0
        prev= 0
        same = 0
        while(True):
            method_prompt, answer, coverage_data, file_path = generate_prompt_2_1(p,target_class,target_ft[0][0],target_ft[0][1],parsed_log,source_data,exclude,choices_count,coverage_data, file_path)

            if method_prompt==-1 or answer==-1:
                return -1
            if choices_count>=1:
                input_prompt = f"""
You are a debugging assistant. After reviewing the failing test case that exposed the bug, and a buggy class, I want you to select up to {choices_count} methods that most likely contain the bug.

Instructions:
1. You may **ONLY** choose methods from the list under ##EXISTING_METHODS. This list contains all valid method names and line numbers.
2. Your output must **STRICTLY** follow the format under ##OUTPUT_FORMAT. Replace the placeholders with actual method names and line numbers from ##EXISTING_METHODS.
3. You must return **at most** {choices_count} lines. If fewer methods are relevant based on ##EXISTING_METHODS, return only those.

##Failing test case that triggered the bug:
{test_prompt}

##target class (each method with its name and line number shown at the beginning)
{method_prompt}

##OUTPUT_FORMAT (replace <methodName>,<lineno> with actual method name and line number from ##EXISTING_METHODS):
{chr(10).join(f"{i+1}.methodName@lineno" for i in range(choices_count))}

Identify the {choices_count} methods most likely to contain the bug, and list them in order from most to least likely. :
"""
            else:
                input_prompt = f"""
You are a debugging assistant. After reviewing the failing test case that exposed the bug and a buggy class, I want you to select one method that is most likely to have caused the bug and needs further investigation. Since your answer will be automatically handled, output ONLY the name and line number of the method, in the format specified below.

Output format example (replace with actual method name and line number):
1.<methodName@lineno>

Failing test case that triggered the bug:
{test_prompt}

target class (each method with its name and line number shown at the beginning)
{method_prompt}

List one method that is most likely to have caused the bug:
"""


            count = approx_token_count(input_prompt)
            count += approx_token_count(answer)
            
            if prev==count:
                same+=1
                if same==3:
                    return -1
            else:
                prev = count
                same = 0
            

            if count < MAX_TOKEN:
                break
            
            if count>20000:
                exclude+=15
            elif count>7000:
                exclude+=7
            elif count>4000:
                exclude+=2
            exclude+=1
        
        return input_prompt, answer, coverage_data, file_path


    else:
        print("nooo")
        return -1

    


import csv
import json


def build_dataset_main(p,csv_file_path, output_jsonl_path,choice_counts,choice):
    results = []
    #choice_counts = [1,2,3]
    #choice_counts = [3]
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # skip header
        i = 0
        
        coverage_data = None
        file_path = None


        for row in reader:
            i+=1
            if row[-2] == '1' and choice==1:  # if 'a' == 1
                print(i)
                filtered_row = row[:-2]  # remove 'a' and 'b'
                
                for cc in choice_counts:
                    try:
                        rv = build_dataset(p,filtered_row,1,cc,coverage_data,file_path)
                        if rv==-1:
                            continue
                        input_prompt, output_prompt,coverage_data, file_path = rv
                    except Exception as e:
                        print(e)
                        continue

                    if input_prompt != -1:
                        results.append({
                            "input": input_prompt,
                            "output": output_prompt
                        })

            if (row[-1] == "1" and choice==2) or (choice==3 and (row[-1]=="1" or row[-2] == "1")):
                print(i)
                filtered_row = row[:-2]
                for cc in choice_counts:
                    try:
                    
                        rv = build_dataset(p,filtered_row,2,cc,coverage_data, file_path)
                        if rv==-1:
                            continue
                        input_prompt, output_prompt, coverage_data, file_path = rv
                    except Exception as e:
                        print(e)
                        continue

                    if input_prompt != -1:
                        results.append({
                            "input" : input_prompt,
                            "output" : output_prompt
                        })

    with open(output_jsonl_path, 'w') as f:
        for item in results:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')

build_dataset_main("Closure", "Closure/data_output2_fixed.csv", "Closure/train_data_s2_123_v3_5000.jsonl", [1,2,3,3,4,5],3)
build_dataset_main("Chart", "Chart/data_output2.csv", "Chart/train_data_s2_123_v3_5000.jsonl", [1,2,3,3,4,5],3)
build_dataset_main("Lang", "Lang/data_output2.csv", "Lang/train_data_s2_123_v3_5000.jsonl", [1,2,3,3,4,5],3)
build_dataset_main("Time", "Time/data_output2.csv", "Time/train_data_s2_123_v3_5000.jsonl", [1,2,3,3,4,5],3)

import time

def main(project):
    start_time = time.time()
    data_input_path = f"{project}/data_output2.csv"
    for i in range(1,3):
        data_output_path = f"{project}/train_data_s{i}_123.jsonl"
        build_dataset_main(project, data_input_path, data_output_path, [1,2,3],i)
    


    #build_dataset_main("Closure", "data_output2_fixed.csv", "train_data_s2_3.jsonl", [3],2)
    #build_dataset_main("Closure", "data_output2_fixed.csv", "train_data_s2_123.jsonl", [1,2,3],2)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Total time spent: {elapsed_time:.2f} seconds")


#main("Chart")
#main("Lang")
#main("Time")

# Example usage
#1 - with summary, error
#2 - without summary
#3 - with summaray

#4 - excluding bugs with too much tests
#5 - + 1,2,3 classes

#data = ["com.google.debugging.sourcemap.SourceMapConsumerV3",	"62",	"/home/yinseok/lorafl/mutation_data/results/failing_tests__com.google.debugging.sourcemap.SourceMapConsumerV3__62",	"6"	,"SourceMapGeneratorV3Test"	,"1"	,"0"	,"1"]


#data = ['com.google.debugging.sourcemap.SourceMapConsumerV3', '62', '/home/yinseok/lorafl/mutation_data/results/failing_tests__com.google.debugging.sourcemap.SourceMapConsumerV3__62', '0', 'SourceMapGeneratorV3Test']
#data = ["com.google.debugging.sourcemap.SourceMapConsumerV3","124","/home/yinseok/lorafl/mutation_data/results/failing_tests__com.google.debugging.sourcemap.SourceMapConsumerV3__124","1","SourceMapGeneratorV3Test",1]
#input_data, output_data, _, _ = build_dataset("Closure",data,2,3,None,None)
#print(input_data)
#print("\n\n\n\n")
#print(output_data)



