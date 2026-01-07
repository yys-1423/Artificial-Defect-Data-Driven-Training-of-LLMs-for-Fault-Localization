import os
import json
import csv
import copy
from collections import Counter
import random
import re
from helper_source.extract_pakcage_dataset import extract_package_data
from helper_source.extract_class_dataset import extract_class_dataset
from helper_source.extract_enum_dataset import extract_enum_dataset
from helper_source.extract_interface_dataset import extract_interface_dataset
from helper_source.extract_method_dataset import extract_method_dataset
from helper_source.extract_constructor_dataset import extract_constructor_dataset

detailed_summary_closure = [
        """What is Closure Compiler?
Closure Compiler is a JavaScript optimizer and static analyzer developed by Google. It's not a traditional compiler that translates code into machine language. Instead, it transforms and optimizes JavaScript code to make it smaller, faster, and more robust.

Distinction Between "Closure" and "Closure Compiler"
Closure (JavaScript concept): A closure is a feature of JavaScript where an inner function retains access to variables of its outer function even after that outer function has returned. This enables private data, function factories, and scoped state.


function outer() {
  let message = "Hello";
  function inner() {
    console.log(message);
  }
  return inner;
}
const closureFn = outer();
closureFn(); // Logs "Hello"
Closure Compiler (Google project): Despite sharing the name, the compiler’s name comes from its use in Google's Closure Tools, not directly from the closure concept itself.

Main Objectives of Closure Compiler
Closure Compiler aims to analyze and optimize JavaScript code. It is especially suited for large-scale web applications where performance and correctness are critical.

1. Dead Code Elimination
Analyzes dependency trees and removes functions, variables, and code paths that are never used.

This reduces the final bundle size and eliminates redundant logic.

2. Minification and Renaming
Renames variables and functions to shorter names to reduce code size.

Strips whitespace and comments.

In ADVANCED mode, it aggressively renames even object properties—only safe if all source code is visible to the compiler.

3. Static Type Checking
Closure Compiler can infer or explicitly validate types using JSDoc.

Example:

/** @param {number} x */
function double(x) {
  return x * 2;
}
double("hi"); // Compiler will warn: "Expected number but got string."
4. Performance Optimization
It rewrites JavaScript in semantically equivalent but faster forms.

In ADVANCED mode, it can inline functions, fold constants, remove unused parameters, and more.

5. Transpilation
Can convert modern JavaScript (ES6+) into ES5 for broader browser support.

Handles language features like arrow functions, classes, destructuring, etc.

Compilation Levels
Closure Compiler supports three levels of compilation:

Level	Description
WHITESPACE_ONLY	Removes comments and whitespace only. Minimal transformation.
SIMPLE	Renames local variables, removes dead code, preserves public APIs.
ADVANCED	Aggressively renames and rewrites code. Best compression, but requires full control and careful design.
Challenges with ADVANCED Mode
Requires code to be fully annotated with JSDoc or written with compiler in mind.

Can break code that dynamically accesses properties using string names or reflects over its own structure.

External libraries need to be explicitly declared using externs files to prevent breaking changes.

Build Tool and Ecosystem Integration
Available as:

Java JAR

npm package (google-closure-compiler)

Web UI (Closure Compiler Service)

Can be integrated into build pipelines like Webpack, Gulp, or used directly via CLI.

Used In Production By Google
Used internally at Google for Gmail, Google Docs, and other large apps.

Enables high-scale deployment with minimal payload size and better maintainability.

Summary
Closure Compiler is a powerful tool for JavaScript optimization, especially in large codebases. It goes beyond typical minifiers by providing:

Advanced static analysis

Dead code elimination

Aggressive compression

Type checking and early error detection

However, it comes with a learning curve and requires careful code design, especially in ADVANCED mode. With proper use, it can drastically improve performance and reliability of web applications.""",
"""Closure Compiler is a tool made by Google to help make JavaScript code smaller, faster, and less buggy. It's called a “compiler,” but it doesn’t turn JavaScript into machine code. Instead, it improves the JavaScript code you already wrote.

What Does It Do?
Removes Unused Code

Deletes any code that isn’t actually used, making your file smaller.

Minifies and Renames

Makes variable names short like a, b, c, and removes spaces and comments.

Checks for Errors

Finds syntax mistakes or wrong types (like using a string when a number is expected).

Optimizes the Code

Makes the code run faster by simplifying it behind the scenes.

Transpiles Code

Can convert modern JavaScript (like ES6) into older versions for browser support.

Compilation Levels
Level	What It Does
WHITESPACE_ONLY	Removes only spaces and comments.
SIMPLE	Renames local variables and removes unused code safely.
ADVANCED	Aggressively rewrites and renames code. Gives best results but needs careful setup.
Why Use It?
Great for big websites and web apps

Helps catch bugs before the browser does

Makes files smaller, so they load faster

Used by Google on products like Gmail and Docs

Things to Watch Out For
In ADVANCED mode, it can break code if you don’t write it the right way.

You may need to use special comments (JSDoc) or define externs for external libraries.

Summary
Closure Compiler is like a super-smart assistant for JavaScript. It cleans your code, checks it for problems, and makes it fast. It takes some effort to set up, especially for advanced use, but it's powerful and reliable—Google uses it every day
""",
"""
Closure Compiler is a tool that does following :

1. Dead Code Elimination
What it does: Removes functions, variables, and code paths that are never used.

Why it matters: Reduces the final file size and makes the code cleaner.

2. Minification
What it does: Shortens variable and function names, strips whitespace and comments.

Why it matters: Makes code faster to download and harder to reverse-engineer.

3. Type Checking
What it does: Uses type annotations (like JSDoc) to detect type mismatches and bugs before running the code.

Why it matters: Helps catch errors early, improves code reliability.

4. Syntax Validation
What it does: Checks the JavaScript for syntax errors.

Why it matters: Prevents broken scripts from being deployed.

5. Code Optimization
What it does: Rewrites code into simpler or faster versions without changing its behavior.

Examples: Inlining functions, removing unused parameters, combining statements.

Why it matters: Improves runtime performance.

6. Transpilation
What it does: Converts modern JavaScript (like ES6+) into older versions (like ES5).

Why it matters: Ensures compatibility with older browsers.

7. Module & Dependency Management
What it does: Understands and compiles code split into modules using goog.module or ES modules.

Why it matters: Helps manage large codebases with many files.

8. Externs Handling
What it does: Protects external code (like libraries) from being renamed or removed.

Why it matters: Prevents breaking third-party APIs or frameworks.

How It Works (High-Level)
Parse your JavaScript into an abstract syntax tree (AST)

Analyze the code (types, usage, dependencies)

Optimize by removing and rewriting parts

Output optimized JavaScript

""",
"""
# 🛠️ Closure Compiler: Detailed Functional Overview

**Closure Compiler** is a powerful JavaScript **optimizer, analyzer, and transpiler** created by Google. Unlike traditional compilers, it does not generate machine code — instead, it rewrites and improves JavaScript for performance, size, and reliability.

---

## 1. Dead Code Elimination (Tree Shaking)

- **What it does:**  
  Removes:
  - Unused functions and variables  
  - Unreachable code (e.g., `if (false) { ... }`)
- **Why it matters:**  
  Reduces bundle size and makes code cleaner.

---

## 2. Minification

- **What it does:**  
  - Renames variables and functions (`userName → a`)  
  - Removes whitespace, comments, and unnecessary characters
  - Strips debug code in ADVANCED mode
- **Levels:**
  - `SIMPLE`: Safe variable renaming
  - `ADVANCED`: Aggressive minification including property renaming
- **Why it matters:**  
  Smaller files, faster downloads, obfuscated code

---

## 3. Type Checking (Static Type Inference)

- **What it does:**  
  - Uses [JSDoc](https://github.com/google/closure-compiler/wiki/Annotating-JavaScript-for-the-Closure-Compiler) to enforce or infer types  
  - Detects type mismatches
- **Example:**
  ```js
  /** @param {number} x */
  function square(x) {
    return x * x;
  }
  square("hello"); // Type warning
Why it matters:
Helps catch bugs early, improves documentation

4. Syntax and Semantic Validation
What it does:

Detects common JavaScript mistakes:

Syntax errors

Undeclared variables

Incorrect property accesses

Why it matters:
Prevents runtime issues and enforces good practices

5. Code Optimization
What it does:

Inlines functions

Performs constant folding (e.g., 2 + 2 → 4)

Removes unused parameters

Flattens scopes and simplifies expressions

Why it matters:
Faster runtime performance, less memory usage

6. Transpilation (ES6+ to ES5)
What it does:

Converts modern JS features:

let, const, arrow functions

Classes and modules

Outputs ES5 code for legacy browser support

Why it matters:
Write modern code, run it anywhere

7. Module & Dependency Management
What it does:

Supports:

Closure modules (goog.module, goog.require)

ES modules (import, export)

Automatically resolves and orders dependencies

Why it matters:
Keeps large codebases organized and modular

8. Externs Support
What it does:

Protects external libraries from being renamed or removed

Used to define global APIs (e.g., jQuery, window, document)

Example:

js
/** @externs */
var $;
Why it matters:
Prevents breakage of third-party APIs or browser globals

9. Testable, Repeatable Builds
What it does:

Deterministic output for the same input

Works well in CI/CD pipelines

Supports:

CLI

Java JAR

Node.js (google-closure-compiler npm package)

Tools like Webpack, Gulp, Bazel
""",
"""
Google's Closure Compiler is a sophisticated tool designed to optimize JavaScript code through a combination of static analysis, code transformation, and performance enhancement. At its core, Closure Compiler is not a traditional compiler that converts source code into machine language; rather, it takes JavaScript code as input and rewrites it into more efficient, compact, and robust output. One of its key capabilities is dead code elimination, where the compiler intelligently removes unused variables, functions, and statements from the codebase. This process significantly reduces file size and removes redundancy, which is crucial for maintaining fast-loading web applications.

Another major functionality of Closure Compiler is minification, which involves renaming variables and functions to shorter names and stripping out whitespace and comments. This results in reduced bandwidth usage and improved load times, especially for resource-constrained environments. In addition to size optimization, the compiler performs type checking and validation using JSDoc annotations and built-in inference mechanisms. This helps developers catch type mismatches and potential runtime errors early in the development cycle. The type checker also ensures that properties are accessed on valid objects and that constructors and functions are used correctly, enhancing overall code safety.

Closure Compiler also supports transpilation, converting modern ECMAScript syntax into older ES5 code to ensure compatibility across different browsers and environments. This feature allows developers to write modern, expressive JavaScript while still supporting legacy platforms. The tool handles module and dependency management through support for Closure Library modules (goog.module, goog.require) as well as standard ES modules, making it suitable for large-scale codebases. It can resolve dependencies and ensure proper order of execution during compilation.

A particularly powerful mode offered by the compiler is ADVANCED_OPTIMIZATIONS, which applies aggressive transformations to maximize performance and minimize output. In this mode, even object properties can be renamed, and internal function structures may be inlined or collapsed, provided the entire codebase is visible to the compiler. This results in highly compact and performant code, although it requires careful design to ensure compatibility. To facilitate safe interaction with external libraries or browser APIs, Closure Compiler supports externs files, which explicitly declare identifiers that should not be modified during compilation.

Finally, Closure Compiler ensures repeatable and testable builds by operating deterministically—identical input always results in identical output. It is available through various interfaces including a command-line tool, Java JAR file, and a Node.js package, and it integrates well with modern build tools and CI pipelines. Overall, Closure Compiler is a powerful and flexible solution for JavaScript developers seeking to build reliable, efficient, and production-ready web applications.
""",
"""
Closure Compiler is a powerful JavaScript optimization tool developed by Google, designed to make web applications faster, smaller, and more reliable. Rather than compiling JavaScript into machine code, Closure Compiler reads JavaScript code and rewrites it into a more efficient form while preserving its behavior. Its core strength lies in performing advanced static analysis, transforming source code by removing unnecessary parts, simplifying expressions, and minifying names. This results in significantly smaller scripts that load quickly in the browser and consume less bandwidth.

One of the most notable features of Closure Compiler is its ability to eliminate unused code. It scans the entire codebase to detect variables, functions, and expressions that are never referenced, and removes them from the output. This “tree shaking” process ensures that only what’s actually needed in the application gets deployed. In addition to removing dead code, Closure Compiler applies aggressive minification techniques, shortening variable names, removing comments and whitespace, and consolidating code without affecting functionality. These changes make the JavaScript code both compact and difficult to reverse-engineer.

Beyond size optimization, Closure Compiler offers a robust type-checking system. It can infer types automatically or work with developer-provided annotations using JSDoc syntax. This system helps detect inconsistencies and potential runtime errors before deployment, such as calling functions with the wrong arguments or accessing undefined properties. Its static analysis also assists in validating correct usage of JavaScript features like object prototypes, inheritance, and strict mode. When used in larger projects, these checks encourage better code hygiene and can prevent hard-to-find bugs.

Another strength of Closure Compiler is its ability to transpile modern JavaScript into older versions like ES5, ensuring compatibility with a wide range of browsers. This allows developers to write modern, maintainable code while still supporting legacy environments. Closure Compiler also supports module systems, enabling developers to build complex applications using modular code while ensuring that the compiled output is properly ordered and resolved. It works well with both Google’s Closure Library modules and standard ECMAScript modules.

Finally, Closure Compiler integrates smoothly into development and build pipelines. It can be used via command-line interfaces, Java-based tools, or Node.js, and supports integration with build tools like Webpack or Gulp. With its ability to generate source maps, support strict mode, and enforce consistent coding standards, Closure Compiler provides a comprehensive solution for preparing production-grade JavaScript. It remains a cornerstone in optimizing front-end performance for applications that demand both reliability and efficiency at scale."""

]

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

