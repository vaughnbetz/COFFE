import sys
import os
import shutil
import time 
import datetime


def compare_tfall_trise(tfall, trise):
    """ Compare tfall and trise and returns largest value or -1.0
        -1.0 is return if something went wrong in SPICE """
    
    # Initialize output delay
    delay = -1.0
    
    # Compare tfall and trise
    if (tfall == 0.0) or (trise == 0.0):
        # Couldn't find one of the values in output
        # This is an error because maybe SPICE failed
        delay = -1.0
    elif tfall > trise:
        if tfall > 0.0:
            # tfall is positive and bigger than the trise, this is a valid result
            delay = tfall
        else:
            # Both tfall and trise are negative, this is an invalid result
            delay = -1.0
    elif trise >= tfall:
        if trise > 0.0:
            # trise is positive and larger or equal to tfall, this is value result
            delay = trise
        else:
            delay = -1.0
    else:
        delay = -1.0
        
    return delay
   
    
def print_area_and_delay(report_file, fpga_inst):
    """ Print area and delay per subcircuit """
    
    print_and_write(report_file, "  SUBCIRCUIT AREA, DELAY & POWER")
    print_and_write(report_file, "  ------------------------------")
    
    area_dict = fpga_inst.area_dict

    # I'm using 'ljust' to create neat columns for printing this data. 
    # If subcircuit names are changed, it might make this printing function 
    # not work as well. The 'ljust' constants would have to be adjusted accordingly.
    
    # Print the header
    print_and_write(report_file, "  Subcircuit".ljust(24) + "Area (um^2)".ljust(13) + "Delay (ps)".ljust(13) + "tfall (ps)".ljust(13) + "trise (ps)".ljust(13) + "Power at 250MHz (uW)".ljust(22)) 
    
    # Switch block mux
    print_and_write(report_file, "  " + fpga_inst.sb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.sb_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.sb_mux.delay/1e-12,4)).ljust(13) + 
        str(round(fpga_inst.sb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.sb_mux.trise/1e-12,4)).ljust(13) + str(fpga_inst.sb_mux.power/1e-6).ljust(22))
    
    # Connection block mux
    print_and_write(report_file, "  " + fpga_inst.cb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.cb_mux.name]/1e6,3)).ljust(13) + str(round(fpga_inst.cb_mux.delay/1e-12,4)).ljust(13) + 
        str(round(fpga_inst.cb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.cb_mux.trise/1e-12,4)).ljust(13) + str(fpga_inst.cb_mux.power/1e-6))
    
    # Local mux
    print_and_write(report_file, "  " + fpga_inst.logic_cluster.local_mux.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.local_mux.name]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.logic_cluster.local_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.local_mux.tfall/1e-12,4)).ljust(13) + 
        str(round(fpga_inst.logic_cluster.local_mux.trise/1e-12,4)).ljust(13) + str(fpga_inst.logic_cluster.local_mux.power/1e-6))
    
    # Local BLE output
    print_and_write(report_file, "  " + fpga_inst.logic_cluster.ble.local_output.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.local_output.name]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.logic_cluster.ble.local_output.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.local_output.tfall/1e-12,4)).ljust(13) + 
        str(round(fpga_inst.logic_cluster.ble.local_output.trise/1e-12,4)).ljust(13) + str(fpga_inst.logic_cluster.ble.local_output.power/1e-6))
    
    # General BLE output
    print_and_write(report_file, "  " + fpga_inst.logic_cluster.ble.general_output.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.general_output.name]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.logic_cluster.ble.general_output.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output.tfall/1e-12,4)).ljust(13) + 
        str(round(fpga_inst.logic_cluster.ble.general_output.trise/1e-12,4)).ljust(13) + str(fpga_inst.logic_cluster.ble.general_output.power/1e-6))

    # General BLE output 3:1
    if fpga_inst.updates:
        print_and_write(report_file, "  " + fpga_inst.logic_cluster.ble.general_output3.name.ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.general_output3.name]/1e6,3)).ljust(13) + 
            str(round(fpga_inst.logic_cluster.ble.general_output3.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.general_output3.tfall/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.logic_cluster.ble.general_output3.trise/1e-12,4)).ljust(13) + str(fpga_inst.logic_cluster.ble.general_output3.power/1e-6))
    
    # LUT
    print_and_write(report_file, "  " + (fpga_inst.logic_cluster.ble.lut.name + " (SRAM to out)").ljust(22) + str(round(area_dict[fpga_inst.logic_cluster.ble.lut.name]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.logic_cluster.ble.lut.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.logic_cluster.ble.lut.tfall/1e-12,4)).ljust(13) + 
        str(round(fpga_inst.logic_cluster.ble.lut.trise/1e-12,4)).ljust(13) + "n/a".ljust(22))
    
    # Get LUT input names so that we can print inputs in sorted order
    lut_input_names = fpga_inst.logic_cluster.ble.lut.input_drivers.keys()
    lut_input_names.sort()
      
    # LUT input drivers
    for input_name in lut_input_names:
        lut_input = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name]
        print_and_write(report_file, "  " + ("lut_" + input_name).ljust(22) + "n/a".ljust(13) + str(round(lut_input.delay/1e-12,4)).ljust(13) + str(round(lut_input.trise/1e-12,4)).ljust(13) + 
            str(round(lut_input.tfall/1e-12,4)).ljust(13) + str(lut_input.power/1e-6).ljust(22))

        driver = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name].driver
        not_driver = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name].not_driver
        print_and_write(report_file, "  " + driver.name.ljust(22) + str(round(area_dict[driver.name]/1e6,3)).ljust(13) + str(round(driver.delay/1e-12,4)).ljust(13) + 
            str(round(driver.tfall/1e-12,4)).ljust(13) + str(round(driver.trise/1e-12,4)).ljust(13) + str(driver.power/1e-6).ljust(22))
        print_and_write(report_file, "  " + not_driver.name.ljust(22) + str(round(area_dict[not_driver.name]/1e6,3)).ljust(13) + str(round(not_driver.delay/1e-12,4)).ljust(13) + 
            str(round(not_driver.tfall/1e-12,4)).ljust(13) + str(round(not_driver.trise/1e-12,4)).ljust(13) + str(not_driver.power/1e-6).ljust(22))

    # Carry chain    
    if fpga_inst.specs.enable_carry_chain == 1:
        #carry path
        print_and_write(report_file, "  " + (fpga_inst.carrychain.name).ljust(22) + str(round(area_dict[fpga_inst.carrychain.name]/1e6,3)).ljust(13) + 
            str(round(fpga_inst.carrychain.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.carrychain.tfall/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.carrychain.trise/1e-12,4)).ljust(13) + "n/a".ljust(22))
        # Sum inverter
        print_and_write(report_file, "  " + (fpga_inst.carrychainperf.name).ljust(22) + str(round(area_dict[fpga_inst.carrychainperf.name]/1e6,3)).ljust(13) + 
            str(round(fpga_inst.carrychainperf.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.carrychainperf.tfall/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.carrychainperf.trise/1e-12,4)).ljust(13) + "n/a".ljust(22))
        # mux
        if not fpga_inst.updates:
            print_and_write(report_file, "  " + (fpga_inst.carrychainmux.name).ljust(22) + str(round(area_dict[fpga_inst.carrychainmux.name]/1e6,3)).ljust(13) + 
                str(round(fpga_inst.carrychainmux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.carrychainmux.tfall/1e-12,4)).ljust(13) + 
                str(round(fpga_inst.carrychainmux.trise/1e-12,4)).ljust(13) + "n/a".ljust(22))
        # Intercluster
        print_and_write(report_file, "  " + (fpga_inst.carrychaininter.name).ljust(22) + str(round(area_dict[fpga_inst.carrychaininter.name]/1e6,3)).ljust(13) + 
            str(round(fpga_inst.carrychaininter.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.carrychaininter.tfall/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.carrychaininter.trise/1e-12,4)).ljust(13) + "n/a".ljust(22))
        # total carry chain area
        print_and_write(report_file, "  " + "total carry chain area".ljust(22) + str(round(area_dict["total_carry_chain"]/1e6,3)).ljust(13))

        if fpga_inst.specs.carry_chain_type == "skip":
            # skip and
            print_and_write(report_file, "  " + (fpga_inst.carrychainand.name).ljust(22) + str(round(area_dict[fpga_inst.carrychainand.name]/1e6,3)).ljust(13) + 
                str(round(fpga_inst.carrychainand.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.carrychainand.tfall/1e-12,4)).ljust(13) + 
                str(round(fpga_inst.carrychainand.trise/1e-12,4)).ljust(13) + "n/a".ljust(22))
            # skip mux
            print_and_write(report_file, "  " + (fpga_inst.carrychainskipmux.name).ljust(22) + str(round(area_dict[fpga_inst.carrychainskipmux.name]/1e6,3)).ljust(13) + 
                str(round(fpga_inst.carrychainskipmux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.carrychainskipmux.tfall/1e-12,4)).ljust(13) + 
                str(round(fpga_inst.carrychainskipmux.trise/1e-12,4)).ljust(13) + "n/a".ljust(22))



    for hardblock in fpga_inst.hardblocklist:
        ############################################
        ## Size dedicated routing links
        ############################################
        if hardblock.parameters['num_dedicated_outputs'] > 0:
            print_and_write(report_file, "  dedicated link ".ljust(24) + str(round(fpga_inst.area_dict[hardblock.dedicated.name]/1e6,3)).ljust(13) + 
                str(round(hardblock.dedicated.delay/1e-12,4)).ljust(13) + str(round(hardblock.dedicated.tfall/1e-12,4)).ljust(13) + 
                str(round(hardblock.dedicated.trise/1e-12,4)).ljust(13) + str(hardblock.dedicated.power/1e-6).ljust(22))
        
        print_and_write(report_file, "  mux " + str(hardblock.parameters['name']).ljust(24) + str(round(fpga_inst.area_dict[hardblock.mux.name +"_sram"]/1e6,3)).ljust(13) + 
            str(round(hardblock.mux.delay/1e-12,4)).ljust(13) + str(round(hardblock.mux.tfall/1e-12,4)).ljust(13) + str(round(hardblock.mux.trise/1e-12,4)).ljust(13) + 
            str(hardblock.mux.power/1e-6).ljust(22))

        
    # Connection block mux
    print_and_write(report_file, "  " + fpga_inst.cb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.cb_mux.name +"_sram"]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.cb_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.cb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.cb_mux.trise/1e-12,4)).ljust(13) + 
        str(fpga_inst.cb_mux.power/1e-6))
    
    # Switch block mux,
    print_and_write(report_file, "  " + fpga_inst.sb_mux.name.ljust(22) + str(round(area_dict[fpga_inst.sb_mux.name +"_sram"]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.sb_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.sb_mux.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.sb_mux.trise/1e-12,4)).ljust(13) + 
        str(fpga_inst.sb_mux.power/1e-6).ljust(22))
    

    if fpga_inst.specs.enable_bram_block == 0:
        print_and_write(report_file, "\n")
        return 


    # RAM

    # RAM local input mux
    print_and_write(report_file, "  " + fpga_inst.RAM.RAM_local_mux.name.ljust(22) + str(round(fpga_inst.area_dict["ram_local_mux_total"]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.RAM.RAM_local_mux.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.RAM_local_mux.tfall/1e-12,4)).ljust(13) + 
        str(round(fpga_inst.RAM.RAM_local_mux.trise/1e-12,4)).ljust(13) + str(fpga_inst.RAM.RAM_local_mux.power/1e-6).ljust(22))
    
    # Row decoder:
    stage1_delay = 0.0
    stage0_delay = 0.0
    stage2_delay = 0.0
    stage3_delay = 0.0
    stage0_delay = fpga_inst.RAM.rowdecoder_stage0.delay

    if fpga_inst.RAM.valid_row_dec_size3 == 1:
        stage1_delay = fpga_inst.RAM.rowdecoder_stage1_size3.delay
    if fpga_inst.RAM.valid_row_dec_size2 == 1:
        if fpga_inst.RAM.rowdecoder_stage1_size2.delay > stage1_delay:
            stage1_delay = fpga_inst.RAM.rowdecoder_stage1_size2.delay
    stage3_delay = fpga_inst.RAM.rowdecoder_stage3.delay

    row_decoder_delay =  stage0_delay + stage1_delay + stage3_delay + stage2_delay

    print_and_write(report_file, "  Row Decoder".ljust(24) + str(round(fpga_inst.area_dict["decoder"]/1e6,3)).ljust(13) + str(round(row_decoder_delay/1e-12,4)).ljust(13) + 
        "n/m".ljust(13) + "n/m".ljust(13) + "n/m".ljust(22))    

    print "  Power Breakdown: ".ljust(24) + "stage0".ljust(22)+ str(round(fpga_inst.RAM.rowdecoder_stage0.power/1e-6,4)).ljust(22)

    if fpga_inst.RAM.valid_row_dec_size2 == 1:
        print "  Power Breakdown: ".ljust(24) + "stage1".ljust(22)+ str(round(fpga_inst.RAM.rowdecoder_stage1_size2.power/1e-6,4)).ljust(22)
    if fpga_inst.RAM.valid_row_dec_size3 == 1:
        print "  Power Breakdown: ".ljust(24) + "stage1".ljust(22)+ str(round(fpga_inst.RAM.rowdecoder_stage1_size3.power/1e-6,4)).ljust(22)
    print "  Power Breakdown: ".ljust(24) + "stage2".ljust(22)+ str(round(fpga_inst.RAM.rowdecoder_stage3.power/1e-6,4)).ljust(22)        

    # Configurable decoder:
    configdelay = fpga_inst.RAM.configurabledecoderi.delay 

    if fpga_inst.RAM.cvalidobj1 !=0 and fpga_inst.RAM.cvalidobj2 !=0:
        configdelay += max(fpga_inst.RAM.configurabledecoder3ii.delay, fpga_inst.RAM.configurabledecoder2ii.delay)
    elif fpga_inst.RAM.cvalidobj1 !=0:
        configdelay += fpga_inst.RAM.configurabledecoder3ii.delay
    else:
        configdelay += fpga_inst.RAM.configurabledecoder2ii.delay

    # Column decoder:
    print_and_write(report_file, "  Column Decoder".ljust(24) + str(round(fpga_inst.area_dict["columndecoder_total"]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.RAM.columndecoder.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.columndecoder.tfall/1e-12,4)).ljust(13) + 
        str(round(fpga_inst.RAM.columndecoder.trise/1e-12,4)).ljust(13) + str(fpga_inst.RAM.columndecoder.power/1e-6).ljust(22))
    print_and_write(report_file, "  Configurable Decoder".ljust(24) + str(round(fpga_inst.area_dict["configurabledecoder"]/1e6,3)).ljust(13) + 
        str(round(configdelay/1e-12,4)).ljust(13) + "n/m".ljust(13) + "n/m".ljust(13) + "n/m".ljust(22))
    print_and_write(report_file, "  CD driver delay ".ljust(24) + "n/a".ljust(13) + 
        str(round(fpga_inst.RAM.configurabledecoderiii.delay/1e-12,4)).ljust(13) + "n/m".ljust(13) + "n/m".ljust(13) + "n/m".ljust(22))

    print "  Power Breakdown: ".ljust(24) + "stage0".ljust(22)+ str(round(fpga_inst.RAM.configurabledecoderi.power/1e-6,4)).ljust(22)
    if fpga_inst.RAM.cvalidobj2 !=0:
        print "  Power Breakdown: ".ljust(24) + "stage1".ljust(22)+ str(round(fpga_inst.RAM.configurabledecoder2ii.power/1e-6,4)).ljust(22)
    if fpga_inst.RAM.cvalidobj1 !=0:    
        print "  Power Breakdown: ".ljust(24) + "stage1".ljust(22)+ str(round(fpga_inst.RAM.configurabledecoder3ii.power/1e-6,4)).ljust(22)
    print "  Power Breakdown: ".ljust(24) + "stage2".ljust(22)+ str(round(fpga_inst.RAM.configurabledecoderiii.power/1e-6,4)).ljust(22)


    # BRAM output crossbar:
    print_and_write(report_file, "  Output Crossbar".ljust(24) + str(round(fpga_inst.area_dict["pgateoutputcrossbar_sram"]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.RAM.pgateoutputcrossbar.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.pgateoutputcrossbar.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.pgateoutputcrossbar.trise/1e-12,4)).ljust(13) + str(fpga_inst.RAM.pgateoutputcrossbar.power/1e-6).ljust(22))
    
    # reporting technology-specific part of the BRAM (sense amplifier, precharge/predischarge and write driver/bitline charge)
    if fpga_inst.RAM.memory_technology == "SRAM":
        print_and_write(report_file, "  sense amp".ljust(24) + str(round(fpga_inst.area_dict["samp_total"]/1e6,3)).ljust(13) + 
            str(round((fpga_inst.RAM.samp.delay + fpga_inst.RAM.samp_part2.delay)/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.samp.tfall/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.RAM.samp.trise/1e-12,4)).ljust(13) + str(fpga_inst.RAM.samp.power/1e-6).ljust(22))
    
        print_and_write(report_file, "  precharge".ljust(24) + str(round(fpga_inst.area_dict["precharge_total"]/1e6,3)).ljust(13) + 
            str(round(fpga_inst.RAM.precharge.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.precharge.tfall/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.RAM.precharge.trise/1e-12,4)).ljust(13) + str(fpga_inst.RAM.precharge.power/1e-6).ljust(22))

        print_and_write(report_file, "  Write driver".ljust(24) + str(round(fpga_inst.area_dict["writedriver_total"]/1e6,3)).ljust(13) + 
            str(round(fpga_inst.RAM.writedriver.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.writedriver.tfall/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.RAM.writedriver.trise/1e-12,4)).ljust(13) + str(fpga_inst.RAM.writedriver.power/1e-6).ljust(22))
    else:
        print_and_write(report_file, "  Sense Amp".ljust(24) + " ".ljust(13) + str(round(fpga_inst.RAM.mtjsamp.delay/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.RAM.mtjsamp.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.mtjsamp.trise/1e-12,4)).ljust(13) + str(fpga_inst.RAM.mtjsamp.power/1e-6).ljust(22))
    
        print_and_write(report_file, "  BL Charge".ljust(24) + " ".ljust(13) + str(round(fpga_inst.RAM.blcharging.delay/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.RAM.blcharging.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.blcharging.trise/1e-12,4)).ljust(13) + 
            str(fpga_inst.RAM.blcharging.power/1e-6).ljust(22))

        print_and_write(report_file, "  BL Discharge".ljust(24) + " ".ljust(13) + str(round(fpga_inst.RAM.bldischarging.delay/1e-12,4)).ljust(13) + 
            str(round(fpga_inst.RAM.bldischarging.tfall/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.bldischarging.trise/1e-12,4)).ljust(13) + 
            str(fpga_inst.RAM.bldischarging.power/1e-6).ljust(22))
    
    # wordline driver:
    print_and_write(report_file, "  Wordline driver".ljust(24) + str(round(fpga_inst.area_dict["wordline_driver"]/1e6,3)).ljust(13) + 
        str(round(fpga_inst.RAM.wordlinedriver.delay/1e-12,4)).ljust(13) + str(round(fpga_inst.RAM.wordlinedriver.tfall/1e-12,4)).ljust(13) + 
        str(round(fpga_inst.RAM.wordlinedriver.trise/1e-12,4)).ljust(13) + str(fpga_inst.RAM.wordlinedriver.power/1e-6).ljust(22))
    
    # Level shifter: This was measured outside COFFE by kosuke.
    print_and_write(report_file, "  Level Shifter".ljust(24) + str(round(fpga_inst.area_dict["level_shifter"]/1e6,3)).ljust(13) + str(round(32.3,4)).ljust(13) + 
        str(round(32.3,4)).ljust(13) + str(round(32.3,4)).ljust(13) + str(2.26e-7/1e-6).ljust(22))

    print_and_write(report_file, "\n")


