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
	already_synthesized = False
	lowest_cost = sys.float_info.max
	lowest_cost_area = 1.0
	lowest_cost_delay = 1.0
	lowest_cost_power = 1.0

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
	# Make sure we managed to read the design files
	assert len(design_files) >= 1
	for clock_period in flow_settings['clock_period']:
		for wire_selection in flow_settings['wire_selection']:
			file = open("dc_script.tcl","w")
			file.write("cd " + os.path.expanduser(flow_settings['design_folder']) + "\n")
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
			file.write("check_design >  "+os.path.expanduser(flow_settings['synth_folder'])+"checkprecompile.rpt\n")
			file.write("link \n")
			file.write("uniquify \n")
			file.write(r'set_wire_load_selection '+wire_selection+" \n")
			file.write("set my_period "+str(clock_period)+" \n")
			file.write("set find_clock [ find port [list $my_clock_pin] ] \n")
			file.write("if { $find_clock != [list] } { \n")
			file.write("set clk_name $my_clock_pin \n")
			file.write("create_clock -period $my_period $clk_name} \n\n")
			file.write("compile_ultra -no_autoungroup -no_boundary_optimization\n")
			#file.write("compile_ultra\n")
			#file.write("compile\n")
			file.write("check_design >  "+os.path.expanduser(flow_settings['synth_folder'])+"check.rpt\n")
			file.write("link \n")
			file.write("write_file -format ddc -hierarchy -output "+os.path.expanduser(flow_settings['synth_folder'])+""+ flow_settings['top_level'] +".ddc \n")

			if flow_settings['read_saif_file']:
				file.write("read_saif saif.saif \n")
			else:
				file.write("set_switching_activity -static_probability "+str(flow_settings['static_probability'])+" -toggle_rate "+str(flow_settings['toggle_rate'])+" [all_nets] \n")

			#file.write("ungroup -all -flatten \n")
			file.write("report_power > "+os.path.expanduser(flow_settings['synth_folder'])+"power.rpt\n")
			file.write("report_area -nosplit -hierarchy > "+os.path.expanduser(flow_settings['synth_folder'])+"area.rpt\n")
			file.write("report_resources -nosplit -hierarchy > "+os.path.expanduser(flow_settings['synth_folder'])+"resources.rpt\n")			
			file.write("report_timing > "+os.path.expanduser(flow_settings['synth_folder'])+"timing.rpt\n")
			file.write("change_names -hier -rule verilog \n") 
			file.write("write -f verilog -output "+os.path.expanduser(flow_settings['synth_folder'])+"synthesized.v\n")
			file.write("write_sdf "+os.path.expanduser(flow_settings['synth_folder'])+"synthsized.sdf \n")
			file.write("write_parasitics -output "+os.path.expanduser(flow_settings['synth_folder'])+"synthesized.spef \n")
			file.write("write_sdc "+os.path.expanduser(flow_settings['synth_folder'])+"synthesized.sdc \n")

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
			check_file = open(os.path.expanduser(flow_settings['synth_folder'])+"check.rpt", "r")
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
				file = open(os.path.expanduser(flow_settings['synth_folder'])+"area.rpt" ,"r")
				for line in file:
					if line.startswith('Total cell area:'):
						total_area = re.findall(r'\d+\.{0,1}\d*', line)
				file.close()

				# Read timing parameters
				file = open(os.path.expanduser(flow_settings['synth_folder'])+"timing.rpt" ,"r")
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
				file = open(os.path.expanduser(flow_settings['synth_folder'])+"power.rpt" ,"r")
				for line in file:
					if 'Total Dynamic Power' in line:
						total_dynamic_power = re.findall(r'  \d+\.{0,1}\d*', line)
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
				file.write("total area = " +str(total_area[0])+ "\n")
				file.write("total delay = "+str(total_delay)+" ns\n")
				file.write("total power = "+str(total_dynamic_power[0])+" W\n")
				file.close()

				#return
				exit()
			for metal_layer in flow_settings['metal_layers']:
				for core_utilization in flow_settings['core_utilization']:
					# generate the EDI (encounter) configuration
					file = open("edi.conf", "w")
					file.write("global rda_Input \n")
					file.write("set cwd .\n\n")
					file.write("set rda_Input(ui_leffile) "+flow_settings['lef_files']+"\n")
					file.write("set rda_Input(ui_timelib,min) "+flow_settings['best_case_libs']+"\n")
					file.write("set rda_Input(ui_timelib) "+flow_settings['standard_libs']+"\n")
					file.write("set rda_Input(ui_timelib,max) "+flow_settings['worst_case_libs']+"\n")
					file.write("set rda_Input(ui_netlist) "+os.path.expanduser(flow_settings['synth_folder'])+"synthesized.v"+"\n")
					file.write("set rda_Input(ui_netlisttype) {Verilog} \n")
					file.write("set rda_Input(import_mode) {-treatUndefinedCellAsBbox 0 -keepEmptyModule 1}\n")
					file.write("set rda_Input(ui_timingcon_file) "+os.path.expanduser(flow_settings['synth_folder'])+"synthesized.sdc"+"\n")
					file.write("set rda_Input(ui_topcell) "+flow_settings['top_level']+"\n\n")

					file.write("set rda_Input(ui_gndnet) {VSS} \n")
					file.write("set rda_Input(ui_pwrnet) {VDD} \n")
					file.write("set rda_Input(ui_pg_connections) [list {PIN:VSS:} {TIEL::} {NET:VSS:} {NET:VDD:} {TIEH::} {PIN:VDD:} ] \n")

					file.write("set rda_Input(PIN:VSS:) {VSS} \n")
					file.write("set rda_Input(TIEL::) {VSS} \n")
					file.write("set rda_Input(NET:VSS:) {VSS} \n")
					file.write("set rda_Input(PIN:VDD:) {VDD} \n")
					file.write("set rda_Input(TIEH::) {VDD} \n")
					file.write("set rda_Input(NET:VDD:) {VDD} \n\n")

					file.write("set rda_Input(ui_inv_footprint) {INVD0}\n")
					file.write("set rda_Input(ui_buf_footprint) {BUFFD1}\n")
					file.write("set rda_Input(ui_delay_footprint) {DEL0}\n")

					file.close()

					# generate the EDI (encounter) script
					file = open("edi.tcl", "w")
					file.write("loadConfig edi.conf \n")
					file.write("floorPlan -site core -r "+str(flow_settings['height_to_width_ratio'])+" "+str(core_utilization)+" "+ str(flow_settings['space_around_core'])+ " "+ str(flow_settings['space_around_core'])+ " ")
					file.write(str(flow_settings['space_around_core'])+ " "+ str(flow_settings['space_around_core']) + "\n")
					file.write("setMaxRouteLayer "+str(metal_layer)+ " \n")
					file.write("fit \n")
					file.write("addRing -spacing_bottom "+str(flow_settings['power_ring_spacing'])+" -spacing_right "+str(flow_settings['power_ring_spacing'])+" -spacing_top "+str(flow_settings['power_ring_spacing'])+" -spacing_left "+str(flow_settings['power_ring_spacing'])+" ")
					file.write("-width_right "+str(flow_settings['power_ring_width'])+" -width_left "+str(flow_settings['power_ring_width'])+" -width_bottom "+str(flow_settings['power_ring_width'])+" -width_top "+str(flow_settings['power_ring_width'])+" ")
					file.write("-layer_bottom M1 -center 1 -stacked_via_top_layer AP -around core -layer_top M1  -layer_right M2 -layer_left M2 -nets { VSS VDD } -stacked_via_bottom_layer M1 \n")

					file.write("setPlaceMode -fp false -maxRouteLayer "+str(metal_layer)+ "\n")
					file.write("placeDesign -inPlaceOpt -noPrePlaceOpt \n")
					file.write("checkPlace "+flow_settings['top_level']+" \n")


					
					file.write("trialroute \n")
					file.write("buildTimingGraph \n")
					file.write("timeDesign -preCTS -idealClock -numPaths 10 -prefix preCTS \n")
					file.write("optDesign -preCTS \n")
					# I won't do a CTS anyway as the blocks are small.

					file.write("addFiller -cell {FILL1 FILL16 FILL1_LL FILL2 FILL32 FILL64 FILL8 FILL_NW_FA_LL FILL_NW_HH FILL_NW_LL} -prefix FILL -merge true \n")	
					
					file.write("clearGlobalNets \n")
					file.write("globalNetConnect VSS -type pgpin -pin VSS -inst {} \n")
					file.write("globalNetConnect VDD -type pgpin -pin VDD -inst {} \n")
					file.write("globalNetConnect VSS -type net -net VSS \n")
					file.write("globalNetConnect VDD -type net -net VDD \n")
					file.write("globalNetConnect VDD -type pgpin -pin VDD -inst * \n")
					file.write("globalNetConnect VSS -type pgpin -pin VSS -inst * \n")
					file.write("globalNetConnect VDD -type tiehi -inst * \n")
					file.write("globalNetConnect VSS -type tielo -inst * \n")

					file.write("sroute -connect { blockPin padPin padRing corePin floatingStripe } -layerChangeRange { M1 AP } -blockPinTarget { nearestRingStripe nearestTarget } -padPinPortConnect { allPort oneGeom } -checkAlignedSecondaryPin 1 -blockPin useLef -allowJogging 1 -crossoverViaBottomLayer M1 -allowLayerChange 1 -targetViaTopLayer AP -crossoverViaTopLayer AP -targetViaBottomLayer M1 -nets { VSS VDD } \n")



					file.write("routeDesign -globalDetail\n")
					file.write("setExtractRCMode -engine postRoute \n")
					file.write("extractRC \n")
					file.write("buildTimingGraph \n")
					file.write("timeDesign -postRoute \n")
					file.write("optDesign -postRoute \n")


					file.write("verifyGeometry \n")
					file.write("verifyConnectivity -type all \n")

					# report area
					file.write("summaryReport -outFile "+os.path.expanduser(flow_settings['pr_folder'])+"pr_report.txt \n")


					# save design
					file.write(r'saveNetlist '+os.path.expanduser(flow_settings['pr_folder'])+r'netlist.v'+ "\n")
					file.write(r'saveDesign '+os.path.expanduser(flow_settings['pr_folder'])+r'design.enc'+" \n")
					file.write(r'rcOut -spef '+os.path.expanduser(flow_settings['pr_folder'])+r'spef.spef'+" \n")
					file.write(r'write_sdf -ideal_clock_network '+os.path.expanduser(flow_settings['pr_folder'])+r'sdf.sdf'+" \n")
					file.write(r'streamOut final.gds2 -mapFile streamOut.map -stripes 1 -units 1000 -mode ALL' + "\n")
					file.write("exit \n")
					file.close()

					# Run the scrip in EDI
					subprocess.call('encounter -init edi.tcl', shell=True) 
					# clean after EDI!
					subprocess.call('rm -rf edi.tcl', shell=True)
					subprocess.call('rm -rf edi.conf', shell=True)
					subprocess.call('mv encounter.log '+os.path.expanduser(flow_settings['pr_folder'])+'/logfile.log', shell=True)
					subprocess.call('mv encounter.cmd '+os.path.expanduser(flow_settings['pr_folder'])+'/encounter.cmd', shell=True)

					# read total area from the report file:
					file = open(os.path.expanduser(flow_settings['pr_folder'])+"pr_report.txt" ,"r")
					for line in file:
						if line.startswith('Total area of Core:'):
							total_area = re.findall(r'\d+\.{0,1}\d*', line)
					file.close()
					
					if len(flow_settings['mode_signal']) > 0:
						mode_enabled = True
					else:
						mode_enabled = False
					the_power = 0.0
			

					for x in range(0, 2**len(flow_settings['mode_signal']) + 1):
						if not mode_enabled:
							x = 2**len(flow_settings['mode_signal'])
						# backannotate into primetime
						# This part should be reported for all the modes in the design.
						# This script supports two modes at the moment but can be easily changed to support more.
						subprocess.call("mkdir "+os.path.expanduser(flow_settings['primetime_folder'])+"\n", shell=True)
						file = open("primetime.tcl", "w")
						file.write("set sh_enable_page_mode true \n")

						file.write("set search_path "+flow_settings['primetime_lib_path']+" \n")
						file.write("set link_path " +r'"* tcbn65gpluswc.db tpzn65gpgv2wc.db"'+" \n")

						file.write("read_verilog "+os.path.expanduser(flow_settings['pr_folder'])+"netlist.v \n")
						if mode_enabled and x <2**len(flow_settings['mode_signal']):
							for y in range (0, len(flow_settings['mode_signal'])):
								file.write("set_case_analysis "+str((x >> y) & 1)+" "+ flow_settings['mode_signal'][y]+" \n")
						file.write("link \n")

						file.write("create_clock -period "+clock_period+" "+flow_settings['clock_pin_name']+" \n")
						file.write("read_parasitics -increment "+os.path.expanduser(flow_settings['pr_folder'])+"spef.spef \n")
						file.write("report_timing > "+os.path.expanduser(flow_settings['primetime_folder'])+"timing.rpt \n")
						file.write("quit \n")
						file.close()

						# run prime time
						subprocess.call('dc_shell-t -f primetime.tcl', shell=True) 

						# clean after prime time
						subprocess.call('rm -rf primetime.tcl', shell=True)

						# Read timing parameters
						file = open(os.path.expanduser(flow_settings['primetime_folder'])+"timing.rpt" ,"r")
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
						file = open("primetime.tcl", "w")
						file.write("set sh_enable_page_mode true \n")

						file.write("set search_path "+flow_settings['primetime_lib_path']+" \n")
						file.write("set link_path " +r'"* tcbn65gpluswc.db tpzn65gpgv2wc.db"'+" \n") 

						file.write("read_verilog "+os.path.expanduser(flow_settings['pr_folder'])+"netlist.v \n")
						file.write("link \n")

						file.write("create_clock -period "+str(total_delay)+" "+flow_settings['clock_pin_name']+" \n")
						if mode_enabled and x <2**len(flow_settings['mode_signal']):
							for y in range (0, len(flow_settings['mode_signal'])):
								file.write("set_case_analysis "+str((x >> y) & 1)+" "+ flow_settings['mode_signal'][y]+ " \n")
						file.write("set power_enable_analysis TRUE \n")
						file.write(r'set power_analysis_mode "averaged"'+"\n")
						if flow_settings['read_saif_file']:
							file.write("read_saif saif.saif \n")
						else:
							file.write("set_switching_activity -static_probability "+str(flow_settings['static_probability'])+" -toggle_rate "+str(flow_settings['toggle_rate'])+" [all_nets] \n")
						file.write(r'read_parasitics -increment '+os.path.expanduser(flow_settings['pr_folder'])+r'spef.spef'+"\n")
						file.write(r'report_power > '+os.path.expanduser(flow_settings['primetime_folder'])+r'power.rpt'+" \n")
						file.write("quit\n")
						file.close()

						# run prime time
						subprocess.call('dc_shell-t -f primetime.tcl', shell=True) 

						# clean after prime time
						subprocess.call('rm -rf primetime.tcl', shell=True)


						# Read dynamic power
						file = open(os.path.expanduser(flow_settings['primetime_folder'])+"power.rpt" ,"r")
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
							file = open("report_mode"+str(x)+"_"+str(flow_settings['top_level'])+"_"+str(clock_period)+"_"+str(wire_selection)+"_wire_"+str(metal_layer)+"_"+str(core_utilization)+".txt" ,"w")
						else:
							file = open("report_"+str(flow_settings['top_level'])+"_"+str(clock_period)+"_"+str(wire_selection)+"_wire_"+str(metal_layer)+"_"+str(core_utilization)+".txt" ,"w")
						file.write("total area = " +str(total_area[0])+ "\n")
						file.write("total delay = "+str(total_delay)+" ns \n")
						file.write("total power = "+str(total_dynamic_power[0])+" W \n")
						file.close()
						if total_dynamic_power[0] > the_power:
							the_power = total_dynamic_power[0]
							
						if lowest_cost < math.pow(float(total_area[0]), float(flow_settings['area_cost_exp'])) * math.pow(float(total_delay), float(flow_settings['area_cost_exp'])):
							lowest_cost = math.pow(float(total_area[0]), float(flow_settings['area_cost_exp'])) * math.pow(float(total_delay), float(flow_settings['area_cost_exp']))
							lowest_cost_area = float(total_area[0])
							lowest_cost_delay = float(total_delay)
							lowest_cost_power = float(the_power)
							
						del total_dynamic_power[:]
						del library_setup_time[:]
						del data_arrival_time[:]
		
		
	
	return (float(lowest_cost_area), float(lowest_cost_delay), float(lowest_cost_power))
