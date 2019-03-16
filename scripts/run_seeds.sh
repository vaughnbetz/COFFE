

echo "xor lut"

for f in ../process_data_*00.l
do
echo $f
cp $f ../process_data.l
	for i in {1..250}
	do
	python ../../../COFFE/scripts/gen_rand_full_lut.py $i 1
	hspice rand_lut.sp 2>&1 | grep meas_avg_power=
	done
done

echo "random lut"

for f in ../process_data_*00.l
do
echo $f
cp $f ../process_data.l
	for i in {1..250}
	do
	python ../../../COFFE/scripts/gen_rand_full_lut.py $i 0
	hspice rand_lut.sp 2>&1 | grep meas_avg_power=
	done
done

echo "done"
