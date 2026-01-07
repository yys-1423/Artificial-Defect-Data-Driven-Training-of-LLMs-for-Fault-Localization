import xml.etree.ElementTree as ET
import os
def parse_methods_coverage(file_path, target_class_name):
    """
    Parse a Cobertura-style coverage XML file for a given class and extract method-level coverage metrics.
    
    For the given target class (identified by its 'name' attribute), this function extracts
    coverage metrics for each method contained within its <methods> element. The metrics for
    each method are:
      - method name: as given by the 'name' attribute.
      - total_lines: total number of <line> elements inside the method.
      - covered_lines: number of <line> elements with hits > 0.
      - total_line_hits: sum of all the hit counts for that method's lines.
      
    Parameters:
      file_path (str): Path to the coverage.xml file.
      target_class_name (str): The fully qualified name of the class to extract method information from.
      
    Returns:
      dict: A dictionary where each key is a method name and its value is a dictionary:
            {
                'total_lines': int,
                'covered_lines': int,
                'total_line_hits': int
            }
    """
    print(file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    methods_coverage = {}
    method_counter = {}

    packages = root.find('packages')
    if packages is None:
        return methods_coverage  # No packages element found.
    
    # Iterate over all packages and classes to find the specified target class.
    """
    for package in packages.findall('package'):
        classes = package.find('classes')
        if classes is None:
            continue
        for clazz in classes.findall('class'):
            if target_class_name in clazz.attrib.get('name'):
                methods_elem = clazz.find('methods')
                if methods_elem is None:
                    continue
                for method in methods_elem.findall('method'):
                    method_name = method.attrib.get('name')
                    total_lines = 0
                    covered_lines = 0
                    total_line_hits = 0
                    
                    # Process the <lines> block inside the method.
                    lines_elem = method.find('lines')
                    if lines_elem is not None:
                        for line in lines_elem.findall('line'):
                            total_lines += 1
                            hits = int(line.attrib.get('hits', '0'))
                            total_line_hits += hits
                            if hits > 0:
                                covered_lines += 1
                    # If the same method appears multiple times (e.g. in different packages), aggregate its metrics.
                    if method_name in methods_coverage:
                        methods_coverage[method_name]['total_lines'] += total_lines
                        methods_coverage[method_name]['covered_lines'] += covered_lines
                        methods_coverage[method_name]['total_line_hits'] += total_line_hits
                    else:
                        methods_coverage[method_name] = {
                            'total_lines': total_lines,
                            'covered_lines': covered_lines,
                            'total_line_hits': total_line_hits
                        }

    return methods_coverage"""
    for package in packages.findall('package'):
        classes = package.find('classes')
        if classes is None:
            continue
        for clazz in classes.findall('class'):
            if target_class_name in clazz.attrib.get('name'):
                methods_elem = clazz.find('methods')
                if methods_elem is None:
                    continue
                for method in methods_elem.findall('method'):
                    method_name = method.attrib.get('name')
                    total_lines = 0
                    covered_lines = 0
                    total_line_hits = 0
                    start_line = float('inf')
                    end_line = float('-inf')

                    # Process the <lines> block inside the method.
                    lines_elem = method.find('lines')
                    if lines_elem is not None:
                        for line in lines_elem.findall('line'):
                            line_num = int(line.attrib.get('number'))
                            start_line = min(start_line, line_num)
                            end_line = max(end_line, line_num)

                            total_lines += 1
                            hits = int(line.attrib.get('hits', '0'))
                            total_line_hits += hits
                            if hits > 0:
                                covered_lines += 1

                    # Construct unique method identifier
                    base_key = method_name
                    method_counter[base_key] = method_counter.get(base_key, 0) + 1
                    method_key = f"{base_key}#{method_counter[base_key]}"

                    methods_coverage[method_key] = {
                        'total_lines': total_lines,
                        'covered_lines': covered_lines,
                        'total_line_hits': total_line_hits,
                        'start_line': start_line if start_line != float('inf') else None,
                        'end_line': end_line if end_line != float('-inf') else None
                    }

    return methods_coverage


def combine_methods_coverage(file_paths, target_class_name):
    """
    Combine method-level coverage metrics for a given class from multiple coverage XML files.
    
    For each file in the provided list, the function calls parse_methods_coverage
    to obtain metrics for the specified target class and then aggregates the results
    by summing the metrics for methods with the same name.
    
    Parameters:
      file_paths (list of str): A list of paths to coverage XML files.
      target_class_name (str): The fully qualified name of the class whose method metrics should be combined.
      
    Returns:
      dict: A dictionary where each key is a method name and its value is a dictionary with aggregated metrics:
            {
                'total_lines': int,
                'covered_lines': int,
                'total_line_hits': int
            }
    """
    combined_methods = {}
    
    for path in file_paths:
        file_methods = parse_methods_coverage(path, target_class_name)
        for method_name, metrics in file_methods.items():
            if method_name in combined_methods:
                #combined_methods[method_name]['total_lines'] += metrics.get('total_lines', 0)
                combined_methods[method_name]['covered_lines'] += metrics.get('covered_lines', 0)
                combined_methods[method_name]['total_line_hits'] += metrics.get('total_line_hits', 0)
            else:
                combined_methods[method_name] = metrics.copy()
    
    return combined_methods

def find_files_with_substring(directory, substring):
    """
    Return a list of file names in the given directory
    that contain the given substring.
    """
    result = []
    # List all files in the given directory
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        # Check if it's a file and contains the substring
        if os.path.isfile(full_path) and substring in filename:
            result.append(filename)
    return result


def extract_method_coverage(p,t):
     base_path = "/home/yinseok/lorafl/"

     #if p=="Closure":
     #    project_path = "/home/yinseok/lorafl/temp/Closure_1/Closure_1_fixed"

     data_path = f"/home/yinseok/lorafl/mutation_data/{p}"

     results_path = data_path + "/results"

     coverage_path = data_path + "/coverage"

     files = find_files_with_substring(coverage_path, t)

     coverage_files = []

     for file in files:
         coverage_files.append(coverage_path+"/"+file)


     data = combine_methods_coverage(coverage_files,t)
     return data
     #for cls, info in data.items():
     #    print(f"Method: {cls}")
     #    for key, value in info.items():
     #        print(f"  {key}: {value}")
     #    print()

#extract_method_coverage("Closure", "com.google.javascript.jscomp.AbstractPeepholeOptimization")