def print_power(report_file, fpga_inst):
    """ Print power per subcircuit """
    
    print "  SUBCIRCUIT POWER AT 250MHz (uW)"
    print "  --------------------------"

    print "  " + fpga_inst.sb_mux.name.ljust(22) + str(fpga_inst.sb_mux.power/1e-6) 
    print "  " + fpga_inst.cb_mux.name.ljust(22) + str(fpga_inst.cb_mux.power/1e-6) 
    print "  " + fpga_inst.logic_cluster.local_mux.name.ljust(22) + str(fpga_inst.logic_cluster.local_mux.power/1e-6) 
    print "  " + fpga_inst.logic_cluster.ble.local_output.name.ljust(22) + str(fpga_inst.logic_cluster.ble.local_output.power/1e-6) 
    print "  " + fpga_inst.logic_cluster.ble.general_output.name.ljust(22) + str(fpga_inst.logic_cluster.ble.general_output.power/1e-6) 

    # Figure out LUT power
    lut_input_names = fpga_inst.logic_cluster.ble.lut.input_drivers.keys()
    lut_input_names.sort()
    for input_name in lut_input_names:
        lut_input = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name]
        path_power = lut_input.power
        driver_power = lut_input.driver.power
        not_driver_power = lut_input.not_driver.power
        print "  " + ("lut_" + input_name).ljust(22) + str((path_power + driver_power + not_driver_power)/1e-6)
        print "  " + ("  lut_" + input_name + "_data_path").ljust(22) + str(path_power/1e-6)
        print "  " + ("  lut_" + input_name + "_driver").ljust(22) + str(driver_power/1e-6)
        print "  " + ("  lut_" + input_name + "_driver_not").ljust(22) + str(not_driver_power/1e-6)

    print ""

    
