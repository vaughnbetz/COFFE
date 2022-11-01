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


def write_synth_tcl(flow_settings,clock_period,wire_selection):
  """
  Writes the dc_script.tcl file which will be executed to run synthesis using Synopsys Design Compiler, tested under 2017 version
  """
  file = open("dc_script.tcl","w")
  file.write("cd " + flow_settings['synth_folder'] + "\n")
  #search path should have all directories which contain source , std cell libs, DesignCompiler libs
  file.write("set search_path " + flow_settings["search_path"] + " \n")
  if len(flow_settings["design_files"]) == 1:
    file.write("set my_files " + flow_settings["design_files"][0] + "\n")
  else:
    file.write("set my_files [list ")
    for entity in flow_settings["design_files"]:
      #currently set to ignore filenames of parameters.v/c_functions.v this should be updated in the future as its design specific TODO
      if not (entity == "parameters.v" or entity == "c_functions.v"):
        file.write(entity + " ")
    file.write("] \n")
  file.write("set my_top_level " + flow_settings['top_level'] + "\n")
  file.write("set my_clock_pin " + flow_settings['clock_pin_name'] + "\n")
  #after pre_processing function, the target_library and link_library vars should be set (link_library is all files in cwd and target_library)
  file.write("set target_library " + flow_settings["target_library"] + "\n")
  file.write("set link_library " + flow_settings["link_library"] + "\n")
  file.write(r'set power_analysis_mode "averaged"' + "\n")
  file.write("define_design_lib WORK -path ./WORK \n")
  if flow_settings['design_language'] == 'verilog':
    file.write("analyze -f verilog $my_files \n")
  elif flow_settings['design_language'] == 'vhdl':
    file.write("analyze -f vhdl $my_files \n")
  else:
    file.write("analyze -f sverilog $my_files \n")
  file.write("elaborate $my_top_level \n")
  file.write("current_design $my_top_level \n")
  file.write("check_design >  " + flow_settings['synth_folder'] + "/checkprecompile.rpt\n")
  file.write("link \n")
  file.write("uniquify \n")
  #If wire_selection is None, then no wireload model is used during synthesis. This does imply results 
  #are not as accurate (wires don't have any delay and area), but is useful to let the flow work/proceed 
  #if the std cell library is missing wireload models.
  if wire_selection != "None":
    file.write(r'set_wire_load_selection ' + wire_selection + " \n")
  file.write("set my_period " + str(clock_period) + " \n")
  file.write("set find_clock [ find port [list $my_clock_pin] ] \n")
  file.write("if { $find_clock != [list] } { \n")
  file.write("set clk_name $my_clock_pin \n")
  file.write("create_clock -period $my_period $clk_name} \n\n")
  file.write("compile_ultra\n")
  file.write("check_design >  " + flow_settings['synth_folder'] + "/check.rpt\n")
  file.write("link \n")
  file.write("write_file -format ddc -hierarchy -output " + flow_settings['synth_folder'] + "/" +  flow_settings['top_level']  + ".ddc \n")
  if flow_settings['read_saif_file']:
    file.write("read_saif saif.saif \n")
  else:
    file.write("set_switching_activity -static_probability " + str(flow_settings['static_probability']) + " -toggle_rate " + str(flow_settings['toggle_rate']) + " -base_clock $my_clock_pin -type inputs \n")
  file.write("ungroup -all -flatten \n")
  file.write("report_power > " + flow_settings['synth_folder'] + "/power.rpt\n")
  file.write("report_area -nosplit -hierarchy > " + flow_settings['synth_folder'] + "/area.rpt\n")
  file.write("report_resources -nosplit -hierarchy > " + flow_settings['synth_folder'] + "/resources.rpt\n")      
  file.write("report_timing > " + flow_settings['synth_folder'] + "/timing.rpt\n")
  file.write("change_names -hier -rule verilog \n") 
  file.write("write -f verilog -output " + flow_settings['synth_folder'] + "/synthesized.v\n")
  file.write("write_sdf " + flow_settings['synth_folder'] + "/synthsized.sdf \n")
  file.write("write_parasitics -output " + flow_settings['synth_folder'] + "/synthesized.spef \n")
  file.write("write_sdc " + flow_settings['synth_folder'] + "/synthesized.sdc \n")
  file.write("quit \n")
  file.close()

