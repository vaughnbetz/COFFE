# This module contains classes that describe FPGA circuitry. 
#
# The most important class (and the only one that should be instantiated outside this 
# file) is the 'fpga' class defined at the bottom of the file. 
#
# An 'fpga' object describes the FPGA that we want to design. A tile-based FPGA is 
# assumed, which consists of a switch block, a connection block and a logic cluster.
# Likewise, the 'fpga' object contains a 'SwitchBlockMUX' object, a 'ConnectionBlockMUX' 
# and a 'LogicCluster' object, each of which describe those parts of the FPGA in more detail.
# The 'LogicCluster' contains other objects that describe the various parts of its circuitry
# (local routing multiplexers, LUTs, FF, etc.) When you create an 'fpga' object, you 
# specify architecture parameters along with a few process parameters which are stored 
# in the 'fpga' object. 
#
# The 'fpga' does more than just hold information about the FPGA.
#
#      - It uses this information to generate the SPICE netlists that COFFE uses to 
#        measure delay. These netlists are generated with the appropriate transistor and
#        wire loading, which are a function of architecture parameters, transistor sizes as
#        well as some hard-coded layout assumptions (see [1] for layout assumption details).
#        It is important to note that these netlists only contain 'transistor-size' and 
#        'wire-load' VARIABLES and not hard-coded sizes and wire loads. These variables are
#        defined in their own external files. This allows us to create a single set of netlists. 
#        As COFFE changes the sizes of transistors, it only has to modify these external
#        files and the netlist will behave appropriately (transistor and wire loads depend on 
#        transistor sizes). 
#
#      - It can calculate the physical area of each circuit and structure inside the FPGA 
#        (transistors, MUXes, LUTs, BLE, Logic Cluster, FPGA tile, etc.) based on the sizes of
#        transistors and circuit topologies.
#
#      - It can calculate the length of wires in the FPGA circuitry based on the area of 
#        the circuitry and the layout assumptions.
#
#      - It can report the delay of each subcircuit in the FPGA.
#
# COFFE's transistor sizing engine uses the 'fpga' object to evaluate the impact of different transistor
# sizing combinations on the area and delay of the FPGA.
#
# [1] C. Chiasson and V.Betz, "COFFE: Fully-Automated Transistor Sizing for FPGAs", FPT2013

import os
import sys
import math

# Subcircuit Modules
import basic_subcircuits
import mux_subcircuits
import lut_subcircuits
import ff_subcircuits
import load_subcircuits

# Top level file generation module
import top_level

# HSPICE handling module
import spice


class _Specs:
	""" General FPGA specs. """
 
	def __init__(self, N, K, W, L, I, Fs, Fcin, Fcout, Fclocal, Or, Ofb, Rsel, Rfb,
					vdd, vsram, vsram_n, gate_length, min_tran_width, min_width_tran_area, sram_cell_area, model_path, model_library):
		self.N = N
		self.K = K
		self.W = W
		self.L = L
		self.I = I
		self.Fs = Fs
		self.Fcin = Fcin
		self.Fcout = Fcout
		self.Fclocal = Fclocal
		self.num_ble_general_outputs = Or
		self.num_ble_local_outputs = Ofb
		self.num_cluster_outputs = N*Or
		self.Rsel = Rsel
		self.Rfb = Rfb
		self.vdd = vdd
		self.vsram = vsram
		self.vsram_n = vsram_n
		self.gate_length = gate_length
		self.min_tran_width = min_tran_width
		self.min_width_tran_area = min_width_tran_area
		self.sram_cell_area = sram_cell_area
		self.model_path = model_path
		self.model_library = model_library

		
class _SizableCircuit:
	""" This is a base class used to identify FPGA circuits that can be sized (e.g. transistor sizing on lut)
		and declare attributes common to all SizableCircuits.
		If a class inherits _SizableCircuit, it should override all methods (error is raised otherwise). """
		
	# A list of the names of transistors in this subcircuit. This list should be logically sorted such 
	# that transistor names appear in the order that they should be sized.
	transistor_names = []
	# A list of the names of wires in this subcircuit
	wire_names = []
	# A dictionary of the initial transistor sizes
	initial_transistor_sizes = {}
	# Path to the top level spice file
	top_spice_path = ""    
	# Fall time for this subcircuit
	tfall = 1
	# Rise time for this subcircuit
	trise = 1
	# Delay to be used for this subcircuit
	delay = 1
	# Delay weight used to calculate delay of representative critical path
	delay_weight = 1

	
	def generate(self):
		""" Generate SPICE subcircuits.
			Generate method for base class must be overridden by child. """
		msg = "Function 'generate' must be overridden in class _SizableCircuit."
		raise NotImplementedError(msg)
	   
	   
	def generate_top(self):
		""" Generate top-level SPICE circuit.
			Generate method for base class must be overridden by child. """
		msg = "Function 'generate_top' must be overridden in class _SizableCircuit."
		raise NotImplementedError(msg)
	 
	 
	def update_area(self, area_dict, width_dict):
		""" Calculate area of circuit.
			Update area method for base class must be overridden by child. """
		msg = "Function 'update_area' must be overridden in class _SizableCircuit."
		raise NotImplementedError(msg)
		
		
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """
		msg = "Function 'update_wires' must be overridden in class _SizableCircuit."
		raise NotImplementedError(msg)
				
  
class _CompoundCircuit:
	""" This is a base class used to identify FPGA circuits that should not be sized. These circuits are
		usually composed of multiple smaller circuits, so we call them 'compound' circuits.
		Examples: circuits representing routing wires and loads. 
		If a class inherits _CompoundCircuit, it should override all methods."""

	def generate(self):
		""" Generate method for base class must be overridden by child. """
		msg = "Function 'generate' must be overridden in class _CompoundCircuit."
		raise NotImplementedError(msg)
		
		
class _SwitchBlockMUX(_SizableCircuit):
	""" Switch Block MUX Class: Pass-transistor 2-level mux with output driver """
	
	def __init__(self, required_size, num_per_tile):
		# Subcircuit name
		self.name = "sb_mux"
		# How big should this mux be (dictated by architecture specs)
		self.required_size = required_size 
		# How big did we make the mux (it is possible that we had to make the mux bigger for level sizes to work out, this is how big the mux turned out)
		self.implemented_size = -1
		# This is simply the implemented_size-required_size
		self.num_unused_inputs = -1
		# Number of switch block muxes in one FPGA tile
		self.num_per_tile = num_per_tile
		# Number of SRAM cells per mux
		self.sram_per_mux = -1
		# Size of the first level of muxing
		self.level1_size = -1
		# Size of the second level of muxing
		self.level2_size = -1
		# Delay weight in a representative critical path
		self.delay_weight = 0.3596
		
		
	def generate(self, subcircuit_filename, min_tran_width):
		""" 
		Generate switch block mux. 
		Calculates implementation specific details and write the SPICE subcircuit. 
		"""
		
		print "Generating switch block mux"
		
		# Calculate level sizes and number of SRAMs per mux
		self.level2_size = int(math.sqrt(self.required_size))
		self.level1_size = int(math.ceil(float(self.required_size)/self.level2_size))
		self.implemented_size = self.level1_size*self.level2_size
		self.num_unused_inputs = self.implemented_size - self.required_size
		self.sram_per_mux = self.level1_size + self.level2_size
		
		# Call MUX generation function
		self.transistor_names, self.wire_names = mux_subcircuits.generate_ptran_2lvl_mux(subcircuit_filename, self.name, self.implemented_size, self.level1_size, self.level2_size)

		# Initialize transistor sizes (to something more reasonable than all min size, but not necessarily a good choice, depends on architecture params)
		self.initial_transistor_sizes["ptran_" + self.name + "_L1_nmos"] = 3
		self.initial_transistor_sizes["ptran_" + self.name + "_L2_nmos"] = 4
		self.initial_transistor_sizes["rest_" + self.name + "_pmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_1_nmos"] = 8
		self.initial_transistor_sizes["inv_" + self.name + "_1_pmos"] = 4
		self.initial_transistor_sizes["inv_" + self.name + "_2_nmos"] = 10
		self.initial_transistor_sizes["inv_" + self.name + "_2_pmos"] = 20
	   
		return self.initial_transistor_sizes


	def generate_top(self):
		""" Generate top level SPICE file """
		
		print "Generating top-level switch block mux"
		self.top_spice_path = top_level.generate_switch_block_top(self.name)
   
   
	def update_area(self, area_dict, width_dict):
		""" Update area. To do this, we use area_dict which is a dictionary, maintained externally, that contains
			the area of everything. It is expected that area_dict will have all the information we need to calculate area.
			We update area_dict and width_dict with calculations performed in this function. """
		
		# MUX area
		area = ((self.level1_size*self.level2_size)*area_dict["ptran_" + self.name + "_L1"] +
				self.level2_size*area_dict["ptran_" + self.name + "_L2"] +
				area_dict["rest_" + self.name + ""] +
				area_dict["inv_" + self.name + "_1"] +
				area_dict["inv_" + self.name + "_2"])
		
		# MUX area including SRAM
		area_with_sram = (area + (self.level1_size + self.level2_size)*area_dict["sram"])
		
		width = math.sqrt(area)
		width_with_sram = math.sqrt(area_with_sram)
		area_dict[self.name] = area
		width_dict[self.name] = width
		area_dict[self.name + "_sram"] = area_with_sram
		width_dict[self.name + "_sram"] = width_with_sram
		
		# Update VPR areas
		area_dict["switch_mux_trans_size"] = area_dict["ptran_" + self.name + "_L1"]
		area_dict["switch_buf_size"] = area_dict["rest_" + self.name + ""] + area_dict["inv_" + self.name + "_1"] + area_dict["inv_" + self.name + "_2"]


	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """

		# Update wire lengths
		wire_lengths["wire_" + self.name + "_driver"] = (width_dict["inv_" + self.name + "_1"] + width_dict["inv_" + self.name + "_2"])/4
		wire_lengths["wire_" + self.name + "_L1"] = width_dict[self.name]
		wire_lengths["wire_" + self.name + "_L2"] = width_dict[self.name]
		
		# Update set wire layers
		wire_layers["wire_" + self.name + "_driver"] = 0
		wire_layers["wire_" + self.name + "_L1"] = 0
		wire_layers["wire_" + self.name + "_L2"] = 0
	
	
	def print_details(self):
		""" Print switch block details """

		print "  SWITCH BLOCK DETAILS:"
		print "  Style: two-level MUX"
		print "  Required MUX size: " + str(self.required_size) + ":1"
		print "  Implemented MUX size: " + str(self.implemented_size) + ":1"
		print "  Level 1 size = " + str(self.level1_size)
		print "  Level 2 size = " + str(self.level2_size)
		print "  Number of unused inputs = " + str(self.num_unused_inputs)
		print "  Number of MUXes per tile: " + str(self.num_per_tile)
		print "  Number of SRAM cells per MUX: " + str(self.sram_per_mux)
		print ""
 

class _ConnectionBlockMUX(_SizableCircuit):
	""" Connection Block MUX Class: Pass-transistor 2-level mux """
	
	def __init__(self, required_size, num_per_tile):
		# Subcircuit name
		self.name = "cb_mux"
		# How big should this mux be (dictated by architecture specs)
		self.required_size = required_size 
		# How big did we make the mux (it is possible that we had to make the mux bigger for level sizes to work out, this is how big the mux turned out)
		self.implemented_size = -1
		# This is simply the implemented_size-required_size
		self.num_unused_inputs = -1
		# Number of switch block muxes in one FPGA tile
		self.num_per_tile = num_per_tile
		# Number of SRAM cells per mux
		self.sram_per_mux = -1
		# Size of the first level of muxing
		self.level1_size = -1
		# Size of the second level of muxing
		self.level2_size = -1
		# Delay weight in a representative critical path
		self.delay_weight = 0.176
		
	
	def generate(self, subcircuit_filename, min_tran_width):
		print "Generating connection block mux"
		
		# Calculate level sizes and number of SRAMs per mux
		self.level2_size = int(math.sqrt(self.required_size))
		self.level1_size = int(math.ceil(float(self.required_size)/self.level2_size))
		self.implemented_size = self.level1_size*self.level2_size
		self.num_unused_inputs = self.implemented_size - self.required_size
		self.sram_per_mux = self.level1_size + self.level2_size
		
		# Call MUX generation function
		self.transistor_names, self.wire_names = mux_subcircuits.generate_ptran_2lvl_mux(subcircuit_filename, self.name, self.implemented_size, self.level1_size, self.level2_size)
		
		# Initialize transistor sizes (to something more reasonable than all min size, but not necessarily a good choice, depends on architecture params)
		self.initial_transistor_sizes["ptran_" + self.name + "_L1_nmos"] = 2
		self.initial_transistor_sizes["ptran_" + self.name + "_L2_nmos"] = 2
		self.initial_transistor_sizes["rest_" + self.name + "_pmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_1_nmos"] = 2
		self.initial_transistor_sizes["inv_" + self.name + "_1_pmos"] = 2
		self.initial_transistor_sizes["inv_" + self.name + "_2_nmos"] = 6
		self.initial_transistor_sizes["inv_" + self.name + "_2_pmos"] = 12
	   
		return self.initial_transistor_sizes


	def generate_top(self):
		print "Generating top-level connection block mux"
		self.top_spice_path = top_level.generate_connection_block_top(self.name)
		
   
	def update_area(self, area_dict, width_dict):
		""" Update area. To do this, we use area_dict which is a dictionary, maintained externally, that contains
			the area of everything. It is expected that area_dict will have all the information we need to calculate area.
			We update area_dict and width_dict with calculations performed in this function. """
			
		# MUX area
		area = ((self.level1_size*self.level2_size)*area_dict["ptran_" + self.name + "_L1"] +
				self.level2_size*area_dict["ptran_" + self.name + "_L2"] +
				area_dict["rest_" + self.name + ""] +
				area_dict["inv_" + self.name + "_1"] +
				area_dict["inv_" + self.name + "_2"])
		
		# MUX area including SRAM
		area_with_sram = (area + (self.level1_size + self.level2_size)*area_dict["sram"])
		
		width = math.sqrt(area)
		width_with_sram = math.sqrt(area_with_sram)
		area_dict[self.name] = area
		width_dict[self.name] = width
		area_dict[self.name + "_sram"] = area_with_sram
		width_dict[self.name + "_sram"] = width_with_sram
		
		# Update VPR area numbers
		area_dict["ipin_mux_trans_size"] = area_dict["ptran_" + self.name + "_L1"]
		
	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """

		# Update wire lengths
		wire_lengths["wire_" + self.name + "_driver"] = (width_dict["inv_" + self.name + "_1"] + width_dict["inv_" + self.name + "_2"])/4
		wire_lengths["wire_" + self.name + "_L1"] = width_dict[self.name]
		wire_lengths["wire_" + self.name + "_L2"] = width_dict[self.name]
		
		# Update set wire layers
		wire_layers["wire_" + self.name + "_driver"] = 0
		wire_layers["wire_" + self.name + "_L1"] = 0
		wire_layers["wire_" + self.name + "_L2"] = 0    
		
   
	def print_details(self):
		""" Print connection block details """
		
		print "  CONNECTION BLOCK DETAILS:"
		print "  Style: two-level MUX"
		print "  Required MUX size: " + str(self.required_size) + ":1"
		print "  Implemented MUX size: " + str(self.implemented_size) + ":1"
		print "  Level 1 size = " + str(self.level1_size)
		print "  Level 2 size = " + str(self.level2_size)
		print "  Number of unused inputs = " + str(self.num_unused_inputs)
		print "  Number of MUXes per tile: " + str(self.num_per_tile)
		print "  Number of SRAM cells per MUX: " + str(self.sram_per_mux)
		print ""
		
		
class _LocalMUX(_SizableCircuit):
	""" Local MUX Class: Pass-transistor 2-level mux with no driver """
	
	def __init__(self, required_size, num_per_tile):
		# Subcircuit name
		self.name = "local_mux"
		# How big should this mux be (dictated by architecture specs)
		self.required_size = required_size 
		# How big did we make the mux (it is possible that we had to make the mux bigger for level sizes to work out, this is how big the mux turned out)
		self.implemented_size = -1
		# This is simply the implemented_size-required_size
		self.num_unused_inputs = -1
		# Number of switch block muxes in one FPGA tile
		self.num_per_tile = num_per_tile
		# Number of SRAM cells per mux
		self.sram_per_mux = -1
		# Size of the first level of muxing
		self.level1_size = -1
		# Size of the second level of muxing
		self.level2_size = -1
		# Delay weight in a representative critical path
		self.delay_weight = 0.0862
	
	
	def generate(self, subcircuit_filename, min_tran_width):
		print "Generating local mux"
		
		# Calculate level sizes and number of SRAMs per mux
		self.level2_size = int(math.sqrt(self.required_size))
		self.level1_size = int(math.ceil(float(self.required_size)/self.level2_size))
		self.implemented_size = self.level1_size*self.level2_size
		self.num_unused_inputs = self.implemented_size - self.required_size
		self.sram_per_mux = self.level1_size + self.level2_size
		
		# Call MUX generation function
		self.transistor_names, self.wire_names = mux_subcircuits.generate_ptran_2lvl_mux_no_driver(subcircuit_filename, self.name, self.implemented_size, self.level1_size, self.level2_size)
		
		# Initialize transistor sizes (to something more reasonable than all min size, but not necessarily a good choice, depends on architecture params)
		self.initial_transistor_sizes["ptran_" + self.name + "_L1_nmos"] = 2
		self.initial_transistor_sizes["ptran_" + self.name + "_L2_nmos"] = 2
		self.initial_transistor_sizes["rest_" + self.name + "_pmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_1_nmos"] = 2
		self.initial_transistor_sizes["inv_" + self.name + "_1_pmos"] = 2
	   
		return self.initial_transistor_sizes

	def generate_top(self):
		print "Generating top-level local mux"
		self.top_spice_path = top_level.generate_local_mux_top(self.name)
		
   
	def update_area(self, area_dict, width_dict):
		""" Update area. To do this, we use area_dict which is a dictionary, maintained externally, that contains
			the area of everything. It is expected that area_dict will have all the information we need to calculate area.
			We update area_dict and width_dict with calculations performed in this function. """        
		
		# MUX area
		area = ((self.level1_size*self.level2_size)*area_dict["ptran_" + self.name + "_L1"] +
				self.level2_size*area_dict["ptran_" + self.name + "_L2"] +
				area_dict["rest_" + self.name + ""] +
				area_dict["inv_" + self.name + "_1"])
		  
		# MUX area including SRAM
		area_with_sram = (area + (self.level1_size + self.level2_size)*area_dict["sram"])
		  
		width = math.sqrt(area)
		width_with_sram = math.sqrt(area_with_sram)
		area_dict[self.name] = area
		width_dict[self.name] = width
		area_dict[self.name + "_sram"] = area_with_sram
		width_dict[self.name + "_sram"] = width_with_sram

	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """

		# Update wire lengths
		wire_lengths["wire_" + self.name + "_L1"] = width_dict[self.name]
		wire_lengths["wire_" + self.name + "_L2"] = width_dict[self.name]
		
		# Update wire layers
		wire_layers["wire_" + self.name + "_L1"] = 0
		wire_layers["wire_" + self.name + "_L2"] = 0  
		
   
	def print_details(self):
		""" Print local mux details """
		
		print "  LOCAL MUX DETAILS:"
		print "  Style: two-level MUX"
		print "  Required MUX size: " + str(self.required_size) + ":1"
		print "  Implemented MUX size: " + str(self.implemented_size) + ":1"
		print "  Level 1 size = " + str(self.level1_size)
		print "  Level 2 size = " + str(self.level2_size)
		print "  Number of unused inputs = " + str(self.num_unused_inputs)
		print "  Number of MUXes per tile: " + str(self.num_per_tile)
		print "  Number of SRAM cells per MUX: " + str(self.sram_per_mux)
		print ""
	

