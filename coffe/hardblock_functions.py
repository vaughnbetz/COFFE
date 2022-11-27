# Hard block script for COFFE flow.
# Created by: Sadegh Yazdanshenas
# Email: sadegh.yazdanshenas@mail.utoronto.ca
# University of Toronto, 2017

import os,stat
import sys
import subprocess
import re
import shutil
import math
import glob
import multiprocessing as mp


"""
Notes:
We have a data structure for parameters needed in the flow, but there are other params which are like the output paths for the synthesis stag
it may make more sense to have a data structure containing paths for connecting stages of the flow synth->pnr->sta
"""
def file_write_ln(fd, line):
  """
  writes a line to a file with newline after
  """
  fd.write(line + "\n")

def write_synth_tcl(flow_settings,clock_period,wire_selection,rel_outputs=False):
  """
  Writes the dc_script.tcl file which will be executed to run synthesis using Synopsys Design Compiler, tested under 2017 version.
  Relative output parameter is to accomodate legacy use of function while allowing the new version to run many scripts in parallel
  """
  report_path = flow_settings['synth_folder'] if (not rel_outputs) else os.path.join("..","reports")
  output_path = flow_settings['synth_folder'] if (not rel_outputs) else os.path.join("..","outputs")
  report_path = os.path.abspath(report_path)
  output_path = os.path.abspath(output_path)

  #Below lines could be done in the preprocessing function
  #create var named my_files of a list of design files
  if len(flow_settings["design_files"]) == 1:
    design_files_str = "set my_files " + flow_settings["design_files"][0]
  else:
    design_files_str = "set my_files [list " + " ".join([ent for ent in flow_settings["design_files"] if (ent != "parameters.v" and ent  != "c_functions.v") ]) + " ]"
  #analyze design files based on RTL lang
  if flow_settings['design_language'] == 'verilog':
    analyze_cmd_str = "analyze -f verilog $my_files"
  elif flow_settings['design_language'] == 'vhdl':
    analyze_cmd_str = "analyze -f vhdl $my_files"
  else:
    analyze_cmd_str = "analyze -f sverilog $my_files"

  #If wire_selection is None, then no wireload model is used during synthesis. This does imply results 
  #are not as accurate (wires don't have any delay and area), but is useful to let the flow work/proceed 
  #if the std cell library is missing wireload models.
  if wire_selection != "None":
    wire_ld_sel_str = "set_wire_load_selection " + wire_selection
  else:
    wire_ld_sel_str = "#No WIRE LOAD MODEL SELECTED, RESULTS NOT AS ACCURATE"

  if flow_settings['read_saif_file']:
    sw_activity_str = "read_saif saif.saif"
  else:
    sw_activity_str = "set_switching_activity -static_probability " + str(flow_settings['static_probability']) + " -toggle_rate " + str(flow_settings['toggle_rate']) + " -base_clock $my_clock_pin -type inputs"

  #Ungrouping settings command
  if flow_settings["ungroup_regex"] != "":
    set_ungroup_cmd = "set_attribute [get_cells -regex " + "\"" + flow_settings["ungroup_regex"] + "\"" + "] ungroup false" #this will ungroup all blocks
  else:
    set_ungroup_cmd = "# NO UNGROUPING SETTINGS APPLIED, MODULES WILL BE FLATTENED ACCORDING TO DC"
    
  synthesized_fname = "synthesized"
  file_lines = [
    #This line sets the naming convention of DC to not add parameters to module insts
    "set template_parameter_style \"\"",
    "set template_naming_style \"%s\"",
    "set search_path " + flow_settings["search_path"],
    design_files_str,
    "set my_top_level " + flow_settings['top_level'],
    "set my_clock_pin " + flow_settings['clock_pin_name'],
    "set target_library " + flow_settings["target_library"],
    "set link_library " + flow_settings["link_library"],
    "set power_analysis_mode \"averaged\"",
    "define_design_lib WORK -path ./WORK",
    analyze_cmd_str,
    "elaborate $my_top_level",
    "current_design $my_top_level",
    "check_design > " +                             os.path.join(report_path,"check_precompile.rpt"),
    "link",
    "uniquify",
    wire_ld_sel_str,
    "set my_period " + str(clock_period),
    "set find_clock [ find port [list $my_clock_pin] ]",
    "if { $find_clock != [list] } { ",
    "set clk_name $my_clock_pin ",
    "create_clock -period $my_period $clk_name}",
    set_ungroup_cmd,
    "compile_ultra",
    "check_design >  " +                            os.path.join(report_path,"check.rpt"),
    "write -format verilog -hierarchy -output " +   os.path.join(output_path,synthesized_fname+"_hier.v"),
    "write_file -format ddc -hierarchy -output " +  os.path.join(output_path,flow_settings['top_level'] + ".ddc"),
    sw_activity_str,
    "ungroup -all -flatten ",
    "report_power > " +                             os.path.join(report_path,"power.rpt"),
    "report_area -nosplit -hierarchy > " +          os.path.join(report_path,"area.rpt"),
    "report_resources -nosplit -hierarchy > " +     os.path.join(report_path,"resources.rpt"),
    "report_timing > " +                            os.path.join(report_path,"timing.rpt"),
    "report_design > " +                            os.path.join(report_path,"design.rpt"),
    "all_registers > " +                            os.path.join(report_path,"registers.rpt"),
    "change_names -hier -rule verilog ",    
    "write -f verilog -output " +                   os.path.join(output_path,synthesized_fname+"_flat.v"),
    "write_sdf " +                                  os.path.join(output_path,synthesized_fname+".sdf"),
    "write_parasitics -output " +                   os.path.join(output_path,synthesized_fname+".spef"),
    "write_sdc " +                                  os.path.join(output_path,synthesized_fname+".sdc")
  ]
  fd = open("dc_script.tcl","w")
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"quit")
  fd.close()
  return report_path,output_path

def copy_syn_outputs(flow_settings,clock_period,wire_selection,syn_report_path,only_reports=True):
  """
  During serial operation of the hardblock flow this function will copy the outputs of synthesis to a new param specific directory, if one only wants reports that is an option
  """
  synth_report_str = flow_settings["top_level"] + "_period_" + clock_period + "_" + "wiremdl_" + wire_selection
  report_dest_str = os.path.join(flow_settings['synth_folder'],synth_report_str + "_reports")
  mkdir_cmd_str = "mkdir -p " + report_dest_str
  copy_rep_cmd_str = "cp " + os.path.join(syn_report_path,"*") + " " + report_dest_str if not only_reports else "cp " + os.path.join(syn_report_path,"*.rpt ") + report_dest_str
  copy_logs_cmd_str = "cp " + "dc.log "+ "dc_script.tcl " + report_dest_str
  subprocess.call(mkdir_cmd_str,shell=True)
  subprocess.call(copy_rep_cmd_str,shell=True)
  subprocess.call(copy_logs_cmd_str,shell=True)
  subprocess.call('rm -f dc.log dc_script.tcl',shell=True)
  return synth_report_str


def check_synth_run(flow_settings,syn_report_path):
  """
  This function checks to make sure synthesis ran properly
  """
  # Make sure it worked properly
  # Open the timing report and make sure the critical path is non-zero:
  check_file = open(os.path.join(syn_report_path,"check.rpt"), "r")
  for line in check_file:
    if "Error" in line:
      print("Your design has errors. Refer to check.rpt in synthesis directory")
      sys.exit(-1)
    elif "Warning" in line and flow_settings['show_warnings']:
      print("Your design has warnings. Refer to check.rpt in synthesis directory")
      print("In spite of the warning, the rest of the flow will continue to execute.")
  check_file.close()


#search_path_dirs,design_files,
def run_synth(flow_settings,clock_period,wire_selection):
  """"
  runs the synthesis flow for specific clock period and wireload model
  Prereqs: flow_settings_pre_process() function to properly format params for scripts
  """
  syn_report_path, syn_output_path = write_synth_tcl(flow_settings,clock_period,wire_selection)
  # Run the script in design compiler shell
  synth_run_cmd = "dc_shell-t -f " + "dc_script.tcl" + " | tee dc.log"
  subprocess.call(synth_run_cmd, shell=True, executable="/bin/bash")
  # clean after DC!
  subprocess.call('rm -rf command.log', shell=True)
  subprocess.call('rm -rf default.svf', shell=True)
  subprocess.call('rm -rf filenames.log', shell=True)

  check_synth_run(flow_settings,syn_report_path)

  #Copy synthesis results to a unique dir in synth dir
  synth_report_str = copy_syn_outputs(flow_settings,clock_period,wire_selection,syn_report_path)
  #if the user doesn't want to perform place and route, extract the results from DC reports and end
  if flow_settings['synthesis_only']:
    # read total area from the report file:
    file = open(flow_settings['synth_folder'] + "/area.rpt" ,"r")
    for line in file:
      if line.startswith('Total cell area:'):
        total_area = re.findall(r'\d+\.{0,1}\d*', line)
    file.close()
    # Read timing parameters
    file = open(flow_settings['synth_folder'] + "/timing.rpt" ,"r")
    for line in file:
      if 'library setup time' in line:
        library_setup_time = re.findall(r'\d+\.{0,1}\d*', line)
      if 'data arrival time' in line:
        data_arrival_time = re.findall(r'\d+\.{0,1}\d*', line)
    try:
      total_delay =  float(library_setup_time[0]) + float(data_arrival_time[0])
    except NameError:
      total_delay =  float(data_arrival_time[0])
    file.close()    
    # Read dynamic power
    file = open(flow_settings['synth_folder'] + "/power.rpt" ,"r")
    for line in file:
      if 'Total Dynamic Power' in line:
        total_dynamic_power = re.findall(r'\d+\.\d*', line)
        total_dynamic_power[0] = float(total_dynamic_power[0])
        if 'mW' in line:
          total_dynamic_power[0] *= 0.001
        elif 'uw' in line:
          total_dynamic_power[0] *= 0.000001
        else:
          total_dynamic_power[0] = 0
    file.close()
    # write the final report file:
    file = open("report.txt" ,"w")
    file.write("total area = "  + str(total_area[0]) +  "\n")
    file.write("total delay = " + str(total_delay) + " ns\n")
    file.write("total power = " + str(total_dynamic_power[0]) + " W\n")
    file.close()
    #return
  return synth_report_str,syn_output_path

