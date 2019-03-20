echo "a" > a.txt
echo "b" > b.txt
echo "c" > c.txt
echo "d" > d.txt
echo "e" > e.txt
echo "f" > f.txt
echo "x" > x.txt

for f in ../process_data_*00.l
do
	echo $f
	cp $f ../process_data.l
	echo $f >> a.txt
	echo $f >> b.txt
	echo $f >> c.txt
	echo $f >> d.txt
	echo $f >> e.txt
	echo $f >> f.txt
	echo $f >> x.txt
	for i in {1..3}
		do
		python ../../../COFFE/scripts/gen_rand_full_lut.py $i
		hspice rand_lut_a.sp 2>&1 | grep meas_avg_power= >> a.txt  &
		hspice rand_lut_b.sp 2>&1 | grep meas_avg_power= >> b.txt  &
		hspice rand_lut_c.sp 2>&1 | grep meas_avg_power= >> c.txt  &
		hspice rand_lut_d.sp 2>&1 | grep meas_avg_power= >> d.txt  &
		hspice rand_lut_e.sp 2>&1 | grep meas_avg_power= >> e.txt  &
		hspice rand_lut_f.sp 2>&1 | grep meas_avg_power= >> f.txt  &
		hspice rand_lut_x.sp 2>&1 | grep meas_avg_power= >> x.txt  &
		wait
	done
done
sed 's/ meas_avg_power= *//' a.txt > a_power.txt &
sed 's/ meas_avg_power= *//' b.txt > b_power.txt &
sed 's/ meas_avg_power= *//' c.txt > c_power.txt &
sed 's/ meas_avg_power= *//' d.txt > d_power.txt &
sed 's/ meas_avg_power= *//' e.txt > e_power.txt &
sed 's/ meas_avg_power= *//' f.txt > f_power.txt &
sed 's/ meas_avg_power= *//' x.txt > x_power.txt &
wait
rm a.txt &
rm b.txt &
rm c.txt &
rm d.txt &
rm e.txt &
rm f.txt &
rm x.txt &
wait
echo "done"