#search_path_dirs,design_files,
def run_synth(flow_settings,clock_period,wire_selection):
  """"
  runs the synthesis flow for specific clock period and wireload model
  Prereqs: flow_settings_pre_process() function to properly format params for scripts
  """
  write_synth_tcl(flow_settings,clock_period,wire_selection)
  # Run the scrip in design compiler shell
  subprocess.call('dc_shell-t -f dc_script.tcl | tee dc.log', shell=True,executable="/bin/bash")
  # clean after DC!
  subprocess.call('rm -rf command.log', shell=True)
  subprocess.call('rm -rf default.svf', shell=True)
  subprocess.call('rm -rf filenames.log', shell=True)

  # Make sure it worked properly
  # Open the timing report and make sure the critical path is non-zero:
  check_file = open(flow_settings['synth_folder'] + "/check.rpt", "r")
  for line in check_file:
    if "Error" in line:
      print "Your design has errors. Refer to check.rpt in synthesis directory"
      exit(-1)
    elif "Warning" in line and flow_settings['show_warnings']:
      print "Your design has warnings. Refer to check.rpt in synthesis directory"
      print "In spite of the warning, the rest of the flow will continue to execute."
  check_file.close()

  #Copy synthesis results to a unique dir in synth dir
  synth_report_str = flow_settings["top_level"] + "_period_" + clock_period + "_" + "wiremdl_" + wire_selection
  report_dest_str = os.path.join(flow_settings['synth_folder'],synth_report_str + "_reports")
  mkdir_cmd_str = "mkdir -p " + report_dest_str
  copy_rep_cmd_str = "cp " + flow_settings['synth_folder'] + "/* " + report_dest_str
  copy_logs_cmd_str = "cp " + "dc.log "+ "dc_script.tcl " + report_dest_str
  subprocess.call(mkdir_cmd_str,shell=True)
  subprocess.call(copy_rep_cmd_str,shell=True)
  subprocess.call(copy_logs_cmd_str,shell=True)
  subprocess.call('rm -f dc.log dc_script.tcl',shell=True)

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
    exit()
  return synth_report_str

def file_write_ln(fd, line):
  fd.write(line + "\n")

def write_innovus_view_file(flow_settings):
  """Write .view file for innovus place and route, this is used for for creating the delay corners from timing libs and importings constraints"""
  fname = flow_settings["top_level"]+".view"
  file = open(fname,"w")
  file.write("# Version:1.0 MMMC View Definition File\n# Do Not Remove Above Line\n")
  #I created a typical delay corner but I don't think its being used as its not called in create_analysis_view command, however, may be useful? not sure but its here
  #One could put RC values (maybe temperature in here) later for now they will all be the same
  file.write("create_rc_corner -name RC_BEST -preRoute_res {1.0} -preRoute_cap {1.0} -preRoute_clkres {0.0} -preRoute_clkcap {0.0} -postRoute_res {1.0} -postRoute_cap {1.0} -postRoute_xcap {1.0} -postRoute_clkres {0.0} -postRoute_clkcap {0.0}"+ "\n")
  file.write("create_rc_corner -name RC_TYP -preRoute_res {1.0} -preRoute_cap {1.0} -preRoute_clkres {0.0} -preRoute_clkcap {0.0} -postRoute_res {1.0} -postRoute_cap {1.0} -postRoute_xcap {1.0} -postRoute_clkres {0.0} -postRoute_clkcap {0.0}" + "\n")
  file.write("create_rc_corner -name RC_WORST -preRoute_res {1.0} -preRoute_cap {1.0} -preRoute_clkres {0.0} -preRoute_clkcap {0.0} -postRoute_res {1.0} -postRoute_cap {1.0} -postRoute_xcap {1.0} -postRoute_clkres {0.0} -postRoute_clkcap {0.0}" + "\n")
  #create libraries for each timing corner
  file.write("create_library_set -name MIN_TIMING -timing {" + flow_settings["best_case_libs"] + "}" + "\n")
  file.write("create_library_set -name TYP_TIMING -timing {" + flow_settings["standard_libs"] + "}" + "\n")
  file.write("create_library_set -name MAX_TIMING -timing {" + flow_settings["worst_case_libs"] + "}" + "\n")
  #import constraints from synthesis generated sdc
  file.write("create_constraint_mode -name CONSTRAINTS -sdc_files {" + flow_settings['synth_folder'] + "/synthesized.sdc" + "}"  + "\n")
  file.write("create_delay_corner -name MIN_DELAY -library_set {MIN_TIMING} -rc_corner {RC_BEST}" + "\n")
  file.write("create_delay_corner -name TYP_DELAY -library_set {TYP_TIMING} -rc_corner {RC_TYP}" + "\n")
  file.write("create_delay_corner -name MAX_DELAY -library_set {MAX_TIMING} -rc_corner {RC_WORST}" + "\n")
  file.write("create_analysis_view -name BEST_CASE -constraint_mode {CONSTRAINTS} -delay_corner {MIN_DELAY}" + "\n")
  file.write("create_analysis_view -name TYP_CASE -constraint_mode {CONSTRAINTS} -delay_corner {TYP_DELAY}" + "\n")
  file.write("create_analysis_view -name WORST_CASE -constraint_mode {CONSTRAINTS} -delay_corner {MAX_DELAY}" + "\n")
  #This sets our analysis view to be using our worst case analysis view for setup and best for timing,
  #This makes sense as the BC libs would have the most severe hold violations and vice versa for setup 
  file.write("set_analysis_view -setup {WORST_CASE} -hold {BEST_CASE}" + "\n")
  file.close()
  return fname