class _LUTInputDriver(_SizableCircuit):
	""" LUT input driver class. LUT input drivers can optionally support register feedback.
		They can also be connected to FF register input select. 
		Thus, there are 4  types of LUT input drivers: "default", "default_rsel", "reg_fb" and "reg_fb_rsel".
		When a LUT input driver is created in the '__init__' function, it is given one of these types.
		All subsequent processes (netlist generation, area calculations, etc.) will use this type attribute.
		"""

	def __init__(self, name, type, use_tgate):
		self.name = "lut_" + name + "_driver"
		# LUT input driver type ("default", "default_rsel", "reg_fb" and "reg_fb_rsel")
		self.type = type
		# Delay weight in a representative critical path
		self.delay_weight = 0.031
		# use pass transistor or transmission gate
		self.use_tgate = use_tgate
		
		
	def generate(self, subcircuit_filename, min_tran_width):
		""" Generate SPICE netlist based on type of LUT input driver. """
		if not self.use_tgate :
			self.transistor_names, self.wire_names = lut_subcircuits.generate_ptran_lut_driver(subcircuit_filename, self.name, self.type)
		else :
			self.transistor_names, self.wire_names = lut_subcircuits.generate_tgate_lut_driver(subcircuit_filename, self.name, self.type)
		
		# Initialize transistor sizes (to something more reasonable than all min size, but not necessarily a good choice, depends on architecture params)
		if self.type != "default":
			self.initial_transistor_sizes["inv_" + self.name + "_0_nmos"] = 2
			self.initial_transistor_sizes["inv_" + self.name + "_0_pmos"] = 2
		if self.type == "reg_fb" or self.type == "reg_fb_rsel":
			self.initial_transistor_sizes["ptran_" + self.name + "_0_nmos"] = 2
			self.initial_transistor_sizes["rest_" + self.name + "_pmos"] = 1
		if self.type != "default":
			self.initial_transistor_sizes["inv_" + self.name + "_1_nmos"] = 1
			self.initial_transistor_sizes["inv_" + self.name + "_1_pmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_2_nmos"] = 2
		self.initial_transistor_sizes["inv_" + self.name + "_2_pmos"] = 2
			   
		return self.initial_transistor_sizes


	def generate_top(self):
		""" Generate top-level SPICE file based on type of LUT input driver. """
		
		# Generate top level files based on what type of driver this is.
		self.top_spice_path = top_level.generate_lut_driver_top(self.name, self.type)
		# And, generate the LUT driver + LUT path top level file. We use this file to measure total delay through the LUT.
		top_level.generate_lut_and_driver_top(self.name, self.type)       
	 
	 
	def update_area(self, area_dict, width_dict):
		""" Update area. To do this, we use area_dict which is a dictionary, maintained externally, that contains
			the area of everything. It is expected that area_dict will have all the information we need to calculate area.
			We update area_dict and width_dict with calculations performed in this function. 
			We also return the area of this driver, which is calculated based on driver type. """
		
		area = 0.0
		
		if not self.use_tgate :	 
			# Calculate area based on input type
			if self.type != "default":
				area += area_dict["inv_" + self.name + "_0"]
			if self.type == "reg_fb" or self.type == "reg_fb_rsel":
				area += 2*area_dict["ptran_" + self.name + "_0"]
				area += area_dict["rest_" + self.name]
			if self.type != "default":
				area += area_dict["inv_" + self.name + "_1"]
			area += area_dict["inv_" + self.name + "_2"]
		
		else :
			# Calculate area based on input type
			if self.type != "default":
				area += area_dict["inv_" + self.name + "_0"]
			if self.type == "reg_fb" or self.type == "reg_fb_rsel":
				area += 2*area_dict["ptran_" + self.name + "_0"]
				area += area_dict["rest_" + self.name]
			if self.type != "default":
				area += area_dict["inv_" + self.name + "_1"]
			area += area_dict["inv_" + self.name + "_2"]

		# Add SRAM cell if this is a register feedback input
		if self.type == "reg_fb" or self.type == "ref_fb_rsel":
			area += area_dict["sram"]
		
		# Calculate layout width
		width = math.sqrt(area)
		
		# Add to dictionaries
		area_dict[self.name] = area
		width_dict[self.name] = width
		
		return area
		

	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict.
			Wires differ based on input type. """
		 
		# Update wire lengths and wire layers
		if self.type == "default_rsel" or self.type == "reg_fb_rsel":
			wire_lengths["wire_" + self.name + "_0_rsel"] = width_dict[self.name]/4 + width_dict["lut"] + width_dict["ff"]/4 
			wire_layers["wire_" + self.name + "_0_rsel"] = 0
		if self.type == "default_rsel":
			wire_lengths["wire_" + self.name + "_0_out"] = width_dict["inv_" + self.name + "_0"]/4 + width_dict["inv_" + self.name + "_2"]/4
			wire_layers["wire_" + self.name + "_0_out"] = 0
		if self.type == "reg_fb" or self.type == "reg_fb_rsel":
			wire_lengths["wire_" + self.name + "_0_out"] = width_dict["inv_" + self.name + "_0"]/4 + width_dict["ptran_" + self.name + "_0"]/4
			wire_layers["wire_" + self.name + "_0_out"] = 0
			wire_lengths["wire_" + self.name + "_0"] = width_dict["ptran_" + self.name + "_0"]
			wire_layers["wire_" + self.name + "_0"] = 0
		if self.type == "default":
			wire_lengths["wire_" + self.name] = width_dict["local_mux"]/4 + width_dict["inv_" + self.name + "_2"]/4
			wire_layers["wire_" + self.name] = 0
		else:
			wire_lengths["wire_" + self.name] = width_dict["inv_" + self.name + "_1"]/4 + width_dict["inv_" + self.name + "_2"]/4
			wire_layers["wire_" + self.name] = 0
			

class _LUTInputNotDriver(_SizableCircuit):
	""" LUT input not-driver. This is the complement driver. """

	def __init__(self, name, type, use_tgate):
		self.name = "lut_" + name + "_driver_not"
		# LUT input driver type ("default", "default_rsel", "reg_fb" and "reg_fb_rsel")
		self.type = type
		# Delay weight in a representative critical path
		self.delay_weight = 0.031
		# use pass transistor or transmission gates
		self.use_tgate = use_tgate
   
	
	def generate(self, subcircuit_filename, min_tran_width):
		""" Generate not-driver SPICE netlist """
		if not self.use_tgate :
			self.transistor_names, self.wire_names = lut_subcircuits.generate_ptran_lut_not_driver(subcircuit_filename, self.name)
		else :
			self.transistor_names, self.wire_names = lut_subcircuits.generate_tgate_lut_not_driver(subcircuit_filename, self.name)
		
		# Initialize transistor sizes (to something more reasonable than all min size, but not necessarily a good choice, depends on architecture params)
		self.initial_transistor_sizes["inv_" + self.name + "_1_nmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_1_pmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_2_nmos"] = 2
		self.initial_transistor_sizes["inv_" + self.name + "_2_pmos"] = 2
	   
		return self.initial_transistor_sizes


	def generate_top(self):
		""" Generate top-level SPICE file for LUT not driver """

		self.top_spice_path = top_level.generate_lut_driver_not_top(self.name, self.type)
		
	
	def update_area(self, area_dict, width_dict):
		""" Update area. To do this, we use area_dict which is a dictionary, maintained externally, that contains
			the area of everything. It is expected that area_dict will have all the information we need to calculate area.
			We update area_dict and width_dict with calculations performed in this function. 
			We also return the area of this not_driver."""
		
		area = (area_dict["inv_" + self.name + "_1"] +
				area_dict["inv_" + self.name + "_2"])
		width = math.sqrt(area)
		area_dict[self.name] = area
		width_dict[self.name] = width
		
		return area
	
	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """
		
		# Update wire lengths
		wire_lengths["wire_" + self.name] = (width_dict["inv_" + self.name + "_1"] + width_dict["inv_" + self.name + "_2"])/4
		# Update wire layers
		wire_layers["wire_" + self.name] = 0
	

class _LUTInput(_CompoundCircuit):
	""" LUT input. It contains a LUT input driver and a LUT input not driver (complement). """

	def __init__(self, name, Rsel, Rfb, use_tgate):
		# Subcircuit name (should be driver letter like a, b, c...)
		self.name = name
		# The type is either 'default': a normal input or 'reg_fb': a register feedback input 
		# In addition, the input can (optionally) drive the register select circuitry: 'default_rsel' or 'reg_fb_rsel'
		# Therefore, there are 4 different types, which are controlled by Rsel and Rfb
		if name in Rfb:
			if Rsel == name:
				self.type = "reg_fb_rsel"
			else:
				self.type = "reg_fb"
		else:
			if Rsel == name:
				self.type = "default_rsel"
			else:
				self.type = "default"
		# Create LUT input driver
		self.driver = _LUTInputDriver(name, self.type, use_tgate)
		# Create LUT input not driver
		self.not_driver = _LUTInputNotDriver(name, self.type, use_tgate)
		
		# LUT input delays are the delays through the LUT for specific input (doesn't include input driver delay)
		self.tfall = 1
		self.trise = 1
		self.delay = 1
		self.delay_weight = 1
		
		
	def generate(self, subcircuit_filename, min_tran_width):
		""" Generate both driver and not-driver SPICE netlists. """
		
		print "Generating lut " + self.name + "-input driver (" + self.type + ")"

		# Generate the driver
		init_tran_sizes = self.driver.generate(subcircuit_filename, min_tran_width)
		# Generate the not driver
		init_tran_sizes.update(self.not_driver.generate(subcircuit_filename, min_tran_width))

		return init_tran_sizes
  
			
	def generate_top(self):
		""" Generate top-level SPICE file for driver and not-driver. """
		
		print "Generating top-level lut " + self.name + "-input"
		
		# Generate the driver top
		self.driver.generate_top()
		# Generate the not driver top
		self.not_driver.generate_top()

	 
	def update_area(self, area_dict, width_dict):
		""" Update area. We update the area of the the driver and the not driver by calling area update functions
			inside these objects. We also return the total area of this input driver."""        
		
		# Calculate area of driver
		driver_area = self.driver.update_area(area_dict, width_dict)
		# Calculate area of not driver
		not_driver_area = self.not_driver.update_area(area_dict, width_dict)
		# Return the sum
		return driver_area + not_driver_area
	
	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers for input driver and not_driver """
		
		# Update driver wires
		self.driver.update_wires(width_dict, wire_lengths, wire_layers)
		# Update not driver wires
		self.not_driver.update_wires(width_dict, wire_lengths, wire_layers)
		
		
	def print_details(self):
		""" Print LUT input driver details """
		
		print "  LUT input " + self.name + " type: " + self.type

		
class _LUTInputDriverLoad:
	""" LUT input driver load. This load consists of a wire as well as the gates
		of a particular level in the LUT. """

	def __init__(self, name, use_tgate):
		self.name = name
		self.use_tgate = use_tgate
	
	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """

		# Update wire lengths
		wire_lengths["wire_lut_" + self.name + "_driver_load"] = width_dict["lut"]
		
		# Update set wire layers
		wire_layers["wire_lut_" + self.name + "_driver_load"] = 0
		
		
	def generate(self, subcircuit_filename, K):
		
		print "Generating LUT " + self.name + "-input driver load"
		
		if not self.use_tgate :
			# Call generation function based on input
			if self.name == "a":
				self.wire_names = lut_subcircuits.generate_ptran_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "b":
				self.wire_names = lut_subcircuits.generate_ptran_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "c":
				self.wire_names = lut_subcircuits.generate_ptran_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "d":
				self.wire_names = lut_subcircuits.generate_ptran_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "e":
				self.wire_names = lut_subcircuits.generate_ptran_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "f":
				self.wire_names = lut_subcircuits.generate_ptran_lut_driver_load(subcircuit_filename, self.name, K)
		else :
			# Call generation function based on input
			if self.name == "a":
				self.wire_names = lut_subcircuits.generate_tgate_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "b":
				self.wire_names = lut_subcircuits.generate_tgate_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "c":
				self.wire_names = lut_subcircuits.generate_tgate_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "d":
				self.wire_names = lut_subcircuits.generate_tgate_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "e":
				self.wire_names = lut_subcircuits.generate_tgate_lut_driver_load(subcircuit_filename, self.name, K)
			elif self.name == "f":
				self.wire_names = lut_subcircuits.generate_tgate_lut_driver_load(subcircuit_filename, self.name, K)
		
		
	def print_details(self):
		print "LUT input driver load details."
		
		
