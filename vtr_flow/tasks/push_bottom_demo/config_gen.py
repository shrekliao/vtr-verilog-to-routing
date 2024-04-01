import os

def modify_config():
    script_dir = os.path.dirname(__file__)  # Get the directory of the Python script

    benchmarks_path = os.path.join(script_dir, "Benchmarks") 
    config_path = os.path.join(script_dir, "config") 

    # Check if folders exist
    if not os.path.exists(benchmarks_path):
        print(f"Error: Benchmarks folder not found: {benchmarks_path}")
        return
    if not os.path.exists(config_path):
        print(f"Error: config folder not found: {config_path}")
        return

    # Collect files from Benchmarks
    benchmarks_files = [(filename, filename.split('.')[-1]) 
                        for filename in os.listdir(benchmarks_path)]

    # Collect architectures
    architectures_path = os.path.join(script_dir, "Architectures")
    architectures_files = [(filename, filename.split('.')[-1]) 
                           for filename in os.listdir(architectures_path)]

    # Open config.txt 
    config_file = os.path.join(config_path, "config.txt")
    try:
        with open(config_file, 'r+') as f:
            lines = f.readlines()
            insert_index = None
            existing_benchmarks = set()  # Track existing benchmarks
            existing_architectures = set()             

            for i, line in enumerate(lines):
                if line.strip() == "# Add circuits to list to sweep":
                    insert_index = i + 1
                elif line.strip().startswith("circuit_list_add="):
                    existing_benchmarks.add(line.split('=')[1].strip())  
                elif line.strip().startswith("arch_list_add="):
                    existing_architectures.add(line.split('=')[1].strip())                      

            if insert_index is not None:
                #Add benchmarks
                for filename, filetype in benchmarks_files:
                    if filename not in existing_benchmarks: 
                        new_line = f"circuit_list_add={filename}\n"
                        lines.insert(insert_index, new_line)
                        insert_index += 1

                # Add architectures
                for filename, filetype in architectures_files:
                    if filename not in existing_architectures:
                        lines.insert(insert_index, f"arch_list_add={filename}\n")
                        insert_index += 1                
                
                f.seek(0)  # Go back to the beginning of the file
                f.writelines(lines)
                print("config.txt updated successfully")
            else:
                print("Error: '# Add circuits to list to sweep' line not found in config.txt")

    except FileNotFoundError:
        print(f"Error: config.txt not found: {config_file}")

if __name__ == "__main__":
    modify_config()