def write_innovus_script(flow_settings,metal_layer,core_utilization,init_script_fname):
  """
  This function writes the innvous script which actually performs place and route.
  Precondition to this script is the creation of an initialization script which is sourced on the first line.
  """
  #some format adjustment (could move to preproc function)
  core_utilization = str(core_utilization)
  metal_layer = str(metal_layer)
  flow_settings["power_ring_spacing"] = str(flow_settings["power_ring_spacing"])

  metal_layer_bottom = flow_settings["metal_layer_names"][0]
  metal_layer_second = flow_settings["metal_layer_names"][1]
  metal_layer_top = flow_settings["metal_layer_names"][int(metal_layer)-1]
  power_ring_metal_top = flow_settings["power_ring_metal_layer_names"][0] 
  power_ring_metal_bottom = flow_settings["power_ring_metal_layer_names"][1] 
  power_ring_metal_left = flow_settings["power_ring_metal_layer_names"][2] 
  power_ring_metal_right = flow_settings["power_ring_metal_layer_names"][3] 
  #output files
  output_files = []  
  fname = flow_settings["top_level"] + "_innovus.tcl"
  file = open(fname,"w")
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
    # "addRing -type core_rings -nets {VDD VSS} -layer {top M1 bottom M1 left M2 right M2} -width 3 -spacing 3 -offset 3 -follow io"
    " ".join(["addRing", "-type core_rings","-nets","{" + " ".join([flow_settings["pwr_net"],flow_settings["gnd_net"]]) + "}",
      "-layer {" + " ".join(["top",metal_layer_bottom,"bottom",metal_layer_bottom,"left",metal_layer_second,"right",metal_layer_second]) + "}",
      "-width", flow_settings["power_ring_width"],
      "-spacing", flow_settings["power_ring_spacing"],
      "-offset", flow_settings["power_ring_width"],
      "-follow io"]),
    "setPlaceMode -fp false",
    "place_design -noPrePlaceOpt",
    "earlyGlobalRoute",
    "timeDesign -preCTS -idealClock -numPaths 10 -prefix preCTS -outDir " + os.path.join(flow_settings["pr_folder"],"timeDesignpreCTSReports"),
    "optDesign -preCTS -outDir " + os.path.join(flow_settings["pr_folder"],"optDesignpreCTSReports"),
    "addFiller -cell {" +  " ".join(flow_settings["filler_cell_names"]) + "} -prefix FILL -merge true",
    "clearGlobalNets",
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
    "routeDesign -globalDetail",
    "setExtractRCMode -engine postRoute",
    "extractRC",
    "buildTimingGraph",
    "setAnalysisMode -analysisType onChipVariation -cppr both",
    "timeDesign -postRoute -outDir " +  os.path.join(flow_settings["pr_folder"],"timeDesignReports"),
    "optDesign -postRoute -outDir " +  os.path.join(flow_settings["pr_folder"],"optDesignReports"),
    "verify_drc -report " + os.path.join(flow_settings["pr_folder"],"geom.rpt"),
    "verifyConnectivity -type all -report " + os.path.join(flow_settings["pr_folder"],"conn.rpt"),
    "report_timing > " + os.path.join(flow_settings["pr_folder"],"setup_timing.rpt"),
    "setAnalysisMode -checkType hold",
    "report_timing > " + os.path.join(flow_settings["pr_folder"],"hold_timing.rpt"),
    "report_power > " + os.path.join(flow_settings["pr_folder"],"power.rpt"),
    "report_constraint -all_violators > " + os.path.join(flow_settings["pr_folder"],"violators.rpt"),
    "report_area > " + os.path.join(flow_settings["pr_folder"],"area.rpt"),
    "summaryReport -outFile " + os.path.join(flow_settings["pr_folder"],"pr_report.txt"),
    "saveNetlist " + os.path.join(flow_settings["pr_folder"],"netlist.v"),
    "saveDesign " +  os.path.join(flow_settings["pr_folder"],"design.enc"),
    "rcOut -spef " +  os.path.join(flow_settings["pr_folder"],"spef.spef"),
    "write_sdf -ideal_clock_network " + os.path.join(flow_settings["pr_folder"],"sdf.sdf")]
  #If the user specified a layer mapping file, then use that. Otherwise, just let the tool create a default one.
  if flow_settings['map_file'] != "None":
    file_lines.append("streamOut " +  os.path.join(flow_settings["pr_folder"],"final.gds2") + " -mapFile " + flow_settings["map_file"] + " -stripes 1 -units 1000 -mode ALL")
  else:
    file_lines.append("streamOut " +  os.path.join(flow_settings["pr_folder"],"final.gds2") + " -stripes 1 -units 1000 -mode ALL")
  for line in file_lines:
    file_write_ln(file,line)
  file_write_ln(file,"exit")
  file.close()
  return fname

