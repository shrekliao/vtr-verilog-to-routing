import os
import re
import argparse
import csv

one_clk_sdc = '''
create_clock -period 0 *
'''

two_clk_sdc = '''
create_clock -period 0 *
set_clock_groups -exclusive -group {<clk1>} -group {<clk2>}
'''

three_clk_sdc = '''
create_clock -period 0 *
set_clock_groups -exclusive -group {<clk1>} -group {<clk2>}
set_clock_groups -exclusive -group {<clk1>} -group {<clk3>}
set_clock_groups -exclusive -group {<clk3>} -group {<clk2>}
'''

four_clk_sdc = '''
create_clock -period 0 *
set_clock_groups -exclusive -group {<clk1>} -group {<clk2>}
set_clock_groups -exclusive -group {<clk1>} -group {<clk3>}
set_clock_groups -exclusive -group {<clk1>} -group {<clk4>}
set_clock_groups -exclusive -group {<clk2>} -group {<clk1>}
set_clock_groups -exclusive -group {<clk2>} -group {<clk3>}
set_clock_groups -exclusive -group {<clk2>} -group {<clk4>}
set_clock_groups -exclusive -group {<clk3>} -group {<clk1>}
set_clock_groups -exclusive -group {<clk3>} -group {<clk2>}
set_clock_groups -exclusive -group {<clk3>} -group {<clk4>}
set_clock_groups -exclusive -group {<clk4>} -group {<clk1>}
set_clock_groups -exclusive -group {<clk4>} -group {<clk2>}
set_clock_groups -exclusive -group {<clk4>} -group {<clk3>}
'''

clk_names_dict = {
#'matmul_8x8_fp16' : ['clk', 'clk_mem'],
#'matmul_20x20_fp16' : ['clk', 'clk_mem'],
#'tpu.16x16.int8' : ['clk', 'clk_mem'],
#'tpu.32x32.int8' : ['clk', 'clk_mem'],
#'conv_layer' : ['clk', 'clk_mem'],
#'gemm_8x8_int8' : ['s00_axi_aclk'],
#'reduction_layer' : ['clk'],
#'eltwise_layer' : ['clk', 'clk_mem'],
#'conv_layer_hls' : ['ap_clk'],
#'robot_rl' : ['clk'],
#'softmax' : ['clk'],
#'maf.baseline.128taps' : ['clk'],
#'maf.baseline.256taps' : ['clk'],
#'maf.proposed.128.gen' : ['clk'],
'fir_filter.proposed.comefa' : ['clk'],
'fir_filter.proposed.mantra' : ['clk'],
'fir_filter.baseline' : ['clk'],
'winograd.baseline' : ['clk'],
'winograd.proposed.ccb' : ['clk'],
'winograd.proposed.comefa' : ['clk'],
'winograd.proposed.mantra' : ['clk'],
'raid_array_baseline' : ['clk'],
'raid_array_proposed.ccb' : ['clk'],
'raid_array_proposed.comefa' : ['clk'],
'raid_array_proposed.mantra' : ['clk'],
'equisearch_baseline' : ['clk'],
'equisearch_proposed.mantra' : ['clk'],
'equisearch_proposed.comefa' : ['clk'],
'equisearch_proposed.ccb' : ['clk'],
'mvm.baseline' : ['clk'],
'accumulation_kernel.baseline' : ['clk'],
'accumulation_kernel.proposed.mantra' : ['clk'],
'accumulation_kernel.proposed.comefa' : ['clk'],
'accumulation_kernel.proposed.ccb' : ['clk'],
#'mvm.15_instr_gen_logic.dp' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.5_instr_gen_logic.dp' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.1_instr_gen_logic.dp' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.15_instr_gen_logic.dp.ccb' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.5_instr_gen_logic.dp.ccb' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.1_instr_gen_logic.dp.ccb' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.15_instr_gen_logic' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.5_instr_gen_logic' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.1_instr_gen_logic' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.15_instr_gen_logic.ccb' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.5_instr_gen_logic.ccb' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'mvm.1_instr_gen_logic.ccb' : ['clk','clk_mem','clk_instr','clk_load_unload'],
#'softmax' : ['clk'],
#'softmax_p8_fp16' : ['clk'],
#'mlp_leflow' : ['clk', 'clk2x'],
#'spmv' : ['clk'],
#'clstm_large' : ['clk'],
#'clstm_medium' : ['clk'],
#'clstm_small' : ['clk'],
#'lstm' : ['clk'],
#'bnn_hls': ['ap_clk'],
#'tiny_darknet_hls': ['ap_clk'],
#'attention' : ['clk'],
#'dla_small' : ['clk'],
#'dla_medium' : ['clk'],
#'tpu_v2' : ['clk', 'mem_clk'],
#'LU32PEEng' : ['clk'],
#'LU64PEEng' : ['clk'],
#'LU8PEEng' : ['clk'],
#'arm_core' : ['i_clk'],
#'bgm' : ['clock'],
#'blob_merge' : ['clk'],
#'boundtop' : ['tm3_clk_v0'],
#'ch_intrinsics' : ['clk'],
#'diffeq1' : ['clk'],
#'diffeq2' : ['clk'],
#'mcml' : ['clk'],
#'mkDelayWorker32B' : ['wciS0_Clk'],
#'mkPktMerge' : ['CLK'],
#'mkSMAdapter4B' : ['wciS0_Clk'],
#'or1200' : ['clk'],
#'raygentop' : ['tm3_clk_v0'],
#'sha' : ['clk_i'],
#'spree' : ['clk'],
#'stereovision0' : ['tm3_clk_v0'],
#'stereovision1' : ['tm3_clk_v0'],
#'stereovision2' : ['tm3_clk_v0'],
#'stereovision3' : ['tm3_clk_v0'],
}

