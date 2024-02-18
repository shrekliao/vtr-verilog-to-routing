import os
import re
import argparse
import csv
import subprocess
from collections import defaultdict


# ###############################################################
# Class for parsing VTR results for various experiments
# ###############################################################
class GenResults():
  #--------------------------
  #constructor
  #--------------------------
  def __init__(self):
    #members
    self.infile = ""
    self.outfile = ""
    self.result_list = []
    self.metrics = ["design", \
                    "dirname", \
                    "run_num", \
                    "type", \
                    "arch", \
                    "date", \
                    "tag" , \
                    "order", \
                    "vpr_results_found", \
                    "pre_vpr_blif_found", \
                    "parse_results_found", \
                    "power_results_found", \
                    "critical_path", \
                    "frequency", \
                    "frequency_clk", \
                    "frequency_clk_mem", \
                    "frequency_clk_instr", \
                    "frequency_clk_load_unload", \
                    "logic_area", \
                    "routing_area", \
                    "total_area", \
                    "channel_width", \
                    "num_global_nets", \
                    "num_routed_nets", \
                    "total_nets_routed", \
                    "total_connections_routed", \
                    #"total_heap_pushes", \
                    #"total_heap_pops", \
                    "average_net_length", \
                    "max_net_length", \
                    "max_fanout", \
                    "max_non_global_fanout", \
                    "average_wire_segments_per_net", \
                    "max_segments_used_by_a_net", \
                    "total_routed_wire_length", \
                    "non_io_wire_length", \
                    "resource_usage_io", \
                    "resource_usage_clb", \
                    "resource_usage_dsp", \
                    "resource_usage_memory", \
                    "dual_port_ram_before_vpr", \
                    "single_port_ram_before_vpr", \
                    "resource_usage_memory_storage", \
                    "resource_usage_memory_compute", \
                    "total_num_fle", \
                    "fle_for_logic_and_reg", \
                    "fle_for_only_logic", \
                    "fle_for_only_reg", \
                    "utilization_io", \
                    "block_input", \
                    "block_output", \
                    "utilization_clb", \
                    "utilization_dsp", \
                    "utilization_memory", \
                    "utilization_device", \
                    "two_mult_18x19", \
                    "mult_9x9_fixed_pt", \
                    "mult_add", \
                    "one_mult_27x27", \
                    "device_io", \
                    "device_clb", \
                    "device_dsp", \
                    "device_memory", \
                    "single_bit_adders", \
                    "luts", \
                    #"0_lut", \
                    #"6_lut", \
                    "lut3", \
                    "lut4", \
                    "lut5", \
                    "lut6", \
                    "ffs", \
                    "mem_512x40_sp", \
                    "mem_2048x10_dp", \
                    "mem_1024x20_dp", \
                    "memory_slice", \
                    "ff_to_lut_ratio", \
                    "dsp_to_clb_ratio", \
                    "memory_to_clb_ratio", \
                    "adder_to_lut_ratio", \
                    "dsp_to_lut_ratio", \
                    "memory_to_lut_ratio", \
                    "netlist_primitives", \
                    "netlist_primitives>10k", \
                    "vtr_flow_elapsed_time", \
                    "odin_time", \
                    "abc_time", \
                    "pack_time", \
                    "place_time", \
                    "route_time", \
                    "vtr_flow_peak_memory_usage", \
                    "near_crit_connections", \
                    "logic_depth", \
                    "device_height", \
                    "device_width" , \
                    "grid_size_limiter", \
                    "max_routing_channel_util", \
                    "min_util_for_largest_pct_of_total_channels", \
                    "max_util_for_largest_pct_of_total_channels", \
                    "largest_pct_of_total_channels", \
                    "routing_histogram_1_inf_val",  \
                    "routing_histogram_09_1_val",  \
                    "routing_histogram_08_09_val",  \
                    "routing_histogram_07_08_val",  \
                    "routing_histogram_06_07_val",  \
                    "routing_histogram_05_06_val",  \
                    "routing_histogram_04_05_val",  \
                    "routing_histogram_03_04_val",  \
                    "routing_histogram_02_03_val",  \
                    "routing_histogram_01_02_val",  \
                    "routing_histogram_00_01_val",  \
                    "routing_histogram_1_inf_pct",  \
                    "routing_histogram_09_1_pct",  \
                    "routing_histogram_08_09_pct",  \
                    "routing_histogram_07_08_pct",  \
                    "routing_histogram_06_07_pct",  \
                    "routing_histogram_05_06_pct",  \
                    "routing_histogram_04_05_pct",  \
                    "routing_histogram_03_04_pct",  \
                    "routing_histogram_02_03_pct",  \
                    "routing_histogram_01_02_pct",  \
                    "routing_histogram_00_01_pct", \
                    "sw1_max_num", "sw1_max_cord","sw2_max_num", "sw2_max_cord"]

    self.components_of_interest = ["routing", "clock", "clb", "dsp", "memory"]
    self.power_types = ["abs_total_power", \
                        "abs_dynamic_power", \
                        "abs_static_power", \
                        "pct_total_power", \
                        "pct_dynamic_power", \
                        "pct_static_power"]

    for power in self.power_types:
      for component in self.components_of_interest:
        self.metrics.append(component+"_"+power)
      for component in ["compute_ram", "storage_ram"]:
        self.metrics.append(component+"_"+power)
      
    self.metrics += [\
      "absolute_dynamic_power_of_circuit", \
      "absolute_static_power_of_circuit", \
      "absolute_total_power_of_circuit"
    ]

    #method calls in order
    self.parse_args()
    self.extract_info()
    self.print_csv()

  #--------------------------
  #parse command line args
  #--------------------------
  def parse_args(self):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--infile",
                        action='store',
                        default="dec_2023.log",
                        help="File containing the STDOUT of VTR runs")
    parser.add_argument("-o",
                        "--outfile",
                        action='store',
                        default="out.dec_2023.csv",
                        help="Name of output file")
    parser.add_argument("-t",
                        "--tag",
                        action='store',
                        default="",
                        help="Tag for these results")
    args = parser.parse_args()
    print("infile = "+ args.infile)
    print("outfile = "+args.outfile)
    self.infile = args.infile
    self.outfile = args.outfile
    self.tag = args.tag

  #--------------------------
  #print the csv file 
  #--------------------------
  def print_csv(self):
    print("Printing csv: " + self.outfile)
    outfile = open(self.outfile, 'w+')
    writer = csv.DictWriter(outfile, fieldnames=self.metrics)
    writer.writeheader()
    for data in self.result_list:
      writer.writerow(data)
    outfile.close()

  #--------------------------
  #find a file
  #--------------------------
  def find_file(self, dirname, run_num, file_to_find):
    found = False
    for root, dirs, files in os.walk(os.path.realpath(dirname + "/" + run_num), topdown=True):
      #print(root, dirs, files)
      for filename in files:
        #print("filename:", filename)
        match = re.match(file_to_find, filename)
        if match is not None:
          found = True
          found_filename = os.path.join(root,filename)
          #print("Found {} for {}: {}".format(file_to_find, dirname, found_filename))
          return found_filename
    if not found:
      print("Could not find {} for {}".format(file_to_find, dirname))
      return None

  #--------------------------
  #get routing area of various blocks
  #--------------------------
  def get_routing_area(self, arch, block):
    #if arch == "stratix":
    #  routing_area_clb = 30481 #in MWTAs
    #  routing_area_dsp = 4 * routing_area_clb #DSP is 4 rows high
    #  routing_area_memory = 6 * routing_area_clb #Memory is 6 rows high
    #elif arch == "agilex":
    #area values from coffe, changed from um2 to mwtas
    #area is SB + CB in the tile
    routing_area_clb = (684+305) / 0.033864 #converting um2 into MWTAs
    routing_area_dsp = 4 * routing_area_clb #DSP is 4 rows high
    routing_area_memory = 2 * routing_area_clb #Memory is 2 rows high
    #else:
    #  print("Unsupported architecture: {}".format(arch))  
    #  raise SystemExit(0)

    if block == "clb":
      return routing_area_clb
    elif block == "dsp":
      return routing_area_dsp
    elif block == "memory":
      return routing_area_memory
    else:
      print("Unsupported block: {}".format(block))
      raise SystemExit(0)

  #--------------------------
  #extract information for each entry in infile
  #--------------------------
  def extract_info(self):
    infile = open(self.infile, 'r')
    #the infile contains dir names. each dir_name/latest contains a vpr.out file
    for line in infile:
      #if the line is commented out, ignore it
      check_for_comment = re.search(r'^#', line)
      if check_for_comment is not None:
        continue
      check_for_task_dir = re.search(r'^task_run_dir=', line)
      if check_for_task_dir is None:
        continue
      m = re.search('task_run_dir=(.*)/(run.*)', line.rstrip())
      if m is not None:
        dirname = m.group(1)
        run_num = m.group(2)
      else:
        print("Unable to parse line: " + line)
        continue
      result_dict = {}
      result_dict['dirname'] = dirname #/mnt/vault0/cliao43/vtr_cc/vtr-verilog-to-routing/vtr_flow/tasks/chengchieh/k6FracN10LB_mem20K_complexDSP_customSB_22nm/spree/
      result_dict['run_num'] = run_num #run001

      #extract experiment info from dirname
      # List all arch_names under dirname
      arch_names = [d for d in os.listdir(os.path.join(dirname, run_num)) if os.path.isdir(os.path.join(dirname, run_num, d))]
      # If there's only one arch_name, convert it to a string
      if len(arch_names) == 1:
          arch_name = arch_names[0]
          #print ("arch_name:", arch_name)
          design_path = os.path.join(dirname, run_num, arch_name)
          #print ("design_path:", design_path)
          # Check if the arch_name name matches the pattern
          design_name = [d for d in os.listdir(design_path) if os.path.isdir(os.path.join(design_path, d))]
          pattern = r'([^/]*)\.v$'
          v_folder = next((d for d in design_name if re.search(pattern, d)), None)
          if v_folder:
              # If a .v directory is found, extract the directory name
              folder_name = re.search(pattern, v_folder).group(1)
              result_dict['arch'] = arch_name
              result_dict['design'] = folder_name
              new_full_path = str(design_path + "/" + folder_name+ ".v")
              #print("Extracting info for " + new_full_path)              
              #print("Found design folder: " + folder_name)
          else:
              print("No .v folder found.")
      else:
          print("More than one arch_name found. Please check the arch_name list.")

      #--------------------------
      #extract information from vpr.out
      #--------------------------
      #try to find vpr.out
      vpr_out_filename = self.find_file(dirname, run_num, "vpr.out")
      if vpr_out_filename is None:
        result_dict['vpr_results_found'] = "No" 
      else:      
        result_dict['vpr_results_found'] = "Yes" 

        #Start parsing vtr.out
        vpr_out = open(vpr_out_filename, 'r')

        resource_usage_ff = 0
        resource_usage_adder = 0
        #resource_usage_memory = 0
        resource_usage_memory_compute = 0
        resource_usage_lut = 0
        num_memory_slice = 0
        pb_types_usage = False
        routing_channel_util_section = False
        largest_pct_of_total_channels = 0.0
        crit_path_section = False

        result_dict['single_bit_adders'] = 0
        result_dict['logic_area'] = 0

        for line in vpr_out:
          #pb types usage section starts with this text
          pb_types_usage_match = re.search('Pb types usage', line)
          if pb_types_usage_match is not None:
            pb_types_usage = True

          #pb types usage section ends with this text
          create_device_usage_match = re.search('# Create Device', line)
          if create_device_usage_match is not None:
            pb_types_usage = False

          #routing channel utilization section starts with this text
          routing_channel_util_match = re.search(r'Routing channel utilization histogram:', line)
          if routing_channel_util_match is not None:
            routing_channel_util_section = True

          #routing channel utilization section ends with this text
          max_routing_channel_util_match = re.search(r'Maximum routing channel utilization:', line)
          if max_routing_channel_util_match is not None:
            routing_channel_util_section = False

          #critical path section starts with this text
          intra_crit_path_match = re.search(r'Final intra-domain critical path delays', line)
          if intra_crit_path_match is not None:
            crit_path_section = True

          #critical path section ends with this text
          inter_crit_path_match = re.search(r'Final inter-domain critical path delays', line)
          if inter_crit_path_match is not None:
            crit_path_section = False

          #print(line)
          logic_area_match = re.search(r'Total used logic block area: (.*)', line)
          if logic_area_match is not None:
            logic_area = logic_area_match.group(1)
            result_dict['logic_area'] = logic_area or "Not found"

          #routing_area_match = re.search(r'Total routing area: (.*), per logic tile', line)
          #if routing_area_match is not None:
          #  routing_area = routing_area_match.group(1)
          #  result_dict['routing_area'] = routing_area or "Not found"

          crit_path_match3 = re.search(r'Final critical path: (.*) ns', line)
          crit_path_match4 = re.search(r'Final critical path delay \(least slack\): (.*) ns', line)
          if crit_path_match3 is not None or crit_path_match4 is not None:
            if crit_path_match3 is not None:
              crit_path_match = crit_path_match3
            if crit_path_match4 is not None:
              crit_path_match = crit_path_match4
            critical_path = crit_path_match.group(1)
            result_dict['critical_path'] = float(critical_path) or 0
            result_dict['frequency'] = 1/result_dict['critical_path']*1000

          crit_path_match_clk = re.search(r'top\^clk to top\^clk CPD: .*\((.*) MHz\)', line)
          if crit_path_match_clk is not None and crit_path_section is True:
            freq_clk = crit_path_match_clk.group(1)
            result_dict['frequency_clk'] = float(freq_clk) or 0

          crit_path_match_clk_mem = re.search(r'top\^clk_mem to top\^clk_mem CPD: .*\((.*) MHz\)', line)
          if crit_path_match_clk_mem is not None and crit_path_section is True:
            freq_clk_mem = crit_path_match_clk_mem.group(1)
            result_dict['frequency_clk_mem'] = float(freq_clk_mem) or 0

          crit_path_match_clk_instr = re.search(r'top\^clk_instr to top\^clk_instr CPD: .*\((.*) MHz\)', line)
          if crit_path_match_clk_instr is not None and crit_path_section is True:
            freq_clk_instr = crit_path_match_clk_instr.group(1)
            result_dict['frequency_clk_instr'] = float(freq_clk_instr) or 0

          crit_path_match_clk_load_unload = re.search(r'top\^clk_load_unload to top\^clk_load_unload CPD: .*\((.*) MHz\)', line)
          if crit_path_match_clk_load_unload is not None and crit_path_section is True:
            freq_clk_load_unload = crit_path_match_clk_load_unload.group(1)
            result_dict['frequency_clk_load_unload'] = float(freq_clk_load_unload) or 0

          channel_width_match = re.search(r'Circuit successfully routed with a channel width factor of (.*)\.', line)
          if channel_width_match is not None:
            channel_width = channel_width_match.group(1)
            result_dict['channel_width'] = channel_width or "Not found"

          num_global_nets_match = re.search(r'Number of global nets: (.*)', line)
          if num_global_nets_match is not None:
            num_global_nets = num_global_nets_match.group(1)
            result_dict['num_global_nets'] = int(num_global_nets) or "Not found"

          num_routed_nets_match = re.search(r'Number of routed nets \(nonglobal\): (.*)', line)
          if num_routed_nets_match is not None:
            num_routed_nets = num_routed_nets_match.group(1)
            result_dict['num_routed_nets'] = int(num_routed_nets) or "Not found"

          total_routed_match = re.search(r'Router Stats: total_nets_routed: (.*) total_connections_routed: (.*) total_heap_pushes: (.*) total_heap_pops: (.*)', line)
          if total_routed_match is not None:
            total_nets_routed = total_routed_match.group(1)
            total_connections_routed = total_routed_match.group(2)
            #total_heap_pushes = total_routed_match.group(3)
            #total_heap_pops = total_routed_match.group(4)
            result_dict['total_nets_routed'] = float(total_nets_routed) or "Not found"

          #total_connections_routed_match = re.search(r'total_connections_routed: (.*)', line)
          #if total_connections_routed_match is not None:
          #  total_connections_routed = total_connections_routed_match.group(1)
            result_dict['total_connections_routed'] = float(total_connections_routed) or "Not found"
