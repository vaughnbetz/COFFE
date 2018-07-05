*** SUBCIRCUITS

.LIB SUBCIRCUITS

******************************************************************************************
* sb_mux driver subcircuit (12:1)
******************************************************************************************
.SUBCKT sb_mux_driver n_in n_out n_vdd n_gnd
Xrest_sb_mux n_in n_1_1 n_vdd n_gnd rest Wp=rest_sb_mux_pmos
Xinv_sb_mux_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_sb_mux_1_nmos Wp=inv_sb_mux_1_pmos
Xwire_sb_mux_driver n_1_1 n_1_2 wire Rw=wire_sb_mux_driver_res Cw=wire_sb_mux_driver_cap
Xinv_sb_mux_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_sb_mux_2_nmos Wp=inv_sb_mux_2_pmos
.ENDS


******************************************************************************************
* sb_mux subcircuit (12:1), turned off 
******************************************************************************************
.SUBCKT sb_mux_off n_in n_gate n_gate_n n_vdd n_gnd
Xptran_sb_mux_L1 n_in n_gnd n_gnd n_gnd ptran Wn=ptran_sb_mux_L1_nmos
.ENDS


******************************************************************************************
* sb_mux subcircuit (12:1), partially turned on
******************************************************************************************
.SUBCKT sb_mux_partial n_in n_gate n_gate_n n_vdd n_gnd
Xptran_sb_mux_L1 n_in n_1 n_gate n_gnd ptran Wn=ptran_sb_mux_L1_nmos
Xwire_sb_mux_L1_1 n_1 n_1_1 wire Rw='wire_sb_mux_L1_res/4' Cw='wire_sb_mux_L1_cap/4'
Xptran_sb_mux_L1_1h n_gnd n_1_1 n_gnd n_gnd ptran Wn=ptran_sb_mux_L1_nmos
Xwire_sb_mux_L1_2 n_1_1 n_1_2 wire Rw='wire_sb_mux_L1_res/4' Cw='wire_sb_mux_L1_cap/4'
Xptran_sb_mux_L1_2h n_gnd n_1_2 n_gnd n_gnd ptran Wn=ptran_sb_mux_L1_nmos
Xwire_sb_mux_L1_3 n_1_2 n_1_3 wire Rw='wire_sb_mux_L1_res/4' Cw='wire_sb_mux_L1_cap/4'
Xptran_sb_mux_L1_3h n_gnd n_1_3 n_gnd n_gnd ptran Wn=ptran_sb_mux_L1_nmos
Xwire_sb_mux_L1_4 n_1_3 n_1_4 wire Rw='wire_sb_mux_L1_res/4' Cw='wire_sb_mux_L1_cap/4'
Xptran_sb_mux_L2 n_1_4 n_gnd n_gnd n_gnd ptran Wn=ptran_sb_mux_L2_nmos
.ENDS


******************************************************************************************
* sb_mux subcircuit (12:1), fully turned on (mux only)
******************************************************************************************
.SUBCKT sb_mux_on_mux_only n_in n_out n_gate n_gate_n n_vdd n_gnd
Xptran_sb_mux_L1 n_in n_1 n_gate n_gnd ptran Wn=ptran_sb_mux_L1_nmos
Xwire_sb_mux_L1_1 n_1 n_1_1 wire Rw='wire_sb_mux_L1_res/4' Cw='wire_sb_mux_L1_cap/4'
Xptran_sb_mux_L1_1h n_gnd n_1_1 n_gnd n_gnd ptran Wn=ptran_sb_mux_L1_nmos
Xwire_sb_mux_L1_2 n_1_1 n_1_2 wire Rw='wire_sb_mux_L1_res/4' Cw='wire_sb_mux_L1_cap/4'
Xptran_sb_mux_L1_2h n_gnd n_1_2 n_gnd n_gnd ptran Wn=ptran_sb_mux_L1_nmos
Xwire_sb_mux_L1_3 n_1_2 n_1_3 wire Rw='wire_sb_mux_L1_res/4' Cw='wire_sb_mux_L1_cap/4'
Xptran_sb_mux_L1_3h n_gnd n_1_3 n_gnd n_gnd ptran Wn=ptran_sb_mux_L1_nmos
Xwire_sb_mux_L1_4 n_1_3 n_1_4 wire Rw='wire_sb_mux_L1_res/4' Cw='wire_sb_mux_L1_cap/4'
Xptran_sb_mux_L2 n_1_4 n_2 n_gate n_gnd ptran Wn=ptran_sb_mux_L2_nmos
Xwire_sb_mux_L2_1 n_2 n_out wire Rw='wire_sb_mux_L2_res/2' Cw='wire_sb_mux_L2_cap/2'
Xptran_sb_mux_L2_1h n_gnd n_out n_gnd n_gnd ptran Wn=ptran_sb_mux_L2_nmos
Xwire_sb_mux_L2_2  n_out n_2_1 wire Rw='wire_sb_mux_L2_res/2' Cw='wire_sb_mux_L2_cap/2'
Xptran_sb_mux_L2_2h n_gnd n_2_1 n_gnd n_gnd ptran Wn=ptran_sb_mux_L2_nmos
.ENDS


******************************************************************************************
* sb_mux subcircuit (12:1), fully turned on 
******************************************************************************************
.SUBCKT sb_mux_on n_in n_out n_gate n_gate_n n_vdd n_gnd
Xsb_mux_on_mux_only n_in n_1_1 n_gate n_gate_n n_vdd n_gnd sb_mux_on_mux_only
Xsb_mux_driver n_1_1 n_out n_vdd n_gnd sb_mux_driver
.ENDS


******************************************************************************************
* cb_mux driver subcircuit (64:1)
******************************************************************************************
.SUBCKT cb_mux_driver n_in n_out n_vdd n_gnd
Xrest_cb_mux n_in n_1_1 n_vdd n_gnd rest Wp=rest_cb_mux_pmos
Xinv_cb_mux_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_cb_mux_1_nmos Wp=inv_cb_mux_1_pmos
Xwire_cb_mux_driver n_1_1 n_1_2 wire Rw=wire_cb_mux_driver_res Cw=wire_cb_mux_driver_cap
Xinv_cb_mux_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_cb_mux_2_nmos Wp=inv_cb_mux_2_pmos
.ENDS


******************************************************************************************
* cb_mux subcircuit (64:1), turned off 
******************************************************************************************
.SUBCKT cb_mux_off n_in n_gate n_gate_n n_vdd n_gnd
Xptran_cb_mux_L1 n_in n_gnd n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
.ENDS


******************************************************************************************
* cb_mux subcircuit (64:1), partially turned on
******************************************************************************************
.SUBCKT cb_mux_partial n_in n_gate n_gate_n n_vdd n_gnd
Xptran_cb_mux_L1 n_in n_1 n_gate n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_1 n_1 n_1_1 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_1h n_gnd n_1_1 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_2 n_1_1 n_1_2 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_2h n_gnd n_1_2 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_3 n_1_2 n_1_3 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_3h n_gnd n_1_3 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_4 n_1_3 n_1_4 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_4h n_gnd n_1_4 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_5 n_1_4 n_1_5 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_5h n_gnd n_1_5 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_6 n_1_5 n_1_6 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_6h n_gnd n_1_6 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_7 n_1_6 n_1_7 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_7h n_gnd n_1_7 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_8 n_1_7 n_1_8 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L2 n_1_8 n_gnd n_gnd n_gnd ptran Wn=ptran_cb_mux_L2_nmos
.ENDS