def print_block_area(report_file, fpga_inst):
        """ Print physical area of important blocks (like SB, CB, LUT, etc.) in um^2 """
        
        tile = fpga_inst.area_dict["tile"]/1000000
        lut = fpga_inst.area_dict["lut_total"]/1000000
        ff = fpga_inst.area_dict["ff_total"]/1000000
        ble_output = fpga_inst.area_dict["ble_output_total"]/1000000
        local_mux = fpga_inst.area_dict["local_mux_total"]/1000000
        cb = fpga_inst.area_dict["cb_total"]/1000000
        sb = fpga_inst.area_dict["sb_total"]/1000000
        sanity_check = lut+ff+ble_output+local_mux+cb+sb

        if fpga_inst.specs.enable_bram_block == 1:
            ram = fpga_inst.area_dict["ram"]/1000000
            decod = fpga_inst.area_dict["decoder_total"]/1000000

            ramlocalmux = fpga_inst.area_dict["ram_local_mux_total"]/1000000

            ramcoldecode = fpga_inst.area_dict["columndecoder_sum"]/1000000

            ramconfdecode = (fpga_inst.area_dict["configurabledecoder"] * 2)/1000000

            ramoutputcbar = fpga_inst.area_dict["pgateoutputcrossbar_sram"] /1000000 

            if fpga_inst.RAM.memory_technology == "SRAM":

                prechargetotal = fpga_inst.area_dict["precharge_total"] /1000000 

                writedrivertotal = fpga_inst.area_dict["writedriver_total"] /1000000 

                samptotal = fpga_inst.area_dict["samp_total"] /1000000 
            else:
                cstotal = fpga_inst.area_dict["cs_total"] /1000000 

                writedrivertotal = fpga_inst.area_dict["writedriver_total"] /1000000 

                samptotal = fpga_inst.area_dict["samp_total"] /1000000 

            wordlinedrivera = fpga_inst.area_dict["wordline_total"] /1000000 

            levels = fpga_inst.area_dict["level_shifters"] /1000000 

            RAM_SB_TOTAL = fpga_inst.area_dict["RAM_SB"] / 1000000 
            RAM_CB_TOTAL = fpga_inst.area_dict["RAM_CB"] / 1000000 


            memcells = fpga_inst.area_dict["memorycell_total"] /1000000 
            if fpga_inst.RAM.memory_technology == "SRAM":
                ram_routing = ram - decod - ramlocalmux - ramcoldecode - ramconfdecode - ramoutputcbar - prechargetotal - writedrivertotal - samptotal - memcells - wordlinedrivera - levels
            else:
                ram_routing = ram - decod - ramlocalmux - ramcoldecode - ramconfdecode - ramoutputcbar - memcells - wordlinedrivera - writedrivertotal - samptotal - cstotal - levels

        print_and_write(report_file, "  TILE AREA CONTRIBUTIONS")
        print_and_write(report_file, "  -----------------------")
        print_and_write(report_file, "  Block".ljust(20) + "Total Area (um^2)".ljust(20) + "Fraction of total tile area")
        print_and_write(report_file, "  Tile".ljust(20) + str(round(tile,3)).ljust(20) + "100%")
        print_and_write(report_file, "  LUT".ljust(20) + str(round(lut,3)).ljust(20) + str(round(lut/tile*100,3)) + "%")
        print_and_write(report_file, "  FF".ljust(20) + str(round(ff,3)).ljust(20) + str(round(ff/tile*100,3)) + "%")
        print_and_write(report_file, "  BLE output".ljust(20) + str(round(ble_output,3)).ljust(20) + str(round(ble_output/tile*100,3)) + "%")
        print_and_write(report_file, "  Local mux".ljust(20) + str(round(local_mux,3)).ljust(20) + str(round(local_mux/tile*100,3)) + "%")
        print_and_write(report_file, "  Connection block".ljust(20) + str(round(cb,3)).ljust(20) + str(round(cb/tile*100,3)) + "%")
        print_and_write(report_file, "  Switch block".ljust(20) + str(round(sb,3)).ljust(20) + str(round(sb/tile*100,3)) + "%")
        print_and_write(report_file, "")
        if fpga_inst.specs.enable_bram_block == 1:
            print_and_write(report_file, "  RAM AREA CONTRIBUTIONS")
            print_and_write(report_file, "  Block".ljust(20) + "Total Area (um^2)".ljust(20) + "Fraction of RAM tile area")
            print_and_write(report_file, "  RAM".ljust(20) + str(round(ram,3)).ljust(20) + str(round(ram/ram*100,3)) + "%")
            print_and_write(report_file, "  RAM Local Mux".ljust(20) + str(round(ramlocalmux,3)).ljust(20) + str(round(ramlocalmux/ram*100,3)) + "%")
            print_and_write(report_file, "  Level Shifters".ljust(20) + str(round(levels,3)).ljust(20) + str(round(levels/ram*100,3)) + "%")
            print_and_write(report_file, "  Decoder".ljust(20) + str(round(decod,3)).ljust(20) + str(round(decod/ram*100,3)) + "%")
            print_and_write(report_file, "  WL driver".ljust(20) + str(round(wordlinedrivera,3)).ljust(20) + str(round(wordlinedrivera/ram*100,3)) + "%"            )
            print_and_write(report_file, "  Column Decoder".ljust(20) + str(round(ramcoldecode,3)).ljust(20) + str(round(ramcoldecode/ram*100,3)) + "%")
            print_and_write(report_file, "  Configurable Dec".ljust(20) + str(round(ramconfdecode,3)).ljust(20) + str(round(ramconfdecode/ram*100,3)) + "%")
            print_and_write(report_file, "  Output CrossBar".ljust(20) + str(round(ramoutputcbar,3)).ljust(20) + str(round(ramoutputcbar/ram*100,3)) + "%")
            if fpga_inst.RAM.memory_technology == "SRAM":
                print_and_write(report_file, "  Precharge Total".ljust(20) + str(round(prechargetotal,3)).ljust(20) + str(round(prechargetotal/ram*100,3)) + "%")
                print_and_write(report_file, "  Write Drivers".ljust(20) + str(round(writedrivertotal,3)).ljust(20) + str(round(writedrivertotal/ram*100,3)) + "%")
                print_and_write(report_file, "  Sense Amp Total ".ljust(20) + str(round(samptotal,3)).ljust(20) + str(round(samptotal/ram*100,3)) + "%")
            else:
                print_and_write(report_file, "  Column selectors".ljust(20) + str(round(cstotal,3)).ljust(20) + str(round(cstotal/ram*100,3)) + "%")
                print_and_write(report_file, "  Write Drivers".ljust(20) + str(round(writedrivertotal,3)).ljust(20) + str(round(writedrivertotal/ram*100,3)) + "%")
                print_and_write(report_file, "  Sense Amp Total ".ljust(20) + str(round(samptotal,3)).ljust(20) + str(round(samptotal/ram*100,3)) + "%")

            print_and_write(report_file, "  Memory Cells ".ljust(20) + str(round(memcells,3)).ljust(20) + str(round(memcells/ram*100,3)) + "%")
            print_and_write(report_file, "  RAM Routing".ljust(20) + str(round(ram_routing,3)).ljust(20) + str(round(ram_routing/ram*100,3)) + "%")
            print_and_write(report_file, "  RAM CB".ljust(20) + str(round(RAM_CB_TOTAL,3)).ljust(20) + str(round(RAM_CB_TOTAL/ram*100,3)) + "%")
            print_and_write(report_file, "  RAM SB".ljust(20) + str(round(RAM_SB_TOTAL,3)).ljust(20) + str(round(RAM_SB_TOTAL/ram*100,3)) + "%")
     

