import os
import csv
import re
import random
import json

from extract_method_coverage import extract_method_coverage, parse_methods_coverage
#from extract_class_coverage import parse_coverage, extract_class_coverage

MAX_TOKEN = 3000

def score_classes(data):
    """
    Score each class on how related it is to the bug using both percentage-based and naive (absolute) indicators.

    Indicators used:
      - Percentage-based:
          * hit_rate: total_line_hits / total_lines
          * lines_coverage: covered_lines / total_lines
          * methods_coverage: covered_methods / method_count
      - Absolute size indicators:
          * total_lines: absolute value for class size/complexity
          * method_count: absolute value for class size/complexity
      - Naive (absolute) coverage counts:
          * naive_covered_lines: raw covered_lines
          * naive_total_line_hits: raw total_line_hits
          * naive_covered_methods: raw covered_methods

    Classes with covered_lines == 0 are excluded.

    The raw metrics are normalized (min-max) across the remaining classes and then combined
    with weights to compute a final score for each class.

    Returns:
      A dictionary mapping class names to their normalized score.
    """
    # Exclude classes with zero covered_lines
    filtered_data = {cls: info for cls, info in data.items() if info["covered_lines"] > 0}

    # Compute raw metrics for each class
    metrics = {}
    for cls, info in filtered_data.items():
        total_lines = info["total_lines"]
        method_count = info["method_count"]

        # Percentage-based indicators: protect against division by zero
        hit_rate = info["total_line_hits"] / total_lines if total_lines > 0 else 0
        lines_coverage = info["covered_lines"] / total_lines if total_lines > 0 else 0
        methods_coverage = info["covered_methods"] / method_count if method_count > 0 else 0

        # Naive (absolute) indicators: raw values
        naive_covered_lines = info["covered_lines"]
        naive_total_line_hits = info["total_line_hits"]
        naive_covered_methods = info["covered_methods"]

        metrics[cls] = {
            "hit_rate": hit_rate,
            "lines_coverage": lines_coverage,
            "methods_coverage": methods_coverage,
            "total_lines": total_lines,
            "method_count": method_count,
            "naive_covered_lines": naive_covered_lines,
            "naive_total_line_hits": naive_total_line_hits,
            "naive_covered_methods": naive_covered_methods
        }

    # List of all metric keys to consider
    metric_keys = [
        "hit_rate",
        "lines_coverage",
        "methods_coverage",
        "total_lines",
        "method_count",
        "naive_covered_lines",
        "naive_total_line_hits",
        "naive_covered_methods"
    ]

    # Determine the min and max for each metric (for normalization)
    metric_min = {key: float('inf') for key in metric_keys}
    metric_max = {key: float('-inf') for key in metric_keys}

    for m in metrics.values():
        for key in metric_keys:
            val = m[key]
            if val < metric_min[key]:
                metric_min[key] = val
            if val > metric_max[key]:
                metric_max[key] = val

    # Normalization helper: scale value to the range [0, 1]
    def normalize(val, mn, mx):
        # If all values are the same, return 1.0 (or 0.0); here we treat it as maximum importance.
        if mx == mn:
            return 1.0
        return (val - mn) / (mx - mn)

    # Define weights for each normalized metric
    weights = {
        "hit_rate": 1.0,
        "lines_coverage": 1.0,
        "methods_coverage": 1.0,
        "total_lines": 0,
        "method_count": 0,
        "naive_covered_lines": 0.5,
        "naive_total_line_hits": 0.5,
        "naive_covered_methods": 0.5
    }
    total_weight = sum(weights.values())

    # Compute final weighted score for each class
    scores = {}
    for cls, m in metrics.items():
        weighted_sum = 0.0
        for key in metric_keys:
            norm_val = normalize(m[key], metric_min[key], metric_max[key])
            weighted_sum += weights[key] * norm_val
        # Normalize the combined weighted score so it falls between 0 and 1.
        score = weighted_sum / total_weight
        scores[cls] = score

    return scores