******************************************************************************************
* cb_mux subcircuit (64:1), fully turned on (mux only)
******************************************************************************************
.SUBCKT cb_mux_on_mux_only n_in n_out n_gate n_gate_n n_vdd n_gnd
Xptran_cb_mux_L1 n_in n_1 n_gate n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_1 n_1 n_1_1 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_1h n_gnd n_1_1 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_2 n_1_1 n_1_2 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_2h n_gnd n_1_2 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_3 n_1_2 n_1_3 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_3h n_gnd n_1_3 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_4 n_1_3 n_1_4 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_4h n_gnd n_1_4 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_5 n_1_4 n_1_5 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_5h n_gnd n_1_5 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_6 n_1_5 n_1_6 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_6h n_gnd n_1_6 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_7 n_1_6 n_1_7 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L1_7h n_gnd n_1_7 n_gnd n_gnd ptran Wn=ptran_cb_mux_L1_nmos
Xwire_cb_mux_L1_8 n_1_7 n_1_8 wire Rw='wire_cb_mux_L1_res/8' Cw='wire_cb_mux_L1_cap/8'
Xptran_cb_mux_L2 n_1_8 n_2 n_gate n_gnd ptran Wn=ptran_cb_mux_L2_nmos
Xwire_cb_mux_L2_1 n_2 n_2_1 wire Rw='wire_cb_mux_L2_res/7' Cw='wire_cb_mux_L2_cap/7'
Xptran_cb_mux_L2_1h n_gnd n_2_1 n_gnd n_gnd ptran Wn=ptran_cb_mux_L2_nmos
Xwire_cb_mux_L2_2 n_2_1 n_2_2 wire Rw='wire_cb_mux_L2_res/7' Cw='wire_cb_mux_L2_cap/7'
Xptran_cb_mux_L2_2h n_gnd n_2_2 n_gnd n_gnd ptran Wn=ptran_cb_mux_L2_nmos
Xwire_cb_mux_L2_3 n_2_2 n_2_3 wire Rw='wire_cb_mux_L2_res/7' Cw='wire_cb_mux_L2_cap/7'
Xptran_cb_mux_L2_3h n_gnd n_2_3 n_gnd n_gnd ptran Wn=ptran_cb_mux_L2_nmos
Xwire_cb_mux_L2_4 n_2_3 n_out wire Rw='wire_cb_mux_L2_res/14' Cw='wire_cb_mux_L2_cap/14'
Xwire_cb_mux_L2_5  n_out n_2_4 wire Rw='wire_cb_mux_L2_res/14' Cw='wire_cb_mux_L2_cap/14'
Xptran_cb_mux_L2_4h n_gnd n_2_4 n_gnd n_gnd ptran Wn=ptran_cb_mux_L2_nmos
Xwire_cb_mux_L2_6 n_2_4 n_2_5 wire Rw='wire_cb_mux_L2_res/7' Cw='wire_cb_mux_L2_cap/7'
Xptran_cb_mux_L2_5h n_gnd n_2_5 n_gnd n_gnd ptran Wn=ptran_cb_mux_L2_nmos
Xwire_cb_mux_L2_7 n_2_5 n_2_6 wire Rw='wire_cb_mux_L2_res/7' Cw='wire_cb_mux_L2_cap/7'
Xptran_cb_mux_L2_6h n_gnd n_2_6 n_gnd n_gnd ptran Wn=ptran_cb_mux_L2_nmos
Xwire_cb_mux_L2_8 n_2_6 n_2_7 wire Rw='wire_cb_mux_L2_res/7' Cw='wire_cb_mux_L2_cap/7'
Xptran_cb_mux_L2_7h n_gnd n_2_7 n_gnd n_gnd ptran Wn=ptran_cb_mux_L2_nmos
.ENDS


******************************************************************************************
* cb_mux subcircuit (64:1), fully turned on 
******************************************************************************************
.SUBCKT cb_mux_on n_in n_out n_gate n_gate_n n_vdd n_gnd
Xcb_mux_on_mux_only n_in n_1_1 n_gate n_gate_n n_vdd n_gnd cb_mux_on_mux_only
Xcb_mux_driver n_1_1 n_out n_vdd n_gnd cb_mux_driver
.ENDS


******************************************************************************************
* 6-LUT subcircuit 
******************************************************************************************
.SUBCKT lut n_in n_out n_a n_b n_c n_d n_e n_f n_vdd n_gnd
Xinv_lut_sram_driver_1 n_in n_1_1 n_vdd n_gnd inv Wn=45n Wp=75.015n
Xwire_lut_sram_driver n_1_1 n_1_2 wire Rw=wire_lut_sram_driver_res Cw=wire_lut_sram_driver_cap
Xinv_lut_sram_driver_2 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_lut_0sram_driver_2_nmos Wp=inv_lut_0sram_driver_2_pmos
Xwire_lut_sram_driver_out n_2_1 n_2_2 wire Rw=wire_lut_sram_driver_out_res Cw=wire_lut_sram_driver_out_cap

* First chain
Xptran_lut_L1 n_2_2 n_3_1 n_a n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_L1 n_3_1 n_3_2 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'
Xwire_lut_L1h n_3_2 n_3_3 wire Rw='wire_lut_L1_res/2' Cw='wire_lut_L1_cap/2'
Xptran_lut_L1h n_gnd n_3_3 n_gnd n_gnd ptran Wn=ptran_lut_L1_nmos
Xptran_lut_L2 n_3_2 n_4_1 n_b n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_L2 n_4_1 n_4_2 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'
Xwire_lut_L2h n_4_2 n_4_3 wire Rw='wire_lut_L2_res/2' Cw='wire_lut_L2_cap/2'
Xptran_lut_L2h n_gnd n_4_3 n_gnd n_gnd ptran Wn=ptran_lut_L2_nmos
Xptran_lut_L3 n_4_2 n_5_1 n_c n_gnd ptran Wn=ptran_lut_L3_nmos
Xwire_lut_L3 n_5_1 n_5_2 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'
Xwire_lut_L3h n_5_2 n_5_3 wire Rw='wire_lut_L3_res/2' Cw='wire_lut_L3_cap/2'
Xptran_lut_L3h n_gnd n_5_3 n_gnd n_gnd ptran Wn=ptran_lut_L3_nmos

* Internal buffer 
Xrest_lut_int_buffer n_5_2 n_6_1 n_vdd n_gnd rest Wp=rest_lut_int_buffer_pmos
Xinv_lut_int_buffer_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_1_nmos Wp=inv_lut_int_buffer_1_pmos
Xwire_lut_int_buffer n_6_1 n_6_2 wire Rw=wire_lut_int_buffer_res Cw=wire_lut_int_buffer_cap
Xinv_lut_int_buffer_2 n_6_2 n_7_1 n_vdd n_gnd inv Wn=inv_lut_int_buffer_2_nmos Wp=inv_lut_int_buffer_2_pmos
Xwire_lut_int_buffer_out n_7_1 n_7_2 wire Rw=wire_lut_int_buffer_out_res Cw=wire_lut_int_buffer_out_cap

* Second chain
Xptran_lut_L4 n_7_2 n_8_1 n_d n_gnd ptran Wn=ptran_lut_L4_nmos
Xwire_lut_L4 n_8_1 n_8_2 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'
Xwire_lut_L4h n_8_2 n_8_3 wire Rw='wire_lut_L4_res/2' Cw='wire_lut_L4_cap/2'
Xptran_lut_L4h n_gnd n_8_3 n_gnd n_gnd ptran Wn=ptran_lut_L4_nmos
Xptran_lut_L5 n_8_2 n_9_1 n_e n_gnd ptran Wn=ptran_lut_L5_nmos
Xwire_lut_L5 n_9_1 n_9_2 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'
Xwire_lut_L5h n_9_2 n_9_3 wire Rw='wire_lut_L5_res/2' Cw='wire_lut_L5_cap/2'
Xptran_lut_L5h n_gnd n_9_3 n_gnd n_gnd ptran Wn=ptran_lut_L5_nmos
Xptran_lut_L6 n_9_2 n_10_1 n_f n_gnd ptran Wn=ptran_lut_L6_nmos
Xwire_lut_L6 n_10_1 n_10_2 wire Rw='wire_lut_L6_res/2' Cw='wire_lut_L6_cap/2'
Xwire_lut_L6h n_10_2 n_10_3 wire Rw='wire_lut_L6_res/2' Cw='wire_lut_L6_cap/2'
Xptran_lut_L6h n_gnd n_10_3 n_gnd n_gnd ptran Wn=ptran_lut_L6_nmos