def write_innovus_view_file(flow_settings,syn_output_path):
  """Write .view file for innovus place and route, this is used for for creating the delay corners from timing libs and importings constraints"""
  fname = flow_settings["top_level"]+".view"

  file_lines = [
    "# Version:1.0 MMMC View Definition File\n# Do Not Remove Above Line",
    #I created a typical delay corner but I don't think its being used as its not called in create_analysis_view command, however, may be useful? not sure but its here
    #One could put RC values (maybe temperature in here) later for now they will all be the same
    "create_rc_corner -name RC_BEST -preRoute_res {1.0} -preRoute_cap {1.0} -preRoute_clkres {0.0} -preRoute_clkcap {0.0} -postRoute_res {1.0} -postRoute_cap {1.0} -postRoute_xcap {1.0} -postRoute_clkres {0.0} -postRoute_clkcap {0.0}",
    "create_rc_corner -name RC_TYP -preRoute_res {1.0} -preRoute_cap {1.0} -preRoute_clkres {0.0} -preRoute_clkcap {0.0} -postRoute_res {1.0} -postRoute_cap {1.0} -postRoute_xcap {1.0} -postRoute_clkres {0.0} -postRoute_clkcap {0.0}",
    "create_rc_corner -name RC_WORST -preRoute_res {1.0} -preRoute_cap {1.0} -preRoute_clkres {0.0} -preRoute_clkcap {0.0} -postRoute_res {1.0} -postRoute_cap {1.0} -postRoute_xcap {1.0} -postRoute_clkres {0.0} -postRoute_clkcap {0.0}",
    #create libraries for each timing corner
    "create_library_set -name MIN_TIMING -timing {" + flow_settings["best_case_libs"] + "}",
    "create_library_set -name TYP_TIMING -timing {" + flow_settings["standard_libs"] + "}",
    "create_library_set -name MAX_TIMING -timing {" + flow_settings["worst_case_libs"] + "}",
    #import constraints from synthesis generated sdc
    "create_constraint_mode -name CONSTRAINTS -sdc_files {" + os.path.join(syn_output_path,"synthesized.sdc") + "}" ,
    "create_delay_corner -name MIN_DELAY -library_set {MIN_TIMING} -rc_corner {RC_BEST}",
    "create_delay_corner -name TYP_DELAY -library_set {TYP_TIMING} -rc_corner {RC_TYP}",
    "create_delay_corner -name MAX_DELAY -library_set {MAX_TIMING} -rc_corner {RC_WORST}",
    "create_analysis_view -name BEST_CASE -constraint_mode {CONSTRAINTS} -delay_corner {MIN_DELAY}",
    "create_analysis_view -name TYP_CASE -constraint_mode {CONSTRAINTS} -delay_corner {TYP_DELAY}",
    "create_analysis_view -name WORST_CASE -constraint_mode {CONSTRAINTS} -delay_corner {MAX_DELAY}",
    #This sets our analysis view to be using our worst case analysis view for setup and best for timing,
    #This makes sense as the BC libs would have the most severe hold violations and vice versa for setup 
    "set_analysis_view -setup {WORST_CASE} -hold {BEST_CASE}"
  ]
  fd = open(fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  fd.close()
  view_abs_path = os.path.join(os.getcwd(),fname)
  return view_abs_path 


def write_edit_port_script_pre_ptn(flow_settings):
  """
  Currently this only works for the NoC ports, in the future these would have to be autogenerated or generated in a more general way.
  This function generates and edits the pin locations for the NoC design based on (1) size of overall floorplan and (2)
  """
  # Below code was to be used to allow for general correlation of ports/pins based on topology of NoC, innovus commands useful so here they are
  # flow_settings["ptn_params"]["sep_ports_regex"] = "channel"
  # "set enc_tcl_return_display_limit 1000000" #set it to 10^6 why not just dont want to cut off stuff
  # "dbGet top.terms.name -regex "channel" #lets set this to grab input/output channels for now, <- this grabs all ports in the design matching regex
  #number of port groups on the NoC would need to be a param for the above to work (Ex. there should be 4 + 1 for 2D mesh)


  #Current hard params which will only work for the NoC design under current flow, I'd like to change this but I dont see a reason to bring this to the user as no other value would work
  rtr_mod_name = "vcr_top_1"

  #offset from start of line in which pins are being placed (Ex. if they are being placed on edge 1 cw the offset would be from NW corner towards NE)
  #grab fp coordinates for the router module
  rtr_fp_coords = [e["fp_coords"] for e in flow_settings["ptn_params"]["ptn_list"] if e["mod_name"] == rtr_mod_name][0]
  #extract height and width
  rtr_dims = [abs(float(rtr_fp_coords[0]) - float(rtr_fp_coords[2])),abs(float(rtr_fp_coords[1]) - float(rtr_fp_coords[3]))] # w,h
  #below values were tuned manually for reasonable pin placement w.r.t router dimensions
  #TODO when actually creating a lattice of partitioned routers we would need to swap the placement of in/out ports (currently you have inputs facing inputs) but this is fine for link length study
  #below offsets are where the channel in/out pins should be placed
  ch_in_offset = rtr_dims[0]/(10.0) + float(rtr_fp_coords[0]) #Assuming square for now just for ease, rtr side len 
  ch_out_offset = rtr_dims[1] - (rtr_dims[0]/(10.0))*3 + float(rtr_fp_coords[0])#both offsets, doubled the subtraction as they are instantiated in same direction
  #one side of the NoC will have the equivilant of two channels representing the compute connections so we want to deal with these offsets independantly
  noc_comm_edge_offsets = [ch_in_offset - rtr_dims[0]/(20.0),ch_out_offset - rtr_dims[0]/5.0]  

  #The below port strings for the channel were taken from innovus by loading in the floorplan and using the below command:
  # > dbGet top.terms.name > my_output_file
  # I then divided them according to the topology of the NoC and bits/channel, in the future to make this general one could take the ports from dbGet command...
  # ...and divide thier indicies by the number of connections to other routers (Ex. total_channel_width/4 = 68 ports per in/out channel) 
  # I put other ports into variables but I'm only worrying about channel pin assignments, the rest will be done via pnr tool 
  fd = open("port_vars.tcl","w")
  file_lines = [
    #side 0
    "set my_0_ch_in_ports {\"channel_in_ip_d[0]\" \"channel_in_ip_d[1]\" \"channel_in_ip_d[2]\" \"channel_in_ip_d[3]\" \"channel_in_ip_d[4]\" \"channel_in_ip_d[5]\" \"channel_in_ip_d[6]\" \"channel_in_ip_d[7]\" \"channel_in_ip_d[8]\" \"channel_in_ip_d[9]\" \"channel_in_ip_d[10]\" \"channel_in_ip_d[11]\" \"channel_in_ip_d[12]\" \"channel_in_ip_d[13]\" \"channel_in_ip_d[14]\" \"channel_in_ip_d[15]\" \"channel_in_ip_d[16]\" \"channel_in_ip_d[17]\" \"channel_in_ip_d[18]\" \"channel_in_ip_d[19]\" \"channel_in_ip_d[20]\" \"channel_in_ip_d[21]\" \"channel_in_ip_d[22]\" \"channel_in_ip_d[23]\" \"channel_in_ip_d[24]\" \"channel_in_ip_d[25]\" \"channel_in_ip_d[26]\" \"channel_in_ip_d[27]\" \"channel_in_ip_d[28]\" \"channel_in_ip_d[29]\" \"channel_in_ip_d[30]\" \"channel_in_ip_d[31]\" \"channel_in_ip_d[32]\" \"channel_in_ip_d[33]\" \"channel_in_ip_d[34]\" \"channel_in_ip_d[35]\" \"channel_in_ip_d[36]\" \"channel_in_ip_d[37]\" \"channel_in_ip_d[38]\" \"channel_in_ip_d[39]\" \"channel_in_ip_d[40]\" \"channel_in_ip_d[41]\" \"channel_in_ip_d[42]\" \"channel_in_ip_d[43]\" \"channel_in_ip_d[44]\" \"channel_in_ip_d[45]\" \"channel_in_ip_d[46]\" \"channel_in_ip_d[47]\" \"channel_in_ip_d[48]\" \"channel_in_ip_d[49]\" \"channel_in_ip_d[50]\" \"channel_in_ip_d[51]\" \"channel_in_ip_d[52]\" \"channel_in_ip_d[53]\" \"channel_in_ip_d[54]\" \"channel_in_ip_d[55]\" \"channel_in_ip_d[56]\" \"channel_in_ip_d[57]\" \"channel_in_ip_d[58]\" \"channel_in_ip_d[59]\" \"channel_in_ip_d[60]\" \"channel_in_ip_d[61]\" \"channel_in_ip_d[62]\" \"channel_in_ip_d[63]\" \"channel_in_ip_d[64]\" \"channel_in_ip_d[65]\" \"channel_in_ip_d[66]\" \"channel_in_ip_d[67]\"}",
    #side 1
    "set my_1_ch_in_ports {\"channel_in_ip_d[68]\" \"channel_in_ip_d[69]\" \"channel_in_ip_d[70]\" \"channel_in_ip_d[71]\" \"channel_in_ip_d[72]\" \"channel_in_ip_d[73]\" \"channel_in_ip_d[74]\" \"channel_in_ip_d[75]\" \"channel_in_ip_d[76]\" \"channel_in_ip_d[77]\" \"channel_in_ip_d[78]\" \"channel_in_ip_d[79]\" \"channel_in_ip_d[80]\" \"channel_in_ip_d[81]\" \"channel_in_ip_d[82]\" \"channel_in_ip_d[83]\" \"channel_in_ip_d[84]\" \"channel_in_ip_d[85]\" \"channel_in_ip_d[86]\" \"channel_in_ip_d[87]\" \"channel_in_ip_d[88]\" \"channel_in_ip_d[89]\" \"channel_in_ip_d[90]\" \"channel_in_ip_d[91]\" \"channel_in_ip_d[92]\" \"channel_in_ip_d[93]\" \"channel_in_ip_d[94]\" \"channel_in_ip_d[95]\" \"channel_in_ip_d[96]\" \"channel_in_ip_d[97]\" \"channel_in_ip_d[98]\" \"channel_in_ip_d[99]\" \"channel_in_ip_d[100]\" \"channel_in_ip_d[101]\" \"channel_in_ip_d[102]\" \"channel_in_ip_d[103]\" \"channel_in_ip_d[104]\" \"channel_in_ip_d[105]\" \"channel_in_ip_d[106]\" \"channel_in_ip_d[107]\" \"channel_in_ip_d[108]\" \"channel_in_ip_d[109]\" \"channel_in_ip_d[110]\" \"channel_in_ip_d[111]\" \"channel_in_ip_d[112]\" \"channel_in_ip_d[113]\" \"channel_in_ip_d[114]\" \"channel_in_ip_d[115]\" \"channel_in_ip_d[116]\" \"channel_in_ip_d[117]\" \"channel_in_ip_d[118]\" \"channel_in_ip_d[119]\" \"channel_in_ip_d[120]\" \"channel_in_ip_d[121]\" \"channel_in_ip_d[122]\" \"channel_in_ip_d[123]\" \"channel_in_ip_d[124]\" \"channel_in_ip_d[125]\" \"channel_in_ip_d[126]\" \"channel_in_ip_d[127]\" \"channel_in_ip_d[128]\" \"channel_in_ip_d[129]\" \"channel_in_ip_d[130]\" \"channel_in_ip_d[131]\" \"channel_in_ip_d[132]\" \"channel_in_ip_d[133]\" \"channel_in_ip_d[134]\" \"channel_in_ip_d[135]\"}",
    #side 2
    "set my_2_ch_in_ports {\"channel_in_ip_d[136]\" \"channel_in_ip_d[137]\" \"channel_in_ip_d[138]\" \"channel_in_ip_d[139]\" \"channel_in_ip_d[140]\" \"channel_in_ip_d[141]\" \"channel_in_ip_d[142]\" \"channel_in_ip_d[143]\" \"channel_in_ip_d[144]\" \"channel_in_ip_d[145]\" \"channel_in_ip_d[146]\" \"channel_in_ip_d[147]\" \"channel_in_ip_d[148]\" \"channel_in_ip_d[149]\" \"channel_in_ip_d[150]\" \"channel_in_ip_d[151]\" \"channel_in_ip_d[152]\" \"channel_in_ip_d[153]\" \"channel_in_ip_d[154]\" \"channel_in_ip_d[155]\" \"channel_in_ip_d[156]\" \"channel_in_ip_d[157]\" \"channel_in_ip_d[158]\" \"channel_in_ip_d[159]\" \"channel_in_ip_d[160]\" \"channel_in_ip_d[161]\" \"channel_in_ip_d[162]\" \"channel_in_ip_d[163]\" \"channel_in_ip_d[164]\" \"channel_in_ip_d[165]\" \"channel_in_ip_d[166]\" \"channel_in_ip_d[167]\" \"channel_in_ip_d[168]\" \"channel_in_ip_d[169]\" \"channel_in_ip_d[170]\" \"channel_in_ip_d[171]\" \"channel_in_ip_d[172]\" \"channel_in_ip_d[173]\" \"channel_in_ip_d[174]\" \"channel_in_ip_d[175]\" \"channel_in_ip_d[176]\" \"channel_in_ip_d[177]\" \"channel_in_ip_d[178]\" \"channel_in_ip_d[179]\" \"channel_in_ip_d[180]\" \"channel_in_ip_d[181]\" \"channel_in_ip_d[182]\" \"channel_in_ip_d[183]\" \"channel_in_ip_d[184]\" \"channel_in_ip_d[185]\" \"channel_in_ip_d[186]\" \"channel_in_ip_d[187]\" \"channel_in_ip_d[188]\" \"channel_in_ip_d[189]\" \"channel_in_ip_d[190]\" \"channel_in_ip_d[191]\" \"channel_in_ip_d[192]\" \"channel_in_ip_d[193]\" \"channel_in_ip_d[194]\" \"channel_in_ip_d[195]\" \"channel_in_ip_d[196]\" \"channel_in_ip_d[197]\" \"channel_in_ip_d[198]\" \"channel_in_ip_d[199]\" \"channel_in_ip_d[200]\" \"channel_in_ip_d[201]\" \"channel_in_ip_d[202]\" \"channel_in_ip_d[203]\"}",
    #side 3 (68 + 68)
    "set my_3_ch_in_ports {\"channel_in_ip_d[204]\" \"channel_in_ip_d[205]\" \"channel_in_ip_d[206]\" \"channel_in_ip_d[207]\" \"channel_in_ip_d[208]\" \"channel_in_ip_d[209]\" \"channel_in_ip_d[210]\" \"channel_in_ip_d[211]\" \"channel_in_ip_d[212]\" \"channel_in_ip_d[213]\" \"channel_in_ip_d[214]\" \"channel_in_ip_d[215]\" \"channel_in_ip_d[216]\" \"channel_in_ip_d[217]\" \"channel_in_ip_d[218]\" \"channel_in_ip_d[219]\" \"channel_in_ip_d[220]\" \"channel_in_ip_d[221]\" \"channel_in_ip_d[222]\" \"channel_in_ip_d[223]\" \"channel_in_ip_d[224]\" \"channel_in_ip_d[225]\" \"channel_in_ip_d[226]\" \"channel_in_ip_d[227]\" \"channel_in_ip_d[228]\" \"channel_in_ip_d[229]\" \"channel_in_ip_d[230]\" \"channel_in_ip_d[231]\" \"channel_in_ip_d[232]\" \"channel_in_ip_d[233]\" \"channel_in_ip_d[234]\" \"channel_in_ip_d[235]\" \"channel_in_ip_d[236]\" \"channel_in_ip_d[237]\" \"channel_in_ip_d[238]\" \"channel_in_ip_d[239]\" \"channel_in_ip_d[240]\" \"channel_in_ip_d[241]\" \"channel_in_ip_d[242]\" \"channel_in_ip_d[243]\" \"channel_in_ip_d[244]\" \"channel_in_ip_d[245]\" \"channel_in_ip_d[246]\" \"channel_in_ip_d[247]\" \"channel_in_ip_d[248]\" \"channel_in_ip_d[249]\" \"channel_in_ip_d[250]\" \"channel_in_ip_d[251]\" \"channel_in_ip_d[252]\" \"channel_in_ip_d[253]\" \"channel_in_ip_d[254]\" \"channel_in_ip_d[255]\" \"channel_in_ip_d[256]\" \"channel_in_ip_d[257]\" \"channel_in_ip_d[258]\" \"channel_in_ip_d[259]\" \"channel_in_ip_d[260]\" \"channel_in_ip_d[261]\" \"channel_in_ip_d[262]\" \"channel_in_ip_d[263]\" \"channel_in_ip_d[264]\" \"channel_in_ip_d[265]\" \"channel_in_ip_d[266]\" \"channel_in_ip_d[267]\" \"channel_in_ip_d[268]\" \"channel_in_ip_d[269]\" \"channel_in_ip_d[270]\" \"channel_in_ip_d[271]\" \"channel_in_ip_d[272]\" \"channel_in_ip_d[273]\" \"channel_in_ip_d[274]\" \"channel_in_ip_d[275]\" \"channel_in_ip_d[276]\" \"channel_in_ip_d[277]\" \"channel_in_ip_d[278]\" \"channel_in_ip_d[279]\" \"channel_in_ip_d[280]\" \"channel_in_ip_d[281]\" \"channel_in_ip_d[282]\" \"channel_in_ip_d[283]\" \"channel_in_ip_d[284]\" \"channel_in_ip_d[285]\" \"channel_in_ip_d[286]\" \"channel_in_ip_d[287]\" \"channel_in_ip_d[288]\" \"channel_in_ip_d[289]\" \"channel_in_ip_d[290]\" \"channel_in_ip_d[291]\" \"channel_in_ip_d[292]\" \"channel_in_ip_d[293]\" \"channel_in_ip_d[294]\" \"channel_in_ip_d[295]\" \"channel_in_ip_d[296]\" \"channel_in_ip_d[297]\" \"channel_in_ip_d[298]\" \"channel_in_ip_d[299]\" \"channel_in_ip_d[300]\" \"channel_in_ip_d[301]\" \"channel_in_ip_d[302]\" \"channel_in_ip_d[303]\" \"channel_in_ip_d[304]\" \"channel_in_ip_d[305]\" \"channel_in_ip_d[306]\" \"channel_in_ip_d[307]\" \"channel_in_ip_d[308]\" \"channel_in_ip_d[309]\" \"channel_in_ip_d[310]\" \"channel_in_ip_d[311]\" \"channel_in_ip_d[312]\" \"channel_in_ip_d[313]\" \"channel_in_ip_d[314]\" \"channel_in_ip_d[315]\" \"channel_in_ip_d[316]\" \"channel_in_ip_d[317]\" \"channel_in_ip_d[318]\" \"channel_in_ip_d[319]\" \"channel_in_ip_d[320]\" \"channel_in_ip_d[321]\" \"channel_in_ip_d[322]\" \"channel_in_ip_d[323]\" \"channel_in_ip_d[324]\" \"channel_in_ip_d[325]\" \"channel_in_ip_d[326]\" \"channel_in_ip_d[327]\" \"channel_in_ip_d[328]\" \"channel_in_ip_d[329]\" \"channel_in_ip_d[330]\" \"channel_in_ip_d[331]\" \"channel_in_ip_d[332]\" \"channel_in_ip_d[333]\" \"channel_in_ip_d[334]\" \"channel_in_ip_d[335]\" \"channel_in_ip_d[336]\" \"channel_in_ip_d[337]\" \"channel_in_ip_d[338]\" \"channel_in_ip_d[339]\"}",
    #in ports for ctrl flow
    "set my_flow_ctrl_in_ports {\"flow_ctrl_out_ip_q[0]\" \"flow_ctrl_out_ip_q[1]\" \"flow_ctrl_out_ip_q[2]\" \"flow_ctrl_out_ip_q[3]\" \"flow_ctrl_out_ip_q[4]\" \"flow_ctrl_out_ip_q[5]\" \"flow_ctrl_out_ip_q[6]\" \"flow_ctrl_out_ip_q[7]\" \"flow_ctrl_out_ip_q[8]\" \"flow_ctrl_out_ip_q[9]\"}",

    #side 0
    "set my_0_ch_out_ports {\"channel_out_op_q[0]\" \"channel_out_op_q[1]\" \"channel_out_op_q[2]\" \"channel_out_op_q[3]\" \"channel_out_op_q[4]\" \"channel_out_op_q[5]\" \"channel_out_op_q[6]\" \"channel_out_op_q[7]\" \"channel_out_op_q[8]\" \"channel_out_op_q[9]\" \"channel_out_op_q[10]\" \"channel_out_op_q[11]\" \"channel_out_op_q[12]\" \"channel_out_op_q[13]\" \"channel_out_op_q[14]\" \"channel_out_op_q[15]\" \"channel_out_op_q[16]\" \"channel_out_op_q[17]\" \"channel_out_op_q[18]\" \"channel_out_op_q[19]\" \"channel_out_op_q[20]\" \"channel_out_op_q[21]\" \"channel_out_op_q[22]\" \"channel_out_op_q[23]\" \"channel_out_op_q[24]\" \"channel_out_op_q[25]\" \"channel_out_op_q[26]\" \"channel_out_op_q[27]\" \"channel_out_op_q[28]\" \"channel_out_op_q[29]\" \"channel_out_op_q[30]\" \"channel_out_op_q[31]\" \"channel_out_op_q[32]\" \"channel_out_op_q[33]\" \"channel_out_op_q[34]\" \"channel_out_op_q[35]\" \"channel_out_op_q[36]\" \"channel_out_op_q[37]\" \"channel_out_op_q[38]\" \"channel_out_op_q[39]\" \"channel_out_op_q[40]\" \"channel_out_op_q[41]\" \"channel_out_op_q[42]\" \"channel_out_op_q[43]\" \"channel_out_op_q[44]\" \"channel_out_op_q[45]\" \"channel_out_op_q[46]\" \"channel_out_op_q[47]\" \"channel_out_op_q[48]\" \"channel_out_op_q[49]\" \"channel_out_op_q[50]\" \"channel_out_op_q[51]\" \"channel_out_op_q[52]\" \"channel_out_op_q[53]\" \"channel_out_op_q[54]\" \"channel_out_op_q[55]\" \"channel_out_op_q[56]\" \"channel_out_op_q[57]\" \"channel_out_op_q[58]\" \"channel_out_op_q[59]\" \"channel_out_op_q[60]\" \"channel_out_op_q[61]\" \"channel_out_op_q[62]\" \"channel_out_op_q[63]\" \"channel_out_op_q[64]\" \"channel_out_op_q[65]\" \"channel_out_op_q[66]\" \"channel_out_op_q[67]\"}",
    #side 1
    "set my_1_ch_out_ports {\"channel_out_op_q[68]\" \"channel_out_op_q[69]\" \"channel_out_op_q[70]\" \"channel_out_op_q[71]\" \"channel_out_op_q[72]\" \"channel_out_op_q[73]\" \"channel_out_op_q[74]\" \"channel_out_op_q[75]\" \"channel_out_op_q[76]\" \"channel_out_op_q[77]\" \"channel_out_op_q[78]\" \"channel_out_op_q[79]\" \"channel_out_op_q[80]\" \"channel_out_op_q[81]\" \"channel_out_op_q[82]\" \"channel_out_op_q[83]\" \"channel_out_op_q[84]\" \"channel_out_op_q[85]\" \"channel_out_op_q[86]\" \"channel_out_op_q[87]\" \"channel_out_op_q[88]\" \"channel_out_op_q[89]\" \"channel_out_op_q[90]\" \"channel_out_op_q[91]\" \"channel_out_op_q[92]\" \"channel_out_op_q[93]\" \"channel_out_op_q[94]\" \"channel_out_op_q[95]\" \"channel_out_op_q[96]\" \"channel_out_op_q[97]\" \"channel_out_op_q[98]\" \"channel_out_op_q[99]\" \"channel_out_op_q[100]\" \"channel_out_op_q[101]\" \"channel_out_op_q[102]\" \"channel_out_op_q[103]\" \"channel_out_op_q[104]\" \"channel_out_op_q[105]\" \"channel_out_op_q[106]\" \"channel_out_op_q[107]\" \"channel_out_op_q[108]\" \"channel_out_op_q[109]\" \"channel_out_op_q[110]\" \"channel_out_op_q[111]\" \"channel_out_op_q[112]\" \"channel_out_op_q[113]\" \"channel_out_op_q[114]\" \"channel_out_op_q[115]\" \"channel_out_op_q[116]\" \"channel_out_op_q[117]\" \"channel_out_op_q[118]\" \"channel_out_op_q[119]\" \"channel_out_op_q[120]\" \"channel_out_op_q[121]\" \"channel_out_op_q[122]\" \"channel_out_op_q[123]\" \"channel_out_op_q[124]\" \"channel_out_op_q[125]\" \"channel_out_op_q[126]\" \"channel_out_op_q[127]\" \"channel_out_op_q[128]\" \"channel_out_op_q[129]\" \"channel_out_op_q[130]\" \"channel_out_op_q[131]\" \"channel_out_op_q[132]\" \"channel_out_op_q[133]\" \"channel_out_op_q[134]\" \"channel_out_op_q[135]\"}",
    #side 2
    "set my_2_ch_out_ports {\"channel_out_op_q[136]\" \"channel_out_op_q[137]\" \"channel_out_op_q[138]\" \"channel_out_op_q[139]\" \"channel_out_op_q[140]\" \"channel_out_op_q[141]\" \"channel_out_op_q[142]\" \"channel_out_op_q[143]\" \"channel_out_op_q[144]\" \"channel_out_op_q[145]\" \"channel_out_op_q[146]\" \"channel_out_op_q[147]\" \"channel_out_op_q[148]\" \"channel_out_op_q[149]\" \"channel_out_op_q[150]\" \"channel_out_op_q[151]\" \"channel_out_op_q[152]\" \"channel_out_op_q[153]\" \"channel_out_op_q[154]\" \"channel_out_op_q[155]\" \"channel_out_op_q[156]\" \"channel_out_op_q[157]\" \"channel_out_op_q[158]\" \"channel_out_op_q[159]\" \"channel_out_op_q[160]\" \"channel_out_op_q[161]\" \"channel_out_op_q[162]\" \"channel_out_op_q[163]\" \"channel_out_op_q[164]\" \"channel_out_op_q[165]\" \"channel_out_op_q[166]\" \"channel_out_op_q[167]\" \"channel_out_op_q[168]\" \"channel_out_op_q[169]\" \"channel_out_op_q[170]\" \"channel_out_op_q[171]\" \"channel_out_op_q[172]\" \"channel_out_op_q[173]\" \"channel_out_op_q[174]\" \"channel_out_op_q[175]\" \"channel_out_op_q[176]\" \"channel_out_op_q[177]\" \"channel_out_op_q[178]\" \"channel_out_op_q[179]\" \"channel_out_op_q[180]\" \"channel_out_op_q[181]\" \"channel_out_op_q[182]\" \"channel_out_op_q[183]\" \"channel_out_op_q[184]\" \"channel_out_op_q[185]\" \"channel_out_op_q[186]\" \"channel_out_op_q[187]\" \"channel_out_op_q[188]\" \"channel_out_op_q[189]\" \"channel_out_op_q[190]\" \"channel_out_op_q[191]\" \"channel_out_op_q[192]\" \"channel_out_op_q[193]\" \"channel_out_op_q[194]\" \"channel_out_op_q[195]\" \"channel_out_op_q[196]\" \"channel_out_op_q[197]\" \"channel_out_op_q[198]\" \"channel_out_op_q[199]\" \"channel_out_op_q[200]\" \"channel_out_op_q[201]\" \"channel_out_op_q[202]\" \"channel_out_op_q[203]\"}",
    #side 3 (68 + 68)
    "set my_3_ch_out_ports {\"channel_out_op_q[204]\" \"channel_out_op_q[205]\" \"channel_out_op_q[206]\" \"channel_out_op_q[207]\" \"channel_out_op_q[208]\" \"channel_out_op_q[209]\" \"channel_out_op_q[210]\" \"channel_out_op_q[211]\" \"channel_out_op_q[212]\" \"channel_out_op_q[213]\" \"channel_out_op_q[214]\" \"channel_out_op_q[215]\" \"channel_out_op_q[216]\" \"channel_out_op_q[217]\" \"channel_out_op_q[218]\" \"channel_out_op_q[219]\" \"channel_out_op_q[220]\" \"channel_out_op_q[221]\" \"channel_out_op_q[222]\" \"channel_out_op_q[223]\" \"channel_out_op_q[224]\" \"channel_out_op_q[225]\" \"channel_out_op_q[226]\" \"channel_out_op_q[227]\" \"channel_out_op_q[228]\" \"channel_out_op_q[229]\" \"channel_out_op_q[230]\" \"channel_out_op_q[231]\" \"channel_out_op_q[232]\" \"channel_out_op_q[233]\" \"channel_out_op_q[234]\" \"channel_out_op_q[235]\" \"channel_out_op_q[236]\" \"channel_out_op_q[237]\" \"channel_out_op_q[238]\" \"channel_out_op_q[239]\" \"channel_out_op_q[240]\" \"channel_out_op_q[241]\" \"channel_out_op_q[242]\" \"channel_out_op_q[243]\" \"channel_out_op_q[244]\" \"channel_out_op_q[245]\" \"channel_out_op_q[246]\" \"channel_out_op_q[247]\" \"channel_out_op_q[248]\" \"channel_out_op_q[249]\" \"channel_out_op_q[250]\" \"channel_out_op_q[251]\" \"channel_out_op_q[252]\" \"channel_out_op_q[253]\" \"channel_out_op_q[254]\" \"channel_out_op_q[255]\" \"channel_out_op_q[256]\" \"channel_out_op_q[257]\" \"channel_out_op_q[258]\" \"channel_out_op_q[259]\" \"channel_out_op_q[260]\" \"channel_out_op_q[261]\" \"channel_out_op_q[262]\" \"channel_out_op_q[263]\" \"channel_out_op_q[264]\" \"channel_out_op_q[265]\" \"channel_out_op_q[266]\" \"channel_out_op_q[267]\" \"channel_out_op_q[268]\" \"channel_out_op_q[269]\" \"channel_out_op_q[270]\" \"channel_out_op_q[271]\" \"channel_out_op_q[272]\" \"channel_out_op_q[273]\" \"channel_out_op_q[274]\" \"channel_out_op_q[275]\" \"channel_out_op_q[276]\" \"channel_out_op_q[277]\" \"channel_out_op_q[278]\" \"channel_out_op_q[279]\" \"channel_out_op_q[280]\" \"channel_out_op_q[281]\" \"channel_out_op_q[282]\" \"channel_out_op_q[283]\" \"channel_out_op_q[284]\" \"channel_out_op_q[285]\" \"channel_out_op_q[286]\" \"channel_out_op_q[287]\" \"channel_out_op_q[288]\" \"channel_out_op_q[289]\" \"channel_out_op_q[290]\" \"channel_out_op_q[291]\" \"channel_out_op_q[292]\" \"channel_out_op_q[293]\" \"channel_out_op_q[294]\" \"channel_out_op_q[295]\" \"channel_out_op_q[296]\" \"channel_out_op_q[297]\" \"channel_out_op_q[298]\" \"channel_out_op_q[299]\" \"channel_out_op_q[300]\" \"channel_out_op_q[301]\" \"channel_out_op_q[302]\" \"channel_out_op_q[303]\" \"channel_out_op_q[304]\" \"channel_out_op_q[305]\" \"channel_out_op_q[306]\" \"channel_out_op_q[307]\" \"channel_out_op_q[308]\" \"channel_out_op_q[309]\" \"channel_out_op_q[310]\" \"channel_out_op_q[311]\" \"channel_out_op_q[312]\" \"channel_out_op_q[313]\" \"channel_out_op_q[314]\" \"channel_out_op_q[315]\" \"channel_out_op_q[316]\" \"channel_out_op_q[317]\" \"channel_out_op_q[318]\" \"channel_out_op_q[319]\" \"channel_out_op_q[320]\" \"channel_out_op_q[321]\" \"channel_out_op_q[322]\" \"channel_out_op_q[323]\" \"channel_out_op_q[324]\" \"channel_out_op_q[325]\" \"channel_out_op_q[326]\" \"channel_out_op_q[327]\" \"channel_out_op_q[328]\" \"channel_out_op_q[329]\" \"channel_out_op_q[330]\" \"channel_out_op_q[331]\" \"channel_out_op_q[332]\" \"channel_out_op_q[333]\" \"channel_out_op_q[334]\" \"channel_out_op_q[335]\" \"channel_out_op_q[336]\" \"channel_out_op_q[337]\" \"channel_out_op_q[338]\" \"channel_out_op_q[339]\"}",
    #out ports for ctrl flow
    "set my_flow_ctrl_out_ports {\"flow_ctrl_in_op_d[0]\" \"flow_ctrl_in_op_d[1]\" \"flow_ctrl_in_op_d[2]\" \"flow_ctrl_in_op_d[3]\" \"flow_ctrl_in_op_d[4]\" \"flow_ctrl_in_op_d[5]\" \"flow_ctrl_in_op_d[6]\" \"flow_ctrl_in_op_d[7]\" \"flow_ctrl_in_op_d[8]\" \"flow_ctrl_in_op_d[9]\"}",
    
    #gen i/o s these can be assigned pretty much anywhere (can be left to the tool)
    # \"flow_ctrl_out_ip_q[0]\" \"flow_ctrl_out_ip_q[1]\" \"flow_ctrl_out_ip_q[2]\" \"flow_ctrl_out_ip_q[3]\" \"flow_ctrl_out_ip_q[4]\" \"flow_ctrl_out_ip_q[5]\" \"flow_ctrl_out_ip_q[6]\" \"flow_ctrl_out_ip_q[7]\" \"flow_ctrl_out_ip_q[8]\" \"flow_ctrl_out_ip_q[9]\" \"flow_ctrl_in_op_d[0]\" \"flow_ctrl_in_op_d[1]\" \"flow_ctrl_in_op_d[2]\" \"flow_ctrl_in_op_d[3]\" \"flow_ctrl_in_op_d[4]\" \"flow_ctrl_in_op_d[5]\" \"flow_ctrl_in_op_d[6]\" \"flow_ctrl_in_op_d[7]\" \"flow_ctrl_in_op_d[8]\" \"flow_ctrl_in_op_d[9]\"
    "set my_gen_pins {\"clk\" \"reset\" \"router_address[0]\" \"router_address[1]\" \"router_address[2]\" \"router_address[3]\" \"router_address[4]\" \"router_address[5]\" \"flow_ctrl_out_ip_q[0]\" \"flow_ctrl_out_ip_q[1]\" \"flow_ctrl_out_ip_q[2]\" \"flow_ctrl_out_ip_q[3]\" \"flow_ctrl_out_ip_q[4]\" \"flow_ctrl_out_ip_q[5]\" \"flow_ctrl_out_ip_q[6]\" \"flow_ctrl_out_ip_q[7]\" \"flow_ctrl_out_ip_q[8]\" \"flow_ctrl_out_ip_q[9]\" \"flow_ctrl_in_op_d[0]\" \"flow_ctrl_in_op_d[1]\" \"flow_ctrl_in_op_d[2]\" \"flow_ctrl_in_op_d[3]\" \"flow_ctrl_in_op_d[4]\" \"flow_ctrl_in_op_d[5]\" \"flow_ctrl_in_op_d[6]\" \"flow_ctrl_in_op_d[7]\" \"flow_ctrl_in_op_d[8]\" \"flow_ctrl_in_op_d[9]\" \"error\"}",
    #assign pin locations
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 0 -layer 3 -spreadType start -spacing " + flow_settings["ptn_params"]["fp_pin_spacing"] + " -offsetStart " + str(ch_in_offset) + " -pin $my_0_ch_in_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 1 -layer 4 -spreadType start -spacing "+ flow_settings["ptn_params"]["fp_pin_spacing"] + " -offsetStart " + str(ch_in_offset) + " -pin $my_1_ch_in_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 2 -layer 3 -spreadType start -spacing "+ flow_settings["ptn_params"]["fp_pin_spacing"] + " -offsetStart " + str(ch_in_offset) + " -pin $my_2_ch_in_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 3 -layer 4 -spreadType start -spacing "+ flow_settings["ptn_params"]["fp_pin_spacing"] + " -offsetStart " + str(noc_comm_edge_offsets[0]) + " -pin $my_3_ch_in_ports",
    "",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 0 -layer 3 -spreadType start -spacing "+ flow_settings["ptn_params"]["fp_pin_spacing"] + " -offsetStart " + str(ch_out_offset) + " -pin $my_0_ch_out_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 1 -layer 4 -spreadType start -spacing "+ flow_settings["ptn_params"]["fp_pin_spacing"] + " -offsetStart " + str(ch_out_offset) + " -pin $my_1_ch_out_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 2 -layer 3 -spreadType start -spacing "+ flow_settings["ptn_params"]["fp_pin_spacing"] + " -offsetStart " + str(ch_out_offset) + " -pin $my_2_ch_out_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 3 -layer 4 -spreadType start -spacing "+ flow_settings["ptn_params"]["fp_pin_spacing"] + " -offsetStart " + str(noc_comm_edge_offsets[1]) + " -pin $my_3_ch_out_ports",
    "",
    #Previously used pin settings (caused too much congestion/DRC errors)
    # "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 0 -layer 3 -spreadType start -spacing 1 -offsetStart 50 -pin $my_0_ch_in_ports",
    # "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 1 -layer 4 -spreadType start -spacing 1 -offsetStart 50 -pin $my_1_ch_in_ports",
    # "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 2 -layer 3 -spreadType start -spacing 1 -offsetStart 50 -pin $my_2_ch_in_ports",
    # "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 3 -layer 4 -spreadType start -spacing 1 -offsetStart 50 -pin $my_3_ch_in_ports",
    # "",
    # "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 0 -layer 3 -spreadType start -spacing 1 -offsetStart 78 -pin $my_0_ch_out_ports",
    # "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 1 -layer 4 -spreadType start -spacing 1 -offsetStart 78 -pin $my_1_ch_out_ports",
    # "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 2 -layer 3 -spreadType start -spacing 1 -offsetStart 78 -pin $my_2_ch_out_ports",
    # "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 3 -layer 4 -spreadType start -spacing 1 -offsetStart 100 -pin $my_3_ch_out_ports",

    "legalizePin"
  ]
  for line in file_lines:
    file_write_ln(fd,line)
  fd.close()
  return ch_in_offset, ch_out_offset


def write_innovus_fp_script(flow_settings,metal_layer,init_script_fname,fp_dims):
  """
  This generates the lines for a script which can generate a floorplan for a design, this must be done prior to creating partitions.
  The fp_dims parameter is a list of floorplan dimensions for the width and height of floorplan
  """
  output_path = os.path.join("..","outputs")
  script_path = os.path.join("..","scripts")
  output_path = os.path.abspath(output_path)
  script_path = os.path.abspath(script_path)

  #new file for every dimension
  fp_script_fname = flow_settings["top_level"] + "_dimlen_" + str(fp_dims[0]) + "_innovus_fp_gen.tcl"
  #new floorplan for every dimension
  fp_save_file = "_".join([flow_settings["top_level"],"dimlen",str(fp_dims[0])+".fp"])
  metal_layer_bottom = flow_settings["metal_layer_names"][0]
  metal_layer_second = flow_settings["metal_layer_names"][1]
  metal_layer_top = flow_settings["metal_layer_names"][int(metal_layer)-1]

  file_lines = [
    "source " + init_script_fname,
    
    # New static dimension fplan cmd
    "floorPlan -site " +
      " ".join([flow_settings["core_site_name"],
      "-s", 
      " ".join(["{",
        str(fp_dims[0]),
        str(fp_dims[1]),
        flow_settings["space_around_core"],
        flow_settings["space_around_core"],
        flow_settings["space_around_core"],
        flow_settings["space_around_core"],
        "}"])
      ]),
    "setDesignMode -topRoutingLayer " + metal_layer,
    "fit",
    " ".join(["addRing", "-type core_rings","-nets","{" + " ".join([flow_settings["pwr_net"],flow_settings["gnd_net"]]) + "}",
      "-layer {" + " ".join(["top",metal_layer_bottom,"bottom",metal_layer_bottom,"left",metal_layer_second,"right",metal_layer_second]) + "}",
      "-width", flow_settings["power_ring_width"],
      "-spacing", flow_settings["power_ring_spacing"],
      "-offset", flow_settings["power_ring_width"],
      "-follow io"]),
    "set sprCreateIeRingOffset 1.0",
    "set sprCreateIeRingLayers {}",
    "set sprCreateIeStripeWidth " + flow_settings["space_around_core"],
    "set sprCreateIeStripeThreshold 1.0",
    #TODO keep the width and spacing settings of noc settings file constant while running length tests, change the below lines for parameterization later.
    "setAddStripeMode -ignore_block_check false -break_at none -route_over_rows_only false -rows_without_stripes_only false -extend_to_closest_target none -stop_at_last_wire_for_area false -partial_set_thru_domain false -ignore_nondefault_domains false -trim_antenna_back_to_shape none -spacing_type edge_to_edge -spacing_from_block 0 -stripe_min_length stripe_width -stacked_via_top_layer AP -stacked_via_bottom_layer M1 -via_using_exact_crossover_size false -split_vias false -orthogonal_only true -allow_jog { padcore_ring  block_ring } -skip_via_on_pin {  standardcell } -skip_via_on_wire_shape {  noshape   }",
    "addStripe -nets {VDD VSS} -layer M2 -direction vertical -width 1.8 -spacing 1.8 -set_to_set_distance 50 -start_from left -start_offset 50 -switch_layer_over_obs false -max_same_layer_jog_length 2 -padcore_ring_top_layer_limit AP -padcore_ring_bottom_layer_limit M1 -block_ring_top_layer_limit AP -block_ring_bottom_layer_limit M1 -use_wire_group 0 -snap_wire_center_to_grid None",
    #"clearGlobalNets", #Pretty sure we don't need this but leaving it in case
    "globalNetConnect " + flow_settings["gnd_pin"] + " -type pgpin -pin " + flow_settings["gnd_pin"] + " -inst {}",
    "globalNetConnect " + flow_settings["pwr_pin"] + " -type pgpin -pin " + flow_settings["pwr_pin"] + " -inst {}",
    "globalNetConnect " + flow_settings["gnd_net"] + " -type net -net  " + flow_settings["gnd_net"],
    "globalNetConnect " + flow_settings["pwr_net"] + " -type net -net  " + flow_settings["pwr_net"],
    "globalNetConnect " + flow_settings["pwr_pin"] + " -type pgpin -pin  " + flow_settings["pwr_pin"] + " -inst *",
    "globalNetConnect " + flow_settings["gnd_pin"] + " -type pgpin -pin  " + flow_settings["gnd_pin"] + " -inst *",
    "globalNetConnect " + flow_settings["pwr_pin"] + " -type tiehi -inst *",
    "globalNetConnect " + flow_settings["gnd_pin"] + " -type tielo -inst *",
    "sroute -connect { blockPin padPin padRing corePin floatingStripe } -layerChangeRange { "+ " ".join([metal_layer_bottom,metal_layer_top]) + " }"\
     + " -blockPinTarget { nearestRingStripe nearestTarget } -padPinPortConnect { allPort oneGeom } -checkAlignedSecondaryPin 1 -blockPin useLef -allowJogging 1"\
     + " -crossoverViaBottomLayer " + metal_layer_bottom + " -targetViaBottomLayer " + metal_layer_bottom + " -allowLayerChange 1"\
     + " -targetViaTopLayer " + metal_layer_top + " -crossoverViaTopLayer " + metal_layer_top + " -nets {" + " ".join([flow_settings["gnd_net"],flow_settings["pwr_net"]]) +  "}",
    #Placement needs to be performed to place IO pins... 
    "setPlaceMode -fp false -place_global_place_io_pins true",
    "place_design -noPrePlaceOpt",
    "earlyGlobalRoute",
    # Assign port locations
    "source " + os.path.join(script_path,"port_vars.tcl"),
    "saveFPlan " + os.path.join(output_path,fp_save_file)
  ]
  fd = open(fp_script_fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"exit")
  fd.close()
  return fp_script_fname, os.path.join(output_path,fp_save_file)

# Commented function extracts all information from pins which would be useful for partition locations, but adding in the flow requires
# innovus to be run before all scripts can be generated, not a big change but would just have to consider that and one couldn't run parallel fp flow as it is

# def write_innovus_info_extract_script(flow_settings):
#   file_lines = [
#     "setDbGetMode -displayLimit 1000000",
#     "dbGet top.terms.?? > ../outputs/pin_info.txt",
#   ]
#   fname = "innovus_pin_info_extract.tcl"
#   fd = open(fname,"w")
#   for line in file_lines:
#     file_write_ln(fd,file_lines)
#   fd.close()
#   return fname

def write_innovus_ptn_script(flow_settings,init_script_fname,fp_save_file,offsets,dim_pair,auto_assign_regs=False):
  """
  Writes script to partition a design, uses ptn_info_list extracted from parameter file to define partition locations, has the option to auto assign register partitions but option has not been 
  extended to support unique params.
  """
  
  ptn_info_list = flow_settings["ptn_params"]["ptn_list"]
  #
  report_path = os.path.join("..","reports")
  output_path = os.path.join("..","outputs")
  report_path = os.path.abspath(report_path)
  output_path = os.path.abspath(output_path)
  

  if(auto_assign_regs):
    #offsets[0] is channel_in [1] is channel out
    ff_const_offset = 1.0 #ff offset from pin offsets
    ff_depth_from_pins = 20.0
    ff_width = 68.0 #w.r.t the pins
    ff_height = 12.0 #w.r.t the pins
    fp_dims_error_margin = 0.005
    
    #This is a bit of a hack as to really find the width of a grouping of pins we need to access innovus and it would be annoying to make the script generation execution dependant again
    #Actually realized I can properly estimate the width by looking at the beginning and end of pin offsets
    for ptn in ptn_info_list:
      if("ff" in ptn["inst_name"]): #TODO fix -> design specific
        #The bounds will be found automatically to match pin locations
        #filter out which channel corresponds to ports, again this is going to be hacky
        # 1 in inst name corresponds to edge 1
        if("1" in ptn["inst_name"]):
          #North side connections
          if("in" in ptn["inst_name"]):
            ptn["fp_coords"][0] = offsets[0] - ff_const_offset #lc x 
            ptn["fp_coords"][1] = dim_pair[1] - ff_depth_from_pins - ff_height #lc y
            ptn["fp_coords"][2] = offsets[0] + ff_width + ff_const_offset #uc x 
            ptn["fp_coords"][3] = dim_pair[1] - ff_depth_from_pins #uc y
          elif("out" in ptn["inst_name"]):
            ptn["fp_coords"][0] = offsets[1] - ff_const_offset #lc x 
            ptn["fp_coords"][1] = dim_pair[1] - ff_depth_from_pins - ff_height #lc y
            ptn["fp_coords"][2] = offsets[1] + ff_width + ff_const_offset#uc x 
            ptn["fp_coords"][3] = dim_pair[1] - ff_depth_from_pins #uc y
        elif("2" in ptn["inst_name"]):
          if("in" in ptn["inst_name"]):
            #East side connections
            ptn["fp_coords"][0] = dim_pair[0] - ff_depth_from_pins - ff_height #lc x 
            ptn["fp_coords"][1] = offsets[0] - ff_const_offset #lc y
            ptn["fp_coords"][2] = dim_pair[0] - ff_depth_from_pins #uc y
            ptn["fp_coords"][3] = offsets[0] + ff_width + ff_const_offset
          elif("out" in ptn["inst_name"]):
            ptn["fp_coords"][0] = dim_pair[0] - ff_depth_from_pins - ff_height #lc x 
            ptn["fp_coords"][1] = offsets[1] - ff_const_offset #lc y
            ptn["fp_coords"][2] = dim_pair[0] - ff_depth_from_pins #uc y
            ptn["fp_coords"][3] = offsets[1] + ff_width + ff_const_offset

      
  #load in partition floorplan boundaries
  obj_fplan_box_cmds = [" ".join(["setObjFPlanBox","Module",ptn["inst_name"]," ".join([str(coord) for coord in ptn["fp_coords"]])]) for ptn in ptn_info_list]
  #define partitions
  def_ptn_cmds = [" ".join(["definePartition","-hinst",ptn["inst_name"],"-coreSpacing 0.0 0.0 0.0 0.0 -railWidth 0.0 -minPitchLeft 2 -minPitchRight 2 -minPitchTop 2 -minPitchBottom 2 -reservedLayer { 1 2 3 4 5 6 7 8 9 10} -pinLayerTop { 2 4 6 8 10} -pinLayerLeft { 3 5 7 9} -pinLayerBottom { 2 4 6 8 10} -pinLayerRight { 3 5 7 9} -placementHalo 0.0 0.0 0.0 0.0 -routingHalo 0.0 -routingHaloTopLayer 10 -routingHaloBottomLayer 1"]) for ptn in ptn_info_list]
  ptn_script_fname = os.path.splitext(os.path.basename(fp_save_file))[0] + "_ptn" + ".tcl"
  post_partition_fplan = "_".join([os.path.splitext(fp_save_file)[0],"post_ptn.fp"])

  file_lines = [
    " ".join(["source",init_script_fname]),
    "loadFPlan " + fp_save_file,
    obj_fplan_box_cmds,
    def_ptn_cmds,
    #Tutorial says that one should save the floorplan after the partition is defined, not sure why maybe will have to add SaveFP command here
    "saveFPlan " + os.path.join(output_path,post_partition_fplan),
    "setPlaceMode -place_hard_fence true",
    "setOptMode -honorFence true",
    "place_opt_design",
    "assignPtnPin",
    "setBudgetingMode -virtualOptEngine gigaOpt",
    "setBudgetingMode -constantModel true",
    "setBudgetingMode -includeLatency true",
    "deriveTimingBudget",
    #commits partition
    "partition",
    "savePartition -dir " + os.path.splitext(os.path.basename(fp_save_file))[0] + "_ptn" + " -def"
  ]
  #this command flattens heterogenous lists Ex ["hello", ["billy","bob"],[["johnson"]]] -> ["hello", "billy","bob","johnson"]
  flat_list = lambda file_lines:[element for item in file_lines for element in flat_list(item)] if type(file_lines) is list else [file_lines]
  file_lines = flat_list(file_lines)
  fd = open(ptn_script_fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"exit")
  fd.close()
  return ptn_script_fname

def write_innovus_ptn_block_flow(metal_layer,ptn_dir_name,block_name):
  """
  After parititioning, we need to run placement and routing for each new partition created as well as the top level, This function generates the 
  script to run block specific pnr flow, partitions must be created at this point with subdirectories for each block
  """ 
  file_lines = [
    "cd " + os.path.join("..","work",ptn_dir_name,block_name),
    " ".join(["source", block_name + ".globals"]),
    "init_design",
    "loadFPlan " + block_name + ".fp.gz",
    "place_opt_design",
    "extractRC",
    "timeDesign -preCTS -pathReports -drvReports -slackReports -numPaths 50 -prefix " + block_name + "_preCTS -outDir timingReports",
    "create_ccopt_clock_tree_spec",
    "ccopt_design",
    "optDesign -postCTS",
    "setNanoRouteMode -quiet -routeWithTimingDriven 1",
    "setNanoRouteMode -quiet -routeWithSiDriven 1",
    "setNanoRouteMode -quiet -routeTopRoutingLayer " + str(metal_layer),
    "setNanoRouteMode -quiet -routeBottomRoutingLayer 1",
    "setNanoRouteMode -quiet -drouteEndIteration 1",
    "setNanoRouteMode -quiet -routeWithTimingDriven true",
    "setNanoRouteMode -quiet -routeWithSiDriven true",
    "routeDesign -globalDetail",
    "setAnalysisMode -analysisType onChipVariation -cppr both",
    "optDesign -postRoute",
    #put a check in place to make sure the above optimization actually results in timing passing
    "timeDesign -postRoute -pathReports -drvReports -slackReports -numPaths 50 -prefix " +  block_name + "_postRoute -outDir timingReports",
    "saveDesign " + block_name + "_imp",
  ]
  block_ptn_flow_script_fname = ptn_dir_name + "_" + block_name + "_block_flow.tcl"
  fd = open(block_ptn_flow_script_fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"exit")
  fd.close()

def write_innovus_ptn_top_level_flow(metal_layer,ptn_dir_name,top_level_name):
  """
  This script runs partitioning for the top level module containing the sub blocks, the sub block partitions must have gone through pnr before this point.
  """ 
  file_lines = [
    "cd " + os.path.join("..","work",ptn_dir_name,top_level_name),
    " ".join(["source", top_level_name + ".globals"]),
    "init_design",
    "defIn " + top_level_name + ".def.gz",
    "create_ccopt_clock_tree_spec",
    "ccopt_design",
    "optDesign -postCTS",
    "setNanoRouteMode -quiet -routeWithTimingDriven 1",
    "setNanoRouteMode -quiet -routeWithSiDriven 1",
    "setNanoRouteMode -quiet -routeTopRoutingLayer " + str(metal_layer),
    "setNanoRouteMode -quiet -routeBottomRoutingLayer 1",
    "setNanoRouteMode -quiet -drouteEndIteration 1",
    "setNanoRouteMode -quiet -routeWithTimingDriven true",
    "setNanoRouteMode -quiet -routeWithSiDriven true",
    "routeDesign -globalDetail",
    "setAnalysisMode -analysisType onChipVariation -cppr both",
    "optDesign -postRoute",
    "timeDesign -postRoute -pathReports -drvReports -slackReports -numPaths 50 -prefix " + top_level_name + " -outDir timingReports",
    "saveDesign " + top_level_name + "_imp",
  ]
  toplvl_ptn_flow_script_fname = ptn_dir_name + "_toplvl_flow.tcl"
  fd = open(toplvl_ptn_flow_script_fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"exit")
  fd.close()

def write_innovus_assemble_script(flow_settings,ptn_dir_name,block_list,top_level_name):
  """
  Once all previous partition pnr stages have been completed, we can assemble the design, optimize it and get timing results for the hierarchical design.
  """
  report_path = os.path.join("..","reports")
  output_path = os.path.join("..","outputs")
  report_path = os.path.abspath(report_path)
  output_path = os.path.abspath(output_path)
  assem_blk_str_list = ["-blockDir " + os.path.join(ptn_dir_name,block_name,block_name + "_imp.dat") for block_name in block_list]
  assem_blk_str = " " + " ".join(assem_blk_str_list) + " "
  file_lines = [ 
    "assembleDesign -topDir " + os.path.join(ptn_dir_name,top_level_name,top_level_name+"_imp.dat") +
     assem_blk_str +
     #os.path.join(ptn_dir_name,block_name,block_name + "_imp.dat") + 
     " -fe -mmmcFile " + os.path.join("..","scripts",flow_settings["top_level"]+".view"),
    "setAnalysisMode -analysisType onChipVariation -cppr both",
    "optDesign -postRoute",
    #-setup -postRoute",
    #"optDesign -hold -postRoute",
    #"optDesign -drv -postRoute",
    "timeDesign -postRoute -prefix assembled -outDir " + os.path.join(report_path,ptn_dir_name,"timingReports"),
    "verify_drc -report " + os.path.join(report_path, ptn_dir_name,"geom.rpt"),
    "verifyConnectivity -type all -report " + os.path.join(report_path,ptn_dir_name, "conn.rpt"),
    "report_timing > " + os.path.join(report_path,ptn_dir_name, "setup_timing.rpt"),
    "setAnalysisMode -checkType hold",
    "report_timing > " + os.path.join(report_path,ptn_dir_name, "hold_timing.rpt"),
    "report_power > " + os.path.join(report_path,ptn_dir_name, "power.rpt"),
    "report_constraint -all_violators > " + os.path.join(report_path,ptn_dir_name, "violators.rpt"),
    "report_area > " + os.path.join(report_path,ptn_dir_name, "area.rpt"),
    "summaryReport -outFile " + os.path.join(report_path,ptn_dir_name, "pr_report.txt"),
    "saveDesign " + os.path.join(output_path,ptn_dir_name + "_assembled")
  ]
  assemble_ptn_flow_script_fname = ptn_dir_name + "_assembly_flow.tcl"
  fd = open(assemble_ptn_flow_script_fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"exit")
  fd.close()  
  return ptn_dir_name,os.path.abspath(report_path),os.path.abspath(output_path)


def write_innovus_script(flow_settings,metal_layer,core_utilization,init_script_fname,rel_outputs=False,cts_flag=False):
  """
  This function writes the innvous script which actually performs place and route.
  Precondition to this script is the creation of an initialization script which is sourced on the first line.
  """

  report_path = flow_settings['pr_folder'] if (not rel_outputs) else os.path.join("..","reports")
  output_path = flow_settings['pr_folder'] if (not rel_outputs) else os.path.join("..","outputs")
  
  report_path = os.path.abspath(report_path)
  output_path = os.path.abspath(output_path)

  #some format adjustment (could move to preproc function)
  core_utilization = str(core_utilization)
  metal_layer = str(metal_layer)
  flow_settings["power_ring_spacing"] = str(flow_settings["power_ring_spacing"])

  #filename
  fname = flow_settings["top_level"] + "_innovus.tcl"
  
  #cts commands
  if cts_flag: 
    cts_cmds = [
      "create_ccopt_clock_tree_spec",
      "ccopt_design",
      "timeDesign -postCTS -prefix postCTSpreOpt -outDir " + os.path.join(report_path,"timeDesignPostCTSReports"),
      "optDesign -postCTS -prefix postCTSOpt -outDir " + os.path.join(report_path,"optDesignPostCTSReports"),
      "timeDesign -postCTS -prefix postCTSpostOpt -outDir " + os.path.join(report_path,"timeDesignPostCTSReports")
    ]
  else:
    cts_cmds = ["#CTS NOT PERFORMED"]
  
  #If the user specified a layer mapping file, then use that. Otherwise, just let the tool create a default one.
  if flow_settings['map_file'] != "None":
    stream_out_cmd = "streamOut " +  os.path.join(output_path,"final.gds2") + " -mapFile " + flow_settings["map_file"] + " -stripes 1 -units 1000 -mode ALL"
  else:
    stream_out_cmd = "streamOut " +  os.path.join(output_path,"final.gds2") + " -stripes 1 -units 1000 -mode ALL"

  metal_layer_bottom = flow_settings["metal_layer_names"][0]
  metal_layer_second = flow_settings["metal_layer_names"][1]
  metal_layer_top = flow_settings["metal_layer_names"][int(metal_layer)-1]
  power_ring_metal_top = flow_settings["power_ring_metal_layer_names"][0] 
  power_ring_metal_bottom = flow_settings["power_ring_metal_layer_names"][1] 
  power_ring_metal_left = flow_settings["power_ring_metal_layer_names"][2] 
  power_ring_metal_right = flow_settings["power_ring_metal_layer_names"][3] 


  file_lines = [
    "source " + init_script_fname,
    "setDesignMode -process " + flow_settings["process_size"],
    "floorPlan -site " +
    " ".join([flow_settings["core_site_name"],
    "-r",flow_settings["height_to_width_ratio"],core_utilization,
    flow_settings["space_around_core"],
    flow_settings["space_around_core"],
    flow_settings["space_around_core"],
    flow_settings["space_around_core"]]),
    "setDesignMode -topRoutingLayer " + metal_layer,
    "fit",
    #Add Power Rings
    " ".join(["addRing", "-type core_rings","-nets","{" + " ".join([flow_settings["pwr_net"],flow_settings["gnd_net"]]) + "}",
      "-layer {" + " ".join(["top",metal_layer_bottom,"bottom",metal_layer_bottom,"left",metal_layer_second,"right",metal_layer_second]) + "}",
      "-width", flow_settings["power_ring_width"],
      "-spacing", flow_settings["power_ring_spacing"],
      "-offset", flow_settings["power_ring_width"],
      "-follow io"]),
    #Global net connections
    "clearGlobalNets",
    "globalNetConnect " + flow_settings["gnd_pin"] + " -type pgpin -pin " + flow_settings["gnd_pin"] + " -inst {}",
    "globalNetConnect " + flow_settings["pwr_pin"] + " -type pgpin -pin " + flow_settings["pwr_pin"] + " -inst {}",
    "globalNetConnect " + flow_settings["gnd_net"] + " -type net -net  " + flow_settings["gnd_net"],
    "globalNetConnect " + flow_settings["pwr_net"] + " -type net -net  " + flow_settings["pwr_net"],
    "globalNetConnect " + flow_settings["pwr_pin"] + " -type pgpin -pin  " + flow_settings["pwr_pin"] + " -inst *",
    "globalNetConnect " + flow_settings["gnd_pin"] + " -type pgpin -pin  " + flow_settings["gnd_pin"] + " -inst *",
    "globalNetConnect " + flow_settings["pwr_pin"] + " -type tiehi -inst *",
    "globalNetConnect " + flow_settings["gnd_pin"] + " -type tielo -inst *",
    #special routing for horizontal VDD VSS connections
    "sroute -connect { blockPin padPin padRing corePin floatingStripe } -layerChangeRange { "+ " ".join([metal_layer_bottom,metal_layer_top]) + " }"\
     + " -blockPinTarget { nearestRingStripe nearestTarget } -padPinPortConnect { allPort oneGeom } -checkAlignedSecondaryPin 1 -blockPin useLef -allowJogging 1"\
     + " -crossoverViaBottomLayer " + metal_layer_bottom + " -targetViaBottomLayer " + metal_layer_bottom + " -allowLayerChange 1"\
     + " -targetViaTopLayer " + metal_layer_top + " -crossoverViaTopLayer " + metal_layer_top + " -nets {" + " ".join([flow_settings["gnd_net"],flow_settings["pwr_net"]]) +  "}",
    #perform initial placement with IOs
    "setPlaceMode -fp false -place_global_place_io_pins true",
    "place_design -noPrePlaceOpt",
    "earlyGlobalRoute",
    "timeDesign -preCTS -idealClock -numPaths 10 -prefix preCTSpreOpt -outDir " + os.path.join(report_path,"timeDesignpreCTSReports"),
    "optDesign -preCTS -outDir " + os.path.join(report_path,"optDesignpreCTSReports"),
    "timeDesign -preCTS -idealClock -numPaths 10 -prefix preCTSpostOpt -outDir " + os.path.join(report_path,"timeDesignpreCTSReports"),
    "addFiller -cell {" +  " ".join(flow_settings["filler_cell_names"]) + "} -prefix FILL -merge true",
    # If cts flag is set perform clock tree synthesis and post cts optimization
    cts_cmds,
    # "clearGlobalNets",
    # "globalNetConnect " + flow_settings["gnd_pin"] + " -type pgpin -pin " + flow_settings["gnd_pin"] + " -inst {}",
    # "globalNetConnect " + flow_settings["pwr_pin"] + " -type pgpin -pin " + flow_settings["pwr_pin"] + " -inst {}",
    # "globalNetConnect " + flow_settings["gnd_net"] + " -type net -net  " + flow_settings["gnd_net"],
    # "globalNetConnect " + flow_settings["pwr_net"] + " -type net -net  " + flow_settings["pwr_net"],
    # "globalNetConnect " + flow_settings["pwr_pin"] + " -type pgpin -pin  " + flow_settings["pwr_pin"] + " -inst *",
    # "globalNetConnect " + flow_settings["gnd_pin"] + " -type pgpin -pin  " + flow_settings["gnd_pin"] + " -inst *",
    # "globalNetConnect " + flow_settings["pwr_pin"] + " -type tiehi -inst *",
    # "globalNetConnect " + flow_settings["gnd_pin"] + " -type tielo -inst *",
    # "sroute -connect { blockPin padPin padRing corePin floatingStripe } -layerChangeRange { "+ " ".join([metal_layer_bottom,metal_layer_top]) + " }"\
    #  + " -blockPinTarget { nearestRingStripe nearestTarget } -padPinPortConnect { allPort oneGeom } -checkAlignedSecondaryPin 1 -blockPin useLef -allowJogging 1"\
    #  + " -crossoverViaBottomLayer " + metal_layer_bottom + " -targetViaBottomLayer " + metal_layer_bottom + " -allowLayerChange 1"\
    #  + " -targetViaTopLayer " + metal_layer_top + " -crossoverViaTopLayer " + metal_layer_top + " -nets {" + " ".join([flow_settings["gnd_net"],flow_settings["pwr_net"]]) +  "}",
    
    #perform routing
    "setNanoRouteMode -quiet -routeWithTimingDriven 1",
    "setNanoRouteMode -quiet -routeWithSiDriven 1",
    "setNanoRouteMode -quiet -routeTopRoutingLayer " + metal_layer,
    "setNanoRouteMode -quiet -routeBottomRoutingLayer 1",
    "setNanoRouteMode -quiet -drouteEndIteration 1",
    "setNanoRouteMode -quiet -routeWithTimingDriven true",
    "setNanoRouteMode -quiet -routeWithSiDriven true",
    "routeDesign -globalDetail",
    "setExtractRCMode -engine postRoute",
    "extractRC",
    "buildTimingGraph",
    "setAnalysisMode -analysisType onChipVariation -cppr both",
    "timeDesign -postRoute -prefix postRoutePreOpt -outDir " +  os.path.join(report_path,"timeDesignPostRouteReports"),
    "optDesign -postRoute -prefix postRouteOpt -outDir " +  os.path.join(report_path,"optDesignPostRouteReports"),
    "timeDesign -postRoute -prefix postRoutePostOpt -outDir" +  os.path.join(report_path,"timeDesignPostRouteReports"),
    #output reports
    "report_qor > " + os.path.join(report_path,"qor.rpt"),
    "verify_drc -report " + os.path.join(report_path,"geom.rpt"),
    "verifyConnectivity -type all -report " + os.path.join(report_path,"conn.rpt"),
    "report_timing > " + os.path.join(report_path,"setup_timing.rpt"),
    "setAnalysisMode -checkType hold",
    "report_timing > " + os.path.join(report_path,"hold_timing.rpt"),
    "report_power > " + os.path.join(report_path,"power.rpt"),
    "report_constraint -all_violators > " + os.path.join(report_path,"violators.rpt"),
    "report_area > " + os.path.join(report_path,"area.rpt"),
    "summaryReport -outFile " + os.path.join(report_path,"pr_report.txt"),
    #output design files
    "saveNetlist " + os.path.join(output_path,"netlist.v"),
    "saveDesign " +  os.path.join(output_path,"design.enc"),
    "rcOut -spef " +  os.path.join(output_path,"spef.spef"),
    "write_sdf -ideal_clock_network " + os.path.join(output_path,"sdf.sdf"),
    stream_out_cmd
  ]
  #flatten list
  #file_lines = [item for sublist in file_lines for item in sublist]
  flat_list = lambda file_lines:[element for item in file_lines for element in flat_list(item)] if type(file_lines) is list else [file_lines]
  file_lines = flat_list(file_lines)
  file = open(fname,"w")
  for line in file_lines:
    file_write_ln(file,line)
  file_write_ln(file,"exit")
  file.close()
  
  return fname,output_path

def write_innovus_init_script(flow_settings,view_fpath,syn_output_path):
  """
  This function generates init script which sets variables used in pnr,
  The contents of this file were generated from using the innovus GUI
  setting relavent files/nets graphically and exporting the .globals file
  """
  flow_settings["lef_files"] = flow_settings["lef_files"].strip("\"")
  fname = flow_settings["top_level"]+"_innovus_init.tcl"
  file = open(fname,"w")
  file_lines = [
    "set_global _enable_mmmc_by_default_flow      $CTE::mmmc_default",
    "suppressMessage ENCEXT-2799",
    "set ::TimeLib::tsgMarkCellLatchConstructFlag 1",
    "set conf_qxconf_file NULL",
    "set conf_qxlib_file NULL",
    "set dbgDualViewAwareXTree 1",
    "set defHierChar /",
    "set distributed_client_message_echo 1",
    "set distributed_mmmc_disable_reports_auto_redirection 0",
    #The below config file comes from the INNOVUS directory, if not using an x86 system this will probably break
    "set dlgflprecConfigFile " + os.path.join(flow_settings["EDI_HOME"],"tools.lnx86/dlApp/run_flprec.cfg"),
    "set enable_ilm_dual_view_gui_and_attribute 1",
    "set enc_enable_print_mode_command_reset_options 1",
    "set init_design_settop 0",
    "set init_gnd_net " + flow_settings["gnd_net"],
    #/CMC/kits/tsmc_65nm_libs/tcbn65gplus/TSMCHOME/digital/Back_End/lef/tcbn65gplus_200a/lef/tcbn65gplus_9lmT2.lef /CMC/kits/tsmc_65nm_libs/tpzn65gpgv2/TSMCHOME/digital/Back_End/lef/tpzn65gpgv2_140c/mt_2/9lm/lef/antenna_9lm.lef /CMC/kits/tsmc_65nm_libs/tpzn65gpgv2/TSMCHOME/digital/Back_End/lef/tpzn65gpgv2_140c/mt_2/9lm/lef/tpzn65gpgv2_9lm.lef
    "set init_lef_file {" + flow_settings["lef_files"]  + "}",
    "set init_mmmc_file {" + view_fpath + "}",
    "set init_pwr_net " + flow_settings["pwr_net"],
    "set init_top_cell " + flow_settings["top_level"],
    "set init_verilog " + os.path.join(syn_output_path,"synthesized_hier.v"),
    "get_message -id GLOBAL-100 -suppress",
    "get_message -id GLOBAL-100 -suppress",
    "set latch_time_borrow_mode max_borrow",
    "set pegDefaultResScaleFactor 1",
    "set pegDetailResScaleFactor 1",
    "set pegEnableDualViewForTQuantus 1",
    "get_message -id GLOBAL-100 -suppress",
    "get_message -id GLOBAL-100 -suppress",
    "set report_inactive_arcs_format {from to when arc_type sense reason}",
    "set spgUnflattenIlmInCheckPlace 2",
    "get_message -id GLOBAL-100 -suppress",
    "get_message -id GLOBAL-100 -suppress",
    "set timing_remove_data_path_pessimism_min_slack_threshold -1.70141e+38",
    "set defStreamOutCheckUncolored false",
    "set init_verilog_tolerate_port_mismatch 0",
    "set load_netlist_ignore_undefined_cell 1",
    "setDesignMode -process " + flow_settings["process_size"],
    "init_design"
  ]
  for line in file_lines:
    file_write_ln(file,line)
  file.close()
  init_script_abs_path = os.path.join(os.getcwd(),fname)
  return init_script_abs_path
  


def write_enc_script(flow_settings,metal_layer,core_utilization):
  """
  Writes script for place and route using cadence encounter (tested under 2009 version)
  """
  # generate the EDI (encounter) configuration
  file = open("edi.conf", "w")
  file.write("global rda_Input \n")
  file.write("set cwd .\n\n")
  file.write("set rda_Input(ui_leffile) " + flow_settings['lef_files'] + "\n")
  file.write("set rda_Input(ui_timelib,min) " + flow_settings['best_case_libs'] + "\n")
  file.write("set rda_Input(ui_timelib) " + flow_settings['standard_libs'] + "\n")
  file.write("set rda_Input(ui_timelib,max) " + flow_settings['worst_case_libs'] + "\n")
  file.write("set rda_Input(ui_netlist) " + os.path.expanduser(flow_settings['synth_folder']) + "/synthesized.v" + "\n")
  file.write("set rda_Input(ui_netlisttype) {Verilog} \n")
  file.write("set rda_Input(import_mode) {-treatUndefinedCellAsBbox 0 -keepEmptyModule 1}\n")
  file.write("set rda_Input(ui_timingcon_file) " + os.path.expanduser(flow_settings['synth_folder']) + "/synthesized.sdc" + "\n")
  file.write("set rda_Input(ui_topcell) " + flow_settings['top_level'] + "\n\n")
  gnd_pin = flow_settings['gnd_pin']
  gnd_net = flow_settings['gnd_net']
  pwr_pin = flow_settings['pwr_pin']
  pwr_net = flow_settings['pwr_net']
  file.write("set rda_Input(ui_gndnet) {" + gnd_net + "} \n")
  file.write("set rda_Input(ui_pwrnet) {" + pwr_net + "} \n")
  if flow_settings['tilehi_tielo_cells_between_power_gnd'] is True:
    file.write("set rda_Input(ui_pg_connections) [list {PIN:" + gnd_pin + ":}" + " {TIEL::} " + "{NET:" + gnd_net + ":} {NET:" + pwr_net + ":}" + " {TIEH::} " + "{PIN:" + pwr_pin + ":} ] \n")
  else:
    file.write("set rda_Input(ui_pg_connections) [list {PIN:" + gnd_pin + ":} {NET:" + gnd_net + ":} {NET:" + pwr_net + ":} {PIN:" + pwr_pin + ":} ] \n")
  file.write("set rda_Input(PIN:" + gnd_pin + ":) {" + gnd_pin + "} \n")
  file.write("set rda_Input(TIEL::) {" + gnd_pin + "} \n")
  file.write("set rda_Input(NET:" + gnd_net + ":) {" + gnd_net + "} \n")
  file.write("set rda_Input(PIN:" + pwr_pin + ":) {" + pwr_pin + "} \n")
  file.write("set rda_Input(TIEH::) {" + pwr_pin + "} \n")
  file.write("set rda_Input(NET:" + pwr_net + ":) {" + pwr_net + "} \n\n")
  if (flow_settings['inv_footprint'] != "None"):
    file.write("set rda_Input(ui_inv_footprint) {" + flow_settings['inv_footprint'] + "}\n")
  if (flow_settings['buf_footprint'] != "None"):
    file.write("set rda_Input(ui_buf_footprint) {" + flow_settings['buf_footprint'] + "}\n")
  if (flow_settings['delay_footprint'] != "None"):
    file.write("set rda_Input(ui_delay_footprint) {" + flow_settings['delay_footprint'] + "}\n")
  file.close()
  metal_layer_bottom = flow_settings["metal_layer_names"][0]
  metal_layer_second = flow_settings["metal_layer_names"][1]
  metal_layer_top = flow_settings["metal_layer_names"][int(metal_layer)-1]
  power_ring_metal_top = flow_settings["power_ring_metal_layer_names"][0] 
  power_ring_metal_bottom = flow_settings["power_ring_metal_layer_names"][1] 
  power_ring_metal_left = flow_settings["power_ring_metal_layer_names"][2] 
  power_ring_metal_right = flow_settings["power_ring_metal_layer_names"][3] 
  # generate the EDI (encounter) script
  file = open("edi.tcl", "w")
  file.write("loadConfig edi.conf \n")
  file.write("floorPlan -site " + flow_settings['core_site_name'] \
              + " -r " + str(flow_settings['height_to_width_ratio']) \
              + " " + str(core_utilization) \
              + " " + str(flow_settings['space_around_core']) \
              + " " + str(flow_settings['space_around_core']) + " ")
  file.write(str(flow_settings['space_around_core']) + " " + str(flow_settings['space_around_core']) + "\n")
  file.write("setMaxRouteLayer " + str(metal_layer) + " \n")
  file.write("fit \n")
  file.write("addRing -spacing_bottom " + str(flow_settings['power_ring_spacing']) \
              + " -spacing_right " + str(flow_settings['power_ring_spacing']) \
              + " -spacing_top " + str(flow_settings['power_ring_spacing']) \
              + " -spacing_left " + str(flow_settings['power_ring_spacing']) \
              + " -width_right " + str(flow_settings['power_ring_width']) \
              + " -width_left " + str(flow_settings['power_ring_width']) \
              + " -width_bottom " + str(flow_settings['power_ring_width']) \
              + " -width_top " + str(flow_settings['power_ring_width']) \
              + " -center 1" \
              + " -around core" \
              + " -layer_top " + power_ring_metal_top \
              + " -layer_bottom " + power_ring_metal_bottom \
              + " -layer_left " + power_ring_metal_left \
              + " -layer_right " + power_ring_metal_right \
              + " -nets { " + gnd_net + " " + pwr_net + " }" \
              + " -stacked_via_top_layer "+ metal_layer_top \
              + " -stacked_via_bottom_layer " + metal_layer_bottom + " \n")
  file.write("setPlaceMode -fp false -maxRouteLayer " + str(metal_layer) + "\n")
  file.write("placeDesign -inPlaceOpt -noPrePlaceOpt \n")
  file.write("checkPlace " + flow_settings['top_level'] +" \n")
  file.write("trialroute \n")
  file.write("buildTimingGraph \n")
  file.write("timeDesign -preCTS -idealClock -numPaths 10 -prefix preCTS -outDir " + os.path.expanduser(flow_settings['pr_folder']) + "/timeDesignpreCTSReports" + "\n")
  file.write("optDesign -preCTS -outDir " + os.path.expanduser(flow_settings['pr_folder']) + "/optDesignpreCTSReports" + "\n")
  # I won't do a CTS anyway as the blocks are small.
  file.write("addFiller -cell {" + " ".join([str(item) for item in flow_settings['filler_cell_names']]) + "} -prefix FILL -merge true \n")  
  file.write("clearGlobalNets \n")
  file.write("globalNetConnect " + gnd_net + " -type pgpin -pin " + gnd_pin + " -inst {} \n")
  file.write("globalNetConnect " + pwr_net + " -type pgpin -pin " + pwr_pin + " -inst {} \n")
  file.write("globalNetConnect " + gnd_net + " -type net -net " + gnd_net + " \n")
  file.write("globalNetConnect " + pwr_net + " -type net -net " + pwr_net + " \n")
  file.write("globalNetConnect " + pwr_net + " -type pgpin -pin " + pwr_pin + " -inst * \n")
  file.write("globalNetConnect " + gnd_net + " -type pgpin -pin " + gnd_pin + " -inst * \n")
  file.write("globalNetConnect " + pwr_net + " -type tiehi -inst * \n")
  file.write("globalNetConnect " + gnd_net + " -type tielo -inst * \n")
  file.write("sroute -connect { blockPin padPin padRing corePin floatingStripe }" \
              + " -layerChangeRange { " + metal_layer_bottom + " " + metal_layer_top + " }" \
              + " -blockPinTarget { nearestRingStripe nearestTarget }" \
              + " -padPinPortConnect { allPort oneGeom }" \
              + " -checkAlignedSecondaryPin 1" \
              + " -blockPin useLef" \
              + " -allowJogging 1" \
              + " -crossoverViaBottomLayer " + metal_layer_bottom \
              + " -allowLayerChange 1" \
              + " -targetViaTopLayer " + metal_layer_top \
              + " -crossoverViaTopLayer " + metal_layer_top \
              + " -targetViaBottomLayer " + metal_layer_bottom \
              + " -nets { " + gnd_net + " " + pwr_net + " } \n")
  file.write("routeDesign -globalDetail\n")
  file.write("setExtractRCMode -engine postRoute \n")
  file.write("extractRC \n")
  file.write("buildTimingGraph \n")
  file.write("timeDesign -postRoute -outDir " + os.path.expanduser(flow_settings['pr_folder']) + "/timeDesignReports" + "\n")
  file.write("optDesign -postRoute -outDir " + os.path.expanduser(flow_settings['pr_folder']) + "/optDesignReports" + "\n")
  #by default, violations are reported in designname.geom.rpt
  file.write("verifyGeometry -report " + (os.path.expanduser(flow_settings['pr_folder']) + "/" + flow_settings['top_level'] + ".geom.rpt") + "\n")
  #by default, violations are reported in designname.conn.rpt
  file.write("verifyConnectivity -type all -report " + (os.path.expanduser(flow_settings['pr_folder']) + "/" + flow_settings['top_level'] + ".conn.rpt") + "\n")
  # report area
  file.write("summaryReport -outFile " + os.path.expanduser(flow_settings['pr_folder']) + "/pr_report.txt \n")
  # save design
  file.write(r'saveNetlist ' + os.path.expanduser(flow_settings['pr_folder']) + r'/netlist.v' + "\n")
  file.write(r'saveDesign ' + os.path.expanduser(flow_settings['pr_folder']) + r'/design.enc' + " \n")
  file.write(r'rcOut -spef ' + os.path.expanduser(flow_settings['pr_folder']) + r'/spef.spef' + " \n")
  file.write(r'write_sdf -ideal_clock_network ' + os.path.expanduser(flow_settings['pr_folder']) + r'/sdf.sdf' + " \n")
  #If the user specified a layer mapping file, then use that. Otherwise, just let the tool create a default one.
  if flow_settings['map_file'] != "None":
    file.write(r'streamOut ' + os.path.expanduser(flow_settings['pr_folder']) + r'/final.gds2' + ' -mapFile ' + flow_settings['map_file'] + ' -stripes 1 -units 1000 -mode ALL' + "\n")
  else:
    file.write(r'streamOut ' + os.path.expanduser(flow_settings['pr_folder']) + r'/final.gds2' + ' -stripes 1 -units 1000 -mode ALL' + "\n")
  file.write("exit \n")
  file.close()

def copy_pnr_outputs(flow_settings,copy_logs_cmd_str,report_dest_str,only_reports=False):
  #Copy pnr results to a unique dir in pnr dir
  clean_logs_cmd_str = copy_logs_cmd_str.split(" ")
  clean_logs_cmd_str[0] = "rm -f"
  #removes the last element in the string (this is the desintation report directory)
  del clean_logs_cmd_str[-1]
  clean_logs_cmd_str = " ".join(clean_logs_cmd_str)

  mkdir_cmd_str = "mkdir -p " + report_dest_str
  if(not only_reports):
    copy_rep_cmd_str = "cp " + flow_settings['pr_folder'] + "/* " + report_dest_str
  else:
    copy_rep_cmd_str = "cp " + flow_settings['pr_folder'] + "/*.rpt " + report_dest_str
  copy_rec_cmd_str = " ".join(["cp -r",os.path.join(flow_settings['pr_folder'],"design.enc.dat"),report_dest_str])
  print("####################### PNR #######################")
  print(mkdir_cmd_str)
  print(copy_rep_cmd_str)
  print(copy_rec_cmd_str)
  print(copy_logs_cmd_str)
  print(clean_logs_cmd_str)
  print("####################### PNR #######################")
  # subprocess.call(mkdir_cmd_str,shell=True)
  # subprocess.call(copy_rep_cmd_str,shell=True)
  # subprocess.call(copy_rec_cmd_str,shell=True)
  # subprocess.call(copy_logs_cmd_str,shell=True)
  # subprocess.call(clean_logs_cmd_str,shell=True)


def run_pnr(flow_settings,metal_layer,core_utilization,synth_report_str,syn_output_path):
  """
  runs place and route using cadence encounter
  Prereqs: flow_settings_pre_process() function to properly format params for scripts
  """
  work_dir = os.getcwd()
  pnr_report_str = synth_report_str + "_" + "metal_layers_" + metal_layer + "_" + "util_" + core_utilization
  report_dest_str = os.path.join(flow_settings['pr_folder'],pnr_report_str + "_reports")
  if(flow_settings["pnr_tool"] == "encounter"):
    write_enc_script(flow_settings,metal_layer,core_utilization)
    copy_logs_cmd_str = "cp " + "edi.log " + "edi.tcl " + "edi.conf " + "encounter.log " + "encounter.cmd " + report_dest_str
    subprocess.call('encounter -nowin -init edi.tcl | tee edi.log', shell=True,executable="/bin/bash") 
  elif(flow_settings["pnr_tool"] == "innovus"):
    # if(flow_settings["partition"] == True):
    #   init_util = 0.1
    #   fp_gen_fname, fp_fname = write_innovus_fp_script(flow_settings,metal_layer,init_util)
    #   ptn_script_fname = write_innovus_ptn_script(flow_settings,metal_layer,core_utilization,init_script_fname,fp_fname)
    #   sys.exit(1)
    # else:
    view_fpath = write_innovus_view_file(flow_settings,syn_output_path)
    init_script_fname = write_innovus_init_script(flow_settings,view_fpath,syn_output_path)
    innovus_script_fname, pnr_output_path = write_innovus_script(flow_settings,metal_layer,core_utilization,init_script_fname,cts_flag=False)
    run_innovus_cmd = "innovus -no_gui -init " + innovus_script_fname + " | tee inn.log"
    copy_logs_cmd_str = " ".join(["cp", "inn.log", init_script_fname, view_fpath, os.path.join(work_dir,innovus_script_fname), report_dest_str])
    subprocess.call(run_innovus_cmd, shell=True,executable="/bin/bash") 

  # read total area from the report file:
  file = open(os.path.expanduser(flow_settings['pr_folder']) + "/pr_report.txt" ,"r")
  for line in file:
    if line.startswith('Total area of Core:'):
      total_area = re.findall(r'\d+\.{0,1}\d*', line)
  file.close()
  copy_pnr_outputs(flow_settings,copy_logs_cmd_str,report_dest_str)
  return pnr_report_str, pnr_output_path, total_area

def run_sim():
  """
  Runs simulation using a user inputted testbench, not tested and unsure of which hard block its modeling USE AT OWN RISK (ie use saif file option in hardblock settings file)
  """
  # Create a modelsim folder
  #subprocess.call("mkdir -p"+os.path.expanduser("./modelsim_dir")+"\n", shell=True)
  # Create a modelsim .do file:
  #subprocess.call("vlib modelsim_dir/libraries"+"\n",shell=True)
  # todo: change the address and take it from the user as input
  #subprocess.call("vlog -work modelsim_dir/libraries /CMC/kits/tsmc_65nm_libs/tcbn65gplus/TSMCHOME/digital/Front_End/verilog/tcbn65gplus_140b/tcbn65gplus.v /CMC/kits/tsmc_65nm_libs/tpzn65gpgv2/TSMCHOME/digital/Front_End/verilog/tpzn65gpgv2_140c/tpzn65gpgv2.v"+"\n",shell=True)
  file = open("modelsim.do", "w")
  file.write("cd " + os.path.expanduser("./modelsim_dir") + "\n")
  file.write("vlib work \n")
  file.write("vlog -work work ../../test/testbench.v \n")
  file.write("vlog -work work ../../pr/netlist.v \n")
  file.write("vsim -L work -L libraries testbench\n")
  file.write("vcd file vcd.vcd \n")
  file.write("vcd add -r testbench/uut/* \n")
  file.write("run 1000 ns \n")
  file.write("quit \n")
  file.close()      
  subprocess.call('vsim -c -do modelsim.do', shell=True)           
  subprocess.call('rm -rf modelsim.do', shell=True)
  subprocess.call('vcd2wlf ./modelsim_dir/vcd.vcd out.wlf', shell=True)
  subprocess.call('wlf2vcd -o test.vcd out.wlf', shell=True)
  subprocess.call('vcd2saif -input test.vcd -o saif.saif', shell=True)

def write_pt_power_script(flow_settings,mode_enabled,clock_period,x,pnr_output_folder,rel_outputs=False):
  """"
  writes the tcl script for power analysis using Synopsys Design Compiler, tested under 2017 version
  Update: changed the [all_nets] argument used in set_switching_activity to use -baseClk and -inputs args instead.
  This function takes the RC values generated from pnr script in form of .spef file and the user inputted switching probability or 
  a .saif file generated from a testbench to estimate power.
  """
  report_path = flow_settings["primetime_folder"] if (not rel_outputs) else os.path.join("..","reports")
  report_path = os.path.abspath(report_path)
  # Create a script to measure power:
  file_lines = [
    "set sh_enable_page_mode true",
    "set search_path " + flow_settings['search_path'], 
    "set my_top_level " + flow_settings['top_level'],
    "set my_clock_pin " + flow_settings['clock_pin_name'],
    "set target_library " + flow_settings['primetime_libs'],
    "set link_library " + flow_settings['link_library'],
    "read_verilog " + os.path.join(pnr_output_folder,"netlist.v"),
    "link",
    "set my_period " + str(clock_period) ,
    "set find_clock [ find port [list $my_clock_pin] ]",
    "if { $find_clock != [list] } { ",
    "set clk_name $my_clock_pin",
    "create_clock -period $my_period $clk_name}",
  ]

  file = open("primetime_power.tcl", "w")
  file.write("set sh_enable_page_mode true \n")
  file.write("set search_path " + flow_settings['search_path'] + " \n")
  file.write("set my_top_level " + flow_settings['top_level'] + "\n")
  file.write("set my_clock_pin " + flow_settings['clock_pin_name'] + "\n")
  file.write("set target_library " + flow_settings['primetime_libs'] + "\n")
  file.write("set link_library " + flow_settings['link_library'] + "\n")
  file.write("read_verilog " + os.path.join(pnr_output_folder,"netlist.v") + "\n")
  file.write("link \n")
  file.write("set my_period " + str(clock_period) + " \n")
  file.write("set find_clock [ find port [list $my_clock_pin] ] \n")
  file.write("if { $find_clock != [list] } { \n")
  file.write("set clk_name $my_clock_pin \n")
  file.write("create_clock -period $my_period $clk_name} \n\n")
  if mode_enabled and x <2**len(flow_settings['mode_signal']):
    for y in range (0, len(flow_settings['mode_signal'])):
      file.write("set_case_analysis " + str((x >> y) & 1) + " " +  flow_settings['mode_signal'][y] +  " \n")
  file.write("set power_enable_analysis TRUE \n")
  file.write("set power_analysis_mode \"averaged\"" + " \n")
  if flow_settings['generate_activity_file']:
    file.write("read_saif -input saif.saif -instance_name testbench/uut \n")
  else:
    file.write("set_switching_activity -static_probability " + str(flow_settings['static_probability']) + " -toggle_rate " + str(flow_settings['toggle_rate']) + " -base_clock $my_clock_pin -type inputs \n")
  #file.write("read_saif -input saif.saif -instance_name testbench/uut \n")
  #file.write("read_vcd -input ./modelsim_dir/vcd.vcd \n")
  file.write("read_parasitics -increment " + os.path.join(pnr_output_folder,'spef.spef') + "\n")
  #file.write("update_power \n")
  file.write("report_power > " + os.path.join(report_path,"power.rpt") + " \n")
  file.write("quit\n")
  file.close()

def write_pt_timing_script(flow_settings,mode_enabled,clock_period,x,pnr_output_path,rel_outputs=False):
  """
  writes the tcl script for timing analysis using Synopsys Design Compiler, tested under 2017 version
  This should look for setup/hold violations using the worst case (hold) and best case (setup) libs
  """
  report_path = flow_settings["primetime_folder"] if (not rel_outputs) else os.path.join("..","reports")
  report_path = os.path.abspath(report_path)
  
  # if mode_enabled and x <2**len(flow_settings['mode_signal']):
    # for y in range (0, len(flow_settings['mode_signal'])):
      # file.write("set_case_analysis " + str((x >> y) & 1) + " " +  flow_settings['mode_signal'][y] + " \n")
  if mode_enabled and x < 2**len(flow_settings['mode_signal']):
    case_analysis_cmds = [" ".join(["set_case_analysis",str((x >> y) & 1),flow_settings['mode_signal'][y]]) for y in range(0,len(flow_settings["mode_signal"]))]
  else:
    case_analysis_cmds = ["#MULTIMODAL ANALYSIS DISABLED"]
  #For power switching activity estimation
  if flow_settings['generate_activity_file']:
    switching_activity_cmd = "read_saif -input saif.saif -instance_name testbench/uut"
  else:
    switching_activity_cmd = "set_switching_activity -static_probability " + str(flow_settings['static_probability']) + " -toggle_rate " + str(flow_settings['toggle_rate']) + " -base_clock $my_clock_pin -type inputs"

  # backannotate into primetime
  # This part should be reported for all the modes in the design.
  file_lines = [
    "set sh_enable_page_mode true",
    "set search_path " + flow_settings['search_path'],
    "set my_top_level " + flow_settings['top_level'],
    "set my_clock_pin " + flow_settings['clock_pin_name'],
    "set target_library " + flow_settings['primetime_libs'],
    "set link_library " + flow_settings['link_library'],
    "read_verilog " + pnr_output_path + "/netlist.v",
    case_analysis_cmds,
    "link",
    "set my_period " + str(clock_period),
    "set find_clock [ find port [list $my_clock_pin] ] ",
    "if { $find_clock != [list] } { ",
    "set clk_name $my_clock_pin",
    "create_clock -period $my_period $clk_name",
    "}",
    #Standard Parasitic Exchange Format. File format to save parasitic information extracted by the place and route tool.
    "read_parasitics -increment " + pnr_output_path + "/spef.spef",
    "report_timing > " + os.path.join(report_path,"timing.rpt"),
    "set power_enable_analysis TRUE",
    "set power_analysis_mode \"averaged\"",
    switching_activity_cmd,
    "report_power > " + os.path.join(report_path,"power.rpt"),
    "quit",
  ]
  flat_list = lambda file_lines:[element for item in file_lines for element in flat_list(item)] if type(file_lines) is list else [file_lines]
  file_lines = flat_list(file_lines)

  # file = open("primetime.tcl", "w")
  # file.write("set sh_enable_page_mode true \n")
  # file.write("set search_path " + flow_settings['search_path'] + " \n")
  # file.write("set my_top_level " + flow_settings['top_level'] + "\n")
  # file.write("set my_clock_pin " + flow_settings['clock_pin_name'] + "\n")
  # file.write("set target_library " + flow_settings['primetime_libs'] + "\n")
  # file.write("set link_library " + flow_settings['link_library'] + "\n")
  # file.write("read_verilog " + pnr_output_path + "/netlist.v \n")
  # if mode_enabled and x <2**len(flow_settings['mode_signal']):
    # for y in range (0, len(flow_settings['mode_signal'])):
      # file.write("set_case_analysis " + str((x >> y) & 1) + " " +  flow_settings['mode_signal'][y] + " \n")
  # file.write("link \n")
  # file.write("set my_period " + str(clock_period) + " \n")
  # file.write("set find_clock [ find port [list $my_clock_pin] ] \n")
  # file.write("if { $find_clock != [list] } { \n")
  # file.write("set clk_name $my_clock_pin \n")
  # file.write("create_clock -period $my_period $clk_name} \n\n")
  # file.write("read_parasitics -increment " + pnr_output_path + "/spef.spef \n")
  # file.write("report_timing > " + report_path + "/timing.rpt \n")
  # file.write("quit \n")
  fname = "pt_pwr_timing.tcl"
  fd = open(fname, "w")
  for line in file_lines:
    file_write_ln(fd,line)
  fd.close()
  fpath = os.path.join(os.getcwd(),fname)
  #print("pt_pwr_timing fpath %s " % (fpath))
  return fpath,report_path

def run_power_timing(flow_settings,mode_enabled,clock_period,x,pnr_report_str,pnr_output_path):
  """
  This runs STA using PrimeTime and the pnr generated .spef and netlist file to get a more accurate result for delay
  """
  #If there is no multi modal analysis selected then x (mode of operation) will be set to 0 (only 1 mode) not sure why this is done like below but not going to change it
  #if there is multi modal analysis then the x will be the mode of operation and it will be looped from 0 -> 2^num_modes
  #This is done because multimodal setting basically sets a mux to the value of 0 or 1 and each mode represents 1 mux ie to evaluate them all we have 2^num_modes states to test 
  if not mode_enabled:
    x = 2**len(flow_settings['mode_signal'])
  pt_timing_fpath,timing_report_path = write_pt_timing_script(flow_settings,mode_enabled,clock_period,x,pnr_output_path)
  # run prime time, by getting abs path from writing the script, we can run the command in different directory where the script exists
  run_pt_timing_cmd = "dc_shell-t -f " + pt_timing_fpath + " | tee pt_pwr_timing.log"
  subprocess.call(run_pt_timing_cmd, shell=True,executable="/bin/bash")
  # Read timing parameters
  file = open(os.path.join(timing_report_path,"timing.rpt"),"r")
  for line in file:
    if 'library setup time' in line:
      library_setup_time = re.findall(r'\d+\.{0,1}\d*', line)
    if 'data arrival time' in line:
      data_arrival_time = re.findall(r'\d+\.{0,1}\d*', line)
  try:
    total_delay =  float(library_setup_time[0]) + float(data_arrival_time[0])
  except NameError:
    total_delay =  float(data_arrival_time[0])
  file.close()
  #write_pt_power_script(flow_settings,mode_enabled,clock_period,x,pnr_output_path)
  # run prime time
  #subprocess.call('dc_shell-t -f primetime_power.tcl | tee pt_pwr.log', shell=True,executable="/bin/bash") 
  #copy reports and logs to a unique dir in pt dir
  pt_report_str = pnr_report_str + "_" + "mode_" + str(x)
  report_dest_str = os.path.expanduser(flow_settings['primetime_folder']) + "/" + pt_report_str + "_reports"
  mkdir_cmd_str = "mkdir -p " + report_dest_str
  copy_rep_cmd_str = "cp " + os.path.expanduser(flow_settings['primetime_folder']) + "/* " + report_dest_str
  copy_logs_cmd_str = "cp " + "pt.log pt_pwr.log primetime.tcl primetime_power.tcl " + report_dest_str
  subprocess.call(mkdir_cmd_str,shell=True)
  subprocess.call(copy_rep_cmd_str,shell=True)
  subprocess.call(copy_logs_cmd_str,shell=True)
  # subprocess.call('rm -f pt.log pt_pwr.log primetime.tcl primetime_power.tcl', shell=True)
  # print("####################### STA #######################")
  # print(mkdir_cmd_str)
  # print(copy_rep_cmd_str)
  # print(copy_logs_cmd_str)
  # print("####################### STA #######################")
  # Read dynamic power
  file = open(os.path.expanduser(flow_settings['primetime_folder']) + "/power.rpt" ,"r")
  for line in file:
    if 'Total Dynamic Power' in line:
      total_dynamic_power = re.findall(r'\d+\.{0,1}\d*', line)
      total_dynamic_power[0] = float(total_dynamic_power[0])
      if 'mW' in line:
        total_dynamic_power[0] *= 0.001
      elif 'uw' in line:
        total_dynamic_power[0] *= 0.000001
      else:
        total_dynamic_power[0] = 0
  file.close() 
  return library_setup_time, data_arrival_time, total_delay, total_dynamic_power   


def flow_settings_pre_process(processed_flow_settings,cur_env):
  """Takes values from the flow_settings dict and converts them into data structures which can be used to write synthesis script"""
  # formatting design_files
  design_files = []
  if processed_flow_settings['design_language'] == 'verilog':
    ext_re = re.compile(".*.v")
  elif processed_flow_settings['design_language'] == 'vhdl':
    ext_re = re.compile(".*.vhdl")
  elif processed_flow_settings['design_language'] == 'sverilog':
    ext_re = re.compile(".*(.sv)|(.v)")

  design_folder = os.path.expanduser(processed_flow_settings['design_folder'])
  design_files = [fn for _, _, fs in os.walk(design_folder) for fn in fs if ext_re.search(fn)]
  #The syn_write_tcl_script function expects this to be a list of all design files
  processed_flow_settings["design_files"] = design_files
  # formatting search_path
  search_path_dirs = []
  search_path_dirs.append(".")
  try:
    syn_root = cur_env.get("SYNOPSYS")
    search_path_dirs = [os.path.join(syn_root,"libraries",dirname) for dirname in ["syn","syn_ver","sim_ver"] ]
  except:
    print("could not find 'SYNOPSYS' environment variable set, please source your ASIC tools or run the following command to your sysopsys home directory")
    print("export SYNOPSYS=/abs/path/to/synopsys/home")
    print("Ex. export SYNOPSYS=/CMC/tools/synopsys/syn_vN-2017.09/")
    sys.exit(1)
  #Place and route
  if(processed_flow_settings["pnr_tool"] == "innovus"):
    try:
      edi_root = cur_env.get("EDI_HOME")
      processed_flow_settings["EDI_HOME"] = edi_root
    except:
      print("could not find 'EDI_HOME' environment variable set, please source your ASIC tools or run the following command to your INNOVUS/ENCOUNTER home directory")
      sys.exit(1)
  
  for p_lib_path in processed_flow_settings["process_lib_paths"]:
    search_path_dirs.append(p_lib_path)
  search_path_dirs.append(design_folder)
  for root,dirnames,fnames in os.walk(design_folder):
    for dirname,fname in zip(dirnames,fnames):
      if(ext_re.search(fname)):
        search_path_dirs.append(os.path.join(root,dirname))
  search_path_str = "\"" + " ".join(search_path_dirs) + "\""
  processed_flow_settings["search_path"] = search_path_str
  #formatting target libs
  processed_flow_settings["target_library"] = "\"" + " ".join(processed_flow_settings['target_libraries']) + "\""
  processed_flow_settings["link_library"] = "\"" + "* $target_library" + "\""
  #formatting all paths to files to expand them to user space
  for flow_key, flow_val in processed_flow_settings.items():
    if("folder" in flow_key):
      processed_flow_settings[flow_key] = os.path.expanduser(flow_val)

  #formatting process specific params
  processed_flow_settings["lef_files"] = "\"" + " ".join(processed_flow_settings['lef_files']) + "\""
  processed_flow_settings["best_case_libs"] = "\"" + " ".join(processed_flow_settings['best_case_libs']) + "\""
  processed_flow_settings["standard_libs"] = "\"" + " ".join(processed_flow_settings['standard_libs']) + "\""
  processed_flow_settings["worst_case_libs"] = "\"" + " ".join(processed_flow_settings['worst_case_libs']) + "\""
  processed_flow_settings["primetime_libs"] = "\"" + " ".join(processed_flow_settings['primetime_libs']) + "\""

  #TODO bring these to the top new flow_settings options
  #processed_flow_settings["ungroup_regex"] = ".*ff.*|.*vcr.*"
  if(processed_flow_settings["partition_flag"]):
    processed_flow_settings["ptn_params"]["scaling_array"] = [float(scale) for scale in processed_flow_settings["ptn_params"]["scaling_array"]]
    processed_flow_settings["ptn_params"]["fp_init_dims"] = [float(dim) for dim in processed_flow_settings["ptn_params"]["fp_init_dims"]]

    for ptn_dict in processed_flow_settings["ptn_params"]["ptn_list"]:
      ptn_dict["fp_coords"] = [float(coord) for coord in ptn_dict["fp_coords"]]

    processed_flow_settings["parallel_hardblock_folder"] = os.path.expanduser(processed_flow_settings["parallel_hardblock_folder"])
  
  
def gen_dir(dir_path):
  if(not os.path.isdir(dir_path)):
    os.mkdir(dir_path)

def gen_n_trav(dir_path):
  gen_dir(dir_path)
  os.chdir(dir_path)

def get_dc_cmd(script_path):
  syn_shell = "dc_shell-t"
  return " ".join([syn_shell,"-f",script_path," > dc.log"])

def get_sta_cmd(script_path):
  pt_shell = "dc_shell-t"
  return " ".join([pt_shell,"-f",script_path," > pt_timing_pwr.log"])


def write_param_flow_stage_bash_script(flow_settings,param_path):
  flow_stage = param_path.split("/")[-2]
  flow_cmd = ""
  if(flow_stage == "synth"):
    script_rel_path = os.path.join("..","scripts", "dc_script.tcl")
    flow_cmd = get_dc_cmd(script_rel_path)
  elif(flow_stage == "pnr"):
    script_rel_path = os.path.join("..","scripts","_".join([flow_settings["top_level"],flow_settings["pnr_tool"]+".tcl"]))
    if(flow_settings["pnr_tool"] == "innovus"):
      flow_cmd = get_innovus_cmd(script_rel_path)
    elif(flow_settings["pnr_tool"] == "encounter"):
      flow_cmd = get_encounter_cmd(script_rel_path)
  elif(flow_stage == "sta"):
    script_rel_path = os.path.join("..","scripts", "pt_pwr_timing.tcl") #TODO fix the filename dependancy issues
    flow_cmd = get_sta_cmd(script_rel_path)
  if(flow_cmd == ""):
    return
  file_lines = [
    "#!/bin/bash",
    "cd " + os.path.join(param_path,"work"),
    flow_cmd,
  ]
  fd = open(param_path.split("/")[-1] + "_" + flow_stage + "_run_parallel.sh","w")  
  for line in file_lines:
    file_write_ln(fd,line)
  fd.close()

def write_top_lvl_parallel_bash_script(parallel_script_path):
  #this writes a top_level script which runs each synthesis script for respective params in parallel
  script_fname = "top_level_parallel.sh"
  file_lines = [
    "#!/bin/bash"
    ]  
  for f in os.listdir(parallel_script_path):
    if(os.path.isfile(os.path.join(parallel_script_path,f) )):
      file_lines.append(os.path.join(parallel_script_path,f) + " &")
  fd = open(script_fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  fd.close()

def write_parallel_scripts(flow_settings,top_level_path):
  os.chdir(top_level_path)
  #CWD Ex. asic_work/router_wrap
  for flow_stage_dir in os.listdir(top_level_path):
    parallel_work_dir = flow_stage_dir + "_parallel_work"
    os.chdir(flow_stage_dir)
    flow_path = os.getcwd()
    #CWD Ex. asic_work/router_wrap/synth
    gen_n_trav(parallel_work_dir)
    gen_n_trav("scripts")
    #clean existing bash scripts
    sh_scripts = glob.glob("*.sh")
    for s in sh_scripts:
      os.remove(s)
    for dir in os.listdir(flow_path):
      if("period" in dir): #TODO DEPENDANCY
        write_param_flow_stage_bash_script(flow_settings,os.path.join(flow_path,dir))
    os.chdir("..")
    write_top_lvl_parallel_bash_script("scripts")
    os.chdir(top_level_path)

def hardblock_script_gen(flow_settings):
  """
  This function will generate all ASIC flow scripts and run some basic environment/parameter checks to make sure the scripts will function properly but won't run any tools
  This function should be run into an asic_work directory which will have directory structure generated inside of it
  """
  print("Generating hardblock scripts...")
  pre_func_dir = os.getcwd()
  cur_env = os.environ.copy()
  processed_flow_settings = flow_settings
  flow_settings_pre_process(processed_flow_settings,cur_env)
  #Generate the parallel work directory if it doesn't exist and move into it
  gen_n_trav(flow_settings["parallel_hardblock_folder"])
  # print(os.getcwd())
  # sys.exit(1)



  #some constants for directory structure will stay the same for now (dont see a reason why users should be able to change this)
  synth_dir = "synth"
  pnr_dir = "pnr"
  sta_dir = "sta"
  #directories generated in each parameterized directory
  work_dir = "work" 
  script_dir = "scripts"
  outputs_dir = "outputs"
  reports_dir = "reports"
  generate_flow_links = False #Kinda sketchy setting, I found it useful when playing around but could cause problems

  parameterized_subdirs = [work_dir,script_dir,outputs_dir,reports_dir]



  assert len(processed_flow_settings["design_files"]) >= 1
  #create top level directory, synth dir traverse to synth dir
  gen_n_trav(flow_settings["top_level"])
  top_abs_path = os.getcwd()
  gen_n_trav(synth_dir)
  synth_abs_path = os.getcwd()
  for clock_period in flow_settings["clock_period"]:
    for wire_selection in flow_settings['wire_selection']:
      os.chdir(synth_abs_path)
      parameterized_synth_dir = "_".join(["period",clock_period,"wiremdl",wire_selection])
      gen_n_trav(parameterized_synth_dir)
      param_synth_path = os.getcwd()
      #############################################
      # sym_link_dir = "synth_link"
      # if(os.path.isdir(sym_link_dir)):
      #   sym_link_cmd = "unlink " + os.path.join(os.getcwd(),sym_link_dir)
      #   print(sym_link_cmd)
      #############################################
      #generate subdirs in parameterized dir
      for d in parameterized_subdirs:
        gen_dir(d)
      os.chdir(script_dir)
      #synthesis script generation
      syn_report_path, syn_output_path = write_synth_tcl(flow_settings,clock_period,wire_selection,rel_outputs=True)
      #the next stage will traverse into pnr directory so we want to go back to top level
      os.chdir(top_abs_path)
      gen_n_trav(pnr_dir)
      pnr_abs_path = os.getcwd()
      for metal_layer in flow_settings['metal_layers']:
          for core_utilization in flow_settings['core_utilization']:
            os.chdir(pnr_abs_path)
            #expect to be in pnr dir
            parameterized_pnr_dir = parameterized_synth_dir + "_" + "_".join(["mlayer",metal_layer,"util",core_utilization])
            gen_n_trav(parameterized_pnr_dir)
            param_pnr_path = os.getcwd()   
            #generate subdirs in parameterized dir
            #once we're in the param_pnr dir, we can create sym link to the previous synth_dir (this makes this directory structure easy to traverse, think doubly linked list)
            ###############################
            # if(generate_flow_links):
            #   sym_link_dir = "synth_link"
            #   if(not os.path.isdir(sym_link_dir)):
            #     sym_link_cmd = "ln -s " + param_synth_path + " " + os.path.join(os.getcwd(),sym_link_dir)
            #     subprocess.call(sym_link_cmd,shell=True)
            #   #then go back to previous stage and create a sym_link to the next stage
            #   if(os.path.isdir(sym_link_dir)):
            #     os.chdir(sym_link_dir)
            #     sym_link_dir = "pnr_link"
            #     if(not os.path.isdir(sym_link_dir)):
            #       sym_link_cmd = "ln -s " + param_pnr_path + " " + os.path.join(os.getcwd(),sym_link_dir)
            #       subprocess.call(sym_link_cmd,shell=True)
            # else:
            #   sym_link_dir = "synth_link"
            #   if(os.path.isdir(sym_link_dir)):
            #     sym_link_cmd = "unlink " + os.path.join(os.getcwd(),sym_link_dir)
            #     print(sym_link_cmd)
            #   sym_link_dir = "sta_link"
            #   if(os.path.isdir(sym_link_dir)):
            #     sym_link_cmd = "unlink " + os.path.join(os.getcwd(),sym_link_dir)
            #     print(sym_link_cmd)
                # subprocess.call(sym_link_cmd,shell=True)
              #then go back to previous stage and create a sym_link to the next stage
              # if(os.path.isdir(sym_link_dir)):
              #   os.chdir(sym_link_dir)
              #   sym_link_dir = "pnr_link"
              #   if(os.path.isdir(sym_link_dir)):
              #     sym_link_cmd = "unlink " + os.path.join(os.getcwd(),sym_link_dir)
              #     print(sym_link_cmd)
              #     subprocess.call(sym_link_cmd,shell=True)
            ###############################
            #change back to original dir
            os.chdir(param_pnr_path)
            for d in parameterized_subdirs:
              gen_dir(d)
            os.chdir(script_dir)
            #clean existings scripts
            prev_scripts = glob.glob("./*.tcl")
            for file in prev_scripts:
              os.remove(file)
            if(flow_settings["pnr_tool"] == "encounter"):
              #write encounter scripts
              write_enc_script(flow_settings,metal_layer,core_utilization)
            elif(flow_settings["pnr_tool"] == "innovus"):
              #write generic innovus scripts
              view_fpath = write_innovus_view_file(flow_settings,syn_output_path)
              init_script_fname = write_innovus_init_script(flow_settings,view_fpath,syn_output_path)
              innovus_script_fname,pnr_output_path = write_innovus_script(flow_settings,metal_layer,core_utilization,init_script_fname,rel_outputs=True)
              
              #TODO below command could be done with the dbGet, which makes it more general 
              #top.terms.name (then looking at parameters for network on chip verilog to determine number of ports per edge)
              if(flow_settings["partition_flag"]):
                offsets = write_edit_port_script_pre_ptn(flow_settings)

                #initializing floorplan settings
                scaled_dims_list = []
                for scale in flow_settings["ptn_params"]["scaling_array"]:
                  ptn_info_list = flow_settings["ptn_params"]["ptn_list"]
                  ptn_block_list = [ptn["mod_name"] for ptn in ptn_info_list]
                  #overall floorplan 
                  new_dim_pair = [dim*scale for dim in flow_settings["ptn_params"]["fp_init_dims"]]
                  scaled_dims_list.append(new_dim_pair)
                
                for dim_pair in scaled_dims_list:
                  #creates initial floorplan
                  fp_script_fname, fp_save = write_innovus_fp_script(flow_settings,metal_layer,init_script_fname,dim_pair)
                  #creates partitions
                  ptn_script_fname = write_innovus_ptn_script(flow_settings,init_script_fname,fp_save,offsets,dim_pair,auto_assign_regs=True)
                  
                  for block_name in ptn_block_list:
                    #runs pnr on subblock ptn
                    write_innovus_ptn_block_flow(metal_layer,os.path.splitext(ptn_script_fname)[0],block_name)
                  #runs pnr on top level module ptn
                  write_innovus_ptn_top_level_flow(metal_layer,os.path.splitext(ptn_script_fname)[0],flow_settings["top_level"])
                  #assembles parititons and gets results
                  #to make it easier to parse results we want to create an output dir for each set of params
                  ptn_dir, report_path, output_path = write_innovus_assemble_script(flow_settings,os.path.splitext(ptn_script_fname)[0],ptn_block_list,flow_settings["top_level"])
                  gen_dir(os.path.join(report_path,ptn_dir))
                
            os.chdir(top_abs_path)
            gen_n_trav(sta_dir)
            sta_abs_dir = os.getcwd()
            #this cycles through all modes of the design
            for mode in range(0, 2**len(flow_settings['mode_signal']) + 1):
              os.chdir(sta_abs_dir)
              mode_enabled = True if (len(flow_settings['mode_signal']) > 0) else False
              if mode_enabled:
                parameterized_sta_dir = parameterized_pnr_dir + "_" + "_".join(["mode",str(mode)])
              else:
                parameterized_sta_dir = parameterized_pnr_dir
              gen_n_trav(parameterized_sta_dir)
              param_sta_path = os.getcwd()
              ###############################
              # if(generate_flow_links):
              #   sym_link_dir = "pnr_link"
              #   if(not os.path.isdir(sym_link_dir)):
              #     sym_link_cmd = "ln -s " + param_pnr_path + " " + os.path.join(os.getcwd(),sym_link_dir)
              #     subprocess.call(sym_link_cmd,shell=True)
              #   #then go back to previous stage and create a sym_link to the next stage
              #   if(os.path.isdir(sym_link_dir)):
              #     os.chdir(sym_link_dir)
              #     sym_link_dir = "sta_link"
              #     if(not os.path.isdir(sym_link_dir)):
              #       sym_link_cmd = "ln -s " + param_sta_path + " " + os.path.join(os.getcwd(),sym_link_dir)
              #       subprocess.call(sym_link_cmd,shell=True)
              #   os.chdir(param_sta_path)
              # else:
              #   sym_link_dir = "pnr_link"
              #   if(os.path.isdir(sym_link_dir)):
              #     sym_link_cmd = "unlink " + os.path.join(os.getcwd(),sym_link_dir)
              #     print(sym_link_cmd)
              #     # subprocess.call(sym_link_cmd,shell=True)
              #   #then go back to previous stage and create a sym_link to the next stage
              #   # if(os.path.isdir(sym_link_dir)):
              #   #   os.chdir(sym_link_dir)
              #   #   sym_link_dir = "sta_link"
              #     # if(os.path.isdir(sym_link_dir)):
              #     #   print(sym_link_cmd)
              #     #   sym_link_cmd = "unlink " + os.path.join(os.getcwd(),sym_link_dir)
              #     #   subprocess.call(sym_link_cmd,shell=True)
              #   os.chdir(param_sta_path)
              ##############################
              #generate subdirs in parameterized dir
              for d in parameterized_subdirs:
                gen_dir(d)
              os.chdir(script_dir)
              fpath,report_path = write_pt_timing_script(flow_settings,mode_enabled,clock_period,mode,pnr_output_path,rel_outputs=True)
              #write_pt_power_script(flow_settings,mode_enabled,clock_period,mode,pnr_output_path,rel_outputs=True)
  write_parallel_scripts(flow_settings,top_abs_path)
  os.chdir(pre_func_dir)

def get_innovus_cmd(script_path):
  innovus_cmd = " ".join(["innovus","-no_gui","-init",script_path])
  innovus_cmd = innovus_cmd + " > " + os.path.splitext(os.path.basename(innovus_cmd.split(" ")[-1]))[0] + ".log"
  return innovus_cmd

def get_encounter_cmd(script_path):
  encounter_cmd = " ".join(["encounter","-no_gui","-init",script_path])
  encounter_cmd = encounter_cmd + " > " + os.path.splitext(os.path.basename(encounter_cmd.split(" ")[-1]))[0] + ".log"
  return encounter_cmd

def run_cmd(cmd_str):
  print("cwd: %s\n cmd: %s" %(os.getcwd(),cmd_str))
  subprocess.call(cmd_str,shell=True,executable="/bin/bash")

def run_inn_dim_specific_pnr_cmd_series(inn_command_series):
  for dim_cmds in inn_command_series:
    if(isinstance(dim_cmds,list) and len(dim_cmds) > 1):
      for cmd in dim_cmds:
        run_cmd(get_innovus_cmd(cmd))
      # pool.map(run_cmd,dim_cmds)

      #for cmd in dim_cmds:
      #Below is how one would perform nested parallelism, its not supported in the pool/threading library so will have to figure this one out later
      # threads = []
      # for cmd_str in inn_command_series:
      #   thread = threading.Thread(target=run_cmd,args=(cmd_str))
      #   threads.append(thread)
      # for thread in threads:
      #   thread.join()
      # pool.close()
    else:
      run_cmd(get_innovus_cmd(dim_cmds))
    



def get_params_from_str(param_str):
  #TODO define this parameter structure somewhere
  param_dict = {}
  params = param_str.split("_")
  for idx in range(0,len(params),2):
    param_dict[params[idx]] = params[idx+1]
  return param_dict


def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def find_lowest_cost_in_result_dict(flow_settings,result_dict):

  lowest_cost_dicts = {}
  flow_cost_dict = {
    "area": 0.0,
    "delay": 0.0,
    "power": 0.0,
    "cost": 0.0,
    "run_params":""
  }

  # for flow_type in result_dict.keys():
  #   lowest_cost_dict[flow_type] = flow_dict
  
  for flow_type, flow_dict in result_dict.items():
    param_str = ""
    lowest_cost_dict = {}
    lowest_cost_dicts[flow_type] = {}
    lowest_cost = sys.float_info.max
    lowest_cost_area = 0.0
    lowest_cost_delay = 0.0
    lowest_cost_power = 0.0

    if(flow_type == "synth" or flow_type == "pnr"):
      for run_params, param_result_dict in flow_dict.items():
        total_delay = param_result_dict["delay"]
        total_power = param_result_dict["power"]
        total_area = param_result_dict["area"]
        cur_cost = math.pow(float(total_area), float(flow_settings['area_cost_exp'])) * math.pow(float(total_delay), float(flow_settings['delay_cost_exp']))
        result_dict[flow_type][run_params]["cost"] = cur_cost
        if lowest_cost > cur_cost:
          param_str = run_params
          lowest_cost = cur_cost
          lowest_cost_area = total_area
          lowest_cost_delay = total_delay
          lowest_cost_power = total_power
      
      lowest_cost_dict["area"] = lowest_cost_area
      lowest_cost_dict["delay"] = lowest_cost_delay
      lowest_cost_dict["power"] = lowest_cost_power
      lowest_cost_dict["cost"] = lowest_cost
      lowest_cost_dict["run_params"] = param_str
      lowest_cost_dicts[flow_type] = lowest_cost_dict
    

  return lowest_cost_dicts


def parse_parallel_outputs(flow_settings):
    """
    This function parses the ASIC results directory created after running scripts generated from option of coffe flow
    """
    #Directory structure of the parallel results is as follows:
    #results_dir: 
    #--->synth
    #-------->parameterized_folder
    #------------>outputs
    #------------>reports
    #------------>work
    #------------>scripts
    #--->pnr
    #......Same as above structure....
    #--->sta
    #......Same as above structure....
    parallel_results_path = os.path.expanduser(flow_settings["parallel_hardblock_folder"])
    out_dict = {
        "pnr": {},
        "synth": {},
        "sta": {}
    }
    decimal_re = re.compile(r"\d+\.{0,1}\d*")
    timing_str = "setup_timing"
    area_str = "area"
    power_str = "power"
    violator_str = "violators"
    valid_rpt_re = re.compile("^dimlen_[0-9]+|\.[0-9]+_ptn_\w+\.rpt",re.DOTALL|re.MULTILINE)
    os.chdir(parallel_results_path)
    results_path = os.getcwd()
    for top_level_mod in os.listdir(os.getcwd()):
        os.chdir(os.path.join(results_path,top_level_mod))
        top_level_mod_path = os.getcwd()
        for flow_dir in os.listdir(os.getcwd()):
            os.chdir(os.path.join(top_level_mod_path,flow_dir))
            flow_path = os.getcwd()
            for parameterized_dir in os.listdir(os.getcwd()):
                if("period" not in parameterized_dir):
                  continue
                os.chdir(os.path.join(flow_path,parameterized_dir))
                parameterized_path = os.getcwd()
                for dir in os.listdir(os.getcwd()):
                    os.chdir(os.path.join(parameterized_path,dir))
                    dir_path = os.getcwd()
                    if(os.path.basename(dir_path) == "reports" and len(dir_path) > 0):
                        for report_file in os.listdir(os.getcwd()):
                            if( (not valid_rpt_re.search(report_file) or not os.path.isfile(report_file)) and flow_dir == "pnr"):
                              continue
                            dict_entry = ""
                            if("area" in report_file):
                                #Below is the index at which the value for total area will be found in either synth or pnr report file
                                area_idx = -2 if (flow_dir == "pnr") else 1
                                #Area report
                                fd = open(report_file,"r")
                                for line in fd:
                                    if(flow_settings["top_level"] in line):
                                        area = re.split(r"\s+",line)[area_idx]
                                dict_entry = parameterized_dir + "_" + re.sub(string=os.path.basename(os.path.splitext(report_file)[0]),pattern=area_str,repl="") #(area_str,os.path.basename(os.path.splitext(report_file)[0]))
                                # period = decode_report_str(dict_entry)
                                if(dict_entry not in out_dict[flow_dir]):
                                    out_dict[flow_dir][dict_entry] = {}
                                out_dict[flow_dir][dict_entry]["area"] = float(area)
                                fd.close()
                            elif("timing" in report_file and ".rpt" in report_file):
                                timing_met_re = re.compile(r"VIOLATED")
                                if(flow_dir == "synth" or flow_dir == "sta"):
                                  arrival_time_str = "data arrival time"
                                  lib_setup_time_str = "library setup time"    
                                  timing_str = "timing"                              
                                elif(flow_dir == "pnr"):
                                  arrival_time_str = "- Arrival Time"
                                  lib_setup_time_str = "Setup"
                                  timing_analysis_mode_str = "setup" if ("setup" in report_file) else "hold"
                                  timing_str = timing_analysis_mode_str + "_" + "timing"
                                #timing report
                                fd = open(report_file,"r")
                                text = fd.read()
                                for line in text.split("\n"):
                                    if(arrival_time_str in line):
                                        arrival_time = float(decimal_re.findall(line)[0])
                                    elif(lib_setup_time_str in line):
                                        lib_setup_time = float(decimal_re.findall(line)[0])
                                total_del = arrival_time + lib_setup_time
                                dict_entry = parameterized_dir + "_" + re.sub(string=os.path.basename(os.path.splitext(report_file)[0]),pattern=timing_str,repl="")
                                if(dict_entry not in out_dict[flow_dir]):
                                    out_dict[flow_dir][dict_entry] = {}
                                out_dict[flow_dir][dict_entry]["delay"] = float(truncate(total_del,3))
                                if(timing_met_re.search(text)):
                                    timing_met = False
                                else:
                                    timing_met = True
                                out_dict[flow_dir][dict_entry]["timing_met_"+timing_analysis_mode_str] = timing_met
                                fd.close()
                            elif("power" in report_file and ".rpt" in report_file):
                                #power report
                                fd = open(report_file,"r")
                                for line in fd:
                                  if(flow_dir == "sta" or flow_dir == "synth"):
                                      if 'Total Dynamic Power' in line:
                                        total_power = re.findall(r'\d+\.{0,1}\d*', line)
                                        total_power = float(total_power[0])
                                        #TODO figure out power units
                                        # if 'mW' in line:
                                        #   total_dynamic_power[0] *= 0.001
                                        # elif 'uw' in line:
                                        #   total_dynamic_power[0] *= 0.000001
                                        # else:
                                        #   total_dynamic_power[0] = 0
                                  elif(flow_dir == "pnr"):
                                      if("Total Power:" in line):
                                          total_power = float(decimal_re.search(line).group(0))
                                dict_entry = parameterized_dir + "_" + re.sub(string=os.path.basename(os.path.splitext(report_file)[0]),pattern=power_str,repl="")
                                if(dict_entry not in out_dict[flow_dir]):
                                    out_dict[flow_dir][dict_entry] = {}
                                out_dict[flow_dir][dict_entry]["power"] = float(truncate(total_power,3))
                                fd.close()
                            if(dict_entry != ""):
                                #grabbing link dimensions from the fname
                                dict_ent_params = dict_entry.split("_")
                                dim_len = 0
                                period = 0
                                for idx,e in enumerate(dict_ent_params):
                                    if("len" in e):
                                        dim_len = float(dict_ent_params[idx+1])
                                    elif("period" in e):
                                        period = float(dict_ent_params[idx+1])
                                out_dict[flow_dir][dict_entry]["dim_len"] = float(dim_len)  
                                out_dict[flow_dir][dict_entry]["period"] = float(period)                      
    return out_dict


def hardblock_parallel_flow(flow_settings):
  pre_flow_dir = os.getcwd()
  #This expects cwd to be asic_work
  hardblock_script_gen(flow_settings)
  #make sure to be in the parallel_hardblock_folder
  os.chdir(flow_settings["parallel_hardblock_folder"])
  #PARAM
  flow_integration_settings = {
    "run_synth" : False,
    "run_pnr" : True,
    "run_sta" : False
  }
  #PARAM
  flow_settings["override_pnr_outputs"] = False


  #this dict will filter the parallel run script s.t only the parameters specified will be run
  #PARAM
  run_param_filters = {
    "period" : ["1","0.75"], #["0.5","0.75", "1", "1.53", "2.0", "4"], 
    "wiremdl" : ["WireAreaLowkAgr"],
    "mlayer" : ["8"],
    "util" : ["0.70"],
  }

  ########################### PARALLEL SYNTHESIS SECTION ###########################
  if flow_integration_settings["run_synth"]:
    # synth_parallel_work_path = os.path.join(os.getcwd(),"synth","synth_parallel_work")
    synth_parallel_work_path="/autofs/fs1.ece/fs1.eecg.vaughn/morestep/COFFE/output_files/network_on_chip/asic_work/router_wrap/synth/synth_parallel_work"
    os.chdir(synth_parallel_work_path)
    #setup the scripts to be able to run
    pll_synth_scripts = glob.glob(os.path.join(synth_parallel_work_path,"scripts","*"))
    pll_synth_scripts.append("./top_level_parallel.sh")
    for s in pll_synth_scripts:
      os.chmod(s,stat.S_IRWXU)

    top_pll_synth_cmds = ["top_level_parallel.sh"]
    parallel_synth_p = subprocess.Popen(top_pll_synth_cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = parallel_synth_p.communicate()
    print(stdout,stderr)
  ########################### PARALLEL SYNTHESIS SECTION ###########################
  ########################### PARALLEL PNR SECTION #################################
  if flow_integration_settings["run_pnr"]:
    pnr_parallel_path="/autofs/fs1.ece/fs1.eecg.vaughn/morestep/COFFE/output_files/network_on_chip/asic_work/router_wrap/pnr"
    # pnr_parallel_path = os.path.join(os.getcwd(),"pnr","pnr_parallel_work")
    #DEPENDANCY OF PNR SCRIPTS
    # run_gen_blocks for each ptn block in design [] denotes parallelism
    # gen_fp(dim) -> gen_ptns(dim) -> [gen_blocks(dim)]  -> pnr(top_lvl) -> assemble(all_parts_of_design) 

    #These settings are only to filter the dimensions being run for the fp ptn flow
    fp_dim = 948.4
    scaling_array = [1,2,3,4,5,8,10]
    #only scripts with dims in the below list will be evauluated
    scaled_dims = [fp_dim*fac for fac in scaling_array]
    if(flow_settings["partition_flag"]):
      os.chdir(pnr_parallel_path)
      for param_dir in os.listdir(pnr_parallel_path):
        continue_flag = False
        if("period" not in param_dir): 
          os.chdir(pnr_parallel_path)
          continue
        # print(os.getcwd())
        os.chdir(param_dir)
        #Before anything else use filter to only run the selected params:
        param_dict = get_params_from_str(param_dir)
        for cur_key,cur_val in param_dict.items():
          if cur_key in run_param_filters.keys():
            if all(cur_val != val for val in run_param_filters[cur_key]):
              continue_flag = True
              break
            else:
              continue_flag = False
        if(continue_flag):
          os.chdir(pnr_parallel_path)
          continue
        # sys.exit(1)
        #iterate through parameterized pnr dirs
        #loop through scripts in pnr script path
        #First group the scripts according to their dimensions
        dim_grouped_scripts = []
        for dim in scaled_dims:
          dim_group = [f for f in os.listdir("scripts") if str(dim) in f]
          dim_grouped_scripts.append(dim_group)
        order_of_exec_pnr_per_dim = []
        for group in dim_grouped_scripts:
          #Now group according to order of exec
          fp_gen_script = [f for f in group if "fp_gen" in f]
          ptn_script = [f for f in group if "ptn.tcl" in f]
          block_scripts = [f for f in group if "block" in f]
          toplvl_script = [f for f in group if "toplvl" in f]
          assembly_script = [f for f in group if "assembly" in f]
          order_of_exec_pnr_scripts = [fp_gen_script,ptn_script,block_scripts,toplvl_script,assembly_script]
          order_of_exec_pnr_scripts = [e[0] if len(e) == 1 else e for e in order_of_exec_pnr_scripts]
          order_of_exec_pnr_per_dim.append(order_of_exec_pnr_scripts)


        os.chdir("work")
        output_dir = os.path.join("..","outputs")

        cmd_series_list = []
        for inn_command_series in order_of_exec_pnr_per_dim:
          
          #filter out commands which are out of bounds of our dims we want to evaluate
          if not any(str(dim) in inn_command_series[0] for dim in scaled_dims):
            print("dim out of dimension list, not running %s... " % (inn_command_series[0]))
            continue

          if(not flow_settings["override_pnr_outputs"]):
            #if theres already a design saved for the fp flow skip it
            saved_design = os.path.join(output_dir,os.path.splitext(inn_command_series[1])[0]+"_assembled.dat")
            if(os.path.exists(saved_design)):
              print("found %s, Skipping..." % (saved_design))
              print(os.getcwd())
              continue

            #if top level flow has been run only run the assembly
            saved_tl_imp = os.path.join(os.path.splitext(inn_command_series[1])[0],flow_settings["top_level"],flow_settings["top_level"]+"_imp")
            #if partition flow has been run only run top lvl + assembly
            ptn_dir = os.path.join(os.path.splitext(inn_command_series[1])[0])
            cmds = []
            for cmd in inn_command_series:
              if(isinstance(cmd,str)):
                cmds.append(os.path.join("..","scripts",cmd))
              elif(isinstance(cmd,list)):
                blk_cmds = [os.path.join("..","scripts",blk_cmd) for blk_cmd in cmd]
                cmds.append(blk_cmds)
            if(os.path.isfile(saved_tl_imp)):
              print("found top level imp, running only assembly")
              print(os.getcwd())
              del cmds[0:3]
            elif(os.path.isdir(ptn_dir)):
              print("found ptn dir, running only blocks + toplvl + assembly")
              print(os.getcwd())
              del cmds[0:2]
            cmd_series_list.append(cmds)
          else:
            # cmd_series_list = order_of_exec_pnr_per_dim
            cmd_series_list = [[os.path.join("..","scripts",cmd) for cmd in cmds] for cmds in order_of_exec_pnr_per_dim]

        #flow_settings["mp_num_cores"]
        pool = mp.Pool()
        #execute all scripts
        pool.map(run_inn_dim_specific_pnr_cmd_series,cmd_series_list)
        pool.close()
        os.chdir(pnr_parallel_path)
    else:
      pnr_parallel_work_path="/autofs/fs1.ece/fs1.eecg.vaughn/morestep/COFFE/output_files/network_on_chip/asic_work/router_wrap/pnr/pnr_parallel_work"
      # pnr_parallel_work_path = os.path.join(os.getcwd(),"pnr","pnr_parallel_work")
      os.chdir(pnr_parallel_work_path)
      #setup the scripts to be able to run
      pll_pnr_scripts = glob.glob(os.path.join(pnr_parallel_work_path,"scripts","*"))
      pll_pnr_scripts.append("top_level_parallel.sh")
      for s in pll_pnr_scripts:
        os.chmod(s,stat.S_IRWXU)

      #Runs the parallel synthesis across params
      top_pll_synth_cmds = ["top_level_parallel.sh"]
      parallel_pnr_p = subprocess.Popen(top_pll_synth_cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = parallel_pnr_p.communicate()

  ########################### PARALLEL PNR SECTION #################################
  ########################### PARALLEL STA SECTION #################################
    #pnr_parallel_work_path="/autofs/fs1.ece/fs1.eecg.vaughn/morestep/COFFE/output_files/network_on_chip/asic_work/router_wrap/sta/sta_parallel_work"
    if(flow_integration_settings["run_sta"]):
      sta_parallel_work_path="/autofs/fs1.ece/fs1.eecg.vaughn/morestep/COFFE/output_files/network_on_chip/asic_work/router_wrap/sta/sta_parallel_work"
      # sta_parallel_work_path = os.path.join(os.getcwd(),flow_settings["top_level"],"sta","sta_parallel_work")
      os.chdir(sta_parallel_work_path)
      #setup the scripts to be able to run
      pll_sta_scripts = glob.glob(os.path.join(sta_parallel_work_path,"scripts","*"))
      pll_sta_scripts.append("top_level_parallel.sh")
      for s in pll_pnr_scripts:
        os.chmod(s,stat.S_IRWXU)

      #Runs the parallel synthesis across params
      top_pll_synth_cmds = ["top_level_parallel.sh"]
      parallel_sta_p = subprocess.Popen(top_pll_synth_cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = parallel_sta_p.communicate()
  ########################### PARALLEL STA SECTION #################################
  
  #hardblock flow stuff
  lowest_cost = sys.float_info.max
  lowest_cost_area = 1.0
  lowest_cost_delay = 1.0
  lowest_cost_power = 1.0
  
  os.chdir(pre_flow_dir)
  return (float(lowest_cost_area), float(lowest_cost_delay), float(lowest_cost_power))

# wire loads in the library are WireAreaLowkCon WireAreaLowkAgr WireAreaForZero
def hardblock_flow(flow_settings): 
  cur_env = os.environ.copy()
  processed_flow_settings = flow_settings
  flow_settings_pre_process(processed_flow_settings,cur_env)
  # Enter all the signals that change modes
  lowest_cost = sys.float_info.max
  lowest_cost_area = 1.0
  lowest_cost_delay = 1.0
  lowest_cost_power = 1.0
  subprocess.call("mkdir -p " + flow_settings['synth_folder'] + "\n", shell=True)
  subprocess.call("mkdir -p " + flow_settings['pr_folder'] + "\n", shell=True)
  subprocess.call("mkdir -p " + flow_settings['primetime_folder'] + "\n", shell=True)
  # Make sure we managed to read the design files
  assert len(processed_flow_settings["design_files"]) >= 1
  try:
    for clock_period in flow_settings['clock_period']:
      for wire_selection in flow_settings['wire_selection']:
        synth_report_str,syn_output_path = run_synth(processed_flow_settings,clock_period,wire_selection)
        for metal_layer in flow_settings['metal_layers']:
          for core_utilization in flow_settings['core_utilization']:
            #set the pnr flow to accept the correct name for flattened netlist
            pnr_report_str, pnr_output_path, total_area = run_pnr(processed_flow_settings,metal_layer,core_utilization,synth_report_str,syn_output_path)
            mode_enabled = True if len(flow_settings['mode_signal']) > 0 else False
            the_power = 0.0
            # Optional: use modelsim to generate an activity file for the design:
            if flow_settings['generate_activity_file'] is True:
              run_sim()
            #loops over every combination of user inputted modes to set the set_case_analysis value (determines value of mode mux)
            for x in range(0, 2**len(flow_settings['mode_signal']) + 1):
              library_setup_time, data_arrival_time, total_delay, total_dynamic_power = run_power_timing(flow_settings,mode_enabled,clock_period,x,pnr_report_str,pnr_output_path)
              # write the final report file:
              if mode_enabled and x <2**len(flow_settings['mode_signal']):
                file = open("report_mode" + str(x) + "_" + str(flow_settings['top_level']) + "_" + str(clock_period) + "_" + str(wire_selection) + "_wire_" + str(metal_layer) + "_" + str(core_utilization) + ".txt" ,"w")
              else:
                file = open("report_" + str(flow_settings['top_level']) + "_" + str(clock_period) + "_" + str(wire_selection) + "_wire_" + str(metal_layer) + "_" + str(core_utilization) + ".txt" ,"w")
              file.write("total area = "  + str(total_area[0]) +  " um^2 \n")
              file.write("total delay = " + str(total_delay) + " ns \n")
              file.write("total power = " + str(total_dynamic_power[0]) + " W \n")
              file.close()
              if total_dynamic_power[0] > the_power:
                the_power = total_dynamic_power[0]
              if lowest_cost > math.pow(float(total_area[0]), float(flow_settings['area_cost_exp'])) * math.pow(float(total_delay), float(flow_settings['delay_cost_exp'])):
                lowest_cost = math.pow(float(total_area[0]), float(flow_settings['area_cost_exp'])) * math.pow(float(total_delay), float(flow_settings['delay_cost_exp']))
                lowest_cost_area = float(total_area[0])
                lowest_cost_delay = float(total_delay)
                lowest_cost_power = float(the_power)
              del total_dynamic_power[:]
              del library_setup_time[:]
              del data_arrival_time[:]
              if(flow_settings["hb_run_type"] == "solo"):
                #This catches the exception and continues running the program (python doesnt make breaking out of nested loop easy...)
                print("solo run setting selected, only running single set of hardblock parameters...")
                sys.exit(1)
  except Exception as e:
    print("CAUGHT %s" % (e))
    pass
    
  return (float(lowest_cost_area), float(lowest_cost_delay), float(lowest_cost_power))