def select_classes(scores, n, bias=1.0):
    """
    Select n classes from scores dict.
    Bias controls randomness vs score preference:
        bias = 1.0 -> Top-n
        bias = 0.0 -> Pure Random
        0 < bias < 1 -> Weighted Random Favoring Higher Scores (no duplicates)
    """
    if n > len(scores):
        n = len(scores)
    if bias >= 1.0:
        # Pure Top-n
        return [cls for cls, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]]

    if bias <= 0.0:
        # Pure Random
        return random.sample(list(scores.keys()), n)

    # Normalize scores to [0, 1]
    max_score = max(scores.values())
    min_score = min(scores.values())
    norm_scores = {
        cls: (s - min_score) / (max_score - min_score) if max_score > min_score else 1.0
        for cls, s in scores.items()
    }

    # Adjust weights using bias
    adjusted_weights = {
        cls: norm_score ** (1 / bias)
        for cls, norm_score in norm_scores.items()
    }

    # Weighted random sampling *without* duplicates
    population = list(adjusted_weights.keys())

    weights = list(adjusted_weights.values())
    if not any(w > 0 for w in weights):
        print("All weights are zero. Here are the scores and normalized weights:")
        for cls in scores:
            print(f"{cls}: score={scores[cls]}, norm={(scores[cls] - min_score)/(max_score - min_score) if max_score > min_score else 1.0}")
        print("Falling back to pure random.")
        return random.sample(list(scores.keys()), min(n, len(scores)))
    selected = []

    total_weight = sum(weights)
    if total_weight == 0:
        # fallback to pure random if weights are degenerate
        return random.sample(list(scores.keys()), n)
    try:
        for _ in range(n):
            if not population:
                break
            chosen = random.choices(population=population, weights=weights, k=1)[0]
            selected.append(chosen)
            idx = population.index(chosen)
            del population[idx]
            del weights[idx]
    except ValueError as e:
        if "Total of weights must be greater than zero" in str(e):
            print("Caught ValueError: Total of weights must be greater than zero. Falling back to random sampling.")
            return random.sample(list(scores.keys()), n)
        else:
            raise e  # re-raise any other ValueError

    return selected



def merge_inner_classes(data):
    """
    Merges inner class info into its parent class record.
    
    The function checks for keys with a '$' and splits them into a parent name and an inner part.
    If the parent exists in the dictionary, each numeric field from the inner class is added
    to the corresponding parent's field.
    
    Example:
      Input:
          {
              'a': {'total_lines': 10, 'method_count': 5},
              'a$b': {'total_lines': 2,  'method_count': 1},
              'a$c': {'total_lines': 3,  'method_count': 1}
          }
      Output:
          {
              'a': {'total_lines': 15, 'method_count': 7}
          }
          
    If the parent doesn't exist, the inner class entry is discarded.
    """
    # We'll make a shallow copy of the data to safely modify it
    merged_data = dict(data)
    
    # Collect keys that represent inner classes (contain a '$')
    inner_keys = [key for key in merged_data if '$' in key]
    
    for inner in inner_keys:
        # Extract the parent name (substring before the first '$')
        parent = inner.split('$', 1)[0]
        # Only merge if the parent's data exists
        if parent in merged_data:
            for metric, value in merged_data[inner].items():
                # If the parent's metric exists, add the inner's value;
                # otherwise, initialize it with the inner's value.
                merged_data[parent][metric] = merged_data[parent].get(metric, 0) + value
        # Remove the inner class from the merged data regardless of merging.
        del merged_data[inner]
    
    return merged_data

def print_data_simple(data):
    for cls,_ in data.items():
        print(cls, _["start_line"])

def print_data(data):
    for cls,info in data.items():
        print(f"Method: {cls}")
        for key,value in info.items():
            print(f"    {key}: {value}")
        print()

import random

def exclude_method(coverage_data, parsed_log, exclude):
    target_method_name = (parsed_log["location"].split("@")[-1]).split("(")[0]

    # Step 1: Build list of candidate methods to exclude
    candidates = [
        key for key, val in coverage_data.items()
        if not (
            target_method_name in key and
            val["start_line"] - 10 < parsed_log["lineno"] and
            val["end_line"] + 10 > parsed_log["lineno"]
        )
    ]

    # Step 2: Randomly select 'exclude' keys to remove
    keys_to_remove = random.sample(candidates, min(exclude, len(candidates)))
    # Step 3: Delete them from the original dict
    for key in keys_to_remove:
        del coverage_data[key]
    

    return coverage_data