* Output buffer 
Xrest_lut_out_buffer n_10_2 n_11_1 n_vdd n_gnd rest Wp=rest_lut_out_buffer_pmos
Xinv_lut_out_buffer_1 n_10_2 n_11_1 n_vdd n_gnd inv Wn=inv_lut_out_buffer_1_nmos Wp=inv_lut_out_buffer_1_pmos
Xwire_lut_out_buffer n_11_1 n_11_2 wire Rw=wire_lut_out_buffer_res Cw=wire_lut_out_buffer_cap
Xinv_lut_out_buffer_2 n_11_2 n_out n_vdd n_gnd inv Wn=inv_lut_out_buffer_2_nmos Wp=inv_lut_out_buffer_2_pmos

.ENDS


******************************************************************************************
* LUT lut_a_driver subcircuit 
******************************************************************************************
.SUBCKT lut_a_driver n_in n_out n_gate n_gate_n n_rsel n_not_input n_vdd n_gnd
Xwire_lut_a_driver n_in n_not_input wire Rw=wire_lut_a_driver_res Cw=wire_lut_a_driver_cap
Xinv_lut_a_driver_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_lut_a_driver_2_nmos Wp=inv_lut_a_driver_2_pmos
.ENDS


******************************************************************************************
* LUT lut_a_driver_not subcircuit 
******************************************************************************************
.SUBCKT lut_a_driver_not n_in n_out n_vdd n_gnd
Xinv_lut_a_driver_not_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_lut_a_driver_not_1_nmos Wp=inv_lut_a_driver_not_1_pmos
Xwire_lut_a_driver_not n_1_1 n_1_2 wire Rw=wire_lut_a_driver_not_res Cw=wire_lut_a_driver_not_cap
Xinv_lut_a_driver_not_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_lut_a_driver_not_2_nmos Wp=inv_lut_a_driver_not_2_pmos
.ENDS


******************************************************************************************
* LUT lut_b_driver subcircuit 
******************************************************************************************
.SUBCKT lut_b_driver n_in n_out n_gate n_gate_n n_rsel n_not_input n_vdd n_gnd
Xwire_lut_b_driver n_in n_not_input wire Rw=wire_lut_b_driver_res Cw=wire_lut_b_driver_cap
Xinv_lut_b_driver_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_lut_b_driver_2_nmos Wp=inv_lut_b_driver_2_pmos
.ENDS


******************************************************************************************
* LUT lut_b_driver_not subcircuit 
******************************************************************************************
.SUBCKT lut_b_driver_not n_in n_out n_vdd n_gnd
Xinv_lut_b_driver_not_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_lut_b_driver_not_1_nmos Wp=inv_lut_b_driver_not_1_pmos
Xwire_lut_b_driver_not n_1_1 n_1_2 wire Rw=wire_lut_b_driver_not_res Cw=wire_lut_b_driver_not_cap
Xinv_lut_b_driver_not_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_lut_b_driver_not_2_nmos Wp=inv_lut_b_driver_not_2_pmos
.ENDS


******************************************************************************************
* LUT lut_c_driver subcircuit 
******************************************************************************************
.SUBCKT lut_c_driver n_in n_out n_gate n_gate_n n_rsel n_not_input n_vdd n_gnd
Xinv_lut_c_driver_0 n_in n_1_1 n_vdd n_gnd inv Wn=inv_lut_c_driver_0_nmos Wp=inv_lut_c_driver_0_pmos
Xwire_lut_c_driver_0_rsel n_1_1 n_rsel wire Rw=wire_lut_c_driver_0_rsel_res Cw=wire_lut_c_driver_0_rsel_cap
Xwire_lut_c_driver_0_out n_1_1 n_1_2 wire Rw=wire_lut_c_driver_0_out_res Cw=wire_lut_c_driver_0_out_cap
Xptran_lut_c_driver_0 n_1_2 n_2_1 n_gate n_gnd ptran Wn=ptran_lut_c_driver_0_nmos
Xwire_lut_c_driver_0 n_2_1 n_2_2 wire Rw='wire_lut_c_driver_0_res/2' Cw='wire_lut_c_driver_0_cap/2'
Xwire_lut_c_driver_0h n_2_2 n_2_3 wire Rw='wire_lut_c_driver_0_res/2' Cw='wire_lut_c_driver_0_cap/2'
Xptran_lut_c_driver_0h n_gnd n_2_3 n_gate_n n_gnd ptran Wn=ptran_lut_c_driver_0_nmos
Xrest_lut_c_driver n_2_2 n_3_1 n_vdd n_gnd rest Wp=rest_lut_c_driver_pmos
Xinv_lut_c_driver_1 n_2_2 n_3_1 n_vdd n_gnd inv Wn=inv_lut_c_driver_1_nmos Wp=inv_lut_c_driver_1_pmos
Xwire_lut_c_driver n_3_1 n_not_input wire Rw=wire_lut_c_driver_res Cw=wire_lut_c_driver_cap
Xinv_lut_c_driver_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_lut_c_driver_2_nmos Wp=inv_lut_c_driver_2_pmos
.ENDS


******************************************************************************************
* LUT lut_c_driver_not subcircuit 
******************************************************************************************
.SUBCKT lut_c_driver_not n_in n_out n_vdd n_gnd
Xinv_lut_c_driver_not_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_lut_c_driver_not_1_nmos Wp=inv_lut_c_driver_not_1_pmos
Xwire_lut_c_driver_not n_1_1 n_1_2 wire Rw=wire_lut_c_driver_not_res Cw=wire_lut_c_driver_not_cap
Xinv_lut_c_driver_not_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_lut_c_driver_not_2_nmos Wp=inv_lut_c_driver_not_2_pmos
.ENDS


******************************************************************************************
* LUT lut_d_driver subcircuit 
******************************************************************************************
.SUBCKT lut_d_driver n_in n_out n_gate n_gate_n n_rsel n_not_input n_vdd n_gnd
Xwire_lut_d_driver n_in n_not_input wire Rw=wire_lut_d_driver_res Cw=wire_lut_d_driver_cap
Xinv_lut_d_driver_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_lut_d_driver_2_nmos Wp=inv_lut_d_driver_2_pmos
.ENDS


******************************************************************************************
* LUT lut_d_driver_not subcircuit 
******************************************************************************************
.SUBCKT lut_d_driver_not n_in n_out n_vdd n_gnd
Xinv_lut_d_driver_not_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_lut_d_driver_not_1_nmos Wp=inv_lut_d_driver_not_1_pmos
Xwire_lut_d_driver_not n_1_1 n_1_2 wire Rw=wire_lut_d_driver_not_res Cw=wire_lut_d_driver_not_cap
Xinv_lut_d_driver_not_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_lut_d_driver_not_2_nmos Wp=inv_lut_d_driver_not_2_pmos
.ENDS


