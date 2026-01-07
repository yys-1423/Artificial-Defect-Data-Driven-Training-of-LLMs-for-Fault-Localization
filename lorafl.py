from helper.get_answer import get_answer
from helper.reconstruct_class import reconstruct_class
from helper.collect_covered_classes import collect_covered_classes
from helper.reconstruct_class_with_method import reconstruct_class_with_method
from helper.helpers import format_test_info, format_test_info_exclude_related, extract_class_from_response, get_review, process_response,check_if_exist_class, check_if_exist_method, count_test_occurrences, process_response_simple

project_basic_dir = get_base_dir()
p,b,_,_,_ = get_bug_info()

import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Optionally import PeftModel only if parameter_dir is provided
try:
    from peft import PeftModel
except ImportError:
    PeftModel = None

class LlamaModelWrapper:
    def __init__(self, model_dir, parameter_dir=None, max_context_length=8192):
        self.max_context_length = max_context_length
        
        # Load tokenizer once
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model once
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        if parameter_dir and PeftModel is not None:
            self.model = PeftModel.from_pretrained(self.model, parameter_dir)
        
        self.model.eval()

    def generate_response(self, prompt, max_new_tokens=64, temperature=0.7, top_p=0.9):
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.model.device)
        if input_ids.shape[1] > self.max_context_length:
            return -1, f"Input too long: {input_ids.shape[1]} tokens (max {self.max_context_length})"
        
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids=input_ids,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=self.tokenizer.eos_token_id
            )
        response_text = self.tokenizer.decode(
            output_ids[0][input_ids.shape[1]:], 
            skip_special_tokens=True
        )
        return 1, response_text.strip()



# Example of a function that processes multiple prompts
def mem_main(repeat):

    verbose = True
    
    # Assume create_log_directory, project_basic_dir, p, b, and other variables are defined elsewhere.
    log_dir = create_log_directory(f"{project_basic_dir}update_log/03_06")
    if log_dir is None:
        return -1
    count = 0

    # Load the LLaMA model only once
    llama_model = LlamaModelWrapper(model_dir, parameter_dir)

    for i in range(len(p)):
        if p[i] != "Closure":
            continue
    
        project_name = p[i]
        bug_id = b[i]
        
        print("begin : ", project_name, bug_id)

        # Define the directories
        base_path = f"{project_basic_dir}data/{project_name}/"
        summary_dir = f"{base_path}class_summaries/"
        data_dir = f"{base_path}data/{project_name}_{bug_id}/"
        #memory_path = f"{base_path}memory/{mem_path}/"

        # Define the file path
        summary_file_path = f"{base_path}summary.txt"
        class_file_path = f"{base_path}classes.csv"
        test_info_path = f"{data_dir}failed_test.json"

        covered_class_file_path = f"{data_dir}covered_classes.txt"
        
        
        # Read and store file contents
        file_names = []
        summaries = []
        try:
            
            with open(covered_class_file_path, 'r') as f:
                covered_classes = f.read()

            with open(summary_file_path, 'r') as f:
                summary_content = f.read()
            
            with open(class_file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    file_names.append(row[0].strip())
                    summaries.append(row[1].strip())

            with open(test_info_path, 'r') as f:
                test_info_content = json.load(f)  # Load JSON data as a Python dictionary      
                
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")  
            
        if covered_classes == '-1':
            print("bug does not exist on top 60 classes...",project_name,bug_id)
            return 0, model,["Not_on_50"],[]
        else:
            covered_classes = covered_classes.split('\n')      
            
        #extracting class names
        class_name_set = set()
        duplicates = set()

        covered_classes_for_prompt = ""####
        for i, covered_class in enumerate(covered_classes,start=1):
            if covered_class in file_names:
                index = file_names.index(covered_class)
                class_name = covered_class.split(".")[-2]
                if class_name in class_name_set:
                    duplicates.add(class_name)  # Store duplicates
                else:
                    class_name_set.add(class_name)

                if stage_2_simple:
                    summary = summaries[index]
                else:
                    if project_name == "Chart":
                        summary_file_name = "org.jfree." +covered_class.rsplit(".java", 1)[0] +"_summary.txt"
                    elif project_name == "Closure":
                        summary_file_name = "com.google." +covered_class.rsplit(".java", 1)[0] +"_summary.txt"
                    elif project_name == "Lang" or project_name=="Math":
                        summary_file_name = "org.apache." +covered_class.rsplit(".java", 1)[0] +"_summary.txt"
                    elif project_name == "Time":
                        summary_file_name = "org.joda." +covered_class.rsplit(".java", 1)[0] +"_summary.txt"
                    summary_path = os.path.join(summary_dir, summary_file_name)

                    if os.path.exists(summary_path):
                        with open(summary_path, 'r') as f:
                            summary = f.read().strip()
                    else:
                        summary = "Summary not found"

                covered_classes_for_prompt += f"  Class {i} : <{class_name}>, summary : {summary}\n"
            else:
                continue
        
        class_length = len(covered_classes)
      
        test_info = count_test_occurrences(project_name, bug_id)


        #Log that will be saved
        log = []
        
        #Prepare test information
        formatted_test = format_test_info(test_info_content)
        simple_formatted_test = format_test_info_exclude_related(test_info_content)            


        count += 1
        path = os.path.join(log_dir, f"{p[i]}_{b[i]}")
        os.makedirs(path, exist_ok=True)
        
        j = 0
        scores = []
        results = []
        
        
        
        # First Step
        if (class_length>15):
        
            prompt1 = generate_prompt1(summary_content, covered_classes_for_prompt)
            step_1_results = []
            for _ in range(repeat):
                rv, response = llama_model.generate_response(prompt1)
                if rv == 1:
                    step_1_results.append(response)
                else:
                    step_1_results.append(f"Error: {response}")
            if verbose:
                print(response)
            
            
            summed_rank = sum_results_1(step_1_results, covered_classes,15)
            
            # Save the responses to a log file (example structure)
            log = {"responses": results, "scores": scores}
            file_name = os.path.join(path, f"log_{j}.json")
            with open(file_name, "w") as file:
                json.dump(log, file, indent=4)
            j += 1
            
        
        # Second Step
        if (class_length>3):
            prompt2 = generate_prompt1(summary_content, detailed_review)


            for _ in range(repeat):
                rv, response = llama_model.generate_response(prompt1)
                if rv == 1:
                    results.append(response)
                else:
                    results.append(f"Error: {response}")
                    
            
            # Save the responses to a log file (example structure)
            log = {"responses": results, "scores": scores}
            file_name = os.path.join(path, f"log_{j}.json")
            with open(file_name, "w") as file:
                json.dump(log, file, indent=4)
            j += 1






if __name__ == "__main__":
    mem_main(1)


