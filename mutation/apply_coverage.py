import os
import random
from parse_failing_test import parse_failing_tests
from collections import Counter
from run_command import run_command
import shutil
from construct_path import construct_path

def reset(p):
    if p=="Chart":
        project_path = "/home/yinseok/lorafl/temp/Chart_1/Chart_1_fixed"
        original_path = "/home/yinseok/ttr_1/temp/Chart_1/Chart_1_fixed"
    elif p=="Lang":
        project_path = "/home/yinseok/lorafl/temp/Lang_1/Lang_1_fixed"
        original_path = "/home/yinseok/ttr_1/temp/Lang_1/Lang_1_fixed"
    elif p=="Time":
        project_path = "/home/yinseok/lorafl/temp/Time_4/Time_4_fixed"
        original_path = "/home/yinseok/ttr_1/temp/Time_4/Time_4_fixed"
    elif p=="Closure":
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


def find_files_with_substring(directory, substring):
    """
    Return a list of file names in the given directory
    that contain the given substring.
    """
    result = []
    
    # List all files in the given directory
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        
        # Check if it's a file and contains the substring
        if os.path.isfile(full_path) and substring in filename:
            result.append(filename)
    
    return result


def apply_coverage(p,t):

    test_case_counter = Counter()


    base_path = "/home/yinseok/lorafl/"

    if p== "Chart":
        project_path = "/home/yinseok/lorafl/temp/Chart_1/Chart_1_fixed"
    elif p=="Lang":
        project_path = "/home/yinseok/lorafl/temp/Lang_1/Lang_1_fixed"
    elif p=="Time":
        project_path = "/home/yinseok/lorafl/temp/Time_4/Time_4_fixed"
    elif p == "Closure":
        project_path = "/home/yinseok/lorafl/temp/Closure_1/Closure_1_fixed"

    
    data_path = f"/home/yinseok/lorafl/mutation_data/{p}"

    results_path = data_path + "/results"

    coverage_path = data_path + "/coverage"

    files = find_files_with_substring(results_path, t)
    
    if len(files)==0:
        return
    
    
    for file in files:
        #print(file)
        file_path = results_path +"/" + file
        
        parsed = parse_failing_tests(file_path)
        

        for parsedd in parsed:
            test_case = parsedd[0][0]+"::"+parsedd[0][1]
            test_case_counter[test_case] += 1  # Count occurrences
    
    all_test_cases = list(test_case_counter.keys())
    # If total test cases <= 20 -> Just return all
    if len(all_test_cases) <= 20:
        final_test_cases = all_test_cases

    else:
        # Top 20 by frequency
        top_20 = [tc for tc, _ in test_case_counter.most_common(20)]

        # Remaining candidates
        remaining_test_cases = list(set(all_test_cases) - set(top_20))

        # Random sample from remaining (up to 20)
        random_30 = random.sample(remaining_test_cases, min(30, len(remaining_test_cases)))

        # Merge them
        final_test_cases = top_20 + random_30

    print("Selected Test Cases:")
    
    for tc in final_test_cases:
        reset(p)
        coverage_command = f"defects4j coverage -w {project_path} -t {tc} -i total/{p}/total.src"
        print(tc)

        try:
            print(run_command(coverage_command))
        except Exception as e:
            print(e)
            continue
        
        target_file = project_path + "/coverage.xml"
        destination = coverage_path + f"/coverage__{t}__{tc}.xml"
        
        if os.path.isfile(target_file):
            shutil.copy2(target_file, destination)
        else:
            print("nothing~")
        

#apply_coverage("Closure", "com.google.javascript.jscomp.ScopedAliases")