def extract_package_level_data(p):
    package_path = "data_original/" + p + "/" + p + "_package_summary.json"

    with open(package_path, 'r', encoding='utf-8') as f:
        package_data = json.load(f)

    class_list = extract_class_csv(p)

    #print(len(package_data))
    stat = extract_stat(package_data,class_list)
    #print(stat)

    grouped_stat = group_stats(stat)
    #print(grouped_stat)
    dataset = []

    for i,package in enumerate(package_data):
        name = package["name"]
        description = package["content"]
        fs = package["file_structure"]

        dataset.append([name,description,fs,grouped_stat[i]])

    
    #number of datapoints for each group


    #dataset format = [ name , description, [fs] , priority ]
    return dataset

def extract_data(data, upper_classes, category):
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
            new_category = max(0,category-2)
            inner_class, inner_method, inner_gv = extract_data(inner,new_upper_classes,new_category)
            class_data.extend(inner_class)
            method_data.extend(inner_method)
            gv_data.extend(inner_gv)

            processed_innertypes.append([inner["name"],inner["type"]])
    
    class_data.append([name,comment,type_,package_name,processed_innertypes,processed_methods, implementedTypes, extended_type, upper_classes,enum, category ])
    for method in methods:
        method_data.append([method["name"], method["comment"], "method", method["signature"], name, type_, package_name, method["snippet"], upper_classes, category])
    for constructor in constructors:
        method_data.append([constructor["signature"], constructor["comment"], "constructor", constructor["signature"], name, type_, package_name, constructor["snippet"], upper_classes, category])
    for gv in gvs:
        gv_data.append([gv["signatureLeft"], gv["signatureRight"], gv["comment"], name, type_, upper_classes, category])
    return class_data, method_data, gv_data

