import os
import csv
import re
import random


from extract_class_coverage import parse_coverage, extract_class_coverage

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



def print_data(data):
    for cls,info in data.items():
        print(f"Class: {cls}")
        for key,value in info.items():
            print(f"    {key}: {value}")
        print()

def generate_prompt_1(p,target_class,test_class,test_method, coverage_data2, file_path2):
    n = 45

    coverage_path = f"/home/yinseok/lorafl/mutation_data/{p}/coverage"

    target_class = target_class.split("@")[0]
    target_class = target_class.split("$")[0]
    coverage_file_path = f"{coverage_path}/coverage__{target_class}__{test_class}::{test_method}.xml"

    if os.path.exists(coverage_file_path):
        if file_path2 == coverage_file_path:
            coverage_data = coverage_data2
            file_path = file_path2
        #print("here1")
        else:
            coverage_data = parse_coverage(coverage_file_path)
            file_path = coverage_file_path
    else:
        fp = f"CLASS:{target_class}"
        if file_path2 == fp:
            coverage_data = coverage_data2
            file_path = file_path2
        else:
        #print("here2")
            coverage_data = extract_class_coverage(p,target_class)
            file_path = f"CLASS:{target_class}"

    #print_data(data)
    data = merge_inner_classes(coverage_data)    
    #print_data(data)
    scores = score_classes(data)
    #print(scores)
    if len(scores)==0:
        return -1, coverage_data, file_path
    if scores==None:
        return -1, coverage_data, file_path

    #print("score",scores)
    #for s in scores:
    #    print(s)


    selected_classes = select_classes(scores, n, bias = 0.7)
    
    #for s in selected_classes:
    #    print(s)

    print()
    if target_class not in selected_classes:
        print("not selected, inserted")
        # Insert target_class to random idx within top 10
        low_value = min(len(selected_classes),4)
        
        idx = random.randint(low_value, min(15, len(selected_classes)-1))
        
        selected_classes[idx] = target_class
        
        # Delete the last element to keep size n
        selected_classes = selected_classes[:n]
    
    for i in range(len(selected_classes)):
        selected_classes[i] = selected_classes[i] +".java"
        #print(selected_classes[i])

    class_file_path = f"/home/yinseok/lorafl/data/{p}/classes.csv"

    file_names = []
    summaries = []
    
    with open(class_file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            file_names.append(row[0].strip())
            summaries.append(row[1].strip())
    
    


    if p=="Closure":
        for i in range(len(file_names)):
            file_names[i] = "com.google." + file_names[i]


    covered_classes_for_prompt = ""####


    i = 1
    for covered_class in selected_classes:
        if covered_class in file_names:
            index = file_names.index(covered_class)
            class_name = covered_class.split(".")[-2]

            summary = summaries[index]

            #covered_classes_for_prompt += f"  Class {i} : <{class_name}>\n"
            covered_classes_for_prompt += f"  Class {i} : <{class_name}> : {summary}\n"
            i+=1
    #print("cc")        
    #print(covered_classes_for_prompt)
    return covered_classes_for_prompt, coverage_data, file_path
    #for s in selected_classes:
    #    print(s)







def generate_prompt_2(p,target_class,test_class,test_method,count, coverage_data2, file_path2):
    #if count==1:
    #    return f"1.<{target_class}>"

    n = count
    coverage_path = f"/home/yinseok/lorafl/mutation_data/{p}/coverage"

    target_class = target_class.split("@")[0]
    target_class = target_class.split("$")[0]

    coverage_file_path = f"{coverage_path}/coverage__{target_class}__{test_class}::{test_method}.xml"

    if os.path.exists(coverage_file_path):
        if file_path2 == coverage_file_path:
            coverage_data = coverage_data2
            file_path = file_path2
        else:
            coverage_data = parse_coverage(coverage_file_path)
            file_path = coverage_file_path
    else:
        fp = f"CLASS:{target_class}"
        if file_path2 == fp:
            coverage_data = coverage_data2
            file_path = file_path2
        else:
            coverage_data = extract_class_coverage(p,target_class)
            file_path = f"CLASS{target_class}"
    data = merge_inner_classes(coverage_data)    
    #print_data(data)
    scores = score_classes(data)
    
    if len(scores)==0:
        return -1, coverage_data, file_path
    if scores==None:
        return -1,coverage_data, file_path
    

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
        
    return "\n".join(f"{i+1}.<{selected_classes[i].split('.')[-1]}>" for i in range(len(selected_classes))), coverage_data, file_path




































