import random

def extract_class_dataset(p, simple_summary_closure):
    """
    """
    package_prob = 0.1
    implemented_type_prob = 0.1
    method_prob = 0.25
    base_prob = 1
    upper_class_prob = 0.5

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
            note = f"\n\nNote: This class is nested inside the following outer class hierarchy:\n{hierarchy}"
            return prompt_text + note
        else:
            return prompt_text

    # Helper: format list of inner types as "name (type)" pairs.
    inner_types_str = ", ".join([f"{it[0]} ({it[1]})" for it in innerTypes]) if innerTypes else "None"
    # Similarly for methods, implemented and extended types.
    methods_str = ", ".join(methodNames) if methodNames else "None"
    impl_types_str = ", ".join(implementedTypes) if implementedTypes else "None"
    ext_types_str = ", ".join(extendedTypes) if extendedTypes else "None"
    upper_str = ", ".join(upperClasses) if upperClasses else "None"

    # 1. Package Identification
    # Variant without project context:
    if random.random() < base_prob:
        prompt = (
            "### Task: Package Identification\n"
            "Identify which package this class belongs to based on the details below.\n\n"
            f"### Class Name: {className}\n"
            f"### Class Comments: {classComments}"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": packageName})
    
    # Variant with project context:
    if random.random() < base_prob:

        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Package Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Identify which package this class belongs to based on the details below.\n\n"
                f"### Class Name: {className}\n"
                f"### Class Comments: {classComments}"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": packageName})
    
    # 2. Class Identification
    # Variant without project context:
    if random.random() < base_prob:
        prompt = (
            "### Task: Class Identification\n"
            "Identify the class name from the details below.\n\n"
            f"### Class Comments: {classComments}\n"
            f"### Package Name: {packageName}"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": className})
    
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Class Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Identify the class name from the following details.\n\n"
                f"### Class Comments: {classComments}\n"
                f"### Package Name: {packageName}"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": className})
    
    # 3. Class Summarization
    # Variant without project context:
    if random.random() < base_prob:
        prompt = (
            "### Task: Class Summarization\n"
            "Summarize the class using the provided comments.\n\n"
            f"### Class Name: {className}\n"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": classComments})
    
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Class Summarization with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Summarize the class based on the following details.\n\n"
                f"### Class Name: {className}\n"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": classComments})
        
    # 4. Inner Types Identification
    # Variant without project context:
    if random.random() < base_prob:
        if not inner_types_str == "None":
            prompt = (
                "### Task: Inner Types Identification\n"
                "List all inner types (with their types) defined in the class.\n\n"
                f"### Class Name: {className}\n"
                f"### Class Comments: {classComments}"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": inner_types_str})
        
            # Variant with project context:
            if random.random() < package_prob:
                summary = random.choice(simple_summary_closure)
                prompt = (
                    "### Task: Inner Types Identification with Project Context\n"
                    f"Considering the project context:\n{summary}\n\n"
                    "List all inner types (with their types) defined in the class.\n\n"
                    f"### Class Name: {className}\n"
                    f"### Class Comments: {classComments}"
                )
                prompt = add_upper_classes(prompt)
                json_lines.append({"input": prompt, "output": inner_types_str})
        
    # 5. Methods Identification
    # Variant without project context:
    if random.random() < base_prob:
        if random.random() < method_prob:
            prompt = (
                "### Task: Methods Identification\n"
                "Extract all method names defined in the class.\n\n"
                f"### Class Name: {className}\n"
                f"### Class Comments: {classComments}"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": methods_str})
            
            # Variant with project context:
            if random.random() < package_prob:
                summary = random.choice(simple_summary_closure)
                prompt = (
                    "### Task: Methods Identification with Project Context\n"
                    f"Considering the project context:\n{summary}\n\n"
                    "Extract all method names defined in the class.\n\n"
                    f"### Class Name: {className}\n"
                    f"### Class Comments: {classComments}"
                )
                prompt = add_upper_classes(prompt)
                json_lines.append({"input": prompt, "output": methods_str})
        
    # 6. Implemented Types Identification
    # Variant without project context:
    if random.random() < base_prob:
        if not impl_types_str=="None":
            if random.random() < implemented_type_prob:
                prompt = (
                    "### Task: Implemented Types Identification\n"
                    "Identify all implemented types of the class.\n\n"
                    f"### Class Name: {className}\n"
                    f"### Class Comments: {classComments}"
                )
                prompt = add_upper_classes(prompt)
                json_lines.append({"input": prompt, "output": impl_types_str})
                
                # Variant with project context:
                if random.random() < package_prob:
                    summary = random.choice(simple_summary_closure)
                    prompt = (
                        "### Task: Implemented Types Identification with Project Context\n"
                        f"Considering the project context:\n{summary}\n\n"
                        "Identify all implemented types of the class.\n\n"
                        f"### Class Name: {className}\n"
                        f"### Class Comments: {classComments}"
                    )
                    prompt = add_upper_classes(prompt)
                    json_lines.append({"input": prompt, "output": impl_types_str})
        
    # 7. Extended Types Identification
    # Variant without project context:
    if random.random() < base_prob:
        if not ext_types_str=="None":
            prompt = (
                "### Task: Extended Types Identification\n"
                "Determine all extended types for the class.\n\n"
                f"### Class Name: {className}\n"
                f"### Class Comments: {classComments}"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": ext_types_str})
            
            # Variant with project context:
            if random.random() < package_prob:
                summary = random.choice(simple_summary_closure)
                prompt = (
                    "### Task: Extended Types Identification with Project Context\n"
                    f"Considering the project context:\n{summary}\n\n"
                    "Determine all extended types for the class.\n\n"
                    f"### Class Name: {className}\n"
                    f"### Class Comments: {classComments}"
                )
                prompt = add_upper_classes(prompt)
                json_lines.append({"input": prompt, "output": ext_types_str})
        
    # 8. Upper Classes Identification
    # Variant without project context:
    if random.random() < base_prob:
        if random.random() < upper_class_prob:
            if upperClasses:
                # Variant without project context
                prompt = (
                    "### Task: Outer Class Identification\n"
                    "Determine the outer (enclosing) classes for the following class. These represent the hierarchy of classes this one is nested inside.\n\n"
                    f"### Class Name: {className}\n"
                    f"### Class Comments: {classComments}"
                )
                json_lines.append({
                    "input": prompt,
                    "output": ",".join(upperClasses)
                })

                # Variant with project context
                if random.random() < package_prob:
                    summary = random.choice(simple_summary_closure)
                    prompt = (
                        "### Task: Outer Class Identification with Project Context\n"
                        f"Considering the following project context:\n{summary}\n\n"
                        "Determine the outer (enclosing) classes for the given class. These represent the class nesting structure.\n\n"
                        f"### Class Name: {className}\n"
                        f"### Class Comments: {classComments}"
                    )
                    json_lines.append({
                        "input": prompt,
                        "output": ",".join(upperClasses)
                    })

    
    return json_lines
