# COFFE User Guide


## Details of Features
The current release of COFFE supports a wide variety of features which gradually introduced in the following papers. If you are interested in more details on a particular feature, you might want to read its corresponding paper.

* Yazdanshenas, S. and Betz, V. "Automatic circuit design and modelling for heterogeneous FPGAs." International Conference on Field-Programmable Technology (FPT), 2017.
  * Fracturacture logic tiles
  * Logic tiles with hard arithmetic (carry chains)
  * Arbitrary hybrid (standard cell + full custom) blocks

* Yazdanshenas, S, Tatsumura, K., and Betz, V. Yazdanshenas, Sadegh, Kosuke Tatsumura, and Vaughn Betz. "Don't Forget the Memory: Automatic Block RAM Modelling, Optimization, and Architecture Exploration." ACM/SIGDA International Symposium on Field-Programmable Gate Arrays (FPGA), 2017. 
  * SRAM-based and MTJ-based on-chip memories

* Chiasson, C. and Betz, V. "COFFE: Fully-automated Transistor Sizing for FPGAs." International Conference on Field-Programmable Technology (FPT),
  * Logic tiles with fixed-size LUTs
  
## Setting up

To run coffe with most of its (except hybrid blocks) features, you need Hspice. We have tested COFFE with two versions of Hspice: Hspice 2013.03 and 2011.01-SP1. But we expect other versions to also be able to work.
To support arbitrary hybrid block modelling, you will also need a working version of Synopsys Design Compiler and Cadence Encounter Digital Implementation (EDI). We have tested COFFE using Synopsys Design Compiler 2013.03-SP5-2 and Cadence EDI 9.12.
We expect newer versions of Synopsys Design Compiler to still work with our flow, but newer versions of Cadence EDI will require changing the scripts.
To obtain the switching activity of hybrid blocks for more accurate power estimation, you will also need Mentor modelsim. We tested this feature using Mentor Modelsim 10 and we expect other version to continue to work with COFFE.

  
## How to Run

To run COFFE, simply run coffe.py and follow the instructions.
There are several sample input files in the test directory accompanying COFFE which stimulate all existing features. These files describe what each of the parameters are; simply read them and change them to form your desired architecture.
We have also included several tests with COFFE which should smoothly run when using the latest version. To test your setup, you can run those.

# How to run a test for ASIC flow (using stratix III like DSP)
The following test was tested with the following tools:
-Synopsys Design Compiler 2017
-Cadence Encounter 2009

Prerequisites:
Make sure the ASIC tools are on your environments path, this can be done with the following commands:
$(which dc_shell-t)
$(which encounter)

1. Now the configuration files for the asic tools must be edited to match the environment and ASIC PDK being used
(If you're using UofT servers you can skip this portion as they're already setup)

  open up the following file in editor:
  - ~/COFFE/input_files/strtx_III_dsp/dsp_hb_settings.txt

  If you only want to run the asic flow, set the "asic_flow_only" param to True

  - set the "target_libraries" and "link_libraries" parameters to the absolute paths to the standard cell front end .db files provided by semiconductor PDK (surrounded by quotes).
  - set the "inv_footprint", "buf_footprint", and "delay_footprint" params to footprints, found in front end .lib files from pdk (found under similar names to "INVD0" "BUFFD1" "DEL0")

  The following params can be found in the PDK back end .lef files
  - set "metal_layer_names", "filler_cell_names", "core_site_name" params
  - set the "lef_files" param to the absolute path of the .lef files 

  Note: 
    make sure the number of metal layers being used is less than or equal to the number of metal_layer_names defined.
    make sure the .lef file has the correct number of metal layers as well

  - set the "best_case_libs", "standard_libs", and "worst_case_libs" to the corresponding absolute paths to PDK ".lib" files
  - set the primetime_lib_path to the absolute paths of the following design compiler directories and the front end PDK dirs used
  Optional Parameter Changes:
  - if desired one can sweep target frequency, number of metal layers, wire load model, core utilization, and mode of operation (this currently only works for dsp block)
    - to add additional sweep parameters one would define the variable to be swept again with the new value:
      - Ex. 
        clock_period=2.0
        clock_period=2.5
        etc...
2. run the following command (run this with python2):
  - $(python2 coffe.py -i 1 input_files/strtx_III_dsp/dsp_coffe_params.txt)

3. Once the program has finished go to the following directory:
  - ~/COFFE/analyze_results

  run the following command the argument points to where the .txt reports from post ASIC flow exist, which should be the same as the arch_out_folder param in dsp_coffe_params.txt):
    - $(python2 condense_results.py -r ../output_files/strtx_III_dsp/arch_out_dir)

  The above command creates a csv file with all reports from the specified directory.
  To plot the power, area, and delay results against target frequency run the following command (this requires python3 and matplotlib to be installed):
  - $(python3 plot_coffe_results.py -c report_csv_out/condensed_report.csv)

4. A script that runs all of the above commands can be run from COFFE repo:
  - $(chmod +x ./unit_test.sh)
  - $(./unit_test.sh)






## How to report an issue.

If you encounter an issue running COFFE, or if you have any questions about the features we support, please file an issue in github.
Please include the following with any issue you file:

  * COFFE git commit number showing which version of COFFE you used.
  * Version of external CAD tools (e.g. Hspice) used together with COFFE.
  * Detailed description of the issue.
    * Expected behaviour v.s. encountered behaviour.
    * Screenshot of COFFE output depictin the unexpected behaviour.
    * Contents of the last log file generated by COFFE (sort the files in the output directory by time and find the most recent).
    * Details on when the issue occurs e.g. is it during the time an external tool such as Hspice is running or when COFFE's code is running?


    
  
