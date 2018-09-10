# COFFE Developer Guide

## How to Change
if you are new to developing COFFE, you might want to start by looking at the top-level definition of the FPGA being modelled which can be found in "fpga.py" file.
Spend some time and understand how things work around in this file. Take a look at any of the classes that inherit the _SizableCircuit class.
These classes have the following functions: initialization, generate, generate_top, update_area, and update_wire.
If you are going to edit one of these classes and/or add a new class, you need to include these stages. There are numerous classes in this file that you can use as examples.

To make add a sizeable circuit class to COFFE's sizing loop, you should also modify "tran_sizing.py".
Take a look around this file and find the main sizing loop. You should include your sizable circuit here. Again, there are numerous examples in this file and you should simply follow one of those.

## How to Test
Before committing any code to the repository, you must make sure none of the previous functionality is broken.
In the tests directory, you can find "tests_top_level.py". Run this file to execute existing tests. If any of the tests are broken, fix the code before committing your changes.
There are several examples of tests in this file and you might want to add your own tests similar to these for any functionality you add.