def print_vpr_delays(report_file, fpga_inst):

    print_and_write(report_file, "  VPR DELAYS")
    print_and_write(report_file, "  ----------")
    print_and_write(report_file, "  Path".ljust(50) + "Delay (ps)")
    print_and_write(report_file, "  Tdel (routing switch)".ljust(50) + str(fpga_inst.sb_mux.delay))
    print_and_write(report_file, "  T_ipin_cblock (connection block mux)".ljust(50) + str(fpga_inst.cb_mux.delay))
    print_and_write(report_file, "  CLB input -> BLE input (local CLB routing)".ljust(50) + str(fpga_inst.logic_cluster.local_mux.delay))
    print_and_write(report_file, "  LUT output -> BLE input (local feedback)".ljust(50) + str(fpga_inst.logic_cluster.ble.local_output.delay))
    print_and_write(report_file, "  LUT output -> CLB output (logic block output)".ljust(50) + str(fpga_inst.logic_cluster.ble.general_output.delay))
    
    # Figure out LUT delays
    lut_input_names = fpga_inst.logic_cluster.ble.lut.input_drivers.keys()
    lut_input_names.sort()
    for input_name in lut_input_names:
        lut_input = fpga_inst.logic_cluster.ble.lut.input_drivers[input_name]
        driver_delay = max(lut_input.driver.delay, lut_input.not_driver.delay)
        path_delay = lut_input.delay
        print_and_write(report_file, ("  lut_" + input_name).ljust(50) + str(driver_delay+path_delay))
    
    print_and_write(report_file, "")
 

def print_vpr_areas(report_file, fpga_inst):

    print_and_write(report_file, "  VPR AREAS")
    print_and_write(report_file, "  ----------")
    print_and_write(report_file, "  grid_logic_tile_area".ljust(50) + str(fpga_inst.area_dict["logic_cluster"]/fpga_inst.specs.min_width_tran_area))
    print_and_write(report_file, "  ipin_mux_trans_size (connection block mux)".ljust(50) + str(fpga_inst.area_dict["ipin_mux_trans_size"]/fpga_inst.specs.min_width_tran_area))
    print_and_write(report_file, "  mux_trans_size (routing switch)".ljust(50) + str(fpga_inst.area_dict["switch_mux_trans_size"]/fpga_inst.specs.min_width_tran_area))
    print_and_write(report_file, "  buf_size (routing switch)".ljust(50) + str(fpga_inst.area_dict["switch_buf_size"]/fpga_inst.specs.min_width_tran_area))
    print_and_write(report_file, "")

    
