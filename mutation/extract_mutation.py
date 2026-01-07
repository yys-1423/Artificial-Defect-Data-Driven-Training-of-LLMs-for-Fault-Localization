import os
import re
import csv

from parse_failing_test import parse_failing_tests

def open_and_parse_failing_tests(project,directory):
    pattern = re.compile(r"failing_tests__(.+?)__(\d+)$")
    data = []
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            target_class, number = match.groups()
            number = int(number)
            file_path = os.path.join(directory, filename)
            try:
                print(f"Opened: {filename}, Parsed class: {target_class}, #: {number}")
                bug_reports = parse_failing_tests(file_path)
                
                for i,bug_report in enumerate(bug_reports):
                    test = bug_report[0][0].split(".")[-1]
                    data.append([target_class, number, file_path, i,test])

            except Exception as e:
                print(f"{e}")
    data.sort(key=lambda x: (x[0], x[1], x[3]))  # target_class, number, bug_index 기준 정렬
    


    with open(f"{project}/data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["target_class", "number", "filename", "bug_index", "test"])
        writer.writerows(data)


import csv
from collections import defaultdict

def analyze_data_csv(project):
    csv_file = f"{project}/data.csv"
    data = []
    
    # Load CSV data
    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            target_class, number, _, _, _ = row
            data.append((target_class, int(number)))
    
    # Group by target_class
    class_to_numbers = defaultdict(set)
    class_number_to_count = defaultdict(int)

    for target_class, number in data:
        class_to_numbers[target_class].add(number)
        class_number_to_count[(target_class, number)] += 1

    # How many unique target_class (x[0]) exist
    num_unique_classes = len(class_to_numbers)

    # Average number of unique x[1] (number) for each x[0] (target_class)
    avg_unique_numbers_per_class = sum(len(numbers) for numbers in class_to_numbers.values()) / num_unique_classes

    # Average number of elements for each (target_class, number) pair
    avg_elements_per_class_number = sum(class_number_to_count.values()) / len(class_number_to_count)

    # Print results
    print(f"Number of unique target_class (x[0]): {num_unique_classes}")
    print(f"Average number of unique number (x[1]) per target_class: {avg_unique_numbers_per_class:.2f}")
    print(f"Average number of test cases per (target_class, number) pair: {avg_elements_per_class_number:.2f}")

def print_filtered_unique_numbers_per_class(project):
    import csv
    from collections import defaultdict

    csv_file = f"{project}/data.csv"
    class_number_counts = defaultdict(int)
    class_to_filtered_numbers = defaultdict(set)

    # First pass: count occurrences of each (target_class, number) pair
    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            target_class, number, *_ = row
            number = int(number)
            class_number_counts[(target_class, number)] += 1

    # Second pass: collect only (target_class, number) pairs with < 100 entries
    for (target_class, number), count in class_number_counts.items():
        if count < 100:
            class_to_filtered_numbers[target_class].add(number)

    # Print result
    for target_class in sorted(class_to_filtered_numbers.keys()):
        print(f"{target_class} : {len(class_to_filtered_numbers[target_class])}")

def print_class_number_and_methods(project):
    import csv
    from collections import defaultdict

    csv_file = f"{project}/data.csv"
    # Count how many entries each (class, number) pair has
    pair_count = defaultdict(int)
    data_rows = []

    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            target_class, number, _, _, test = row
            number = int(number)
            pair_count[(target_class, number)] += 1
            data_rows.append((target_class, number, test))

    # Group methods by (class, number) where count < 100 and not NameAnalyzer
    classnum_to_methods = defaultdict(set)
    for target_class, number, test in data_rows:
        if target_class == "com.google.javascript.jscomp.NameAnalyzer":
            continue
        if pair_count[(target_class, number)] >= 30:
            continue
        class_name = target_class.split(".")[-1]
        key = f"{class_name}_{number}"
        classnum_to_methods[key].add(test)

    # Print
    for key in sorted(classnum_to_methods.keys()):
        print(key)
        for method in sorted(classnum_to_methods[key]):
            print(f"\t{method}")

import csv
import random
from collections import defaultdict
def save_back(project):

    
    csv_file = f"{project}/data.csv"
    output_file = f"{project}/data_back.csv"
    
    class_number_counts = defaultdict(int)
    unique_class_number_counts = defaultdict(int)
    data = []

    # First pass: Count (target_class, number)
    last_class = ""
    last_num = 0
    test_set = set()
    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

        for row in rows:
            target_class, number, _,_,test = row
            number = int(number)
            class_number_counts[(target_class, number)] += 1
            if target_class == last_class and number == last_num:
                if test not in test_set:
                    unique_class_number_counts[(target_class, number)] += 1
                    test_set.add(test)
            else:
                test_set = set()
            last_class = target_class
            last_num = number

    # Second pass: Save only rows with < 100 occurrences
    for row in rows:
        target_class, number, *_ = row
        number = int(number)
        unique_class_count = unique_class_number_counts[(target_class, number)]
        row.append(unique_class_count)
        if class_number_counts[(target_class, number)] < 100 and unique_class_count<30:
            if unique_class_count>15:
                if random.random()<0.1:
                    data.append(row)
            elif unique_class_count>10:
                if random.random()<0.2:
                    data.append(row)
            elif unique_class_count>5:
                if random.random() < 0.5:
                    data.append(row)
            else:
                data.append(row)

    
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

#save_back()
import csv
from collections import defaultdict

def print_entry_and_unique_number(csv_file="data_back_filled.csv"):
    
    csv_file = f"{project}/data.csv"
    
    class_entry_count = defaultdict(int)
    class_unique_numbers = defaultdict(set)

    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            target_class, number, *_ = row
            number = int(number)
            class_entry_count[target_class] += 1
            class_unique_numbers[target_class].add(number)

    for target_class in sorted(class_entry_count.keys()):
        print(f"{target_class} : #entry={class_entry_count[target_class]} / #unique_number={len(class_unique_numbers[target_class])}")
import csv
import random
from collections import defaultdict

def fill_small_entries(project):
    

    csv_file = f"{project}/data_back.csv"
    output_file = f"{project}/data_back_filled.csv"
    
    class_to_rows = defaultdict(list)

    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            target_class = row[0]
            class_to_rows[target_class].append(row)

    new_data = []

    for target_class, rows in class_to_rows.items():
        if len(rows) < 5:
            print(f"Duplicating {target_class} : current #entry={len(rows)} → 5")
            while len(rows) < 5:
                rows.append(random.choice(rows))  # Duplicate random row
        new_data.extend(rows)

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(new_data)
#fill_small_entries()

import csv
from collections import defaultdict

def choose_bugs_and_write_csv(input_csv: str, output_csv: str, a: int, b: int):
    """
    Read the input CSV, add two columns (a, b), and select up to a rows for a=1
    and b rows for b=1 per target_class, attempting to distribute picks among
    different 'number' values if possible.

    :param input_csv: Path to the original CSV file (with columns
                     target_class, number, filename, bug_index, test)
    :param output_csv: Path to the new CSV file to write
    :param a: How many bugs to mark with a=1 for each target_class
    :param b: How many bugs to mark with b=1 for each target_class
    """

    # 1) Read CSV into list of dicts
    rows = []
    with open(input_csv, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # 2) Initialize columns 'a' and 'b' to "0" (string form for CSV)
    for row in rows:
        row['a'] = "0"
        row['b'] = "0"

    # 3) Group rows by 'target_class'
    grouped_by_class = defaultdict(list)
    for row in rows:
        grouped_by_class[row['target_class']].append(row)

    # 4) For each target_class, pick rows for a=1 and b=1
    for tc, group_rows in grouped_by_class.items():

        # Group by 'number' within this target_class
        by_number = defaultdict(list)
        for r in group_rows:
            by_number[r['number']].append(r)

        # Sort the distinct numbers just to have a deterministic order
        distinct_numbers = sorted(by_number.keys(), key=lambda x: (x))

        # --- Assign 'a' = 1 ---
        a_remaining = a

        # Round 1: pick at most one row from each distinct number
        for num in distinct_numbers:
            if a_remaining <= 0:
                break
            # If there is at least one row here, pick the first unchosen row
            rows_for_this_num = by_number[num]
            if rows_for_this_num:
                # Pick the first row that is still "a=0"
                for candidate in rows_for_this_num:
                    if candidate['a'] == "0":
                        candidate['a'] = "1"
                        a_remaining -= 1
                        break  # Only pick one row in this pass from this 'number'

        # Round 2: if we still need more 'a', pick from wherever possible
        if a_remaining > 0:
            for num in distinct_numbers:
                if a_remaining <= 0:
                    break
                rows_for_this_num = by_number[num]
                for candidate in rows_for_this_num:
                    if candidate['a'] == "0":
                        candidate['a'] = "1"
                        a_remaining -= 1
                        if a_remaining <= 0:
                            break

        # --- Assign 'b' = 1 ---
        b_remaining = b

        # Round 1: pick at most one row from each distinct number, where a=0 so we don't reuse
        for num in distinct_numbers:
            if b_remaining <= 0:
                break
            rows_for_this_num = by_number[num]
            if rows_for_this_num:
                for candidate in rows_for_this_num:
                    # Only assign b=1 to a row if it's currently a=0 and b=0
                    if candidate['a'] == "0" and candidate['b'] == "0":
                        candidate['b'] = "1"
                        b_remaining -= 1
                        break  # pick only one in this pass from this 'number'

        # Round 2: if we still need more 'b', pick from wherever possible
        if b_remaining > 0:
            for num in distinct_numbers:
                if b_remaining <= 0:
                    break
                rows_for_this_num = by_number[num]
                for candidate in rows_for_this_num:
                    if candidate['a'] == "0" and candidate['b'] == "0":
                        candidate['b'] = "1"
                        b_remaining -= 1
                        if b_remaining <= 0:
                            break

    # 5) Write out the new CSV with the added 'a' and 'b' columns
    fieldnames = ['target_class','number','filename','bug_index','test','a','b']
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
import csv
import random
from collections import defaultdict

def choose_bugs_randomly(project, a: int, b: int):
    

    input_csv = f"{project}/data_back_filled.csv"
    output_csv = f"{project}/data_output2.csv"
    """
    Reads the input CSV (with columns: target_class, number, filename, bug_index, test),
    adds two new columns ('a' and 'b'), and for each target_class randomly selects
    up to 'a' rows to mark a=1 and up to 'b' rows to mark b=1. The selection for a and b 
    is done independently, so a row can end up with both a=1 and b=1.

    :param input_csv: Path to the original CSV file.
    :param output_csv: Path to the new CSV file with added columns.
    :param a: Maximum number of rows to mark with a=1 for each target_class.
    :param b: Maximum number of rows to mark with b=1 for each target_class.
    """
    # Read rows from the CSV file
    rows = []
    with open(input_csv, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Initialize new columns 'a' and 'b' with "0"
    for row in rows:
        row['a'] = "0"
        row['b'] = "0"

    # Group rows by target_class
    groups = defaultdict(list)
    for row in rows:
        groups[row['target_class']].append(row)

    # For each target_class group, randomly mark rows
    for target_class, group_rows in groups.items():
        total_rows = len(group_rows)
        if total_rows == 0:
            continue

        # Randomly select indices for column a (up to 'a' rows)
        a_count = min(a, total_rows)
        a_indices = random.sample(range(total_rows), a_count)
        for idx in a_indices:
            group_rows[idx]['a'] = "1"

        # Randomly select indices for column b (up to 'b' rows)
        b_count = min(b, total_rows)
        b_indices = random.sample(range(total_rows), b_count)
        for idx in b_indices:
            group_rows[idx]['b'] = "1"
    
    # Write out the results to a new CSV file with all the columns plus 'a' and 'b'
    # Assumes that the first row contains all fields.
    fieldnames = list(rows[0].keys())
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

# Example usage:

# Example usage (uncomment and run if you like):
#choose_bugs_and_write_csv(
#    input_csv="data_back_filled.csv",
#    output_csv="data_output.csv",
#    a=10,
#    b=10
#)


#print_entry_and_unique_number()


###1.
project = ""
directory = f"/home/yinseok/lorafl/mutation_data/{project}/results"
open_and_parse_failing_tests(project,directory)

analyze_data_csv(project)

#print_filtered_unique_numbers_per_class(project)

#print_class_number_and_methods(project)

save_back(project)

fill_small_entries(project)

choose_bugs_randomly(project, a=20, b=20)
