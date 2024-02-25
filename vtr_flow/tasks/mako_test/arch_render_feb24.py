import argparse
from mako.template import Template
from textwrap import dedent
import os
import re
import ast
from itertools import product
import logging  # For better error reporting

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
                        default="modes.txt",
                        help="File name containing architecture modes")
    args = parser.parse_args()
    return args

index = [0]
def render_template_file(template_fname, result_fname, modes):
    template_basename = os.path.basename(template_fname)
    header_text = dedent("""\
        ////////////////////////////////////////////////////////////////////////////////
        // THIS FILE WAS AUTOMATICALLY GENERATED FROM ${filename}
        // DO NOT EDIT
        ////////////////////////////////////////////////////////////////////////////////

    """)
    header = Template(header_text).render(filename=template_basename)

    with open(template_fname, "r") as f:
        template = Template(f.read())

    result_dirname = os.path.dirname(result_fname)
    os.makedirs(result_dirname, exist_ok=True)

    rendered = template.render(**modes)
    output = header + rendered

    # Split the filename and extension
    result_basename, result_extension = os.path.splitext(result_fname)

    # Create a string with list name and mode pairs
    #modes_str = "_".join(f"{name}{int(mode) if mode.is_integer() else str(mode).replace('.', '-')}" for name, mode in modes.items())

    # Insert the index and modes string before the extension
    #output_fname = f"{result_basename}_{modes_str}{result_extension}"
    output_fname = f"{result_basename}_{index[0]}{result_extension}"

    index[0] += 1

    with open(output_fname, "w") as f:
        f.write(output)


def main():
    args = cmd_line_args()

    # Read modes from a text file
    modes = {}
    with open(args.para_inps, "r") as f:
        for line in f:
            line = line.strip()
            if "#" in line or not line:  # Skip commented lines
                continue
            try:
                mode_names, mode_values = line.split("=")
                mode_names = mode_names.strip().split(",")
                mode_values = ast.literal_eval(mode_values.strip())

                for mode_name in mode_names:
                    modes[mode_name] = mode_values
            except ValueError:
                logging.warning(f"Error: Malformed line in input file: {line}")


    # Call the render_template_file function for each combination of modes
    for mode_combination in modes.values():
        mode_dict = dict(zip(modes.keys(), mode_combination))
        render_template_file(args.infile, args.outfile, mode_dict)


if __name__ == "__main__":
    main()