def load_arch_params(filename):
    """ Parse the architecture description file and load values into dictionary. 
        Returns this dictionary.
        Will print error message and terminate program if an invalid parameter is found
        or if a parameter is missing.
        """
    
    # This is the dictionary of parameters we expect to find
    arch_params = {
        'W': -1,
        'L': -1,
        'Fs': -1,
        'N': -1,
        'K': -1,
        'I': -1,
        'Fcin': -1.0,
        'Fcout': -1.0,
        'Or': -1,
        'Ofb': -1,
        'Fclocal': -1.0,
        'Rsel': "",
        'Rfb': "",
        'transistor_type': "",
        'switch_type': "",
        'use_tgate': False,
        'use_finfet': False,
        'memory_technology': "SRAM",
        'enable_bram_module': 0,
        'ram_local_mux_size': 25,
        'read_to_write_ratio': 1.0,
        'vdd': -1,
        'vsram': -1,
        'vsram_n': -1,
        'vclmp': 0.653,
        'vref': 0.627,
        'vdd_low_power': 0.95,
        'number_of_banks': 1,
        'gate_length': -1,
        'rest_length_factor': -1,
        'min_tran_width': -1,
        'min_width_tran_area': -1,
        'sram_cell_area': -1,
        'trans_diffusion_length' : -1,
        'model_path': "",
        'model_library': "",
        'metal' : [],
        'row_decoder_bits': 8,
        'col_decoder_bits': 1,
        'conf_decoder_bits' : 5,
        'sense_dv': 0.3,
        'worst_read_current': 1e-6,
        'SRAM_nominal_current': 1.29e-5,
        'MTJ_Rlow_nominal': 2500,
        'MTJ_Rhigh_nominal': 6250,
        'MTJ_Rlow_worstcase': 3060,
        'MTJ_Rhigh_worstcase': 4840,
        'use_fluts': False,
        'independent_inputs': 0,
        'enable_carry_chain': 0,
        'carry_chain_type': "ripple",
        'FAs_per_flut':2,
        'hb_files' : []
    }

    params_file = open(filename, 'r')
    for line in params_file:
    
        # Ignore comment lines
        if line.startswith('#'):
            continue
        
        # Remove line feeds and spaces
        line = line.replace('\n', '')
        line = line.replace('\r', '')
        line = line.replace('\t', '')
        line = line.replace(' ', '')
        
        # Ignore empty lines
        if line == "":
            continue
        
        # Split lines at '='
        words = line.split('=')
        if words[0] not in arch_params.keys():
            print "ERROR: Found invalid architecture parameter (" + words[0] + ") in " + filename
            sys.exit()
         
        param = words[0]
        value = words[1]

        #architecture parameters 
        if param == 'W':
            arch_params['W'] = int(value)
        elif param == 'L':
            arch_params['L'] = int(value)
        elif param == 'Fs':
            arch_params['Fs'] = int(value)
        elif param == 'N':
            arch_params['N'] = int(value)
        elif param == 'K':
            arch_params['K'] = int(value)
        elif param == 'I':
            arch_params['I'] = int(value)
        elif param == 'Fcin':
            arch_params['Fcin'] = float(value)
        elif param == 'Fcout':
            arch_params['Fcout'] = float(value) 
        elif param == 'Or':
            arch_params['Or'] = int(value)
        elif param == 'Ofb':
            arch_params['Ofb'] = int(value)
        elif param == 'Fclocal':
            arch_params['Fclocal'] = float(value)
        elif param == 'Rsel':
            arch_params['Rsel'] = value
        elif param == 'Rfb':
            arch_params['Rfb'] = value
        elif param == 'row_decoder_bits':
            arch_params['row_decoder_bits'] = int(value)
        elif param == 'col_decoder_bits':
            arch_params['col_decoder_bits'] = int(value)
        elif param == 'number_of_banks':
            arch_params['number_of_banks'] = int(value)
        elif param == 'conf_decoder_bits':
            arch_params['conf_decoder_bits'] = int(value) 
        #process technology parameters
        elif param == 'transistor_type':
            arch_params['transistor_type'] = value
            if value == 'finfet':
                arch_params['use_finfet'] = True
        elif param == 'switch_type':  
            arch_params['switch_type'] = value        
            if value == 'transmission_gate':
                arch_params['use_tgate'] = True
        elif param == 'memory_technology':
            arch_params['memory_technology'] = value
        elif param == 'vdd':
            arch_params['vdd'] = float(value)
        elif param == 'vsram':
            arch_params['vsram'] = float(value)
        elif param == 'vsram_n':
            arch_params['vsram_n'] = float(value)
        elif param == 'gate_length':
            arch_params['gate_length'] = int(value)
        elif param == 'sense_dv':
            arch_params['sense_dv'] = float(value)
        elif param == 'vdd_low_power':
            arch_params['vdd_low_power'] = float(value)
        elif param == 'vclmp':
            arch_params['vclmp'] = float(value)
        elif param == 'read_to_write_ratio':
            arch_params['read_to_write_ratio'] = float(value)
        elif param == 'enable_bram_module':
            arch_params['enable_bram_module'] = int(value)
        elif param == 'ram_local_mux_size':
            arch_params['ram_local_mux_size'] = int(value)
        elif param == 'use_fluts':
            arch_params['use_fluts'] = (value == 'True')
        elif param == 'independent_inputs':
            arch_params['independent_inputs'] = int(value)
        elif param == 'enable_carry_chain':
            arch_params['enable_carry_chain'] = int(value)
        elif param == 'carry_chain_type':
            arch_params['carry_chain_type'] = value
        elif param == 'FAs_per_flut':
            arch_params['FAs_per_flut'] = int(value)
        elif param == 'vref':
            arch_params['ref'] = float(value)
        elif param == 'worst_read_current':
            arch_params['worst_read_current'] = float(value)
        elif param == 'SRAM_nominal_current':
            arch_params['SRAM_nominal_current'] = float(value)
        elif param == 'MTJ_Rlow_nominal':
            arch_params['MTJ_Rlow_nominal'] = float(value)
        elif param == 'MTJ_Rhigh_nominal':
            arch_params['MTJ_Rhigh_nominal'] = float(value)
        elif param == 'MTJ_Rlow_worstcase':
            arch_params['MTJ_Rlow_worstcase'] = float(value)
        elif param == 'MTJ_Rhigh_worstcase':
            arch_params['MTJ_Rhigh_worstcase'] = float(value)          
        elif param == 'rest_length_factor':
            arch_params['rest_length_factor'] = int(value)
        elif param == 'min_tran_width':
            arch_params['min_tran_width'] = int(value)
        elif param == 'min_width_tran_area':
            arch_params['min_width_tran_area'] = int(value)
        elif param == 'sram_cell_area':
            arch_params['sram_cell_area'] = float(value)
        elif param == 'trans_diffusion_length':
            arch_params['trans_diffusion_length'] = float(value)
        elif param == 'model_path':
            arch_params['model_path'] = os.path.abspath(value)
        elif param == 'model_library':
            arch_params['model_library'] = value
        elif param == 'metal':
            value_words = value.split(',')
            r = value_words[0].replace(' ', '')
            r = r.replace(' ', '')
            r = r.replace('\n', '')
            r = r.replace('\r', '')
            r = r.replace('\t', '')
            c = value_words[1].replace(' ', '')
            c = c.replace(' ', '')
            c = c.replace('\n', '')
            c = c.replace('\r', '')
            c = c.replace('\t', '')
            arch_params['metal'].append((float(r),float(c)))
        elif param == 'hb_files':
            arch_params['hb_files'].append(value)

    params_file.close()
    
    # Check that we read everything
    for param, value in arch_params.iteritems():
        if value == -1 or value == "":
            print "ERROR: Did not find architecture parameter " + param + " in " + filename
            sys.exit()
    
    # Check architecture parameters to make sure that they are valid
    check_arch_params(arch_params, filename)

    return arch_params 




