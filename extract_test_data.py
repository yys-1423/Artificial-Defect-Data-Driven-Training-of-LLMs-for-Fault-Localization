import os
import json
import csv
import copy
from collections import Counter
import random
import re
from helper_test.extract_class_dataset import extract_class_dataset
from helper_test.extract_method_dataset import extract_method_dataset
from helper_test.extract_constructor_dataset import extract_constructor_dataset
import glob

simple_summary_closure = [
"""Closure Compiler is a JavaScript optimization tool by Google that reduces code size and improves performance by removing unused code and minifying variable names. It also performs type checking and code analysis to catch potential errors before runtime. Additionally, it supports modern JavaScript features and ensures compatibility with older browsers through transpilation.""",
"""Closure Compiler is a tool that helps make JavaScript code faster and smaller by analyzing and rewriting it. It removes unused code, shortens variable names, and checks for errors using static analysis. It also allows developers to write modern JavaScript while ensuring it works in older browsers.""",
"""Closure Compiler is an advanced JavaScript optimizer that rewrites code to improve speed and reduce file size. It offers features like dead code removal, minification, and type checking. Developers use it to create efficient, reliable, and browser-compatible web applications.""",
"""Closure Compiler is a tool that optimizes JavaScript by removing unused code, shortening variable names, and checking for errors. It helps developers create faster, smaller, and more reliable web applications.""",
"""Closure Compiler improves JavaScript code by analyzing and transforming it for better performance and smaller file size. It also ensures code quality through type checking and supports modern-to-legacy JavaScript conversion.""",
"""Closure Compiler supports large-scale JavaScript development by managing modules and enforcing coding standards. It integrates well with build tools, making it suitable for complex projects that require consistent and maintainable code.""",
"""Closure Compiler enhances JavaScript by optimizing code structure and applying advanced transformations like minification and dead code elimination. It also supports modularity and compatibility with older browsers, making it ideal for large-scale web applications.""",
"""Closure Compiler is a JavaScript optimization tool that streamlines code, supports modular development, and ensures compatibility across browsers.""",
"""Closure Compiler transforms JavaScript code to be faster, smaller, and more maintainable for production use.""",
"""Closure Compiler analyzes, optimizes, and rewrites JavaScript code by removing unused code, minifying variables, and checking for errors.""",
"""Closure Compiler is a JavaScript compiler that transforms source code into a more efficient version through static analysis, optimization, and code generation.""",
"""Closure Compiler is a compiler that processes JavaScript code to improve performance by analyzing, optimizing, and rewriting it into a more compact and efficient form.""",
"""Closure Compiler transforms JavaScript code by analyzing, optimizing, and rewriting it for efficiency.""",
"Closure Compiler enhances JavaScript by analyzing, optimizing, and minimizing code for better performance.",
"Closure Compiler improves code efficiency by performing analysis, optimization, and transformation during compilation.",
"Google’s Closure Compiler optimizes JavaScript by stripping out unused code and shortening identifiers to shrink bundle size and boost execution speed.",
"Closure Compiler speeds up and shrinks JavaScript by analyzing and rewriting source files.",
"Closure Compiler is a sophisticated optimizer that rewrites JavaScript for faster performance and smaller output.",
"Closure Compiler strips unused code, abbreviates identifiers, and detects errors to optimize JavaScript.",
"Closure Compiler analyzes and transforms JavaScript into a smaller, higher‑performance form.",
"Closure Compiler streamlines large‑scale development by managing modules and enforcing consistent coding practices.",
"Closure Compiler refines code structure and applies advanced transformations like minification and tree shaking."
"Closure Compiler streamlines JavaScript, enforces modular architecture, and ensures cross‑browser support."
"Closure Compiler converts JavaScript into a lean, high‑performance, production‑ready format."
"Closure Compiler analyzes and rewrites code to remove dead paths, compress identifiers, and catch errors."
"Closure Compiler compiles JavaScript into a more efficient form via static analysis and code generation."
"Closure Compiler processes JavaScript to boost performance by analyzing, optimizing, and compacting source code."
"Closure Compiler enhances efficiency by analyzing, optimizing, and rewriting JavaScript."
"Closure Compiler optimizes JavaScript by removing unused code and shortening identifiers to dramatically reduce file size."
]