******************************************************************************************
* LUT lut_e_driver subcircuit 
******************************************************************************************
.SUBCKT lut_e_driver n_in n_out n_gate n_gate_n n_rsel n_not_input n_vdd n_gnd
Xwire_lut_e_driver n_in n_not_input wire Rw=wire_lut_e_driver_res Cw=wire_lut_e_driver_cap
Xinv_lut_e_driver_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_lut_e_driver_2_nmos Wp=inv_lut_e_driver_2_pmos
.ENDS


******************************************************************************************
* LUT lut_e_driver_not subcircuit 
******************************************************************************************
.SUBCKT lut_e_driver_not n_in n_out n_vdd n_gnd
Xinv_lut_e_driver_not_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_lut_e_driver_not_1_nmos Wp=inv_lut_e_driver_not_1_pmos
Xwire_lut_e_driver_not n_1_1 n_1_2 wire Rw=wire_lut_e_driver_not_res Cw=wire_lut_e_driver_not_cap
Xinv_lut_e_driver_not_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_lut_e_driver_not_2_nmos Wp=inv_lut_e_driver_not_2_pmos
.ENDS


******************************************************************************************
* LUT lut_f_driver subcircuit 
******************************************************************************************
.SUBCKT lut_f_driver n_in n_out n_gate n_gate_n n_rsel n_not_input n_vdd n_gnd
Xwire_lut_f_driver n_in n_not_input wire Rw=wire_lut_f_driver_res Cw=wire_lut_f_driver_cap
Xinv_lut_f_driver_2 n_not_input n_out n_vdd n_gnd inv Wn=inv_lut_f_driver_2_nmos Wp=inv_lut_f_driver_2_pmos
.ENDS


******************************************************************************************
* LUT lut_f_driver_not subcircuit 
******************************************************************************************
.SUBCKT lut_f_driver_not n_in n_out n_vdd n_gnd
Xinv_lut_f_driver_not_1 n_in n_1_1 n_vdd n_gnd inv Wn=inv_lut_f_driver_not_1_nmos Wp=inv_lut_f_driver_not_1_pmos
Xwire_lut_f_driver_not n_1_1 n_1_2 wire Rw=wire_lut_f_driver_not_res Cw=wire_lut_f_driver_not_cap
Xinv_lut_f_driver_not_2 n_1_2 n_out n_vdd n_gnd inv Wn=inv_lut_f_driver_not_2_nmos Wp=inv_lut_f_driver_not_2_pmos
.ENDS


******************************************************************************************
* LUT a-input load subcircuit 
******************************************************************************************
.SUBCKT lut_a_driver_load n_1 n_vdd n_gnd
Xwire_lut_a_driver_load_1 n_1 n_2 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_1 n_gnd n_gnd n_2 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_2 n_2 n_3 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_2 n_gnd n_gnd n_3 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_3 n_3 n_4 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_3 n_gnd n_gnd n_4 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_4 n_4 n_5 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_4 n_gnd n_gnd n_5 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_5 n_5 n_6 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_5 n_gnd n_gnd n_6 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_6 n_6 n_7 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_6 n_gnd n_gnd n_7 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_7 n_7 n_8 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_7 n_gnd n_gnd n_8 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_8 n_8 n_9 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_8 n_gnd n_gnd n_9 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_9 n_9 n_10 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_9 n_gnd n_gnd n_10 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_10 n_10 n_11 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_10 n_gnd n_gnd n_11 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_11 n_11 n_12 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_11 n_gnd n_gnd n_12 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_12 n_12 n_13 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_12 n_gnd n_gnd n_13 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_13 n_13 n_14 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_13 n_gnd n_gnd n_14 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_14 n_14 n_15 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_14 n_gnd n_gnd n_15 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_15 n_15 n_16 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_15 n_gnd n_gnd n_16 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_16 n_16 n_17 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_16 n_gnd n_gnd n_17 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_17 n_17 n_18 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_17 n_gnd n_gnd n_18 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_18 n_18 n_19 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_18 n_gnd n_gnd n_19 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_19 n_19 n_20 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_19 n_gnd n_gnd n_20 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_20 n_20 n_21 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_20 n_gnd n_gnd n_21 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_21 n_21 n_22 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_21 n_gnd n_gnd n_22 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_22 n_22 n_23 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_22 n_gnd n_gnd n_23 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_23 n_23 n_24 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_23 n_gnd n_gnd n_24 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_24 n_24 n_25 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_24 n_gnd n_gnd n_25 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_25 n_25 n_26 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_25 n_gnd n_gnd n_26 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_26 n_26 n_27 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_26 n_gnd n_gnd n_27 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_27 n_27 n_28 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_27 n_gnd n_gnd n_28 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_28 n_28 n_29 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_28 n_gnd n_gnd n_29 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_29 n_29 n_30 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_29 n_gnd n_gnd n_30 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_30 n_30 n_31 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_30 n_gnd n_gnd n_31 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_31 n_31 n_32 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_31 n_gnd n_gnd n_32 n_gnd ptran Wn=ptran_lut_L1_nmos
Xwire_lut_a_driver_load_32 n_32 n_33 wire Rw='wire_lut_a_driver_load_res/32' Cw='wire_lut_a_driver_load_cap/32'
Xptran_lut_a_driver_load_32 n_gnd n_gnd n_33 n_gnd ptran Wn=ptran_lut_L1_nmos
.ENDS


******************************************************************************************
* LUT b-input load subcircuit 
******************************************************************************************
.SUBCKT lut_b_driver_load n_1 n_vdd n_gnd
Xwire_lut_b_driver_load_1 n_1 n_2 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_1 n_gnd n_gnd n_2 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_2 n_2 n_3 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_2 n_gnd n_gnd n_3 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_3 n_3 n_4 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_3 n_gnd n_gnd n_4 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_4 n_4 n_5 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_4 n_gnd n_gnd n_5 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_5 n_5 n_6 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_5 n_gnd n_gnd n_6 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_6 n_6 n_7 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_6 n_gnd n_gnd n_7 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_7 n_7 n_8 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_7 n_gnd n_gnd n_8 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_8 n_8 n_9 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_8 n_gnd n_gnd n_9 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_9 n_9 n_10 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_9 n_gnd n_gnd n_10 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_10 n_10 n_11 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_10 n_gnd n_gnd n_11 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_11 n_11 n_12 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_11 n_gnd n_gnd n_12 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_12 n_12 n_13 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_12 n_gnd n_gnd n_13 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_13 n_13 n_14 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_13 n_gnd n_gnd n_14 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_14 n_14 n_15 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_14 n_gnd n_gnd n_15 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_15 n_15 n_16 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_15 n_gnd n_gnd n_16 n_gnd ptran Wn=ptran_lut_L2_nmos
Xwire_lut_b_driver_load_16 n_16 n_17 wire Rw='wire_lut_b_driver_load_res/16' Cw='wire_lut_b_driver_load_cap/16'
Xptran_lut_b_driver_load_16 n_gnd n_gnd n_17 n_gnd ptran Wn=ptran_lut_L2_nmos
.ENDS