#
          #total_heap_pushes_match = re.search(r'total_heap_pushes: (.*)', line)
          #if total_heap_pushes_match is not None:
          #  total_heap_pushes = total_heap_pushes_match.group(1)
          #  result_dict['total_heap_pushes'] = float(total_heap_pushes) or "Not found"
#
          #total_heap_pops_match = re.search(r'total_heap_pops: (.*)', line)
          #if total_heap_pops_match is not None:
          #  total_heap_pops= total_heap_pops_match.group(1)
          #  result_dict['total_heap_pops'] = float(total_heap_pops) or "Not found"

          average_net_length_match = re.search(r'average net length: (.*)', line)
          if average_net_length_match is not None:
            average_net_length = average_net_length_match.group(1)
            result_dict['average_net_length'] = float(average_net_length) or "Not found"

          max_net_length_match = re.search(r'Maximum net length: (.*)', line)
          if max_net_length_match is not None:
            max_net_length = max_net_length_match.group(1)
            result_dict['max_net_length'] = max_net_length or "Not found"

          average_wire_segments_per_net_match = re.search(r'average wire segments per net: (.*)', line)
          if average_wire_segments_per_net_match is not None:
            average_wire_segments_per_net = average_wire_segments_per_net_match.group(1)
            result_dict['average_wire_segments_per_net'] = average_wire_segments_per_net or "Not found"

          max_segments_used_by_a_net_match = re.search(r'Maximum segments used by a net: (.*)', line)
          if max_segments_used_by_a_net_match is not None:
            max_segments_used_by_a_net = max_segments_used_by_a_net_match.group(1)
            result_dict['max_segments_used_by_a_net'] = max_segments_used_by_a_net or "Not found"

          total_routed_wire_length_match = re.search(r'Total wirelength: (.*), average net length:', line)
          if total_routed_wire_length_match is not None:
            total_routed_wire_length = total_routed_wire_length_match.group(1)
            result_dict['total_routed_wire_length'] = total_routed_wire_length or "Not found"

          total_num_fle_match = re.search(r'Total number of Logic Elements used : (.*)', line)
          if total_num_fle_match is not None:
            total_num_fle = total_num_fle_match.group(1)
            result_dict['total_num_fle'] = float(total_num_fle) or 0

          fle_for_logic_and_reg_match = re.search(r'LEs used for logic and registers    : (.*)', line)
          if fle_for_logic_and_reg_match is not None:
            fle_for_logic_and_reg= fle_for_logic_and_reg_match.group(1)
            result_dict['fle_for_logic_and_reg'] = float(fle_for_logic_and_reg) or 0

          fle_for_only_logic_match = re.search(r'LEs used for logic only             : (.*)', line)
          if fle_for_only_logic_match is not None:
            fle_for_only_logic = fle_for_only_logic_match.group(1)
            result_dict['fle_for_only_logic'] = float(fle_for_only_logic) or 0
          
          fle_for_only_reg_match = re.search(r'LEs used for registers only         : (.*)', line)
          if fle_for_only_reg_match is not None:
            fle_for_only_reg = fle_for_only_reg_match.group(1)
            result_dict['fle_for_only_reg'] = float(fle_for_only_reg) or 0
                    
          utilization_io_match = re.search(r'Block Utilization: (\d+\.\d+) Type: io', line)
          if utilization_io_match is not None:
            utilization_io = utilization_io_match.group(1)
            result_dict['utilization_io'] = float(utilization_io) or 0

          utilization_clb_match = re.search(r'Block Utilization: (\d+\.\d+) Type: clb', line)
          if utilization_clb_match is not None:
            utilization_clb = utilization_clb_match.group(1)
            result_dict['utilization_clb'] = float(utilization_clb) or 0

          utilization_dsp_match = re.search(r'Block Utilization: (\d+\.\d+) Type: (dsp_top|mult_27)', line)
          if utilization_dsp_match is not None:
            utilization_dsp = utilization_dsp_match.group(1)
            result_dict['utilization_dsp'] = float(utilization_dsp) or 0

          two_mult_18x19_match = re.search(r'two_mult_18x19\s*:\s*(\d+)', line)
          if two_mult_18x19_match is not None:
            two_mult_18x19 = two_mult_18x19_match.group(1)
            result_dict['two_mult_18x19'] = float(two_mult_18x19) or 0

          mult_9x9_fixed_pt_match = re.search(r'mult_9x9_fixed_pt\s*:\s*(\d+)', line)
          if mult_9x9_fixed_pt_match is not None:
            mult_9x9_fixed_pt = mult_9x9_fixed_pt_match.group(1)
            result_dict['mult_9x9_fixed_pt'] = float(mult_9x9_fixed_pt) or 0

          mult_add_match = re.search(r'mult_add\s*:\s*(\d+)', line)
          if mult_add_match is not None:
            mult_add = mult_add_match.group(1)
            result_dict['mult_add'] = float(mult_add) or 0

          one_mult_27x27_match = re.search(r'one_mult_27x27\s*:\s*(\d+)', line)
          if one_mult_27x27_match is not None:
            one_mult_27x27 = one_mult_27x27_match.group(1)
            result_dict['one_mult_27x27'] = float(one_mult_27x27) or 0            

          mem_512x40_sp_match = re.search(r'mem_512x40_sp\s*:\s*(\d+)', line)
          if mem_512x40_sp_match is not None:
            mem_512x40_sp = mem_512x40_sp_match.group(1)
            result_dict['mem_512x40_sp'] = float(mem_512x40_sp) or 0

          mem_1024x20_dp_match = re.search(r'mem_1024x20_dp\s*:\s*(\d+)', line)
          if mem_1024x20_dp_match is not None:
            mem_1024x20_dp = mem_1024x20_dp_match.group(1)
            result_dict['mem_1024x20_dp'] = float(mem_1024x20_dp) or 0

          mem_2048x10_dp_match = re.search(r'mem_2048x10_dp\s*:\s*(\d+)', line)
          if mem_2048x10_dp_match is not None:
            mem_2048x10_dp = mem_2048x10_dp_match.group(1)
            result_dict['mem_2048x10_dp'] = float(mem_2048x10_dp) or 0   
            
          utilization_memory_match = re.search(r'Block Utilization: (\d+\.\d+) Type: memory', line)
          if utilization_memory_match is not None:
            utilization_memory = utilization_memory_match.group(1)
            result_dict['utilization_memory'] = float(utilization_memory) or 0

          utilization_device_match = re.search(r'Device Utilization: (\d+\.\d+)', line)
          if utilization_device_match is not None:
            utilization_device = utilization_device_match.group(1)
            result_dict['utilization_device'] = float(utilization_device) or 0

          resource_usage_io_match = re.search(r'(\d+)\s+blocks of type: io', line)
          if resource_usage_io_match is not None and ("Netlist" in prev_line):
            resource_usage_io = resource_usage_io_match.group(1)
            result_dict['resource_usage_io'] = int(resource_usage_io) or 0

          #zero_lut_match = re.search(r'(0-LUT)\s*:\s*(\d+)', line)
          #if zero_lut_match is not None:
          #  zero_lut = zero_lut_match.group(2)
          #  result_dict['0_lut'] = int(zero_lut) or 0
