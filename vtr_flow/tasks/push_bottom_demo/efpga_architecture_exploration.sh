#############################################################################
#Top-level push-button flow for automatic eFPGA arch exploration
#Inputs: Architectures, Benchmarks
#Outputs: Our evaluation results in a csv file, which can be used to obtain the best architecture.
#############################################################################

#############################################################################
#1. Architecture file generation
#Inputs: An architecture template file (.xml), and a list of parameters to vary (.txt).
#Outputs: Generated architecture files (in the Architecture folder), and a table of all the architectrues with detail parameters (arch_dict.csv)
#############################################################################
python3 ../../mako_arch_gen/arch_render_0404_dict.py -i ../../mako_arch_gen/arch_template_0402.xml -o Architectures/stratix.xml -p ../../mako_arch_gen/values.txt
  
#############################################################################
#2. Generate config file for VTR tasks
#Inputs: The architecure files in the Architecture folder, and benchmark files in a folder named Benchmarks.
#Outputs: Updated vtr task config file.
#############################################################################
python3 ../../mako_arch_gen/config_gen0404.py

#############################################################################
#3. Run VTR for all arch and benchmark combinations
#Inputs: architectures, benchmarks, and config file.
#Outputs: Logs generated by VTR in runxxx directory.
#############################################################################
python3 -u ../../scripts/run_vtr_task_cc.py . -j 16

#############################################################################
#4. Evaluate performance
#Inputs: runxxx/qor_results.txt
#Outputs: A csv file with performance results averaged across benchmarks.
#############################################################################
python3 ../../parse/qor_evalu.py -alpha 1 -beta 2 -i run001/qor_results.txt
