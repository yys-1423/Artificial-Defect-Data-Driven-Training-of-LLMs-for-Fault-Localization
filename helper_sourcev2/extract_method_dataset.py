import random

def extract_method_dataset(p, simple_summary_closure):
    """
    Input format:
    [methodName, MethodComments, MethodType, MethodSignature, ClassName, ClassType, PackageName, Snippet, [Upper_classes], category]
    Outputs:
    1. ClassName
    2. MethodName
    3. MethodComments (if exists)
    4. Method Signature
    5. Upper Classes (if exists)
    """
    package_prob = 0.1
    base_prob = 0.1
    method_prob = 0.25

    json_lines = []

    methodName = p[0]
    methodComment = p[1]
    methodType = p[2]
    methodSignature = p[3]
    className = p[4]
    classType = p[5]
    packageName = p[6]
    snippet = p[7]
    upperClasses = p[8]

    # Helper
    def add_upper_note(text):
        if upperClasses:
            return text + f"\n\nNote: This method belongs to a nested class inside: {', '.join(upperClasses)}"
        return text

    # Variant 1: Identify Class from Method
    if random.random() < base_prob:
        if random.random() < 0.8:
            prompt = (
                "### Task: Class Identification\n"
                "Identify the class that defines the following method.\n\n"
                f"### Method Signature: {methodSignature}"
                f"### Method Comment: {methodComment}"
            )
            prompt = add_upper_note(prompt)
            json_lines.append({"input": prompt, "output": className})
        
        else:
            prompt = (
                "### Task: Class Identification\n"
                "Identify the class that defines the following method.\n\n"
                f"### Method Signature: {methodSignature}"
                f"### Method Snippet: {snippet}"
            )
            prompt = add_upper_note(prompt)
            json_lines.append({"input": prompt, "output": className})            



    # Variant 2: Method Comment Summarization
    if random.random() < base_prob:
        if methodComment.strip():
            if random.random()<0.8:
                prompt = (
                    "### Task: Method Summarization\n"
                    "Summarize the following method.\n\n"
                    f"### Method Name: {methodName}\n"
                )
                prompt = add_upper_note(prompt)
                json_lines.append({"input": prompt, "output": methodComment})
            else:
                prompt = (
                    "### Task: Method Summarization\n"
                    "Summarize the following method.\n\n"
                    f"### Method Snippet: {snippet}\n"
                )
                prompt = add_upper_note(prompt)
                json_lines.append({"input": prompt, "output": methodComment})                



    # Variant 5: Identify Upper Classes if exists
    if random.random() < base_prob:
        if upperClasses:
            prompt = (
                "### Task: Outer Class Identification\n"
                "Identify the enclosing class hierarchy of the following method.\n\n"
                f"### Method Name: {methodName}\n"
                f"### Class: {className}"
            )
            json_lines.append({"input": prompt, "output": ', '.join(upperClasses)})

    
    # Variant 6 : Method snippet generation
    if random.random() < base_prob:
        prompt = (
            "### Task: Method Snippet Generation\n"
            "Generate a Java method implementation given its name, signature, and class name.\n\n"
            f"### Class Name: {className}\n"
            f"### Method Name: {methodSignature}"
            f"### Method Comments: {methodComment}"
        )
        output = snippet
        json_lines.append({"input": prompt, "output": output})

    # Variant 7 : Method signature generation with comment
    if random.random() <base_prob:
        if methodComment.strip():
            prompt = (
                "### Task: Method Signature Generation\n"
                "Generate the Java method signature based on the name, comment, and class name.\n\n"
                f"### Class Name: {className}\n"
                f"### Comment: {methodComment}"
            )
            output = methodSignature
            json_lines.append({"input": prompt, "output": output})
    
    

    # With project context
    if random.random() < package_prob:
        if random.random() <base_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                f"### Task: Method Identification with Project Context\n"
                f"Project Context:\n{summary}\n\n"
                f"Which class defines this method?\n\n"
                f"### Method Name: {methodName}"
            )
            prompt = add_upper_note(prompt)
            json_lines.append({"input": prompt, "output": className})



        if random.random() <base_prob:
            summary = random.choice(simple_summary_closure)
            prompt = (
                "### Task: Method Snippet Generation with Project Context\n"
                f"Project Context:\n{summary}\n\n"
                "Generate the Java method body using the name, signature, and class information.\n\n"
                f"### Class Name: {className}\n"
                f"### Method Name: {methodName}\n"
                f"### Signature: {methodSignature}"
                f"### Comment: {methodComment}"
            )
            output = snippet
            json_lines.append({"input": prompt, "output": output})


    return json_lines
