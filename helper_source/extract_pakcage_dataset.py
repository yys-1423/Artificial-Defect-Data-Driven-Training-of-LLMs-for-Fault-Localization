import random

def extract_package_data(p, simple_summary_closure):
    json_lines = []
    
    # --- Base Package Summarization Variants ---
    # Variant 1a: Full class list with package name
    json_lines.append({
        "input": f"### Task: Package Summarization\nPlease generate a concise summary for the package below.\n\n### Package Name: {p[0]}\n### Classes: {', '.join(p[2])}",
        "output": p[1]
    })
    # Variant 1b: Partial class list with package name
    class_sample = random.sample(p[2], max(3, len(p[2]) // 3))
    json_lines.append({
        "input": f"### Task: Package Summarization\nPlease generate a concise summary for the package below.\n\n### Package Name: {p[0]}\n### Classes: {', '.join(class_sample)}",
        "output": p[1]
    })
    # Variant 1c: Package name only
    json_lines.append({
        "input": f"### Task: Package Summarization\nPlease generate a concise summary for the package below.\n\n### Package Name: {p[0]}",
        "output": p[1]
    })
    # Variant 1d: Based solely on class names
    if random.random() < 0.5:
        json_lines.append({
            "input": f"### Task: Package Summarization\nPlease summarize the functionality of the package based solely on its class names.\n\n### Classes: {', '.join(p[2])}",
            "output": p[1]
        })
    
    # --- Base Package Identification Variants ---
    # Variant 2a: Description + full class list
    json_lines.append({
        "input": f"### Task: Package Identification\nIdentify the package name from the given description and class list.\n\n### Description: {p[1]}\n### Classes: {', '.join(p[2])}",
        "output": p[0]
    })
    # Variant 2b: Description only
    json_lines.append({
        "input": f"### Task: Package Identification\nIdentify the package name based on the following description.\n\n### Description: {p[1]}",
        "output": p[0]
    })
    # Variant 2c: Classes only (partial sample)
    if random.random() < 0.5:
        json_lines.append({
            "input": f"### Task: Package Identification\nIdentify the package name from the given classes.\n\n### Classes: {', '.join(class_sample)}",
            "output": p[0]
        })
    
    # --- Base Class Identification Variants ---
    # Variant 3a: Listing classes using package name and class list
    if random.random() < 0.5:
        json_lines.append({
            "input": f"### Task: Class Identification\nList all classes defined in the following package.\n\n### Package Name: {p[0]}\n### Classes: {', '.join(p[2])}",
            "output": ', '.join(p[2])
        })
    # Variant 3b: Listing classes using package name only
    if random.random() < 0.5:
        json_lines.append({
            "input": f"### Task: Class Identification\nList all classes that belong to the package below.\n\n### Package Name: {p[0]}",
            "output": ', '.join(p[2])
        })
    
    # --- Additional Variants that Incorporate Project Summary (Closure Context) ---
    # Summarization with full class list
    summary = random.choice(simple_summary_closure)
    json_lines.append({
        "input": f"### Task: Package Summarization with Project Context\nConsidering the following project context:\n{summary}\n\nGenerate a concise summary for the package below.\n\n### Package Name: {p[0]}\n### Classes: {', '.join(p[2])}",
        "output": p[1]
    })
    # Summarization with partial class list
    summary = random.choice(simple_summary_closure)
    class_sample = random.sample(p[2], max(3, len(p[2]) // 3))
    json_lines.append({
        "input": f"### Task: Package Summarization with Project Context\nBased on the project context below:\n{summary}\n\nGenerate a concise summary for the package below.\n\n### Package Name: {p[0]}\n### Classes: {', '.join(class_sample)}",
        "output": p[1]
    })
    # Summarization with package name only
    summary = random.choice(simple_summary_closure)
    json_lines.append({
        "input": f"### Task: Package Summarization with Project Context\nTaking into account the project context:\n{summary}\n\nGenerate a concise summary for the following package.\n\n### Package Name: {p[0]}",
        "output": p[1]
    })
    # Summarization based solely on class names with project context
    if random.random() < 0.5:
        summary = random.choice(simple_summary_closure)
        json_lines.append({
            "input": f"### Task: Package Summarization with Project Context\nGiven the project context below:\n{summary}\n\nSummarize the functionality of the package based solely on its class names.\n\n### Classes: {', '.join(p[2])}",
            "output": p[1]
        })
    
    # Identification with project context: description + full class list
    summary = random.choice(simple_summary_closure)
    json_lines.append({
       "input": f"### Task: Package Identification with Project Context\nConsidering the project context:\n{summary}\n\nIdentify the package name from the following description and class list.\n\n### Description: {p[1]}\n### Classes: {', '.join(p[2])}",
       "output": p[0]
    })
    # Identification with project context: description only
    summary = random.choice(simple_summary_closure)
    json_lines.append({
       "input": f"### Task: Package Identification with Project Context\nTaking into account the project context:\n{summary}\n\nIdentify the package name based solely on the following description.\n\n### Description: {p[1]}",
       "output": p[0]
    })
    # Identification with project context: classes only (partial sample)
    if random.random() < 0.5:
        summary = random.choice(simple_summary_closure)
        class_sample = random.sample(p[2], max(3, len(p[2]) // 3))
        json_lines.append({
        "input": f"### Task: Package Identification with Project Context\nWith the project context in mind:\n{summary}\n\nIdentify the package name from the following classes.\n\n### Classes: {', '.join(class_sample)}",
        "output": p[0]
        })
    
    # Class Identification with project context: using package name and class list
    #if random.random() < 0.5:
    #    summary = random.choice(simple_summary_closure)
    #    json_lines.append({
    #    "input": f"### Task: Class Identification with Project Context\nConsidering the project context below:\n{summary}\n\nList all classes defined in the following package.\n\n### Package Name: {p[0]}\n### Classes: {', '.join(p[2])}",
    #    "output": ', '.join(p[2])
    #    })

    # Class Identification with project context: using package name only
    #if random.random() < 0.5:
    #    summary = random.choice(simple_summary_closure)
    #    json_lines.append({
    #    "input": f"### Task: Class Identification with Project Context\nGiven the project context:\n{summary}\n\nList all classes that belong to the following package.\n\n### Package Name: {p[0]}",
    #    "output": ', '.join(p[2])
    #    })
    
    return json_lines

