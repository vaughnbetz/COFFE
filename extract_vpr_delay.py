import os
import sys
import shutil
import argparse
import time

file_path_list = ["vpr_outputs/5xp1.out", 
			 "vpr_outputs/9sym.out",
			 "vpr_outputs/9symml.out",
			 "vpr_outputs/alu2.out",
			 "vpr_outputs/alu4.out",
			 "vpr_outputs/apex1.out",
			 "vpr_outputs/apex2.out",
			 "vpr_outputs/apex3.out",
			 "vpr_outputs/apex4.out",
			 "vpr_outputs/apex5.out",
			]
delay_sum = 0
count = 0
for file_path in file_path_list :
	file = open(file_path, 'r')
	
	for line in file :
		words = line.split()
		if "Final critical path" in line:
			delay = words[3]
			print "file: " + file_path + " Final critical path: " + delay
			delay_sum += float(delay)
			count += 1
	file.close()

average_delay = delay_sum/count
print "total count: " + str(count)
print "average_delay: " + str(average_delay)

# i = 1
# for file_path in file_path_list :
# 	file = open(file_path, 'w')
# 	file.write("filename: " + file_path + "\n")
# 	file.write("stuff: abc\n")
# 	file.write("target: " + str(i) + "\n")
# 	file.write("something: 123\n")
# 	file.close()
# 	i = i + 1