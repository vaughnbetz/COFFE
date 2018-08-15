import tests.py

'''
This is the top-level tester for COFFE runs.
To add a test, you need to provide 1) a reference file 2) a directory in which the test was already executed 3) an acceptable margin for error.
[VB: add run COFFE]
As features are added to COFFE, you should ensure they are covered by the tests in this file. 
As COFFE invokes HSPICE many times and hence has a high runtime, we are also trying to cover COFFE's features with a small
number of architectures by changing many architecture parameters from one test to the next.
The following are some examples for these items.
'''

# A fracturable lut test files
print "Testing an Architecture with Fracturable 6-LUTs with no extra inputs and 2 bits of carry per FLUT with carry skip."
test1_flut0_reference = '~/COFFE-master/tests/test_references/flut0.txt'  # Known good results
test1_flut0_directory = '~/COFFE-master/input_files/flut0test'  # Your new run of COFFE
test1_flut_margin = 0.05  # Allowable difference from the reference is 5% for each number.
# Execute the test
test_flow(test1_flut0_reference, test1_flut0_directory, test1_flut_margin)


# SRAM-based memory test. Also tests non-fracturable 6-LUTs without carry chains.
print "Testing an Architecture with SRAM-based memory, along with non-fracturable 6-LUTs without carry chains."
test2_sram0_reference = '~/COFFE-master/tests/test_references/sram0.txt'
test2_sram0_directory = '~/COFFE-master/input_files/sram0test'
test2_sram_margin = 0.05
# Execute the test
test_flow(test1_sram0_reference, test1_sram0_directory, test1_sram0_margin)


# MTJ memory test. Also tests a fracturable 6-LUT with 5 extra inputs and 1 bit of carry per FLUT with a ripple adder.
print "Testing an Architecture with MTJ-based memory, along with a fracturable 6-LUT with 5 extra inputs and 1 bit of carry per FLUT with a ripple adder."
test2_mtj0_reference = '~/COFFE-master/tests/test_references/mtj0.txt'
test2_mtj0_directory = '~/COFFE-master/input_files/mtj0test'
test2_mtj_margin = 0.05
# Execute the test
test_flow(test1_mtj0_reference, test1_mtj0_directory, test1_mtj0_margin)


# Hard block test. The hard block is simple: a registered inverter. Also tests a non-fracturable 4-LUT
print "Testing a Hardblock with peripherals. The goal is to make sure the ASIC flow runs successfully and the full-custom interface code is not broken. Also tests a non-fracturable 4-LUT."
test2_hb0_reference = '~/COFFE-master/tests/test_references/hb0.txt'
test2_hb0_directory = '~/COFFE-master/input_files/hb0test'
test2_hb_margin = 0.05
# Execute the test
test_flow(test1_hb0_reference, test1_hb0_directory, test1_hb0_margin)