def exclude_non_existing(coverage_data, source_data):
    def collect_all_signatures(src):
        method_entries = []

        # Constructors
        for cons in src.get("constructors", []):
            method_entries.append({
                "name": "<init>",
                "start": cons["startLine"],
                "end": cons["endLine"]
            })

        # Methods
        for method in src.get("methods", []):
            method_entries.append({
                "name": method["name"],
                "start": method["startLine"],
                "end": method["endLine"]
            })

        # Inner types (recursively)
        for inner in src.get("innerTypes", []):
            method_entries.extend(collect_all_signatures(inner))

        return method_entries

    # Step 1: Flatten all methods/constructors from source_data
    valid_methods = collect_all_signatures(source_data)

    # Step 2: Build new filtered dict
    filtered = {}
    for key, cov_info in coverage_data.items():
        # Remove #suffix from method name
        method_name = key.split("#")[0]

        cov_end = cov_info["end_line"]

        # Try to find a matching method or constructor
        exists = any(
            m["name"] == method_name and abs(m["end"] - cov_end) <= 10
            for m in valid_methods
        )

        if exists:
            filtered[key] = cov_info

    return filtered

def format_method_review(method_review):
    # Sort by line number (index 1 of each element)
    sorted_methods = sorted(method_review, key=lambda x: x[1])

    # Build the string output with each line numbered
    lines = []
    lines.append("##EXISTING_METHODS (format: MethodName@LineNumber)\n")
    lines.append("'''")
    for i, (name, line_number) in enumerate(sorted_methods, start=1):
        lines.append(f"{name}@{line_number}")
    lines.append("'''")
    return "\n".join(lines)



