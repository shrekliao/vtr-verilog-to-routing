import argparse
from mako.template import Template
from textwrap import dedent
import os
import re
from itertools import product
import json
import pandas as pd
from pathlib import Path

def cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--infile",
                        action='store',
                        help="Name of input architecture template")
    parser.add_argument("-o",
                        "--outfile",
                        action='store',
                        help="Name of output architecture file")
    parser.add_argument("-p",
                        "--para_inps",
                        action='store',
                        default="values.txt",
                        help="File name containing architecture values")
    args = parser.parse_args()
    return args

def render_template_file(template_fname, result_fname, values, i):
    with open(template_fname, "r") as f:
        template = Template(f.read())

    result_dirname = os.path.dirname(result_fname)
    os.makedirs(result_dirname, exist_ok=True)

    rendered = template.render(**values)

    # Generate the output file name in numerical sequence
    output_fname = f"{result_fname}_{i}.xml"

    with open(output_fname, "w") as f:
        f.write(rendered)

    return output_fname

def write_json_file(filename, data):
    # Convert numeric values to integers if they are integers
    data = {k: {k2: int(v2) if v2.is_integer() else v2 for k2, v2 in v.items()} for k, v in data.items()}  
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def write_csv_file(filename, data):
  for fname, values in data.items():
    for key, value in values.items():
      if key in ['flut6']:  # Convert these directly to "on"/"off"
        values[key] = 'on' if value == 1 else 'off'
#      elif key in ['switch_block_type']:
#        values[key] = 'custom' if value == 1 else 'wilton'
#      elif key == 'n2lut5_with_n1lut6':
#        if 'flut6' in values and values['flut6'] == 'off':
#          values[key] = "don't care"
#          continue
#        elif value.is_integer():  # Only check for on/off if flut6 is 'on' 
#          values[key] = 'on' if value == 1 else 'off' 
      elif value.is_integer():
        values[key] = int(value)

  # Transpose the data so that parameter names become row headers and file names become column headers
  df = pd.DataFrame(data).T
  # Write the DataFrame to a CSV file
  df.to_csv(filename)


def main():
    args = cmd_line_args()

    # Read values from a text file
    values = {}
    with open(args.para_inps, "r") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("#"):
                match = re.search(r'(\w+)\s*=\s*\{(.*)\}', line)
                if match is not None:
                    list_name = match.group(1)
                    list_values_str = match.group(2).strip()
                    list_values = [float(val.replace(',', '')) for val in list_values_str.split()]
                    values[list_name] = list_values

    # Generate all combinations of values
    combinations = list(product(*values.values()))

    # Prepare a dictionary to store the details of each output file
    arch_dict = {}

    # Call the function with each combination of values
    for i, combination in enumerate(combinations):
        values_combination = dict(zip(values.keys(), combination))
        # Check if lut6 is selected, skip the consideration of n2lut5_with_n1lut6
        #if 'flut6' in values_combination and 'n2lut5_with_n1lut6' in values_combination:
        #    if values_combination['flut6'] == 0 and values_combination['n2lut5_with_n1lut6'] == 0:
        #        continue
        # Call the function with the index i as an additional argument
        output_fname = render_template_file(args.infile, args.outfile, values_combination, i)
        # Store the details of the output file in arch_dict
        arch_dict[output_fname] = values_combination

    # Get the directory of the outfile
    dir_name = Path(args.outfile).parent
    # Get the parent directory of dir_name
    parent_dir = dir_name.parent
    # Write arch_dict to a new file
    write_json_file(parent_dir / 'arch_dict.json', arch_dict)
    # Write arch_dict to a new CSV file
    write_csv_file(parent_dir / 'arch_dict.csv', arch_dict)

if __name__ == "__main__":
    main()
    print ("Success: Architecture files have been genetated!")
