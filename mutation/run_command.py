import subprocess

def run_command(command_list,directory=None):
     try:
         # Run the command and capture the output
         result = subprocess.run(command_list, timeout=600, capture_output=True, text=True, shell=True,cwd = directory)
         
         # Return the command output
         return result.stdout
     except subprocess.CalledProcessError as e:
         # Handle errors (if command fails)
         print(f"Error occurred: {e}")
         print(f"Output: {e.output}")
         print(f"Error message: {e.stderr}")
         return "Error"
