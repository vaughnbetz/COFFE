module half_dsp (
A0,
A1,
B0,
B1,
C0,
C1,
D0,
D1,
mode_0,
mode_1,
from_previous,
add_previous,
clk,
reset,
result
);

input [17:0] A0;
input [17:0] A1;
input [17:0] B0;
input [17:0] B1;
input [17:0] C0;
input [17:0] C1;
input [17:0] D0;
input [17:0] D1;
input [43:0] from_previous;
input clk;
input reset;
input mode_0;
input mode_1;
input add_previous;

output [143:0] result;

wire [71:0] partial_0;
wire [71:0] partial_1;
wire [143:0] the_output;

two_multipliers_one_adder m0(
.A0 (A0),
.A1 (A1),
.B0 (B0),
.B1 (B1),
.clk (clk),
.mode_0 (mode_0),
.mode_1 (mode_1),
.reset (reset),
.P (partial_0)
);


two_multipliers_one_adder m1(
.A0 (C0),
.A1 (C1),
.B0 (D0),
.B1 (D1),
.clk (clk),
.mode_0 (mode_0),
.mode_1 (mode_1),
.reset (reset),
.P (partial_1)
);


accumulate m2(
.A0 (partial_0),
.B0 (partial_1),
.C0 (from_previous),
.add_previous (add_previous),
.S (the_output),
.clk (clk),
.mode_0 (mode_0),
.reset (reset)
);

assign result = the_output;

endmodule