def write_innovus_init_script(flow_settings,view_fname):
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
    "set init_mmmc_file {" + view_fname + "}",
    "set init_pwr_net " + flow_settings["pwr_net"],
    "set init_top_cell " + flow_settings["top_level"],
    "set init_verilog ../synth/synthesized.v",
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
  return fname


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
def run_pnr(flow_settings,metal_layer,core_utilization,synth_report_str):
  """
  runs place and route using cadence encounter
  Prereqs: flow_settings_pre_process() function to properly format params for scripts
  """
  pnr_report_str = synth_report_str + "_" + "metal_layers_" + metal_layer + "_" + "util_" + core_utilization
  report_dest_str = os.path.join(flow_settings['pr_folder'],pnr_report_str + "_reports")
  if(flow_settings["pnr_tool"] == "encounter"):
    write_enc_script(flow_settings,metal_layer,core_utilization)
    copy_logs_cmd_str = "cp " + "edi.log " + "edi.tcl " + "edi.conf " + "encounter.log " + "encounter.cmd " + report_dest_str
    # Run the scrip in EDI
    subprocess.call('encounter -nowin -init edi.tcl | tee edi.log', shell=True,executable="/bin/bash") 
  elif(flow_settings["pnr_tool"] == "innovus"):
    view_fname = write_innovus_view_file(flow_settings)
    init_script_fname = write_innovus_init_script(flow_settings,view_fname)
    innovus_script_fname = write_innovus_script(flow_settings,metal_layer,core_utilization,init_script_fname)
    run_innovus_cmd = "innovus -no_gui -init " + innovus_script_fname + " | tee inn.log"
    copy_logs_cmd_str = " ".join(["cp","inn.log",init_script_fname, view_fname,innovus_script_fname,report_dest_str])
    subprocess.call(run_innovus_cmd, shell=True,executable="/bin/bash") 

  # read total area from the report file:
  file = open(os.path.expanduser(flow_settings['pr_folder']) + "/pr_report.txt" ,"r")
  for line in file:
    if line.startswith('Total area of Core:'):
      total_area = re.findall(r'\d+\.{0,1}\d*', line)
  file.close()
  #Copy pnr results to a unique dir in pnr dir
  clean_logs_cmd_str = copy_logs_cmd_str.split(" ")
  clean_logs_cmd_str[0] = "rm -f"
  #removes the last element in the string (this is the desintation report directory)
  del clean_logs_cmd_str[-1]
  clean_logs_cmd_str = " ".join(clean_logs_cmd_str)

  mkdir_cmd_str = "mkdir -p " + report_dest_str
  copy_rep_cmd_str = "cp " + os.path.expanduser(flow_settings['pr_folder']) + "/* " + report_dest_str
  copy_rec_cmd_str = " ".join(["cp -r",os.path.join(flow_settings['pr_folder'],"design.enc.dat"),report_dest_str])
  subprocess.call(mkdir_cmd_str,shell=True)
  subprocess.call(copy_rep_cmd_str,shell=True)
  subprocess.call(copy_rec_cmd_str,shell=True)
  subprocess.call(copy_logs_cmd_str,shell=True)
  subprocess.call(clean_logs_cmd_str,shell=True)

  return pnr_report_str, total_area

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

