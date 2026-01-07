import os
import json
from bs4 import BeautifulSoup

def is_java_package(directory):
    for file in os.listdir(directory):
        if file.endswith('.java') or file == 'package.html':
            return True
    return False

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def summarize_package_htmls(root_dir, output_file='package_summary.json'):
    summary = []

    for dirpath, _, filenames in os.walk(root_dir):
        if 'package.html' in filenames:
            rel_path = os.path.relpath(dirpath, root_dir)
            package_name = rel_path.replace(os.sep, '.')

            package_html_path = os.path.join(dirpath, 'package.html')
            with open(package_html_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_html = f.read()
                content = extract_text_from_html(raw_html)

            structure = []
            for item in os.listdir(dirpath):
                item_path = os.path.join(dirpath, item)
                if item.endswith('.java'):
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
summarize_package_htmls('D:/lora/defects4j/Math_2/Math_2_fixed/src/main/java/')