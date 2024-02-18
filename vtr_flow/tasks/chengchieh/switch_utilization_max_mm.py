import os
import re
import csv
from collections import defaultdict

def parse_switch(file_path, route_fname):
    # Append the desired subdirectories
    print("file_path:",file_path)
    print("route_fname:",route_fname)
    new_subdirectories = f"common/{route_fname}.route"
    new_path = os.path.join(file_path, new_subdirectories)
    print ("new_path:",new_path)

    result_list = {}
    if os.path.isfile(new_path):
        print("Route file found.")
        with open(new_path, 'r') as file:
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
                        #print ("count:", coord_counts[switch][nearest_coord[-2:]])
                        current_coord = nearest_coord
                        #print ("current_coord:",current_coord)

        for switch in [1, 2]:
            max_count_coord = max(coord_counts[switch], key=coord_counts[switch].get)
            if switch == 1:                  
                result_list['sw1_max_cord'] = max_count_coord
                result_list['sw1_max_num'] = coord_counts[switch][max_count_coord]
            else:
                result_list['sw2_max_cord'] = max_count_coord
                result_list['sw2_max_num'] = coord_counts[switch][max_count_coord]
    else:
        print("Route file not found.")            
    
    return result_list

def print_csv(result_list):
    # Append the coordinates with the largest counts for each switch to a CSV file   
    with open('final.csv', 'a', newline='') as csvfile:
        fieldnames = ["sw1_max_num", "sw1_max_cord","sw2_max_num", "sw2_max_cord"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(result_list)
        csvfile.close()

if __name__ == "__main__":
    result_list = parse_switch("/mnt/vault0/cliao43/vtr_cc/vtr-verilog-to-routing/vtr_flow/tasks/chengchieh/4bit_adder_double_chain_arch/spree/run003/4bit_adder_double_chain_arch.xml/spree.v","spree")
    print_csv(result_list)
    result_list = parse_switch("/mnt/vault0/cliao43/vtr_cc/vtr-verilog-to-routing/vtr_flow/tasks/chengchieh/4bit_adder_double_chain_arch/softmax/run003/4bit_adder_double_chain_arch.xml/softmax.v","softmax")
    print_csv(result_list)
