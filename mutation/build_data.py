import csv
from run_command import run_command
import os

def build_class_mutation_data(p, t):
    base_path = "/home/yinseok/lorafl"
    if p == "Closure":
        path = "/home/yinseok/lorafl/temp/Closure_1/Closure_1_fixed"
    elif p=="Chart":
        path = "/home/yinseok/lorafl/temp/Chart_1/Chart_1_fixed"
    elif p=="Math":
        path = f"/home/yinseok/lorafl/temp/{p}_2/{p}_2_fixed"
    elif p=="Lang":
        path = f"/home/yinseok/lorafl/temp/{p}_1/{p}_1_fixed"
    elif p=="Time":
        path = f"/home/yinseok/lorafl/temp/{p}_4/{p}_4_fixed"

    i_path = path + "/instrumented_class.txt"  # make sure to add "/" if needed

    # Write 't' to the file
    with open(i_path, 'w', encoding='utf-8') as f:
        f.write(t)
    
    
    mutation_command = f"defects4j mutation -w {path} -i {i_path}"
    print(mutation_command)
    output = run_command(mutation_command)
    
    print(output)
    
    kill_path = path + "/kill.csv"
    log_path = path + "/mutants.log"
    
    if os.path.exists(kill_path):
        os.rename(kill_path, base_path + f"/mutation_data/{p}/kill/kill.{t}.csv")
    if os.path.exists(log_path):
        os.rename(log_path, base_path + f"/mutation_data/{p}/log/mutants.{t}.log")

#build_class_mutation_data("Closure","com.google.javascript.jscomp.TypedScopeCreator")
#build_class_mutation_data("Closure","com.google.javascript.jscomp.parsing.IRFactory")
#build_class_mutation_data("Closure","com.google.javascript.jscomp.TypeCheck")
#build_class_mutation_data("Closure","com.google.javascript.jscomp.NodeUtil")
#build_class_mutation_data("Closure","com.google.javascript.jscomp.Compiler")
#build_class_mutation_data("Closure","com.google.javascript.jscomp.CodeConsumer")
#build_class_mutation_data("Closure","com.google.javascript.rhino.jstype.NamedType")