#
          #six_lut_match = re.search(r'(6-LUT)\s*:\s*(\d+)', line)
          #if six_lut_match is not None:
          #  six_lut = six_lut_match.group(2)
          #  result_dict['6_lut'] = int(six_lut) or 0        

          block_input_match = re.search(r'(\.input)\s*:\s*(\d+)', line)
          if block_input_match is not None:
            block_input = block_input_match.group(2)
            result_dict['block_input'] = int(block_input) or 0       

          block_output_match = re.search(r'(\.output)\s*:\s*(\d+)', line)
          if block_output_match is not None:
            block_output = block_output_match.group(2)
            result_dict['block_output'] = int(block_output) or 0          

          dual_port_ram_match = re.search(r'(dual_port_ram)\s*:\s*(\d+)', line)
          if dual_port_ram_match is not None:
            dual_port_ram = dual_port_ram_match.group(2)
            result_dict['dual_port_ram_before_vpr'] = int(dual_port_ram) or 0

          single_port_ram_match = re.search(r'(single_port_ram)\s*:\s*(\d+)', line)
          if single_port_ram_match is not None:
            single_port_ram = single_port_ram_match.group(2)
            result_dict['single_port_ram_before_vpr'] = int(single_port_ram) or 0          

          resource_usage_clb_match = re.search(r'(\d+)\s+blocks of type: clb', line)
          if resource_usage_clb_match is not None and ("Netlist" in prev_line):
            resource_usage_clb = resource_usage_clb_match.group(1)
            result_dict['resource_usage_clb'] = int(resource_usage_clb) or 0

          resource_usage_dsp_match = re.search(r'(\d+)\s+blocks of type: (dsp_top|mult_\d+)', line)
          #if result_dict['arch'] == "stratix":
          #if result_dict['arch'].startswith("k6FracN10LB"):
          #  resource_usage_dsp_match = re.search(r'(\d+)\s+blocks of type: dsp_top', line)
          ##elif result_dict['arch'] == "agilex":
          #elif result_dict['arch'].startswith("4bit_adder"):
          #  resource_usage_dsp_match = re.search(r'(\d+)\s+blocks of type: mult_27', line)
          #else:
          #  print("Unsupported dsp architecture")
          #  raise SystemExit(0)          
          if resource_usage_dsp_match is not None and ("Netlist" in prev_line):
            resource_usage_dsp = resource_usage_dsp_match.group(1)
            result_dict['resource_usage_dsp'] = int(resource_usage_dsp) or 0

          resource_usage_memory_match = re.search(r'(\d+)\s+blocks of type: memory', line)
          if resource_usage_memory_match is not None and ("Netlist" in prev_line):
            resource_usage_memory = resource_usage_memory_match.group(1)
            result_dict['resource_usage_memory'] = int(resource_usage_memory) or 0

          resource_usage_memory_compute_match = re.search(r'(mem_\d+x\d+)\s*:\s*(\d+)', line)
          if resource_usage_memory_compute_match is not None and pb_types_usage is True:
            resource_usage_memory_compute += int(resource_usage_memory_compute_match.group(2))
            result_dict['resource_usage_memory_compute'] = int(resource_usage_memory_compute) or 0

          device_io_match = re.search(r'(\d+)\s+blocks of type: io', line)
          if device_io_match is not None and ("Architecture" in prev_line):
            device_io = device_io_match.group(1)
            result_dict['device_io'] = int(device_io) or 0

          device_clb_match = re.search(r'(\d+)\s+blocks of type: clb', line)
          if device_clb_match is not None and ("Architecture" in prev_line):
            device_clb = device_clb_match.group(1)
            result_dict['device_clb'] = int(device_clb) or 0

          device_dsp_match = re.search(r'(\d+)\s+blocks of type: (dsp_top|mult_27)', line)
          if device_dsp_match is not None and ("Architecture" in prev_line):
            device_dsp = device_dsp_match.group(1)
            result_dict['device_dsp'] = int(device_dsp) or 0

          device_memory_match = re.search(r'(\d+)\s+blocks of type: memory', line)
          if device_memory_match is not None and ("Architecture" in prev_line):
            device_memory = device_memory_match.group(1)
            result_dict['device_memory'] = int(device_memory) or 0

          resource_usage_adder_match = re.search(r'adder\s*:\s*(\d*)', line)
          if resource_usage_adder_match is not None and pb_types_usage is True:
            resource_usage_adder += int(resource_usage_adder_match.group(1))
            result_dict['single_bit_adders'] = int(resource_usage_adder) or "Not found"

          resource_usage_lut_match = re.search(r'lut\s*:\s*(\d*)', line)
          if resource_usage_lut_match is not None and pb_types_usage is True:
            resource_usage_lut += int(resource_usage_lut_match.group(1))
            result_dict['luts'] = int(resource_usage_lut) or 0

          resource_usage_lut3_match = re.search(r'lut3\s*:\s*(\d*)', line)
          if resource_usage_lut3_match is not None and pb_types_usage is True:
            resource_usage_lut3 = int(resource_usage_lut3_match.group(1))
            result_dict['lut3'] = int(resource_usage_lut3) or  "Not found"

          resource_usage_lut4_match = re.search(r'lut3\s*:\s*(\d*)', line)
          if resource_usage_lut4_match is not None and pb_types_usage is True:
            resource_usage_lut4 = int(resource_usage_lut4_match.group(1))
            result_dict['lut4'] = int(resource_usage_lut4) or  "Not found"

          resource_usage_lut5_match = re.search(r'lut3\s*:\s*(\d*)', line)
          if resource_usage_lut5_match is not None and pb_types_usage is True:
            resource_usage_lut5 = int(resource_usage_lut5_match.group(1))
            result_dict['lut5'] = int(resource_usage_lut5) or  "Not found"

          resource_usage_lut6_match = re.search(r'lut3\s*:\s*(\d*)', line)
          if resource_usage_lut6_match is not None and pb_types_usage is True:
            resource_usage_lut6 = int(resource_usage_lut6_match.group(1))
            result_dict['lut6'] = int(resource_usage_lut6) or  "Not found"

          resource_usage_ff_match = re.search(r'ff\s*:\s*(\d*)', line)
          if resource_usage_ff_match is not None and pb_types_usage is True:
            resource_usage_ff += int(resource_usage_ff_match.group(1))
            result_dict['ffs'] = int(resource_usage_ff) or 0
        
          memory_slice_match = re.search(r'memory_slice\s*:\s*(\d*)', line)
          if memory_slice_match is not None and pb_types_usage is True:
            num_memory_slice += int(memory_slice_match.group(1))
            result_dict['memory_slice'] = int(num_memory_slice) or 0

          max_fanout_match = re.search(r'Max Fanout\s*:\s*(.*)', line)
          if max_fanout_match is not None and ("Avg Fanout" in prev_line):
            max_fanout = max_fanout_match.group(1)
            result_dict['max_fanout'] = round(float(max_fanout)) or 0

          max_non_global_fanout_match = re.search(r'Max Non Global Net Fanout\s*:\s*(.*)', line)
          if max_non_global_fanout_match is not None:
            max_non_global_fanout = max_non_global_fanout_match.group(1)
            result_dict['max_non_global_fanout'] = round(float(max_non_global_fanout)) or 0

          near_crit_connections_match = re.search(r'\[        0:      0.1\)\s*\d+\s*\(\s*([\d\.]*)%\)', line)
          if near_crit_connections_match is not None and ("Final Net Connection Criticality Histogram" in prev_line):
            near_crit_connections = near_crit_connections_match.group(1)
            result_dict['near_crit_connections'] = float(near_crit_connections) or 0

          max_routing_channel_util_match = re.search(r'Maximum routing channel utilization:\s+(.*) at \(.*\)', line)
          if max_routing_channel_util_match is not None:
            result_dict['max_routing_channel_util'] = max_routing_channel_util_match.group(1)

          if routing_channel_util_section is True:
            routing_histogram_match = re.search(r'\[\s+(.*):\s+(.*)\)\s*.*\s*\(\s*(.*)%\)', line)
            if routing_histogram_match is not None:
              utilization_min = float(routing_histogram_match.group(1))
              utilization_max = float(routing_histogram_match.group(2))
              pct_of_total_channels = float(routing_histogram_match.group(3))
              if pct_of_total_channels > largest_pct_of_total_channels:
                largest_pct_of_total_channels = pct_of_total_channels
                min_util_for_largest_pct_of_total_channels = utilization_min
                max_util_for_largest_pct_of_total_channels = utilization_max

            routing_histogram_1_inf_match = re.search(r'\[\s+1:\s+inf\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_1_inf_match is not None:
              result_dict["routing_histogram_1_inf_val"] = int(routing_histogram_1_inf_match.group(1))
              result_dict["routing_histogram_1_inf_pct"] = float(routing_histogram_1_inf_match.group(2))
            routing_histogram_09_1_match  = re.search(r'\[\s+0.9:\s+1\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_09_1_match is not None:
              result_dict["routing_histogram_09_1_val"] = int(routing_histogram_09_1_match.group(1))
              result_dict["routing_histogram_09_1_pct"] = float(routing_histogram_09_1_match.group(2))
            routing_histogram_08_09_match = re.search(r'\[\s+0.8:\s+0.9\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_08_09_match is not None:
              result_dict["routing_histogram_08_09_val"] = int(routing_histogram_08_09_match.group(1))
              result_dict["routing_histogram_08_09_pct"] = float(routing_histogram_08_09_match.group(2))
            routing_histogram_07_08_match = re.search(r'\[\s+0.7:\s+0.8\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_07_08_match is not None:
              result_dict["routing_histogram_07_08_val"] = int(routing_histogram_07_08_match.group(1))
              result_dict["routing_histogram_07_08_pct"] = float(routing_histogram_07_08_match.group(2))
            routing_histogram_06_07_match = re.search(r'\[\s+0.6:\s+0.7\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_06_07_match is not None:
              result_dict["routing_histogram_06_07_val"] = int(routing_histogram_06_07_match.group(1))
              result_dict["routing_histogram_06_07_pct"] = float(routing_histogram_06_07_match.group(2))
            routing_histogram_05_06_match = re.search(r'\[\s+0.5:\s+0.6\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_05_06_match is not None:
              result_dict["routing_histogram_05_06_val"] = int(routing_histogram_05_06_match.group(1))
              result_dict["routing_histogram_05_06_pct"] = float(routing_histogram_05_06_match.group(2))
            routing_histogram_04_05_match = re.search(r'\[\s+0.4:\s+0.5\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_04_05_match is not None:
              result_dict["routing_histogram_04_05_val"] = int(routing_histogram_04_05_match.group(1))
              result_dict["routing_histogram_04_05_pct"] = float(routing_histogram_04_05_match.group(2))
            routing_histogram_03_04_match = re.search(r'\[\s+0.3:\s+0.4\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_03_04_match is not None:
              result_dict["routing_histogram_03_04_val"] = int(routing_histogram_03_04_match.group(1))
              result_dict["routing_histogram_03_04_pct"] = float(routing_histogram_03_04_match.group(2))
            routing_histogram_02_03_match = re.search(r'\[\s+0.2:\s+0.3\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_02_03_match is not None:
              result_dict["routing_histogram_02_03_val"] = int(routing_histogram_02_03_match.group(1))
              result_dict["routing_histogram_02_03_pct"] = float(routing_histogram_02_03_match.group(2))
            routing_histogram_01_02_match = re.search(r'\[\s+0.1:\s+0.2\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_01_02_match is not None:
              result_dict["routing_histogram_01_02_val"] = int(routing_histogram_01_02_match.group(1))
              result_dict["routing_histogram_01_02_pct"] = float(routing_histogram_01_02_match.group(2))
            routing_histogram_00_01_match = re.search(r'\[\s+0:\s+0.1\)\s*(.*)\s*\(\s*(.*)%\)', line)
            if routing_histogram_00_01_match is not None:
              result_dict["routing_histogram_00_01_val"] = int(routing_histogram_00_01_match.group(1))
              result_dict["routing_histogram_00_01_pct"] = float(routing_histogram_00_01_match.group(2))

          prev_line = line 
          
        #calculated metrics
        if 'logic_area' in result_dict and 'resource_usage_clb' in result_dict \
          and 'resource_usage_dsp' in result_dict and 'resource_usage_memory' in result_dict:
          routing_area_clb = self.get_routing_area(result_dict["arch"], "clb")
          routing_area_dsp = self.get_routing_area(result_dict["arch"], "dsp")
          routing_area_memory = self.get_routing_area(result_dict["arch"], "memory")
          result_dict['routing_area'] = (routing_area_clb * result_dict['resource_usage_clb']) +\
                                        (routing_area_dsp * result_dict['resource_usage_dsp']) +\
                                        (routing_area_memory * result_dict['resource_usage_memory'])
          result_dict['total_area'] = float(result_dict['logic_area']) + float(result_dict['routing_area'])

        if 'ffs' in result_dict and 'luts' in result_dict and 'resource_usage_clb' in result_dict \
          and 'resource_usage_dsp' in result_dict and 'resource_usage_memory' in result_dict \
          and 'single_bit_adders' in result_dict:
          result_dict['ff_to_lut_ratio'] = result_dict['ffs'] / result_dict['luts']
          result_dict['dsp_to_clb_ratio'] = result_dict['resource_usage_dsp'] / result_dict['resource_usage_clb']
          result_dict['memory_to_clb_ratio'] = result_dict['resource_usage_memory'] / result_dict['resource_usage_clb']
          result_dict['adder_to_lut_ratio'] = result_dict['single_bit_adders'] / result_dict['luts']
          result_dict['dsp_to_lut_ratio'] = result_dict['resource_usage_dsp'] / result_dict['luts']
          result_dict['memory_to_lut_ratio'] = result_dict['resource_usage_memory'] / result_dict['luts']

        result_dict['largest_pct_of_total_channels'] = largest_pct_of_total_channels
        result_dict['min_util_for_largest_pct_of_total_channels'] = min_util_for_largest_pct_of_total_channels  
        result_dict['max_util_for_largest_pct_of_total_channels'] = max_util_for_largest_pct_of_total_channels  

        if 'resource_usage_memory_compute' in result_dict and 'resource_usage_memory' in result_dict:
          result_dict['resource_usage_memory_storage'] = result_dict['resource_usage_memory'] - result_dict['resource_usage_memory_compute']

        if 'num_routed_nets' in result_dict and 'average_net_length' in result_dict and 'resource_usage_io' in result_dict:
          result_dict['non_io_wire_length'] = (result_dict['num_routed_nets'] - result_dict['resource_usage_io']) * result_dict['average_net_length']

      ##--------------------------
      ##extract information from odin.blif
      ##--------------------------
      ##try to find <design>.odin.blif 
      #odin_blif_filename = self.find_file(dirname, run_num, result_dict['design']+'.odin.blif')
      #if odin_blif_filename is None:
      #  result_dict['odin_blif_found'] = "No" 
      #else:      
      #  result_dict['odin_blif_found'] = "Yes" 
  
      #  netlist_primitives = 0
      #  odin_blif = open(odin_blif_filename, "r")
      #  for line in odin_blif:
      #    if ".latch" in line or ".subckt" in line or ".names" in line:
      #      netlist_primitives = netlist_primitives + 1

      #  result_dict['netlist_primitives'] = netlist_primitives
      #  result_dict['netlist_primitives>100k'] = (netlist_primitives > 100000)

      #  odin_blif.close()

      #--------------------------
      #extract information from pre-vpr.blif
      #--------------------------
      #try to find <design>.pre-vpr.blif 
      pre_vpr_blif_filename = self.find_file(dirname, run_num, result_dict['design']+'.pre-vpr.blif')
      if pre_vpr_blif_filename is None:
        result_dict['pre_vpr_blif_found'] = "No" 
      else:      
        result_dict['pre_vpr_blif_found'] = "Yes" 
  
        netlist_primitives = 0
        pre_vpr_blif = open(pre_vpr_blif_filename, "r")
        for line in pre_vpr_blif:
          if ".latch" in line or ".subckt" in line or ".names" in line:
            netlist_primitives = netlist_primitives + 1

        result_dict['netlist_primitives'] = netlist_primitives
        result_dict['netlist_primitives>10k'] = (netlist_primitives > 10000)

        pre_vpr_blif.close()

      #--------------------------
      #extract information from parse_results.txt
      #--------------------------
      #try to find parse_results.txt
      parse_results_filename = self.find_file(dirname, run_num, 'parse_results.txt')
      if parse_results_filename is None:
        result_dict['parse_results_found'] = "No" 
      else:
        result_dict['parse_results_found'] = "Yes"
        parse_results_filehandle = open(parse_results_filename, "r")
        parse_results_dict_reader = csv.DictReader(parse_results_filehandle, delimiter='\t')
        for row in parse_results_dict_reader:
          #print(row.keys())
          #print(row.values())
          result_dict['vtr_flow_elapsed_time'] = row['vtr_flow_elapsed_time']
          result_dict['odin_time'] = row['odin_synth_time']
          result_dict['abc_time'] = row['abc_synth_time']
          result_dict['pack_time'] = row['pack_time']
          result_dict['place_time'] = row['place_time']
          result_dict['route_time'] = row['min_chan_width_route_time']
          result_dict['vtr_flow_peak_memory_usage'] = max(float(row['max_odin_mem']), \
                                                          float(row['max_abc_mem']), \
                                                          float(row['max_vpr_mem']))
          result_dict['logic_depth'] = row['abc_depth']
          result_dict['device_height'] = row['device_height']
          result_dict['device_width'] = row['device_width']
          result_dict['grid_size_limiter'] = row['device_limiting_resources']
          #result_dict['min_channel_width'] = row['min_chan_width']
          #result_dict['critical_path'] = row['critical_path_delay']
        parse_results_filehandle.close()

      #---------------------------------------------------
      # extract info from route file
      #---------------------------------------------------
      #def parse_switch(file_path, route_fname):
      # Append the desired subdirectories
      print("file_path:",new_full_path)
      print("route_fname:",folder_name)
      new_subdirectories = f"common/{folder_name}.route"
      new_path = os.path.join(new_full_path, new_subdirectories)
      #print ("new_path:",new_path)

      if os.path.isfile(new_path):
          #print("Route file found.")
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
                          current_coord = nearest_coord

          for switch in [1, 2]:
              max_count_coord = max(coord_counts[switch], key=coord_counts[switch].get)
              if switch == 1:                  
                  result_dict['sw1_max_cord'] = max_count_coord
                  result_dict['sw1_max_num'] = coord_counts[switch][max_count_coord]
              else:
                  result_dict['sw2_max_cord'] = max_count_coord
                  result_dict['sw2_max_num'] = coord_counts[switch][max_count_coord]

      else:
          print("Route file not found.") 

      #--------------------------
      #identify whether this is ml or non-ml design
      #--------------------------
      config_file = dirname + "/config/config.txt"
      config_fh = open(config_file, "r")
      result_dict["type"] = "non_ml"
      for line in config_fh:
        m = re.search("circuits_dir.*koios", line)
        if m is not None:
          result_dict["type"] = "ml"
          break
      config_fh.close()  

      result_dict["tag"] = self.tag

      #--------------------------
      # additional logic for 06-07 bucket in the routing util histogram
      # because VPR doesn't print this bucket for some reason
      #--------------------------
      if result_dict['vpr_results_found'] == "Yes" and result_dict['parse_results_found'] == "Yes":
        total_channels = 2 * (int(result_dict["device_width"])-1) * (int(result_dict["device_height"])-1)
        # calculates the percentage for the 06-07 bucket in the routing histogram by subtracting the sum of all other bucket percentages from 100. This value is stored in result_dict["routing_histogram_06_07_pct"].
        result_dict["routing_histogram_06_07_val"] = \
         total_channels - (\
         result_dict["routing_histogram_1_inf_val"] + \
         result_dict["routing_histogram_09_1_val"] + \
         result_dict["routing_histogram_08_09_val"] + \
         result_dict["routing_histogram_07_08_val"] + \
         result_dict["routing_histogram_05_06_val"] + \
         result_dict["routing_histogram_04_05_val"] + \
         result_dict["routing_histogram_03_04_val"] + \
         result_dict["routing_histogram_02_03_val"] + \
         result_dict["routing_histogram_01_02_val"] + \
         result_dict["routing_histogram_00_01_val"] )
        result_dict["routing_histogram_06_07_pct"] = \
          round(100 - (\
         result_dict["routing_histogram_1_inf_pct"] + \
         result_dict["routing_histogram_09_1_pct"] + \
         result_dict["routing_histogram_08_09_pct"] + \
         result_dict["routing_histogram_07_08_pct"] + \
         result_dict["routing_histogram_05_06_pct"] + \
         result_dict["routing_histogram_04_05_pct"] + \
         result_dict["routing_histogram_03_04_pct"] + \
         result_dict["routing_histogram_02_03_pct"] + \
         result_dict["routing_histogram_01_02_pct"] + \
         result_dict["routing_histogram_00_01_pct"] ))

      ## disabling power result collection ## #--------------------------
      ## disabling power result collection ## #extract information from <circuit>.power file
      ## disabling power result collection ## #--------------------------
      ## disabling power result collection ## #try to find the file
      ## disabling power result collection ## power_results_filename = self.find_file(dirname, run_num, result_dict['design']+'.power')
      ## disabling power result collection ## absolute_dynamic_power_of_circuit = 0
      ## disabling power result collection ## absolute_static_power_of_circuit = 0
      ## disabling power result collection ## absolute_total_power_of_circuit = 0
      ## disabling power result collection ## if power_results_filename is None:
      ## disabling power result collection ##   result_dict['power_results_found'] = "No" 
      ## disabling power result collection ## else:
      ## disabling power result collection ##   result_dict['power_results_found'] = "Yes"
      ## disabling power result collection ##   power_results_filehandle = open(power_results_filename, "r")
      ## disabling power result collection ##   for line in power_results_filehandle:
      ## disabling power result collection ##     m = re.search(r'(.*?)\s+([0-9]*\.?[0-9]+|-nan)\s+([0-9]*\.?[0-9]+|-nan)\s+([0-9]*\.?[0-9]+|-nan)', line)
      ## disabling power result collection ##     if m is not None:
      ## disabling power result collection ##       component = m.group(1).strip().lower()
      ## disabling power result collection ##       print("Obtained power data for: {}".format(component))
      ## disabling power result collection ##       if component in self.components_of_interest:
      ## disabling power result collection ##         
      ## disabling power result collection ##         #We want to ignore rows that contain "clock" but are not in the main table
      ## disabling power result collection ##         if (component == "clock") and ("Other Estimation Methods" not in prev_line):
      ## disabling power result collection ##           continue

      ## disabling power result collection ##         absolute_total_power_of_component = float(m.group(2)) if m.group(2) != "-nan" else 0
      ## disabling power result collection ##         print("Absolute power of component is {}".format(absolute_total_power_of_component))
      ## disabling power result collection ##         how_much_pct_of_circuit_power_is_this_component = float(m.group(3)) if m.group(3) != "-nan" else 0
      ## disabling power result collection ##         how_much_pct_of_component_power_is_dynamic = float(m.group(4)) if m.group(4) != "-nan" else 0

      ## disabling power result collection ##         #Calculated metrics
      ## disabling power result collection ##         absolute_dynamic_power_of_component = absolute_total_power_of_component * how_much_pct_of_component_power_is_dynamic
      ## disabling power result collection ##         absolute_static_power_of_component = absolute_total_power_of_component - absolute_dynamic_power_of_component

      ## disabling power result collection ##         result_dict[component+"_abs_total_power"] = absolute_total_power_of_component
      ## disabling power result collection ##         result_dict[component+"_abs_dynamic_power"] = absolute_dynamic_power_of_component
      ## disabling power result collection ##         result_dict[component+"_abs_static_power"] = absolute_static_power_of_component
      ## disabling power result collection ##         result_dict[component+"_pct_total_power"] = how_much_pct_of_circuit_power_is_this_component

      ## disabling power result collection ##         absolute_dynamic_power_of_circuit += absolute_dynamic_power_of_component
      ## disabling power result collection ##         absolute_static_power_of_circuit += absolute_static_power_of_component
      ## disabling power result collection ##         absolute_total_power_of_circuit += absolute_total_power_of_component

      ## disabling power result collection ##     prev_line = line 

      ## disabling power result collection ##   for component in self.components_of_interest:
      ## disabling power result collection ##     result_dict[component+"_pct_dynamic_power"] = result_dict[component+"_abs_dynamic_power"] / absolute_dynamic_power_of_circuit
      ## disabling power result collection ##     result_dict[component+"_pct_static_power"] = result_dict[component+"_abs_static_power"] / absolute_static_power_of_circuit
      ## disabling power result collection ##   
      ## disabling power result collection ##   result_dict["absolute_dynamic_power_of_circuit"] = absolute_dynamic_power_of_circuit
      ## disabling power result collection ##   result_dict["absolute_static_power_of_circuit"]  = absolute_static_power_of_circuit
      ## disabling power result collection ##   result_dict["absolute_total_power_of_circuit"]   = absolute_total_power_of_circuit

      ## disabling power result collection ##   power_results_filehandle.close()

      ## disabling power result collection ##   #Now extract compute ram power
      ## disabling power result collection ##   power_results_filehandle = open(power_results_filename, "r")
      ## disabling power result collection ##   for line in power_results_filehandle:
      ## disabling power result collection ##     m = re.search(r'(.*?)\s+([0-9]*\.?[0-9]+|-nan)\s+([0-9]*\.?[0-9]+|-nan)\s+([0-9]*\.?[0-9]+|-nan)', line)
      ## disabling power result collection ##     if m is not None:
      ## disabling power result collection ##       component = m.group(1).strip().lower()
      ## disabling power result collection ##       if component == "mem_128x128_compute":
      ## disabling power result collection ##         
      ## disabling power result collection ##         absolute_total_power_of_component = float(m.group(2)) if m.group(2) != "-nan" else 0
      ## disabling power result collection ##         how_much_pct_of_circuit_power_is_this_component = float(m.group(3)) if m.group(3) != "-nan" else 0
      ## disabling power result collection ##         how_much_pct_of_component_power_is_dynamic = float(m.group(4)) if m.group(4) != "-nan" else 0

      ## disabling power result collection ##         #Calculated metrics
      ## disabling power result collection ##         absolute_dynamic_power_of_component = absolute_total_power_of_component * how_much_pct_of_component_power_is_dynamic
      ## disabling power result collection ##         absolute_static_power_of_component = absolute_total_power_of_component - absolute_dynamic_power_of_component

      ## disabling power result collection ##         result_dict["compute_ram"+"_abs_total_power"]    = absolute_total_power_of_component
      ## disabling power result collection ##         result_dict["compute_ram"+"_abs_dynamic_power"]  = absolute_dynamic_power_of_component
      ## disabling power result collection ##         result_dict["compute_ram"+"_abs_static_power"]   = absolute_static_power_of_component
      ## disabling power result collection ##         result_dict["compute_ram"+"_pct_total_power"]    = how_much_pct_of_circuit_power_is_this_component
      ## disabling power result collection ##         result_dict["compute_ram"+"_pct_dynamic_power"]  = result_dict["compute_ram"+"_abs_dynamic_power"] / absolute_dynamic_power_of_circuit
      ## disabling power result collection ##         result_dict["compute_ram"+"_pct_static_power"]   = result_dict["compute_ram"+"_abs_static_power"] / absolute_static_power_of_circuit

      ## disabling power result collection ##         result_dict["storage_ram"+"_abs_total_power"]    = result_dict["memory"+"_abs_total_power"] - result_dict["compute_ram"+"_abs_total_power"]
      ## disabling power result collection ##         result_dict["storage_ram"+"_abs_dynamic_power"]  = result_dict["memory"+"_abs_dynamic_power"] - result_dict["compute_ram"+"_abs_dynamic_power"]
      ## disabling power result collection ##         result_dict["storage_ram"+"_abs_static_power"]   = result_dict["memory"+"_abs_static_power"] - result_dict["compute_ram"+"_abs_static_power"]
      ## disabling power result collection ##         result_dict["storage_ram"+"_pct_total_power"]    = result_dict["storage_ram"+"_abs_total_power"] / absolute_total_power_of_circuit
      ## disabling power result collection ##         result_dict["storage_ram"+"_pct_dynamic_power"]  = result_dict["storage_ram"+"_abs_dynamic_power"] / absolute_dynamic_power_of_circuit
      ## disabling power result collection ##         result_dict["storage_ram"+"_pct_static_power"]   = result_dict["storage_ram"+"_abs_static_power"] / absolute_static_power_of_circuit

      ## disabling power result collection ##   power_results_filehandle.close()
      """
      #----------------------------
      #clean up the directory
      #----------------------------
      if result_dict['pre_vpr_blif_found'] == "No" or result_dict['vpr_results_found'] == "No" or result_dict['parse_results_found'] == "No":
        print("One of the log files required was not found")
      else:
        #print("Parsing complete. Deleting logs/temp files")
        #Delete temp files except the 3 we need
        os.system("rm -rf " + dirname +"/" + run_num + "/*/*/*/*odin.blif")
        os.system("rm -rf " + dirname +"/" + run_num + "/*/*/*/*abc.blif")
        os.system("rm -rf " + dirname +"/" + run_num + "/*/*/*/*.net")
        os.system("rm -rf " + dirname +"/" + run_num + "/*/*/*/*.place")
        os.system("rm -rf " + dirname +"/" + run_num + "/*/*/*/*.route")
        os.system("rm -rf " + dirname +"/" + run_num + "/*/*/*/*.post_routing")
      """
      #append the current results to the main result list
      self.result_list.append(result_dict)
  
# ###############################################################
# main()
# ###############################################################
if __name__ == "__main__":
  GenResults()

