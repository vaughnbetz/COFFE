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


# wire loads in the library are WireAreaLowkCon WireAreaLowkAgr WireAreaForZero
def hardblock_flow(flow_settings):

  # Enter all the signals that change modes
  lowest_cost = sys.float_info.max
  lowest_cost_area = 1.0
  lowest_cost_delay = 1.0
  lowest_cost_power = 1.0

  ###########################################
  # Synthesis
  ###########################################
  design_files = []
  if flow_settings['design_language'] == 'verilog':
    for file in os.listdir(os.path.expanduser(flow_settings['design_folder'])):
      if file.endswith(".v"):
        design_files.append(file)
  elif flow_settings['design_language'] == 'vhdl':
    for file in os.listdir(os.path.expanduser(flow_settings['design_folder'])):
      if file.endswith(".vhdl"):
        design_files.append(file)
  elif flow_settings['design_language'] == 'sverilog':
    for file in os.listdir(os.path.expanduser(flow_settings['design_folder'])):
      if file.endswith(".sv"):
        design_files.append(file)    
  subprocess.call("mkdir -p " + os.path.expanduser(flow_settings['synth_folder']) + "\n", shell=True)
  # Make sure we managed to read the design files
  assert len(design_files) >= 1
  for clock_period in flow_settings['clock_period']:
    for wire_selection in flow_settings['wire_selection']:
      file = open("dc_script.tcl","w")
      file.write("cd " + os.path.expanduser(flow_settings['synth_folder']) + "\n")
      file.write("set search_path " + flow_settings['design_folder'] + " \n")
      if len(design_files) == 1:
        file.write("set my_files " + design_files[0] + "\n")
      else:
        file.write("set my_files [list ")
        for entity in design_files:
          if not (entity == "parameters.v" or entity == "c_functions.v"):
            file.write(entity + " ")
        file.write("] \n")
      file.write("set my_top_level " + flow_settings['top_level'] + "\n")
      file.write("set my_clock_pin " + flow_settings['clock_pin_name'] + "\n")
      file.write("set link_library " + flow_settings['link_libraries'] + "\n")
      file.write("set target_library " + flow_settings['target_libraries'] + "\n")
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
      file.write("check_design >  " + os.path.expanduser(flow_settings['synth_folder']) + "/checkprecompile.rpt\n")
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
      file.write("check_design >  " + os.path.expanduser(flow_settings['synth_folder']) + "/check.rpt\n")
      file.write("link \n")
      file.write("write_file -format ddc -hierarchy -output " + os.path.expanduser(flow_settings['synth_folder']) + "/" +  flow_settings['top_level']  + ".ddc \n")

      if flow_settings['read_saif_file']:
        file.write("read_saif saif.saif \n")
      else:
        file.write("set_switching_activity -static_probability " + str(flow_settings['static_probability']) + " -toggle_rate " + str(flow_settings['toggle_rate']) + " [all_nets] \n")

      file.write("ungroup -all -flatten \n")
      file.write("report_power > " + os.path.expanduser(flow_settings['synth_folder']) + "/power.rpt\n")
      file.write("report_area -nosplit -hierarchy > " + os.path.expanduser(flow_settings['synth_folder']) + "/area.rpt\n")
      file.write("report_resources -nosplit -hierarchy > " + os.path.expanduser(flow_settings['synth_folder']) + "/resources.rpt\n")      
      file.write("report_timing > " + os.path.expanduser(flow_settings['synth_folder']) + "/timing.rpt\n")
      file.write("change_names -hier -rule verilog \n") 
      
      file.write("write -f verilog -output " + os.path.expanduser(flow_settings['synth_folder']) + "/synthesized.v\n")
      file.write("write_sdf " + os.path.expanduser(flow_settings['synth_folder']) + "/synthsized.sdf \n")
      file.write("write_parasitics -output " + os.path.expanduser(flow_settings['synth_folder']) + "/synthesized.spef \n")
      file.write("write_sdc " + os.path.expanduser(flow_settings['synth_folder']) + "/synthesized.sdc \n")

      file.write("quit \n")
      file.close()

      # Run the scrip in design compiler shell
      subprocess.call('dc_shell-t -f dc_script.tcl', shell=True, executable='/bin/tcsh') 
      # clean after DC!
      subprocess.call('rm -rf command.log', shell=True)
      subprocess.call('rm -rf default.svf', shell=True)
      subprocess.call('rm -rf filenames.log', shell=True)
      subprocess.call('rm -rf dc_script.tcl', shell=True) 

      # Make sure it worked properly
      # Open the timing report and make sure the critical path is non-zero:
      check_file = open(os.path.expanduser(flow_settings['synth_folder']) + "/check.rpt", "r")
      for line in check_file:
        if "Error" in line:
          print "Your design has errors. Refer to check.rpt in synthesis directory"
          exit(-1)
        elif "Warning" in line and flow_settings['show_warnings']:
          print "Your design has warnings. Refer to check.rpt in synthesis directory"
          print "In spite of the warning, the rest of the flow will continue to execute."
      check_file.close()

      #if the user doesn't want to perform place and route, extract the results from DC reports and end

      if flow_settings['synthesis_only']:

        # read total area from the report file:
        file = open(os.path.expanduser(flow_settings['synth_folder']) + "/area.rpt" ,"r")
        for line in file:
          if line.startswith('Total cell area:'):
            total_area = re.findall(r'\d+\.{0,1}\d*', line)
        file.close()

        # Read timing parameters
        file = open(os.path.expanduser(flow_settings['synth_folder']) + "/timing.rpt" ,"r")
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
        file = open(os.path.expanduser(flow_settings['synth_folder']) + "/power.rpt" ,"r")
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

      ###########################################
      # Place and Route
      ###########################################
      subprocess.call("mkdir -p " + os.path.expanduser(flow_settings['pr_folder']) + "\n", shell=True)
      for metal_layer in flow_settings['metal_layers']:
        for core_utilization in flow_settings['core_utilization']:
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

          # Run the scrip in EDI
          subprocess.call('encounter -nowin -init edi.tcl', shell=True) 
          # clean after EDI!
          subprocess.call('rm -rf edi.tcl', shell=True)
          subprocess.call('rm -rf edi.conf', shell=True)
          subprocess.call('mv encounter.log ' + os.path.expanduser(flow_settings['pr_folder']) + '/encounter_log.log', shell=True)
          subprocess.call('mv encounter.cmd ' + os.path.expanduser(flow_settings['pr_folder']) + '/encounter.cmd', shell=True)

          # read total area from the report file:
          file = open(os.path.expanduser(flow_settings['pr_folder']) + "/pr_report.txt" ,"r")
          for line in file:
            if line.startswith('Total area of Core:'):
              total_area = re.findall(r'\d+\.{0,1}\d*', line)
          file.close()
          
          if len(flow_settings['mode_signal']) > 0:
            mode_enabled = True
          else:
            mode_enabled = False
          the_power = 0.0

          # Optional: use modelsim to generate an activity file for the design:
          if flow_settings['generate_activity_file'] is True:
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
          

          ###########################################
          # Primetime
          ###########################################
          for x in range(0, 2**len(flow_settings['mode_signal']) + 1):
            if not mode_enabled:
              x = 2**len(flow_settings['mode_signal'])
            # backannotate into primetime
            # This part should be reported for all the modes in the design.
            subprocess.call("mkdir -p " + os.path.expanduser(flow_settings['primetime_folder']) + "\n", shell=True)
            file = open("primetime.tcl", "w")
            file.write("set sh_enable_page_mode true \n")

            file.write("set search_path " + flow_settings['primetime_lib_path'] + " \n")
            file.write("set link_path "  + r'"* ' + flow_settings['primetime_lib_name'] + '"' + " \n") 

            file.write("read_verilog " + os.path.expanduser(flow_settings['pr_folder']) + "/netlist.v \n")
            if mode_enabled and x <2**len(flow_settings['mode_signal']):
              for y in range (0, len(flow_settings['mode_signal'])):
                file.write("set_case_analysis " + str((x >> y) & 1) + " " +  flow_settings['mode_signal'][y] + " \n")
            file.write("link \n")

            file.write("create_clock -period " + clock_period + " " + flow_settings['clock_pin_name'] + " \n")
            file.write("read_parasitics -increment " + os.path.expanduser(flow_settings['pr_folder']) + "/spef.spef \n")
            file.write("report_timing > " + os.path.expanduser(flow_settings['primetime_folder']) + "/timing.rpt \n")
            file.write("quit \n")
            file.close()

            # run prime time
            subprocess.call('dc_shell-t -f primetime.tcl', shell=True) 

            # clean after prime time
            subprocess.call('rm -rf primetime.tcl', shell=True)

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
            # Create a script to measure power:
            file = open("primetime_power.tcl", "w")
            file.write("set sh_enable_page_mode true \n")

            file.write("set search_path " + flow_settings['primetime_lib_path'] + " \n")
            file.write("set link_path "  + r'"* ' + flow_settings['primetime_lib_name'] + '"' + " \n") 

            file.write("read_verilog " + os.path.expanduser(flow_settings['pr_folder']) + "/netlist.v \n")
            file.write("link \n")

            file.write("create_clock -period " + str(total_delay) + " " + flow_settings['clock_pin_name'] + " \n")
            if mode_enabled and x <2**len(flow_settings['mode_signal']):
              for y in range (0, len(flow_settings['mode_signal'])):
                file.write("set_case_analysis " + str((x >> y) & 1) + " " +  flow_settings['mode_signal'][y] +  " \n")
            file.write("set power_enable_analysis TRUE \n")
            file.write(r'set power_analysis_mode "averaged"' + "\n")
            if flow_settings['generate_activity_file']:
							file.write("read_saif -input saif.saif -instance_name testbench/uut \n")
            else:
              file.write("set_switching_activity -static_probability " + str(flow_settings['static_probability']) + " -toggle_rate " + str(flow_settings['toggle_rate']) + " [all_nets] \n")
            #file.write("read_saif -input saif.saif -instance_name testbench/uut \n")
            #file.write("read_vcd -input ./modelsim_dir/vcd.vcd \n")
            file.write(r'read_parasitics -increment ' + os.path.expanduser(flow_settings['pr_folder']) + r'/spef.spef' + "\n")
            #file.write("update_power \n")
            file.write(r'report_power > ' + os.path.expanduser(flow_settings['primetime_folder']) + r'/power.rpt' + " \n")
            file.write("quit\n")
            file.close()

            # run prime time
            subprocess.call('dc_shell-t -f primetime_power.tcl', shell=True) 

            # clean after prime time
            subprocess.call('rm -rf primetime_power.tcl', shell=True)


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
