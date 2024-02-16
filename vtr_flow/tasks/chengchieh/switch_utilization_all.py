import os
import re
import sys
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

def parse_script(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    coord_counts = defaultdict(int)
    current_coord = (0, 0, 0)

    for i in range(len(lines)-1):
        line = lines[i]
        next_line = lines[i+1]

        # Parse coordinates and switch value from the current line
        coords = re.findall(r'\((\d+,\d+,\d+)\)', line)
        coords += re.findall(r'\((\d+,\d+)\)', line)
        coords = [tuple(map(int, coord.split(','))) for coord in coords]
        switch_match = re.search(r'Switch: (\d+)', line)

        if switch_match is not None:
            switch = int(switch_match.group(1))

            if switch == 2:
                # Parse coordinates from the next line
                next_coords = re.findall(r'\((\d+,\d+,\d+)\)', next_line)
                next_coords += re.findall(r'\((\d+,\d+)\)', next_line)
                next_coords = [tuple(map(int, coord.split(','))) for coord in next_coords]

                # Convert 2D coordinates to 3D
                next_coords = [(0, *coord) if len(coord) == 2 else coord for coord in next_coords]

                if next_coords:
                    # Find the nearest coordinate to the current one
                    nearest_coord = min(next_coords, key=lambda coord: sum(abs(a-b) for a, b in zip(coord, current_coord)))

                    # Update the count and current coordinate
                    coord_counts[nearest_coord] += 1
                    current_coord = nearest_coord

    # Print the counts for each coordinate
    for coord, count in sorted(coord_counts.items()):
        print(f'{coord}: {count}')


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
            print ("new_path:", new_path)
            parse_script(new_path)

            # Add the new path to the list
            new_paths.append(new_path)
        