# ###############################################################
# Class for generating sdc files
# ###############################################################
class GenSDCFiles():
  #--------------------------
  #constructor
  #--------------------------
  def __init__(self):
    #members
    self.dirs = ''
    self.template = ''
    
    #method calls in order
    self.parse_args()
    self.generate_sdcs()

  #--------------------------
  #parse command line args
  #--------------------------
  def parse_args(self):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d",
                        "--dirs",
                        action='store',
                        default="list_of_experiments.july_2021",
                        help="File containing list of directories")
    parser.add_argument("-o",
                        "--only_print",
                        action='store_true',
                        help="Only print. Do not execute commands")
    args = parser.parse_args()
    print("Parsed arguments:", vars(args))
    self.dirs = args.dirs
    self.only_print = args.only_print

  #--------------------------
  #generate sdc files 
  #--------------------------
  def generate_sdcs(self):

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

      #extract design info from expname
      info = re.search(r'(\w*)\.(\w*)\.(.*)', expname)
      if info is not None:
        design = info.group(3)
      else:
        print("Unable to extract info from " + expname)
        raise SystemExit(0)

      if design not in clk_names_dict:
        print("Design {} mentioned in the list of experiments doesn't have it's clocks mentioned in the dict".format(design))
        raise SystemExit(0)
      else:
        clk_list = clk_names_dict[design]

      sdc_filename = "../sdc/"+design+".sdc"
     
      print("sdc_filename: ", sdc_filename)

      if not self.only_print:
        try:
          sdc = open(sdc_filename, 'w')
        except:
          print("File " + sdc_filename + " couldn't be created")

        if len(clk_list) == 1:
          sdc.write(one_clk_sdc)
        elif len(clk_list) == 2:
          temp = two_clk_sdc.replace('<clk1>', clk_list[0])\
                            .replace('<clk2>', clk_list[1])
          sdc.write(temp)
        elif len(clk_list) == 3:
          temp = three_clk_sdc.replace('<clk1>', clk_list[0])\
                              .replace('<clk2>', clk_list[1])\
                              .replace('<clk3>', clk_list[2])
          sdc.write(temp)
        elif len(clk_list) == 4:
          temp = four_clk_sdc.replace('<clk1>', clk_list[0])\
                             .replace('<clk2>', clk_list[1])\
                             .replace('<clk3>', clk_list[2])\
                             .replace('<clk4>', clk_list[3])
          sdc.write(temp)
        else:
          print("Do not support SDCs with more than 2 clocks yet")
          raise SystemExit(0)

        sdc.close()

        #add to git
        os.system("git add " + sdc_filename)
        
        print("Done")

  
# ###############################################################
# main()
# ###############################################################
if __name__ == "__main__":
  GenSDCFiles()


