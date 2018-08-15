import tests.py

'''
This is the top-level tester for COFFE runs.
To add a test, you need to provide 1) a reference file 2)directory of test execution 3)acceptable margin for error.
The following are some of the examples for these items
'''

# A fracturable lut test files
print "Testing an Architecture with Fracturable LUTs and Carry chains."
test1_flut0_reference = '~/COFFE-master/tests/test_references/flut0.txt'
test1_flut0_directory = '~/COFFE-master/input_files/flut0test'
test1_flut_margin = 0.05
# Execute the test
test_flow(test1_flut0_reference, test1_flut0_directory, test1_flut_margin)



# SRAM-based memory test
print "Testing an Architecture with SRAM-based memory."
test2_sram0_reference = '~/COFFE-master/tests/test_references/sram0.txt'
test2_sram0_directory = '~/COFFE-master/input_files/sram0test'
test2_sram_margin = 0.05
# Execute the test
test_flow(test1_sram0_reference, test1_sram0_directory, test1_sram0_margin)


# MTJ memory test
print "Testing an Architecture with MTJ-based memory."
test2_mtj0_reference = '~/COFFE-master/tests/test_references/mtj0.txt'
test2_mtj0_directory = '~/COFFE-master/input_files/mtj0test'
test2_mtj_margin = 0.05
# Execute the test
test_flow(test1_mtj0_reference, test1_mtj0_directory, test1_mtj0_margin)



# Hard block test
print "Testing a Hardblock with peripherals. The goal is to make sure the ASIC flow runs successfully and the full-custom interface code is not broken."
test2_hb0_reference = '~/COFFE-master/tests/test_references/hb0.txt'
test2_hb0_directory = '~/COFFE-master/input_files/hb0test'
test2_hb_margin = 0.05
# Execute the test
test_flow(test1_hb0_reference, test1_hb0_directory, test1_hb0_margin)



