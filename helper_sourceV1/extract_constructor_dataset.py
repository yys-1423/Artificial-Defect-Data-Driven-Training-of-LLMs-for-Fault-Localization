import random

def extract_constructor_dataset(p, simple_summary_closure):
    """
    Input format:
    [methodName, MethodComments, MethodType, MethodSignature, ClassName, ClassType, PackageName, Snippet, [Upper_classes], category]
    Outputs:
    1. ClassName
    2. MethodName
    3. MethodComments (if exists)
    4. Constructor Signature
    5. Upper Classes (if exists)
    """
    package_prob = 0.5
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
            return text + f"\n\nNote: This constructor belongs to a nested class inside: {', '.join(upperClasses)}"
        return text


    # Variant 1: Constructor Comment Summarization
    if random.random() < base_prob:
        if methodComment.strip():
            prompt = (
                "### Task: Constructor Summarization\n"
                "Summarize the following constructor given its name and class that its part of.\n\n"
                f"### Constructor Name: {methodName}\n"
                f"### Class Name: {className}\n"
            )
            prompt = add_upper_note(prompt)
            json_lines.append({"input": prompt, "output": methodComment})

    # Variant 2 : Constructor snippet generation
    if random.random() < base_prob:
        prompt = (
            "### Task: Constructor Snippet Generation\n"
            "Generate a Java constructor implementation given its name, signature, and class name.\n\n"
            f"### Class Name: {className}\n"
            f"### Signature: {methodSignature}"
        )
        output = snippet
        json_lines.append({"input": prompt, "output": output})

    return json_lines