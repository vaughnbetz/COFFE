# Hard block script for COFFE flow.
# Created by: Sadegh Yazdanshenas
# Email: sadegh.yazdanshenas@mail.utoronto.ca
# University of Toronto, 2017

import os
import sys
import subprocess
import re
import shutil
import math


"""
Notes:
We have a data structure for parameters needed in the flow, but there are other params which are like the output paths for the synthesis stag
it may make more sense to have a data structure containing paths for connecting stages of the flow synth->pnr->sta
"""
def file_write_ln(fd, line):
  fd.write(line + "\n")

def write_synth_tcl(flow_settings,clock_period,wire_selection,rel_outputs=False,ptn_flag=False):
  """
  Writes the dc_script.tcl file which will be executed to run synthesis using Synopsys Design Compiler, tested under 2017 version.
  Relative reporting parameter is to accomodate legacy use of function while allowing the new version to run many scripts in parallel
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
    "define_design_lib WORK -path ./WORK", #TODO make the work dir different s.t I can parallelize this
    analyze_cmd_str,
    "elaborate $my_top_level",
    "current_design $my_top_level",
    "check_design > " +                             os.path.join(report_path,"check_precompile.rpt"), #DEPENDANCY
    "link",
    "uniquify",
    wire_ld_sel_str,
    "set my_period " + str(clock_period),
    "set find_clock [ find port [list $my_clock_pin] ]",
    "if { $find_clock != [list] } { ",
    "set clk_name $my_clock_pin ",
    "create_clock -period $my_period $clk_name}",
    "set_ungroup vcr_top_1 false", #DEPENDANCY
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
    #"report_cells > " +                             os.path.join(report_path,"cells.rpt"),
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

  # WARNING this hardpath for the check.rpt will only work if write_synth_tcl has the rel_outputs param set to False 
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


def write_edit_port_script():
  """
  Currently this only works for the NoC ports in the future these would have to be autogenerated, editPorts for NoC
  """
  fd = open("port_vars.tcl","w")
  file_lines = [
    #side 0
    "set my_0_ch_in_ports {\"channel_in_ip[0]\" \"channel_in_ip[1]\" \"channel_in_ip[2]\" \"channel_in_ip[3]\" \"channel_in_ip[4]\" \"channel_in_ip[5]\" \"channel_in_ip[6]\" \"channel_in_ip[7]\" \"channel_in_ip[8]\" \"channel_in_ip[9]\" \"channel_in_ip[10]\" \"channel_in_ip[11]\" \"channel_in_ip[12]\" \"channel_in_ip[13]\" \"channel_in_ip[14]\" \"channel_in_ip[15]\" \"channel_in_ip[16]\" \"channel_in_ip[17]\" \"channel_in_ip[18]\" \"channel_in_ip[19]\" \"channel_in_ip[20]\" \"channel_in_ip[21]\" \"channel_in_ip[22]\" \"channel_in_ip[23]\" \"channel_in_ip[24]\" \"channel_in_ip[25]\" \"channel_in_ip[26]\" \"channel_in_ip[27]\" \"channel_in_ip[28]\" \"channel_in_ip[29]\" \"channel_in_ip[30]\" \"channel_in_ip[31]\" \"channel_in_ip[32]\" \"channel_in_ip[33]\" \"channel_in_ip[34]\" \"channel_in_ip[35]\" \"channel_in_ip[36]\" \"channel_in_ip[37]\" \"channel_in_ip[38]\" \"channel_in_ip[39]\" \"channel_in_ip[40]\" \"channel_in_ip[41]\" \"channel_in_ip[42]\" \"channel_in_ip[43]\" \"channel_in_ip[44]\" \"channel_in_ip[45]\" \"channel_in_ip[46]\" \"channel_in_ip[47]\" \"channel_in_ip[48]\" \"channel_in_ip[49]\" \"channel_in_ip[50]\" \"channel_in_ip[51]\" \"channel_in_ip[52]\" \"channel_in_ip[53]\" \"channel_in_ip[54]\" \"channel_in_ip[55]\" \"channel_in_ip[56]\" \"channel_in_ip[57]\" \"channel_in_ip[58]\" \"channel_in_ip[59]\" \"channel_in_ip[60]\" \"channel_in_ip[61]\" \"channel_in_ip[62]\" \"channel_in_ip[63]\" \"channel_in_ip[64]\" \"channel_in_ip[65]\" \"channel_in_ip[66]\" \"channel_in_ip[67]\"}",
    #side 1
    "set my_1_ch_in_ports {\"channel_in_ip[68]\" \"channel_in_ip[69]\" \"channel_in_ip[70]\" \"channel_in_ip[71]\" \"channel_in_ip[72]\" \"channel_in_ip[73]\" \"channel_in_ip[74]\" \"channel_in_ip[75]\" \"channel_in_ip[76]\" \"channel_in_ip[77]\" \"channel_in_ip[78]\" \"channel_in_ip[79]\" \"channel_in_ip[80]\" \"channel_in_ip[81]\" \"channel_in_ip[82]\" \"channel_in_ip[83]\" \"channel_in_ip[84]\" \"channel_in_ip[85]\" \"channel_in_ip[86]\" \"channel_in_ip[87]\" \"channel_in_ip[88]\" \"channel_in_ip[89]\" \"channel_in_ip[90]\" \"channel_in_ip[91]\" \"channel_in_ip[92]\" \"channel_in_ip[93]\" \"channel_in_ip[94]\" \"channel_in_ip[95]\" \"channel_in_ip[96]\" \"channel_in_ip[97]\" \"channel_in_ip[98]\" \"channel_in_ip[99]\" \"channel_in_ip[100]\" \"channel_in_ip[101]\" \"channel_in_ip[102]\" \"channel_in_ip[103]\" \"channel_in_ip[104]\" \"channel_in_ip[105]\" \"channel_in_ip[106]\" \"channel_in_ip[107]\" \"channel_in_ip[108]\" \"channel_in_ip[109]\" \"channel_in_ip[110]\" \"channel_in_ip[111]\" \"channel_in_ip[112]\" \"channel_in_ip[113]\" \"channel_in_ip[114]\" \"channel_in_ip[115]\" \"channel_in_ip[116]\" \"channel_in_ip[117]\" \"channel_in_ip[118]\" \"channel_in_ip[119]\" \"channel_in_ip[120]\" \"channel_in_ip[121]\" \"channel_in_ip[122]\" \"channel_in_ip[123]\" \"channel_in_ip[124]\" \"channel_in_ip[125]\" \"channel_in_ip[126]\" \"channel_in_ip[127]\" \"channel_in_ip[128]\" \"channel_in_ip[129]\" \"channel_in_ip[130]\" \"channel_in_ip[131]\" \"channel_in_ip[132]\" \"channel_in_ip[133]\" \"channel_in_ip[134]\" \"channel_in_ip[135]\"}",
    #side 2
    "set my_2_ch_in_ports {\"channel_in_ip[136]\" \"channel_in_ip[137]\" \"channel_in_ip[138]\" \"channel_in_ip[139]\" \"channel_in_ip[140]\" \"channel_in_ip[141]\" \"channel_in_ip[142]\" \"channel_in_ip[143]\" \"channel_in_ip[144]\" \"channel_in_ip[145]\" \"channel_in_ip[146]\" \"channel_in_ip[147]\" \"channel_in_ip[148]\" \"channel_in_ip[149]\" \"channel_in_ip[150]\" \"channel_in_ip[151]\" \"channel_in_ip[152]\" \"channel_in_ip[153]\" \"channel_in_ip[154]\" \"channel_in_ip[155]\" \"channel_in_ip[156]\" \"channel_in_ip[157]\" \"channel_in_ip[158]\" \"channel_in_ip[159]\" \"channel_in_ip[160]\" \"channel_in_ip[161]\" \"channel_in_ip[162]\" \"channel_in_ip[163]\" \"channel_in_ip[164]\" \"channel_in_ip[165]\" \"channel_in_ip[166]\" \"channel_in_ip[167]\" \"channel_in_ip[168]\" \"channel_in_ip[169]\" \"channel_in_ip[170]\" \"channel_in_ip[171]\" \"channel_in_ip[172]\" \"channel_in_ip[173]\" \"channel_in_ip[174]\" \"channel_in_ip[175]\" \"channel_in_ip[176]\" \"channel_in_ip[177]\" \"channel_in_ip[178]\" \"channel_in_ip[179]\" \"channel_in_ip[180]\" \"channel_in_ip[181]\" \"channel_in_ip[182]\" \"channel_in_ip[183]\" \"channel_in_ip[184]\" \"channel_in_ip[185]\" \"channel_in_ip[186]\" \"channel_in_ip[187]\" \"channel_in_ip[188]\" \"channel_in_ip[189]\" \"channel_in_ip[190]\" \"channel_in_ip[191]\" \"channel_in_ip[192]\" \"channel_in_ip[193]\" \"channel_in_ip[194]\" \"channel_in_ip[195]\" \"channel_in_ip[196]\" \"channel_in_ip[197]\" \"channel_in_ip[198]\" \"channel_in_ip[199]\" \"channel_in_ip[200]\" \"channel_in_ip[201]\" \"channel_in_ip[202]\" \"channel_in_ip[203]\"}",
    #side 3 (68 + 68)
    "set my_3_ch_in_ports {\"channel_in_ip[204]\" \"channel_in_ip[205]\" \"channel_in_ip[206]\" \"channel_in_ip[207]\" \"channel_in_ip[208]\" \"channel_in_ip[209]\" \"channel_in_ip[210]\" \"channel_in_ip[211]\" \"channel_in_ip[212]\" \"channel_in_ip[213]\" \"channel_in_ip[214]\" \"channel_in_ip[215]\" \"channel_in_ip[216]\" \"channel_in_ip[217]\" \"channel_in_ip[218]\" \"channel_in_ip[219]\" \"channel_in_ip[220]\" \"channel_in_ip[221]\" \"channel_in_ip[222]\" \"channel_in_ip[223]\" \"channel_in_ip[224]\" \"channel_in_ip[225]\" \"channel_in_ip[226]\" \"channel_in_ip[227]\" \"channel_in_ip[228]\" \"channel_in_ip[229]\" \"channel_in_ip[230]\" \"channel_in_ip[231]\" \"channel_in_ip[232]\" \"channel_in_ip[233]\" \"channel_in_ip[234]\" \"channel_in_ip[235]\" \"channel_in_ip[236]\" \"channel_in_ip[237]\" \"channel_in_ip[238]\" \"channel_in_ip[239]\" \"channel_in_ip[240]\" \"channel_in_ip[241]\" \"channel_in_ip[242]\" \"channel_in_ip[243]\" \"channel_in_ip[244]\" \"channel_in_ip[245]\" \"channel_in_ip[246]\" \"channel_in_ip[247]\" \"channel_in_ip[248]\" \"channel_in_ip[249]\" \"channel_in_ip[250]\" \"channel_in_ip[251]\" \"channel_in_ip[252]\" \"channel_in_ip[253]\" \"channel_in_ip[254]\" \"channel_in_ip[255]\" \"channel_in_ip[256]\" \"channel_in_ip[257]\" \"channel_in_ip[258]\" \"channel_in_ip[259]\" \"channel_in_ip[260]\" \"channel_in_ip[261]\" \"channel_in_ip[262]\" \"channel_in_ip[263]\" \"channel_in_ip[264]\" \"channel_in_ip[265]\" \"channel_in_ip[266]\" \"channel_in_ip[267]\" \"channel_in_ip[268]\" \"channel_in_ip[269]\" \"channel_in_ip[270]\" \"channel_in_ip[271]\" \"channel_in_ip[272]\" \"channel_in_ip[273]\" \"channel_in_ip[274]\" \"channel_in_ip[275]\" \"channel_in_ip[276]\" \"channel_in_ip[277]\" \"channel_in_ip[278]\" \"channel_in_ip[279]\" \"channel_in_ip[280]\" \"channel_in_ip[281]\" \"channel_in_ip[282]\" \"channel_in_ip[283]\" \"channel_in_ip[284]\" \"channel_in_ip[285]\" \"channel_in_ip[286]\" \"channel_in_ip[287]\" \"channel_in_ip[288]\" \"channel_in_ip[289]\" \"channel_in_ip[290]\" \"channel_in_ip[291]\" \"channel_in_ip[292]\" \"channel_in_ip[293]\" \"channel_in_ip[294]\" \"channel_in_ip[295]\" \"channel_in_ip[296]\" \"channel_in_ip[297]\" \"channel_in_ip[298]\" \"channel_in_ip[299]\" \"channel_in_ip[300]\" \"channel_in_ip[301]\" \"channel_in_ip[302]\" \"channel_in_ip[303]\" \"channel_in_ip[304]\" \"channel_in_ip[305]\" \"channel_in_ip[306]\" \"channel_in_ip[307]\" \"channel_in_ip[308]\" \"channel_in_ip[309]\" \"channel_in_ip[310]\" \"channel_in_ip[311]\" \"channel_in_ip[312]\" \"channel_in_ip[313]\" \"channel_in_ip[314]\" \"channel_in_ip[315]\" \"channel_in_ip[316]\" \"channel_in_ip[317]\" \"channel_in_ip[318]\" \"channel_in_ip[319]\" \"channel_in_ip[320]\" \"channel_in_ip[321]\" \"channel_in_ip[322]\" \"channel_in_ip[323]\" \"channel_in_ip[324]\" \"channel_in_ip[325]\" \"channel_in_ip[326]\" \"channel_in_ip[327]\" \"channel_in_ip[328]\" \"channel_in_ip[329]\" \"channel_in_ip[330]\" \"channel_in_ip[331]\" \"channel_in_ip[332]\" \"channel_in_ip[333]\" \"channel_in_ip[334]\" \"channel_in_ip[335]\" \"channel_in_ip[336]\" \"channel_in_ip[337]\" \"channel_in_ip[338]\" \"channel_in_ip[339]\"}",

    #side 0
    "set my_0_ch_out_ports {\"channel_out_op[0]\" \"channel_out_op[1]\" \"channel_out_op[2]\" \"channel_out_op[3]\" \"channel_out_op[4]\" \"channel_out_op[5]\" \"channel_out_op[6]\" \"channel_out_op[7]\" \"channel_out_op[8]\" \"channel_out_op[9]\" \"channel_out_op[10]\" \"channel_out_op[11]\" \"channel_out_op[12]\" \"channel_out_op[13]\" \"channel_out_op[14]\" \"channel_out_op[15]\" \"channel_out_op[16]\" \"channel_out_op[17]\" \"channel_out_op[18]\" \"channel_out_op[19]\" \"channel_out_op[20]\" \"channel_out_op[21]\" \"channel_out_op[22]\" \"channel_out_op[23]\" \"channel_out_op[24]\" \"channel_out_op[25]\" \"channel_out_op[26]\" \"channel_out_op[27]\" \"channel_out_op[28]\" \"channel_out_op[29]\" \"channel_out_op[30]\" \"channel_out_op[31]\" \"channel_out_op[32]\" \"channel_out_op[33]\" \"channel_out_op[34]\" \"channel_out_op[35]\" \"channel_out_op[36]\" \"channel_out_op[37]\" \"channel_out_op[38]\" \"channel_out_op[39]\" \"channel_out_op[40]\" \"channel_out_op[41]\" \"channel_out_op[42]\" \"channel_out_op[43]\" \"channel_out_op[44]\" \"channel_out_op[45]\" \"channel_out_op[46]\" \"channel_out_op[47]\" \"channel_out_op[48]\" \"channel_out_op[49]\" \"channel_out_op[50]\" \"channel_out_op[51]\" \"channel_out_op[52]\" \"channel_out_op[53]\" \"channel_out_op[54]\" \"channel_out_op[55]\" \"channel_out_op[56]\" \"channel_out_op[57]\" \"channel_out_op[58]\" \"channel_out_op[59]\" \"channel_out_op[60]\" \"channel_out_op[61]\" \"channel_out_op[62]\" \"channel_out_op[63]\" \"channel_out_op[64]\" \"channel_out_op[65]\" \"channel_out_op[66]\" \"channel_out_op[67]\"}",
    #side 1
    "set my_1_ch_out_ports {\"channel_out_op[68]\" \"channel_out_op[69]\" \"channel_out_op[70]\" \"channel_out_op[71]\" \"channel_out_op[72]\" \"channel_out_op[73]\" \"channel_out_op[74]\" \"channel_out_op[75]\" \"channel_out_op[76]\" \"channel_out_op[77]\" \"channel_out_op[78]\" \"channel_out_op[79]\" \"channel_out_op[80]\" \"channel_out_op[81]\" \"channel_out_op[82]\" \"channel_out_op[83]\" \"channel_out_op[84]\" \"channel_out_op[85]\" \"channel_out_op[86]\" \"channel_out_op[87]\" \"channel_out_op[88]\" \"channel_out_op[89]\" \"channel_out_op[90]\" \"channel_out_op[91]\" \"channel_out_op[92]\" \"channel_out_op[93]\" \"channel_out_op[94]\" \"channel_out_op[95]\" \"channel_out_op[96]\" \"channel_out_op[97]\" \"channel_out_op[98]\" \"channel_out_op[99]\" \"channel_out_op[100]\" \"channel_out_op[101]\" \"channel_out_op[102]\" \"channel_out_op[103]\" \"channel_out_op[104]\" \"channel_out_op[105]\" \"channel_out_op[106]\" \"channel_out_op[107]\" \"channel_out_op[108]\" \"channel_out_op[109]\" \"channel_out_op[110]\" \"channel_out_op[111]\" \"channel_out_op[112]\" \"channel_out_op[113]\" \"channel_out_op[114]\" \"channel_out_op[115]\" \"channel_out_op[116]\" \"channel_out_op[117]\" \"channel_out_op[118]\" \"channel_out_op[119]\" \"channel_out_op[120]\" \"channel_out_op[121]\" \"channel_out_op[122]\" \"channel_out_op[123]\" \"channel_out_op[124]\" \"channel_out_op[125]\" \"channel_out_op[126]\" \"channel_out_op[127]\" \"channel_out_op[128]\" \"channel_out_op[129]\" \"channel_out_op[130]\" \"channel_out_op[131]\" \"channel_out_op[132]\" \"channel_out_op[133]\" \"channel_out_op[134]\" \"channel_out_op[135]\"}",
    #side 2
    "set my_2_ch_out_ports {\"channel_out_op[136]\" \"channel_out_op[137]\" \"channel_out_op[138]\" \"channel_out_op[139]\" \"channel_out_op[140]\" \"channel_out_op[141]\" \"channel_out_op[142]\" \"channel_out_op[143]\" \"channel_out_op[144]\" \"channel_out_op[145]\" \"channel_out_op[146]\" \"channel_out_op[147]\" \"channel_out_op[148]\" \"channel_out_op[149]\" \"channel_out_op[150]\" \"channel_out_op[151]\" \"channel_out_op[152]\" \"channel_out_op[153]\" \"channel_out_op[154]\" \"channel_out_op[155]\" \"channel_out_op[156]\" \"channel_out_op[157]\" \"channel_out_op[158]\" \"channel_out_op[159]\" \"channel_out_op[160]\" \"channel_out_op[161]\" \"channel_out_op[162]\" \"channel_out_op[163]\" \"channel_out_op[164]\" \"channel_out_op[165]\" \"channel_out_op[166]\" \"channel_out_op[167]\" \"channel_out_op[168]\" \"channel_out_op[169]\" \"channel_out_op[170]\" \"channel_out_op[171]\" \"channel_out_op[172]\" \"channel_out_op[173]\" \"channel_out_op[174]\" \"channel_out_op[175]\" \"channel_out_op[176]\" \"channel_out_op[177]\" \"channel_out_op[178]\" \"channel_out_op[179]\" \"channel_out_op[180]\" \"channel_out_op[181]\" \"channel_out_op[182]\" \"channel_out_op[183]\" \"channel_out_op[184]\" \"channel_out_op[185]\" \"channel_out_op[186]\" \"channel_out_op[187]\" \"channel_out_op[188]\" \"channel_out_op[189]\" \"channel_out_op[190]\" \"channel_out_op[191]\" \"channel_out_op[192]\" \"channel_out_op[193]\" \"channel_out_op[194]\" \"channel_out_op[195]\" \"channel_out_op[196]\" \"channel_out_op[197]\" \"channel_out_op[198]\" \"channel_out_op[199]\" \"channel_out_op[200]\" \"channel_out_op[201]\" \"channel_out_op[202]\" \"channel_out_op[203]\"}",
    #side 3 (68 + 68)
    "set my_3_ch_out_ports {\"channel_out_op[204]\" \"channel_out_op[205]\" \"channel_out_op[206]\" \"channel_out_op[207]\" \"channel_out_op[208]\" \"channel_out_op[209]\" \"channel_out_op[210]\" \"channel_out_op[211]\" \"channel_out_op[212]\" \"channel_out_op[213]\" \"channel_out_op[214]\" \"channel_out_op[215]\" \"channel_out_op[216]\" \"channel_out_op[217]\" \"channel_out_op[218]\" \"channel_out_op[219]\" \"channel_out_op[220]\" \"channel_out_op[221]\" \"channel_out_op[222]\" \"channel_out_op[223]\" \"channel_out_op[224]\" \"channel_out_op[225]\" \"channel_out_op[226]\" \"channel_out_op[227]\" \"channel_out_op[228]\" \"channel_out_op[229]\" \"channel_out_op[230]\" \"channel_out_op[231]\" \"channel_out_op[232]\" \"channel_out_op[233]\" \"channel_out_op[234]\" \"channel_out_op[235]\" \"channel_out_op[236]\" \"channel_out_op[237]\" \"channel_out_op[238]\" \"channel_out_op[239]\" \"channel_out_op[240]\" \"channel_out_op[241]\" \"channel_out_op[242]\" \"channel_out_op[243]\" \"channel_out_op[244]\" \"channel_out_op[245]\" \"channel_out_op[246]\" \"channel_out_op[247]\" \"channel_out_op[248]\" \"channel_out_op[249]\" \"channel_out_op[250]\" \"channel_out_op[251]\" \"channel_out_op[252]\" \"channel_out_op[253]\" \"channel_out_op[254]\" \"channel_out_op[255]\" \"channel_out_op[256]\" \"channel_out_op[257]\" \"channel_out_op[258]\" \"channel_out_op[259]\" \"channel_out_op[260]\" \"channel_out_op[261]\" \"channel_out_op[262]\" \"channel_out_op[263]\" \"channel_out_op[264]\" \"channel_out_op[265]\" \"channel_out_op[266]\" \"channel_out_op[267]\" \"channel_out_op[268]\" \"channel_out_op[269]\" \"channel_out_op[270]\" \"channel_out_op[271]\" \"channel_out_op[272]\" \"channel_out_op[273]\" \"channel_out_op[274]\" \"channel_out_op[275]\" \"channel_out_op[276]\" \"channel_out_op[277]\" \"channel_out_op[278]\" \"channel_out_op[279]\" \"channel_out_op[280]\" \"channel_out_op[281]\" \"channel_out_op[282]\" \"channel_out_op[283]\" \"channel_out_op[284]\" \"channel_out_op[285]\" \"channel_out_op[286]\" \"channel_out_op[287]\" \"channel_out_op[288]\" \"channel_out_op[289]\" \"channel_out_op[290]\" \"channel_out_op[291]\" \"channel_out_op[292]\" \"channel_out_op[293]\" \"channel_out_op[294]\" \"channel_out_op[295]\" \"channel_out_op[296]\" \"channel_out_op[297]\" \"channel_out_op[298]\" \"channel_out_op[299]\" \"channel_out_op[300]\" \"channel_out_op[301]\" \"channel_out_op[302]\" \"channel_out_op[303]\" \"channel_out_op[304]\" \"channel_out_op[305]\" \"channel_out_op[306]\" \"channel_out_op[307]\" \"channel_out_op[308]\" \"channel_out_op[309]\" \"channel_out_op[310]\" \"channel_out_op[311]\" \"channel_out_op[312]\" \"channel_out_op[313]\" \"channel_out_op[314]\" \"channel_out_op[315]\" \"channel_out_op[316]\" \"channel_out_op[317]\" \"channel_out_op[318]\" \"channel_out_op[319]\" \"channel_out_op[320]\" \"channel_out_op[321]\" \"channel_out_op[322]\" \"channel_out_op[323]\" \"channel_out_op[324]\" \"channel_out_op[325]\" \"channel_out_op[326]\" \"channel_out_op[327]\" \"channel_out_op[328]\" \"channel_out_op[329]\" \"channel_out_op[330]\" \"channel_out_op[331]\" \"channel_out_op[332]\" \"channel_out_op[333]\" \"channel_out_op[334]\" \"channel_out_op[335]\" \"channel_out_op[336]\" \"channel_out_op[337]\" \"channel_out_op[338]\" \"channel_out_op[339]\"}",

    #gen i/o s these can be assigned pretty much anywhere (can be left to the tool)
    "set my_gen_pins {\"clk\" \"reset\" \"router_address[0]\" \"router_address[1]\" \"router_address[2]\" \"router_address[3]\" \"router_address[4]\" \"router_address[5]\" \"flow_ctrl_out_ip[0]\" \"flow_ctrl_out_ip[1]\" \"flow_ctrl_out_ip[2]\" \"flow_ctrl_out_ip[3]\" \"flow_ctrl_out_ip[4]\" \"flow_ctrl_out_ip[5]\" \"flow_ctrl_out_ip[6]\" \"flow_ctrl_out_ip[7]\" \"flow_ctrl_out_ip[8]\" \"flow_ctrl_out_ip[9]\" \"flow_ctrl_in_op[0]\" \"flow_ctrl_in_op[1]\" \"flow_ctrl_in_op[2]\" \"flow_ctrl_in_op[3]\" \"flow_ctrl_in_op[4]\" \"flow_ctrl_in_op[5]\" \"flow_ctrl_in_op[6]\" \"flow_ctrl_in_op[7]\" \"flow_ctrl_in_op[8]\" \"flow_ctrl_in_op[9]\" \"error\"}",
    #assign pin locations
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 0 -layer 3 -spreadType start -spacing 10 -offsetStart 50 -pin $my_0_ch_in_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 1 -layer 4 -spreadType start -spacing 10 -offsetStart 50 -pin $my_1_ch_in_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 2 -layer 3 -spreadType start -spacing 10 -offsetStart 50 -pin $my_2_ch_in_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 3 -layer 4 -spreadType start -spacing 10 -offsetStart 50 -pin $my_3_ch_in_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 0 -layer 3 -spreadType start -spacing 10 -offsetStart 50 -pin $my_0_ch_out_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection clockwise -edge 1 -layer 4 -spreadType start -spacing 10 -offsetStart 50 -pin $my_1_ch_out_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 2 -layer 3 -spreadType start -spacing 10 -offsetStart 50 -pin $my_2_ch_out_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 3 -layer 4 -spreadType start -spacing 10 -offsetStart 50 -pin $my_3_ch_out_ports",
    "editPin -pinWidth 0.1 -pinDepth 0.52 -fixOverlap 1 -global_location -unit TRACK -spreadDirection counterclockwise -edge 3 -layer 4 -spreadType start -spacing 10 -offsetStart 50 -pin $my_gen_pins",
    #legalize
    "legalizePin"
  ]
  for line in file_lines:
    file_write_ln(fd,line)
  fd.close()

# def evaluate_routers_vs_link_len(pnr_script_path):
#   #loop through scripts in pnr script path
#   for f in os.listdir(pnr_script_path):


def write_innovus_fp_script(flow_settings,metal_layer,init_script_fname,fp_dims):
  """
  This generates the lines for a script which can generate a floorplan for a design, this must be done prior to creating partitions.
  The fp_dims parameter is a list of floorplan dimensions for hte width and height of floorplan
  """
  output_path = os.path.join("..","outputs")
  script_path = os.path.join("..","scripts")
  output_path = os.path.abspath(output_path)
  script_path = os.path.abspath(script_path)

  #new file for every dimension
  fp_script_fname = flow_settings["top_level"] + "_len_" + str(fp_dims[0]) + "_innovus_fp_gen.tcl"
  #new floorplan for every dimension
  fp_save_file = "_".join([flow_settings["top_level"],"dimlen",str(fp_dims[0]),"mlayers",metal_layer+".fp"])

  metal_layer_bottom = flow_settings["metal_layer_names"][0]
  metal_layer_second = flow_settings["metal_layer_names"][1]
  metal_layer_top = flow_settings["metal_layer_names"][int(metal_layer)-1]

  file_lines = [
    "source " + init_script_fname,
    "setDesignMode -process " + flow_settings["process_size"],
    #Below floorplan command only would work if specifying utilization rather than static dimensions
    # "floorPlan -site " +
    # " ".join([flow_settings["core_site_name"],
    #   "-r",flow_settings["height_to_width_ratio"],core_utilization,
    #   flow_settings["space_around_core"],
    #   flow_settings["space_around_core"],
    #   flow_settings["space_around_core"],
    #   flow_settings["space_around_core"]]),
    
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
    # "setAddStripeMode -ignore_block_check false -break_at none -route_over_rows_only false -rows_without_stripes_only false -extend_to_closest_target none -stop_at_last_wire_for_area false -partial_set_thru_domain false -ignore_nondefault_domains false -trim_antenna_back_to_shape none -spacing_type edge_to_edge -spacing_from_block 0 -stripe_min_length stripe_width -stacked_via_top_layer AP -stacked_via_bottom_layer M1 -via_using_exact_crossover_size false -split_vias false -orthogonal_only true -allow_jog { padcore_ring  block_ring } -skip_via_on_pin {  standardcell } -skip_via_on_wire_shape {  noshape   }",
    # "addStripe -nets {VDD VSS} -layer M2 -direction vertical -width 1.8 -spacing 1.8 -set_to_set_distance 30 -start_from left -switch_layer_over_obs false -max_same_layer_jog_length 2 -padcore_ring_top_layer_limit AP -padcore_ring_bottom_layer_limit M1 -block_ring_top_layer_limit AP -block_ring_bottom_layer_limit M1 -use_wire_group 0 -snap_wire_center_to_grid None",
    #"clearGlobalNets",
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
    #TODO check if you even need to run placement before creating floorplan, seems unnecessary to me
    #"setPlaceMode -fp false -place_global_place_io_pins true",
    #"place_design -noPrePlaceOpt",
    #"earlyGlobalRoute",
    "source " + os.path.join(script_path,"port_vars.tcl"),
    "saveFPlan " + os.path.join(output_path,fp_save_file)
  ]
  fd = open(fp_script_fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"exit")
  fd.close()
  return fp_script_fname, os.path.join(output_path,fp_save_file)

def write_innovus_ptn_script(flow_settings,metal_layer,core_utilization,init_script_fname,fp_save_file,syn_output_path):
  """
  Writes script to partition a design 
  """
  report_path = os.path.join("..","reports")
  output_path = os.path.join("..","outputs")
  report_path = os.path.abspath(report_path)
  output_path = os.path.abspath(output_path)
  
  ptn_script_fname = os.path.splitext(os.path.basename(fp_save_file))[0] + "_ptn" + ".tcl"
  fd = open(ptn_script_fname,"w")
  post_partition_fplan = "_".join([os.path.splitext(fp_save_file)[0],"post_ptn.fp"])
  ptn_module_name = "genblk1.vcr"
  ptn_dimensions = []
  file_lines = [
    " ".join(["source",init_script_fname]),
    "loadFPlan " + fp_save_file,
    #What this is doing is manually setting the vcr module to the bottom left of the core area with values that get around 70% utiliation
    #TODO update this s.t it works regardless of io boundary settings, io ring settings, target utilization etc
    #This should work regardless of the fp created in the previous script, assuming the 70% utilization target as we just want to stretch the links
    "setObjFPlanBox Module channel_in_ff"
    "setObjFPlanBox Module genblk1.vcr 10.0 10.0 350.0 350.0",
    "definePartition -hinst genblk1.vcr -coreSpacing 0.0 0.0 0.0 0.0 -railWidth 0.0 -minPitchLeft 2 -minPitchRight 2 -minPitchTop 2 -minPitchBottom 2 -reservedLayer { 1 2 3 4 5 6 7 8 9 10} -pinLayerTop { 2 4 6 8 10} -pinLayerLeft { 3 5 7 9} -pinLayerBottom { 2 4 6 8 10} -pinLayerRight { 3 5 7 9} -placementHalo 0.0 0.0 0.0 0.0 -routingHalo 0.0 -routingHaloTopLayer 10 -routingHaloBottomLayer 1",
    #Tutorial says that one should save the floorplan after the partition is defined, not sure why maybe will have to add SaveFP command here
    "saveFPlan " + os.path.join(output_path,post_partition_fplan),
    "setPlaceMode -place_hard_fence true",
    "setOptMode -honorFence true",
    "place_opt_design",
    "assignPtnPin",
    "setBudgetingMode -virtualOptEngine gigaOpt",
    "setBudgetingMode -constantModel true",
    "setBudgetingMode -includeLatency true",
    "deriveTimingBudget -ptn vcr_top_1",
    #commits partition
    "partition",
    "savePartition -dir " + os.path.splitext(os.path.basename(fp_save_file))[0] + "_ptn" + " -def"
  ]
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"exit")
  fd.close()
  return ptn_script_fname

def write_innovus_ptn_block_flow(metal_layer,ptn_dir_name,block_name):
  """
  After parititioning, we need to run placement and routing for each new partition created as well as the top level, This function generates the 
  script to run for the sub block ptn pnr flow
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
    #
    "setNanoRouteMode -quiet -routeWithTimingDriven 1",
    "setNanoRouteMode -quiet -routeWithSiDriven 1",
    "setNanoRouteMode -quiet -routeTopRoutingLayer " + str(metal_layer),
    "setNanoRouteMode -quiet -routeBottomRoutingLayer 1",
    "setNanoRouteMode -quiet -drouteEndIteration 1",
    "setNanoRouteMode -quiet -routeWithTimingDriven true",
    "setNanoRouteMode -quiet -routeWithSiDriven true",
    "routeDesign -globalDetail",
