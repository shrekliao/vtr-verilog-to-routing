import os

def get_file_names(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def update_config(file_names, config_file, add_line, format_string):
    with open(config_file, 'r') as file:
        lines = file.readlines()

    try:
        index = lines.index(add_line + '\n') + 1
    except ValueError:
        print(f"Error: The line '{add_line}' does not exist in the config file.")
        return False

    updated = False
    while index < len(lines) and lines[index].startswith(format_string.split('{}')[0]):
        if lines[index].strip().split('=')[1] not in file_names:
            lines.pop(index)
            updated = True
        else:
            index += 1

    for name in file_names:
        line = format_string.format(name)
        if line not in lines:
            lines.insert(index, line)
            index += 1
            updated = True

    with open(config_file, 'w') as file:
        file.writelines(lines)

    return updated

benchmarks = get_file_names('Benchmarks')
architectures = get_file_names('Architectures')

benchmarks_updated = update_config(benchmarks, 'config/config.txt', '# Add circuits to list to sweep', 'circuit_list_add={}\n')
architectures_updated = update_config(architectures, 'config/config.txt', '# Add architectures to list to sweep', 'arch_list_add={}\n')

if benchmarks_updated:
    print("The benchmarks in config file has been updated.")
if architectures_updated:
    print("The architectures in config file has been updated.")
