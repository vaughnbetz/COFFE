//Two multipliers and adder

module accumulate(
A0,
B0,
C0,
clk,
add_previous,
reset,
mode_0,
S
);

input [71:0] A0;
input [71:0] B0;
input [43:0] C0;
input clk;
input reset;
input add_previous;
input mode_0;
output [143:0] S;


wire [37:0] A0pB0;
wire [43:0] accumulated;
reg [37:0] A0pB0_reg;
reg [143:0] S_temp;

always @(posedge clk)
if (reset) begin
    A0pB0_reg <= 38'b0;
	S_temp <= 144'b0;
    end else begin
    A0pB0_reg <= A0pB0;
	if (mode_0) begin
	S_temp <= {A0[71:0],B0[71:0]};
	end else if (add_previous) begin
    S_temp <= { accumulated , 100'd0};
    end else begin
    S_temp <= {A0pB0_reg, 100'd0};
    end
    
end


assign A0pB0 = A0[35:0] + B0[35:0];
assign accumulated = A0pB0_reg + C0;
assign S = S_temp;

endmodule
