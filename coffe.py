### COFFE: CIRCUIT OPTIMIZATION FOR FPGA EXPLORATION
# Created by: Charles Chiasson (charles.chiasson@gmail.com)
#         at: University of Toronto
#         in: 2013        
      
# BRAM simulation added by Sadegh Yazdanshenas in 2016
# MTJ and SRAM designs by Kosuke Tatsumura
# COFFE 2.0 by Sadegh Yazdanshenas 2015-2018     

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

print "\nCOFFE 2.0\n"
print "Man is a tool-using animal."
print "Without tools he is nothing, with tools he is all."
print "                           - Thomas Carlyle\n\n"

# TODO: see the effect on disabling floorplanning on results and runtime
# if it is worth it we could add an argument which could disable 
# floorplanning for a quicker run

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

# quick mode is disabled by default. Try passing -q 0.03 for 3% minimum improvement
parser.add_argument('-q', '--quick_mode', type=float, default=-1.0, help="minimum cost function improvement for resizing")


args = parser.parse_args()

is_size_transistors = not args.no_sizing


# Make the top-level spice folder if it doesn't already exist
# if it's already there delete its content
arch_folder = utils.create_output_dir(args.arch_description)

# Print the options to both terminal and report file
report_file_path = os.path.join(arch_folder, "report.txt") 
utils.print_run_options(args, report_file_path)

# Load the input architecture description file
arch_params_dict = utils.load_arch_params(args.arch_description)

# Print architecture and process details to terminal and report file
utils.print_architecture_params(arch_params_dict, report_file_path)

# Default_dir is the dir you ran COFFE from. COFFE will be switching directories 
# while running HSPICE, this variable is so that we can get back to our starting point
default_dir = os.getcwd()

# Create an HSPICE interface
spice_interface = spice.SpiceInterface()


# Record start time
total_start_time = time.time()

# this is a temporary parameter it will be checked before executing
# any change introduced to the code to be able to check if the original 
# code is working after adding any change
# this controles appyling or disabling the new updates

# This is commented since it was added to the architecture description file
# 1 ------> Stratix10
# 2 ------> Adding second level of adders
# 3 ------> Adding a by pass mux for the second level of adders
# arch_params_dict['updates'] = 1


# Create an FPGA instance
fpga_inst = fpga.FPGA(arch_params_dict, args, spice_interface)
                     

###############################################################
## GENERATE FILES
###############################################################


# Change to the architecture directory
os.chdir(arch_folder)  

# Generate FPGA and associated SPICE files
fpga_inst.generate() 

# Go back to the base directory
os.chdir(default_dir)

# Extract initial transistor sizes from file and overwrite the 
# default initial sizes if this option was used.
if args.initial_sizes != "default" :
  utils.use_initial_tran_size(args.initial_sizes, fpga_inst, tran_sizing, arch_params_dict['use_tgate'])

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
  # in case of disabeling floorplanning there is no need to 
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
  tran_sizing.print_final_transistor_size(fpga_inst, "transistor_sizes.txt")

# Obtain Memory core power
if arch_params_dict['enable_bram_module'] == 1:
  fpga_inst.update_power(spice_interface)


# Go back to the base directory
os.chdir(default_dir)

# Print out final COFFE report to file
utils.print_summary(arch_folder, fpga_inst, total_start_time)

# Print detailed delays
if fpga_inst.specs.updates:
  delay_report_path = os.path.join(arch_folder, "delays_report.txt") 
  delay_report = open(delay_report_path, 'w')
  utils.print_detailed_delays(delay_report, fpga_inst)
  delay_report.close()

# Print vpr architecure file
# The architecture description file should be changes for vpr
if not fpga_inst.updates:
  coffe.vpr.print_vpr_file(fpga_inst, arch_folder, arch_params_dict['enable_bram_module'])