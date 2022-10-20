module dsp (
A0,
A1,
B0,
B1,
C0,
C1,
D0,
D1,
E0,
E1,
F0,
F1,
G0,
G1,
H0,
H1,
from_previous,
add_previous,
clk,
mode_0,
mode_1,
reset,
result0,
result1
);

input [17:0] A0;
input [17:0] A1;
input [17:0] B0;
input [17:0] B1;
input [17:0] C0;
input [17:0] C1;
input [17:0] D0;
input [17:0] D1;
input [17:0] E0;
input [17:0] E1;
input [17:0] F0;
input [17:0] F1;
input [17:0] G0;
input [17:0] G1;
input [17:0] H0;
input [17:0] H1;
input [43:0] from_previous;
input clk;
input reset;
input mode_0;
input mode_1;
input add_previous;

output [143:0] result0;
output [143:0] result1;

wire [143:0] the_output0;
wire [143:0] the_output1;

half_dsp m0(
.A0 (A0),
.A1 (A1),
.B0 (B0),
.B1 (B1),
.C0 (C0),
.C1 (C1),
.D0 (D0),
.D1 (D1),
.mode_0 (mode_0),
.mode_1 (mode_1),
.from_previous (from_previous),
.add_previous (add_previous),
.clk (clk),
.reset (reset),
.result (the_output0)
);


half_dsp m1(
.A0 (E0),
.A1 (E1),
.B0 (F0),
.B1 (F1),
.C0 (G0),
.C1 (G1),
.D0 (H0),
.D1 (H1),
.mode_0 (mode_0),
.mode_1 (mode_1),
.from_previous (the_output0[71:28]),
.add_previous (add_previous),
.clk (clk),
.reset (reset),
.result (the_output1)
);


assign result0 = the_output0;
assign result1 = the_output1;

endmodule