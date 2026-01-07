import os
import json
from bs4 import BeautifulSoup

def is_java_package(directory):
    for file in os.listdir(directory):
        if file.endswith('.java') or file == 'package-info.java':
            return True
    return False
import re

def extract_package_info_content(file_path):
    """Extract clean Javadoc description from package-info.java."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    doc_lines = []
    inside_comment = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('/**'):
            inside_comment = True
            stripped = stripped[3:]
        elif stripped.endswith('*/') and inside_comment:
            stripped = stripped[:-2]
            doc_lines.append(stripped)
            break

        if inside_comment:
            if stripped.startswith('*'):
                stripped = stripped[1:]
            doc_lines.append(stripped.strip())

    cleaned = ' '.join(line for line in doc_lines if line).strip()

    # Remove <p> and other HTML tags, just to be safe
    cleaned = re.sub(r'<\/?p>', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def summarize_package_infos(root_dir, output_file='package_summary.json'):
    summary = []

    for dirpath, _, filenames in os.walk(root_dir):
        if 'package-info.java' in filenames:
            rel_path = os.path.relpath(dirpath, root_dir)
            package_name = rel_path.replace(os.sep, '.')

            package_info_path = os.path.join(dirpath, 'package-info.java')
            content = extract_package_info_content(package_info_path)

            structure = []
            for item in os.listdir(dirpath):
                item_path = os.path.join(dirpath, item)
                if item.endswith('.java') and item != 'package-info.java':
                    structure.append(item)
                elif os.path.isdir(item_path) and is_java_package(item_path):
                    subpackage_name = f"{package_name}.{item}"
                    structure.append(subpackage_name)

            summary.append({
                'name': package_name,
                'content': content,
                'file_structure': sorted(structure)
            })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Summary saved to {output_file}")

a = ['D:/lora/defects4j/Closure_1/Closure_1_fixed/src/', 
     'D:/lora/defects4j/Lang_1/Lang_1_fixed/src/main/java/','D:/lora/defects4j/Time_4/Time_4_fixed/src/main/java/']

summarize_package_infos('D:/lora/defects4j/Math_38/Math_38_fixed/src/main/java/')