class _LUT(_SizableCircuit):
	""" Lookup table. """

	def __init__(self, K, Rsel, Rfb, use_tgate):
		# Name of LUT 
		self.name = "lut"
		# Size of LUT
		self.K = K
		# Register feedback parameter
		self.Rfb = Rfb
		# Dictionary of input drivers (keys: "a", "b", etc...)
		self.input_drivers = {}
		# Dictionary of input driver loads
		self.input_driver_loads = {}
		# Delay weight in a representative critical path
		self.delay_weight = 0.1858
		# Boolean to use transmission gates 
		self.use_tgate = use_tgate
		# Create a LUT input driver and load for each LUT input
		for i in range(K):
			name = chr(i+97)
			self.input_drivers[name] = _LUTInput(name, Rsel, Rfb, use_tgate)
			self.input_driver_loads[name] = _LUTInputDriverLoad(name, use_tgate)
	
		# Set delay weight, TODO: Need to find better way to do this.
		self.input_drivers["a"].delay_weight = 0.0568
		self.input_drivers["b"].delay_weight = 0.0508
		self.input_drivers["c"].delay_weight = 0.0094
		self.input_drivers["d"].delay_weight = 0.0213
		if K >= 5:
			self.input_drivers["e"].delay_weight = 0.0289
		if K >= 6:
			self.input_drivers["f"].delay_weight = 0.0186
		
	
	def generate(self, subcircuit_filename, min_tran_width):
		""" Generate LUT SPICE netlist based on LUT size. """
		
		# Generate LUT differently based on K
		if self.K == 6:
			init_tran_sizes = self._generate_6lut(subcircuit_filename, min_tran_width, self.use_tgate)
		elif self.K == 5:
			init_tran_sizes = self._generate_5lut(subcircuit_filename, min_tran_width, self.use_tgate)
		elif self.K == 4:
			init_tran_sizes = self._generate_4lut(subcircuit_filename, min_tran_width, self.use_tgate)
   
		return init_tran_sizes


	def generate_top(self):
		print "Generating top-level lut"
		if self.K == 6:
			self.top_spice_path = top_level.generate_lut6_top(self.name)
		elif self.K == 5:
			self.top_spice_path = top_level.generate_lut5_top(self.name)
		elif self.K == 4:
			self.top_spice_path = top_level.generate_lut4_top(self.name)
			
		# Generate top-level driver files
		for input_driver_name, input_driver in self.input_drivers.iteritems():
			input_driver.generate_top()
   
   
	def update_area(self, area_dict, width_dict):
		""" Update area. To do this, we use area_dict which is a dictionary, maintained externally, that contains
			the area of everything. It is expected that area_dict will have all the information we need to calculate area.
			We update area_dict and width_dict with calculations performed in this function. 
			We update the area of the LUT as well as the area of the LUT input drivers. """        
		 
		area = 0.0
		
		if not self.use_tgate :
			# Calculate area (differs with different values of K)
			if self.K == 6:    
				area += (64*area_dict["inv_lut_0sram_driver_2"] + 
						64*area_dict["ptran_lut_L1"] + 
						32*area_dict["ptran_lut_L2"] + 
						16*area_dict["ptran_lut_L3"] + 
						8*area_dict["rest_lut_int_buffer"] + 
						8*area_dict["inv_lut_int_buffer_1"] + 
						8*area_dict["inv_lut_int_buffer_2"] + 
						8*area_dict["ptran_lut_L4"] + 
						4*area_dict["ptran_lut_L5"] + 
						2*area_dict["ptran_lut_L6"] + 
						area_dict["rest_lut_out_buffer"] + 
						area_dict["inv_lut_out_buffer_1"] + 
						area_dict["inv_lut_out_buffer_2"] +
						64*area_dict["sram"])
			elif self.K == 5:
				area += (32*area_dict["inv_lut_0sram_driver_2"] + 
						32*area_dict["ptran_lut_L1"] + 
						16*area_dict["ptran_lut_L2"] + 
						8*area_dict["ptran_lut_L3"] + 
						4*area_dict["rest_lut_int_buffer"] + 
						4*area_dict["inv_lut_int_buffer_1"] + 
						4*area_dict["inv_lut_int_buffer_2"] + 
						4*area_dict["ptran_lut_L4"] + 
						2*area_dict["ptran_lut_L5"] +  
						area_dict["rest_lut_out_buffer"] + 
						area_dict["inv_lut_out_buffer_1"] + 
						area_dict["inv_lut_out_buffer_2"] +
						32*area_dict["sram"])
			elif self.K == 4:
				area += (16*area_dict["inv_lut_0sram_driver_2"] + 
						16*area_dict["ptran_lut_L1"] + 
						8*area_dict["ptran_lut_L2"] + 
						4*area_dict["rest_lut_int_buffer"] + 
						4*area_dict["inv_lut_int_buffer_1"] + 
						4*area_dict["inv_lut_int_buffer_2"] +
						4*area_dict["ptran_lut_L3"] + 
						2*area_dict["ptran_lut_L4"] +   
						area_dict["rest_lut_out_buffer"] + 
						area_dict["inv_lut_out_buffer_1"] + 
						area_dict["inv_lut_out_buffer_2"] +
						16*area_dict["sram"])
		else :
			# Calculate area (differs with different values of K)
			if self.K == 6:    
				area += (64*area_dict["inv_lut_0sram_driver_2"] + 
						64*area_dict["tgate_lut_L1"] + 
						32*area_dict["tgate_lut_L2"] + 
						16*area_dict["tgate_lut_L3"] + 
						8*area_dict["rest_lut_int_buffer"] + 
						8*area_dict["inv_lut_int_buffer_1"] + 
						8*area_dict["inv_lut_int_buffer_2"] + 
						8*area_dict["tgate_lut_L4"] + 
						4*area_dict["tgate_lut_L5"] + 
						2*area_dict["tgate_lut_L6"] + 
						area_dict["rest_lut_out_buffer"] + 
						area_dict["inv_lut_out_buffer_1"] + 
						area_dict["inv_lut_out_buffer_2"] +
						64*area_dict["sram"])
			elif self.K == 5:
				area += (32*area_dict["inv_lut_0sram_driver_2"] + 
						32*area_dict["tgate_lut_L1"] + 
						16*area_dict["tgate_lut_L2"] + 
						8*area_dict["tgate_lut_L3"] + 
						4*area_dict["rest_lut_int_buffer"] + 
						4*area_dict["inv_lut_int_buffer_1"] + 
						4*area_dict["inv_lut_int_buffer_2"] + 
						4*area_dict["tgate_lut_L4"] + 
						2*area_dict["tgate_lut_L5"] +  
						area_dict["rest_lut_out_buffer"] + 
						area_dict["inv_lut_out_buffer_1"] + 
						area_dict["inv_lut_out_buffer_2"] +
						32*area_dict["sram"])
			elif self.K == 4:
				area += (16*area_dict["inv_lut_0sram_driver_2"] + 
						16*area_dict["tgate_lut_L1"] + 
						8*area_dict["tgate_lut_L2"] + 
						4*area_dict["rest_lut_int_buffer"] + 
						4*area_dict["inv_lut_int_buffer_1"] + 
						4*area_dict["inv_lut_int_buffer_2"] +
						4*area_dict["tgate_lut_L3"] + 
						2*area_dict["tgate_lut_L4"] +   
						area_dict["rest_lut_out_buffer"] + 
						area_dict["inv_lut_out_buffer_1"] + 
						area_dict["inv_lut_out_buffer_2"] +
						16*area_dict["sram"])
		
		width = math.sqrt(area)
		area_dict["lut"] = area
		width_dict["lut"] = width
		
		# Calculate LUT driver areas
		total_lut_area = 0.0
		for driver_name, input_driver in self.input_drivers.iteritems():
			driver_area = input_driver.update_area(area_dict, width_dict)
			total_lut_area = total_lut_area + driver_area
	   
		# Now we calculate total LUT area
		total_lut_area = total_lut_area + area_dict["lut"]

		area_dict["lut_and_drivers"] = total_lut_area
		width_dict["lut_and_drivers"] = math.sqrt(total_lut_area)
		
		return total_lut_area
	

	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """

		if not self.use_tgate :
			if self.K == 6:        
				# Update wire lengths
				wire_lengths["wire_lut_sram_driver"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["inv_lut_0sram_driver_2"])/4
				wire_lengths["wire_lut_sram_driver_out"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["ptran_lut_L1"])/4
				wire_lengths["wire_lut_L1"] = width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_L2"] = 2*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_L3"] = 4*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_int_buffer"] = (width_dict["inv_lut_int_buffer_1"] + width_dict["inv_lut_int_buffer_2"])/4
				wire_lengths["wire_lut_int_buffer_out"] = (width_dict["inv_lut_int_buffer_2"] + width_dict["ptran_lut_L4"])/4
				wire_lengths["wire_lut_L4"] = 8*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_L5"] = 16*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_L6"] = 32*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_out_buffer"] = (width_dict["inv_lut_out_buffer_1"] + width_dict["inv_lut_out_buffer_2"])/4

				# Update wire layers
				wire_layers["wire_lut_sram_driver"] = 0
				wire_layers["wire_lut_sram_driver_out"] = 0
				wire_layers["wire_lut_L1"] = 0
				wire_layers["wire_lut_L2"] = 0
				wire_layers["wire_lut_L3"] = 0
				wire_layers["wire_lut_int_buffer"] = 0
				wire_layers["wire_lut_int_buffer_out"] = 0
				wire_layers["wire_lut_L4"] = 0
				wire_layers["wire_lut_L5"] = 0
				wire_layers["wire_lut_L6"] = 0
				wire_layers["wire_lut_out_buffer"] = 0
			  
			elif self.K == 5:
				# Update wire lengths
				wire_lengths["wire_lut_sram_driver"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["inv_lut_0sram_driver_2"])/4
				wire_lengths["wire_lut_sram_driver_out"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["ptran_lut_L1"])/4
				wire_lengths["wire_lut_L1"] = width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_L2"] = 2*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_L3"] = 4*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_int_buffer"] = (width_dict["inv_lut_int_buffer_1"] + width_dict["inv_lut_int_buffer_2"])/4
				wire_lengths["wire_lut_int_buffer_out"] = (width_dict["inv_lut_int_buffer_2"] + width_dict["ptran_lut_L4"])/4
				wire_lengths["wire_lut_L4"] = 8*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_L5"] = 16*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_out_buffer"] = (width_dict["inv_lut_out_buffer_1"] + width_dict["inv_lut_out_buffer_2"])/4

				# Update wire layers
				wire_layers["wire_lut_sram_driver"] = 0
				wire_layers["wire_lut_sram_driver_out"] = 0
				wire_layers["wire_lut_L1"] = 0
				wire_layers["wire_lut_L2"] = 0
				wire_layers["wire_lut_L3"] = 0
				wire_layers["wire_lut_int_buffer"] = 0
				wire_layers["wire_lut_int_buffer_out"] = 0
				wire_layers["wire_lut_L4"] = 0
				wire_layers["wire_lut_L5"] = 0
				wire_layers["wire_lut_out_buffer"] = 0
				
			elif self.K == 4:
				# Update wire lengths
				wire_lengths["wire_lut_sram_driver"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["inv_lut_0sram_driver_2"])/4
				wire_lengths["wire_lut_sram_driver_out"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["ptran_lut_L1"])/4
				wire_lengths["wire_lut_L1"] = width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_L2"] = 2*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_int_buffer"] = (width_dict["inv_lut_int_buffer_1"] + width_dict["inv_lut_int_buffer_2"])/4
				wire_lengths["wire_lut_int_buffer_out"] = (width_dict["inv_lut_int_buffer_2"] + width_dict["ptran_lut_L4"])/4
				wire_lengths["wire_lut_L3"] = 4*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_L4"] = 8*width_dict["ptran_lut_L1"]
				wire_lengths["wire_lut_out_buffer"] = (width_dict["inv_lut_out_buffer_1"] + width_dict["inv_lut_out_buffer_2"])/4

				# Update wire layers
				wire_layers["wire_lut_sram_driver"] = 0
				wire_layers["wire_lut_sram_driver_out"] = 0
				wire_layers["wire_lut_L1"] = 0
				wire_layers["wire_lut_L2"] = 0
				wire_layers["wire_lut_int_buffer"] = 0
				wire_layers["wire_lut_int_buffer_out"] = 0
				wire_layers["wire_lut_L3"] = 0
				wire_layers["wire_lut_L4"] = 0
				wire_layers["wire_lut_out_buffer"] = 0

		else :
			if self.K == 6:        
				# Update wire lengths
				wire_lengths["wire_lut_sram_driver"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["inv_lut_0sram_driver_2"])/4
				wire_lengths["wire_lut_sram_driver_out"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["tgate_lut_L1"])/4
				wire_lengths["wire_lut_L1"] = width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_L2"] = 2*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_L3"] = 4*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_int_buffer"] = (width_dict["inv_lut_int_buffer_1"] + width_dict["inv_lut_int_buffer_2"])/4
				wire_lengths["wire_lut_int_buffer_out"] = (width_dict["inv_lut_int_buffer_2"] + width_dict["tgate_lut_L4"])/4
				wire_lengths["wire_lut_L4"] = 8*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_L5"] = 16*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_L6"] = 32*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_out_buffer"] = (width_dict["inv_lut_out_buffer_1"] + width_dict["inv_lut_out_buffer_2"])/4

				# Update wire layers
				wire_layers["wire_lut_sram_driver"] = 0
				wire_layers["wire_lut_sram_driver_out"] = 0
				wire_layers["wire_lut_L1"] = 0
				wire_layers["wire_lut_L2"] = 0
				wire_layers["wire_lut_L3"] = 0
				wire_layers["wire_lut_int_buffer"] = 0
				wire_layers["wire_lut_int_buffer_out"] = 0
				wire_layers["wire_lut_L4"] = 0
				wire_layers["wire_lut_L5"] = 0
				wire_layers["wire_lut_L6"] = 0
				wire_layers["wire_lut_out_buffer"] = 0
			  
			elif self.K == 5:
				# Update wire lengths
				wire_lengths["wire_lut_sram_driver"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["inv_lut_0sram_driver_2"])/4
				wire_lengths["wire_lut_sram_driver_out"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["tgate_lut_L1"])/4
				wire_lengths["wire_lut_L1"] = width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_L2"] = 2*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_L3"] = 4*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_int_buffer"] = (width_dict["inv_lut_int_buffer_1"] + width_dict["inv_lut_int_buffer_2"])/4
				wire_lengths["wire_lut_int_buffer_out"] = (width_dict["inv_lut_int_buffer_2"] + width_dict["tgate_lut_L4"])/4
				wire_lengths["wire_lut_L4"] = 8*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_L5"] = 16*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_out_buffer"] = (width_dict["inv_lut_out_buffer_1"] + width_dict["inv_lut_out_buffer_2"])/4

				# Update wire layers
				wire_layers["wire_lut_sram_driver"] = 0
				wire_layers["wire_lut_sram_driver_out"] = 0
				wire_layers["wire_lut_L1"] = 0
				wire_layers["wire_lut_L2"] = 0
				wire_layers["wire_lut_L3"] = 0
				wire_layers["wire_lut_int_buffer"] = 0
				wire_layers["wire_lut_int_buffer_out"] = 0
				wire_layers["wire_lut_L4"] = 0
				wire_layers["wire_lut_L5"] = 0
				wire_layers["wire_lut_out_buffer"] = 0
				
			elif self.K == 4:
				# Update wire lengths
				wire_lengths["wire_lut_sram_driver"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["inv_lut_0sram_driver_2"])/4
				wire_lengths["wire_lut_sram_driver_out"] = (width_dict["inv_lut_0sram_driver_2"] + width_dict["tgate_lut_L1"])/4
				wire_lengths["wire_lut_L1"] = width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_L2"] = 2*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_int_buffer"] = (width_dict["inv_lut_int_buffer_1"] + width_dict["inv_lut_int_buffer_2"])/4
				wire_lengths["wire_lut_int_buffer_out"] = (width_dict["inv_lut_int_buffer_2"] + width_dict["tgate_lut_L4"])/4
				wire_lengths["wire_lut_L3"] = 4*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_L4"] = 8*width_dict["tgate_lut_L1"]
				wire_lengths["wire_lut_out_buffer"] = (width_dict["inv_lut_out_buffer_1"] + width_dict["inv_lut_out_buffer_2"])/4

				# Update wire layers
				wire_layers["wire_lut_sram_driver"] = 0
				wire_layers["wire_lut_sram_driver_out"] = 0
				wire_layers["wire_lut_L1"] = 0
				wire_layers["wire_lut_L2"] = 0
				wire_layers["wire_lut_int_buffer"] = 0
				wire_layers["wire_lut_int_buffer_out"] = 0
				wire_layers["wire_lut_L3"] = 0
				wire_layers["wire_lut_L4"] = 0
				wire_layers["wire_lut_out_buffer"] = 0
		  
		# Update input driver wires
		for driver_name, input_driver in self.input_drivers.iteritems():
			input_driver.update_wires(width_dict, wire_lengths, wire_layers) 
			
		# Update input driver load wires
		for driver_load_name, input_driver_load in self.input_driver_loads.iteritems():
			input_driver_load.update_wires(width_dict, wire_lengths, wire_layers)
	
		
	def print_details(self):
		""" Print LUT details """
		
		if self.K == 6:
			print "  LUT DETAILS:"
			print "  Style: Fully encoded MUX tree"
			print "  Size: 6-LUT"
			print "  Internal buffering: 2-stage buffer betweens levels 3 and 4"
			print "  Isolation inverters between SRAM and LUT inputs"
			print ""
			print "  LUT INPUT DRIVER DETAILS:"
			for driver_name, input_driver in self.input_drivers.iteritems():
				input_driver.print_details()
			print ""
		elif self.K == 5:
			print "  LUT DETAILS:"
			print "  Style: Fully encoded MUX tree"
			print "  Size: 5-LUT"
			print "  Internal buffering: 2-stage buffer betweens levels 3 and 4"
			print "  Isolation inverters between SRAM and LUT inputs"
			print ""
			print "  LUT INPUT DRIVER DETAILS:"
			for driver_name, input_driver in self.input_drivers.iteritems():
				input_driver.print_details()
			print ""
		elif self.K == 4:
			print "  LUT DETAILS:"
			print "  Style: Fully encoded MUX tree"
			print "  Size: 4-LUT"
			print "  Internal buffering: 2-stage buffer betweens levels 2 and 3"
			print "  Isolation inverters between SRAM and LUT inputs"
			print ""
			print "  LUT INPUT DRIVER DETAILS:"
			for driver_name, input_driver in self.input_drivers.iteritems():
				input_driver.print_details()
			print ""

	
	def _generate_6lut(self, subcircuit_filename, min_tran_width, use_tgate):
		print "Generating 6-LUT"
		
		# Call the generation function
		if not use_tgate :
			# use pass transistors
			self.transistor_names, self.wire_names = lut_subcircuits.generate_ptran_lut6(subcircuit_filename, min_tran_width)

			# Give initial transistor sizes
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_pmos"] = 6
			self.initial_transistor_sizes["ptran_lut_L1_nmos"] = 2
			self.initial_transistor_sizes["ptran_lut_L2_nmos"] = 2
			self.initial_transistor_sizes["ptran_lut_L3_nmos"] = 2
			self.initial_transistor_sizes["rest_lut_int_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_int_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_int_buffer_2_pmos"] = 6
			self.initial_transistor_sizes["ptran_lut_L4_nmos"] = 3
			self.initial_transistor_sizes["ptran_lut_L5_nmos"] = 3
			self.initial_transistor_sizes["ptran_lut_L6_nmos"] = 3
			self.initial_transistor_sizes["rest_lut_out_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_out_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_out_buffer_2_pmos"] = 6

		else :
			# use transmission gates
			self.transistor_names, self.wire_names = lut_subcircuits.generate_tgate_lut6(subcircuit_filename, min_tran_width)

			# Give initial transistor sizes
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_pmos"] = 6
			self.initial_transistor_sizes["tgate_lut_L1_nmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L1_pmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L2_nmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L2_pmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L3_nmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L3_pmos"] = 2
			self.initial_transistor_sizes["rest_lut_int_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_int_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_int_buffer_2_pmos"] = 6
			self.initial_transistor_sizes["tgate_lut_L4_nmos"] = 3
			self.initial_transistor_sizes["tgate_lut_L4_pmos"] = 3
			self.initial_transistor_sizes["tgate_lut_L5_nmos"] = 3
			self.initial_transistor_sizes["tgate_lut_L5_pmos"] = 3
			self.initial_transistor_sizes["tgate_lut_L6_nmos"] = 3
			self.initial_transistor_sizes["tgate_lut_L6_pmos"] = 3
			self.initial_transistor_sizes["rest_lut_out_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_out_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_out_buffer_2_pmos"] = 6
		
		
		# Generate input drivers (with register feedback if input is in Rfb)
		self.input_drivers["a"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["b"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["c"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["d"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["e"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["f"].generate(subcircuit_filename, min_tran_width)
		
		# Generate input driver loads
		self.input_driver_loads["a"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["b"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["c"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["d"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["e"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["f"].generate(subcircuit_filename, self.K)
	   
		return self.initial_transistor_sizes

		
	def _generate_5lut(self, subcircuit_filename, min_tran_width, use_tgate):
		print "Generating 5-LUT"
		
		# Call the generation function
		if not use_tgate :
			# use pass transistor
			self.transistor_names, self.wire_names = lut_subcircuits.generate_ptran_lut5(subcircuit_filename, min_tran_width)
			# Give initial transistor sizes
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_pmos"] = 6
			self.initial_transistor_sizes["ptran_lut_L1_nmos"] = 2
			self.initial_transistor_sizes["ptran_lut_L2_nmos"] = 2
			self.initial_transistor_sizes["ptran_lut_L3_nmos"] = 2
			self.initial_transistor_sizes["rest_lut_int_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_int_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_int_buffer_2_pmos"] = 6
			self.initial_transistor_sizes["ptran_lut_L4_nmos"] = 3
			self.initial_transistor_sizes["ptran_lut_L5_nmos"] = 3
			self.initial_transistor_sizes["rest_lut_out_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_out_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_out_buffer_2_pmos"] = 6
		else :
			# use transmission gates
			self.transistor_names, self.wire_names = lut_subcircuits.generate_tgate_lut5(subcircuit_filename, min_tran_width)
			# Give initial transistor sizes
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_pmos"] = 6
			self.initial_transistor_sizes["tgate_lut_L1_nmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L1_pmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L2_nmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L2_pmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L3_nmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L3_pmos"] = 2
			self.initial_transistor_sizes["rest_lut_int_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_int_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_int_buffer_2_pmos"] = 6
			self.initial_transistor_sizes["tgate_lut_L4_nmos"] = 3
			self.initial_transistor_sizes["tgate_lut_L4_pmos"] = 3
			self.initial_transistor_sizes["tgate_lut_L5_nmos"] = 3
			self.initial_transistor_sizes["tgate_lut_L5_pmos"] = 3
			self.initial_transistor_sizes["rest_lut_out_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_out_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_out_buffer_2_pmos"] = 6

	   
		# Generate input drivers (with register feedback if input is in Rfb)
		self.input_drivers["a"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["b"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["c"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["d"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["e"].generate(subcircuit_filename, min_tran_width)
		
		# Generate input driver loads
		self.input_driver_loads["a"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["b"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["c"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["d"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["e"].generate(subcircuit_filename, self.K)
		
		return self.initial_transistor_sizes

  
	def _generate_4lut(self, subcircuit_filename, min_tran_width, use_tgate):
		print "Generating 4-LUT"
		
		# Call the generation function
		if not use_tgate :
			# use pass transistor
			self.transistor_names, self.wire_names = lut_subcircuits.generate_ptran_lut4(subcircuit_filename, min_tran_width)
			# Give initial transistor sizes
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_pmos"] = 6
			self.initial_transistor_sizes["ptran_lut_L1_nmos"] = 2
			self.initial_transistor_sizes["ptran_lut_L2_nmos"] = 2
			self.initial_transistor_sizes["rest_lut_int_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_int_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_int_buffer_2_pmos"] = 6
			self.initial_transistor_sizes["ptran_lut_L3_nmos"] = 2
			self.initial_transistor_sizes["ptran_lut_L4_nmos"] = 3
			self.initial_transistor_sizes["rest_lut_out_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_out_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_out_buffer_2_pmos"] = 6
		else :
			# use transmission gates
			self.transistor_names, self.wire_names = lut_subcircuits.generate_tgate_lut4(subcircuit_filename, min_tran_width)
			# Give initial transistor sizes
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_0sram_driver_2_pmos"] = 6
			self.initial_transistor_sizes["tgate_lut_L1_nmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L1_pmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L2_nmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L2_pmos"] = 2
			self.initial_transistor_sizes["rest_lut_int_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_int_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_int_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_int_buffer_2_pmos"] = 6
			self.initial_transistor_sizes["tgate_lut_L3_nmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L3_pmos"] = 2
			self.initial_transistor_sizes["tgate_lut_L4_nmos"] = 3
			self.initial_transistor_sizes["tgate_lut_L4_pmos"] = 3
			self.initial_transistor_sizes["rest_lut_out_buffer_pmos"] = 1
			self.initial_transistor_sizes["inv_lut_out_buffer_1_nmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_1_pmos"] = 2
			self.initial_transistor_sizes["inv_lut_out_buffer_2_nmos"] = 4
			self.initial_transistor_sizes["inv_lut_out_buffer_2_pmos"] = 6
	   
		# Generate input drivers (with register feedback if input is in Rfb)
		self.input_drivers["a"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["b"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["c"].generate(subcircuit_filename, min_tran_width)
		self.input_drivers["d"].generate(subcircuit_filename, min_tran_width)
		
		# Generate input driver loads
		self.input_driver_loads["a"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["b"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["c"].generate(subcircuit_filename, self.K)
		self.input_driver_loads["d"].generate(subcircuit_filename, self.K)
		
		return self.initial_transistor_sizes


class _FlipFlop:
	""" FlipFlop class.
		COFFE does not do transistor sizing for the flip flop. Therefore, the FF is not a SizableCircuit.
		Regardless of that, COFFE has a FlipFlop object that is used to obtain FF area and delay.
		COFFE creates a SPICE netlist for the FF. The 'initial_transistor_sizes', defined below, are
		used when COFFE measures T_setup and T_clock_to_Q. Those transistor sizes were obtained
		through manual design for PTM 22nm process technology. If you use a different process technology,
		you may need to re-size the FF transistors. """
	
	def __init__(self, Rsel):
		# Flip-Flop name
		self.name = "ff"
		# Register select mux, Rsel = LUT input (e.g. 'a', 'b', etc.) or 'z' if no register select 
		self.register_select = Rsel
		# A list of the names of transistors in this subcircuit.
		self.transistor_names = []
		# A list of the names of wires in this subcircuit
		self.wire_names = []
		# A dictionary of the initial transistor sizes
		self.initial_transistor_sizes = {}
		# Path to the top level spice file
		self.top_spice_path = ""    
		# 
		self.t_setup = 1
		# 
		self.t_clk_to_q = 1
		# Delay weight used to calculate delay of representative critical path
		self.delay_weight = 1
		
		 
	def generate(self, subcircuit_filename, min_tran_width):
		""" Generate FF SPICE netlists. Optionally includes register select. """
		
		# Generate FF with optional register select
		if self.register_select == 'z':
			print "Generating FF"
			self.transistor_names, self.wire_names = ff_subcircuits.generate_ptran_d_ff(subcircuit_filename)
		else:
			print "Generating FF with register select on BLE input " + self.register_select
			self.transistor_names, self.wire_names = ff_subcircuits.generate_ptran_2_input_select_d_ff(subcircuit_filename)
		
		# Give initial transistor sizes
		if self.register_select:
			# These only exist if there is a register select MUX
			self.initial_transistor_sizes["ptran_ff_input_select_nmos"] = 4
			self.initial_transistor_sizes["rest_ff_input_select_pmos"] = 1
		
		# These transistors always exists regardless of register select
		self.initial_transistor_sizes["inv_ff_input_1_nmos"] = 3
		self.initial_transistor_sizes["inv_ff_input_1_pmos"] = 8.2
		self.initial_transistor_sizes["tgate_ff_1_nmos"] = 1
		self.initial_transistor_sizes["tgate_ff_1_pmos"] = 1
		self.initial_transistor_sizes["tran_ff_set_n_pmos"] = 1
		self.initial_transistor_sizes["tran_ff_reset_nmos"] = 1
		self.initial_transistor_sizes["inv_ff_cc1_1_nmos"] = 3
		self.initial_transistor_sizes["inv_ff_cc1_1_pmos"] = 4
		self.initial_transistor_sizes["inv_ff_cc1_2_nmos"] = 1
		self.initial_transistor_sizes["inv_ff_cc1_2_pmos"] = 1.3
		self.initial_transistor_sizes["tgate_ff_2_nmos"] = 1
		self.initial_transistor_sizes["tgate_ff_2_pmos"] = 1
		self.initial_transistor_sizes["tran_ff_reset_n_pmos"] = 1
		self.initial_transistor_sizes["tran_ff_set_nmos"] = 1
		self.initial_transistor_sizes["inv_ff_cc2_1_nmos"] = 1
		self.initial_transistor_sizes["inv_ff_cc2_1_pmos"] = 1.3
		self.initial_transistor_sizes["inv_ff_cc2_2_nmos"] = 1
		self.initial_transistor_sizes["inv_ff_cc2_2_pmos"] = 1.3
		self.initial_transistor_sizes["inv_ff_output_driver_nmos"] = 4
		self.initial_transistor_sizes["inv_ff_output_driver_pmos"] = 9.7

		return self.initial_transistor_sizes


	def generate_top(self):
		""" """
		# TODO for T_setup and T_clock_to_Q
		pass
		

	def update_area(self, area_dict, width_dict):
		""" Calculate FF area and update dictionaries. """
		
		area = 0.0
		
		# Calculates area of the FF input select if applicable (we add the SRAM bit later)
		# If there is no input select, we just add the area of the input inverter
		if self.register_select != 'z':
			area += (2*area_dict["ptran_ff_input_select"] +
					area_dict["rest_ff_input_select"] +
					area_dict["inv_ff_input_1"])
		else:
			area += area_dict["inv_ff_input_1"]

		# Add area of FF circuitry
		area += (area_dict["tgate_ff_1"] +
				area_dict["tran_ff_set_n"] +
				area_dict["tran_ff_reset"] +
				area_dict["inv_ff_cc1_1"] +
				area_dict["inv_ff_cc1_2"] +
				area_dict["tgate_ff_2"] +
				area_dict["tran_ff_reset_n"] +
				area_dict["tran_ff_set"] +
				area_dict["inv_ff_cc2_1"] +
				area_dict["inv_ff_cc2_2"]+
				area_dict["inv_ff_output_driver"])        

		# Add the SRAM bit if FF input select is on
		if self.register_select != 'z':
			area += area_dict["sram"]
		
		# Calculate width and add to dictionaries
		width = math.sqrt(area)
		area_dict["ff"] = area
		width_dict["ff"] = width
		
		return area
		
		
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """
		
		# Update wire lengths
		if self.register_select != 'z':
			wire_lengths["wire_ff_input_select"] = width_dict["ptran_ff_input_select"]
			
		wire_lengths["wire_ff_input_out"] = (width_dict["inv_ff_input_1"] + width_dict["tgate_ff_1"])/4
		wire_lengths["wire_ff_tgate_1_out"] = (width_dict["tgate_ff_1"] + width_dict["inv_ff_cc1_1"])/4
		wire_lengths["wire_ff_cc1_out"] = (width_dict["inv_ff_cc1_1"] + width_dict["tgate_ff_2"])/4
		wire_lengths["wire_ff_tgate_2_out"] = (width_dict["tgate_ff_2"] + width_dict["inv_ff_cc1_2"])/4
		wire_lengths["wire_ff_cc2_out"] = (width_dict["inv_ff_cc1_2"] + width_dict["inv_ff_output_driver"])/4
	
		# Update wire layers
		if self.register_select != 'z':
			wire_layers["wire_ff_input_select"] = 0
			
		wire_layers["wire_ff_input_out"] = 0
		wire_layers["wire_ff_tgate_1_out"] = 0
		wire_layers["wire_ff_cc1_out"] = 0
		wire_layers["wire_ff_tgate_2_out"] = 0
		wire_layers["wire_ff_cc2_out"] = 0
		
		
	def print_details(self):
		print "  FF DETAILS:"
		if self.register_select == 'z':
			print "  Register select: None"
		else:
			print "  Register select: BLE input " + self.register_select

		
