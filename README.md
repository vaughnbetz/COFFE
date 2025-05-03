COFFE
=====

COFFE is a tool to create the circuitry and area, delay and power models for FPGA tiles (logic, RAM or heterogeneous tiles like DSP blocks).

If you make changes to COFFE, run the test.pl script to do some basic checks that existing functionality still works. It runs a small number of architectures to confirm COFFE can successfully create the output files, and confirms that the area output per tile is close to the expected value.

How to cite:  
[Sadegh to fill in].

# Update mode 10

Set updates=10 in the input .txt file to `coffe.py` to model the LUT skip architecture, with these additional parameters:
- `Z`: number of additional ALM adder direct inputs
- `sneak_paths`: number of sneak paths present in the S10-like arch
- `Fc_ad`: Fclocal of each adder direct input mux (w.r.t. sneak path inputs)