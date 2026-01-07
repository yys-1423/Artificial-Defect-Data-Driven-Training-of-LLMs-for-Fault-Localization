import json
import re

def transform_lines(text):
    """
    Convert lines like <1.ClassName> to 1.<ClassName>
    """
    lines = text.strip().splitlines()
    new_lines = []
    for line in lines:
        match = re.match(r'<(\d+)\.(.+)>', line.strip())
        if match:
            idx, name = match.groups()
            new_lines.append(f"{idx}.<{name}>")
        else:
            new_lines.append(line.strip())
    return "\n".join(new_lines)

def clean_jsonl(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            try:
                data = json.loads(line)
                if isinstance(data.get("input"),str):
                    if "(-1, -1)" in data["input"]:
                        continue

                # Remove if output is [-1, -1]
                if isinstance(data.get("output"), list) and data["output"] == [-1, -1]:
                    continue

                # Fix format in input if it's a string
                if isinstance(data.get("input"), str):
                    data["input"] = transform_lines(data["input"])

                # Fix format in output if it's a string
                if isinstance(data.get("output"), str):
                    data["output"] = transform_lines(data["output"])

                json.dump(data, outfile, ensure_ascii=False)
                outfile.write('\n')

            except Exception as e:
                print(f"Skipping line due to error: {e}")

if __name__ == "__main__":
    clean_jsonl("train_data6.jsonl", "train_data6_cleaned.jsonl")