class _LocalBLEOutput(_SizableCircuit):
	""" Local BLE Output class """
	
	def __init__(self):
		self.name = "local_ble_output"
		# Delay weight in a representative critical path
		self.delay_weight = 0.0928
		
		
	def generate(self, subcircuit_filename, min_tran_width):
		print "Generating local BLE output"
		self.transistor_names, self.wire_names = mux_subcircuits.generate_ptran_2_to_1_mux(subcircuit_filename, self.name)
		
		# Initialize transistor sizes (to something more reasonable than all min size, but not necessarily a good choice, depends on architecture params)
		self.initial_transistor_sizes["ptran_" + self.name + "_nmos"] = 2
		self.initial_transistor_sizes["rest_" + self.name + "_pmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_1_nmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_1_pmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_2_nmos"] = 4
		self.initial_transistor_sizes["inv_" + self.name + "_2_pmos"] = 4
	  
		return self.initial_transistor_sizes


	def generate_top(self):
		print "Generating top-level " + self.name
		self.top_spice_path = top_level.generate_local_ble_output_top(self.name)
		
		
	def update_area(self, area_dict, width_dict):
		area = (2*area_dict["ptran_" + self.name] +
				area_dict["rest_" + self.name] +
				area_dict["inv_" + self.name + "_1"] +
				area_dict["inv_" + self.name + "_2"])
		area = area + area_dict["sram"]
		width = math.sqrt(area)
		area_dict[self.name] = area
		width_dict[self.name] = width

		return area
		
	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """
	
		# Update wire lengths
		wire_lengths["wire_" + self.name] = width_dict["ptran_" + self.name]
		wire_lengths["wire_" + self.name + "_driver"] = (width_dict["inv_" + self.name + "_1"] + width_dict["inv_" + self.name + "_1"])/4
		
		# Update wire layers
		wire_layers["wire_" + self.name] = 0
		wire_layers["wire_" + self.name + "_driver"] = 0
		
		
	def print_details(self):
		print "Local BLE output details."

	  
class _GeneralBLEOutput(_SizableCircuit):
	""" General BLE Output """
	
	def __init__(self):
		self.name = "general_ble_output"
		self.delay_weight = 0.0502
		
		
	def generate(self, subcircuit_filename, min_tran_width):
		print "Generating general BLE output"
		self.transistor_names, self.wire_names = mux_subcircuits.generate_ptran_2_to_1_mux(subcircuit_filename, self.name)
		
		# Initialize transistor sizes (to something more reasonable than all min size, but not necessarily a good choice, depends on architecture params)
		self.initial_transistor_sizes["ptran_" + self.name + "_nmos"] = 2
		self.initial_transistor_sizes["rest_" + self.name + "_pmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_1_nmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_1_pmos"] = 1
		self.initial_transistor_sizes["inv_" + self.name + "_2_nmos"] = 5
		self.initial_transistor_sizes["inv_" + self.name + "_2_pmos"] = 5
	   
		return self.initial_transistor_sizes


	def generate_top(self):
		print "Generating top-level " + self.name
		self.top_spice_path = top_level.generate_general_ble_output_top(self.name)
		
	 
	def update_area(self, area_dict, width_dict):
		area = (2*area_dict["ptran_" + self.name] +
				area_dict["rest_" + self.name] +
				area_dict["inv_" + self.name + "_1"] +
				area_dict["inv_" + self.name + "_2"])
		area = area + area_dict["sram"]
		width = math.sqrt(area)
		area_dict[self.name] = area
		width_dict[self.name] = width

		return area
		
	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """
	
		# Update wire lengths
		wire_lengths["wire_" + self.name] = width_dict["ptran_" + self.name]
		wire_lengths["wire_" + self.name + "_driver"] = (width_dict["inv_" + self.name + "_1"] + width_dict["inv_" + self.name + "_1"])/4
		
		# Update wire layers
		wire_layers["wire_" + self.name] = 0
		wire_layers["wire_" + self.name + "_driver"] = 0
		
   
	def print_details(self):
		print "General BLE output details."

		
