import os
import re
import sys
import csv
from collections import defaultdict

# Get the current directory where this Python script is located
current_directory = os.path.dirname(os.path.abspath(__file__))
#print ("current_directory:",current_directory)
# Find all files in the current directory
all_files = os.listdir(current_directory)
# Filter files that start with "log.log."
log_file = [filename for filename in all_files if filename.startswith("log.log.")]
log_file_string = ", ".join(log_file)
#print ("log_file:",log_file)
log_file_path = os.path.join(current_directory, log_file_string)
#need to find the one end with the largest number

def parse_switch(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    coord_counts = defaultdict(lambda: defaultdict(int))
    current_coord = (0, 0, 0)

    for i in range(len(lines)-1):
        line = lines[i]
        next_line = lines[i+1]

        # Parse coordinates and switch value from the current line
        coords = re.findall(r'\((-?\d+,-?\d+,-?\d+)\)', line)
        coords = [tuple(map(int, coord.split(','))) for coord in coords]
        switch_match = re.search(r'Switch: (\d+)', line)

        if switch_match is not None:
            switch = int(switch_match.group(1))

            if switch in [1, 2]:
                # Parse coordinates from the next line
                next_coords = re.findall(r'\((-?\d+,-?\d+,-?\d+)\)', next_line)
                next_coords = [tuple(map(int, coord.split(','))) for coord in next_coords]

                if next_coords:
                    # Find the nearest coordinate to the current one
                    nearest_coord = min(next_coords, key=lambda coord: sum(abs(a-b) for a, b in zip(coord[-2:], current_coord[-2:])))

                    # Update the count and current coordinate
                    coord_counts[switch][nearest_coord[-2:]] += 1
                    current_coord = nearest_coord
    
    # Get the last and fifth last parts of the file path
    file_path_parts = file_path.split(os.sep)
    short_file_path = os.sep.join(file_path_parts[-5:])

    # Append the coordinates with the largest counts for each switch to a CSV file   
    with open('switches_max.csv', 'a', newline='') as csvfile:
        fieldnames = ['File Path', 'Switch type', 'Coordinate location', 'Max Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for switch in [1, 2]:
            max_count_coord = max(coord_counts[switch], key=coord_counts[switch].get)
            writer.writerow({'File Path': short_file_path, 'Switch type': switch, 'Coordinate location': max_count_coord, 'Max Count': coord_counts[switch][max_count_coord]})

    # Print the coordinates with the largest counts for each switch
    # for switch in [1, 2]:
    #     max_count_coord = max(coord_counts[switch], key=coord_counts[switch].get)
    #     print(f'Switch: {switch}, Coordinate with largest count: {max_count_coord}, Count: {coord_counts[switch][max_count_coord]}')


# Initialize an empty list to store the new paths
new_paths = []
# Read each line from the log file
with open(log_file_path, "r") as log_file:
    for line in log_file:
        if line.startswith("task_run_dir="):
            # Extract the task_run_dir value
            task_run_dir = line.strip().split("=")[1]
            #print ("task_run_dir:",task_run_dir)
            # Extract the common part (up to /run002)
            #common_part = os.path.dirname(task_run_dir)
            common_part = os.path.join(task_run_dir, "")
            #print ("common_part:",common_part)
            # Get the second and third last folder names
            folders = common_part.split(os.path.sep)
            if len(folders) >= 3:
                arch_folder = folders[-4]  # Second last folder
                bench_folder = folders[-3]  # Third last folder
            else:
                print ("Sth wrong for finding route file")

            # Append the desired subdirectories
            new_subdirectories = f"{arch_folder}.xml/{bench_folder}.v/common/{bench_folder}.route"
            new_path = os.path.join(common_part, new_subdirectories)
            #print ("new_path:", new_path)
            parse_switch(new_path)

            # Add the new path to the list
            new_paths.append(new_path)   
