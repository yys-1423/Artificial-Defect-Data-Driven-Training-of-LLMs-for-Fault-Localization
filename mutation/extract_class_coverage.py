import xml.etree.ElementTree as ET
import os
def parse_coverage(file_path):
    """
    Parse a Cobertura-style coverage XML file to extract coverage information for each class.
    
    For each class, this function collects:
      1. total_lines: total number of <line> elements in the class (in methods and directly under the class)
      2. method_count: total number of <method> elements in the class
      3. covered_lines: number of <line> elements with hits > 0
      4. total_line_hits: sum of hits from every <line> element in the class
      5. covered_methods: number of methods which contain at least one line with hits > 0
      
    Parameters:
      file_path (str): the path to the coverage.xml file.
    
    Returns:
      dict: Mapping of class names to a dictionary with the above coverage information.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    coverage_info = {}
    
    # Get all <package> elements
    packages = root.find('packages')
    if packages is None:
        return coverage_info  # Return empty if no packages found.
    
    for package in packages.findall('package'):
        classes = package.find('classes')
        if classes is None:
            continue
        
        # Process each <class> element
        for clazz in classes.findall('class'):
            class_name = clazz.attrib.get('name')
            total_lines = 0
            method_count = 0
            covered_lines = 0
            total_line_hits = 0
            covered_methods = 0
            
            # Process any lines defined directly inside the class (outside methods)
            class_lines_elem = clazz.find('lines')
            if class_lines_elem is not None:
                for line in class_lines_elem.findall('line'):
                    total_lines += 1
                    hits = int(line.attrib.get('hits', '0'))
                    total_line_hits += hits
                    if hits > 0:
                        covered_lines += 1
            
            # Process the methods inside the class
            methods_elem = clazz.find('methods')
            if methods_elem is not None:
                for method in methods_elem.findall('method'):
                    method_count += 1
                    method_has_coverage = False
                    method_lines_elem = method.find('lines')
                    if method_lines_elem is not None:
                        for line in method_lines_elem.findall('line'):
                            total_lines += 1
                            hits = int(line.attrib.get('hits', '0'))
                            total_line_hits += hits
                            if hits > 0:
                                covered_lines += 1
                                method_has_coverage = True
                    if method_has_coverage:
                        covered_methods += 1
            
            # Save results keyed by class name
            coverage_info[class_name] = {
                'total_lines': total_lines,
                'method_count': method_count,
                'covered_lines': covered_lines,
                'total_line_hits': total_line_hits,
                'covered_methods': covered_methods
            }
    
    return coverage_info

# Example usage:
def combine_coverage_files(file_paths):
    """
    Combine the results of multiple coverage XML files using the parse_coverage function.
    
    For each file in file_paths:
      - It calls parse_coverage and retrieves a dictionary mapping class names to their coverage metrics.
      - If a class appears in multiple files, the metrics are summed.
    
    Parameters:
      file_paths (list of str): A list of paths to coverage XML files.
    
    Returns:
      dict: A dictionary where each key is a class name and the value is another dictionary
            containing the combined metrics:
            - total_lines
            - method_count
            - covered_lines
            - total_line_hits
            - covered_methods
    """
    combined_coverage = {}
    
    for path in file_paths:
        file_coverage = parse_coverage(path)
        for class_name, metrics in file_coverage.items():
            if class_name not in combined_coverage:
                # Create a copy of the metrics dictionary for the new class entry.
                combined_coverage[class_name] = metrics.copy()
            else:
                # Sum each metric with the previously combined value.
                #combined_coverage[class_name]['total_lines'] += metrics.get('total_lines', 0)
                #combined_coverage[class_name]['method_count'] += metrics.get('method_count', 0)
                combined_coverage[class_name]['covered_lines'] += metrics.get('covered_lines', 0)
                combined_coverage[class_name]['total_line_hits'] += metrics.get('total_line_hits', 0)
                combined_coverage[class_name]['covered_methods'] += metrics.get('covered_methods', 0)
    
    return combined_coverage


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


def extract_class_coverage(p,t):
    #print(p,t)
    base_path = "/home/yinseok/lorafl/"

    if p=="Closure":
        project_path = "/home/yinseok/lorafl/temp/Closure_1/Closure_1_fixed"
    
    data_path = "/home/yinseok/lorafl/mutation_data"

    results_path = data_path + "/results"

    coverage_path = data_path + "/coverage"

    files = find_files_with_substring(coverage_path, t)

    coverage_files = []
    
    #print(files)
    for file in files:
        coverage_files.append(coverage_path+"/"+file)


    data = combine_coverage_files(coverage_files)
    #for cls, info in data.items():
    #    print(f"Class: {cls}")
    #    for key, value in info.items():
    #        print(f"  {key}: {value}")
    #    print()
    return data
#extract_class_coverage("Closure", "com.google.javascript.jscomp.AbstractPeepholeOptimization")














