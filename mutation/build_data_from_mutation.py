import csv
import random
from run_command import run_command
import os
import shutil

from construct_path import construct_path


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
        raise ValueError(f"Original code '{original_code}' not found in line {parsed.get('lineno')}: {lines[line_index].strip()}")
    
    if mutated_code == "<NO-OP>":
        # Comment out the original line
        lines[line_index] = "// " + lines[line_index].rstrip() + "  // <no-op>\n"
    else:
        # Replace original code with mutated code
        lines[line_index] = lines[line_index].replace(original_code, mutated_code)

    # Write the modified lines back to the file.
    with open(target_file_path, "w") as file:
        file.writelines(lines)


def build_data_from_mutation(p,t,n):
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

    kill_file_path = data_path + f"/kill/kill.{t}.csv"
    log_file_path =  data_path + f"/log/mutants.{t}.log"

    if os.path.exists(kill_file_path):
        with open(kill_file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            kill_data = list(reader)
    else:
        print(f"{kill_file_path} not found.")
        return 0

    if os.path.exists(log_file_path):
        with open(log_file_path, encoding='utf-8') as f:
            log_data = [line.strip() for line in f]
    else:
        print(f"{log_file_path} not found.")
        return 0
    
    test_command = f"defects4j test -w {project_path}"
    
    #if p=="Closure":
    if p=="Time":
        bug_id = 4
    elif p=="Math":
        pass
    else:
        bug_id = 1
    target_file_path = construct_path(base_path,p,bug_id) + "/"+t.replace('.','/') + ".java"
    if not os.path.exists(target_file_path):
        print("target_file not existing")
        return 0

    fail_count = 0

    fail_entries = [(i, row) for i, row in enumerate(kill_data) if row[1] == 'FAIL']
    
    if len(fail_entries) > n:
        print(f"Length : {len(fail_entries)}, just using {n}")
        fail_entries = random.sample(fail_entries, n)

    fail_count = len(fail_entries)

    selected_fail_indices = set(int(i) for _, [i,_] in fail_entries)
    
    well_done_count = 0
    for i in range(len(log_data)+1):
        if i in selected_fail_indices:
            reset(p)
            parsed = parse_log_data(log_data[i-1])
            try:
                apply_mutation(target_file_path, parsed)
            except Exception as e:
                print(e)
                continue
            print(parsed)
            try:
                output = run_command(test_command)
            except Exception as e:
                print(e)
                continue
            print(output)
            target_file = project_path + "/failing_tests"
            destination = data_path + f"/results/failing_tests__{t}__{parsed['ID']}"
            
            if os.path.isfile(target_file):
                shutil.copy2(target_file, destination)
                well_done_count+=1
            else:
                print("No failing test!")
            reset(p)

            #return 1
#reset("Closure")
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.TypedScopeCreator", 35)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.parsing.IRFactory", 35)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.TypeCheck", 35)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.NodeUtil", 30)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.Compiler", 35)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.CodeConsumer", 35)
#build_data_from_mutation("Closure", "com.google.javascript.rhino.jstype.NamedType", 35)

#build_data_from_mutation("Closure", "com.google.javascript.jscomp.RemoveUnusedVars",30)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.OptimizeCalls",10)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.GoogleCodingConvention",10)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.AnalyzePrototypeProperties",30)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.MaybeReachingVariableUse",30)
#build_data_from_mutation("Closure", "com.google.javascript.rhino.IR",30)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.CollapseVariableDeclarations",30)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.UnrechableCodeElimination",30)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.FunctionToBlockMutator",30)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.CommandLineRunner",30)
#build_data_from_mutation("Closure", "com.google.javascript.rhino.jstype.FunctionParamBuilder",10)
#build_data_from_mutation("Closure", "com.google.javascript.rhino.TokenStream",30)

#build_data_from_mutation("Closure", "com.google.javascript.jscomp.LiveVariableAnalysis",30)
#build_data_from_mutation("Closure", "com.google.javascript.jscomp.FunctionRewriter",30)
