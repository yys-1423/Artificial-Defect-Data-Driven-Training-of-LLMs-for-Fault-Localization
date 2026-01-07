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
    package_prob = 0.5
    low_prob = 0.1
    base_prob = 0.25
    method_prob = 0.5

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
            return text + f"\n\nNote: This test method belongs to a nested class inside: {', '.join(upperClasses)}"
        return text

    # Variant 1: Identify Class from Method
    if random.random()<base_prob:
        if random.random() < 0.5:
            prompt = (
                "### Task: Test Class Identification\n"
                "Identify the test class that defines the following test method.\n\n"
                f"### Test Method Signature: {methodSignature}"
            )
            prompt = add_upper_note(prompt)
            json_lines.append({"input": prompt, "output": className})
        else:
            prompt = (
                "### Task: Test Class Identification\n"
                "Identify the test class that defines the following test method.\n\n"
                f"### Test Method Snippet: {snippet}"
            )
            prompt = add_upper_note(prompt)
            json_lines.append({"input": prompt, "output": className})

    # Variant 2: Identify Method
    if random.random()<base_prob:
        if random.random() < 0.5:
            prompt = (
                "### Task: Test Method Identification\n"
                "Identify the following test method.\n\n"
                f"### Test Method Signature: {methodSignature}"
            )
            prompt = add_upper_note(prompt)
            json_lines.append({"input": prompt, "output": methodName})
        else:
            prompt = (
                "### Task: Test Method Identification\n"
                "Identify the following test method.\n\n"
                f"### Test Method Snippet {snippet}"
            )
            prompt = add_upper_note(prompt)
            json_lines.append({"input": prompt, "output": methodName})

    # Variant 3: Method Comment Summarization
    if methodComment.strip():
        if random.random() < 0.5:
            if methodComment.strip():
                prompt = (
                    "### Task: Test Method Summarization\n"
                    "Summarize the following test method.\n\n"
                    f"### Test Method Name: {methodName}\n"
                )
                prompt = add_upper_note(prompt)
                json_lines.append({"input": prompt, "output": methodComment})

        else:
            if methodComment.strip():
                prompt = (
                    "### Task: Test Method Summarization\n"
                    "Summarize the following test method.\n\n"
                    f"### Test Method Snippet: {snippet}"
                )
                prompt = add_upper_note(prompt)
                json_lines.append({"input": prompt, "output": methodComment})


    # Variant 4: Identify Upper Classes if exists
    if random.random() < low_prob:
        if upperClasses:
            prompt = (
                "### Task: Outer Test Class Identification\n"
                "Identify the enclosing class hierarchy of the following test method.\n\n"
                f"### Test Method Name: {methodName}\n"
                f"### Test Class: {className}"
            )
            json_lines.append({"input": prompt, "output": ', '.join(upperClasses)})

    # Variant 5 : Method snippet generation
    if random.random() < base_prob:
        prompt = (
            "### Task: Test Method Snippet Generation\n"
            "Generate a Java unit test method implementation given its name, signature, and class name.\n\n"
            f"### Test Class Name: {className}\n"
            f"### Test Method Name: {methodSignature}"
        )
        if methodComment:
            prompt+=f"### Test Comment: {methodComment}"
        output = snippet
        json_lines.append({"input": prompt, "output": output})



    # Variant 6 : Method signature generation with comment
    if random.random() <base_prob:
        if methodComment.strip():
            prompt = (
                "### Task: Test Method Signature Generation\n"
                "Generate the Java unit test method signature based on the name, and comment\n\n"
                f"### Method Name {methodName}"
            )
            if methodComment:
                prompt+=f"### Test Comment: {methodComment}"
            output = methodSignature
            json_lines.append({"input": prompt, "output": output})
    

    return json_lines