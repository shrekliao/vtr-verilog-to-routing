import argparse
from mako.template import Template
from textwrap import dedent
import os
import re
from itertools import product

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

    rendered = template.render(**values)
    output = header + rendered

    # Split the filename and extension
    result_basename, result_extension = os.path.splitext(result_fname)

    # Insert the index before the extension
    output_fname = f"{result_basename}_{i}{result_extension}"

    with open(output_fname, "w") as f:
        f.write(output)

def main():
    args = cmd_line_args()

    # Read values from a text file
    values = {}
    with open(args.para_inps, "r") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("#"):
                list_name = re.search(r'(\w+)\s*=\s*\{', line).group(1)
                list_values = [float(val) for val in re.findall(r'[\d\.]+', line)]
                values[list_name] = list_values

    # Generate all combinations of values
    combinations = list(product(*values.values()))

    # Call the function with each combination of values
    for i, combination in enumerate(combinations):
        values_combination = dict(zip(values.keys(), combination))
        render_template_file(args.infile, args.outfile, values_combination, i)

if __name__ == "__main__":
    main()