def apply_mutation(coverage_data, source_data, lineno, original_code, mutated_code, target_method):
    """
    Returns the Java source as a string for the class (and its inner types) including
    only those constructors and methods covered in `coverage_data`, with one mutation
    applied in `target_method` at line `lineno`.

    :param coverage_data: dict of "<name>#<id>" -> {covered_lines, start_line, end_line, …}
    :param source_data:   dict representing a class, with keys:
                          - 'name', 'comment', 'startLine', 'endLine'
                          - 'constructors': [ {signature, snippet, comment, startLine, endLine}, … ]
                          - 'methods':      [ {name, snippet, comment, startLine, endLine}, … ]
                          - 'innerTypes':   [ same structure as source_data, … ]
    :param lineno:        int, the line number in the original file to mutate
    :param original_code: str, the exact substring to replace
    :param mutated_code:  str, the replacement substring
    :param target_method: str, the name of the method to mutate
    :return:              str, the assembled Java source
    """
    import html

    # Map method/ctor name to list of covered end lines
    covered = {}
    for key, info in coverage_data.items():
        if info.get('covered_lines', 0) > 0:
            name = key.split('#')[0]
            end_line = info.get('end_line', info.get('endLine'))
            covered.setdefault(name, []).append(end_line)

    def decode_unicode(s):
        # Convert unicode escapes (e.g. "\u003d") to real characters
        return bytes(s, 'utf-8').decode('unicode_escape') if s else ''

    def class_has_covered(cls):
        # Check constructors
        for e in covered.get('<init>', []):
            for ctor in cls.get('constructors', []):
                if abs(ctor['endLine'] - e) <= 10:
                    return True
        # Check methods
        for name, ends in covered.items():
            if name == '<init>':
                continue
            for m in cls.get('methods', []):
                if m['name'] == name and any(abs(m['endLine'] - e) <= 10 for e in ends):
                    return True
        # Recurse into inner types
        for inner in cls.get('innerTypes', []):
            if class_has_covered(inner):
                return True
        return False

    def process_class(cls, indent_level=0):
        indent = '    ' * indent_level
        lines = []
        method_review = []
        # Class comment
        comment = decode_unicode(cls.get('comment', '')).strip()
        if comment:
            for c_line in comment.splitlines():
                lines.append(f"{indent}{c_line.rstrip()}")
        # Class signature
        lines.append(f"{indent}public class {cls['name']} {{")

        # Constructors
        for ctor in cls.get('constructors', []):
            for e in covered.get('<init>', []):
                if abs(ctor['endLine'] - e) <= 10:
                    snippet = decode_unicode(ctor['snippet']).splitlines()
                    
                    name = ctor["signature"].split("(")[0]
                    startline = ctor["startLine"]

                    lines.append( f"{indent}    ###Method : {name},    line number : {startline}")
                    
                    method_review.append([name,startline])

                    # Constructor comment
                    cmt = ctor.get('comment', '').strip()
                    if cmt:
                        lines.append(f"{indent}    {cmt}")
                    # Body
                    for ln in snippet:
                        lines.append(f"{indent}    {ln}")
                    lines.append('')
                    break

        # Methods
        for m in cls.get('methods', []):
            name = m['name']
            startline = m['startLine']

            if name not in covered:
                continue
            if not any(abs(m['endLine'] - e) <= 10 for e in covered[name]):
                continue
            lines.append('')
            lines.append(f"{indent}    ###Method : {name},      line number : {startline}")

            method_review.append([name,startline])
            
            snippet = decode_unicode(m['snippet']).splitlines()
            # Method comment
            cmt = m.get('comment', '').strip()
            if cmt:
                for c_line in cmt.splitlines():
                    lines.append(f"{indent}    {c_line.rstrip()}")
            # Apply mutation and add lines
            for i, code_line in enumerate(snippet):
                abs_ln = m['startLine'] + i
                if (name == target_method and abs_ln == lineno
                        and original_code in code_line):
                    code_line = code_line.replace(original_code, mutated_code)
                lines.append(f"{indent}    {code_line}")
            lines.append('')

        # Inner types
        for inner in cls.get('innerTypes', []):
            if class_has_covered(inner):
                inner_lines, inner_method = process_class(inner, indent_level + 1)
                lines.extend(inner_lines)
                method_review.extend(inner_method)

        # Closing brace
        lines.append(f"{indent}}}")
        lines.append('')
        return lines, method_review

    # Only proceed if the top-level class has covered members
    if not class_has_covered(source_data):
        return ''

    result, method_review = process_class(source_data, indent_level=0)
    formatted_method_review = format_method_review(method_review)
    """
    for i, item in enumerate(result):
        if not isinstance(item, str):
            print(f"Item {i} is not a string: {item} \n(type={type(item)})\n\n\n")
        else:
            print("good!")
    """
    #print(type(formatted_method_review))
    #print(type(result))
    return '\n'.join(result) + "\n" + formatted_method_review
    #return '\n'.join(result)

def return_answer(coverage_data, source_data, lineno, target_method, choices_count):
    """
    Returns `choices_count` lines in the form:
      Method 1 : <methodName@startLine>
    The first entry is always the mutated `target_method`, followed by random covered entries.
    Constructors use the class name.
    """
    # Helper: find method/ctor entry by name and line margin
    def find_entry(cls, name, start, end):
        # constructors
        if name == '<init>':
            for ctor in cls.get('constructors', []):
                if abs(ctor['startLine'] - start) <= 10 and abs(ctor['endLine'] - end) <= 10:
                    return ctor['startLine'],ctor["signature"]
        else:
            for m in cls.get('methods', []):
                if m['name'] == name and abs(m['startLine']-start)<=10 and abs(m['endLine']-end)<=10:
                    return m['startLine'],None
        for inner in cls.get('innerTypes', []):
            rv = find_entry(inner, name, start, end)
            if rv is not None:
                return rv
        return None

    # Build all covered candidates
    candidates = []  # list of (display_name, startLine)
    for key, info in coverage_data.items():
        if info.get('covered_lines', 0) <= 0:
            continue
        name = key.split('#')[0]
        #print(name)
        start = info.get('start_line', info.get('startLine'))
        end = info.get('end_line', info.get('endLine'))
        rv = find_entry(source_data, name, start, end)
        if rv is None:
            continue
        sl,signature = rv
        display = signature.split("(")[0] if name == '<init>' else name
        #print(display,sl)
        candidates.append((display, sl))

    # Deduplicate while preserving order
    seen = set(); unique = []
    for item in candidates:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    # Ensure target first
    first = None
    rest = []
    for name, sl in unique:
        if name == target_method and first is None:
            first = (name, sl)
        else:
            rest.append((name, sl))
    if first is None:
        # fallback: pick any matching target
        first = rest.pop(0) if rest else ('', 0)

    # Randomly choose remaining
    random.shuffle(rest)
    chosen = [first] + rest[:max(0, choices_count-1)]

    # Format output
    lines = []
    for i, (name, sl) in enumerate(chosen, start=1):
        lines.append(f"{i}.{name}@{sl}")
    return '\n'.join(lines)