def load_hard_params(filename):
    """ Parse the hard block description file and load values into dictionary. 
        Returns this dictionary.
    """
    
    # This is the dictionary of parameters we expect to find
    hard_params = {
        'name': "",
        'num_gen_inputs': -1,
        'crossbar_population': -1.0,
        'height': -1,
        'num_gen_outputs': -1,
        'num_crossbars': -1,
        'crossbar_modelling': "",
        'num_dedicated_outputs': -1,
        'soft_logic_per_block': -1.0,
        'area_scale_factor': -1.0,
        'freq_scale_factor': -1.0,
        'power_scale_factor': -1.0,
        'input_usage': -1.0,
        # Flow Settings:
        'design_folder': "",
        'design_language': '',
        'clock_pin_name': "",
        'clock_period': [],
        'top_level': "",
        'synth_folder': "",
        'show_warnings': False,
        'synthesis_only': False,
        'read_saif_file': False,
        'static_probability': -1.0,
        'toggle_rate': -1,
        'link_libraries': '',
        'target_libraries': '',
        'lef_files': '',
        'best_case_libs': '',
        'standard_libs': '',
        'worst_case_libs': '',
        'power_ring_width': -1,
        'power_ring_spacing': -1,
        'height_to_width_ratio': -1.0,
        'core_utilization': [],
        'space_around_core': -1,
        'pr_folder': "",
        'primetime_lib_path': '',
        'primetime_folder': "" ,
        'delay_cost_exp': 1.0,
        'area_cost_exp': 1.0,
        'wire_selection': [],
        'metal_layers': [],
        'mode_signal': []

    }



    hard_file = open(filename, 'r')
    for line in hard_file:
    
        # Ignore comment lines
        if line.startswith('#'):
            continue
        
        # Remove line feeds and spaces
        line = line.replace('\n', '')
        line = line.replace('\r', '')
        line = line.replace('\t', '')
        
        # Ignore empty lines
        if line == "":
            continue
        
        # Split lines at '='
        words = line.split('=')
        if words[0] not in hard_params.keys():
            print "ERROR: Found invalid hard block parameter (" + words[0] + ") in " + filename
            sys.exit()
         
        param = words[0]
        value = words[1]

        #architecture parameters 
        if param == 'name':
            hard_params['name'] = value
        elif param == 'num_gen_inputs':
            hard_params['num_gen_inputs'] = int(value)
        elif param == 'crossbar_population':
            hard_params['crossbar_population'] = float(value)
        elif param == 'height':
            hard_params['height'] = int(value)
        elif param == 'num_gen_outputs':
            hard_params['num_gen_outputs'] = int(value)
        elif param == 'num_dedicated_outputs':
            hard_params['num_dedicated_outputs'] = int(value)
        elif param == 'soft_logic_per_block':
            hard_params['soft_logic_per_block'] = float(value)
        elif param == 'area_scale_factor':
            hard_params['area_scale_factor'] = float(value)
        elif param == 'freq_scale_factor':
            hard_params['freq_scale_factor'] = float(value)
        elif param == 'power_scale_factor':
            hard_params['power_scale_factor'] = float(value)  
        elif param == 'input_usage':
            hard_params['input_usage'] = float(value)  
        elif param == 'delay_cost_exp':
            hard_params['delay_cost_exp'] = float(value)  
        elif param == 'area_cost_exp':
            hard_params['area_cost_exp'] = float(value)              
            #flow parameters:
        elif param == 'design_folder':
            hard_params['design_folder'] = value
        elif param == 'design_language':
            hard_params['design_language'] = value
        elif param == 'clock_pin_name':
            hard_params['clock_pin_name'] = value
        elif param == 'clock_period':
            hard_params['clock_period'].append(value)
        elif param == 'wire_selection':
            hard_params['wire_selection'].append(value)
        elif param == 'core_utilization':
            hard_params['core_utilization'].append(value)
        elif param == 'metal_layers':
            hard_params['metal_layers'].append(value)
        elif param == 'crossbar_modelling':
            hard_params['crossbar_modelling'] = value
        elif param == 'num_crossbars':
            hard_params['num_crossbars'] = int(value)
        elif param == 'top_level':
            hard_params['top_level'] = value
        elif param == 'synth_folder':
            hard_params['synth_folder'] = value
        elif param == 'show_warnings':
            hard_params['show_warnings'] = (value == "True")
        elif param == 'synthesis_only':
            hard_params['synthesis_only'] = (value == "True")
        elif param == 'read_saif_file':
            hard_params['read_saif_file'] = (value == "True")
        elif param == 'static_probability':
            hard_params['static_probability'] = value
        elif param == 'toggle_rate':
            hard_params['toggle_rate'] = value
        elif param == 'link_libraries':
            hard_params['link_libraries'] = value
        elif param == 'target_libraries':
            hard_params['target_libraries'] = value
        elif param == 'lef_files':
            hard_params['lef_files'] = value
        elif param == 'best_case_libs':
            hard_params['best_case_libs'] = value
        elif param == 'standard_libs':
            hard_params['standard_libs'] = value
        elif param == 'worst_case_libs':
            hard_params['worst_case_libs'] = value
        elif param == 'power_ring_width':
            hard_params['power_ring_width'] = value
        elif param == 'power_ring_spacing':
            hard_params['power_ring_spacing'] = value
        elif param == 'height_to_width_ratio':
            hard_params['height_to_width_ratio'] = value
        elif param == 'space_around_core':
            hard_params['space_around_core'] = value
        elif param == 'pr_folder':
            hard_params['pr_folder'] = value
        elif param == 'primetime_lib_path':
            hard_params['primetime_lib_path'] = value
        elif param == 'primetime_folder':
            hard_params['primetime_folder'] = value

    hard_file.close()
    
    
    return hard_params


