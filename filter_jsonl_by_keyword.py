import json
import random

def filter_jsonl_by_keyword(input_path, output_path, keyword):
    """
    Reads a .jsonl file, and writes a new .jsonl file with 50% of lines
    containing 'keyword' randomly removed.

    Args:
        input_path (str): Path to the input .jsonl file.
        output_path (str): Path to save the filtered .jsonl file.
        keyword (str): Keyword to search for in each JSON line.
    """
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            try:
                obj = json.loads(line)
                obj_str = json.dumps(obj)

                if keyword in obj_str and random.random() < 0.1:
                    continue  # Skip this line
                outfile.write(json.dumps(obj) + '\n')
            except json.JSONDecodeError:
                continue  # Skip invalid JSON lines
filter_jsonl_by_keyword('closure_data.jsonl', 'closure_data1.jsonl', 'Compiler')

