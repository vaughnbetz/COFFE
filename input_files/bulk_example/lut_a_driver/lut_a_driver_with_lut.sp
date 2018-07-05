.TITLE lut_a_driver 

********************************************************************************
** Include libraries, parameters and other
********************************************************************************

.LIB "../includes.l" INCLUDES

********************************************************************************
** Setup and input
********************************************************************************

.TRAN 1p 16n SWEEP DATA=sweep_data
.OPTIONS BRIEF=1

* Input signal
VIN_SRAM n_in_sram gnd PULSE (0 supply_v 4n 0 0 4n 8n)
VIN_GATE n_in_gate gnd PULSE (supply_v 0 3n 0 0 2n 4n)

* Power rail for the circuit under test.
* This allows us to measure power of a circuit under test without measuring the power of wave shaping and load circuitry.
V_LUT vdd_lut gnd supply_v

********************************************************************************
** Measurement
********************************************************************************

* Total delays
.MEASURE TRAN meas_total_tfall TRIG V(n_3_1) VAL='supply_v/2' RISE=2
+    TARG V(n_out) VAL='supply_v/2' FALL=1
.MEASURE TRAN meas_total_trise TRIG V(n_3_1) VAL='supply_v/2' RISE=1
+    TARG V(n_out) VAL='supply_v/2' RISE=1

.MEASURE TRAN meas_logic_low_voltage FIND V(n_out) AT=3n

* Measure the power required to propagate a rise and a fall transition through the lut at 250MHz.
.MEASURE TRAN meas_current1 INTEGRAL I(V_LUT) FROM=5ns TO=7ns
.MEASURE TRAN meas_current2 INTEGRAL I(V_LUT) FROM=9ns TO=11ns
.MEASURE TRAN meas_avg_power PARAM = '-((meas_current1 + meas_current2)/4n)*supply_v'

********************************************************************************
** Circuit
********************************************************************************

Xcb_mux_on_1 n_in_gate n_1_1 vsram vsram_n vdd gnd cb_mux_on
Xlocal_routing_wire_load_1 n_1_1 n_1_2 vsram vsram_n vdd gnd vdd local_routing_wire_load
Xlut_a_driver_1 n_1_2 n_3_1 vsram vsram_n n_rsel n_2_1 vdd gnd lut_a_driver
Xlut_a_driver_not_1 n_2_1 n_1_4 vdd gnd lut_a_driver_not
Xlut n_in_sram n_out n_3_1 vdd vdd vdd vdd vdd vdd_lut gnd lut
Xlut_output_load n_out n_local_out n_general_out vsram vsram_n vdd gnd vdd vdd lut_output_load

.END