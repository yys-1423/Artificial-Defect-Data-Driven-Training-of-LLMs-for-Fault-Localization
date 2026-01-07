import random



def extract_interface_dataset(p, simple_summary_closure):
    """
    Given a interface/interface/enum data tuple 'p' in the format:
      [ interfaceName, interfaceComments, interfaceType, PackageName, [[InnertypeName, Innertype_Type]],
        [Method Names], [Implemented Types], [Extended Types], [Upper_interfaces], category ]
    and a list of simple summary strings (simple_summary_closure), generate multiple prompt variations
    for training an LLM to extract the following outputs (in order):
    
      1. Package Name
      2. interface Name
      3. interface Comments
      4. Inner Types (names and types, if any)
      5. Method Names (if any)
      6. Implemented Types (if any)
      7. Extended Types (if any)
      8. Upper interfaces (if any)
    
    For each of the eight tasks, two variants are produced: one without project context and one with.
    If upper interfaces exist, an explicit note is always added.
    Returns a list of dictionaries, each with "input" and "output" keys.
    """
    base_prob = 0.25
    package_prob = 0.1
    implemented_type_prob = 0.1
    method_prob = 0.1

    json_lines = []
    
    # Unpack fields from the input tuple
    interfaceName = p[0]
    interfaceComments = p[1]
    interfaceType = p[2]
    packageName = p[3]
    innerTypes = p[4]         # List of [InnertypeName, Innertype_Type]
    methodNames = p[5]        # List of method names
    implementedTypes = p[6]   # List of implemented types
    extendedTypes = p[7]      # List of extended types
    upperinterfaces = p[8]       # List of upper interfaces (if exists)
    # p[9] is category, which we ignore for prompt creation

    # Helper: if upper interfaces exist, add them to the prompt.t
    def add_upper_interfaces(prompt_text):
        """
        If this interface is an inner/nested interface, append a note about the outer (enclosing) interfaces.
        """
        if upperinterfaces:
            hierarchy = " , ".join(upperinterfaces)
            note = f"\n\nNote: This interface is nested inside the following outer class hierarchy:\n{hierarchy}"
            return prompt_text + note
        else:
            return prompt_text

    # Helper: format list of inner types as "name (type)" pairs.
    inner_types_str = ", ".join([f"{it[0]} ({it[1]})" for it in innerTypes]) if innerTypes else "None"
    # Similarly for methods, implemented and extended types.
    methods_str = ", ".join(methodNames) if methodNames else "None"
    impl_types_str = ", ".join(implementedTypes) if implementedTypes else "None"
    ext_types_str = ", ".join(extendedTypes) if extendedTypes else "None"
    upper_str = ", ".join(upperinterfaces) if upperinterfaces else "None"

    # 1. Package Identification
    # Variant without project context:
    prompt = (
        "### Task: Package Identification\n"
        "Identify which package this interface belongs to based on the details below.\n\n"
        f"### interface Name: {interfaceName}\n"
        f"### interface Comments: {interfaceComments}"
    )
    prompt = add_upper_interfaces(prompt)
    json_lines.append({"input": prompt, "output": packageName})
    
    # Variant with project context:
    if random.random() < package_prob:
        summary = random.choice(simple_summary_closure)
        prompt = (
            "### Task: Package Identification with Project Context\n"
            f"Considering the project context:\n{summary}\n\n"
            "Identify which package this interface belongs to based on the details below.\n\n"
            f"### interface Name: {interfaceName}\n"
            f"### interface Comments: {interfaceComments}"
        )
        prompt = add_upper_interfaces(prompt)
        json_lines.append({"input": prompt, "output": packageName})
    
    # 2. interface Identification
    # Variant without project context:
    prompt = (
        "### Task: interface Identification\n"
        "Identify the interface name from the details below.\n\n"
        f"### interface Comments: {interfaceComments}\n"
        f"### Package Name: {packageName}"
    )
    prompt = add_upper_interfaces(prompt)
    json_lines.append({"input": prompt, "output": interfaceName})
    
    # Variant with project context:
    if random.random() < package_prob:
        summary = random.choice(simple_summary_closure)
        prompt = (
            "### Task: interface Identification with Project Context\n"
            f"Considering the project context:\n{summary}\n\n"
            "Identify the interface name from the following details.\n\n"
            f"### Package Name: {packageName}"
            f"### interface Comments: {interfaceComments}"
        )
        prompt = add_upper_interfaces(prompt)
        json_lines.append({"input": prompt, "output": interfaceName})
    
    # 3. interface Summarization
    # Variant without project context:
    prompt = (
        "### Task: interface Summarization\n"
        "Summarize the interface\n"
        f"### interface Name: {interfaceName}\n"
    )
    prompt = add_upper_interfaces(prompt)
    json_lines.append({"input": prompt, "output": interfaceComments})
    
    # Variant with project context:
    if random.random() < package_prob:
        summary = random.choice(simple_summary_closure)
        prompt = (
            "### Task: interface Summarization with Project Context\n"
            f"Considering the project context:\n{summary}\n\n"
            "Summarize the interface based on the following details.\n\n"
            f"### interface Name: {interfaceName}\n"
        )
        prompt = add_upper_interfaces(prompt)
        json_lines.append({"input": prompt, "output": interfaceComments})
        
    # 4. Inner Types Identification
    # Variant without project context:
    if not inner_types_str == "None":
        prompt = (
            "### Task: Inner Types Identification\n"
            "List all inner types (with their types) defined in the interface.\n\n"
            f"### interface Name: {interfaceName}\n"
            f"### interface Comments: {interfaceComments}"
        )
        prompt = add_upper_interfaces(prompt)
        json_lines.append({"input": prompt, "output": inner_types_str})
    
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Inner Types Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "List all inner types (with their types) defined in the interface.\n\n"
                f"### interface Name: {interfaceName}\n"
                f"### interface Comments: {interfaceComments}"
            )
            prompt = add_upper_interfaces(prompt)
            json_lines.append({"input": prompt, "output": inner_types_str})
    
    # 5. Methods Identification
    # Variant without project context:
    if random.random() < method_prob:
        prompt = (
            "### Task: Methods Identification\n"
            "Extract all method names defined in the interface.\n\n"
            f"### interface Name: {interfaceName}\n"
            f"### interface Comments: {interfaceComments}"
        )
        prompt = add_upper_interfaces(prompt)
        json_lines.append({"input": prompt, "output": methods_str})
        
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Methods Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Extract all method names defined in the interface.\n\n"
                f"### interface Name: {interfaceName}\n"
                f"### interface Comments: {interfaceComments}"
            )
            prompt = add_upper_interfaces(prompt)
            json_lines.append({"input": prompt, "output": methods_str})
    
    # 6. Implemented Types Identification
    # Variant without project context:
    if not impl_types_str=="None":
        if random.random() < implemented_type_prob:
            prompt = (
                "### Task: Implemented Types Identification\n"
                "Identify all implemented types of the interface.\n\n"
                f"### interface Name: {interfaceName}\n"
                f"### interface Comments: {interfaceComments}"
            )
            prompt = add_upper_interfaces(prompt)
            json_lines.append({"input": prompt, "output": impl_types_str})
            
            # Variant with project context:
            if random.random() < package_prob:
                summary = random.choice(simple_summary_closure)
                prompt = (
                    "### Task: Implemented Types Identification with Project Context\n"
                    f"Considering the project context:\n{summary}\n\n"
                    "Identify all implemented types of the interface.\n\n"
                    f"### interface Name: {interfaceName}\n"
                    f"### interface Comments: {interfaceComments}"
                )
                prompt = add_upper_interfaces(prompt)
                json_lines.append({"input": prompt, "output": impl_types_str})
    
    # 7. Extended Types Identification
    # Variant without project context:
    if not ext_types_str=="None":
        prompt = (
            "### Task: Extended Types Identification\n"
            "Determine all extended types for the interface.\n\n"
            f"### interface Name: {interfaceName}\n"
            f"### interface Comments: {interfaceComments}"
        )
        prompt = add_upper_interfaces(prompt)
        json_lines.append({"input": prompt, "output": ext_types_str})
        
        # Variant with project context:
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Extended Types Identification with Project Context\n"
                f"Considering the project context:\n{summary}\n\n"
                "Determine all extended types for the interface.\n\n"
                f"### interface Name: {interfaceName}\n"
                f"### interface Comments: {interfaceComments}"
            )
            prompt = add_upper_interfaces(prompt)
            json_lines.append({"input": prompt, "output": ext_types_str})
    
    # 8. Upper interfaces Identification
    # Variant without project context:
    if upperinterfaces:
        # Variant without project context
        prompt = (
            "### Task: Outer class Identification\n"
            "Determine the outer (enclosing) classes for the following interface. These represent the hierarchy of interfaces this one is nested inside.\n\n"
            f"### interface Name: {interfaceName}\n"
            f"### interface Comments: {interfaceComments}"
        )
        json_lines.append({
            "input": prompt,
            "output": " , ".join(upperinterfaces)
        })

        # Variant with project context
        if random.random() < package_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Outer class Identification with Project Context\n"
                f"Considering the following project context:\n{summary}\n\n"
                "Determine the outer (enclosing) classes for the given interface. These represent the interface nesting structure.\n\n"
                f"### interface Name: {interfaceName}\n"
                f"### interface Comments: {interfaceComments}"
            )
            json_lines.append({
                "input": prompt,
                "output": " , ".join(upperinterfaces)
            })
    prompt = add_upper_interfaces(prompt)
    json_lines.append({"input": prompt, "output": upper_str})
    
    return json_lines