def remove_known_html_tags(text):
    """
    Removes only known HTML tags from the text (e.g., <p>, </p>, <ul>, <li>, etc.).
    Leaves other non-HTML angle bracket content untouched.
    """
    known_tags = [
        'p', 'ul', 'ol', 'li', 'div', 'span', 'br', 'strong', 'em',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'
    ]
    
    # Build regex pattern to match open and close tags for each known HTML tag
    pattern = '|'.join([fr'</?{tag}[^>]*>' for tag in known_tags])
    
    return re.sub(pattern, '', text, flags=re.IGNORECASE)

def summarize_last_elements(data_lists):
    summaries = []
    for data in data_lists:
        counter = Counter([item[-1] for item in data])
        summary = [f"{k}:{counter.get(k, 0)}" for k in range(4)]
        summaries.append(summary)
    return summaries
projects = ["Chart","Closure", "Lang", "Math", "Math3", "Time"]

p = "Closure"
def group_stats(stat):
    group = [0] * len(stat)
    scores = []

    # Step 1: Compute scores for entries with point != 0
    for i, (count, point,package) in enumerate(stat):
        if point!= 0:
            score = (point * point * point * (package+1)) / (count * count)
            scores.append((score, i))

    # Step 2: Sort scores
    scores.sort()
    total = len(scores)
    chunk = total // 3
    remainder = total % 3

    # Step 3: Assign to groups 1, 2, 3
    idx = 0
    for g in range(1, 4):  # Group IDs: 1, 2, 3
        size = chunk + (1 if remainder > 0 else 0)
        remainder -= 1 if remainder > 0 else 0
        for _ in range(size):
            _, original_idx = scores[idx]
            group[original_idx] = g
            idx += 1
    return group

def extract_stat(package_data, class_list):
    stat = []
    for package in package_data:
        total_category = 0
        count = 0
        total_package = 0
        for  existing_class in package["file_structure"]:
            existing_class = existing_class.removesuffix(".java")
            count +=1
            found = False
            for entry in class_list:
                if entry[0] == package["name"] and entry[1] == existing_class:
                    total_category += entry[2]
                    found = True
                    break
            if not found:
                total_package +=1
        temp = [count, total_category, total_package]
        stat.append(temp)
    return stat

