###############################################################
### COFFE: CIRCUIT OPTIMIZATION FOR FPGA EXPLORATION
###############################################################
# Created by: Charles Chiasson (charles.chiasson@gmail.com)
#         at: University of Toronto
#         in: 2013        
###############################################################
# BRAM simulation added by Sadegh Yazdanshenas in 2016
# MTJ and SRAM designs by Kosuke Tatsumura
# COFFE 2.0 by Sadegh Yazdanshenas 2015-2018     
###############################################################

# The big picture:
#
# COFFE will size the transistors of an FPGA based on some input architecture 
# parameters. COFFE will produce area and delay results that can be used to
# create VPR architecture files for architecture exploration. By changing how
# COFFE designs circuitry, one could also use COFFE to explore different FPGA
# circuit designs.
#
# How it works (in a nutshell):
#
# We start off by creating an 'FPGA' object with the input architecture parameters.
# This FPGA object contains other objects that each represent part of the FPGA
# circuitry (like switch block, LUT, etc.).
# We use the FPGA object to generate SPICE netlists of the circuitry
# We also use it to calculate area and wire loads
# 
# Once the FPGA object is created and the SPICE netlists are generated,
# we pass the FPGA object to COFFE's transistor sizing engine. The following paper 
# explains COFFE's transistor sizing algorithm in detail.
#
# [1] C. Chiasson and V. Betz, "COFFE: Fully-Automated Transistor Sizing for FPGAs", FPT2013
#
 

import os
import sys
import argparse
import time
import coffe.fpga as fpga
import coffe.spice as spice
import coffe.tran_sizing as tran_sizing
import coffe.utils as utils
import coffe.vpr
import datetime
import math

print ("\nCOFFE 2.0\n")
print ("Man is a tool-using animal.")
print ("Without tools he is nothing, with tools he is all.")
print ("                           - Thomas Carlyle\n\n")

# Parse the input arguments with argparse
parser = argparse.ArgumentParser()
parser.add_argument('arch_description')
parser.add_argument('-n', '--no_sizing', help="don't perform transistor sizing", action='store_true')
parser.add_argument('-o', '--opt_type', type=str, choices=["global", "local"], default="global", help="choose optimization type")
parser.add_argument('-s', '--initial_sizes', type=str, default="default", help="path to initial transistor sizes")
parser.add_argument('-m', '--re_erf', type=int, default=1, help="choose how many sizing combos to re-erf")
parser.add_argument('-a', '--area_opt_weight', type=int, default=1, help="area optimization weight")
parser.add_argument('-d', '--delay_opt_weight', type=int, default=1, help="delay optimization weight")
parser.add_argument('-i', '--max_iterations', type=int, default=6, help="max FPGA sizing iterations")
parser.add_argument('-hi', '--size_hb_interfaces', type=float, help="perform transistor sizing only for hard block interfaces", default=0.0)
#arguments for ASIC flow 
parser.add_argument('-ho',"--hardblock_only",help="run only a single hardblock through the asic flow", action='store_true',default=False)
parser.add_argument('-g',"--gen_hb_scripts",help="generates all hardblock scripts which can be run by a user",action='store_true',default=False)
parser.add_argument('-p',"--parallel_hb_flow",help="runs the hardblock flow for current parameter selection in a parallel fashion",action='store_true',default=False)
parser.add_argument('-r',"--parse_pll_hb_flow",help="parses the hardblock flow from previously generated results",action='store_true',default=False)

# quick mode is disabled by default. Try passing -q 0.03 for 3% minimum improvement
parser.add_argument('-q', '--quick_mode', type=float, default=-1.0, help="minimum cost function improvement for resizing")

args = parser.parse_args()

# Load the input architecture description file
coffe_params = utils.load_params(args.arch_description,args)

# Make the top-level spice folder if it doesn't already exist
# if it's already there delete its content
arch_folder = utils.create_output_dir(args.arch_description, coffe_params["fpga_arch_params"]['arch_out_folder'])
if(args.hardblock_only):
  # Change to the architecture directory
  for hardblock_params in coffe_params["asic_hardblock_params"]["hardblocks"]:
    hard_block = fpga._hard_block(hardblock_params,False,args)
    os.chdir(arch_folder)
    if(args.gen_hb_scripts):
      hard_block.generate_hb_scripts()
    elif(args.parallel_hb_flow):
      hard_block.generate_top_parallel()
    elif(args.parse_pll_hb_flow):
      hard_block.generate_parallel_results()
    else:
      hard_block.generate_top()
else:
  is_size_transistors = not args.no_sizing
  size_hb_interfaces = args.size_hb_interfaces

  # Print the options to both terminal and report file
  report_file_path = os.path.join(arch_folder, "report.txt") 
  utils.print_run_options(args, report_file_path)

  # Print architecture and process details to terminal and report file
  utils.print_architecture_params(coffe_params["fpga_arch_params"], report_file_path)

  # Default_dir is the dir you ran COFFE from. COFFE will be switching directories 
  # while running HSPICE, this variable is so that we can get back to our starting point
  default_dir = os.getcwd()

  # Create an HSPICE interface
  spice_interface = spice.SpiceInterface()

  # Record start time
  total_start_time = time.time()

  # Create an FPGA instance
  fpga_inst = fpga.FPGA(coffe_params, args, spice_interface)
                      
  ###############################################################
  ## GENERATE FILES
  ###############################################################

  # Change to the architecture directory
  os.chdir(arch_folder)  

  # Generate FPGA and associated SPICE files
  fpga_inst.generate(is_size_transistors, size_hb_interfaces) 

  # Go back to the base directory
  os.chdir(default_dir)

  # Extract initial transistor sizes from file and overwrite the 
  # default initial sizes if this option was used.
  if args.initial_sizes != "default" :
    utils.use_initial_tran_size(args.initial_sizes, fpga_inst, tran_sizing, coffe_params["fpga_arch_params"]['use_tgate'])

  # Print FPGA implementation details
  report_file = open(report_file_path, 'a')
  fpga_inst.print_details(report_file)  
  report_file.close()

  # Go to architecture directory
  os.chdir(arch_folder)

  ###############################################################
  ## TRANSISTOR SIZING
  ###############################################################

  sys.stdout.flush()

  # Size FPGA transistors
  if is_size_transistors:
      tran_sizing.size_fpga_transistors(fpga_inst, args, spice_interface)                                    
  else:
    # in case of disabling floorplanning there is no need to 
    # update delays before updating area. Tried both ways and 
    # they give exactly the same results
    #fpga_inst.update_delays(spice_interface)

    # same thing here no need to update area before calculating 
    # the lb_height value. Also tested and gave same results
    #fpga_inst.update_area()
    fpga_inst.lb_height = math.sqrt(fpga_inst.area_dict["tile"])
    fpga_inst.update_area()
    fpga_inst.compute_distance()
    fpga_inst.update_wires()
    fpga_inst.update_wire_rc()

    # commented this part to avoid doing floorplannig for
    # a non-sizing run
    #fpga_inst.determine_height()

    fpga_inst.update_delays(spice_interface)

  # Obtain Memory core power
  if coffe_params["fpga_arch_params"]['enable_bram_module'] == 1:
    fpga_inst.update_power(spice_interface)

  # Go back to the base directory
  os.chdir(default_dir)

  # Print out final COFFE report to file
  utils.print_summary(arch_folder, fpga_inst, total_start_time)

  # Print vpr architecure file
  coffe.vpr.print_vpr_file(fpga_inst, arch_folder, coffe_params["fpga_arch_params"]['enable_bram_module'])