def classify_all(lists):
    buckets = [[], [], [], []]
    
    for lst in lists:
        label = lst[-1]
        buckets[label].append(lst)
    
    return buckets

def extract_class_level_data(p):
    class_path = "data_original/" + p + "/classes.csv"

    with open(class_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        classes_list = list(reader)


    class_data = []
    method_data = []
    gv_data = []
    package_data = extract_package_level_data(p)

    for target_class in classes_list:

        category = int(target_class['category'])

        file_path =   "data_original/" + p + "/output_source2/" + target_class["filename"]
        if not os.path.exists(file_path):
            print(f"File not found <extract_class_level_data>: {file_path}")
            return -1
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        rv = extract_data(data, [] , category)
        if rv != -1:
            cd,md,gd = rv
            class_data.extend(cd)
            method_data.extend(md)
            gv_data.extend(gd)
    
    #print(len(class_data), len(method_data), len(gv_data))

    #summary = summarize_last_elements([class_data, method_data, gv_data])
    #print(summary)

    classified_package = classify_all(package_data)
    classified_class = classify_all(class_data)
    classified_methods = classify_all(method_data)
    classified_gv = classify_all(gv_data)
    print("Package:", [len(lst) for lst in classified_package])
    print("Class:  ", [len(lst) for lst in classified_class])
    print("Methods:", [len(lst) for lst in classified_methods])
    print("GV:     ", [len(lst) for lst in classified_gv])

    
    with open("closure_data.jsonl", "w", encoding="utf-8") as f:
        
        ### Project Data Begin
        project_data_count = 0
        for i in range(2):
            for s in detailed_summary_closure:
                json_line = {
                    "input": "### Task: Project Summarization\nPlease generate a detailed summary of the target project below.\n\n### Target Project: Closure Compiler\n",
                    "output": s
                }
                f.write(json.dumps(json_line, ensure_ascii=False) + "\n")
                project_data_count+=1

        for i in range(2):
            for s in simple_summary_closure:
                json_line = {
                    "input": "### Task: Project Summarization\nPlease generate a simple summary of the target project below.\n\n### Target Project: Closure Compiler\n",
                    "output": s
                }
                f.write(json.dumps(json_line, ensure_ascii=False) + "\n")
                project_data_count+=1
        


        ### Package Data Begin
        package_data_count = 0
        sample_0 = random.sample(classified_package[0], max(1, len(classified_package[0]) // 2))
        for p in sample_0:
            json_lines = extract_package_data(p,simple_summary_closure)
            package_data_count+=len(json_lines)
            for json_line in json_lines:
                f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

       
        for p in classified_package[1]:
            json_lines = extract_package_data(p,simple_summary_closure)
                
            package_data_count+=len(json_lines)
            for json_line in json_lines:
                f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

        for i in range(2):
            for p in classified_package[2]:
                json_lines = extract_package_data(p,simple_summary_closure)
                package_data_count+=len(json_lines)
                for json_line in json_lines:
                    f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

        for i in range(5):
            for p in classified_package[3]:
                json_lines = extract_package_data(p,simple_summary_closure)
                package_data_count+=len(json_lines)
                for json_line in json_lines:
                    f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

        ### Class Data Begin

        class_data_count = 0

        sample_0 = random.sample(classified_class[0], max(1, len(classified_class[0]) // 5))
        for p in sample_0:
            if p[2]=="class":
                json_lines = extract_class_dataset(p,simple_summary_closure)
            elif p[2] == "interface":
                json_lines = extract_interface_dataset(p,simple_summary_closure)
            elif p[2] == "enum":
                json_lines = extract_enum_dataset(p,simple_summary_closure)
            else:
                print(p)
            class_data_count+=len(json_lines)
            for json_line in json_lines:
                f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

        
        for p in classified_class[1]:
            if p[2]=="class":
                json_lines = extract_class_dataset(p,simple_summary_closure)
            elif p[2] == "interface":
                json_lines = extract_interface_dataset(p,simple_summary_closure)
            elif p[2] == "enum":
                json_lines = extract_enum_dataset(p,simple_summary_closure)
            else:
                print(p)
            class_data_count+=len(json_lines)
            for json_line in json_lines:
                f.write(json.dumps(json_line, ensure_ascii=False) + "\n")

        for i in range(2):
            for p in classified_class[2]:
                if p[2]=="class":
                    json_lines = extract_class_dataset(p,simple_summary_closure)
                elif p[2] == "interface":
                    json_lines = extract_interface_dataset(p,simple_summary_closure)
                elif p[2] == "enum":
                    json_lines = extract_enum_dataset(p,simple_summary_closure)
                else:
                    print(p)
                class_data_count+=len(json_lines)
                for json_line in json_lines:
                    f.write(json.dumps(json_line, ensure_ascii=False) + "\n")


        for i in range(5):
            for p in classified_class[3]:
                if p[2]=="class":
                    json_lines = extract_class_dataset(p,simple_summary_closure)
                elif p[2] == "interface":
                    json_lines = extract_interface_dataset(p,simple_summary_closure)
                elif p[2] == "enum":
                    json_lines = extract_enum_dataset(p,simple_summary_closure)
                else:
                    print(p)
                class_data_count+=len(json_lines)
                for json_line in json_lines:
                    f.write(json.dumps(json_line, ensure_ascii=False) + "\n")
        
        ### For methods
        method_data_count = 0

        sample_0 = random.sample(classified_methods[0], max(1, len(classified_methods[0]) // 20))
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
        # 1/5 of classified_methods[1]
        sample_1 = random.sample(classified_methods[1], max(1, len(classified_methods[1]) // 2))
        for p in sample_1:
            if p[2]=="method":
                json_lines = extract_method_dataset(p,simple_summary_closure)
            elif p[2] == "constructor":
                json_lines = extract_constructor_dataset(p,simple_summary_closure)
            else:
                print(p)
            method_data_count+=len(json_lines)
            for json_line in json_lines:
                f.write(json.dumps(json_line, ensure_ascii=False) + "\n")
        

        for p in classified_methods[2]:
            if p[2]=="method":
                json_lines = extract_method_dataset(p,simple_summary_closure)
            elif p[2] == "constructor":
                json_lines = extract_constructor_dataset(p,simple_summary_closure)
            else:
                print(p)
            method_data_count+=len(json_lines)
            for json_line in json_lines:
                f.write(json.dumps(json_line, ensure_ascii=False) + "\n")
        

        for i in range(2):
            for p in classified_methods[3]:

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

        print("project", project_data_count)
        print("package", package_data_count)
        print("class", class_data_count)
        print("method", method_data_count)
        print("gv", gv_data_count)

    
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
    extract_class_level_data(p)