******************************************************************************************
* LUT c-input load subcircuit 
******************************************************************************************
.SUBCKT lut_c_driver_load n_1 n_vdd n_gnd
Xwire_lut_c_driver_load_1 n_1 n_2 wire Rw='wire_lut_c_driver_load_res/8' Cw='wire_lut_c_driver_load_cap/8'
Xptran_lut_c_driver_load_1 n_gnd n_gnd n_2 n_gnd ptran Wn=ptran_lut_L3_nmos
Xwire_lut_c_driver_load_2 n_2 n_3 wire Rw='wire_lut_c_driver_load_res/8' Cw='wire_lut_c_driver_load_cap/8'
Xptran_lut_c_driver_load_2 n_gnd n_gnd n_3 n_gnd ptran Wn=ptran_lut_L3_nmos
Xwire_lut_c_driver_load_3 n_3 n_4 wire Rw='wire_lut_c_driver_load_res/8' Cw='wire_lut_c_driver_load_cap/8'
Xptran_lut_c_driver_load_3 n_gnd n_gnd n_4 n_gnd ptran Wn=ptran_lut_L3_nmos
Xwire_lut_c_driver_load_4 n_4 n_5 wire Rw='wire_lut_c_driver_load_res/8' Cw='wire_lut_c_driver_load_cap/8'
Xptran_lut_c_driver_load_4 n_gnd n_gnd n_5 n_gnd ptran Wn=ptran_lut_L3_nmos
Xwire_lut_c_driver_load_5 n_5 n_6 wire Rw='wire_lut_c_driver_load_res/8' Cw='wire_lut_c_driver_load_cap/8'
Xptran_lut_c_driver_load_5 n_gnd n_gnd n_6 n_gnd ptran Wn=ptran_lut_L3_nmos
Xwire_lut_c_driver_load_6 n_6 n_7 wire Rw='wire_lut_c_driver_load_res/8' Cw='wire_lut_c_driver_load_cap/8'
Xptran_lut_c_driver_load_6 n_gnd n_gnd n_7 n_gnd ptran Wn=ptran_lut_L3_nmos
Xwire_lut_c_driver_load_7 n_7 n_8 wire Rw='wire_lut_c_driver_load_res/8' Cw='wire_lut_c_driver_load_cap/8'
Xptran_lut_c_driver_load_7 n_gnd n_gnd n_8 n_gnd ptran Wn=ptran_lut_L3_nmos
Xwire_lut_c_driver_load_8 n_8 n_9 wire Rw='wire_lut_c_driver_load_res/8' Cw='wire_lut_c_driver_load_cap/8'
Xptran_lut_c_driver_load_8 n_gnd n_gnd n_9 n_gnd ptran Wn=ptran_lut_L3_nmos
.ENDS


******************************************************************************************
* LUT d-input load subcircuit 
******************************************************************************************
.SUBCKT lut_d_driver_load n_1 n_vdd n_gnd
Xwire_lut_d_driver_load_1 n_1 n_2 wire Rw='wire_lut_d_driver_load_res/4' Cw='wire_lut_d_driver_load_cap/4'
Xptran_lut_d_driver_load_1 n_gnd n_gnd n_2 n_gnd ptran Wn=ptran_lut_L4_nmos
Xwire_lut_d_driver_load_2 n_2 n_3 wire Rw='wire_lut_d_driver_load_res/4' Cw='wire_lut_d_driver_load_cap/4'
Xptran_lut_d_driver_load_2 n_gnd n_gnd n_3 n_gnd ptran Wn=ptran_lut_L4_nmos
Xwire_lut_d_driver_load_3 n_3 n_4 wire Rw='wire_lut_d_driver_load_res/4' Cw='wire_lut_d_driver_load_cap/4'
Xptran_lut_d_driver_load_3 n_gnd n_gnd n_4 n_gnd ptran Wn=ptran_lut_L4_nmos
Xwire_lut_d_driver_load_4 n_4 n_5 wire Rw='wire_lut_d_driver_load_res/4' Cw='wire_lut_d_driver_load_cap/4'
Xptran_lut_d_driver_load_4 n_gnd n_gnd n_5 n_gnd ptran Wn=ptran_lut_L4_nmos
.ENDS


******************************************************************************************
* LUT e-input load subcircuit 
******************************************************************************************
.SUBCKT lut_e_driver_load n_1 n_vdd n_gnd
Xwire_lut_e_driver_load_1 n_1 n_2 wire Rw='wire_lut_e_driver_load_res/2' Cw='wire_lut_e_driver_load_cap/2'
Xptran_lut_e_driver_load_1 n_gnd n_gnd n_2 n_gnd ptran Wn=ptran_lut_L5_nmos
Xwire_lut_e_driver_load_2 n_2 n_3 wire Rw='wire_lut_e_driver_load_res/2' Cw='wire_lut_e_driver_load_cap/2'
Xptran_lut_e_driver_load_2 n_gnd n_gnd n_3 n_gnd ptran Wn=ptran_lut_L5_nmos
.ENDS


******************************************************************************************
* LUT f-input load subcircuit 
******************************************************************************************
.SUBCKT lut_f_driver_load n_1 n_vdd n_gnd
Xwire_lut_f_driver_load_1 n_1 n_2 wire Rw='wire_lut_f_driver_load_res/1' Cw='wire_lut_f_driver_load_cap/1'
Xptran_lut_f_driver_load_1 n_gnd n_gnd n_2 n_gnd ptran Wn=ptran_lut_L6_nmos
.ENDS


******************************************************************************************
* FF subcircuit 
******************************************************************************************
.SUBCKT ff n_in n_out n_gate n_gate_n n_clk n_clk_n n_set n_set_n n_reset n_reset_n n_vdd n_gnd
* Input selection MUX
Xptran_ff_input_select n_in n_1_1 n_gate n_gnd ptran Wn=ptran_ff_input_select_nmos
Xwire_ff_input_select n_1_1 n_1_2 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'
Xwire_ff_input_select_h n_1_2 n_1_3 wire Rw='wire_ff_input_select_res/2' Cw='wire_ff_input_select_cap/2'
Xptran_ff_input_select_h n_gnd n_1_3 n_gate_n n_gnd ptran Wn=ptran_ff_input_select_nmos
Xrest_ff_input_select n_1_2 n_2_1 n_vdd n_gnd rest Wp=rest_ff_input_select_pmos
Xinv_ff_input_1 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_ff_input_1_nmos Wp=inv_ff_input_1_pmos

* First T-gate and cross-coupled inverters
Xwire_ff_input_out n_2_1 n_2_2 wire Rw=wire_ff_input_out_res Cw=wire_ff_input_out_cap
Xtgate_ff_1 n_2_2 n_3_1 n_clk_n n_clk n_vdd n_gnd tgate Wn=tgate_ff_1_nmos Wp=tgate_ff_1_pmos
MPtran_ff_set_n n_3_1 n_set_n n_vdd n_vdd pmos L=gate_length W=tran_ff_set_n_pmos
MNtran_ff_reset n_3_1 n_reset n_gnd n_gnd nmos L=gate_length W=tran_ff_reset_nmos
Xwire_ff_tgate_1_out n_3_1 n_3_2 wire Rw=wire_ff_tgate_1_out_res Cw=wire_ff_tgate_1_out_cap
Xinv_ff_cc1_1 n_3_2 n_4_1 n_vdd n_gnd inv Wn=inv_ff_cc1_1_nmos Wp=inv_ff_cc1_1_pmos
Xinv_ff_cc1_2 n_4_1 n_3_2 n_vdd n_gnd inv Wn=inv_ff_cc1_2_nmos Wp=inv_ff_cc1_2_pmos
Xwire_ff_cc1_out n_4_1 n_4_2 wire Rw=wire_ff_cc1_out_res Cw=wire_ff_cc1_out_cap

* Second T-gate and cross-coupled inverters
Xtgate_ff_2 n_4_2 n_5_1 n_clk n_clk_n n_vdd n_gnd tgate Wn=tgate_ff_2_nmos Wp=tgate_ff_2_pmos
MPtran_ff_reset_n n_5_1 n_reset_n n_vdd n_vdd pmos L=gate_length W=tran_ff_reset_n_pmos
MNtran_ff_set n_5_1 n_set n_gnd n_gnd nmos L=gate_length W=tran_ff_set_nmos
Xwire_ff_tgate_2_out n_5_1 n_5_2 wire Rw=wire_ff_tgate_2_out_res Cw=wire_ff_tgate_2_out_cap
Xinv_ff_cc2_1 n_5_2 n_6_1 n_vdd n_gnd inv Wn=inv_ff_cc2_1_nmos Wp=inv_ff_cc2_1_pmos
Xinv_ff_cc2_2 n_6_1 n_5_2 n_vdd n_gnd inv Wn=inv_ff_cc2_2_nmos Wp=inv_ff_cc2_2_pmos
Xwire_ff_cc2_out n_6_1 n_6_2 wire Rw=wire_ff_cc2_out_res Cw=wire_ff_cc2_out_cap

