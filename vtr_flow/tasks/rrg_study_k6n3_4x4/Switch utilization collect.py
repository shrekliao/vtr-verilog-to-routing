import re
import sys
from collections import defaultdict

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
    for coord, count in coord_counts.items():
        print(f'{coord}: {count}')

# Get the file path from the command line arguments
file_path = sys.argv[1]
parse_script(file_path)
