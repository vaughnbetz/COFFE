import tests
import subprocess
import os

'''
This is the top-level tester for COFFE runs.
To add a test, you need to provide 1) a reference file 2) an input file 3) an acceptable margin for error.
As features are added to COFFE, you should ensure they are covered by the tests in this file. 
As COFFE invokes HSPICE many times and hence has a high runtime, we are also trying to cover COFFE's features with a small
number of architectures by changing many architecture parameters from one test to the next.
The following are some examples for these items.
'''


# A fracturable lut test files
os.chdir(os.path.expanduser(('~/COFFE-master/latest/COFFE')))
# invoke COFFE with input file
subprocess.call('python coffe.py input_files/flut0.txt -i 4 >testflut.log', shell=True, executable='/bin/bash') 

# Run the tests
print "Testing an Architecture with Fracturable 6-LUTs with no extra inputs and 2 bits of carry per FLUT with carry skip."
test1_flut0_reference = '~/COFFE-master/latest/COFFE/tests/test_references/flut0.txt'  # Known good results
test1_flut0_directory = '~/COFFE-master/latest/COFFE/input_files/flut0'  # Your new run of COFFE
test1_flut_margin = 0.05  # Allowable difference from the reference is 5% for each number.
# Execute the test
tests.test_flow(test1_flut0_reference, test1_flut0_directory, test1_flut_margin)

os.chdir(os.path.expanduser(('~/COFFE-master/latest/COFFE')))
# SRAM-based memory test. Also tests non-fracturable 6-LUTs without carry chains.
# invoke COFFE with input file
subprocess.call('python coffe.py input_files/sram0.txt -i 4 >testsram.log', shell=True, executable='/bin/bash') 
# Run the tests
print "Testing an Architecture with SRAM-based memory, along with non-fracturable 6-LUTs without carry chains."
test2_sram0_reference = '~/COFFE-master/latest/COFFE/tests/test_references/sram0.txt'
test2_sram0_directory = '~/COFFE-master/latest/COFFE/input_files/sram0'
test2_sram0_margin = 0.05
# Execute the test
tests.test_flow(test2_sram0_reference, test2_sram0_directory, test2_sram0_margin)

os.chdir(os.path.expanduser(('~/COFFE-master/latest/COFFE')))
# MTJ memory test. Also tests a fracturable 6-LUT with 5 extra inputs and 1 bit of carry per FLUT with a ripple adder.
# invoke COFFE with input file
subprocess.call('python coffe.py input_files/mtj0.txt -i 4 >testmtj.log', shell=True, executable='/bin/bash') 
# Run the tests
print "Testing an Architecture with MTJ-based memory, along with a fracturable 6-LUT with 5 extra inputs and 1 bit of carry per FLUT with a ripple adder."
test3_mtj0_reference = '~/COFFE-master/latest/COFFE/tests/test_references/mtj0.txt'
test3_mtj0_directory = '~/COFFE-master/latest/COFFE/input_files/mtj0'
test3_mtj0_margin = 0.05
# Execute the test
tests.test_flow(test3_mtj0_reference, test3_mtj0_directory, test3_mtj0_margin)

os.chdir(os.path.expanduser(('~/COFFE-master/latest/COFFE')))
# Hard block test. The hard block is simple: a registered inverter. Also tests a non-fracturable 4-LUT
# invoke COFFE with input file
subprocess.call('python coffe.py input_files/hb0.txt -i 4 >testhb.log', shell=True, executable='/bin/bash') 
# Run the tests
print "Testing a Hardblock with peripherals. The goal is to make sure the ASIC flow runs successfully and the full-custom interface code is not broken. Also tests a non-fracturable 4-LUT."
test4_hb0_reference = '~/COFFE-master/latest/COFFE/tests/test_references/hb0.txt'
test4_hb0_directory = '~/COFFE-master/latest/COFFE/input_files/hb0'
test4_hb0_margin = 0.05
# Execute the test
tests.test_flow(test4_hb0_reference, test4_hb0_directory, test4_hb0_margin)