def check_arch_params (arch_params, filename):
    """
    This function checks the architecture parameters to make sure that all the parameters specified 
    are compatible with COFFE. Right now, this functions just checks really basic stuff like 
    checking for negative values where there shoulnd't be or making sure the LUT size is supported
    etc. But in the future I think it might be a good idea to make this checker a little more 
    intelligent. For example, we might check things like Fc values that make no sense. Such as an
    Fc that is so small that you can't connect to wires, or something like that.
    """

    # TODO: Make these error messages more descriptive of that the problem is.

    if arch_params['W'] <= 0:
        print_error (str(arch_params['W']), "W", filename)
    if arch_params['L'] <= 0:
        print_error (str(arch_params['L']), "L", filename)
    if arch_params['Fs'] <= 0:
        print_error (str(arch_params['Fs']), "Fs", filename)
    if arch_params['N'] <= 0:
        print_error (str(arch_params['N']), "N", filename)
    # We only support 4-LUT, 5-LUT or 6-LUT
    if arch_params['K'] < 4 or  arch_params['K'] > 6:
        print_error (str(arch_params['K']), "K", filename)
    if arch_params['I'] <= 0:
        print_error (str(arch_params['I']), "I", filename)
    if arch_params['Fcin'] <= 0.0 or arch_params['Fcin'] > 1.0:
        print_error (str(arch_params['Fcin']), "Fcin", filename)
    if arch_params['Fcout'] <= 0.0 or arch_params['Fcout'] > 1.0 :
        print_error (str(arch_params['Fcout']), "Fcout", filename)
    if arch_params['Or'] <= 0:
        print_error (str(arch_params['Or']), "Or", filename)
    # We currently only support architectures that have local feedback routing. 
    # It might be a good idea to change COFFE such that you can specify an
    # architecture with no local feedback routing.
    if arch_params['Ofb'] <= 0:
        print_error (str(arch_params['Ofb']), "Ofb", filename)
    if arch_params['Fclocal'] <= 0.0 or arch_params['Fclocal'] > 1.0:
        print_error (str(arch_params['Fclocal']), "Fclocal", filename)
    # Rsel can 'a' the last LUT input. For example for a 6-LUT Rsel can be 'a' to 'f' or 'z' which means no Rsel.
    if arch_params['Rsel'] != 'z' and (arch_params['Rsel'] < 'a' or arch_params['Rsel'] > chr(arch_params['K']+96)):
        print_error (arch_params['Rsel'], "Fclocal", filename)
    # Rfb can be 'z' which means to Rfb. If not 'z', Rfb is a string of the letters of all the LUT inputs that are Rfb.
    if arch_params['Rfb'] == 'z':
        pass    
    elif len(arch_params['Rfb']) > arch_params['K']:
        print_error (arch_params['Rfb'], "Rfb", filename, "(you specified more Rfb LUT inputs than there are LUT inputs)")
    else:
        # Now, let's make sure all these characters are valid characters
        for character in arch_params['Rfb']:
            # The character has to be a valid LUT input
            if (character < 'a' or character > chr(arch_params['K']+96)):
                print_error (arch_params['Rfb'], "Rfb", filename, " (" + character + " is not a valid LUT input)")
            # The character should not appear twice
            elif arch_params['Rfb'].count(character) > 1:
                print_error (arch_params['Rfb'], "Rfb", filename, " (" + character + " appears more than once)")
    # only one or two FAs are allowed per ble
    if arch_params['FAs_per_flut'] > 2:
        print_error (str(arch_params['FAs_per_flut']), "FAs_per_flut", filename, "(number of FA per ble should be 2 or less)")
    # Currently, I only generate the circuit assuming we have a fracturable lut. It can easily be changed to support nonfracturable luts as well.
    if arch_params['enable_carry_chain'] == 1 and arch_params['use_fluts'] == False:
        print_error_not_compatable("carry chains", "non fracturable lut")           


    # Check process technology parameters
    if arch_params['transistor_type'] != 'bulk' and arch_params['transistor_type'] != 'finfet':
        print_error (arch_params['transistor_type'], "transistor_type", filename)
    if arch_params['switch_type'] != 'pass_transistor' and arch_params['switch_type'] != 'transmission_gate':
        print_error (arch_params['switch_type'], "switch_type", filename)
    if arch_params['vdd'] <= 0 :
        print_error (str(arch_params['vdd']), "vdd", filename)                     
    if arch_params['gate_length'] <= 0 :
        print_error (str(arch_params['gate_length']), "gate_length", filename)            
    if arch_params['rest_length_factor'] <= 0 :
        print_error (str(arch_params['rest_length_factor']), "rest_length_factor", filename) 
    if arch_params['min_tran_width'] <= 0 :
        print_error (str(arch_params['min_tran_width']), "min_tran_width", filename)            
    if arch_params['min_width_tran_area'] <= 0 :
        print_error (str(arch_params['min_width_tran_area']), "min_width_tran_area", filename)            
    if arch_params['sram_cell_area'] <= 0 :
        print_error (str(arch_params['sram_cell_area']), "sram_cell_area", filename)
    if arch_params['trans_diffusion_length'] <= 0 :
        print_error (str(arch_params['trans_diffusion_length']), "trans_diffusion_length", filename)  
    if arch_params['enable_bram_module'] == 1 and arch_params['use_finfet'] == True:
        print_error_not_compatable("finfet", "BRAM")           
    if arch_params['use_finfet'] == True and arch_params['use_fluts'] == True:
        print_error_not_compatable("finfet", "flut")           



def print_error(value, argument, filename, msg = ""):
    print "ERROR: Invalid value (" + value + ") for " + argument + " in " + filename + " " + msg
    sys.exit()


def print_error_not_compatable(value1, value2):
    print "ERROR: " + value1 + " and " + value2 + " simulations are not compatible.\n"
    sys.exit()    


def print_run_options(args, report_file_path):
    """ 
    This function prints the run options entered by the user
    when running COFFE, in the terminal and the report file  
    """

    report_file = open(report_file_path, 'w')
    report_file.write("Created " + str(datetime.datetime.now()) + "\n\n")
    
    print_and_write(report_file, "----------------------------------------------")
    print_and_write(report_file, "  RUN OPTIONS:")
    print_and_write(report_file, "----------------------------------------------" + "\n")
    if not args.no_sizing:
        print_and_write(report_file, "  Transistor sizing: on")
    else:
        print_and_write(report_file, "  Transistor sizing: off")
    
    if args.opt_type == "global":
        print_and_write(report_file, "  Optimization type: global")
    else:
        print_and_write(report_file, "  Optimization type: local")
    
    
    print_and_write(report_file, "  Number of top combos to re-ERF: " + str(args.re_erf))
    print_and_write(report_file, "  Area optimization weight: " + str(args.area_opt_weight))
    print_and_write(report_file, "  Delay optimization weight: " + str(args.delay_opt_weight))
    print_and_write(report_file, "  Maximum number of sizing iterations: " + str(args.max_iterations))
    print_and_write(report_file, "")
    print_and_write(report_file, "")

    report_file.close()



def print_architecture_params(arch_params_dict, report_file_path):

    report_file = open(report_file_path, 'a')

    print_and_write(report_file, "-------------------------------------------------")
    print_and_write(report_file, "  ARCHITECTURE PARAMETERS:")
    print_and_write(report_file, "-------------------------------------------------" + "\n")


    print_and_write(report_file, "  Number of BLEs per cluster (N): " + str(arch_params_dict['N']))
    print_and_write(report_file, "  LUT size (K): " + str(arch_params_dict['K']))

    if arch_params_dict['use_fluts'] == True:
        print_and_write(report_file, "  LUT fracturability level: 1")
        print_and_write(report_file, "  Number of adder bits per ALM: " + str(arch_params_dict['FAs_per_flut']))

    print_and_write(report_file, "  Channel width (W): " + str(arch_params_dict['W']))
    print_and_write(report_file, "  Wire segment length (L): " + str(arch_params_dict['L']))
    print_and_write(report_file, "  Number of cluster inputs (I): " + str(arch_params_dict['I']))
    print_and_write(report_file, "  Number of BLE outputs to general routing (Or): " + str(arch_params_dict['Or']))
    print_and_write(report_file, "  Number of BLE outputs to local routing (Ofb): " + str(arch_params_dict['Ofb']))
    print_and_write(report_file, "  Total number of cluster outputs (N*Or): " + str(arch_params_dict['N']*arch_params_dict['Or']))
    print_and_write(report_file, "  Switch block flexibility (Fs): " + str(arch_params_dict['Fs']))
    print_and_write(report_file, "  Cluster input flexibility (Fcin): " + str(arch_params_dict['Fcin']))
    print_and_write(report_file, "  Cluster output flexibility (Fcout): " + str(arch_params_dict['Fcout']))
    print_and_write(report_file, "  Local MUX population (Fclocal): " + str(arch_params_dict['Fclocal']))
    print_and_write(report_file, "  LUT input for register selection MUX (Rsel): " + str(arch_params_dict['Rsel']))
    print_and_write(report_file, "  LUT input(s) for register feedback MUX(es) (Rfb): " + str(arch_params_dict['Rfb']))
    print_and_write(report_file, "")
    
    print_and_write(report_file, "-------------------------------------------------")
    print_and_write(report_file, "  PROCESS TECHNOLOGY PARAMETERS:")
    print_and_write(report_file, "-------------------------------------------------" + "\n")

    print_and_write(report_file, "  transistor_type = " + arch_params_dict['transistor_type'])
    print_and_write(report_file, "  switch_type = " + arch_params_dict['switch_type'])
    print_and_write(report_file, "  vdd = " + str( arch_params_dict['vdd']))
    print_and_write(report_file, "  vsram = " + str( arch_params_dict['vsram']) )
    print_and_write(report_file, "  vsram_n = " + str( arch_params_dict['vsram_n']) )
    print_and_write(report_file, "  gate_length = " + str( arch_params_dict['gate_length']))
    print_and_write(report_file, "  min_tran_width = " + str( arch_params_dict['min_tran_width']) )
    print_and_write(report_file, "  min_width_tran_area = " + str( arch_params_dict['min_width_tran_area']) )
    print_and_write(report_file, "  sram_cell_area = " + str( arch_params_dict['sram_cell_area']) )
    print_and_write(report_file, "  model_path = " + str( arch_params_dict['model_path']) )
    print_and_write(report_file, "  model_library = " + str( arch_params_dict['model_library']) )
    print_and_write(report_file, "  metal = " + str( arch_params_dict['metal']) )
    print_and_write(report_file, "")
    print_and_write(report_file, "")

    report_file.close()


