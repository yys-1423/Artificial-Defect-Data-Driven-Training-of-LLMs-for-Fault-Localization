import random

def extract_class_dataset(p, simple_summary_closure):
    """
    Given a class/interface/enum data tuple 'p' in the format:
      [ className, classComments, classType, PackageName, [[InnertypeName, Innertype_Type]],
        [Method Names], [Implemented Types], [Extended Types], [Upper_classes], category ]
    and a list of simple summary strings (simple_summary_closure), generate multiple prompt variations
    for training an LLM to extract the following outputs (in order):
    
      1. Package Name
      2. Class Name
      3. Class Comments
      4. Inner Types (names and types, if any)
      5. Method Names (if any)
      6. Implemented Types (if any)
      7. Extended Types (if any)
      8. Upper Classes (if any)
    
    For each of the eight tasks, two variants are produced: one without project context and one with.
    If upper classes exist, an explicit note is always added.
    Returns a list of dictionaries, each with "input" and "output" keys.
    """
    package_prob = 0.5
    method_prob = 0.5

    json_lines = []
    
    # Unpack fields from the input tuple
    className = p[0]
    classComments = p[1]
    classType = p[2]
    packageName = p[3]
    innerTypes = p[4]         # List of [InnertypeName, Innertype_Type]
    methodNames = p[5]        # List of method names
    implementedTypes = p[6]   # List of implemented types
    extendedTypes = p[7]      # List of extended types
    upperClasses = p[8]       # List of upper classes (if exists)
    # p[9] is category, which we ignore for prompt creation

    # Helper: if upper classes exist, add them to the prompt.t
    def add_upper_classes(prompt_text):
        """
        If this class is an inner/nested class, append a note about the outer (enclosing) classes.
        """
        if upperClasses:
            hierarchy = ",".join(upperClasses)
            note = f"\n\nNote: This test class is nested inside the following outer class hierarchy:\n{hierarchy}"
            return prompt_text + note
        else:
            return prompt_text


    # Similarly for methods, implemented and extended types.
    methods_str = ", ".join(methodNames) if methodNames else "None"


    

    
    # 1. Class Identification
    # Variant without project context:
    if classComments.strip():
        prompt = (
            "### Task: Test Class Identification\n"
            "Identify the test class name from the details below.\n\n"
            f"### Class Comments: {classComments}\n"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": className})
        
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Test Class Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Identify the test class name from the following details.\n\n"
                f"### Test Class Comments: {classComments}\n"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": className})
        
        # 2. Class Summarization
        # Variant without project context:
    
        prompt = (
            "### Task: Test Class Summarization\n"
            "Summarize the test class\n\n"
            f"### Test Class Name: {className}\n"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": classComments})
    
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Test Class Summarization with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Summarize the test class based on the following details.\n\n"
                f"### Test Class Name: {className}\n"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": classComments})
    
    
    # 3. Methods Identification
    # Variant without project context:
    if random.random() < method_prob:
        prompt = (
            "### Task: Test Methods Identification\n"
            "Extract all test method names defined in the test class.\n\n"
            f"### TestClass Name: {className}\n"
            f"### Test Class Comments: {classComments}\n"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": methods_str})
        
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Test Methods Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Extract all test method names defined in the test class.\n\n"
                f"### Test Class Name: {className}\n"
                f"### Test Class Comments: {classComments}\n"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": methods_str})

    
    return json_lines