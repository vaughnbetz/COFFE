*** BASIC SUBCIRCUITS

.LIB BASIC_SUBCIRCUITS

******************************************************************************************
* Interconnect wire
******************************************************************************************
.SUBCKT wire n_in n_out Rw=1 Cw=1
CWIRE_1 n_in gnd Cw
RWIRE_1 n_in n_out Rw
CWIRE_2 n_out gnd Cw
.ENDS


******************************************************************************************
* Pass-transistor
******************************************************************************************
.SUBCKT ptran n_in n_out n_gate n_gnd Wn=45n 
MNPASS n_in n_gate n_out n_gnd nmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
.ENDS


******************************************************************************************
* PMOS Pass-transistor
******************************************************************************************
.SUBCKT ptranp n_in n_out n_gate n_vdd Wn=45n 
MPPASS n_in n_gate n_out n_vdd pmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
.ENDS


******************************************************************************************
* Transmission gate
******************************************************************************************
.SUBCKT tgate n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=45n Wp=45n
MNTGATE n_in n_gate_nmos n_out n_gnd nmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPTGATE n_in n_gate_pmos n_out n_vdd pmos L=gate_length W=Wp AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length
.ENDS


******************************************************************************************
* Transmission gate
******************************************************************************************
.SUBCKT tgate_lp n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=45n Wp=45n
MNTGATE n_in n_gate_nmos n_out n_gnd nmos_lp L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPTGATE n_in n_gate_pmos n_out n_vdd pmos_lp L=gate_length W=Wp AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length
.ENDS


******************************************************************************************
* Level-restorer PMOS
******************************************************************************************
.SUBCKT rest n_pull n_gate n_vdd n_gnd Wp=45n
MPREST n_pull n_gate n_vdd n_vdd pmos L=gate_length*rest_length_factor W=Wp AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length
.ENDS


******************************************************************************************
* Inverter
******************************************************************************************
.SUBCKT inv n_in n_out n_vdd n_gnd Wn=45n Wp=45n
MNDOWN n_out n_in n_gnd n_gnd nmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP n_out n_in n_vdd n_vdd pmos L=gate_length W=Wp AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length
.ENDS


******************************************************************************************
* Low Power Inverter
******************************************************************************************
.SUBCKT inv_lp n_in n_out n_vdd n_gnd Wn=45n Wp=45n
MNDOWN n_out n_in n_gnd n_gnd nmos_lp L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP n_out n_in n_vdd n_vdd pmos_lp L=gate_length W=Wp AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length
.ENDS


******************************************************************************************
* nand2
******************************************************************************************
.SUBCKT nand2 n_in n_out n_vdd n_gnd Wn=45n Wp=45n
MNDOWN2 n_out n_vdd n_z n_gnd nmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MNDOWN1 n_z n_in n_gnd n_gnd nmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP1 n_out n_vdd n_vdd n_vdd pmos L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP2 n_out n_in n_vdd n_vdd pmos L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
.ENDS


******************************************************************************************
* nand2
******************************************************************************************
.SUBCKT nand2_lp n_in n_out n_vdd n_gnd Wn=45n Wp=45n
MNDOWN2 n_out n_vdd n_z n_gnd nmos_lp L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MNDOWN1 n_z n_in n_gnd n_gnd nmos_lp L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP1 n_out n_vdd n_vdd n_vdd pmos_lp L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP2 n_out n_in n_vdd n_vdd pmos_lp L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
.ENDS


******************************************************************************************
* nand3
******************************************************************************************
.SUBCKT nand3 n_in n_out n_vdd n_gnd Wn=45n Wp=45n
MNDOWN2 n_out n_vdd n_z n_gnd nmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MNDOWN1 n_z n_vdd n_z2 n_gnd nmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MNDOWN0 n_z2 n_in n_gnd n_gnd nmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP0 n_out n_vdd n_vdd n_vdd pmos L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP1 n_out n_vdd n_vdd n_vdd pmos L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP2 n_out n_in n_vdd n_vdd pmos L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
.ENDS


******************************************************************************************
* nand3
******************************************************************************************
.SUBCKT nand3_lp n_in n_out n_vdd n_gnd Wn=45n Wp=45n
MNDOWN2 n_out n_vdd n_z n_gnd nmos_lp L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MNDOWN1 n_z n_vdd n_z2 n_gnd nmos_lp L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MNDOWN0 n_z2 n_in n_gnd n_gnd nmos_lp L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP0 n_out n_vdd n_vdd n_vdd pmos_lp L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP1 n_out n_vdd n_vdd n_vdd pmos_lp L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPUP2 n_out n_in n_vdd n_vdd pmos_lp L=gate_length W=Wp AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
.ENDS


******************************************************************************************
* Transmission gate
******************************************************************************************
.SUBCKT RAM_tgate n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=200n Wp=250n
MNTGATE n_in n_gate_nmos n_out n_gnd nmos L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPTGATE n_in n_gate_pmos n_out n_vdd pmos L=gate_length W=Wp AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length
.ENDS


******************************************************************************************
* Transmission gate
******************************************************************************************
.SUBCKT RAM_tgate_lp n_in n_out n_gate_nmos n_gate_pmos n_vdd n_gnd Wn=200n Wp=250n
MNTGATE n_in n_gate_nmos n_out n_gnd nmos_lp L=gate_length W=Wn AS=Wn*trans_diffusion_length AD=Wn*trans_diffusion_length PS=Wn+2*trans_diffusion_length PD=Wn+2*trans_diffusion_length
MPTGATE n_in n_gate_pmos n_out n_vdd pmos_lp L=gate_length W=Wp AS=Wp*trans_diffusion_length AD=Wp*trans_diffusion_length PS=Wp+2*trans_diffusion_length PD=Wp+2*trans_diffusion_length
.ENDS


.ENDL BASIC_SUBCIRCUITS