* Output driver
Xinv_ff_output_driver n_6_2 n_out n_vdd n_gnd inv Wn=inv_ff_output_driver_nmos Wp=inv_ff_output_driver_pmos

.ENDS


******************************************************************************************
* local_ble_output subcircuit (2:1)
******************************************************************************************
.SUBCKT local_ble_output n_in n_out n_gate n_gate_n n_vdd n_gnd
Xptran_local_ble_output n_in n_1_1 n_gate n_gnd ptran Wn=ptran_local_ble_output_nmos
Xwire_local_ble_output n_1_1 n_1_2 wire Rw='wire_local_ble_output_res/2' Cw='wire_local_ble_output_cap/2'
Xwire_local_ble_output_h n_1_2 n_1_3 wire Rw='wire_local_ble_output_res/2' Cw='wire_local_ble_output_cap/2'
Xptran_local_ble_output_h n_gnd n_1_3 n_gnd n_gnd ptran Wn=ptran_local_ble_output_nmos
Xrest_local_ble_output n_1_2 n_2_1 n_vdd n_gnd rest Wp=rest_local_ble_output_pmos
Xinv_local_ble_output_1 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_local_ble_output_1_nmos Wp=inv_local_ble_output_1_pmos
Xwire_local_ble_output_driver n_2_1 n_2_2 wire Rw=wire_local_ble_output_driver_res Cw=wire_local_ble_output_driver_cap
Xinv_local_ble_output_2 n_2_2 n_out n_vdd n_gnd inv Wn=inv_local_ble_output_2_nmos Wp=inv_local_ble_output_2_pmos
.ENDS


******************************************************************************************
* general_ble_output subcircuit (2:1)
******************************************************************************************
.SUBCKT general_ble_output n_in n_out n_gate n_gate_n n_vdd n_gnd
Xptran_general_ble_output n_in n_1_1 n_gate n_gnd ptran Wn=ptran_general_ble_output_nmos
Xwire_general_ble_output n_1_1 n_1_2 wire Rw='wire_general_ble_output_res/2' Cw='wire_general_ble_output_cap/2'
Xwire_general_ble_output_h n_1_2 n_1_3 wire Rw='wire_general_ble_output_res/2' Cw='wire_general_ble_output_cap/2'
Xptran_general_ble_output_h n_gnd n_1_3 n_gnd n_gnd ptran Wn=ptran_general_ble_output_nmos
Xrest_general_ble_output n_1_2 n_2_1 n_vdd n_gnd rest Wp=rest_general_ble_output_pmos
Xinv_general_ble_output_1 n_1_2 n_2_1 n_vdd n_gnd inv Wn=inv_general_ble_output_1_nmos Wp=inv_general_ble_output_1_pmos
Xwire_general_ble_output_driver n_2_1 n_2_2 wire Rw=wire_general_ble_output_driver_res Cw=wire_general_ble_output_driver_cap
Xinv_general_ble_output_2 n_2_2 n_out n_vdd n_gnd inv Wn=inv_general_ble_output_2_nmos Wp=inv_general_ble_output_2_pmos
.ENDS


******************************************************************************************
* BLE outputs
******************************************************************************************
.SUBCKT ble_outputs n_1_3 n_local_out n_general_out n_gate n_gate_n n_vdd n_gnd n_vdd_local_output_on n_vdd_general_output_on
Xlocal_ble_output_1 n_1_2 n_local_out n_gate n_gate_n n_vdd_local_output_on n_gnd local_ble_output
Xwire_ble_outputs_1 n_1_2 n_1_3 wire Rw='wire_ble_outputs_res/2' Cw='wire_ble_outputs_cap/2'
Xgeneral_ble_output_1 n_1_3 n_general_out n_gate n_gate_n n_vdd_general_output_on n_gnd general_ble_output
Xwire_ble_outputs_2 n_1_3 n_1_4 wire Rw='wire_ble_outputs_res/2' Cw='wire_ble_outputs_cap/2'
Xgeneral_ble_output_2 n_1_4 n_hang_4 n_gate n_gate_n n_vdd n_gnd general_ble_output
.ENDS


******************************************************************************************
* LUT output load
******************************************************************************************
.SUBCKT lut_output_load n_in n_local_out n_general_out n_gate n_gate_n n_vdd n_gnd n_vdd_local_output_on n_vdd_general_output_on
Xwire_lut_output_load_1 n_in n_1_1 wire Rw='wire_lut_output_load_1_res' Cw='wire_lut_output_load_1_cap'
Xff n_1_1 n_hang1 n_gate n_gate_n n_vdd n_gnd n_gnd n_vdd n_gnd n_vdd n_vdd n_gnd ff
Xwire_lut_output_load_2 n_1_1 n_1_2 wire Rw='wire_lut_output_load_2_res' Cw='wire_lut_output_load_2_cap'
Xble_outputs n_1_2 n_local_out n_general_out n_gate n_gate_n n_vdd n_gnd n_vdd_local_output_on n_vdd_general_output_on ble_outputs
.ENDS


******************************************************************************************
* local_mux sense inverter subcircuit (25:1)
******************************************************************************************
.SUBCKT local_mux_sense n_in n_out n_vdd n_gnd
Xrest_local_mux n_in n_out n_vdd n_gnd rest Wp=rest_local_mux_pmos
Xinv_local_mux_1 n_in n_out n_vdd n_gnd inv Wn=inv_local_mux_1_nmos Wp=inv_local_mux_1_pmos
.ENDS


******************************************************************************************
* local_mux subcircuit (25:1), turned off 
******************************************************************************************
.SUBCKT local_mux_off n_in n_gate n_gate_n n_vdd n_gnd
Xptran_local_mux_L1 n_in n_gnd n_gnd n_gnd ptran Wn=ptran_local_mux_L1_nmos
.ENDS


******************************************************************************************
* local_mux subcircuit (25:1), partially turned on
******************************************************************************************
.SUBCKT local_mux_partial n_in n_gate n_gate_n n_vdd n_gnd
Xptran_local_mux_L1 n_in n_1 n_gate n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_1 n_1 n_1_1 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L1_1h n_gnd n_1_1 n_gnd n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_2 n_1_1 n_1_2 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L1_2h n_gnd n_1_2 n_gnd n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_3 n_1_2 n_1_3 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L1_3h n_gnd n_1_3 n_gnd n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_4 n_1_3 n_1_4 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L1_4h n_gnd n_1_4 n_gnd n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_5 n_1_4 n_1_5 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L2 n_1_5 n_gnd n_gnd n_gnd ptran Wn=ptran_local_mux_L2_nmos
.ENDS


