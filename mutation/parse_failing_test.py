import re
import os

def parse_failing_tests(filepath):
    bug_reports = []
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].strip()
        if line.startswith('---'):
            # Extract bug name and test method
            header = line[4:].strip()
            if "::" in header:
                class_name, method_name = header.split("::", 1)
            else:
                class_name, method_name = header, ""

            i += 1
            # Gather error message (until "at" line)
            error_lines = []
            while i < n and not lines[i].strip().startswith("at"):
                error_lines.append(lines[i])
                i += 1

            # Gather stack trace (lines that start with "at")
            stack_lines = []
            while i < n and lines[i].strip().startswith("at"):
                stack_lines.append(lines[i])
                i += 1

            bug_reports.append([
                [class_name, method_name],
                ''.join(error_lines),
                ''.join(stack_lines)
            ])
        else:
            i += 1

    return bug_reports

#r = parse_failing_tests("/home/yinseok/lorafl/mutation_data/results/failing_tests__com.google.javascript.jscomp.CheckMissingReturn__3")

#for rr in r:
#    print(rr)
