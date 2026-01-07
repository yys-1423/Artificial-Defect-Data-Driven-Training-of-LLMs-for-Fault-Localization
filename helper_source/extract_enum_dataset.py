import random

def extract_enum_dataset(p, simple_summary_closure):
    """
    Given a enum/interface/enum data tuple 'p' in the format:
      [ className, classComments, classType, PackageName, [[InnertypeName, Innertype_Type]],
        [Method Names], [Implemented Types], [Extended Types], [Upper_classes], category ]
    and a list of simple summary strings (simple_summary_closure), generate multiple prompt variations
    for training an LLM to extract the following outputs (in order):
    
      1. Package Name
      2. enum Name
      3. enum Comments
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
    implemented_type_prob = 0.25
    method_prob = 0.5
    base_prob = 0.25

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
        If this enum is an inner/nested enum, append a note about the outer (enclosing) classes.
        """
        if upperClasses:
            hierarchy = " , ".join(upperClasses)
            note = f"\n\nNote: This enum is nested inside the following outer enum hierarchy:\n{hierarchy}"
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
            "Identify which package this enum belongs to based on the details below.\n\n"
            f"### enum Name: {className}\n"
            f"### enum Comments: {classComments}"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": packageName})
        
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Package Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Identify which package this enum belongs to based on the details below.\n\n"
                f"### enum Name: {className}\n"
                f"### enum Comments: {classComments}"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": packageName})
        
    # 2. enumIdentification
    # Variant without project context:
    if random.random() < base_prob:
        prompt = (
            "### Task: enum Identification\n"
            "Identify the enum name from the details below.\n\n"
            f"### enum Comments: {classComments}\n"
            f"### Package Name: {packageName}"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": className})
        
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: enum Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Identify the enum name from the following details.\n\n"
                f"### Package Name: {packageName}"
                f"### enum Comments: {classComments}\n"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": className})
        
    # 3. enumSummarization
    # Variant without project context:
    prompt = (
        "### Task: enum Summarization\n"
        "Summarize the enum using the provided comments.\n\n"
        f"### enum Name: {className}\n"
    )
    prompt = add_upper_classes(prompt)
    json_lines.append({"input": prompt, "output": classComments})
    
    # Variant with project context:
    if random.random() < package_prob:
        summary = random.choice(simple_summary_closure)
        prompt = (
            "### Task: enum Summarization with Project Context\n"
            f"Considering the project context:\n{summary}\n\n"
            "Summarize the enum based on the following details.\n\n"
            f"### enum Name: {className}\n"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": classComments})
    
    # 4. Inner Types Identification
    # Variant without project context:
    if not inner_types_str == "None":
        prompt = (
            "### Task: Inner Types Identification\n"
            "List all inner types (with their types) defined in the enum.\n\n"
            f"### enumName: {className}\n"
            f"### enum Comments: {classComments}\n"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": inner_types_str})
    
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Inner Types Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "List all inner types (with their types) defined in the enum.\n\n"
                f"### enumName: {className}\n"
                f"### enum Comments: {classComments}\n"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": inner_types_str})
    
    # 5. Methods Identification
    # Variant without project context:
    if random.random() < method_prob:
        prompt = (
            "### Task: Methods Identification\n"
            "Extract all method names defined in the enum.\n\n"
            f"### enum Name: {className}\n"
            f"### enum Comments: {classComments}\n"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": methods_str})
        
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Methods Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Extract all method names defined in the enum.\n\n"
                f"### enum Name: {className}\n"
                f"### enum Comments: {classComments}\n"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": methods_str})
    
    # 6. Implemented Types Identification
    # Variant without project context:
    if not impl_types_str=="None":
        if random.random() < implemented_type_prob:
            prompt = (
                "### Task: Implemented Types Identification\n"
                "Identify all implemented types of the enum.\n\n"
                f"### enumName: {className}\n"
                f"### enum Comments: {classComments}\n"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": impl_types_str})
            
            # Variant with project context:
            if random.random() < package_prob:
                summary = random.choice(simple_summary_closure)
                prompt = (
                    "### Task: Implemented Types Identification with Project Context\n"
                    f"Considering the project context:\n{summary}\n\n"
                    "Identify all implemented types of the enum.\n\n"
                    f"### enumName: {className}\n"
                    f"### enum Comments: {classComments}\n"
                )
                prompt = add_upper_classes(prompt)
                json_lines.append({"input": prompt, "output": impl_types_str})
    
    # 7. Extended Types Identification
    # Variant without project context:
    if not ext_types_str=="None":
        prompt = (
            "### Task: Extended Types Identification\n"
            "Determine all extended types for the enum.\n\n"
            f"### enumName: {className}\n"
            f"### enum Comments: {classComments}\n"
        )
        prompt = add_upper_classes(prompt)
        json_lines.append({"input": prompt, "output": ext_types_str})
        
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Extended Types Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Determine all extended types for the enum.\n\n"
                f"### enumName: {className}\n"
                f"### enum Comments: {classComments}\n"
            )
            prompt = add_upper_classes(prompt)
            json_lines.append({"input": prompt, "output": ext_types_str})
    
    # 8. Upper Classes Identification
    # Variant without project context:
    if upperClasses:
        # Variant without project context
        prompt = (
            "### Task: Outer class Identification\n"
            "Determine the outer (enclosing) classes for the following enum. These represent the hierarchy of classes this one is nested inside.\n\n"
            f"### enumName: {className}\n"
            f"### enum Comments: {classComments}\n"
        )
        json_lines.append({
            "input": prompt,
            "output": " , ".join(upperClasses)
        })

        # Variant with project context
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Outer class Identification with Project Context\n"
                f"Considering the following project context:\n{summary}\n\n"
                "Determine the outer (enclosing) classes for the given enum. These represent the enum nesting structure.\n\n"
                f"### enumName: {className}\n"
                f"### enum Comments: {classComments}\n"
            )
            json_lines.append({
                "input": prompt,
                "output": " , ".join(upperClasses)
            })
    prompt = add_upper_classes(prompt)
    json_lines.append({"input": prompt, "output": upper_str})
    
    return json_lines 
