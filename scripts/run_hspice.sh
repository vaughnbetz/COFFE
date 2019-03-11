hspice full_lut_A.sp 2>&1 | grep meas_avg_power= &&
hspice full_lut_B.sp 2>&1 | grep meas_avg_power= &&
hspice full_lut_C.sp 2>&1 | grep meas_avg_power= &&
hspice full_lut_D.sp 2>&1 | grep meas_avg_power= &&
hspice full_lut_E.sp 2>&1 | grep meas_avg_power= &&
hspice full_lut_F.sp 2>&1 | grep meas_avg_power= &&
wait
echo "done"