class _LUTOutputLoad:

	def __init__(self, num_local_outputs, num_general_outputs):
		self.name = "lut_output_load"
		self.num_local_outputs = num_local_outputs
		self.num_general_outputs = num_general_outputs
		self.wire_names = []
		
		
	def generate(self, subcircuit_filename, min_tran_width):
		print "Generating LUT output load"
		self.wire_names = load_subcircuits.generate_lut_output_load(subcircuit_filename, self.num_local_outputs, self.num_general_outputs)
		
	 
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """
		
		# Update wire lengths
		wire_lengths["wire_lut_output_load_1"] = (width_dict["ff"] + width_dict["lut_and_drivers"])/8
		wire_lengths["wire_lut_output_load_2"] = width_dict["ff"]
		
		# Update wire layers
		wire_layers["wire_lut_output_load_1"] = 0
		wire_layers["wire_lut_output_load_2"] = 0

		
class _BLE(_CompoundCircuit):

	def __init__(self, K, Or, Ofb, Rsel, Rfb, use_tgate):
		# BLE name
		self.name = "ble"
		# Size of LUT
		self.K = K
		# Number of inputs to the BLE
		self.num_inputs = K
		# Number of local outputs
		self.num_local_outputs = Ofb
		# Number of general outputs
		self.num_general_outputs = Or
		# Create BLE local output object
		self.local_output = _LocalBLEOutput()
		# Create BLE general output object
		self.general_output = _GeneralBLEOutput()
		# Create LUT object
		self.lut = _LUT(K, Rsel, Rfb, use_tgate)
		# Create FF object
		self.ff = _FlipFlop(Rsel)
		# Create LUT output load object
		self.lut_output_load = _LUTOutputLoad(self.num_local_outputs, self.num_general_outputs)
		
		
	def generate(self, subcircuit_filename, min_tran_width):
		print "Generating BLE"
		
		# Generate LUT and FF
		init_tran_sizes = {}
		init_tran_sizes.update(self.lut.generate(subcircuit_filename, min_tran_width))
		init_tran_sizes.update(self.ff.generate(subcircuit_filename, min_tran_width))
		
		# Generate BLE outputs
		init_tran_sizes.update(self.local_output.generate(subcircuit_filename, 
														  min_tran_width))
		init_tran_sizes.update(self.general_output.generate(subcircuit_filename, 
															min_tran_width))
		load_subcircuits.generate_ble_outputs(subcircuit_filename, self.num_local_outputs, self.num_general_outputs)
			
		# Generate LUT load
		self.lut_output_load.generate(subcircuit_filename, min_tran_width)
	   
		return init_tran_sizes

	 
	def generate_top(self):
		self.lut.generate_top()
		self.local_output.generate_top()
		self.general_output.generate_top()
	
	
	def update_area(self, area_dict, width_dict):
	
		lut_area = self.lut.update_area(area_dict, width_dict)
		ff_area = self.ff.update_area(area_dict, width_dict)
		
		# Calculate area of BLE outputs
		local_ble_output_area = self.num_local_outputs*self.local_output.update_area(area_dict, width_dict)
		general_ble_output_area = self.num_general_outputs*self.general_output.update_area(area_dict, width_dict)
		
		ble_output_area = local_ble_output_area + general_ble_output_area
		ble_output_width = math.sqrt(ble_output_area)
		area_dict["ble_output"] = ble_output_area
		width_dict["ble_output"] = ble_output_width
		
		ble_area = lut_area + ff_area + ble_output_area
		ble_width = math.sqrt(ble_area)
		area_dict["ble"] = ble_area
		width_dict["ble"] = ble_width
		
		
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire of member objects. """
		
		# Update lut and ff wires.
		self.lut.update_wires(width_dict, wire_lengths, wire_layers)
		self.ff.update_wires(width_dict, wire_lengths, wire_layers)
		
		# Update BLE output wires
		self.local_output.update_wires(width_dict, wire_lengths, wire_layers)
		self.general_output.update_wires(width_dict, wire_lengths, wire_layers)
		
		# Wire connecting all BLE output mux-inputs together
		wire_lengths["wire_ble_outputs"] = self.num_local_outputs*width_dict["local_ble_output"] + self.num_general_outputs*width_dict["general_ble_output"]
		wire_layers["wire_ble_outputs"] = 0

		# Update LUT load wires
		self.lut_output_load.update_wires(width_dict, wire_lengths, wire_layers)
		
		
	def print_details(self):
	
		self.lut.print_details()
		
		
class _LocalBLEOutputLoad:

	def __init__(self):
		self.name = "local_ble_output_load"
		
		
	def generate(self, subcircuit_filename):
		load_subcircuits.generate_local_ble_output_load(subcircuit_filename)
	 
	 
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """
		
		# Update wire lengths
		wire_lengths["wire_local_ble_output_feedback"] = width_dict["logic_cluster"]
		
		# Update wire layers
		wire_layers["wire_local_ble_output_feedback"] = 0
		

class _GeneralBLEOutputLoad:
	""" Logic cluster output load (i.e. general BLE output load). 
		Made up of a wire loaded by SB muxes. """

	def __init__(self):
		# Subcircuit name
		self.name = "general_ble_output_load"
		# Assumed routing channel usage, we need this for load calculation 
		self.channel_usage_assumption = 0.5
		# Assumed number of 'on' SB muxes on cluster output, needed for load calculation
		self.num_sb_mux_on_assumption = 1
		# Number of 'partially on' SB muxes on cluster output (calculated in compute_load)
		self.num_sb_mux_partial = -1
		# Number of 'off' SB muxes on cluster output (calculated in compute_load)
		self.num_sb_mux_off = -1
		# List of wires in this subcircuit
		self.wire_names = []
		
		
	def generate(self, subcircuit_filename, specs, sb_mux):
		""" Compute cluster output load load and generate SPICE netlist. """
		
		self._compute_load(specs, sb_mux, self.channel_usage_assumption, self.num_sb_mux_on_assumption)
		self.wire_names = load_subcircuits.generate_general_ble_output_load(subcircuit_filename, self.num_sb_mux_off, self.num_sb_mux_partial, self.num_sb_mux_on_assumption)
		
		
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """
		
		# Update wire lengths
		wire_lengths["wire_general_ble_output"] = width_dict["tile"]/4
		
		# Update wire layers
		wire_layers["wire_general_ble_output"] = 0
	  

	def print_details(self):
		""" Print cluster output load details """
		
		print "  CLUSTER OUTPUT LOAD DETAILS"
		print "  Total number of SB inputs connected to cluster output: " + str(self.num_sb_mux_off + self.num_sb_mux_partial + self.num_sb_mux_on_assumption)
		print "  Number of 'on' SB MUXes (assumed): " + str(self.num_sb_mux_on_assumption)
		print "  Number of 'partial' SB MUXes: " + str(self.num_sb_mux_partial)
		print "  Number of 'off' SB MUXes: " + str(self.num_sb_mux_off)
		print ""
		
	  
	def _compute_load(self, specs, sb_mux, channel_usage, sb_mux_on):
		""" Calculate how many on/partial/off switch block multiplexers are connected to each cluster output.
			Inputs are FPGA specs object, switch block mux object, assumed channel usage and assumed number of on muxes.
			The function will update the object's off & partial attributes."""
		
		# Size of second level of switch block mux, need this to figure out how many partially on muxes are connected
		sb_level2_size = sb_mux.level2_size
		
		# Total number of switch block multiplexers connected to cluster output
		total_load = int(specs.Fcout*specs.W)
		
		# Let's calculate how many partially on muxes are connected to each output
		# Based on our channel usage assumption, we can determine how many muxes are in use in a tile.
		# The number of used SB muxes equals the number of SB muxes per tile multiplied by the channel usage.
		used_sb_muxes_per_tile = int(channel_usage*sb_mux.num_per_tile)
		
		# Each one of these used muxes comes with a certain amount of partially on paths.
		# We calculate this based on the size of the 2nd muxing level of the switch block muxes
		total_partial_paths = used_sb_muxes_per_tile*(sb_level2_size-1)
		
		# The partially on paths are connected to both routing wires and cluster outputs
		# We assume that they are distributed evenly across both, which means we need to use the
		# ratio of sb_mux inputs coming from routing wires and coming from cluster outputs to determine
		# how many partially on paths would be connected to cluster outputs
		sb_inputs_from_cluster_outputs = total_load*specs.num_cluster_outputs
		# We use the required size here because we assume that extra inputs that may be present in the "implemented" mux
		# might be connected to GND or VDD and not to routing wires
		sb_inputs_from_routing = sb_mux.required_size*sb_mux.num_per_tile - sb_inputs_from_cluster_outputs
		frac_partial_paths_on_cluster_out = float(sb_inputs_from_cluster_outputs)/(sb_inputs_from_cluster_outputs+sb_inputs_from_routing)
		# The total number of partial paths on the cluster outputs is calculated using that fraction
		total_cluster_output_partial_paths = int(frac_partial_paths_on_cluster_out*total_partial_paths)
		# And we divide by the number of cluster outputs to get partial paths per output
		cluster_output_partial_paths = int(math.ceil(float(total_cluster_output_partial_paths)/specs.num_cluster_outputs))
		
		# Now assign these numbers to the object
		self.num_sb_mux_partial = cluster_output_partial_paths
		self.num_sb_mux_off = total_load - self.num_sb_mux_partial - sb_mux_on
	

class _LocalRoutingWireLoad:
	""" Local routing wire load """
	
	def __init__(self):
		# Name of this wire
		self.name = "local_routing_wire_load"
		# How many LUT inputs are we assuming are used in this logic cluster? (%)
		self.lut_input_usage_assumption = 0.85
		# Total number of local mux inputs per wire
		self.mux_inputs_per_wire = -1
		# Number of on inputs connected to each wire 
		self.on_inputs_per_wire = -1
		# Number of partially on inputs connected to each wire
		self.partial_inputs_per_wire = -1
		#Number of off inputs connected to each wire
		self.off_inputs_per_wire = -1
		# List of wire names in the SPICE circuit
		self.wire_names = []
	

	def generate(self, subcircuit_filename, specs, local_mux):
		print "Generating local routing wire load"
		# Compute load (number of on/partial/off per wire)
		self._compute_load(specs, local_mux)
		# Generate SPICE deck
		self.wire_names = load_subcircuits.local_routing_load_generate(subcircuit_filename, self.on_inputs_per_wire, self.partial_inputs_per_wire, self.off_inputs_per_wire)
	
	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wire lengths and wire layers based on the width of things, obtained from width_dict. """
		
		# Update wire lengths
		wire_lengths["wire_local_routing"] = width_dict["logic_cluster"]
		
		# Update wire layers
		wire_layers["wire_local_routing"] = 0
	
		
	def print_details(self):
		print "LOCAL ROUTING WIRE LOAD DETAILS"
		print ""
		
		
	def _compute_load(self, specs, local_mux):
		""" Compute the load on a local routing wire (number of on/partial/off) """
		
		# The first thing we are going to compute is how many local mux inputs are connected to a local routing wire
		# This is a function of local_mux size, N, K, I and Ofb
		num_local_routing_wires = specs.I+specs.N*specs.num_ble_local_outputs
		self.mux_inputs_per_wire = local_mux.implemented_size*specs.N*specs.K/num_local_routing_wires
		
		# Now we compute how many "on" inputs are connected to each routing wire
		# This is a funtion of lut input usage, number of lut inputs and number of local routing wires
		num_local_muxes_used = self.lut_input_usage_assumption*specs.N*specs.K
		self.on_inputs_per_wire = int(num_local_muxes_used/num_local_routing_wires)
		# We want to model for the case where at least one "on" input is connected to the local wire, so make sure it's at least 1
		if self.on_inputs_per_wire < 1:
			self.on_inputs_per_wire = 1
		
		# Now we compute how many partially on muxes are connected to each wire
		# The number of partially on muxes is equal to (level2_size - 1)*num_local_muxes_used/num_local_routing_wire
		# We can figure out the number of muxes used by using the "on" assumption and the number of local routing wires.
		self.partial_inputs_per_wire = int((local_mux.level2_size - 1.0)*num_local_muxes_used/num_local_routing_wires)
		# Make it at least 1
		if self.partial_inputs_per_wire < 1:
			self.partial_inputs_per_wire = 1
		
		# Number of off inputs is simply the difference
		self.off_inputs_per_wire = self.mux_inputs_per_wire - self.on_inputs_per_wire - self.partial_inputs_per_wire
		

class _LogicCluster(_CompoundCircuit):
	
	def __init__(self, N, K, Or, Ofb, Rsel, Rfb, local_mux_size_required, num_local_mux_per_tile, use_tgate):
		# Name of logic cluster
		self.name = "logic_cluster"
		# Cluster size
		self.N = N
		# Create BLE object
		self.ble = _BLE(K, Or, Ofb, Rsel, Rfb, use_tgate)
		# Create local mux object
		self.local_mux = _LocalMUX(local_mux_size_required, num_local_mux_per_tile)
		# Create local routing wire load object
		self.local_routing_wire_load = _LocalRoutingWireLoad()
		# Create local BLE output load object
		self.local_ble_output_load = _LocalBLEOutputLoad()

		
	def generate(self, subcircuits_filename, min_tran_width, specs):
		print "Generating logic cluster"
		init_tran_sizes = {}
		init_tran_sizes.update(self.ble.generate(subcircuits_filename, min_tran_width))
		init_tran_sizes.update(self.local_mux.generate(subcircuits_filename, min_tran_width))
		self.local_routing_wire_load.generate(subcircuits_filename, specs, self.local_mux)
		self.local_ble_output_load.generate(subcircuits_filename)
		
		return init_tran_sizes


	def generate_top(self):
		self.local_mux.generate_top()
		self.ble.generate_top()
		
		
	def update_area(self, area_dict, width_dict):
		self.ble.update_area(area_dict, width_dict)
		self.local_mux.update_area(area_dict, width_dict)       
		
	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Update wires of things inside the logic cluster. """
		
		# Call wire update functions of member objects.
		self.ble.update_wires(width_dict, wire_lengths, wire_layers)
		self.local_mux.update_wires(width_dict, wire_lengths, wire_layers)
		self.local_routing_wire_load.update_wires(width_dict, wire_lengths, wire_layers)
		self.local_ble_output_load.update_wires(width_dict, wire_lengths, wire_layers)
		
		
	def print_details(self):
		self.local_mux.print_details()
		self.ble.print_details()
	
	   