def extract_initial_tran_size(filename, use_tgate):
    """ Parse the initial sizes file and load values into dictionary. 
        Returns this dictionary.
        """
    
    transistor_sizes = {}

    sizes_file = open(filename, 'r')
    for line in sizes_file:
    
        # Ignore comment lines
        if line.startswith('#'):
            continue
        
        # Remove line feeds and spaces
        line = line.replace('\n', '')
        line = line.replace('\r', '')
        line = line.replace('\t', '')
        line = line.replace(' ', '')
        
        # Ignore empty lines
        if line == "":
            continue
        
        # Split lines at '='
        words = line.split('=')
        trans = words[0]
        size = words[1]

        transistor_sizes[trans] = float(size)

    sizes_file.close()

    return  transistor_sizes


def use_initial_tran_size(initial_sizes, fpga_inst, tran_sizing, use_tgate):

    print "Extracting initial transistor sizes from: " + initial_sizes
    initial_tran_size = extract_initial_tran_size(initial_sizes, use_tgate)
    print "Setting transistor sizes to extracted values"
    tran_sizing.override_transistor_sizes(fpga_inst, initial_tran_size)
    for tran in initial_tran_size :
        fpga_inst.transistor_sizes[tran] = initial_tran_size[tran]
    print "Re-calculating area..."
    fpga_inst.update_area()
    print "Re-calculating wire lengths..."
    fpga_inst.update_wires()
    print "Re-calculating resistance and capacitance..."
    fpga_inst.update_wire_rc()
    print ""


def check_for_time():
    """ This finction should be used before each call for HSPICE it checks
        if the time is between 2:30 a.m and 3:30 a.m. since during this time
        it was found that the license doesn't work on my machine. So, to avoid
        program termination this function was written. If you're using COFFE on 
        a machine that doesn't have this problem you can comment this function 
        in the code """
    now = datetime.datetime.now()
    if (now.hour == 2 or now.hour == 3):
        print "-----------------------------------------------------------------"
        print "      Entered the check for time function @ " + str(now.hour) +":" + str(now.minute) + ":" + str(now.second)
        print "-----------------------------------------------------------------"
        print ""
       
    while (now.hour == 2 and now.minute >= 30) or (now.hour == 3 and now.minute < 30):
    #while (now.minute >= 20) and (now.minute < 25):
        print("\tI'm sleeping")
        time.sleep(60)
        now = datetime.datetime.now()
        if not ((now.hour == 2 and now.minute >= 30) or (now.hour == 3 and now.minute < 30)):
            print("\tExecution is resumed")

    now = datetime.datetime.now()
    if (now.hour == 2 or now.hour == 3):        
        print "-----------------------------------------------------------------"
        print "      Exited the check for time function  @ " + str(now.hour) +":" + str(now.minute) + ":" + str(now.second)
        print "-----------------------------------------------------------------"
        print ""         

def print_and_write(file, string):
    """
    This function takes a file name and a string, it prints the string to the 
    terminal and writes it to the file. Since this sequence is repeated a lot
    in the code this function is added to remove some redundent code. 
    Note: the file should be open for writing before calling this function
    """
    #TODO: check if the file is already open or not
    print(string)
    file.write(string + "\n")


def create_output_dir(arch_file_name):
    """
    This function created the architecture folder and returns its name
    it also deletes the content of the folder in case it's already created
    to avoid any errors in case of multiple runs on the same architecture file
    """

    arch_desc_words = arch_file_name.split('.')
    arch_folder = arch_desc_words[0]
    if not os.path.exists(arch_folder):
        os.mkdir(arch_folder)
    else:
        # Delete contents of sub-directories
        # COFFE generates several 'intermediate results' files during sizing
        # so we delete them to avoid from having them pile up if we run COFFE
        # more than once.
        dir_contents = os.listdir(arch_folder)
        for content in dir_contents:
            if os.path.isdir(arch_folder + "/" + content):
                shutil.rmtree(arch_folder + "/" + content)

    return arch_folder  


def print_summary(arch_folder, fpga_inst, start_time):

    report_file = open(arch_folder + "/report.txt", 'a')
    report_file.write("\n")
    
    print_and_write(report_file, "|--------------------------------------------------------------------------------------------------|")
    print_and_write(report_file, "|    Area and Delay Report                                                                         |")
    print_and_write(report_file, "|--------------------------------------------------------------------------------------------------|")
    print_and_write(report_file, "")
    
    # Print area and delay per subcircuit
    print_area_and_delay(report_file, fpga_inst)
    
    # Print block areas
    print_block_area(report_file, fpga_inst)
    
    # Print VPR delays (to be used to make architecture file)
    print_vpr_delays(report_file, fpga_inst)
    
    # Print VPR areas (to be used to make architecture file)
    print_vpr_areas(report_file, fpga_inst)
          
    # Print area and delay summary
    final_cost = fpga_inst.area_dict["tile"]*fpga_inst.delay_dict["rep_crit_path"]
    
    print_and_write(report_file, "  SUMMARY")
    print_and_write(report_file, "  -------")
    print_and_write(report_file, "  Tile Area                            " + str(round(fpga_inst.area_dict["tile"]/1e6,2)) + " um^2")
    print_and_write(report_file, "  Representative Critical Path Delay   " + str(round(fpga_inst.delay_dict["rep_crit_path"]*1e12,2)) + " ps")
    print_and_write(report_file, "  Cost (area^" + str(fpga_inst.area_opt_weight) + " x delay^" + str(fpga_inst.delay_opt_weight) + ")              " 
           + str(round(final_cost,5)))
    
    print_and_write(report_file, "")
    print_and_write(report_file, "|--------------------------------------------------------------------------------------------------|")
    print_and_write(report_file, "")
    
    # Record end time
    total_end_time = time.time()
    total_time_elapsed = total_end_time - start_time
    total_hours_elapsed = int(total_time_elapsed/3600)
    total_minutes_elapsed = int((total_time_elapsed - 3600*total_hours_elapsed)/60)
    total_seconds_elapsed = int(total_time_elapsed - 3600*total_hours_elapsed - 60*total_minutes_elapsed)
    
    print_and_write(report_file, "Number of HSPICE simulations performed: " + str(fpga_inst.spice_interface.get_num_simulations_performed()))
    print_and_write(report_file, "Total time elapsed: " + str(total_hours_elapsed) + " hours " + str(total_minutes_elapsed) + " minutes " + str(total_seconds_elapsed) + " seconds\n") 
    
    report_file.write("\n")
    report_file.close() 



def wire_name(from_node, to_node):
    """ created a wire name coming from from_node to to_node """
    return "wire_" + from_node + "_to_" + to_node

def create_wire(node_1, node_2, from_node, to_node):
    """ Creates the line of adding a wire to the netlist """
    name = wire_name(from_node, to_node)
    return "X"+name+" "+node_1+" "+node_2+" wire Rw="+name+"_res Cw="+name+"_cap\n"