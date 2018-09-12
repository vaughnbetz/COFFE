# COFFE Developer Guide

## Understanding the code - COFFE 101
If you are new to developing in COFFE, the best place to start reading the code is the top-level definition of the FPGA being modelled which can be found in "fpga.py" file. The comments in this file outline the overall operation of COFFE; we suggest you read them carefully and make sure you understand the high-level operation of this file.


## How to Test
Before committing any code to the repository, you must make sure none of the previous functionality is broken.
In the tests directory, you can find "tests_top_level.py". Run this file to execute existing tests. If any of the tests are broken, fix the code before committing your changes.
There are several examples of tests in this file and you might want to add your own tests similar to these for any functionality you add.


## Adding a new component or modifying a circuit component
If you want to add or modify a circuit component, you will need to make at least 3 changes:

  * Take a look at any of the classes that inherit from the _SizableCircuit class.
Each of these classes have the following functions: initialization (construct your basic data from the user input), generate (create a SPICE subcircuit for this component), generate_top (create a SPICE deck for the subcircuit in context -- i.e. driven by the proper waveform and loaded appropriately), update_area (estimate the area of the component given the current transistor sizing), and update_wire (estimate wire lengths and hence loads given the current area).
If you are going to edit one of these classes and/or add a new class, you need to include these stages. There are numerous classes in this file that you can use as examples; any can be used as a guide for adding a new class/component but picking one similar to the component you are adding likely gives the best guide.

  * To add a sizeable circuit class to COFFE's sizing loop, you should also modify the "size_fpga_transistors" method in "tran_sizing.py".
This method is the main sizing loop; you should include a block of code to size your new sizeable component here. Again, there are numerous examples in this method and you should simply follow one of those.

  * For a new component that impacts the speed of the FPGA (which is most components), you will also need to change the "get_eval_delay" and "get_final_delay" methods in "tran_sizing.py" so that COFFE's area/delay cost function sees the impact of delay changes in your new components. If you don't include your new component's delay in these functions, it will be sized for minimum area.

