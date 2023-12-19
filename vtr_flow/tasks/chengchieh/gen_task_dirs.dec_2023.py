import os
import re
import argparse
import csv

# ###############################################################
# Class for generating task directories, each containing 
# a config.txt file
# ###############################################################
class GenTaskDirs():
  #--------------------------
  #constructor
  #--------------------------
  def __init__(self):
    #members
    self.dirs = ''
    self.template = ''
    
    #method calls in order
    self.parse_args()
    self.generate_dirs()

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
    parser.add_argument("-t",
                        "--template",
                        action='store',
                        default="template_config.dec_2023",
                        help="File containing the template config file")
    parser.add_argument("-o",
                        "--only_print",
                        action='store_true',
                        help="Only print. Do not execute commands")
    parser.add_argument("-s",
                        "--arch_suffix",
                        default=None,
                        action='store',
                        help="Add this suffix to arch file name")
    parser.add_argument("-v",
                        "--vtr_flow_dir",
                        default="../..",
                        action='store',
                        help="Path of vtr_flow directory")
    args = parser.parse_args()
    print("Parsed arguments:", vars(args))
    self.dirs = args.dirs
    self.template = args.template
    self.only_print = args.only_print
    self.arch_suffix = args.arch_suffix
    self.vtr_flow_dir = args.vtr_flow_dir

  #--------------------------
  #generate task directories
  #--------------------------
  def generate_dirs(self):
    dirs = open(self.dirs, 'r')
    #the dirs file contains dir names. each dir_name contains 
    #information about the experiment
    for line in dirs:
      expname = line.rstrip()
      #if the line is commented out, ignore it
      check_for_comment = re.search(r'^#', expname)
      if check_for_comment is not None:
        continue

      print("Processing: " + expname)
      #evaluate arch info from expname
      fourbit_adder_double_chain_arch = re.search(r'4bit_adder_double_chain_arch\.', expname)
      k6FracN10LB_mem20K_complexDSP_customSB_22nm = re.search(r'k6FracN10LB_mem20K_complexDSP_customSB_22nm\.', expname)
      #mantra = re.search(r'mantra\.', expname)
      #comefa = re.search(r'comefa\.', expname)
      if fourbit_adder_double_chain_arch is not None:
        if self.arch_suffix is not None:
          arch_file = "4bit_adder_double_chain_arch."  + self.arch_suffix + ".xml"
        else:
          arch_file = "4bit_adder_double_chain_arch.xml"
        arch_dir = "arch/COFFE_22nm"
      elif k6FracN10LB_mem20K_complexDSP_customSB_22nm is not None:
        arch_file = "k6FracN10LB_mem20K_complexDSP_customSB_22nm.xml"
        arch_dir = "arch/COFFE_22nm"
      #elif mantra is not None:
      #  arch_file = "k6FracN10LB_mem20K_complexDSP_customSB_22nm.mantra.fixed_layout.xml"
      #  arch_dir = "arch/COFFE_22nm/arch_for_paper_jun_2021"
      #elif comefa is not None:
      #  arch_file = "k6FracN10LB_mem20K_complexDSP_customSB_22nm.comefa.fixed_layout.xml"
      #  arch_dir = "arch/COFFE_22nm/arch_for_paper_jun_2021"
      else:
        print("Unable to extract arch info from " + expname)
        raise SystemExit(0)

      #check arch_file_path exists
      arch_file_path = self.vtr_flow_dir+"/"+arch_dir+"/"+ arch_file
      if not os.path.exists(arch_file_path):
        print("Arch file {} doesn't exist".format(arch_file_path))
        raise SystemExit(0)
      
      #evaluate design dir based on expname (ml or not)
      ml = re.search(r'\.ml\.', expname)
      non_ml = re.search(r'\.non_ml\.', expname)
      if ml is not None:
        design_dir="benchmarks/verilog/koios"
      elif non_ml is not None:
        design_dir="benchmarks/verilog"
      else:
        print("Unable to extract design dir from " + expname)
        raise SystemExit(0)

      #extract benchmark info from expname
      # The regular expression (\w*)\.(\w*)\.(.*) matches any word character (equal to [a-zA-Z0-9_]) followed by a period, then any word character again, another period, and finally any character.
      #info = re.search(r'(\w*)\.(\w*)\.(.*)', expname)
      info = re.search(r'(\w*)\.(\w*)\.(\w*)', expname)
      if info is not None:
        design_file = info.group(3)+".v"
        #sdc_file = os.path.abspath(info.group(3)+".sdc")
        #sdc_file = "../../../../../../../sdc/winograd.proposed.sdc"
      else:
        print("Unable to extract benchmark info from " + expname)
        raise SystemExit(0)

      #check design_file_path exists
      design_file_path = self.vtr_flow_dir + "/" + design_dir + "/" + design_file
      if not os.path.exists(design_file_path):
        print("Design file {} doesn't exist".format(design_file_path))
        raise SystemExit(0)

      #extract task dir info from expname
      info = re.search(r'(\w*)\.(\w*)\.(\w*)', expname)
      if info is not None:
        dirname = info.group(1) + "/" + info.group(3)
      else:
        print("Unable to extract dir info from " + expname)
        raise SystemExit(0)

      #create the config file by replacing tags in the template
      config_filename = dirname + "/config/config.txt"
      config_dirname  = dirname + "/config"
     
      print("config_filename: ", config_filename)
      print("config_dirname: ", config_dirname)
      print("design_dir: ", design_dir)
      print("arch_dir: ", arch_dir)
      print("design_file: ", design_file)
      print("arch_file: ", arch_file)
      print("")

      if not self.only_print:
        ret = os.system("mkdir -p " + config_dirname)
        if ret!=0:
          print("Directory " + config_dirname + " couldn't be created")

        try:
          config = open(config_filename, 'w')
        except:
          print("File " + config_filename + " couldn't be created")

        template = open(self.template, 'r')
        for line in template:
          line = line.strip()
          line = re.sub(r'<design_dir>',  design_dir,  line)
          line = re.sub(r'<arch_dir>',    arch_dir,    line)
          line = re.sub(r'<design_file>', design_file, line)
          line = re.sub(r'<arch_file>',   arch_file,   line)
          #line = re.sub(r'<sdc_full_path>', sdc_file, line)
          #if the design is fir filter, then we need to map 'inferred' multipliers to soft logic
          fir_filter = re.search(r'fir_filter', design_file)
          if fir_filter is not None:
            line = re.sub(r'<extra_args>', '-min_hard_mult_size 100', line)
          else:
            line = re.sub(r'<extra_args>', '', line)
          config.write(line)
          config.write("\n")
        config.close()

        #add to git
        os.system("git add " + config_filename)
        
        print("Done")
    dirs.close()


  
# ###############################################################
# main()
# ###############################################################
if __name__ == "__main__":
  GenTaskDirs()