******************************************************************************************
* local_mux subcircuit (25:1), fully turned on (mux only)
******************************************************************************************
.SUBCKT local_mux_on_mux_only n_in n_out n_gate n_gate_n n_vdd n_gnd
Xptran_local_mux_L1 n_in n_1 n_gate n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_1 n_1 n_1_1 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L1_1h n_gnd n_1_1 n_gnd n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_2 n_1_1 n_1_2 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L1_2h n_gnd n_1_2 n_gnd n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_3 n_1_2 n_1_3 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L1_3h n_gnd n_1_3 n_gnd n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_4 n_1_3 n_1_4 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L1_4h n_gnd n_1_4 n_gnd n_gnd ptran Wn=ptran_local_mux_L1_nmos
Xwire_local_mux_L1_5 n_1_4 n_1_5 wire Rw='wire_local_mux_L1_res/5' Cw='wire_local_mux_L1_cap/5'
Xptran_local_mux_L2 n_1_5 n_2 n_gate n_gnd ptran Wn=ptran_local_mux_L2_nmos
Xwire_local_mux_L2_1 n_2 n_2_1 wire Rw='wire_local_mux_L2_res/4' Cw='wire_local_mux_L2_cap/4'
Xptran_local_mux_L2_1h n_gnd n_2_1 n_gnd n_gnd ptran Wn=ptran_local_mux_L2_nmos
Xwire_local_mux_L2_2 n_2_1 n_out wire Rw='wire_local_mux_L2_res/4' Cw='wire_local_mux_L2_cap/4'
Xptran_local_mux_L2_2h n_gnd n_out n_gnd n_gnd ptran Wn=ptran_local_mux_L2_nmos
Xwire_local_mux_L2_3  n_out n_2_2 wire Rw='wire_local_mux_L2_res/4' Cw='wire_local_mux_L2_cap/4'
Xptran_local_mux_L2_3h n_gnd n_2_2 n_gnd n_gnd ptran Wn=ptran_local_mux_L2_nmos
Xwire_local_mux_L2_4 n_2_2 n_2_3 wire Rw='wire_local_mux_L2_res/4' Cw='wire_local_mux_L2_cap/4'
Xptran_local_mux_L2_4h n_gnd n_2_3 n_gnd n_gnd ptran Wn=ptran_local_mux_L2_nmos
.ENDS


******************************************************************************************
* local_mux subcircuit (25:1), fully turned on 
******************************************************************************************
.SUBCKT local_mux_on n_in n_out n_gate n_gate_n n_vdd n_gnd
Xlocal_mux_on_mux_only n_in n_1_1 n_gate n_gate_n n_vdd n_gnd local_mux_on_mux_only
Xlocal_mux_sense n_1_1 n_out n_vdd n_gnd local_mux_sense
.ENDS


******************************************************************************************
* Local routing wire load
******************************************************************************************
.SUBCKT local_routing_wire_load n_in n_out n_gate n_gate_n n_vdd n_gnd n_vdd_local_mux_on
Xwire_local_routing_1 n_in n_1 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_1 n_1 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_2 n_1 n_2 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_2 n_2 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_3 n_2 n_3 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_3 n_3 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_4 n_3 n_4 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_4 n_4 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_5 n_4 n_5 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_5 n_5 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_6 n_5 n_6 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_6 n_6 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_7 n_6 n_7 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_partial_1 n_7 n_gate n_gate_n n_vdd n_gnd local_mux_partial
Xwire_local_routing_8 n_7 n_8 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_7 n_8 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_9 n_8 n_9 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_8 n_9 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_10 n_9 n_10 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_9 n_10 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_11 n_10 n_11 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_10 n_11 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_12 n_11 n_12 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_11 n_12 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_13 n_12 n_13 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_12 n_13 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_14 n_13 n_14 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_partial_2 n_14 n_gate n_gate_n n_vdd n_gnd local_mux_partial
Xwire_local_routing_15 n_14 n_15 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_13 n_15 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_16 n_15 n_16 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_14 n_16 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_17 n_16 n_17 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_15 n_17 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_18 n_17 n_18 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_16 n_18 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_19 n_18 n_19 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_17 n_19 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_20 n_19 n_20 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_18 n_20 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_21 n_20 n_21 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_partial_3 n_21 n_gate n_gate_n n_vdd n_gnd local_mux_partial
Xwire_local_routing_22 n_21 n_22 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_19 n_22 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_23 n_22 n_23 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_20 n_23 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_24 n_23 n_24 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_21 n_24 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_25 n_24 n_25 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_22 n_25 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_26 n_25 n_26 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_23 n_26 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_27 n_26 n_27 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_24 n_27 n_gate n_gate_n n_vdd n_gnd local_mux_off
Xwire_local_routing_28 n_27 n_28 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_partial_4 n_28 n_gate n_gate_n n_vdd n_gnd local_mux_partial
Xwire_local_routing_29 n_28 n_29 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_on_1 n_29 n_out n_gate n_gate_n n_vdd_local_mux_on n_gnd local_mux_on
Xwire_local_routing_30 n_29 n_30 wire Rw='wire_local_routing_res/30' Cw='wire_local_routing_cap/30'
Xlocal_mux_off_25 n_30 n_gate n_gate_n n_vdd n_gnd local_mux_off
.ENDS


******************************************************************************************
* Local BLE output load
******************************************************************************************
.SUBCKT local_ble_output_load n_in n_gate n_gate_n n_vdd n_gnd
Xwire_local_ble_output_feedback n_in n_1_1 wire Rw='wire_local_ble_output_feedback_res' Cw='wire_local_ble_output_feedback_cap'
Xlocal_routing_wire_load_1 n_1_1 n_1_2 n_gate n_gate_n n_vdd n_gnd n_vdd local_routing_wire_load
Xlut_a_driver_1 n_1_2 n_hang1 vsram vsram_n n_hang2 n_hang3 n_vdd n_gnd lut_a_driver

.ENDS


******************************************************************************************
* General BLE output load
******************************************************************************************
.SUBCKT general_ble_output_load n_1_1 n_out n_gate n_gate_n n_vdd n_gnd
Xwire_general_ble_output_1 n_1_1 n_1_2 wire Rw='wire_general_ble_output_res/8' Cw='wire_general_ble_output_cap/8'
Xsb_mux_off_1 n_1_2 n_gate n_gate_n n_vdd n_gnd sb_mux_off
Xwire_general_ble_output_2 n_1_2 n_1_3 wire Rw='wire_general_ble_output_res/8' Cw='wire_general_ble_output_cap/8'
Xsb_mux_off_2 n_1_3 n_gate n_gate_n n_vdd n_gnd sb_mux_off
Xwire_general_ble_output_3 n_1_3 n_1_4 wire Rw='wire_general_ble_output_res/8' Cw='wire_general_ble_output_cap/8'
Xsb_mux_off_3 n_1_4 n_gate n_gate_n n_vdd n_gnd sb_mux_off
Xwire_general_ble_output_4 n_1_4 n_1_5 wire Rw='wire_general_ble_output_res/8' Cw='wire_general_ble_output_cap/8'
Xsb_mux_off_4 n_1_5 n_gate n_gate_n n_vdd n_gnd sb_mux_off
Xwire_general_ble_output_5 n_1_5 n_1_6 wire Rw='wire_general_ble_output_res/8' Cw='wire_general_ble_output_cap/8'
Xsb_mux_off_5 n_1_6 n_gate n_gate_n n_vdd n_gnd sb_mux_off
Xwire_general_ble_output_6 n_1_6 n_1_7 wire Rw='wire_general_ble_output_res/8' Cw='wire_general_ble_output_cap/8'
Xsb_mux_off_6 n_1_7 n_gate n_gate_n n_vdd n_gnd sb_mux_off
Xwire_general_ble_output_7 n_1_7 n_1_8 wire Rw='wire_general_ble_output_res/8' Cw='wire_general_ble_output_cap/8'
Xsb_mux_partial_1 n_1_8 n_gate n_gate_n n_vdd n_gnd sb_mux_partial
Xwire_general_ble_output_8 n_1_8 n_meas_point wire Rw='wire_general_ble_output_res/8' Cw='wire_general_ble_output_cap/8'
Xsb_mux_on_1 n_meas_point n_out n_gate n_gate_n n_vdd n_gnd sb_mux_on
.ENDS


