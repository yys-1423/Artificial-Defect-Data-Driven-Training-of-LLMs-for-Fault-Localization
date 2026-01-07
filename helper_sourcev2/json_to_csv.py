import os
import json
import csv

import os
import csv

import csv

def classify_dynamic_thresholds(
    csv_file_in,
    csv_file_out,
    modified_weight=20,
    loaded_weight=1
):
    """
    Reads a CSV with columns: name, packageName, modified_count, loaded_count
    and assigns each row to a category (0, 1, 2, 3). The thresholds for
    categories 1, 2, and 3 are determined dynamically based on the
    distribution of scores in the CSV.

    :param csv_file_in: Path to the input CSV file.
    :param csv_file_out: Path to the output CSV file. If None, overwrites the input.
    :param modified_weight: Weight to multiply modified_count by in the score.
    :param loaded_weight: Weight to multiply loaded_count by in the score.
    """

    if csv_file_out is None:
        csv_file_out = csv_file_in  # Overwrite input if no separate output is provided

    # 1. Read rows from CSV
    rows = []
    with open(csv_file_in, 'r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames

        # Ensure required columns exist
        if 'modified_count' not in fieldnames or 'loaded_count' not in fieldnames:
            raise ValueError("CSV must have 'modified_count' and 'loaded_count' columns.")

        for row in reader:
            # Convert counts to integers
            row['modified_count'] = int(row['modified_count'])
            row['loaded_count'] = int(row['loaded_count'])
            rows.append(row)

    # 2. Compute scores and separate zero vs. non-zero
    scores = []
    for row in rows:
        mod = row['modified_count']
        load = row['loaded_count']
        # Weighted score
        score = modified_weight * mod + loaded_weight * load
        row['score'] = score
        # We'll assign 'category' later
        row['category'] = None
        # We'll keep track of non-zero scores for thresholding
        if mod != 0 or load != 0:
            scores.append(score)
    #print(scores)
    # 3. Sort the non-zero scores and find dynamic thresholds
    scores.sort()
    if len(scores) == 0:
        # Edge case: everything is zero => all categories are 0
        threshold_1 = threshold_2 = 0
    else:
        # We'll use the 1/3 and 2/3 quantiles
        # Example: if there are 30 non-zero items, the 1/3 quantile is item #10 (0-based index 9)
        #          the 2/3 quantile is item #20 (0-based index 19)
        one_third_idx = int(len(scores) / 3)
        two_thirds_idx = int(2 * len(scores) / 3)

        # Make sure indices are within range
        one_third_idx = min(max(one_third_idx, 0), len(scores) - 1)
        two_thirds_idx = min(max(two_thirds_idx, 0), len(scores) - 1)

        threshold_1 = scores[one_third_idx]
        threshold_2 = scores[two_thirds_idx]
    
    # 4. Assign categories
    #    - Category 0: modified_count == 0 AND loaded_count == 0
    #    - Category 1, 2, 3: based on score vs. threshold_1, threshold_2
    for row in rows:
        mod = row['modified_count']
        load = row['loaded_count']
        if mod == 0 and load == 0:
            # Category 0
            row['category'] = 0
        else:
            s = row['score']
            # If the thresholds end up the same, we handle that gracefully:
            if threshold_1 == threshold_2:
                # Everything non-zero goes to category 3, or you can break them differently
                row['category'] = 3
            else:
                if s < threshold_1:
                    row['category'] = 1
                elif s < threshold_2:
                    row['category'] = 2
                else:
                    row['category'] = 3

    #for r in rows:
    #    print(r)
    # 5. Write updated rows back to CSV (adding 'category' column)
    output_fieldnames = list(fieldnames)
    if 'score' not in output_fieldnames:
        output_fieldnames.append('score')
    if 'category' not in output_fieldnames:
        output_fieldnames.append('category')

    with open(csv_file_out, 'w', newline='', encoding='utf-8') as fout:
        writer = csv.DictWriter(fout, fieldnames=output_fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Classification complete. Updated CSV written to: {csv_file_out}")

def update_class_counts(csv_file, modified_class_path, loaded_class_path, start, end):
    # Read the CSV file and build a mapping from full class name to its row.
    rows = []
    class_map = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create the fully qualified class name (packageName.name)
            filename = row.get('filename', '').strip()
            package = row.get('packageName', '').strip()
            name = row.get('name', '').strip()
            full_class_name = f"{package}.{name}"
            # Initialize count fields
            row['modified_count'] = 0
            row['loaded_count'] = 0
            rows.append(row)
            class_map[full_class_name] = row

    # Process modified class files
    for i in range(start, end + 1):
        file_path = modified_class_path + f"/{i}.src"
        if not os.path.exists(file_path):
            print(f"Modified file '{file_path}' not found. Skipping.")
            continue
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                class_line = line.strip()
                if class_line in class_map:
                    class_map[class_line]['modified_count'] += 1

    # Process loaded class files
    for i in range(start, end + 1):
        file_path = loaded_class_path + f"/{i}.src"
        if not os.path.exists(file_path):
            print(f"Loaded file '{file_path}' not found. Skipping.")
            continue
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                class_line = line.strip()
                if class_line in class_map:
                    class_map[class_line]['loaded_count'] += 1

    # Write the updated data back to the CSV file.
    fieldnames = ['filename','name', 'packageName', 'modified_count', 'loaded_count']
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"CSV file '{csv_file}' updated with class counts.")


def json_to_csv(directory, output_file='output.csv'):
    rows = []

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    name = data.get('name', '')
                    package_name = data.get('packageName', '')
                    rows.append([filename,name, package_name])
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename','name', 'packageName'])  # header
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {output_file}")

path = "/home/yinseok/ttr/lora/data_preprocess/data_original/"

projects = ["Chart","Closure","Math", "Lang", "Math3"]

#for p in projects:
#    json_to_csv(path+f"{p}/output_source2", output_file = path+f"{p}/class.csv")

#if __name__ == "__main__":
#    p = "Math"
#    csv_file = path + f"{p}/class.csv"
#    modified_class_path = f"/home/yinseok/Desktop/project/defects4j/framework/projects/{p}/modified_classes"
#    loaded_class_path = f"/home/yinseok/Desktop/project/defects4j/framework/projects/{p}/loaded_classes"
#    start = 36
#    end = 106
#    update_class_counts(csv_file, modified_class_path, loaded_class_path, start, end)

for p in projects:
    csv_file = path + f"{p}/class.csv"
    csv_file_out = path + f"{p}/classes.csv"
    classify_dynamic_thresholds(csv_file_in = csv_file, csv_file_out = csv_file_out)

