#    "optDesign -setup -postRoute",
#    "optDesign -hold -postRoute",
    "setAnalysisMode -analysisType onChipVariation -cppr both",
    "optDesign -postRoute",
    #put a check in place to make sure the above optimization actually results in timing passing
    "timeDesign -postRoute -pathReports -drvReports -slackReports -numPaths 50 -prefix " +  block_name + "_postRoute -outDir timingReports",
    "saveDesign " + block_name + "_imp",
  ]
  block_ptn_flow_script_fname = ptn_dir_name + "_block_flow.tcl"
  fd = open(block_ptn_flow_script_fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"exit")
  fd.close()

def write_innovus_ptn_top_level_flow(metal_layer,ptn_dir_name,top_level_name):
  """
  After parititioning, we need to run placement and routing for each new partition created as well as the top level, This function generates the 
  script to run for the sub block ptn pnr flow
  """ 
  file_lines = [
    "cd " + os.path.join("..","work",ptn_dir_name,top_level_name),
    " ".join(["source", top_level_name + ".globals"]),
    "init_design",
    "defIn " + top_level_name + ".def.gz",
    "create_ccopt_clock_tree_spec",
    "ccopt_design",
    "optDesign -postCTS",
    #"optDesign -setup -hold -drv -postCTS",
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

def write_innovus_assemble_script(flow_settings,ptn_dir_name,block_name,top_level_name):
  report_path = os.path.join("..","reports")
  output_path = os.path.join("..","outputs")
  report_path = os.path.abspath(report_path)
  output_path = os.path.abspath(output_path)
  #TODO fix hardcoding below using same router every time
  file_lines = [ 
    "assembleDesign -topDir " + os.path.join(ptn_dir_name,top_level_name,top_level_name+"_imp.dat") +
     " -blockDir " + os.path.join(ptn_dir_name,block_name,block_name + "_imp.dat") +
     #os.path.join(ptn_dir_name,block_name,block_name + "_imp.dat") + 
     " -fe -mmmcFile " + os.path.join("..","scripts",flow_settings["top_level"]+".view"),
    "setAnalysisMode -analysisType onChipVariation -cppr both",
    "optDesign -postRoute",
    #-setup -postRoute",
    #"optDesign -hold -postRoute",
    #"optDesign -drv -postRoute",
    "timeDesign -postRoute -prefix assembled -outDir " + os.path.join(report_path,ptn_dir_name + "_timingReports"),
    "verify_drc -report " + os.path.join(report_path, ptn_dir_name + "geom.rpt"),
    "verifyConnectivity -type all -report " + os.path.join(report_path,ptn_dir_name + "conn.rpt"),
    "report_timing > " + os.path.join(report_path,ptn_dir_name + "setup_timing.rpt"),
    "setAnalysisMode -checkType hold",
    "report_timing > " + os.path.join(report_path,ptn_dir_name + "hold_timing.rpt"),
    "report_power > " + os.path.join(report_path,ptn_dir_name + "power.rpt"),
    "report_constraint -all_violators > " + os.path.join(report_path,ptn_dir_name + "violators.rpt"),
    "report_area > " + os.path.join(report_path,ptn_dir_name + "area.rpt"),
    "summaryReport -outFile " + os.path.join(report_path,ptn_dir_name + "pr_report.txt"),
    "saveDesign " + os.path.join(output_path,ptn_dir_name + "_assembled")
  ]
  assemble_ptn_flow_script_fname = ptn_dir_name + "_assembly_flow.tcl"
  fd = open(assemble_ptn_flow_script_fname,"w")
  for line in file_lines:
    file_write_ln(fd,line)
  file_write_ln(fd,"exit")
  fd.close()  
# def write_innovus_assemble_script(flow_settings,)


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
  #subprocess.call('rm -f pt.log pt_pwr.log primetime.tcl primetime_power.tcl', shell=True)
  print("####################### STA #######################")
  print(mkdir_cmd_str)
  print(copy_rep_cmd_str)
  print(copy_logs_cmd_str)
  print("####################### STA #######################")
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
  # print(library_setup_time, data_arrival_time, total_delay, total_dynamic_power)
  # exit(1)
  return library_setup_time, data_arrival_time, total_delay, total_dynamic_power   


# #this function adds additional hardblock flow parameters which don't require user input  
# def add_hb_params(flow_settings,cur_env):

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


def gen_dir(dir_path):
  if(not os.path.isdir(dir_path)):
    os.mkdir(dir_path)

def gen_n_trav(dir_path):
  gen_dir(dir_path)
  os.chdir(dir_path)

def hardblock_script_gen(flow_settings):
  """
  This function will generate all ASIC flow scripts and run some basic environment/parameter checks to make sure the scripts will function properly but won't run any tools
  This function should be run into an asic_work directory which will have directory structure generated inside of it
  """

  partition=True

  cur_env = os.environ.copy()
  #some constants for directory structure will stay the same for now (dont see a reason why users should be able to change this)
  synth_dir = "synth"
  pnr_dir = "pnr"
  sta_dir = "sta"
  #directories generated in each parameterized directory
  work_dir = "work" #
  script_dir = "scripts"
  outputs_dir = "outputs"
  reports_dir = "reports"
  parameterized_subdirs = [work_dir,script_dir,outputs_dir,reports_dir]

  processed_flow_settings = flow_settings
  flow_settings_pre_process(processed_flow_settings,cur_env)
  
  assert len(processed_flow_settings["design_files"]) >= 1
  #create top level directory, synth dir traverse to synth dir
  gen_n_trav(flow_settings["top_level"])
  top_abs_path = os.getcwd()
  gen_n_trav(synth_dir)
  synth_abs_path = os.getcwd()
  for clock_period in flow_settings["clock_period"]:
    #os.chdir(synth_abs_path)
    for wire_selection in flow_settings['wire_selection']:
      os.chdir(synth_abs_path)
      parameterized_synth_dir = "_".join(["period",clock_period,"wiremdl",wire_selection])
      gen_n_trav(parameterized_synth_dir)
      param_synth_path = os.getcwd()
      #generate subdirs in parameterized dir
      for d in parameterized_subdirs:
        gen_dir(d)
      os.chdir(script_dir)
      #synthesis script generation
      syn_report_path, syn_output_path = write_synth_tcl(flow_settings,clock_period,wire_selection,rel_outputs=True)
      #the next stage will traverse into pnr directory so we want to go back to top level
      os.chdir(top_abs_path)
      gen_n_trav(pnr_dir)
      pnr_abs_dir = os.getcwd()
      for metal_layer in flow_settings['metal_layers']:
          #os.chdir(pnr_abs_dir)
          for core_utilization in flow_settings['core_utilization']:
            os.chdir(pnr_abs_dir)
            #expect to be in pnr dir
            parameterized_pnr_dir = parameterized_synth_dir + "_" + "_".join(["mlayer",metal_layer,"util",core_utilization])
            gen_n_trav(parameterized_pnr_dir)
            param_pnr_path = os.getcwd()         
            #generate subdirs in parameterized dir
            #once we're in the param_pnr dir, we can create sym link to the previous synth_dir (this makes this directory structure easy to traverse, think doubly linked list)
            # sym_link_dir = "synth_link"
            # sym_link_cmd = "ln -s " + param_synth_path + " " + sym_link_dir
            # subprocess.call(sym_link_cmd,shell=True)
            #then go back to previous stage and create a sym_link to the next stage
            # if(os.path.isdir(sym_link_dir)):
              # os.chdir(sym_link_dir)
              # sym_link_dir = "pnr_link"
              # sym_link_cmd = "ln -s " + param_pnr_path + " " + sym_link_dir
              # subprocess.call(sym_link_cmd,shell=True)
            #change back to original dir
            # os.chdir(param_pnr_path)
            for d in parameterized_subdirs:
              gen_dir(d)
            os.chdir(script_dir)
            # exit(1)
            if(flow_settings["pnr_tool"] == "encounter"):
              #write encounter scripts
              write_enc_script(flow_settings,metal_layer,core_utilization)
            elif(flow_settings["pnr_tool"] == "innovus"):
              #write generic innovus scripts
              view_fpath = write_innovus_view_file(flow_settings,syn_output_path)
              init_script_fname = write_innovus_init_script(flow_settings,view_fpath,syn_output_path)
              innovus_script_fname,pnr_output_path = write_innovus_script(flow_settings,metal_layer,core_utilization,init_script_fname,rel_outputs=True)
              write_edit_port_script()
              #the innovus fp script, the first dimensions of fp were found by using a utilization of 10% and reducing the size of the router fp to be around 70% utilization
              #First dimensions were 948.4 947.0 such dims were found to have passed timing
              fp_dims_list = [948.4,947.0]
              scaling_array = [1,2,3,4,5,8,10]
              scaled_dims_list = []
              for scale in scaling_array:
                new_dim_pair = [dim*scale for dim in fp_dims_list]
                scaled_dims_list.append(new_dim_pair)
              for dim_pair in scaled_dims_list:
                #creates initial floorplan
                fp_script_fname, fp_save = write_innovus_fp_script(flow_settings,metal_layer,init_script_fname,dim_pair)
                #creates partitions
                ptn_script_fname = write_innovus_ptn_script(flow_settings,metal_layer,core_utilization,init_script_fname,fp_save,syn_output_path)
                #runs pnr on subblock ptn
                write_innovus_ptn_block_flow(metal_layer,os.path.splitext(ptn_script_fname)[0],"vcr_top_1")
                #runs pnr on top level module ptn
                write_innovus_ptn_top_level_flow(metal_layer,os.path.splitext(ptn_script_fname)[0],"router_wrap")
                #assembles parititons and gets timing results
                write_innovus_assemble_script(flow_settings,os.path.splitext(ptn_script_fname)[0],"vcr_top_1","router_wrap")


            os.chdir(top_abs_path)
            gen_n_trav(sta_dir)
            sta_abs_dir = os.getcwd()
            #this cycles through all modes of the design
            for mode in range(0, 2**len(flow_settings['mode_signal']) + 1):
              os.chdir(sta_abs_dir)
              mode_enabled = True if (len(flow_settings['mode_signal']) > 0) else False
              parameterized_sta_dir = parameterized_pnr_dir + "_" + "_".join(["mode",str(mode)])
              gen_n_trav(parameterized_sta_dir)
              ###############################
              # sym_link_dir = "pnr_link"
              # sym_link_cmd = "ln -s " + param_synth_path + " " + sym_link_dir
              # subprocess.call(sym_link_cmd,shell=True)
              # then go back to previous stage and create a sym_link to the next stage
              # if(os.path.isdir(sym_link_dir)):
                # os.chdir(sym_link_dir)
              # sym_link_dir = "sta_link"
              # sym_link_cmd = "ln -s " + param_pnr_path + " " + sym_link_dir
              # subprocess.call(sym_link_cmd,shell=True)
              # os.chdir(param_pnr_path)
              ##############################
              param_sta_path = os.getcwd()
              # sym_link_cmd = "ln -s " + param_synth_path + " synth_link"
              # subprocess.run(sym_link_cmd)
              #generate subdirs in parameterized dir
              for d in parameterized_subdirs:
                gen_dir(d)
              os.chdir(script_dir)
              fpath,report_path = write_pt_timing_script(flow_settings,mode_enabled,clock_period,mode,pnr_output_path,rel_outputs=True)
              #write_pt_power_script(flow_settings,mode_enabled,clock_period,mode,pnr_output_path,rel_outputs=True)


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