******************************************************************************************
* Routing wire load tile 1
******************************************************************************************
.SUBCKT routing_wire_load_tile_1 n_in n_out n_cb_out n_gate n_gate_n n_vdd n_gnd n_vdd_sb_mux_on n_vdd_cb_mux_on
Xwire_gen_routing_1 n_in n_1_1 wire Rw='wire_gen_routing_res/8' Cw='wire_gen_routing_cap/8'

Xwire_sb_load_partial_1 n_1_1 n_1_sb_partial_1 wire Rw=wire_sb_load_partial_res Cw=wire_sb_load_partial_cap
Xsb_load_partial_1 n_1_sb_partial_1 n_gate n_gate_n n_vdd n_gnd sb_mux_partial

Xwire_sb_load_off_1 n_1_1 n_1_sb_off_1 wire Rw=wire_sb_load_off_res Cw=wire_sb_load_off_cap
Xsb_load_off_1 n_1_sb_off_1 n_gate n_gate_n n_vdd n_gnd sb_mux_off

Xwire_cb_load_on_1 n_1_1 n_1_cb_on_1 wire Rw=wire_cb_load_on_res Cw=wire_cb_load_on_cap
Xcb_load_on_1 n_1_cb_on_1 n_cb_out n_gate n_gate_n n_vdd_cb_mux_on n_gnd cb_mux_on

Xwire_cb_load_partial_1 n_1_1 n_1_cb_partial_1 wire Rw=wire_cb_load_partial_res Cw=wire_cb_load_partial_cap
Xcb_load_partial_1 n_1_cb_partial_1 n_gate n_gate_n n_vdd n_gnd cb_mux_partial

Xwire_cb_load_off_1 n_1_1 n_1_cb_off_1 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_1 n_1_cb_off_1 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_2 n_1_1 n_1_cb_off_2 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_2 n_1_cb_off_2 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_gen_routing_2 n_1_1 n_1_2 wire Rw='wire_gen_routing_res/8' Cw='wire_gen_routing_cap/8'
Xsb_mux_on_out n_1_2 n_out n_gate n_gate_n n_vdd_sb_mux_on n_gnd sb_mux_on
.ENDS


******************************************************************************************
* Routing wire load tile 2
******************************************************************************************
.SUBCKT routing_wire_load_tile_2 n_in n_out n_cb_out n_gate n_gate_n n_vdd n_gnd
Xwire_gen_routing_1 n_in n_1_1 wire Rw='wire_gen_routing_res/8' Cw='wire_gen_routing_cap/8'

Xwire_sb_load_off_1 n_1_1 n_1_sb_off_1 wire Rw=wire_sb_load_off_res Cw=wire_sb_load_off_cap
Xsb_load_off_1 n_1_sb_off_1 n_gate n_gate_n n_vdd n_gnd sb_mux_off

Xwire_sb_load_off_2 n_1_1 n_1_sb_off_2 wire Rw=wire_sb_load_off_res Cw=wire_sb_load_off_cap
Xsb_load_off_2 n_1_sb_off_2 n_gate n_gate_n n_vdd n_gnd sb_mux_off

Xwire_cb_load_off_1 n_1_1 n_1_cb_off_1 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_1 n_1_cb_off_1 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_2 n_1_1 n_1_cb_off_2 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_2 n_1_cb_off_2 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_3 n_1_1 n_1_cb_off_3 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_3 n_1_cb_off_3 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_4 n_1_1 n_1_cb_off_4 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_4 n_1_cb_off_4 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_gen_routing_2 n_1_1 n_out wire Rw='wire_gen_routing_res/8' Cw='wire_gen_routing_cap/8'
.ENDS


******************************************************************************************
* Routing wire load tile 3
******************************************************************************************
.SUBCKT routing_wire_load_tile_3 n_in n_out n_cb_out n_gate n_gate_n n_vdd n_gnd
Xwire_gen_routing_1 n_in n_1_1 wire Rw='wire_gen_routing_res/8' Cw='wire_gen_routing_cap/8'

Xwire_sb_load_off_1 n_1_1 n_1_sb_off_1 wire Rw=wire_sb_load_off_res Cw=wire_sb_load_off_cap
Xsb_load_off_1 n_1_sb_off_1 n_gate n_gate_n n_vdd n_gnd sb_mux_off

Xwire_sb_load_off_2 n_1_1 n_1_sb_off_2 wire Rw=wire_sb_load_off_res Cw=wire_sb_load_off_cap
Xsb_load_off_2 n_1_sb_off_2 n_gate n_gate_n n_vdd n_gnd sb_mux_off

Xwire_cb_load_off_1 n_1_1 n_1_cb_off_1 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_1 n_1_cb_off_1 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_2 n_1_1 n_1_cb_off_2 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_2 n_1_cb_off_2 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_3 n_1_1 n_1_cb_off_3 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_3 n_1_cb_off_3 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_4 n_1_1 n_1_cb_off_4 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_4 n_1_cb_off_4 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_gen_routing_2 n_1_1 n_out wire Rw='wire_gen_routing_res/8' Cw='wire_gen_routing_cap/8'
.ENDS


******************************************************************************************
* Routing wire load tile 4
******************************************************************************************
.SUBCKT routing_wire_load_tile_4 n_in n_out n_cb_out n_gate n_gate_n n_vdd n_gnd
Xwire_gen_routing_1 n_in n_1_1 wire Rw='wire_gen_routing_res/8' Cw='wire_gen_routing_cap/8'

Xwire_sb_load_off_1 n_1_1 n_1_sb_off_1 wire Rw=wire_sb_load_off_res Cw=wire_sb_load_off_cap
Xsb_load_off_1 n_1_sb_off_1 n_gate n_gate_n n_vdd n_gnd sb_mux_off

Xwire_sb_load_off_2 n_1_1 n_1_sb_off_2 wire Rw=wire_sb_load_off_res Cw=wire_sb_load_off_cap
Xsb_load_off_2 n_1_sb_off_2 n_gate n_gate_n n_vdd n_gnd sb_mux_off

Xwire_cb_load_off_1 n_1_1 n_1_cb_off_1 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_1 n_1_cb_off_1 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_2 n_1_1 n_1_cb_off_2 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_2 n_1_cb_off_2 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_3 n_1_1 n_1_cb_off_3 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_3 n_1_cb_off_3 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_cb_load_off_4 n_1_1 n_1_cb_off_4 wire Rw=wire_cb_load_off_res Cw=wire_cb_load_off_cap
Xcb_load_off_4 n_1_cb_off_4 n_gate n_gate_n n_vdd n_gnd cb_mux_off

Xwire_gen_routing_2 n_1_1 n_out wire Rw='wire_gen_routing_res/8' Cw='wire_gen_routing_cap/8'
.ENDS


******************************************************************************************
* Routing wire load tile 4
******************************************************************************************
.SUBCKT routing_wire_load n_in n_out n_cb_out n_gate n_gate_n n_vdd n_gnd n_vdd_sb_mux_on n_vdd_cb_mux_on
Xrouting_wire_load_tile_4 n_in n_4 n_hang_4 n_gate n_gate_n n_vdd n_gnd routing_wire_load_tile_4
Xrouting_wire_load_tile_3 n_4 n_3 n_hang_3 n_gate n_gate_n n_vdd n_gnd routing_wire_load_tile_3
Xrouting_wire_load_tile_2 n_3 n_2 n_hang_2 n_gate n_gate_n n_vdd n_gnd routing_wire_load_tile_2
Xrouting_wire_load_tile_1 n_2 n_out n_cb_out n_gate n_gate_n n_vdd n_gnd n_vdd_sb_mux_on n_vdd_cb_mux_on routing_wire_load_tile_1
.ENDS


.ENDL SUBCIRCUITS