def generate_prompt_2_1(p,target_class,test_class,test_method,parsed_log,source_data,exclude,choices_count,coverage_data2, file_path2):

    coverage_path = f"/home/yinseok/lorafl/mutation_data/{p}/coverage"

    target_class = target_class.split("@")[0]

    coverage_file_path = f"{coverage_path}/coverage__{target_class}__{test_class}::{test_method}.xml"

    if os.path.exists(coverage_file_path):
        if file_path2 == coverage_file_path:
            coverage_data = coverage_data2
            file_path = file_path2
        else:
            coverage_data = parse_methods_coverage(coverage_file_path,target_class)
            file_path = coverage_file_path
    else:
        fp = f"CLASS:{target_class}"
        if file_path2 == fp:
            coverage_data = coverage_data2
            file_path = file_path2
        else:
            coverage_data = extract_method_coverage(p,target_class)
            file_path = f"CLASS:{target_class}"
    

    coverage_data = dict(sorted(coverage_data.items(), key=lambda item: (item[1]['start_line'] if item[1]['start_line'] is not None else float('inf'))))
    coverage_data = {
        k: v for k, v in coverage_data.items()
        if v["covered_lines"] != 0 and v["total_lines"] != 0
    }


    target_method_name = (parsed_log["location"].split("@")[-1]).split("(")[0]
    
    found = False
    
    for key,val in coverage_data.items():
        if target_method_name in key and val["start_line"]-10< parsed_log["lineno"] and val["end_line"]+10>parsed_log["lineno"]:
            found = True
            break

    if not found:
        print("Mutation not found in coverage file")
        return -1, -1, coverage_data, file_path
    
    excluded_coverage_data = exclude_non_existing(coverage_data, source_data)


    
    excluded_coverage_data = exclude_method(excluded_coverage_data, parsed_log, exclude)
    
    if len(excluded_coverage_data)<=1 :
        return -1, -1, coverage_data, file_path


    mutated_code = apply_mutation(excluded_coverage_data, source_data, parsed_log["lineno"], parsed_log["original_code"], parsed_log["mutated_code"],target_method_name)
    #print(mutated_code)
    #print()
    answer = return_answer(coverage_data, source_data, parsed_log['lineno'], target_method_name, choices_count)
    #print(answer)
    #print(parsed_log)

    #print(source_data["comment"])


    


    return mutated_code, answer, coverage_data, file_path







def generate_prompt_2_2(p,target_class,test_class,test_method,count):
    n = count
    coverage_path = f"/home/yinseok/lorafl/mutation_data/{p}/coverage"

    target_class = target_class.split("@")[0]

    coverage_file_path = f"{coverage_path}/coverage__{target_class}__{test_class}::{test_method}.xml"

    if os.path.exists(coverage_file_path):
        data = parse_coverage(coverage_file_path)
    else:
        data = extract_class_coverage(p,target_class)
    data = merge_inner_classes(data)    
    #print_data(data)
    scores = score_classes(data)
    
    if len(scores)==0:
        return -1, -1
    if scores==None:
        return -1,-1
    

    #for s in scores:
    #    print(s)


    selected_classes = select_classes(scores, n, bias = 0.90)
    
    #for s in selected_classes:
    #    print(s)

    print()
    if target_class in selected_classes:
        # Move it to front
        selected_classes.remove(target_class)
        selected_classes.insert(0, target_class)
    else:
        # Insert at front (push others)
        selected_classes.insert(0, target_class)

    # Keep only size n
    selected_classes = selected_classes[:n]
        
    return "\n".join(f"<{i+1}.{selected_classes[i].split('.')[-1]}>" for i in range(len(selected_classes)))




































