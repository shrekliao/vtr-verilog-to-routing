import os
import re
import argparse
import csv
import random

# ###############################################################
# Class for generating task list
# ###############################################################
class GenTaskList():
  #--------------------------
  #constructor
  #--------------------------
  def __init__(self):
    #members
    self.dirs = ''
    self.outfile = ''
    
    #method calls in order
    self.parse_args()
    self.generate_task_list()

  #--------------------------
  #parse command line args
  #--------------------------
  def parse_args(self):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d",
                        "--dirs",
                        action='store',
                        default="list_of_experiments.dec_2023",
                        help="File containing list of directories")
    parser.add_argument("-o",
                        "--outfile",
                        default="task_list.dec_2023",
                        action='store',
                        help="Name of the output task lsit file")
    parser.add_argument("-f",
                        "--folder",
                        default="chengchieh",
                        action='store',
                        help="Name of the folder under the tasks/ directory where the task dirs are located")
    parser.add_argument("-n",
                        "--only_print",
                        action='store_true',
                        help="Only print. Do not execute commands")
    args = parser.parse_args()
    print("Parsed arguments:", vars(args))
    self.dirs = args.dirs
    self.outfile = args.outfile
    self.folder = args.folder
    self.only_print = args.only_print

  #--------------------------
  #generate task list
  #--------------------------
  def generate_task_list(self):
    if not self.only_print:
      outfile = open(self.outfile, 'w') #outfile name

    print("Generating file: {}...".format(self.outfile))
    dirs = open(self.dirs, 'r')
    for line in dirs:
      line=line.strip()

      #if the line is commented out, ignore it
      check_for_comment = re.search(r'^#', line)
      if check_for_comment is not None:
        continue

      #info = re.search(r'(\w*)\.(\w*)\.(.*)', line)
      info = re.search(r'(\w*)\.(\w*)\.(\w*)', line)
      if info is not None:
        if self.folder is not None:
          dirname = self.folder + "/" + info.group(1) + "/" + info.group(3)
        else:
          dirname = info.group(1) + "/" + info.group(3)
      else:
        print("Unable to extract benchmark info from " + expname)
        raise SystemExit(0)

      if self.only_print:
        print(dirname)
      else:
        outfile.write(dirname+"\n")
    dirs.close()

    if not self.only_print:
      outfile.close()
    print("..Done")

# ###############################################################
# main()
# ###############################################################
if __name__ == "__main__":
  GenTaskList()

