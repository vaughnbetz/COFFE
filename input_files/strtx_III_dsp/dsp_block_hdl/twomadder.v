//Two multipliers and adder

module two_multipliers_one_adder(
A0,
A1,
B0,
B1,
clk,
reset,
mode_0,
mode_1,
P
);

input [17:0] A0;
input [17:0] A1;
input [17:0] B0;
input [17:0] B1;
input clk;
input reset;
input mode_0;
input mode_1;
output [71:0] P;


reg [17:0] A0_registered;
reg [17:0] B0_registered;
reg [17:0] A1_registered;
reg [17:0] B1_registered;

wire [35:0] A0xB0;
wire [35:0] A1xB1;
wire [36:0] tempsum;

reg [71:0] moutput;

always @(posedge clk)
if (reset) begin
    A0_registered <= 18'b0;
    A1_registered <= 18'b0;
    B0_registered <= 18'b0;
    B1_registered <= 18'b0;
	moutput <= 72'b0;
	
    end else begin
    A0_registered <= A0;
    A1_registered <= A1;
    B0_registered <= B0;
    B1_registered <= B1;
	if (mode_0 == 1'b0 && mode_1 ==1'b0) begin
	moutput <= {35'd0, tempsum};
	end else if (mode_0 == 1'b1 && mode_1 ==1'b0) begin
	moutput <= {A0xB0, A1xB1};
	end else begin
	moutput <= {36'd0, A0xB0};
	end
end

assign A0xB0 = A0_registered * B0_registered;
assign A1xB1 = A1_registered * B1_registered;
assign P = moutput;
assign tempsum = A0xB0 + A1xB1;

endmodule
