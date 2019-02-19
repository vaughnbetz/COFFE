import sys
import os.path
import re

output_dir = sys.argv[1]



file600 = os.path.join(output_dir, "report_600mv.txt")

blocks = []
summary = []

with open(file600) as f:
	data600 = f.read().splitlines()


parsing_block = False
for line in data600:
	if parsing_block:
		if line == "":
			parsing_block = False
		else:
			w = re.split(r'\s{2,}', line)
			blocks.append([w[1]])
			blocks[block_id].append(w[2])
			blocks[block_id].append(w[3])
			block_id += 1

	if "Subcircuit" in line:
		parsing_block = True
		block_id = 0

	if "Tile Area" in line:
		summary.append([re.split(r'\s{2,}', line.replace("um^2",""))[2]])

	if "Representative Critical Path Delay" in line:
		summary[0].append(re.split(r'\s{2,}', line.replace("ps",""))[2])

	if "Cost (area^1 x delay^1)" in line:
		summary[0].append(re.split(r'\s{2,}', line)[2])

files = ["report_700mv.txt", "report_800mv.txt", "report_900mv.txt", "report_1000mv.txt"]

for n in range(4):
	with open(os.path.join(output_dir, files[n])) as f:
		d = f.read().splitlines()

	parsing_block = False
	for line in d:
		if parsing_block:
			if line == "":
				parsing_block = False
			else:
				w = re.split(r'\s{2,}', line)
				blocks[block_id].append(w[3])
				block_id += 1

		if "Subcircuit" in line:
			parsing_block = True
			block_id = 0

		if "Tile Area" in line:
			summary.append([re.split(r'\s{2,}', line.replace("um^2",""))[2]])

		if "Representative Critical Path Delay" in line:
			summary[n+1].append(re.split(r'\s{2,}', line.replace("ps",""))[2])

		if "Cost (area^1 x delay^1)" in line:
			summary[n+1].append(re.split(r'\s{2,}', line)[2])

print ("Subcircuit, Area (um^2), 0.6v, 0.7v, 0.8v, 0.9v, 1.0v")
for b in blocks:
	l = ""
	for d in b:
		l += d + ","

	print(l)

print ("")
print (", 0.6v, 0.7v, 0.8v, 0.9v, 1.0v")
a = "Tile Area(um^2),"
d = "Representative Critical Path Delay(ps),"
c = "Cost (area^1 x delay^1),"
for s in summary:
	a += s[0] + ","
	d += s[1] + ","
	c += s[2] + ","

print (a)
print (d)
print (c)