def write_pt_power_script(flow_settings,mode_enabled,clock_period,x):
  """"
  writes the tcl script for power analysis using Synopsys Design Compiler, tested under 2017 version
  Update: changed the [all_nets] argument used in set_switching_activity to use -baseClk and -inputs args instead.
  This function takes the RC values generated from pnr script in form of .spef file and the user inputted switching probability or 
  a .saif file generated from a testbench to estimate power.
  """
  # Create a script to measure power:
  file = open("primetime_power.tcl", "w")
  file.write("set sh_enable_page_mode true \n")
  file.write("set search_path " + flow_settings['search_path'] + " \n")
  file.write("set my_top_level " + flow_settings['top_level'] + "\n")
  file.write("set my_clock_pin " + flow_settings['clock_pin_name'] + "\n")
  file.write("set target_library " + flow_settings['primetime_libs'] + "\n")
  file.write("set link_library " + flow_settings['link_library'] + "\n")
  file.write("read_verilog " + os.path.join(flow_settings['pr_folder'],"netlist.v") + "\n")
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
  file.write(r'set power_analysis_mode "averaged"' + "\n")
  if flow_settings['generate_activity_file']:
    file.write("read_saif -input saif.saif -instance_name testbench/uut \n")
  else:
    file.write("set_switching_activity -static_probability " + str(flow_settings['static_probability']) + " -toggle_rate " + str(flow_settings['toggle_rate']) + " -base_clock $my_clock_pin -type inputs \n")
  #file.write("read_saif -input saif.saif -instance_name testbench/uut \n")
  #file.write("read_vcd -input ./modelsim_dir/vcd.vcd \n")
  file.write(r'read_parasitics -increment ' + os.path.expanduser(flow_settings['pr_folder']) + r'/spef.spef' + "\n")
  #file.write("update_power \n")
  file.write(r'report_power > ' + os.path.expanduser(flow_settings['primetime_folder']) + r'/power.rpt' + " \n")
  file.write("quit\n")
  file.close()

