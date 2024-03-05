import argparse
from mako.template import Template
from textwrap import dedent
import os
import re

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

def render_template_file(template_fname, result_fname, fs_values, list_name):
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

    for i, fs in enumerate(fs_values):
        rendered = template.render(fs=fs)
        output = header + rendered

        # Split the filename and extension
        result_basename, result_extension = os.path.splitext(result_fname)

        # Insert the index before the extension
        output_fname = f"{result_basename}_{list_name}{i+1}{result_extension}"

        with open(output_fname, "w") as f:
            f.write(output)

def main():
    args = cmd_line_args()

    # Read fs values from a text file
    fs_values = []
    list_name = None
    with open(args.num_inps, "r") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("#"):
                if list_name is None:
                    list_name = re.search(r'(\w+)\s*=\s*\{', line).group(1)
                fs_values.extend(re.findall(r'\d+', line))
    fs_values = [int(fs) for fs in fs_values]

    # Call the function with the fs values
    render_template_file(args.infile, args.outfile, fs_values, list_name)


if __name__ == "__main__":
    main()
