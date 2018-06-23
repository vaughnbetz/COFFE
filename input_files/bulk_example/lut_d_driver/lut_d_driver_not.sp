.TITLE lut_d_driver_not 

********************************************************************************
** Include libraries, parameters and other
********************************************************************************

.LIB "../includes.l" INCLUDES

********************************************************************************
** Setup and input
********************************************************************************

.TRAN 1p 4n SWEEP DATA=sweep_data
.OPTIONS BRIEF=1

* Input signal
VIN n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)

* Power rail for the circuit under test.
* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.
V_LUT_DRIVER vdd_lut_driver gnd supply_v

********************************************************************************
** Measurement
********************************************************************************

* inv_lut_d_driver_not_1 delays
.MEASURE TRAN meas_inv_lut_d_driver_not_1_tfall TRIG V(n_1_2) VAL='supply_v/2' RISE=1
+    TARG V(Xlut_d_driver_not_1.n_1_1) VAL='supply_v/2' FALL=1
.MEASURE TRAN meas_inv_lut_d_driver_not_1_trise TRIG V(n_1_2) VAL='supply_v/2' FALL=1
+    TARG V(Xlut_d_driver_not_1.n_1_1) VAL='supply_v/2' RISE=1

* inv_lut_d_driver_not_2 delays
.MEASURE TRAN meas_inv_lut_d_driver_not_2_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1
+    TARG V(n_out_n) VAL='supply_v/2' FALL=1
.MEASURE TRAN meas_inv_lut_d_driver_not_2_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1
+    TARG V(n_out_n) VAL='supply_v/2' RISE=1

* Total delays
.MEASURE TRAN meas_total_tfall TRIG V(n_1_2) VAL='supply_v/2' FALL=1
+    TARG V(n_out_n) VAL='supply_v/2' FALL=1
.MEASURE TRAN meas_total_trise TRIG V(n_1_2) VAL='supply_v/2' RISE=1
+    TARG V(n_out_n) VAL='supply_v/2' RISE=1

.MEASURE TRAN meas_logic_low_voltage FIND V(n_out) AT=3n

* Measure the power required to propagate a rise and a fall transition through the lut driver at 250MHz.
.MEASURE TRAN meas_current INTEGRAL I(V_LUT_DRIVER) FROM=0ns TO=4ns
.MEASURE TRAN meas_avg_power PARAM = '-((meas_current)/4n)*supply_v'

********************************************************************************
** Circuit
********************************************************************************

Xcb_mux_on_1 n_in n_1_1 vsram vsram_n vdd gnd cb_mux_on
Xlocal_routing_wire_load_1 n_1_1 n_1_2 vsram vsram_n vdd gnd vdd local_routing_wire_load
Xlut_d_driver_1 n_1_2 n_out vsram vsram_n n_rsel n_2_1 vdd gnd lut_d_driver
Xlut_d_driver_not_1 n_2_1 n_out_n vdd_lut_driver gnd lut_d_driver_not
Xlut_d_driver_load_1 n_out n_vdd n_gnd lut_d_driver_load
Xlut_d_driver_load_2 n_out_n n_vdd n_gnd lut_d_driver_load

.END