def write_pt_timing_script(flow_settings,mode_enabled,clock_period,x):
  """
  writes the tcl script for timing analysis using Synopsys Design Compiler, tested under 2017 version
  """
  # backannotate into primetime
  # This part should be reported for all the modes in the design.
  file = open("primetime.tcl", "w")
  file.write("set sh_enable_page_mode true \n")
  file.write("set search_path " + flow_settings['search_path'] + " \n")
  file.write("set my_top_level " + flow_settings['top_level'] + "\n")
  file.write("set my_clock_pin " + flow_settings['clock_pin_name'] + "\n")
  file.write("set target_library " + flow_settings['primetime_libs'] + "\n")
  file.write("set link_library " + flow_settings['link_library'] + "\n")
  file.write("read_verilog " + os.path.expanduser(flow_settings['pr_folder']) + "/netlist.v \n")
  if mode_enabled and x <2**len(flow_settings['mode_signal']):
    for y in range (0, len(flow_settings['mode_signal'])):
      file.write("set_case_analysis " + str((x >> y) & 1) + " " +  flow_settings['mode_signal'][y] + " \n")
  file.write("link \n")
  file.write("set my_period " + str(clock_period) + " \n")
  file.write("set find_clock [ find port [list $my_clock_pin] ] \n")
  file.write("if { $find_clock != [list] } { \n")
  file.write("set clk_name $my_clock_pin \n")
  file.write("create_clock -period $my_period $clk_name} \n\n")
  file.write("read_parasitics -increment " + os.path.expanduser(flow_settings['pr_folder']) + "/spef.spef \n")
  file.write("report_timing > " + os.path.expanduser(flow_settings['primetime_folder']) + "/timing.rpt \n")
  file.write("quit \n")
  file.close()

def run_power_timing(flow_settings,mode_enabled,clock_period,x,pnr_report_str):
  if not mode_enabled:
    x = 2**len(flow_settings['mode_signal'])
  write_pt_timing_script(flow_settings,mode_enabled,clock_period,x)
  # run prime time
  subprocess.call('dc_shell-t -f primetime.tcl | tee pt.log', shell=True,executable="/bin/bash") 
  # Read timing parameters
  file = open(os.path.expanduser(flow_settings['primetime_folder']) + "/timing.rpt" ,"r")
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
  write_pt_power_script(flow_settings,mode_enabled,clock_period,x)
  # run prime time
  subprocess.call('dc_shell-t -f primetime_power.tcl | tee pt_pwr.log', shell=True,executable="/bin/bash") 
  #copy reports and logs to a unique dir in pt dir
  pt_report_str = pnr_report_str + "_" + "mode_" + str(x)
  report_dest_str = os.path.expanduser(flow_settings['primetime_folder']) + "/" + pt_report_str + "_reports"
  mkdir_cmd_str = "mkdir -p " + report_dest_str
  copy_rep_cmd_str = "cp " + os.path.expanduser(flow_settings['primetime_folder']) + "/* " + report_dest_str
  copy_logs_cmd_str = "cp " + "pt.log pt_pwr.log primetime.tcl primetime_power.tcl " + report_dest_str
  subprocess.call(mkdir_cmd_str,shell=True)
  subprocess.call(copy_rep_cmd_str,shell=True)
  subprocess.call(copy_logs_cmd_str,shell=True)
  subprocess.call('rm -f pt.log pt_pwr.log primetime.tcl primetime_power.tcl', shell=True)
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

# wire loads in the library are WireAreaLowkCon WireAreaLowkAgr WireAreaForZero
def hardblock_flow(flow_settings): 
  cur_env = os.environ.copy()
  #add_hb_params(flow_settings,cur_env)
  # processed_flow_settings = {}
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
  for clock_period in flow_settings['clock_period']:
    for wire_selection in flow_settings['wire_selection']:
      synth_report_str = run_synth(processed_flow_settings,clock_period,wire_selection)
      for metal_layer in flow_settings['metal_layers']:
        for core_utilization in flow_settings['core_utilization']:
          pnr_report_str, total_area = run_pnr(processed_flow_settings,metal_layer,core_utilization,synth_report_str)
          if len(flow_settings['mode_signal']) > 0:
            mode_enabled = True
          else:
            mode_enabled = False
          the_power = 0.0
          # Optional: use modelsim to generate an activity file for the design:
          if flow_settings['generate_activity_file'] is True:
            run_sim()
          #loops over every combination of user inputted modes to set the set_case_analysis value (determines value of mode mux)
          for x in range(0, 2**len(flow_settings['mode_signal']) + 1):
            library_setup_time, data_arrival_time, total_delay, total_dynamic_power = run_power_timing(flow_settings,mode_enabled,clock_period,x,pnr_report_str)
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
    
  return (float(lowest_cost_area), float(lowest_cost_delay), float(lowest_cost_power))