class _RoutingWireLoad:
	""" This is the routing wire load for an architecture with direct drive and only one segment length.
		Two-level muxes are assumed and we model for partially on paths. """
		
	def __init__(self, wire_length):
		# Name of this wire
		self.name = "routing_wire_load"
		# Length of wire (in tiles)
		self.wire_length = wire_length
		# We assume that half of the wires in a routing channel are used (limited by routability)
		self.channel_usage_assumption = 0.5
		# We assume that half of the cluster inputs are used
		self.cluster_input_usage_assumption = 0.5
		# Switch block load per wire
		self.sb_load_on = -1
		self.sb_load_partial = -1
		self.sb_load_off = -1
		# Connection block load per wire
		self.cb_load_on = -1
		self.cb_load_partial = -1
		self.cb_load_off = -1
		# Switch block per tile
		self.tile_sb_on = []
		self.tile_sb_partial = []
		self.tile_sb_off = []
		# Connection block per tile
		self.tile_cb_on = []
		self.tile_cb_partial = []
		self.tile_cb_off = []
		# List of wire names in the SPICE circuit
		self.wire_names = []
		
		
	def generate(self, subcircuit_filename, specs, sb_mux, cb_mux):
		""" Generate the SPICE circuit for general routing wire load
			Need specs object, switch block object and connection block object """
		print "Generating routing wire load"
		# Calculate wire load based on architecture parameters
		self._compute_load(specs, sb_mux, cb_mux, self.channel_usage_assumption, self.cluster_input_usage_assumption)
		# Generate SPICE deck
		self.wire_names = load_subcircuits.general_routing_load_generate(subcircuit_filename, self.wire_length, self.tile_sb_on, self.tile_sb_partial, self.tile_sb_off, self.tile_cb_on, self.tile_cb_partial, self.tile_cb_off)
	
	
	def update_wires(self, width_dict, wire_lengths, wire_layers):
		""" Calculate wire lengths and wire layers. """

		# Update wire lengths
		wire_lengths["wire_gen_routing"] = self.wire_length*width_dict["tile"]
		wire_lengths["wire_sb_load_on"] = width_dict["tile"]/2
		wire_lengths["wire_sb_load_partial"] = width_dict["tile"]/2
		wire_lengths["wire_sb_load_off"] = width_dict["tile"]/2 
		wire_lengths["wire_cb_load_on"] = width_dict["tile"]/2
		wire_lengths["wire_cb_load_partial"] = width_dict["tile"]/2
		wire_lengths["wire_cb_load_off"] = width_dict["tile"]/2
		
		# Update wire layers
		wire_layers["wire_gen_routing"] = 1 
		wire_layers["wire_sb_load_on"] = 0 
		wire_layers["wire_sb_load_partial"] = 0 
		wire_layers["wire_sb_load_off"] = 0
		wire_layers["wire_cb_load_on"] = 0
		wire_layers["wire_cb_load_partial"] = 0 
		wire_layers["wire_cb_load_off"] = 0 
	
	
	def print_details(self):
		print "  ROUTING WIRE LOAD DETAILS"
		print "  Number of SB inputs connected to routing wire = " + str(self.sb_load_on + self.sb_load_partial + self.sb_load_off)
		print "  Wire: SB (on = " + str(self.sb_load_on) + ", partial = " + str(self.sb_load_partial) + ", off = " + str(self.sb_load_off) + ")"
		print "  Number of CB inputs connected to routing wire = " + str(self.cb_load_on + self.cb_load_partial + self.cb_load_off)
		print "  Wire: CB (on = " + str(self.cb_load_on) + ", partial = " + str(self.cb_load_partial) + ", off = " + str(self.cb_load_off) + ")"
		for i in range(self.wire_length):
			print "  Tile " + str(i+1) + ": SB (on = " + str(self.tile_sb_on[i]) + ", partial = " + str(self.tile_sb_partial[i]) + ", off = " + str(self.tile_sb_off[i]) + "); CB (on = " + str(self.tile_cb_on[i]) + ", partial = " + str(self.tile_cb_partial[i]) + ", off = " + str(self.tile_cb_off[i]) + ")"
		print ""
		
	   
	def _compute_load(self, specs, sb_mux, cb_mux, channel_usage, cluster_input_usage):
		""" Computes the load on a routing wire """
		
		# Local variables
		W = specs.W
		L = specs.L
		I = specs.I
		Fs = specs.Fs
		sb_mux_size = sb_mux.implemented_size
		cb_mux_size = cb_mux.implemented_size
		sb_level1_size = sb_mux.level1_size
		sb_level2_size = sb_mux.level2_size
		cb_level1_size = cb_mux.level1_size
		cb_level2_size = cb_mux.level2_size
		
		# Calculate switch block load per tile
		# Each tile has Fs-1 switch blocks hanging off of it exept the last one which has 3 (because the wire is ending)
		sb_load_per_intermediate_tile = (Fs - 1)
		# Calculate number of on/partial/off
		# We assume that each routing wire is only driving one more routing wire (at the end)
		self.sb_load_on = 1
		# Each used routing multiplexer comes with (sb_level2_size - 1) partially on paths. 
		# If all wires were used, we'd have (sb_level2_size - 1) partially on paths per wire, TODO: Is this accurate? See ble output load
		# but since we are just using a fraction of the wires, each wire has (sb_level2_size - 1)*channel_usage partially on paths connected to it.
		self.sb_load_partial = int(round(float(sb_level2_size - 1.0)*channel_usage))
		# The number of off sb_mux is (total - partial)
		self.sb_load_off = sb_load_per_intermediate_tile*L - self.sb_load_partial
		
		# Calculate connection block load per tile
		# We assume that cluster inputs are divided evenly between horizontal and vertical routing channels
		# We can get the total number of CB inputs connected to the channel segment by multiplying cluster inputs by cb_mux_size, then divide by W to get cb_inputs/wire
		cb_load_per_tile = int(round((I/2*cb_mux_size)/W))
		# Now we got to find out how many are on, how many are partially on and how many are off
		# For each tile, we have half of the cluster inputs connecting to a routing channel and only a fraction of these inputs are actually used
		# It is logical to assume that used cluster inputs will be connected to used routing wires, so we have I/2*input_usage inputs per tile,
		# we have L tiles so, I/2*input_usage*L fully on cluster inputs connected to W*channel_usage routing wires
		# If we look at the whole wire, we are selecting I/2*input_usage*L signals from W*channel_usage wires
		cb_load_on_probability = float((I/2.0*cluster_input_usage*L))/(W*channel_usage)
		self.cb_load_on = int(round(cb_load_on_probability))
		# If < 1, we round up to one because at least one wire will have a fully on path connected to it and we model for that case.
		if self.cb_load_on == 0:
			self.cb_load_on = 1 
		# Each fully turned on cb_mux comes with (cb_level2_size - 1) partially on paths
		# The number of partially on paths per tile is I/2*input_usage * (cb_level2_size - 1) 
		# Number of partially on paths per wire is (I/2*input_usage * (cb_level2_size - 1) * L) / W
		cb_load_partial_probability = (I/2*cluster_input_usage * (cb_level2_size - 1) * L) / W
		self.cb_load_partial = int(round(cb_load_partial_probability))
		# If < 1, we round up to one because at least one wire will have a partially on path connected to it and we model for that case.
		if self.cb_load_partial == 0:
			self.cb_load_partial = 1 
		# Number of off paths is just number connected to routing wire - on - partial
		self.cb_load_off = cb_load_per_tile*L - self.cb_load_partial - self.cb_load_on
	 
		# Now we want to figure out how to distribute this among the tiles. We have L tiles.
		tile_sb_on_budget = self.sb_load_on
		tile_sb_partial_budget = self.sb_load_partial
		tile_sb_off_budget = self.sb_load_off
		tile_sb_total_budget = tile_sb_on_budget + tile_sb_partial_budget + tile_sb_off_budget
		tile_sb_max = math.ceil(float(tile_sb_total_budget)/L)
		tile_sb_on = []
		tile_sb_partial = []
		tile_sb_off = []
		tile_sb_total = []

		# How this works: We have a certain amount of switch block mux connections to give to the wire,
		# we start at the furthest tile from the drive point and we allocate one mux input per tile iteratively until we run out of mux inputs.
		# The result of this is that on and partial mux inputs will be spread evenly along the wire with a bias towards putting 
		# them farthest away from the driver first (simulating a worst case).
		while tile_sb_total_budget != 0:
			# For each tile distribute load
			for i in range(L):
				# Add to lists
				if len(tile_sb_on) < (i+1):
					tile_sb_on.append(0)
				if len(tile_sb_partial) < (i+1):
					tile_sb_partial.append(0)
				if len(tile_sb_off) < (i+1):
					tile_sb_off.append(0)
				if len(tile_sb_total) < (i+1):
					tile_sb_total.append(0)
				# Distribute loads
				if tile_sb_on_budget != 0:
					if tile_sb_total[i] != tile_sb_max:
						tile_sb_on[i] = tile_sb_on[i] + 1
						tile_sb_on_budget = tile_sb_on_budget - 1
						tile_sb_total[i] = tile_sb_total[i] + 1
						tile_sb_total_budget = tile_sb_total_budget - 1
				if tile_sb_partial_budget != 0:
					if tile_sb_total[i] != tile_sb_max:
						tile_sb_partial[i] = tile_sb_partial[i] + 1
						tile_sb_partial_budget = tile_sb_partial_budget - 1
						tile_sb_total[i] = tile_sb_total[i] + 1
						tile_sb_total_budget = tile_sb_total_budget - 1
				if tile_sb_off_budget != 0:
					if tile_sb_total[i] != tile_sb_max:
						tile_sb_off[i] = tile_sb_off[i] + 1
						tile_sb_off_budget = tile_sb_off_budget - 1
						tile_sb_total[i] = tile_sb_total[i] + 1
						tile_sb_total_budget = tile_sb_total_budget - 1
		 
		# Assign these per-tile counts to the object
		self.tile_sb_on = tile_sb_on
		self.tile_sb_partial = tile_sb_partial
		self.tile_sb_off = tile_sb_off
		 
		tile_cb_on_budget = self.cb_load_on
		tile_cb_partial_budget = self.cb_load_partial
		tile_cb_off_budget = self.cb_load_off
		tile_cb_total_budget = tile_cb_on_budget + tile_cb_partial_budget + tile_cb_off_budget
		tile_cb_max = math.ceil(float(tile_cb_total_budget)/L)
		tile_cb_on = []
		tile_cb_partial = []
		tile_cb_off = []
		tile_cb_total = []

		while tile_cb_total_budget != 0:
			# For each tile distribute load
			for i in range(L):
				# Add to lists
				if len(tile_cb_on) < (i+1):
					tile_cb_on.append(0)
				if len(tile_cb_partial) < (i+1):
					tile_cb_partial.append(0)
				if len(tile_cb_off) < (i+1):
					tile_cb_off.append(0)
				if len(tile_cb_total) < (i+1):
					tile_cb_total.append(0)
				# Distribute loads
				if tile_cb_on_budget != 0:
					if tile_cb_total[i] != tile_cb_max:
						tile_cb_on[i] = tile_cb_on[i] + 1
						tile_cb_on_budget = tile_cb_on_budget - 1
						tile_cb_total[i] = tile_cb_total[i] + 1
						tile_cb_total_budget = tile_cb_total_budget - 1
				if tile_cb_partial_budget != 0:
					if tile_cb_total[i] != tile_cb_max:
						tile_cb_partial[i] = tile_cb_partial[i] + 1
						tile_cb_partial_budget = tile_cb_partial_budget - 1
						tile_cb_total[i] = tile_cb_total[i] + 1
						tile_cb_total_budget = tile_cb_total_budget - 1
				if tile_cb_off_budget != 0:
					if tile_cb_total[i] != tile_cb_max:
						tile_cb_off[i] = tile_cb_off[i] + 1
						tile_cb_off_budget = tile_cb_off_budget - 1
						tile_cb_total[i] = tile_cb_total[i] + 1
						tile_cb_total_budget = tile_cb_total_budget - 1
		
		# Assign these per-tile counts to the object
		self.tile_cb_on = tile_cb_on
		self.tile_cb_partial = tile_cb_partial
		self.tile_cb_off = tile_cb_off

  