def extract_class_csv(p):
    class_path = "data_original/" + p + "/classes.csv"
    with open(class_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        class_list = list(reader)
    new_class_list = [
        [f"{item['packageName']}", f"{item['name']}", int(item['category'])]
        for item in class_list
    ]
    return new_class_list



def extract_data(data, upper_classes):
    type_ = data["type"]
    if type_ == "enum":
        try:
            name = data["name"]
            package_name = data["packageName"]
            type_ = data["type"]
            path = data["path"]
            comment = data["comment"]
            extended_type = data["extendedTypes"]
            implementedTypes = data["implementedTypes"]
            constructors = []
            gvs = []
            methods = data["methods"]
            innertypes = []

        except KeyError as e:
            print(f"Missing expected key in JSON <extract_data>: {e}")
            return -1
    else:        
        try:
            name = data["name"]
            package_name = data["packageName"]
            type_ = data["type"]
            path = data["path"]
            comment = data["comment"]
            extended_type = data["extendedTypes"]
            implementedTypes = data["implementedTypes"]
            constructors = data["constructors"]
            gvs = data["globalVariables"]
            methods = data["methods"]
            innertypes = data["innerTypes"]

        except KeyError as e:
            print(f"Missing expected key in JSON <extract_data>: {e}")
            return -1
    
    if type_ == "enum":
        enum = data["enumConstants"]
    else:
        enum = []
    

    """
    dataset format = [
        [], # class       [   className, classComments, classType, PackageName,  [[InnertypeName, Innertype_Type]], [Method Names],  [Implemented Types], [Extended Types] , [Upper_classes], [enumconstants], category]
        [], # Method      [   methodName, MethodComments, MethodType, MethodSignature, ClassName, ClassType, PackageName, Snippet, [Upper_classes], category]
        []  # GV          [   GV_left, GV_right, GV_comment, class_name, Class_type, [Upper_classes], category ]
    ]
    """    


    processed_methods = [d['name'] for d in methods]

    class_data = []
    method_data = []
    gv_data = []

    processed_innertypes = []
    if len(innertypes)!=0:
        for inner in innertypes:
            
            #print()
            #print(upper_classes)
            new_upper_classes = copy.deepcopy(upper_classes)
            new_upper_classes.append(name)
            #print(inner["name"], new_upper_classes)
            inner_class, inner_method, inner_gv = extract_data(inner,new_upper_classes)
            class_data.extend(inner_class)
            method_data.extend(inner_method)
            gv_data.extend(inner_gv)

            processed_innertypes.append([inner["name"],inner["type"]])
    
    class_data.append([name,comment,type_,package_name,processed_innertypes,processed_methods, implementedTypes, extended_type, upper_classes,enum])
    for method in methods:
        method_data.append([method["name"], method["comment"], "method", method["signature"], name, type_, package_name, method["snippet"], upper_classes])
    for constructor in constructors:
        method_data.append([constructor["signature"], constructor["comment"], "constructor", constructor["signature"], name, type_, package_name, constructor["snippet"], upper_classes])
    for gv in gvs:
        gv_data.append([gv["signatureLeft"], gv["signatureRight"], gv["comment"], name, type_, upper_classes])
    return class_data, method_data, gv_data

def classify_all(lists):
    buckets = [[], [], [], []]
    
    for lst in lists:
        label = lst[-1]
        buckets[label].append(lst)
    
    return buckets

def extract_test_data(p):
    class_path = "data_original/" + p + "/output_test2"

    json_files = glob.glob(os.path.join(class_path, "*.json"))

    class_data = []
    method_data = []
    gv_data = []

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        rv = extract_data(data, [] )
        if rv != -1:
            cd,md,gd = rv
            class_data.extend(cd)
            method_data.extend(md)
            gv_data.extend(gd)
    
    

    #summary = summarize_last_elements([class_data, method_data, gv_data])
    #print(summary)



    print("Class:  ", len(class_data))
    print("Methods:", len(method_data))
    print("GV:     ", len(gv_data))
    
    with open("closure_test_data.jsonl", "w", encoding="utf-8") as f:
        

        ### Class Data Begin

        class_data_count = 0

        for i in range(2):
            for p in class_data:
                if p[2]=="class":
                    json_lines = extract_class_dataset(p,simple_summary_closure)
                else:
                    pass
                class_data_count+=len(json_lines)
                for json_line in json_lines:
                    f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

        

        
        ### For methods
        method_data_count = 0

        sample_0 = random.sample(method_data, max(1, len(method_data) // 2))
        for p in sample_0:
            if p[2]=="method":
                json_lines = extract_method_dataset(p,simple_summary_closure)
            elif p[2] == "constructor":
                json_lines = extract_constructor_dataset(p,simple_summary_closure)
            else:
                print(p)
            method_data_count+=len(json_lines)
            for json_line in json_lines:
                f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

        


        
        ### For gv
        """
        gv_data_count = 0

        selected = random.sample(classified_gv[0], len(classified_gv[0]) // 20)
        for p in selected:
            gv_data_count += 1

        selected = random.sample(classified_gv[1], len(classified_gv[1]) // 5)
        for p in selected:
            gv_data_count += 1

        selected = random.sample(classified_gv[2], len(classified_gv[2]) // 2)
        for p in classified_gv[2]:
            gv_data_count += 1


        for p in classified_gv[3]:
            gv_data_count += 1
        """

        print("class", class_data_count)
        print("method", method_data_count)
        #print("gv", gv_data_count)

    
    """
    dataset format = [
        [], # class       [   className, classComments, classType, PackageName,  [[InnertypeName, Innertype_Type]], [Method Names],  [Implemented Types], [Extended Types] , [Upper_classes], category]
        [], # Method      [   methodName, MethodComments, MethodType, MethodSignature, ClassName, ClassType, PackageName, Snippet, [Upper_classes], category]
        []  # GV          [   GV_left, GV_right, GV_comment, class_name, Class_type, [Upper_classes], category ]
    ]
    """    




#extract_package_level_data(p)
#extract_class_level_data(p,"com.google.javascript.rhino.jstype.EnumType")
#extract_class_level_data(p,"com.google.javascript.jscomp.CompilerOptions")
#extract_class_level_data(p,"com.google.javascript.jscomp.SubclassType")
#
if __name__ == "__main__":
    p = "Closure"
    extract_test_data(p)