class FPGA:
	""" This class describes an FPGA. """
		
	def __init__(self, N, K, W, L, I, Fs, Fcin, Fcout, Fclocal, Or, Ofb, Rsel, Rfb,
					vdd, vsram, vsram_n, gate_length, min_tran_width, min_width_tran_area, sram_cell_area, model_path, model_library, metal_stack, use_tgate):
		  
		# Initialize the specs
		self.specs = _Specs(N, K, W, L, I, Fs, Fcin, Fcout, Fclocal, Or, Ofb, Rsel, Rfb,
										vdd, vsram, vsram_n, gate_length, min_tran_width, min_width_tran_area, sram_cell_area, model_path, model_library)

										
		### CREATE SWITCH BLOCK OBJECT
		# Calculate switch block mux size (for direct-drive routing)
		# The mux will need Fs + (Fs-1)(L-1) inputs for routing-to-routing connections
		# The Fs term comes from starting wires, the (Fs-1) term comes from non-starting wires, of which there are (L-1)
		r_to_r_sb_mux_size = Fs + (Fs-1)*(L-1)
		# Then, each mux needs No*Fcout*L/2 additional inputs for logic cluster outputs (No = number of cluster outputs)
		No = self.specs.num_cluster_outputs
		clb_to_r_sb_mux_size = No*Fcout*L/2
		sb_mux_size_required = int(r_to_r_sb_mux_size + clb_to_r_sb_mux_size)
		# Calculate number of switch block muxes per tile
		num_sb_mux_per_tile = 2*W/L
		# Initialize the switch block
		self.sb_mux = _SwitchBlockMUX(sb_mux_size_required, num_sb_mux_per_tile)
		
		
		### CREATE CONNECTION BLOCK OBJECT
		# Calculate connection block mux size
		# Size is W*Fcin
		cb_mux_size_required = int(W*Fcin)
		num_cb_mux_per_tile = I
		# Initialize the connection block
		self.cb_mux = _ConnectionBlockMUX(cb_mux_size_required, num_cb_mux_per_tile)
		
		
		### CREATE LOGIC CLUSTER OBJECT
		# Calculate local mux size
		# Local mux size is (inputs + feedback) * population
		local_mux_size_required = int((I + Ofb*N) * Fclocal)
		num_local_mux_per_tile = N*K
		# Create the logic cluster object
		self.logic_cluster = _LogicCluster(N, K, Or, Ofb, Rsel, Rfb, local_mux_size_required, num_local_mux_per_tile, use_tgate)
		
		### CREATE LOAD OBJECTS
		# Create cluster output load object
		self.cluster_output_load = _GeneralBLEOutputLoad()
		# Create routing wire load object
		self.routing_wire_load = _RoutingWireLoad(L)
		
		
		### INITIALIZE OTHER VARIABLES, LISTS AND DICTIONARIES
		# Initialize SPICE library filenames
		self.wire_RC_filename = "wire_RC.l"
		self.process_data_filename = "process_data.l"
		self.includes_filename = "includes.l"
		self.basic_subcircuits_filename = "basic_subcircuits.l"
		self.subcircuits_filename = "subcircuits.l"
		self.sweep_data_filename = "sweep_data.l"
		
		# This is a dictionary of all the transistor sizes in the FPGA ('name': 'size')
		# It will contain the data in xMin transistor width, e.g. 'inv_sb_mux_1_nmos': '2'
		# That means inv_sb_mux_1_nmos is a transistor with 2x minimum width
		self.transistor_sizes = {}
		# This is a list of tuples containing area information for each transistor in the FPGA
		# Tuple: (tran_name, tran_channel_width_nm, tran_drive_strength, tran_area_min_areas, tran_area_nm, tran_width_nm)
		self.transistor_area_list = []
		
		# A note on the following 5 dictionaries
		# (area_dict, width_dict, wire_lengths, wire_layers, wire_rc_dict)
		#
		# Transistor sizes and wire lengths are needed at many different places in the SPICE netlists
		# that COFFE creates (e.g. the size of a particular transistor might be needed in many 
		# different files or multiple times in the same file). Since it would be a pain to have to 
		# go through every single line in every single file each time we want to change the size of 
		# a transistor (which will happen many thousands of times), COFFE inserts variables in the
		# SPICE netlists that it creates. These variables, which describe transistor sizes and wire 
		# loads, are assigned values in external files (one file for transistor sizes, one for wire loads). 
		# That way, when we change the size of a transistor (or a wire load), we only need to change
		# it in one place, and this change is seen by all SPICE netlists. 
		# The data structures that COFFE uses to keep track of transistor/circuit areas and wire data 
		# use a similar philosophy. That is, the following 5 dictionaries contain information about 
		# all element in the FPGA (all in one place). For ex., if we want to know the area of a switch block
		# multiplexer we ask 'area_dict' (e.g. area_dict['sb_mux']). One of the reasons for doing this
		# is that it makes outputing this data easier. For example, when we want to update that 'wire
		# load file' that the SPICE netlists use, all we need to do is write out wire_rc_dict to that file.
		# But, the 'fpga' object does not know how to update the area and wire data of each subcircuit.
		# Therefore, these dictionaries will be passed into member objects who will populate them as needed.
		# So, that's just something to keep in mind as you go through this code. You'll likely see these
		# dictionaries a lot.
		#
		# This is a dictionary that contains the area of everything for all levels of hierarchy in the FPGA. 
		# It has transistor area, inverter areas, mux areas, switch_block area, tile area.. etc. 
		# ('entity_name': area) All these areas are in nm^2
		self.area_dict = {}
		# This is a dictionary that contains the width of everything (much like area_dict has the areas).
		# ('entity_name': width) All widths are in nm. The width_dict is useful for figuring out wire lengths.
		self.width_dict = {}
		# This dictionary contains the lengths of all the wires in the FPGA. ('wire_name': length). Lengths in nm.
		self.wire_lengths = {}
		# This dictionary contains the metal layer for each wire. ('wire_name': layer)
		# The layer number (an int) is an index that will be used to select the right metal data
		# from the 'metal_stack' (list described below).
		self.wire_layers = {}
		# This dictionary contains wire resistance and capacitance for each wire as a tuple ('wire_name': (R, C))
		self.wire_rc_dict = {}
		
		# This dictionary contains the delays of all subcircuits (i.e. the max of rise and fall)
		# Contrary to the above 5 dicts, this one is not passed down into the other objects.
		# This dictionary is updated by calling 'update_delays()'
		self.delay_dict = {}
		
		# Metal stack. Lowest index is lowest metal layer. COFFE assumes that wire widths increase as we use higher metal layers.
		# For example, wires in metal_stack[1] are assumed to be wider (and/or more spaced) than wires in metal_stack[0]
		# e.g. metal_stack[0] = (R0, C0)
		self.metal_stack = metal_stack
		
		# weather or not to use transmission gates
		self.use_tgate = use_tgate

	def generate(self, is_size_transistors):
		""" This function generates all SPICE netlists and library files. """
	
		# Here's a file-stack that shows how COFFE organizes its SPICE files.
		# We'll talk more about each one as we generate them below.
	
		# ---------------------------------------------------------------------------------
		# |                                                                               |
		# |                top-level spice files (e.g. sb_mux.sp)                         |
		# |                                                                               |
		# ---------------------------------------------------------------------------------
		# |                                                                               |
		# |                                includes.l                                     |
		# |                                                                               |
		# ---------------------------------------------------------------------------------
		# |                                                                               |
		# |                               subcircuits.l                                   |
		# |                                                                               |
		# ---------------------------------------------------------------------------------
		# |                  |                       |                      |             |
		# |  process_data.l  |  basic_subcircuits.l  |  transistor_sizes.l  |  wire_RC.l  |
		# |                  |                       |                      |             |
		# ---------------------------------------------------------------------------------
	
	
		# TODO: We don't use the transistor_sizes.l file anymore.
		# But, we could add some kind of input file for transistor sizes...
		# If transistor sizing is turned off, we want to keep the transistor sizes
		# that are in 'transistor_sizes.l'. To do this, we keep a copy of the original file
		# as COFFE will overwrite the original, and then we replace the overwritten file with
		# our copy near the end of this function.
		#if is_size_transistors:
		#    print "TRANSISTOR SIZING MODE"
		#else:
		#    print "UPDATE MODE"
		#    os.rename("transistor_sizes.l", "transistor_sizes_hold.l")
		
		# Generate basic subcircuit library (pass-transistor, inverter, wire, etc.).
		# This library will be used to build other netlists.
		self._generate_basic_subcircuits()
		
		# Create 'subcircuits.l' library.
		# The subcircuit generation functions between 'self._create_lib_files()'
		# and 'self._end_lib_files()' will add things to these library files. 
		self._create_lib_files()
		
		# Generate the various subcircuits netlists of the FPGA (call members)
		self.transistor_sizes.update(self.sb_mux.generate(self.subcircuits_filename, 
														  self.specs.min_tran_width))
		self.transistor_sizes.update(self.cb_mux.generate(self.subcircuits_filename, 
														  self.specs.min_tran_width))
		self.transistor_sizes.update(self.logic_cluster.generate(self.subcircuits_filename, 
																 self.specs.min_tran_width, 
																 self.specs))
		self.cluster_output_load.generate(self.subcircuits_filename, self.specs, self.sb_mux)
		self.routing_wire_load.generate(self.subcircuits_filename, self.specs, self.sb_mux, self.cb_mux)
		
		# Add file footers to 'subcircuits.l' and 'transistor_sizes.l' libraries.
		self._end_lib_files()
		
		# Create SPICE library that contains process data and voltage level information
		self._generate_process_data()
		
		# This generates an include file. Top-level SPICE netlists only need to include
		# this 'include' file to include all libraries (for convenience).
		self._generate_includes()
		
		# Create the sweep_data.l file. COFFE will use this to perform multi-variable sweeps.
		self._generate_sweep_data()
		
		# Generate top-level files. These top-level files are the files that COFFE uses to measure 
		# the delay of FPGA circuitry. 
		self.sb_mux.generate_top()
		self.cb_mux.generate_top()
		self.logic_cluster.generate_top()
		
		# Delete new transistor sizes file if transistor sizing is turned off
		# and replace with our copy.
		# TODO: WE don't use the tran sizes file anymore
		#if not is_size_transistors:
		#    print "Restoring transistor sizes..."
		#    os.remove("transistor_sizes.l")
		#    os.rename("transistor_sizes_hold.l", "transistor_sizes.l")
		
		# Calculate area, and wire data.
		print "Calculating area..."
		# Update area values
		self.update_area()
		print "Calculating wire lengths..."
		self.update_wires()
		print "Calculating wire resistance and capacitance..."
		self.update_wire_rc()
		#print "Updating wire RC file..."
		#self.update_wire_rc_file()
	
		print ""
		

	def update_area(self):
		""" This function updates self.area_dict. It passes area_dict to member objects (like sb_mux)
			to update their area. Then, with an up-to-date area_dict it, calculate total tile area. """
		
		# We use the self.transistor_sizes to compute area. This dictionary has the form 'name': 'size'
		# And it knows the transistor sizes of all transistors in the FPGA
		# We first need to calculate the area for each transistor. 
		self._update_area_per_transistor()
		# Now, we have to update area_dict and width_dict with the new transistor area values
		self._update_area_and_width_dicts()
		
		# Calculate area of SRAM
		self.area_dict["sram"] = self.specs.sram_cell_area*self.specs.min_width_tran_area
		
		# Call area calculation functions of sub-blocks
		self.sb_mux.update_area(self.area_dict, self.width_dict)
		self.cb_mux.update_area(self.area_dict, self.width_dict)
		self.logic_cluster.update_area(self.area_dict, self.width_dict)
		
		# Calculate total area of switch block
		switch_block_area = self.sb_mux.num_per_tile*self.area_dict[self.sb_mux.name + "_sram"]
		self.area_dict["sb_total"] = switch_block_area
		self.width_dict["sb_total"] = math.sqrt(switch_block_area)
		
		# Calculate total area of connection block
		connection_block_area = self.cb_mux.num_per_tile*self.area_dict[self.cb_mux.name + "_sram"]
		self.area_dict["cb_total"] = connection_block_area
		self.width_dict["cb_total"] = math.sqrt(connection_block_area)
		
		# Calculate total area of local muxes
		local_mux_area = self.logic_cluster.local_mux.num_per_tile*self.area_dict[self.logic_cluster.local_mux.name + "_sram"]
		self.area_dict["local_mux_total"] = local_mux_area
		self.width_dict["local_mux_total"] = math.sqrt(local_mux_area)
		
		# Calculate total lut area
		lut_area = self.specs.N*self.area_dict["lut_and_drivers"]
		self.area_dict["lut_total"] = lut_area
		self.width_dict["lut_total"] = math.sqrt(lut_area)
		
		# Calculate total ff area
		ff_area = self.specs.N*self.area_dict[self.logic_cluster.ble.ff.name]
		self.area_dict["ff_total"] = ff_area
		self.width_dict["ff_total"] = math.sqrt(ff_area)
		
		# Calcualte total ble output area
		ble_output_area = self.specs.N*(self.area_dict["ble_output"])
		self.area_dict["ble_output_total"] = ble_output_area
		self.width_dict["ble_output_total"] = math.sqrt(ble_output_area)
		
		# Calculate area of logic cluster
		cluster_area = local_mux_area + lut_area + ff_area + ble_output_area
		self.area_dict["logic_cluster"] = cluster_area
		self.width_dict["logic_cluster"] = math.sqrt(cluster_area)
		
		# Calculate tile area
		tile_area = switch_block_area + connection_block_area + cluster_area
		self.area_dict["tile"] = tile_area
		self.width_dict["tile"] = math.sqrt(tile_area)
		
	
	def update_wires(self):
		""" This function updates self.wire_lengths and self.wire_layers. It passes wire_lengths and wire_layers to member 
			objects (like sb_mux) to update their wire lengths and layers. """
		
		# Update wire lengths and layers for all subcircuits
		self.sb_mux.update_wires(self.width_dict, self.wire_lengths, self.wire_layers)
		self.cb_mux.update_wires(self.width_dict, self.wire_lengths, self.wire_layers)
		self.logic_cluster.update_wires(self.width_dict, self.wire_lengths, self.wire_layers)
		self.cluster_output_load.update_wires(self.width_dict, self.wire_lengths, self.wire_layers)
		self.routing_wire_load.update_wires(self.width_dict, self.wire_lengths, self.wire_layers)
	   

	def update_wire_rc(self):
		""" This function updates self.wire_rc_dict based on the FPGA's self.wire_lengths and self.wire_layers."""
			
		# Calculate R and C for each wire
		for wire, length in self.wire_lengths.iteritems():
			# Get wire layer
			layer = self.wire_layers[wire]
			# Get R and C per unit length for wire layer
			rc = self.metal_stack[layer]
			# Calculate total wire R and C
			resistance = rc[0]*length
			capacitance = rc[1]*length/2
			# Add to wire_rc dictionary
			self.wire_rc_dict[wire] = (resistance, capacitance)     


	def update_delays(self, spice_interface):
		""" Extract HSPICE delays for each subcircuit. """
		
		crit_path_delay = 0
	   
		# Create parameter dict of all current transistor sizes and wire rc
		parameter_dict = {}
		for tran_name, tran_size in self.transistor_sizes.iteritems():
			parameter_dict[tran_name] = [1e-9*tran_size*self.specs.min_tran_width]
		for wire_name, rc_data in self.wire_rc_dict.iteritems():
			parameter_dict[wire_name + "_res"] = [rc_data[0]]
			parameter_dict[wire_name + "_cap"] = [rc_data[1]*1e-15]

		# Run HSPICE on all subcircuits and collect the total tfall and trise for that 
		# subcircuit. We are only doing a single run on HSPICE so we expect the result
		# to be in [0] of the spice_meas dictionary. We should probably check for
		# measurements that "failed" before converting to float... 

		# Switch Block MUX 
		print "Updating delay for " + self.sb_mux.name
		spice_meas = spice_interface.run(self.sb_mux.top_spice_path, parameter_dict) 
		tfall = float(spice_meas["meas_total_tfall"][0])
		trise = float(spice_meas["meas_total_trise"][0])
		self.sb_mux.tfall = tfall
		self.sb_mux.trise = trise
		self.sb_mux.delay = max(tfall, trise)
		crit_path_delay += self.sb_mux.delay*self.sb_mux.delay_weight
		self.delay_dict[self.sb_mux.name] = self.sb_mux.delay 
		
		# Connection Block MUX
		print "Updating delay for " + self.cb_mux.name
		spice_meas = spice_interface.run(self.cb_mux.top_spice_path, parameter_dict) 
		tfall = float(spice_meas["meas_total_tfall"][0])
		trise = float(spice_meas["meas_total_trise"][0])
		self.cb_mux.tfall = tfall
		self.cb_mux.trise = trise
		self.cb_mux.delay = max(tfall, trise)
		crit_path_delay += self.cb_mux.delay*self.cb_mux.delay_weight
		self.delay_dict[self.cb_mux.name] = self.cb_mux.delay
		
		# Local MUX
		print "Updating delay for " + self.logic_cluster.local_mux.name
		spice_meas = spice_interface.run(self.logic_cluster.local_mux.top_spice_path, 
										 parameter_dict) 
		tfall = float(spice_meas["meas_total_tfall"][0])
		trise = float(spice_meas["meas_total_trise"][0])
		self.logic_cluster.local_mux.tfall = tfall
		self.logic_cluster.local_mux.trise = trise
		self.logic_cluster.local_mux.delay = max(tfall, trise)
		crit_path_delay += (self.logic_cluster.local_mux.delay*
							self.logic_cluster.local_mux.delay_weight)
		self.delay_dict[self.logic_cluster.local_mux.name] = self.logic_cluster.local_mux.delay
		
		# Local BLE output
		print "Updating delay for " + self.logic_cluster.ble.local_output.name 
		spice_meas = spice_interface.run(self.logic_cluster.ble.local_output.top_spice_path, 
										 parameter_dict) 
		tfall = float(spice_meas["meas_total_tfall"][0])
		trise = float(spice_meas["meas_total_trise"][0])
		self.logic_cluster.ble.local_output.tfall = tfall
		self.logic_cluster.ble.local_output.trise = trise
		self.logic_cluster.ble.local_output.delay = max(tfall, trise)
		crit_path_delay += (self.logic_cluster.ble.local_output.delay*
							self.logic_cluster.ble.local_output.delay_weight)
		self.delay_dict[self.logic_cluster.ble.local_output.name] = self.logic_cluster.ble.local_output.delay
		
		# General BLE output
		print "Updating delay for " + self.logic_cluster.ble.general_output.name
		spice_meas = spice_interface.run(self.logic_cluster.ble.general_output.top_spice_path, 
										 parameter_dict) 
		tfall = float(spice_meas["meas_total_tfall"][0])
		trise = float(spice_meas["meas_total_trise"][0])
		self.logic_cluster.ble.general_output.tfall = tfall
		self.logic_cluster.ble.general_output.trise = trise
		self.logic_cluster.ble.general_output.delay = max(tfall, trise)
		crit_path_delay += (self.logic_cluster.ble.general_output.delay*
							self.logic_cluster.ble.general_output.delay_weight)
		self.delay_dict[self.logic_cluster.ble.general_output.name] = self.logic_cluster.ble.general_output.delay
		
		# LUT delay
		print "Updating delay for " + self.logic_cluster.ble.lut.name
		spice_meas = spice_interface.run(self.logic_cluster.ble.lut.top_spice_path, 
										 parameter_dict) 
		tfall = float(spice_meas["meas_total_tfall"][0])
		trise = float(spice_meas["meas_total_trise"][0])
		self.logic_cluster.ble.lut.tfall = tfall
		self.logic_cluster.ble.lut.trise = trise
		self.logic_cluster.ble.lut.delay = max(tfall, trise)
		self.delay_dict[self.logic_cluster.ble.lut.name] = self.logic_cluster.ble.lut.delay
		
		# Get delay for all paths through the LUT.
		# We get delay for each path through the LUT as well as for the LUT input drivers.
		for lut_input_name, lut_input in self.logic_cluster.ble.lut.input_drivers.iteritems():
			driver = lut_input.driver
			not_driver = lut_input.not_driver

			# Get the delay for a path through the LUT (we do it for each input)
			print "Updating delay for " + driver.name.replace("_driver", "")
			driver_and_lut_sp_path = driver.top_spice_path.replace(".sp", "_with_lut.sp")
			spice_meas = spice_interface.run(driver_and_lut_sp_path, parameter_dict) 
			tfall = float(spice_meas["meas_total_tfall"][0])
			trise = float(spice_meas["meas_total_trise"][0])
			lut_input.tfall = tfall
			lut_input.trise = trise
			lut_input.delay = max(tfall, trise)
			self.delay_dict[lut_input.name] = lut_input.delay
			
			# Now, we want to get the delay and power for the driver
			print "Updating delay for " + driver.name 
			spice_meas = spice_interface.run(driver.top_spice_path, parameter_dict) 
			tfall = float(spice_meas["meas_total_tfall"][0])
			trise = float(spice_meas["meas_total_trise"][0])
			driver.tfall = tfall
			driver.trise = trise
			driver.delay = max(tfall, trise)
			self.delay_dict[driver.name] = driver.delay

			# ... and the not_driver
			print "Updating delay for " + not_driver.name
			spice_meas = spice_interface.run(not_driver.top_spice_path, parameter_dict) 
			tfall = float(spice_meas["meas_total_tfall"][0])
			trise = float(spice_meas["meas_total_trise"][0])
			not_driver.tfall = tfall
			not_driver.trise = trise
			not_driver.delay = max(tfall, trise)
			self.delay_dict[not_driver.name] = not_driver.delay
			
			lut_delay = lut_input.delay + max(driver.delay, not_driver.delay)
			crit_path_delay += lut_delay*lut_input.delay_weight
		
		self.delay_dict["rep_crit_path"] = crit_path_delay
		
		print ""
		
		return
				  
				  
	def print_specs(self):
		print "FPGA ARCHITECTURE SPECS:"
		print "Number of BLEs per cluster (N): " + str(self.specs.N)
		print "LUT size (K): " + str(self.specs.K)
		print "Channel width (W): " + str(self.specs.W)
		print "Wire segment length (L): " + str(self.specs.L)
		print "Number cluster inputs (I): " + str(self.specs.I)
		print "Number of BLE outputs to general routing: " + str(self.specs.num_ble_general_outputs)
		print "Number of BLE outputs to local routing: " + str(self.specs.num_ble_local_outputs)
		print "Number of cluster outputs: " + str(self.specs.num_cluster_outputs)
		print "Switch block flexibility (Fs): " + str(self.specs.Fs)
		print "Cluster input flexibility (Fcin): " + str(self.specs.Fcin)
		print "Cluster output flexibility (Fcout): " + str(self.specs.Fcout)
		print "Local MUX population (Fclocal): " + str(self.specs.Fclocal)
		print ""
		
		
	def print_details(self):
	
		print "|------------------------------------------------------------------------------|"
		print "|   FPGA Implementation Details                                                  |"
		print "|------------------------------------------------------------------------------|"
		print ""
		self.sb_mux.print_details()
		self.cb_mux.print_details()
		self.logic_cluster.print_details()
		self.cluster_output_load.print_details()
		self.routing_wire_load.print_details()
		print "|------------------------------------------------------------------------------|"
		print ""
	
	
	def _area_model(self, tran_name, tran_size):
		""" Transistor area model. 'tran_size' is the transistor drive strength in min. width transistor drive strengths. 
			Transistor area is calculated bsed on 'tran_size' and transistor type, which is determined by tags in 'tran_name'.
			Return valus is the transistor area in minimum width transistor areas. """
	
		# If inverter or transmission gate, use larger area to account for N-well spacing
		# If pass-transistor, use regular area because they don't need N-wells.
		if "inv_" in tran_name or "tgate_" in tran_name:
			area = 0.518 + 0.127*tran_size + 0.428*math.sqrt(tran_size)
		else:
			area = 0.447 + 0.128*tran_size + 0.391*math.sqrt(tran_size)
	
		return area    
	 
	 
	def _create_lib_files(self):
		""" Create SPICE library files and add headers. """

		# Create Subcircuits file
		sc_file = open(self.subcircuits_filename, 'w')
		sc_file.write("*** SUBCIRCUITS\n\n")
		sc_file.write(".LIB SUBCIRCUITS\n\n")
		sc_file.close()
	   

	def _end_lib_files(self):
		""" End the SPICE library files. """

		# Subcircuits file
		sc_file = open(self.subcircuits_filename, 'a')
		sc_file.write(".ENDL SUBCIRCUITS")
		sc_file.close()
	   

	def _generate_basic_subcircuits(self):
		""" Generates the basic subcircuits SPICE file (pass-transistor, inverter, etc.) """
		
		print "Generating basic subcircuits"
		
		# Open basic subcircuits file and write heading
		basic_sc_file = open(self.basic_subcircuits_filename, 'w')
		basic_sc_file.write("*** BASIC SUBCIRCUITS\n\n")
		basic_sc_file.write(".LIB BASIC_SUBCIRCUITS\n\n")
		basic_sc_file.close()

		# Generate wire subcircuit
		basic_subcircuits.wire_generate(self.basic_subcircuits_filename)
		# Generate pass-transistor subcircuit
		basic_subcircuits.ptran_generate(self.basic_subcircuits_filename)
		# Generate transmission gate subcircuit
		basic_subcircuits.tgate_generate(self.basic_subcircuits_filename)
		# Generate level-restore subcircuit
		basic_subcircuits.rest_generate(self.basic_subcircuits_filename)
		# Generate inverter subcircuit
		basic_subcircuits.inverter_generate(self.basic_subcircuits_filename)

		# Write footer
		basic_sc_file = open(self.basic_subcircuits_filename, 'a')
		basic_sc_file.write(".ENDL BASIC_SUBCIRCUITS")
		basic_sc_file.close()
		
		
	def _generate_process_data(self):
		""" Write the process data library file. It contains voltage levels, gate length and device models. """
		
		print "Generating process data file"
		
		process_data_file = open(self.process_data_filename, 'w')
		process_data_file.write("*** PROCESS DATA AND VOLTAGE LEVELS\n\n")
		process_data_file.write(".LIB PROCESS_DATA\n\n")
		process_data_file.write("* Voltage levels\n")
		process_data_file.write(".PARAM supply_v = " + str(self.specs.vdd) + "\n")
		process_data_file.write(".PARAM sram_v = " + str(self.specs.vsram) + "\n")
		process_data_file.write(".PARAM sram_n_v = " + str(self.specs.vsram_n) + "\n\n")
		process_data_file.write("* Gate length\n")
		process_data_file.write(".PARAM gate_length = " + str(self.specs.gate_length) + "n\n\n")
		process_data_file.write("* We have two supply rails, vdd and vdd_subckt.\n")
		process_data_file.write("* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry\n")
		process_data_file.write("VSUPPLY vdd gnd supply_v\n")
		process_data_file.write("VSUBCKT vdd_subckt gnd supply_v\n\n")
		process_data_file.write("* SRAM voltages connecting to gates\n")
		process_data_file.write("VSRAM vsram gnd sram_v\n")
		process_data_file.write("VSRAM_N vsram_n gnd sram_n_v\n\n")
		process_data_file.write("* Device models\n")
		process_data_file.write(".LIB \"" + self.specs.model_path + "\" " + self.specs.model_library + "\n\n")
		process_data_file.write(".ENDL PROCESS_DATA")
		process_data_file.close()
		
		
	def _generate_includes(self):
		""" Generate the includes file. Top-level SPICE decks should only include this file. """
	
		print "Generating includes file"
	
		includes_file = open(self.includes_filename, 'w')
		includes_file.write("*** INCLUDE ALL LIBRARIES\n\n")
		includes_file.write(".LIB INCLUDES\n\n")
		includes_file.write("* Include process data (voltage levels, gate length and device models library)\n")
		includes_file.write(".LIB \"process_data.l\" PROCESS_DATA\n\n")
		includes_file.write("* Include transistor parameters\n")
		includes_file.write("* Include wire resistance and capacitance\n")
		#includes_file.write(".LIB \"wire_RC.l\" WIRE_RC\n\n")
		includes_file.write("* Include basic subcircuits\n")
		includes_file.write(".LIB \"basic_subcircuits.l\" BASIC_SUBCIRCUITS\n\n")
		includes_file.write("* Include subcircuits\n")
		includes_file.write(".LIB \"subcircuits.l\" SUBCIRCUITS\n\n")
		includes_file.write("* Include sweep data file for .DATA sweep analysis\n")
		includes_file.write(".INCLUDE \"sweep_data.l\"\n\n")
		includes_file.write(".ENDL INCLUDES")
		includes_file.close()
		
		
	def _generate_sweep_data(self):
		""" Create the sweep_data.l file that COFFE uses to perform 
			multi-variable HSPICE parameter sweeping. """

		sweep_data_file = open(self.sweep_data_filename, 'w')
		sweep_data_file.close()
		

	def _update_transistor_sizes(self, element_names, combo, inv_ratios=None):
		""" This function is used to update self.transistor_sizes for a particular transistor sizing combination.
			'element_names' is a list of elements (ptran, inv, etc.) that need their sizes updated.
			'combo' is a particular transistor sizing combination for the transistors in 'element_names'
			'inv_ratios' are the inverter P/N ratios for this transistor sizing combination.
			'combo' will typically describe only a small group of transistors. Other transistors retain their current size."""
		
		# We start by making a dictionary of the transistor sizes we need to update
		new_sizes = {}
		for i in range(len(combo)):
			element_name = element_names[i]
			# If it's a pass-transistor, we just add the NMOS size
			if "ptran_" in element_name:
				new_sizes[element_name + "_nmos"] = combo[i]
			# If it's a level-restorer, we just add the PMOS size
			elif "rest_" in element_name:
				new_sizes[element_name + "_pmos"] = combo[i]
			# If it's an inverter, we have to add both NMOS and PMOS sizes
			elif "inv_" in element_name:
				if inv_ratios == None:
					# If no inverter ratios are specified, NMOS and PMOS are equal size
					new_sizes[element_name + "_nmos"] = combo[i]
					new_sizes[element_name + "_pmos"] = combo[i]
				else:
					# If there are inverter ratios, we use them to give different sizes to NMOS and PMOS
					if inv_ratios[element_name] < 1:
						# NMOS is larger than PMOS
						new_sizes[element_name + "_nmos"] = combo[i]/inv_ratios[element_name]
						new_sizes[element_name + "_pmos"] = combo[i]
					else:
						# PMOS is larger than NMOS
						new_sizes[element_name + "_nmos"] = combo[i]
						new_sizes[element_name + "_pmos"] = combo[i]*inv_ratios[element_name]
		
		# Now, update self.transistor_sizes with these new sizes
		self.transistor_sizes.update(new_sizes)
	  
	  
	def _update_area_per_transistor(self):
		""" We use self.transistor_sizes to calculate area
			Using the area model, we calculate the transistor area in minimum width transistor areas.
			We also calculate area in nm and transistor width in nm. Nanometer values are needed for wire length calculations.
			For each transistor, this data forms a tuple (tran_name, tran_channel_width_nm, tran_drive_strength, tran_area_min_areas, tran_area_nm, tran_width_nm)
			The FPGAs transistor_area_list is updated once these values are computed."""
		
		# Initialize transistor area list
		tran_area_list = []
		
		# For each transistor, calculate area
		for tran_name, tran_size in self.transistor_sizes.iteritems():
				# Get transistor drive strength (drive strength is = xMin width)
				tran_drive = tran_size
				# Get tran area in min transistor widths
				tran_area = self._area_model(tran_name, tran_drive)
				# Get area in nm square
				tran_area_nm = tran_area*self.specs.min_width_tran_area
				# Get width of transistor in nm
				tran_width = math.sqrt(tran_area_nm)
				# Add this as a tuple to the tran_area_list
				tran_area_list.append((tran_name, tran_size, tran_drive, tran_area, 
												tran_area_nm, tran_width))
												
	
		# Assign list to FPGA object
		self.transistor_area_list = tran_area_list
		

	def _update_area_and_width_dicts(self):
		""" Calculate area for basic subcircuits like inverters, pass transistor, 
			transmission gates, etc. Update area_dict and width_dict with this data."""
		
		# Initialize component area list
		comp_area_list = []
		
		# Create a dictionary to store component sizes for multi-transistor components
		comp_dict = {}
		
		# For each transistor in the transistor_area_list
		for tran in self.transistor_area_list:
			if "inv_" in tran[0] or "tgate_" in tran[0]:
				# Get the component name
				comp_name = tran[0].replace("_nmos", "")
				comp_name = comp_name.replace("_pmos", "")
				
				# If the component is already in the dictionary
				if comp_name in comp_dict:
					if "_nmos" in tran[0]:
						comp_dict[comp_name]["nmos"] = tran[4]
					else:
						comp_dict[comp_name]["pmos"] = tran[4]
						
					# At this point we should have both NMOS and PMOS sizes in the dictionary
					# We can calculate the area of the inverter or tgate by doing the sum
					comp_area = comp_dict[comp_name]["nmos"] + comp_dict[comp_name]["pmos"]
					comp_width = math.sqrt(comp_area)
					comp_area_list.append((comp_name, comp_area, comp_width))         
						
				else:
					# Create a dict for this component to store nmos and pmos sizes
					comp_area_dict = {}
					# Add either the nmos or pmos item
					if "_nmos" in tran[0]:
						comp_area_dict["nmos"] = tran[4]
					else:
						comp_area_dict["pmos"] = tran[4]
						
					# Add this inverter to the inverter dictionary    
					comp_dict[comp_name] = comp_area_dict
					
			elif "ptran_" in tran[0] or "rest_" in tran[0] or "tran_" in tran[0]:   
				# Get the comp name
				comp_name = tran[0].replace("_nmos", "")
				comp_name = comp_name.replace("_pmos", "")
				
				# Add this to comp_area_list directly
				comp_area_list.append((comp_name, tran[4], tran[5]))            
		
		# Convert comp_area_list to area_dict and width_dict
		area_dict = {}
		width_dict = {}
		for component in comp_area_list:
			area_dict[component[0]] = component[1]
			width_dict[component[0]] = component[2]
		
		# Set the FPGA object area and width dict
		self.area_dict = area_dict
		self.width_dict = width_dict
  
		return
