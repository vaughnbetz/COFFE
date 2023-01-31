/* ======================================================
 *   Title: Fracturable DSP (int27, int18, int9, int4)
 *   Author: Andrew Boutros
 *   Affiliation: University of Toronto
 * ====================================================== */


module FMULT (
	input  clk,
	input  [17:0] data_x1,
	input  [17:0] data_y1,
	input	 [17:0] data_z1,
	input  [2:0]  coef_s1,
	input  [17:0] data_x2,
	input  [17:0] data_y2,
	input  [17:0] data_z2,
	input  [2:0]  coef_s2,
	input	 [17:0] data_scanin,
	input	 [63:0] data_chainin,
	input  signed_c1,
	input  signed_c2,
	input  [1:0] mode_ctrl,
	input  sop_ctrl,
	input	 load_bias_ctrl,
	input  chainin_en_ctrl,
	input  accum_ctrl,
	input	 coeff_en1_ctrl,
	input	 coeff_en2_ctrl,
	input  scanin_en1_ctrl,
	input  scanin_en2_ctrl,
	input  preadd_en1_ctrl,
	input  preadd_en2_ctrl,
	output [71:0] result,
	output [17:0] data_scanout,
	output [63:0] data_chainout
);

reg [17:0] d_x1, d_x2, d_y1, d_y2;
reg [17:0] d_z1, d_z2; 
reg [17:0] scanin_delay1, scanin_delay2;
reg [2:0] coeff_sel1, coeff_sel2; 
reg sign1, sign2, sop, load_bias, accum, coeff_en1, coeff_en2, preadd_en1, preadd_en2;
reg [4:0] mode;
reg [63:0] load_const = 64'd7;
reg [63:0] chainin;
reg [63:0] accum_reg;
reg [71:0] result_reg;

wire [53:0] K2_sum, K2_carry;
wire [53:0] K5_sum, K5_carry;
reg [53:0] K6_sum, K6_carry;

wire [53:0] S2_sum, S2_carry;
wire [26:0] K1_sum, K1_carry;
wire [35:0] M1_sum, M1_carry, S1_sum, S1_carry;
wire [26:0] M2_sum, M2_carry, M3_sum, M3_carry;
wire [17:0] M4_sum, M4_carry;
wire [63:0] K3_sum, K3_carry;
wire [8:0] K4_sum, K4_carry;
wire [7:0] M6_sum, M6_carry, M8_sum, M8_carry;

wire [71:0] CPA_result;

reg [17:0] x1, x2;
wire [17:0] y1, y2;
wire [17:0] coeff1, coeff2;
wire c1_temp, c2_temp, c3_temp, c4_temp, c5_temp;

reg [15:0] temp_1, temp_2;

always @ (posedge clk)
begin
	d_x1 <= data_x1;
	d_y1 <= (scanin_en1_ctrl)? data_scanin: data_y1;
	d_z1 <= data_z1;
	coeff_sel1 <= coef_s1;
	d_x2 <= data_x2;
	d_y2 <= (scanin_en2_ctrl)? scanin_delay1: data_y2;
	d_z2 <= data_z2;
	coeff_sel2 <= coef_s2;
	chainin <= (chainin_en_ctrl)? data_chainin: 64'd0;
	scanin_delay1 <= d_y1;
	scanin_delay2 <= d_y2;
	
	sign1 <= signed_c1;
	sign2 <= signed_c2;
	mode[1:0] <= mode_ctrl;
	mode[2] <= ~mode_ctrl[0] & mode_ctrl[1] & sop_ctrl;
	mode[3] <=  mode_ctrl[0] & mode_ctrl[1];
	mode[4] <=  mode_ctrl[0] & mode_ctrl[1] & sop_ctrl;
	
	sop <= sop_ctrl;
	load_bias <= load_bias_ctrl;
	accum <= accum_ctrl;
	coeff_en1 <= coeff_en1_ctrl;
	coeff_en2 <= coeff_en2_ctrl;
	preadd_en1 <= preadd_en1_ctrl;
	preadd_en2 <= preadd_en2_ctrl;
	
	result_reg <= CPA_result;
end

always @ (*)
begin
	x1 <= (coeff_en1)? coeff1: d_x1;
	x2 <= (coeff_en2)? coeff2: d_x2;
	accum_reg <= result[63:0];
	K6_sum <= (mode[4])? K5_sum: K2_sum;
	K6_carry <= (mode[4])? K5_carry: K2_carry;
end

CPA # (
	.N(36),
	.BP1(18)
) CPA1 (
	.data_x1({d_y1, d_y2}),
	.data_x2({{(18){preadd_en1}} & d_z1, {(18){preadd_en2 || (preadd_en1 && mode)}} & d_z2}),
	.split1((mode[1:0] == 2'b00)? 1'b1: 1'b0),
	.split2(1'b0),
	.result({y1,y2})
);

multiplier_18x18 M1 (
	.clk				(clk),
	.data_x			({x1[17:14], x1[13:9] & {(5){~mode[3]}}, x1[8:0] & {(9){~mode[1]}}}),
	.data_y			({y1[17:14], y1[13:9] & {(5){~mode[3]}}, y1[8:0] & {(9){~mode[1]}}}),
	.signed_x		(sign1),
	.signed_y		(sign1),
	.suppress_sign	(~mode[0]),
	.flv2				(mode[3]),
	.sum				(M1_sum),
	.carry			(M1_carry)
);

multiplier_4x4 M6 (
	.clk				(clk),
	.data_x			(x1[12:9] & {(4){mode[3]}}),
	.data_y			(y1[12:9] & {(4){mode[3]}}),
	.signed_x		(sign1 & mode[3]),
	.signed_y		(sign1 & mode[3]),
	.sum				(M6_sum),
	.carry			(M6_carry)
);

multiplier_9x18_lsb M2 (
	.clk				 (clk),
	.data_x			 ((mode[1:0] == 2'b01)? y2[17:9]: {x2[8:5], x2[4:0] & {(5){~mode[3]}}}),
	.data_y			 ((mode[1:0] == 2'b01)? x1: {y2[17:9] & {(9){~mode[1]}}, y2[8:5], y2[4:0] & {(5){~mode[3]}}}),
	.signed_x		 ((mode[1])? sign2: 1'b0),
	.signed_y		 (sign2),
	.signed_c		 ((~mode[1])? sign2: 1'b0),
	.flv0				 (~mode[1]),
	.flv1				 (mode[1]),
	.flv2				 (mode[3]),
	.suppress_sign_x(1'b0),
	.suppress_sign_y(1'b1),
	.suppress_sign_e(1'b0),
	.sum				 (M2_sum),
	.carry			 (M2_carry)
);

multiplier_4x4 M8 (
	.clk				(clk),
	.data_x			(x2[3:0] & {(4){mode[3]}}),
	.data_y			(y2[3:0] & {(4){mode[3]}}),
	.signed_x		(sign1 & mode[3]),
	.signed_y		(sign1 & mode[3]),
	.sum				(M8_sum),
	.carry			(M8_carry)
);

Kbit_compressor_4to2 # (
	.K(9)
) K4 (
	.A					({{(1){(M1_sum[35] | M1_carry[35] | (M1_carry[34] & M1_sum[34])) & sign1}}, M1_sum[35:28]}),
	.B					({{(1){1'b0}}, M1_carry[35:28]}),
	.C					({{(1){M8_sum[7] & sign1}}, M8_sum}),
	.D					({{(1){1'b0}}, M8_carry}),
	.split			(1'b0),
	.split2			(1'b0),
	.Sum				(K4_sum),
	.Carry			(K4_carry),
	.Cox				(c4_temp)
);

multiplier_9x18_msb M3 (
	.clk				 (clk),
	.data_x			 ((~mode[1])? x2[17:9]: x1[8:0]),
	.data_y			 ((mode[1:0] == 2'b01)? y1: (mode[1:0] == 2'b00)? y2: {y1[8:0], 9'd0}),
	.signed_x		 ((mode[0] & ~mode[3])? 1'b0: sign2),
	.signed_y		 (sign2),
	.signed_c		 ((mode[0] & ~mode[3])? sign1: 1'b0),
	.flv0				 (~mode[1] & ~mode[3]),
	.flv1				 (mode[1] & ~mode[3]),
	.flv2				 (mode[3]),
	.suppress_sign_x(~mode[0]),
	.suppress_sign_y(mode[0]),
	.suppress_sign_e(~mode[0]),
	.sum				 (M3_sum),
	.carry			 (M3_carry)
);

multiplier_9x9 M4  (
	.clk				(clk),
	.data_x			(((mode[0] ^ mode[1]) || mode[3])? x2[17:9]: 9'b0),
	.data_y			(((mode[0] ^ mode[1]) || mode[3])? y2[17:9]: 9'b0),
	.flv0				(~mode[3]),
	.flv1				(mode[3]),
	.signed_x		((mode[1])? sign2: 1'b0),
	.signed_y		((mode[1])? sign2: 1'b0),
	.sum				(M4_sum),
	.carry			(M4_carry)
);

shifter # (
	.N(27),
	.S(9)
) S1 (
	.sum_in			(M2_sum),
	.carry_in		(M2_carry),
	.shift			(mode[0]),
	.sign				(1'b0),
	.enable			(~mode[3]),
	.sum_out			(S1_sum),
	.carry_out		(S1_carry)
);

Kbit_compressor_4to2 # (
	.K(27),
	.BP(9),
	.BP2(18)
) K1 (
	.A					({M3_sum[26:9] & {(18){~(mode[2])}}, (M3_sum[8:0] & {(9){~mode[2] & ~mode[4]}}) | ({(M4_sum[7] | M4_carry[7] | (M4_sum[6] & M4_carry[6])) & sign1, M4_sum[7:0]} & {(9){mode[4]}})}),
	.B					({M3_carry[26:9] & {(18){~(mode[2])}}, (M3_carry[8:0] & {(9){~mode[2] & ~mode[4]}}) | ({1'b0, M4_carry[7:0]} & {(9){mode[4]}})}),
	.C					(S1_sum[35:9] | {{M4_sum[17:10], 2'b00, M2_sum[17:10]} & {(18){mode[4]}}, {M6_sum[7] & sign1, M6_sum} & {(9){mode[4]}}}),
	.D					(S1_carry[35:9] | {{M4_carry[17:10], 2'b00, M2_carry[17:10]} & {(18){mode[4]}}, {1'b0, M6_carry} & {(9){mode[4]}}}),
	.split			(mode[1]),
	.split2			(mode[4]),
	.Sum				(K1_sum),
	.Carry			(K1_carry),
	.Cox				(c1_temp)
);

shifter # (
	.N(36),
	.S(18)
) S2 (
	.sum_in			(M1_sum),
	.carry_in		(M1_carry),
	.shift			(mode[0] | (mode[2])),
	.sign				(sign1),
	.enable			((mode == 2'b01) || sop),
	.sum_out			(S2_sum),
	.carry_out		(S2_carry)
);

Kbit_compressor_4to2 # (
	.K(54),
	.BP(18),
	.BP2(36)
) K2 (
	.A				({S2_sum[53:36], S2_sum[35:18] | {(18){(M4_sum[17] || M4_carry[17]) & sign1 & mode[2]}}, {S2_sum[17:0] | (M4_sum & {(18){(mode[1:0] == 2'b01) | (mode[2])}})}}),
	.B				({S2_carry[53:18], {S2_carry[17:0] | M4_carry & {(18){(mode[1:0] == 2'b01) | (mode[2])}}}}),
	.C				({{(18){K1_sum[26] && sign2 && (mode == 2'b00)}} | (M3_sum[26:9] & {(18){mode[2]}}), K1_sum[26:9] | {(18){K1_sum[8] & sign1 & mode[2]}}, K1_sum[8:0], S1_sum[8:0]}),
	.D				({M3_carry[26:10] & {(17){mode[2]}}, (c1_temp & (mode[1:0] == 2'b01)) | (M3_carry[9] & mode[2]), K1_carry[26:9], K1_carry[8:0], S1_carry[8:0]}),
	.split		(mode[1] & ~sop),
	.split2		(mode[2]),
	.Sum			(K2_sum),
	.Carry		(K2_carry),
	.Cox			(c2_temp)
);

Kbit_compressor_4to2 # (
	.K(54),
	.BP2(36)
) K5 (
	.A				({{(10){(K1_sum[26] | K1_carry[26] | (K1_sum[25] & K1_carry[25])) & sign1}}, K1_sum[26:19], {(27){K1_sum[8] & sign1}}, K1_sum[8:0]}),
	.B				({{(9){1'b0}}, c1_temp & ~sign1, K1_carry[26:19], {(27){1'b0}}, K1_carry[8:0]}),
	.C				({{(9){(K1_sum[17] | K1_carry[17] | (K1_sum[16] & K1_carry[16])) & sign1}}, K1_sum[17] & sign1, K1_sum[16:9], {(27){K4_sum[8] & sign1}}, K4_sum}),
	.D				({{(9){1'b0}}, K1_carry[17] | (K1_sum[17] & ~sign1), K1_carry[16:9], {(27){1'b0}}, K4_carry}),
	.split		(1'b0),
	.split2		(1'b1),
	.Sum			(K5_sum),
	.Carry		(K5_carry),
	.Cox			(c5_temp)
);

Kbit_compressor_4to2 # (
	.K(64),
	.BP(18),
	.BP2(36)
) K3 (
	.A					({{(10){(K6_sum[53] | (c2_temp & mode[2])) & (sign2 & ~(mode[1] & ~sop))}}, K6_sum}),
	.B					({{(9){1'b0}}, c2_temp & ~sign1 & mode[2], K6_carry}),
	.C					(chainin),
	.D					((accum == 1'b1)? accum_reg: load_const & {(64){load_bias}}),
	.split			(mode[1] & ~sop),
	.split2			(mode[2] | mode[4]),
	.Sum				(K3_sum),
	.Carry			(K3_carry),
	.Cox				(c3_temp)
);
 
CPA # (
	.N(72),
	.BP1(36),
	.BP2(18)
) CPA2 (
	.data_x1(
		((mode == 2'b01) || sop)? {{(8){((K3_sum[63]) && sign1) || {chainin[63] && sign1} || (accum_reg[63] && accum && sign1)}}, K3_sum}: 
			{M1_sum[35:28], (M1_sum[27:18] & {(10){~mode[3]}}) | {2'b00, M6_sum}, M1_sum[17:0] | M4_sum, K3_sum[35:18], K3_sum[17:0] | {M2_sum[17:10] & {(8){mode[3]}}, 2'b00, M8_sum}}),
	.data_x2(((mode == 2'b01) || sop)? {{(8){1'b0}}, K3_carry}: 
			{M1_carry[35:28], (M1_carry[27:18] & {(10){~mode[3]}}) | {2'b00, M6_carry}, M1_carry[17:0] | M4_carry, K3_carry[35:18], K3_carry[17:0] | {M2_carry[17:10] & {(8){mode[3]}}, 2'b00, M8_carry}}),
	.split1(~(sop | (mode == 2'b01)) | (mode[2]) | mode[4]),
	.split2(mode[1] & ~sop),
	.result(CPA_result)
);

coeff_bank # (
	.V1(18'd1), .V2(18'd2), .V3(18'd3), .V4(18'd4), .V5(18'd5), .V6(18'd6), .V7(18'd7), .V8(18'd8)
) CB1 (
	.coeff_sel(coeff_sel1),
	.value(coeff1)
);

coeff_bank # (
	.V1(18'd9), .V2(18'd10), .V3(18'd11), .V4(18'd12), .V5(18'd13), .V6(18'd14), .V7(18'd15), .V8(18'd16)
) CB2 (
	.coeff_sel(coeff_sel2),
	.value(coeff2)
);  

assign result = result_reg;
assign data_chainout = result_reg[63:0];
assign data_scanout = scanin_delay2;

endmodule

module coeff_bank # (
	parameter V1 = 18'd1,
	parameter V2 = 18'd2,
	parameter V3 = 18'd3,
	parameter V4 = 18'd4,
	parameter V5 = 18'd5,
	parameter V6 = 18'd6,
	parameter V7 = 18'd7,
	parameter V8 = 18'd8
)(
	input [2:0] coeff_sel,
	output [17:0] value
); 

reg [17:0] selected_value;

always @ (*)
begin
	case(coeff_sel)
		3'b000: selected_value <= V1; 
		3'b001: selected_value <= V2;
		3'b010: selected_value <= V3;
		3'b011: selected_value <= V4;
		3'b100: selected_value <= V5;
		3'b101: selected_value <= V6;
		3'b110: selected_value <= V7;
		3'b111: selected_value <= V8;
		default: selected_value <= V1;
	endcase
end

assign value = selected_value;

endmodule


module CPA # (
	parameter N = 74,
	parameter BP1 = 36,
	parameter BP2 = 18
)(
	input  [N-1:0] data_x1,
	input  [N-1:0] data_x2,
	input  split1,
	input  split2,
	output [N-1:0] result
);

wire[N-1:0] sum, carry;

genvar i;
generate for(i = 0; i < N; i = i+1) 
begin:genFAs
		FA FAi (
			.X(data_x1[i]), 
			.Y(data_x2[i]), 
			.Cin(((i == 0) || ((i == BP1) && (split1 == 1'b1)) || ((i % BP2 == 0) && (split2 == 1'b1)))? 1'b0: carry[i-1]), 
			.S(sum[i]), 
			.Cout(carry[i])
		);
end
endgenerate

assign result = sum;

endmodule

module shifter # (
	parameter N = 27,
	parameter S = 9
)(
	input  [N-1:0] sum_in,
	input  [N-1:0] carry_in,
	input  shift,
	input  sign,
	input  enable,
	output [N+S-1:0] sum_out,
	output [N+S-1:0] carry_out
);

wire [N+S-1:0] sum, carry;

assign sum 	 =  (shift == 1'b0)?  {{(S){(sum_in[N-1] || carry_in[N-1]) && sign}}, sum_in}: {sum_in, {(S){1'b0}}};
assign carry =  (shift == 1'b0)?  {{(S){1'b0}}, carry_in}: {carry_in,  {(S){1'b0}}};

assign sum_out = {(N+S){enable}} & sum;
assign carry_out = {(N+S){enable}} & carry;

endmodule

module Kbit_compressor_4to2 # (
	parameter K = 18,
	parameter BP = 0,
	parameter BP2 = 0
)(
	input  [K-1:0] A,
	input  [K-1:0] B,
	input  [K-1:0] C,
	input  [K-1:0] D,
	input	 split,
	input  split2,
	output [K-1:0] Sum,
	output [K-1:0] Carry,
	output Cox
);

wire Cout [K-1:0];
wire [K-1:0] sum_temp;
wire [K-1:0] carry_temp;

genvar i;
generate
for(i = 0; i < K; i = i + 1) 
begin: compGen
	if(i == BP-1)begin
		compressor_4to2_gated Ci (
			.A(A[i]),
			.B(B[i]),
			.C(C[i]),
			.D(D[i]),
			.Cin(Cout[i-1]),
			.kill(~split),
			.Sum(sum_temp[i]),
			.Carry(carry_temp[i]),
			.Cout(Cout[i])
		);
	end else if(i == BP2-1)begin
		compressor_4to2_gated Ci (
			.A(A[i]),
			.B(B[i]),
			.C(C[i]),
			.D(D[i]),
			.Cin(Cout[i-1]),
			.kill(~split2),
			.Sum(sum_temp[i]),
			.Carry(carry_temp[i]),
			.Cout(Cout[i])
		);
	end else if (i == 0) begin
		compressor_4to2 Ci (
			.A(A[i]),
			.B(B[i]),
			.C(C[i]),
			.D(D[i]),
			.Cin(1'b0),
			.Sum(sum_temp[i]),
			.Carry(carry_temp[i]),
			.Cout(Cout[i])
		);
	end else begin
		compressor_4to2 Ci (
			.A(A[i]),
			.B(B[i]),
			.C(C[i]),
			.D(D[i]),
			.Cin(Cout[i-1]),
			.Sum(sum_temp[i]),
			.Carry(carry_temp[i]),
			.Cout(Cout[i])
		);
	end
end
endgenerate

assign Sum   = sum_temp[K-1:0];
assign Carry = {carry_temp[K-2:0], 1'b0};
assign Cox = carry_temp[K-1] || Cout[K-1];

endmodule

module compressor_4to2_gated (
	input  A,
	input  B,
	input  C,
	input  D,
	input  Cin,
	input  kill,
	output Sum,
	output Carry,
	output Cout
);

wire w0, w1, w2;

assign w0 = A ^ B;
assign w1 = C ^ D;
assign w2 = w0 ^ w1;

assign Cout = kill & ((A & B) | (B & C) | (A & C));
assign Sum = Cin ^ w2;
assign Carry = (w2 == 1)? Cin & kill: D & kill;

endmodule

module compressor_4to2 (
	input  A,
	input  B,
	input  C,
	input  D,
	input  Cin,
	output Sum,
	output Carry,
	output Cout
);

wire w0, w1, w2;

assign w0 = A ^ B;
assign w1 = C ^ D;
assign w2 = w0 ^ w1;

assign Cout = (A & B) | (B & C) | (A & C);
assign Sum = Cin ^ w2;
assign Carry = (w2 == 1)? Cin: D;

endmodule

module multiplier_18x18 (
	input  clk,
	input  [17:0] data_x,
	input  [17:0] data_y,
	input  signed_x,
	input  signed_y,
	input  suppress_sign,
	input  flv2,
	output [35:0] sum,
	output [35:0] carry
);

wire [17:0] PP [17:0];
wire [35:0] dadda_sum, dadda_carry;
reg [17:0] x;
reg [17:0] y;
reg sign_x;
reg sign_y;
reg [35:0] s;
reg [35:0] c;

always @ (*)
begin: reg_in_out
	x <= data_x;
	y <= data_y;
	sign_x <= signed_x;
	sign_y <= signed_y;
	s <= dadda_sum;
	c <= dadda_carry;
end

genvar i, j;
generate
for(i = 0; i < 18; i = i + 1)
begin: arrayV
	for(j = 0; j < 18; j = j + 1)
	begin: arrayH
		if((i == 17 && j <  17)) begin
			arrayBlock_signed BLKsx (.A(y[j]), .B(x[i]), .signed_ctrl(sign_x), .mult(PP[i][j]));
		end else if((j == 17 && i <  17)) begin
			arrayBlock_signed BLKsy (.A(y[j]), .B(x[i]), .signed_ctrl(sign_y), .mult(PP[i][j]));
		end else begin
			arrayBlock_unsigned BLKu (.A(y[j]), .B(x[i]), .mult(PP[i][j]));
		end
	end
end
endgenerate

daddaTree_18x18 DT (
	.PP0(PP[0]),
	.PP1(PP[1]),
	.PP2(PP[2]),
	.PP3(PP[3]),
	.PP4(PP[4]),
	.PP5(PP[5]),
	.PP6(PP[6]),
	.PP7(PP[7]),
	.PP8(PP[8]),
	.PP9(PP[9]),
	.PP10(PP[10]),
	.PP11(PP[11]),
	.PP12(PP[12]),
	.PP13(PP[13]),
	.PP14(PP[14]),
	.PP15(PP[15]),
	.PP16(PP[16]),
	.PP17(PP[17]),
	.sx(sign_x),
	.sy(sign_y),
	.flv2(flv2),
	.suppress_sign(suppress_sign),
	.sum(dadda_sum),
	.carry(dadda_carry)
);

assign sum = s;
assign carry = c;
endmodule

module daddaTree_18x18 (
	input  [17:0] PP0,
	input  [17:0] PP1,
	input  [17:0] PP2,
	input  [17:0] PP3,
	input  [17:0] PP4,
	input  [17:0] PP5,
	input  [17:0] PP6,
	input  [17:0] PP7,
	input  [17:0] PP8,
	input  [17:0] PP9,
	input  [17:0] PP10,
	input  [17:0] PP11,
	input  [17:0] PP12,
	input  [17:0] PP13,
	input  [17:0] PP14,
	input  [17:0] PP15,
	input  [17:0] PP16,
	input  [17:0] PP17,
	input  sx,
	input  sy,
	input  flv2,
	input suppress_sign,
	output [35:0] sum,
	output [35:0] carry
);

/***** Dadda Tree Stage 1 *****/
wire [0:0] c1_0;
wire [1:0] c1_1;
wire [2:0] c1_2;
wire [3:0] c1_3;
wire [4:0] c1_4;
wire [5:0] c1_5;
wire [6:0] c1_6;
wire [7:0] c1_7;
wire [8:0] c1_8;
wire [9:0] c1_9;
wire [10:0] c1_10;
wire [11:0] c1_11;
wire [12:0] c1_12;
wire [13:0] c1_13;
wire [14:0] c1_14;
wire [15:0] c1_15;
wire [16:0] c1_16;
wire [18:0] c1_17;
wire [17:0] c1_18;
wire [15:0] c1_19;
wire [14:0] c1_20;
wire [13:0] c1_21;
wire [12:0] c1_22;
wire [11:0] c1_23;
wire [10:0] c1_24;
wire [9:0] c1_25;
wire [8:0] c1_26;
wire [9:0] c1_27;
wire [6:0] c1_28;
wire [5:0] c1_29;
wire [4:0] c1_30;
wire [3:0] c1_31;
wire [2:0] c1_32;
wire [1:0] c1_33;
wire [2:0] c1_34;
wire [1:0] c1_35;

assign c1_0[0] = PP0[0];
assign c1_1[0] = PP0[1];
assign c1_1[1] = PP1[0];
assign c1_2[0] = PP0[2];
assign c1_2[1] = PP1[1];
assign c1_2[2] = PP2[0];
assign c1_3[0] = PP0[3];
assign c1_3[1] = PP1[2];
assign c1_3[2] = PP2[1];
assign c1_3[3] = PP3[0];
assign c1_4[0] = PP0[4];
assign c1_4[1] = PP1[3];
assign c1_4[2] = PP2[2];
assign c1_4[3] = PP3[1];
assign c1_4[4] = PP4[0];
assign c1_5[0] = PP0[5];
assign c1_5[1] = PP1[4];
assign c1_5[2] = PP2[3];
assign c1_5[3] = PP3[2];
assign c1_5[4] = PP4[1];
assign c1_5[5] = PP5[0];
assign c1_6[0] = PP0[6];
assign c1_6[1] = PP1[5];
assign c1_6[2] = PP2[4];
assign c1_6[3] = PP3[3];
assign c1_6[4] = PP4[2];
assign c1_6[5] = PP5[1];
assign c1_6[6] = PP6[0];
assign c1_7[0] = PP0[7];
assign c1_7[1] = PP1[6];
assign c1_7[2] = PP2[5];
assign c1_7[3] = PP3[4];
assign c1_7[4] = PP4[3];
assign c1_7[5] = PP5[2];
assign c1_7[6] = PP6[1];
assign c1_7[7] = PP7[0];
assign c1_8[0] = PP0[8];
assign c1_8[1] = PP1[7];
assign c1_8[2] = PP2[6];
assign c1_8[3] = PP3[5];
assign c1_8[4] = PP4[4];
assign c1_8[5] = PP5[3];
assign c1_8[6] = PP6[2];
assign c1_8[7] = PP7[1];
assign c1_8[8] = PP8[0];
assign c1_9[0] = PP0[9];
assign c1_9[1] = PP1[8];
assign c1_9[2] = PP2[7];
assign c1_9[3] = PP3[6];
assign c1_9[4] = PP4[5];
assign c1_9[5] = PP5[4];
assign c1_9[6] = PP6[3];
assign c1_9[7] = PP7[2];
assign c1_9[8] = PP8[1];
assign c1_9[9] = PP9[0];
assign c1_10[0] = PP0[10];
assign c1_10[1] = PP1[9];
assign c1_10[2] = PP2[8];
assign c1_10[3] = PP3[7];
assign c1_10[4] = PP4[6];
assign c1_10[5] = PP5[5];
assign c1_10[6] = PP6[4];
assign c1_10[7] = PP7[3];
assign c1_10[8] = PP8[2];
assign c1_10[9] = PP9[1];
assign c1_10[10] = PP10[0];
assign c1_11[0] = PP0[11];
assign c1_11[1] = PP1[10];
assign c1_11[2] = PP2[9];
assign c1_11[3] = PP3[8];
assign c1_11[4] = PP4[7];
assign c1_11[5] = PP5[6];
assign c1_11[6] = PP6[5];
assign c1_11[7] = PP7[4];
assign c1_11[8] = PP8[3];
assign c1_11[9] = PP9[2];
assign c1_11[10] = PP10[1];
assign c1_11[11] = PP11[0];
assign c1_12[0] = PP0[12];
assign c1_12[1] = PP1[11];
assign c1_12[2] = PP2[10];
assign c1_12[3] = PP3[9];
assign c1_12[4] = PP4[8];
assign c1_12[5] = PP5[7];
assign c1_12[6] = PP6[6];
assign c1_12[7] = PP7[5];
assign c1_12[8] = PP8[4];
assign c1_12[9] = PP9[3];
assign c1_12[10] = PP10[2];
assign c1_12[11] = PP11[1];
assign c1_12[12] = PP12[0];
assign c1_13[0] = PP0[13];
assign c1_13[1] = PP1[12];
assign c1_13[2] = PP2[11];
assign c1_13[3] = PP3[10];
assign c1_13[4] = PP4[9];
assign c1_13[5] = PP5[8];
assign c1_13[6] = PP6[7];
assign c1_13[7] = PP7[6];
assign c1_13[8] = PP8[5];
assign c1_13[9] = PP9[4];
assign c1_13[10] = PP10[3];
assign c1_13[11] = PP11[2];
assign c1_13[12] = PP12[1];
assign c1_13[13] = PP13[0];
assign c1_14[0] = PP0[14];
assign c1_14[1] = PP1[13];
assign c1_14[2] = PP2[12];
assign c1_14[3] = PP3[11];
assign c1_14[4] = PP4[10];
assign c1_14[5] = PP5[9];
assign c1_14[6] = PP6[8];
assign c1_14[7] = PP7[7];
assign c1_14[8] = PP8[6];
assign c1_14[9] = PP9[5];
assign c1_14[10] = PP10[4];
assign c1_14[11] = PP11[3];
assign c1_14[12] = PP12[2];
assign c1_14[13] = PP13[1];
assign c1_14[14] = PP14[0];
assign c1_15[0] = PP0[15];
assign c1_15[1] = PP1[14];
assign c1_15[2] = PP2[13];
assign c1_15[3] = PP3[12];
assign c1_15[4] = PP4[11];
assign c1_15[5] = PP5[10];
assign c1_15[6] = PP6[9];
assign c1_15[7] = PP7[8];
assign c1_15[8] = PP8[7];
assign c1_15[9] = PP9[6];
assign c1_15[10] = PP10[5];
assign c1_15[11] = PP11[4];
assign c1_15[12] = PP12[3];
assign c1_15[13] = PP13[2];
assign c1_15[14] = PP14[1];
assign c1_15[15] = PP15[0];
assign c1_16[0] = PP0[16];
assign c1_16[1] = PP1[15];
assign c1_16[2] = PP2[14];
assign c1_16[3] = PP3[13];
assign c1_16[4] = PP4[12];
assign c1_16[5] = PP5[11];
assign c1_16[6] = PP6[10];
assign c1_16[7] = PP7[9];
assign c1_16[8] = PP8[8];
assign c1_16[9] = PP9[7];
assign c1_16[10] = PP10[6];
assign c1_16[11] = PP11[5];
assign c1_16[12] = PP12[4];
assign c1_16[13] = PP13[3];
assign c1_16[14] = PP14[2];
assign c1_16[15] = PP15[1];
assign c1_16[16] = PP16[0];
HA ha0 (PP0[17], PP1[16], c1_17[0], c1_18[0]);
assign c1_17[1] = PP2[15];
assign c1_17[2] = PP3[14];
assign c1_17[3] = PP4[13];
assign c1_17[4] = PP5[12];
assign c1_17[5] = PP6[11];
assign c1_17[6] = PP7[10];
assign c1_17[7] = PP8[9];
assign c1_17[8] = PP9[8];
assign c1_17[9] = PP10[7];
assign c1_17[10] = PP11[6];
assign c1_17[11] = PP12[5];
assign c1_17[12] = PP13[4];
assign c1_17[13] = PP14[3];
assign c1_17[14] = PP15[2];
assign c1_17[15] = PP16[1];
assign c1_17[16] = PP17[0];
assign c1_17[17] = suppress_sign & sx;
assign c1_17[18] = suppress_sign & sy;
assign c1_18[1] = PP1[17];
assign c1_18[2] = PP2[16];
assign c1_18[3] = PP3[15];
assign c1_18[4] = PP4[14];
assign c1_18[5] = PP5[13];
assign c1_18[6] = PP6[12];
assign c1_18[7] = PP7[11];
assign c1_18[8] = PP8[10];
assign c1_18[9] = PP9[9];
assign c1_18[10] = PP10[8];
assign c1_18[11] = PP11[7];
assign c1_18[12] = PP12[6];
assign c1_18[13] = PP13[5];
assign c1_18[14] = PP14[4];
assign c1_18[15] = PP15[3];
assign c1_18[16] = PP16[2];
assign c1_18[17] = PP17[1];
assign c1_19[0] = PP2[17];
assign c1_19[1] = PP3[16];
assign c1_19[2] = PP4[15];
assign c1_19[3] = PP5[14];
assign c1_19[4] = PP6[13];
assign c1_19[5] = PP7[12];
assign c1_19[6] = PP8[11];
assign c1_19[7] = PP9[10];
assign c1_19[8] = PP10[9];
assign c1_19[9] = PP11[8];
assign c1_19[10] = PP12[7];
assign c1_19[11] = PP13[6];
assign c1_19[12] = PP14[5];
assign c1_19[13] = PP15[4];
assign c1_19[14] = PP16[3];
assign c1_19[15] = PP17[2];
assign c1_20[0] = PP3[17];
assign c1_20[1] = PP4[16];
assign c1_20[2] = PP5[15];
assign c1_20[3] = PP6[14];
assign c1_20[4] = PP7[13];
assign c1_20[5] = PP8[12];
assign c1_20[6] = PP9[11];
assign c1_20[7] = PP10[10];
assign c1_20[8] = PP11[9];
assign c1_20[9] = PP12[8];
assign c1_20[10] = PP13[7];
assign c1_20[11] = PP14[6];
assign c1_20[12] = PP15[5];
assign c1_20[13] = PP16[4];
assign c1_20[14] = PP17[3];
assign c1_21[0] = PP4[17];
assign c1_21[1] = PP5[16];
assign c1_21[2] = PP6[15];
assign c1_21[3] = PP7[14];
assign c1_21[4] = PP8[13];
assign c1_21[5] = PP9[12];
assign c1_21[6] = PP10[11];
assign c1_21[7] = PP11[10];
assign c1_21[8] = PP12[9];
assign c1_21[9] = PP13[8];
assign c1_21[10] = PP14[7];
assign c1_21[11] = PP15[6];
assign c1_21[12] = PP16[5];
assign c1_21[13] = PP17[4];
assign c1_22[0] = PP5[17];
assign c1_22[1] = PP6[16];
assign c1_22[2] = PP7[15];
assign c1_22[3] = PP8[14];
assign c1_22[4] = PP9[13];
assign c1_22[5] = PP10[12];
assign c1_22[6] = PP11[11];
assign c1_22[7] = PP12[10];
assign c1_22[8] = PP13[9];
assign c1_22[9] = PP14[8];
assign c1_22[10] = PP15[7];
assign c1_22[11] = PP16[6];
assign c1_22[12] = PP17[5];
assign c1_23[0] = PP6[17];
assign c1_23[1] = PP7[16];
assign c1_23[2] = PP8[15];
assign c1_23[3] = PP9[14];
assign c1_23[4] = PP10[13];
assign c1_23[5] = PP11[12];
assign c1_23[6] = PP12[11];
assign c1_23[7] = PP13[10];
assign c1_23[8] = PP14[9];
assign c1_23[9] = PP15[8];
assign c1_23[10] = PP16[7];
assign c1_23[11] = PP17[6];
assign c1_24[0] = PP7[17];
assign c1_24[1] = PP8[16];
assign c1_24[2] = PP9[15];
assign c1_24[3] = PP10[14];
assign c1_24[4] = PP11[13];
assign c1_24[5] = PP12[12];
assign c1_24[6] = PP13[11];
assign c1_24[7] = PP14[10];
assign c1_24[8] = PP15[9];
assign c1_24[9] = PP16[8];
assign c1_24[10] = PP17[7];
assign c1_25[0] = PP8[17];
assign c1_25[1] = PP9[16];
assign c1_25[2] = PP10[15];
assign c1_25[3] = PP11[14];
assign c1_25[4] = PP12[13];
assign c1_25[5] = PP13[12];
assign c1_25[6] = PP14[11];
assign c1_25[7] = PP15[10];
assign c1_25[8] = PP16[9];
assign c1_25[9] = PP17[8];
assign c1_26[0] = PP9[17];
assign c1_26[1] = PP10[16];
assign c1_26[2] = PP11[15];
assign c1_26[3] = PP12[14];
assign c1_26[4] = PP13[13];
assign c1_26[5] = PP14[12];
assign c1_26[6] = PP15[11];
assign c1_26[7] = PP16[10];
assign c1_26[8] = PP17[9];
assign c1_27[0] = PP10[17];
assign c1_27[1] = PP11[16];
assign c1_27[2] = PP12[15];
assign c1_27[3] = PP13[14];
assign c1_27[4] = PP14[13];
assign c1_27[5] = PP15[12];
assign c1_27[6] = PP16[11];
assign c1_27[7] = PP17[10];
assign c1_27[8] = sx & flv2;
assign c1_27[9] = sy & flv2;
assign c1_28[0] = PP11[17];
assign c1_28[1] = PP12[16];
assign c1_28[2] = PP13[15];
assign c1_28[3] = PP14[14];
assign c1_28[4] = PP15[13];
assign c1_28[5] = PP16[12];
assign c1_28[6] = PP17[11];
assign c1_29[0] = PP12[17];
assign c1_29[1] = PP13[16];
assign c1_29[2] = PP14[15];
assign c1_29[3] = PP15[14];
assign c1_29[4] = PP16[13];
assign c1_29[5] = PP17[12];
assign c1_30[0] = PP13[17];
assign c1_30[1] = PP14[16];
assign c1_30[2] = PP15[15];
assign c1_30[3] = PP16[14];
assign c1_30[4] = PP17[13];
assign c1_31[0] = PP14[17];
assign c1_31[1] = PP15[16];
assign c1_31[2] = PP16[15];
assign c1_31[3] = PP17[14];
assign c1_32[0] = PP15[17];
assign c1_32[1] = PP16[16];
assign c1_32[2] = PP17[15];
assign c1_33[0] = PP16[17];
assign c1_33[1] = PP17[16];
assign c1_34[0] = PP17[17];
assign c1_34[1] = sx;
assign c1_34[2] = sy;
assign c1_35[0] = sx;
assign c1_35[1] = sy;

/***** Dadda Tree Stage 2 *****/
wire [0:0] c2_0;
wire [1:0] c2_1;
wire [2:0] c2_2;
wire [3:0] c2_3;
wire [4:0] c2_4;
wire [5:0] c2_5;
wire [6:0] c2_6;
wire [7:0] c2_7;
wire [8:0] c2_8;
wire [9:0] c2_9;
wire [10:0] c2_10;
wire [11:0] c2_11;
wire [12:0] c2_12;
wire [12:0] c2_13;
wire [12:0] c2_14;
wire [12:0] c2_15;
wire [12:0] c2_16;
wire [12:0] c2_17;
wire [12:0] c2_18;
wire [12:0] c2_19;
wire [12:0] c2_20;
wire [12:0] c2_21;
wire [12:0] c2_22;
wire [12:0] c2_23;
wire [10:0] c2_24;
wire [9:0] c2_25;
wire [8:0] c2_26;
wire [9:0] c2_27;
wire [6:0] c2_28;
wire [5:0] c2_29;
wire [4:0] c2_30;
wire [3:0] c2_31;
wire [2:0] c2_32;
wire [1:0] c2_33;
wire [2:0] c2_34;
wire [1:0] c2_35;

assign c2_0[0] = c1_0[0];
assign c2_1[0] = c1_1[0];
assign c2_1[1] = c1_1[1];
assign c2_2[0] = c1_2[0];
assign c2_2[1] = c1_2[1];
assign c2_2[2] = c1_2[2];
assign c2_3[0] = c1_3[0];
assign c2_3[1] = c1_3[1];
assign c2_3[2] = c1_3[2];
assign c2_3[3] = c1_3[3];
assign c2_4[0] = c1_4[0];
assign c2_4[1] = c1_4[1];
assign c2_4[2] = c1_4[2];
assign c2_4[3] = c1_4[3];
assign c2_4[4] = c1_4[4];
assign c2_5[0] = c1_5[0];
assign c2_5[1] = c1_5[1];
assign c2_5[2] = c1_5[2];
assign c2_5[3] = c1_5[3];
assign c2_5[4] = c1_5[4];
assign c2_5[5] = c1_5[5];
assign c2_6[0] = c1_6[0];
assign c2_6[1] = c1_6[1];
assign c2_6[2] = c1_6[2];
assign c2_6[3] = c1_6[3];
assign c2_6[4] = c1_6[4];
assign c2_6[5] = c1_6[5];
assign c2_6[6] = c1_6[6];
assign c2_7[0] = c1_7[0];
assign c2_7[1] = c1_7[1];
assign c2_7[2] = c1_7[2];
assign c2_7[3] = c1_7[3];
assign c2_7[4] = c1_7[4];
assign c2_7[5] = c1_7[5];
assign c2_7[6] = c1_7[6];
assign c2_7[7] = c1_7[7];
assign c2_8[0] = c1_8[0];
assign c2_8[1] = c1_8[1];
assign c2_8[2] = c1_8[2];
assign c2_8[3] = c1_8[3];
assign c2_8[4] = c1_8[4];
assign c2_8[5] = c1_8[5];
assign c2_8[6] = c1_8[6];
assign c2_8[7] = c1_8[7];
assign c2_8[8] = c1_8[8];
assign c2_9[0] = c1_9[0];
assign c2_9[1] = c1_9[1];
assign c2_9[2] = c1_9[2];
assign c2_9[3] = c1_9[3];
assign c2_9[4] = c1_9[4];
assign c2_9[5] = c1_9[5];
assign c2_9[6] = c1_9[6];
assign c2_9[7] = c1_9[7];
assign c2_9[8] = c1_9[8];
assign c2_9[9] = c1_9[9];
assign c2_10[0] = c1_10[0];
assign c2_10[1] = c1_10[1];
assign c2_10[2] = c1_10[2];
assign c2_10[3] = c1_10[3];
assign c2_10[4] = c1_10[4];
assign c2_10[5] = c1_10[5];
assign c2_10[6] = c1_10[6];
assign c2_10[7] = c1_10[7];
assign c2_10[8] = c1_10[8];
assign c2_10[9] = c1_10[9];
assign c2_10[10] = c1_10[10];
assign c2_11[0] = c1_11[0];
assign c2_11[1] = c1_11[1];
assign c2_11[2] = c1_11[2];
assign c2_11[3] = c1_11[3];
assign c2_11[4] = c1_11[4];
assign c2_11[5] = c1_11[5];
assign c2_11[6] = c1_11[6];
assign c2_11[7] = c1_11[7];
assign c2_11[8] = c1_11[8];
assign c2_11[9] = c1_11[9];
assign c2_11[10] = c1_11[10];
assign c2_11[11] = c1_11[11];
assign c2_12[0] = c1_12[0];
assign c2_12[1] = c1_12[1];
assign c2_12[2] = c1_12[2];
assign c2_12[3] = c1_12[3];
assign c2_12[4] = c1_12[4];
assign c2_12[5] = c1_12[5];
assign c2_12[6] = c1_12[6];
assign c2_12[7] = c1_12[7];
assign c2_12[8] = c1_12[8];
assign c2_12[9] = c1_12[9];
assign c2_12[10] = c1_12[10];
assign c2_12[11] = c1_12[11];
assign c2_12[12] = c1_12[12];
HA ha1 (c1_13[0], c1_13[1], c2_13[0], c2_14[0]);
assign c2_13[1] = c1_13[2];
assign c2_13[2] = c1_13[3];
assign c2_13[3] = c1_13[4];
assign c2_13[4] = c1_13[5];
assign c2_13[5] = c1_13[6];
assign c2_13[6] = c1_13[7];
assign c2_13[7] = c1_13[8];
assign c2_13[8] = c1_13[9];
assign c2_13[9] = c1_13[10];
assign c2_13[10] = c1_13[11];
assign c2_13[11] = c1_13[12];
assign c2_13[12] = c1_13[13];
FA fa0 (c1_14[0], c1_14[1], c1_14[2], c2_14[1], c2_15[0]);
HA ha2 (c1_14[3], c1_14[4], c2_14[2], c2_15[1]);
assign c2_14[3] = c1_14[5];
assign c2_14[4] = c1_14[6];
assign c2_14[5] = c1_14[7];
assign c2_14[6] = c1_14[8];
assign c2_14[7] = c1_14[9];
assign c2_14[8] = c1_14[10];
assign c2_14[9] = c1_14[11];
assign c2_14[10] = c1_14[12];
assign c2_14[11] = c1_14[13];
assign c2_14[12] = c1_14[14];
FA fa1 (c1_15[0], c1_15[1], c1_15[2], c2_15[2], c2_16[0]);
FA fa2 (c1_15[3], c1_15[4], c1_15[5], c2_15[3], c2_16[1]);
HA ha3 (c1_15[6], c1_15[7], c2_15[4], c2_16[2]);
assign c2_15[5] = c1_15[8];
assign c2_15[6] = c1_15[9];
assign c2_15[7] = c1_15[10];
assign c2_15[8] = c1_15[11];
assign c2_15[9] = c1_15[12];
assign c2_15[10] = c1_15[13];
assign c2_15[11] = c1_15[14];
assign c2_15[12] = c1_15[15];
FA fa3 (c1_16[0], c1_16[1], c1_16[2], c2_16[3], c2_17[0]);
FA fa4 (c1_16[3], c1_16[4], c1_16[5], c2_16[4], c2_17[1]);
FA fa5 (c1_16[6], c1_16[7], c1_16[8], c2_16[5], c2_17[2]);
HA ha4 (c1_16[9], c1_16[10], c2_16[6], c2_17[3]);
assign c2_16[7] = c1_16[11];
assign c2_16[8] = c1_16[12];
assign c2_16[9] = c1_16[13];
assign c2_16[10] = c1_16[14];
assign c2_16[11] = c1_16[15];
assign c2_16[12] = c1_16[16];
FA fa6 (c1_17[0], c1_17[1], c1_17[2], c2_17[4], c2_18[0]);
FA fa7 (c1_17[3], c1_17[4], c1_17[5], c2_17[5], c2_18[1]);
FA fa8 (c1_17[6], c1_17[7], c1_17[8], c2_17[6], c2_18[2]);
FA fa9 (c1_17[9], c1_17[10], c1_17[11], c2_17[7], c2_18[3]);
FA fa10 (c1_17[12], c1_17[13], c1_17[14], c2_17[8], c2_18[4]);
assign c2_17[9] = c1_17[15];
assign c2_17[10] = c1_17[16];
assign c2_17[11] = c1_17[17];
assign c2_17[12] = c1_17[18];
FA fa11 (c1_18[0], c1_18[1], c1_18[2], c2_18[5], c2_19[0]);
FA fa12 (c1_18[3], c1_18[4], c1_18[5], c2_18[6], c2_19[1]);
FA fa13 (c1_18[6], c1_18[7], c1_18[8], c2_18[7], c2_19[2]);
FA fa14 (c1_18[9], c1_18[10], c1_18[11], c2_18[8], c2_19[3]);
FA fa15 (c1_18[12], c1_18[13], c1_18[14], c2_18[9], c2_19[4]);
assign c2_18[10] = c1_18[15];
assign c2_18[11] = c1_18[16];
assign c2_18[12] = c1_18[17];
FA fa16 (c1_19[0], c1_19[1], c1_19[2], c2_19[5], c2_20[0]);
FA fa17 (c1_19[3], c1_19[4], c1_19[5], c2_19[6], c2_20[1]);
FA fa18 (c1_19[6], c1_19[7], c1_19[8], c2_19[7], c2_20[2]);
FA fa19 (c1_19[9], c1_19[10], c1_19[11], c2_19[8], c2_20[3]);
assign c2_19[9] = c1_19[12];
assign c2_19[10] = c1_19[13];
assign c2_19[11] = c1_19[14];
assign c2_19[12] = c1_19[15];
FA fa20 (c1_20[0], c1_20[1], c1_20[2], c2_20[4], c2_21[0]);
FA fa21 (c1_20[3], c1_20[4], c1_20[5], c2_20[5], c2_21[1]);
FA fa22 (c1_20[6], c1_20[7], c1_20[8], c2_20[6], c2_21[2]);
assign c2_20[7] = c1_20[9];
assign c2_20[8] = c1_20[10];
assign c2_20[9] = c1_20[11];
assign c2_20[10] = c1_20[12];
assign c2_20[11] = c1_20[13];
assign c2_20[12] = c1_20[14];
FA fa23 (c1_21[0], c1_21[1], c1_21[2], c2_21[3], c2_22[0]);
FA fa24 (c1_21[3], c1_21[4], c1_21[5], c2_21[4], c2_22[1]);
assign c2_21[5] = c1_21[6];
assign c2_21[6] = c1_21[7];
assign c2_21[7] = c1_21[8];
assign c2_21[8] = c1_21[9];
assign c2_21[9] = c1_21[10];
assign c2_21[10] = c1_21[11];
assign c2_21[11] = c1_21[12];
assign c2_21[12] = c1_21[13];
FA fa25 (c1_22[0], c1_22[1], c1_22[2], c2_22[2], c2_23[0]);
assign c2_22[3] = c1_22[3];
assign c2_22[4] = c1_22[4];
assign c2_22[5] = c1_22[5];
assign c2_22[6] = c1_22[6];
assign c2_22[7] = c1_22[7];
assign c2_22[8] = c1_22[8];
assign c2_22[9] = c1_22[9];
assign c2_22[10] = c1_22[10];
assign c2_22[11] = c1_22[11];
assign c2_22[12] = c1_22[12];
assign c2_23[1] = c1_23[0];
assign c2_23[2] = c1_23[1];
assign c2_23[3] = c1_23[2];
assign c2_23[4] = c1_23[3];
assign c2_23[5] = c1_23[4];
assign c2_23[6] = c1_23[5];
assign c2_23[7] = c1_23[6];
assign c2_23[8] = c1_23[7];
assign c2_23[9] = c1_23[8];
assign c2_23[10] = c1_23[9];
assign c2_23[11] = c1_23[10];
assign c2_23[12] = c1_23[11];
assign c2_24[0] = c1_24[0];
assign c2_24[1] = c1_24[1];
assign c2_24[2] = c1_24[2];
assign c2_24[3] = c1_24[3];
assign c2_24[4] = c1_24[4];
assign c2_24[5] = c1_24[5];
assign c2_24[6] = c1_24[6];
assign c2_24[7] = c1_24[7];
assign c2_24[8] = c1_24[8];
assign c2_24[9] = c1_24[9];
assign c2_24[10] = c1_24[10];
assign c2_25[0] = c1_25[0];
assign c2_25[1] = c1_25[1];
assign c2_25[2] = c1_25[2];
assign c2_25[3] = c1_25[3];
assign c2_25[4] = c1_25[4];
assign c2_25[5] = c1_25[5];
assign c2_25[6] = c1_25[6];
assign c2_25[7] = c1_25[7];
assign c2_25[8] = c1_25[8];
assign c2_25[9] = c1_25[9];
assign c2_26[0] = c1_26[0];
assign c2_26[1] = c1_26[1];
assign c2_26[2] = c1_26[2];
assign c2_26[3] = c1_26[3];
assign c2_26[4] = c1_26[4];
assign c2_26[5] = c1_26[5];
assign c2_26[6] = c1_26[6];
assign c2_26[7] = c1_26[7];
assign c2_26[8] = c1_26[8];
assign c2_27[0] = c1_27[0];
assign c2_27[1] = c1_27[1];
assign c2_27[2] = c1_27[2];
assign c2_27[3] = c1_27[3];
assign c2_27[4] = c1_27[4];
assign c2_27[5] = c1_27[5];
assign c2_27[6] = c1_27[6];
assign c2_27[7] = c1_27[7];
assign c2_27[8] = c1_27[8];
assign c2_27[9] = c1_27[9];
assign c2_28[0] = c1_28[0];
assign c2_28[1] = c1_28[1];
assign c2_28[2] = c1_28[2];
assign c2_28[3] = c1_28[3];
assign c2_28[4] = c1_28[4];
assign c2_28[5] = c1_28[5];
assign c2_28[6] = c1_28[6];
assign c2_29[0] = c1_29[0];
assign c2_29[1] = c1_29[1];
assign c2_29[2] = c1_29[2];
assign c2_29[3] = c1_29[3];
assign c2_29[4] = c1_29[4];
assign c2_29[5] = c1_29[5];
assign c2_30[0] = c1_30[0];
assign c2_30[1] = c1_30[1];
assign c2_30[2] = c1_30[2];
assign c2_30[3] = c1_30[3];
assign c2_30[4] = c1_30[4];
assign c2_31[0] = c1_31[0];
assign c2_31[1] = c1_31[1];
assign c2_31[2] = c1_31[2];
assign c2_31[3] = c1_31[3];
assign c2_32[0] = c1_32[0];
assign c2_32[1] = c1_32[1];
assign c2_32[2] = c1_32[2];
assign c2_33[0] = c1_33[0];
assign c2_33[1] = c1_33[1];
assign c2_34[0] = c1_34[0];
assign c2_34[1] = c1_34[1];
assign c2_34[2] = c1_34[2];
assign c2_35[0] = c1_35[0];
assign c2_35[1] = c1_35[1];

/***** Dadda Tree Stage 3 *****/
wire [0:0] c3_0;
wire [1:0] c3_1;
wire [2:0] c3_2;
wire [3:0] c3_3;
wire [4:0] c3_4;
wire [5:0] c3_5;
wire [6:0] c3_6;
wire [7:0] c3_7;
wire [8:0] c3_8;
wire [8:0] c3_9;
wire [8:0] c3_10;
wire [8:0] c3_11;
wire [8:0] c3_12;
wire [8:0] c3_13;
wire [8:0] c3_14;
wire [8:0] c3_15;
wire [8:0] c3_16;
wire [8:0] c3_17;
wire [8:0] c3_18;
wire [8:0] c3_19;
wire [8:0] c3_20;
wire [8:0] c3_21;
wire [8:0] c3_22;
wire [8:0] c3_23;
wire [8:0] c3_24;
wire [8:0] c3_25;
wire [8:0] c3_26;
wire [8:0] c3_27;
wire [7:0] c3_28;
wire [5:0] c3_29;
wire [4:0] c3_30;
wire [3:0] c3_31;
wire [2:0] c3_32;
wire [1:0] c3_33;
wire [2:0] c3_34;
wire [1:0] c3_35;

assign c3_0[0] = c2_0[0];
assign c3_1[0] = c2_1[0];
assign c3_1[1] = c2_1[1];
assign c3_2[0] = c2_2[0];
assign c3_2[1] = c2_2[1];
assign c3_2[2] = c2_2[2];
assign c3_3[0] = c2_3[0];
assign c3_3[1] = c2_3[1];
assign c3_3[2] = c2_3[2];
assign c3_3[3] = c2_3[3];
assign c3_4[0] = c2_4[0];
assign c3_4[1] = c2_4[1];
assign c3_4[2] = c2_4[2];
assign c3_4[3] = c2_4[3];
assign c3_4[4] = c2_4[4];
assign c3_5[0] = c2_5[0];
assign c3_5[1] = c2_5[1];
assign c3_5[2] = c2_5[2];
assign c3_5[3] = c2_5[3];
assign c3_5[4] = c2_5[4];
assign c3_5[5] = c2_5[5];
assign c3_6[0] = c2_6[0];
assign c3_6[1] = c2_6[1];
assign c3_6[2] = c2_6[2];
assign c3_6[3] = c2_6[3];
assign c3_6[4] = c2_6[4];
assign c3_6[5] = c2_6[5];
assign c3_6[6] = c2_6[6];
assign c3_7[0] = c2_7[0];
assign c3_7[1] = c2_7[1];
assign c3_7[2] = c2_7[2];
assign c3_7[3] = c2_7[3];
assign c3_7[4] = c2_7[4];
assign c3_7[5] = c2_7[5];
assign c3_7[6] = c2_7[6];
assign c3_7[7] = c2_7[7];
assign c3_8[0] = c2_8[0];
assign c3_8[1] = c2_8[1];
assign c3_8[2] = c2_8[2];
assign c3_8[3] = c2_8[3];
assign c3_8[4] = c2_8[4];
assign c3_8[5] = c2_8[5];
assign c3_8[6] = c2_8[6];
assign c3_8[7] = c2_8[7];
assign c3_8[8] = c2_8[8];
HA ha5 (c2_9[0], c2_9[1], c3_9[0], c3_10[0]);
assign c3_9[1] = c2_9[2];
assign c3_9[2] = c2_9[3];
assign c3_9[3] = c2_9[4];
assign c3_9[4] = c2_9[5];
assign c3_9[5] = c2_9[6];
assign c3_9[6] = c2_9[7];
assign c3_9[7] = c2_9[8];
assign c3_9[8] = c2_9[9];
FA fa26 (c2_10[0], c2_10[1], c2_10[2], c3_10[1], c3_11[0]);
HA ha6 (c2_10[3], c2_10[4], c3_10[2], c3_11[1]);
assign c3_10[3] = c2_10[5];
assign c3_10[4] = c2_10[6];
assign c3_10[5] = c2_10[7];
assign c3_10[6] = c2_10[8];
assign c3_10[7] = c2_10[9];
assign c3_10[8] = c2_10[10];
FA fa27 (c2_11[0], c2_11[1], c2_11[2], c3_11[2], c3_12[0]);
FA fa28 (c2_11[3], c2_11[4], c2_11[5], c3_11[3], c3_12[1]);
HA ha7 (c2_11[6], c2_11[7], c3_11[4], c3_12[2]);
assign c3_11[5] = c2_11[8];
assign c3_11[6] = c2_11[9];
assign c3_11[7] = c2_11[10];
assign c3_11[8] = c2_11[11];
FA fa29 (c2_12[0], c2_12[1], c2_12[2], c3_12[3], c3_13[0]);
FA fa30 (c2_12[3], c2_12[4], c2_12[5], c3_12[4], c3_13[1]);
FA fa31 (c2_12[6], c2_12[7], c2_12[8], c3_12[5], c3_13[2]);
HA ha8 (c2_12[9], c2_12[10], c3_12[6], c3_13[3]);
assign c3_12[7] = c2_12[11];
assign c3_12[8] = c2_12[12];
FA fa32 (c2_13[0], c2_13[1], c2_13[2], c3_13[4], c3_14[0]);
FA fa33 (c2_13[3], c2_13[4], c2_13[5], c3_13[5], c3_14[1]);
FA fa34 (c2_13[6], c2_13[7], c2_13[8], c3_13[6], c3_14[2]);
FA fa35 (c2_13[9], c2_13[10], c2_13[11], c3_13[7], c3_14[3]);
assign c3_13[8] = c2_13[12];
FA fa36 (c2_14[0], c2_14[1], c2_14[2], c3_14[4], c3_15[0]);
FA fa37 (c2_14[3], c2_14[4], c2_14[5], c3_14[5], c3_15[1]);
FA fa38 (c2_14[6], c2_14[7], c2_14[8], c3_14[6], c3_15[2]);
FA fa39 (c2_14[9], c2_14[10], c2_14[11], c3_14[7], c3_15[3]);
assign c3_14[8] = c2_14[12];
FA fa40 (c2_15[0], c2_15[1], c2_15[2], c3_15[4], c3_16[0]);
FA fa41 (c2_15[3], c2_15[4], c2_15[5], c3_15[5], c3_16[1]);
FA fa42 (c2_15[6], c2_15[7], c2_15[8], c3_15[6], c3_16[2]);
FA fa43 (c2_15[9], c2_15[10], c2_15[11], c3_15[7], c3_16[3]);
assign c3_15[8] = c2_15[12];
FA fa44 (c2_16[0], c2_16[1], c2_16[2], c3_16[4], c3_17[0]);
FA fa45 (c2_16[3], c2_16[4], c2_16[5], c3_16[5], c3_17[1]);
FA fa46 (c2_16[6], c2_16[7], c2_16[8], c3_16[6], c3_17[2]);
FA fa47 (c2_16[9], c2_16[10], c2_16[11], c3_16[7], c3_17[3]);
assign c3_16[8] = c2_16[12];
FA fa48 (c2_17[0], c2_17[1], c2_17[2], c3_17[4], c3_18[0]);
FA fa49 (c2_17[3], c2_17[4], c2_17[5], c3_17[5], c3_18[1]);
FA fa50 (c2_17[6], c2_17[7], c2_17[8], c3_17[6], c3_18[2]);
FA fa51 (c2_17[9], c2_17[10], c2_17[11], c3_17[7], c3_18[3]);
assign c3_17[8] = c2_17[12];
FA fa52 (c2_18[0], c2_18[1], c2_18[2], c3_18[4], c3_19[0]);
FA fa53 (c2_18[3], c2_18[4], c2_18[5], c3_18[5], c3_19[1]);
FA fa54 (c2_18[6], c2_18[7], c2_18[8], c3_18[6], c3_19[2]);
FA fa55 (c2_18[9], c2_18[10], c2_18[11], c3_18[7], c3_19[3]);
assign c3_18[8] = c2_18[12];
FA fa56 (c2_19[0], c2_19[1], c2_19[2], c3_19[4], c3_20[0]);
FA fa57 (c2_19[3], c2_19[4], c2_19[5], c3_19[5], c3_20[1]);
FA fa58 (c2_19[6], c2_19[7], c2_19[8], c3_19[6], c3_20[2]);
FA fa59 (c2_19[9], c2_19[10], c2_19[11], c3_19[7], c3_20[3]);
assign c3_19[8] = c2_19[12];
FA fa60 (c2_20[0], c2_20[1], c2_20[2], c3_20[4], c3_21[0]);
FA fa61 (c2_20[3], c2_20[4], c2_20[5], c3_20[5], c3_21[1]);
FA fa62 (c2_20[6], c2_20[7], c2_20[8], c3_20[6], c3_21[2]);
FA fa63 (c2_20[9], c2_20[10], c2_20[11], c3_20[7], c3_21[3]);
assign c3_20[8] = c2_20[12];
FA fa64 (c2_21[0], c2_21[1], c2_21[2], c3_21[4], c3_22[0]);
FA fa65 (c2_21[3], c2_21[4], c2_21[5], c3_21[5], c3_22[1]);
FA fa66 (c2_21[6], c2_21[7], c2_21[8], c3_21[6], c3_22[2]);
FA fa67 (c2_21[9], c2_21[10], c2_21[11], c3_21[7], c3_22[3]);
assign c3_21[8] = c2_21[12];
FA fa68 (c2_22[0], c2_22[1], c2_22[2], c3_22[4], c3_23[0]);
FA fa69 (c2_22[3], c2_22[4], c2_22[5], c3_22[5], c3_23[1]);
FA fa70 (c2_22[6], c2_22[7], c2_22[8], c3_22[6], c3_23[2]);
FA fa71 (c2_22[9], c2_22[10], c2_22[11], c3_22[7], c3_23[3]);
assign c3_22[8] = c2_22[12];
FA fa72 (c2_23[0], c2_23[1], c2_23[2], c3_23[4], c3_24[0]);
FA fa73 (c2_23[3], c2_23[4], c2_23[5], c3_23[5], c3_24[1]);
FA fa74 (c2_23[6], c2_23[7], c2_23[8], c3_23[6], c3_24[2]);
FA fa75 (c2_23[9], c2_23[10], c2_23[11], c3_23[7], c3_24[3]);
assign c3_23[8] = c2_23[12];
FA fa76 (c2_24[0], c2_24[1], c2_24[2], c3_24[4], c3_25[0]);
FA fa77 (c2_24[3], c2_24[4], c2_24[5], c3_24[5], c3_25[1]);
FA fa78 (c2_24[6], c2_24[7], c2_24[8], c3_24[6], c3_25[2]);
assign c3_24[7] = c2_24[9];
assign c3_24[8] = c2_24[10];
FA fa79 (c2_25[0], c2_25[1], c2_25[2], c3_25[3], c3_26[0]);
FA fa80 (c2_25[3], c2_25[4], c2_25[5], c3_25[4], c3_26[1]);
assign c3_25[5] = c2_25[6];
assign c3_25[6] = c2_25[7];
assign c3_25[7] = c2_25[8];
assign c3_25[8] = c2_25[9];
FA fa81 (c2_26[0], c2_26[1], c2_26[2], c3_26[2], c3_27[0]);
assign c3_26[3] = c2_26[3];
assign c3_26[4] = c2_26[4];
assign c3_26[5] = c2_26[5];
assign c3_26[6] = c2_26[6];
assign c3_26[7] = c2_26[7];
assign c3_26[8] = c2_26[8];
FA fa82 (c2_27[0], c2_27[1], c2_27[2], c3_27[1], c3_28[0]);
assign c3_27[2] = c2_27[3];
assign c3_27[3] = c2_27[4];
assign c3_27[4] = c2_27[5];
assign c3_27[5] = c2_27[6];
assign c3_27[6] = c2_27[7];
assign c3_27[7] = c2_27[8];
assign c3_27[8] = c2_27[9];
assign c3_28[1] = c2_28[0];
assign c3_28[2] = c2_28[1];
assign c3_28[3] = c2_28[2];
assign c3_28[4] = c2_28[3];
assign c3_28[5] = c2_28[4];
assign c3_28[6] = c2_28[5];
assign c3_28[7] = c2_28[6];
assign c3_29[0] = c2_29[0];
assign c3_29[1] = c2_29[1];
assign c3_29[2] = c2_29[2];
assign c3_29[3] = c2_29[3];
assign c3_29[4] = c2_29[4];
assign c3_29[5] = c2_29[5];
assign c3_30[0] = c2_30[0];
assign c3_30[1] = c2_30[1];
assign c3_30[2] = c2_30[2];
assign c3_30[3] = c2_30[3];
assign c3_30[4] = c2_30[4];
assign c3_31[0] = c2_31[0];
assign c3_31[1] = c2_31[1];
assign c3_31[2] = c2_31[2];
assign c3_31[3] = c2_31[3];
assign c3_32[0] = c2_32[0];
assign c3_32[1] = c2_32[1];
assign c3_32[2] = c2_32[2];
assign c3_33[0] = c2_33[0];
assign c3_33[1] = c2_33[1];
assign c3_34[0] = c2_34[0];
assign c3_34[1] = c2_34[1];
assign c3_34[2] = c2_34[2];
assign c3_35[0] = c2_35[0];
assign c3_35[1] = c2_35[1];

/***** Dadda Tree Stage 4 *****/
wire [0:0] c4_0;
wire [1:0] c4_1;
wire [2:0] c4_2;
wire [3:0] c4_3;
wire [4:0] c4_4;
wire [5:0] c4_5;
wire [5:0] c4_6;
wire [5:0] c4_7;
wire [5:0] c4_8;
wire [5:0] c4_9;
wire [5:0] c4_10;
wire [5:0] c4_11;
wire [5:0] c4_12;
wire [5:0] c4_13;
wire [5:0] c4_14;
wire [5:0] c4_15;
wire [5:0] c4_16;
wire [5:0] c4_17;
wire [5:0] c4_18;
wire [5:0] c4_19;
wire [5:0] c4_20;
wire [5:0] c4_21;
wire [5:0] c4_22;
wire [5:0] c4_23;
wire [5:0] c4_24;
wire [5:0] c4_25;
wire [5:0] c4_26;
wire [5:0] c4_27;
wire [5:0] c4_28;
wire [5:0] c4_29;
wire [5:0] c4_30;
wire [4:0] c4_31;
wire [2:0] c4_32;
wire [1:0] c4_33;
wire [2:0] c4_34;
wire [1:0] c4_35;

assign c4_0[0] = c3_0[0];
assign c4_1[0] = c3_1[0];
assign c4_1[1] = c3_1[1];
assign c4_2[0] = c3_2[0];
assign c4_2[1] = c3_2[1];
assign c4_2[2] = c3_2[2];
assign c4_3[0] = c3_3[0];
assign c4_3[1] = c3_3[1];
assign c4_3[2] = c3_3[2];
assign c4_3[3] = c3_3[3];
assign c4_4[0] = c3_4[0];
assign c4_4[1] = c3_4[1];
assign c4_4[2] = c3_4[2];
assign c4_4[3] = c3_4[3];
assign c4_4[4] = c3_4[4];
assign c4_5[0] = c3_5[0];
assign c4_5[1] = c3_5[1];
assign c4_5[2] = c3_5[2];
assign c4_5[3] = c3_5[3];
assign c4_5[4] = c3_5[4];
assign c4_5[5] = c3_5[5];
HA ha9 (c3_6[0], c3_6[1], c4_6[0], c4_7[0]);
assign c4_6[1] = c3_6[2];
assign c4_6[2] = c3_6[3];
assign c4_6[3] = c3_6[4];
assign c4_6[4] = c3_6[5];
assign c4_6[5] = c3_6[6];
FA fa83 (c3_7[0], c3_7[1], c3_7[2], c4_7[1], c4_8[0]);
HA ha10 (c3_7[3], c3_7[4], c4_7[2], c4_8[1]);
assign c4_7[3] = c3_7[5];
assign c4_7[4] = c3_7[6];
assign c4_7[5] = c3_7[7];
FA fa84 (c3_8[0], c3_8[1], c3_8[2], c4_8[2], c4_9[0]);
FA fa85 (c3_8[3], c3_8[4], c3_8[5], c4_8[3], c4_9[1]);
HA ha11 (c3_8[6], c3_8[7], c4_8[4], c4_9[2]);
assign c4_8[5] = c3_8[8];
FA fa86 (c3_9[0], c3_9[1], c3_9[2], c4_9[3], c4_10[0]);
FA fa87 (c3_9[3], c3_9[4], c3_9[5], c4_9[4], c4_10[1]);
FA fa88 (c3_9[6], c3_9[7], c3_9[8], c4_9[5], c4_10[2]);
FA fa89 (c3_10[0], c3_10[1], c3_10[2], c4_10[3], c4_11[0]);
FA fa90 (c3_10[3], c3_10[4], c3_10[5], c4_10[4], c4_11[1]);
FA fa91 (c3_10[6], c3_10[7], c3_10[8], c4_10[5], c4_11[2]);
FA fa92 (c3_11[0], c3_11[1], c3_11[2], c4_11[3], c4_12[0]);
FA fa93 (c3_11[3], c3_11[4], c3_11[5], c4_11[4], c4_12[1]);
FA fa94 (c3_11[6], c3_11[7], c3_11[8], c4_11[5], c4_12[2]);
FA fa95 (c3_12[0], c3_12[1], c3_12[2], c4_12[3], c4_13[0]);
FA fa96 (c3_12[3], c3_12[4], c3_12[5], c4_12[4], c4_13[1]);
FA fa97 (c3_12[6], c3_12[7], c3_12[8], c4_12[5], c4_13[2]);
FA fa98 (c3_13[0], c3_13[1], c3_13[2], c4_13[3], c4_14[0]);
FA fa99 (c3_13[3], c3_13[4], c3_13[5], c4_13[4], c4_14[1]);
FA fa100 (c3_13[6], c3_13[7], c3_13[8], c4_13[5], c4_14[2]);
FA fa101 (c3_14[0], c3_14[1], c3_14[2], c4_14[3], c4_15[0]);
FA fa102 (c3_14[3], c3_14[4], c3_14[5], c4_14[4], c4_15[1]);
FA fa103 (c3_14[6], c3_14[7], c3_14[8], c4_14[5], c4_15[2]);
FA fa104 (c3_15[0], c3_15[1], c3_15[2], c4_15[3], c4_16[0]);
FA fa105 (c3_15[3], c3_15[4], c3_15[5], c4_15[4], c4_16[1]);
FA fa106 (c3_15[6], c3_15[7], c3_15[8], c4_15[5], c4_16[2]);
FA fa107 (c3_16[0], c3_16[1], c3_16[2], c4_16[3], c4_17[0]);
FA fa108 (c3_16[3], c3_16[4], c3_16[5], c4_16[4], c4_17[1]);
FA fa109 (c3_16[6], c3_16[7], c3_16[8], c4_16[5], c4_17[2]);
FA fa110 (c3_17[0], c3_17[1], c3_17[2], c4_17[3], c4_18[0]);
FA fa111 (c3_17[3], c3_17[4], c3_17[5], c4_17[4], c4_18[1]);
FA fa112 (c3_17[6], c3_17[7], c3_17[8], c4_17[5], c4_18[2]);
FA fa113 (c3_18[0], c3_18[1], c3_18[2], c4_18[3], c4_19[0]);
FA fa114 (c3_18[3], c3_18[4], c3_18[5], c4_18[4], c4_19[1]);
FA fa115 (c3_18[6], c3_18[7], c3_18[8], c4_18[5], c4_19[2]);
FA fa116 (c3_19[0], c3_19[1], c3_19[2], c4_19[3], c4_20[0]);
FA fa117 (c3_19[3], c3_19[4], c3_19[5], c4_19[4], c4_20[1]);
FA fa118 (c3_19[6], c3_19[7], c3_19[8], c4_19[5], c4_20[2]);
FA fa119 (c3_20[0], c3_20[1], c3_20[2], c4_20[3], c4_21[0]);
FA fa120 (c3_20[3], c3_20[4], c3_20[5], c4_20[4], c4_21[1]);
FA fa121 (c3_20[6], c3_20[7], c3_20[8], c4_20[5], c4_21[2]);
FA fa122 (c3_21[0], c3_21[1], c3_21[2], c4_21[3], c4_22[0]);
FA fa123 (c3_21[3], c3_21[4], c3_21[5], c4_21[4], c4_22[1]);
FA fa124 (c3_21[6], c3_21[7], c3_21[8], c4_21[5], c4_22[2]);
FA fa125 (c3_22[0], c3_22[1], c3_22[2], c4_22[3], c4_23[0]);
FA fa126 (c3_22[3], c3_22[4], c3_22[5], c4_22[4], c4_23[1]);
FA fa127 (c3_22[6], c3_22[7], c3_22[8], c4_22[5], c4_23[2]);
FA fa128 (c3_23[0], c3_23[1], c3_23[2], c4_23[3], c4_24[0]);
FA fa129 (c3_23[3], c3_23[4], c3_23[5], c4_23[4], c4_24[1]);
FA fa130 (c3_23[6], c3_23[7], c3_23[8], c4_23[5], c4_24[2]);
FA fa131 (c3_24[0], c3_24[1], c3_24[2], c4_24[3], c4_25[0]);
FA fa132 (c3_24[3], c3_24[4], c3_24[5], c4_24[4], c4_25[1]);
FA fa133 (c3_24[6], c3_24[7], c3_24[8], c4_24[5], c4_25[2]);
FA fa134 (c3_25[0], c3_25[1], c3_25[2], c4_25[3], c4_26[0]);
FA fa135 (c3_25[3], c3_25[4], c3_25[5], c4_25[4], c4_26[1]);
FA fa136 (c3_25[6], c3_25[7], c3_25[8], c4_25[5], c4_26[2]);
FA fa137 (c3_26[0], c3_26[1], c3_26[2], c4_26[3], c4_27[0]);
FA fa138 (c3_26[3], c3_26[4], c3_26[5], c4_26[4], c4_27[1]);
FA fa139 (c3_26[6], c3_26[7], c3_26[8], c4_26[5], c4_27[2]);
FA fa140 (c3_27[0], c3_27[1], c3_27[2], c4_27[3], c4_28[0]);
FA fa141 (c3_27[3], c3_27[4], c3_27[5], c4_27[4], c4_28[1]);
FA fa142 (c3_27[6], c3_27[7], c3_27[8], c4_27[5], c4_28[2]);
FA fa143 (c3_28[0], c3_28[1], c3_28[2], c4_28[3], c4_29[0]);
FA fa144 (c3_28[3], c3_28[4], c3_28[5], c4_28[4], c4_29[1]);
HA ha12 (c3_28[6], c3_28[7], c4_28[5], c4_29[2]);
FA fa145 (c3_29[0], c3_29[1], c3_29[2], c4_29[3], c4_30[0]);
HA ha13 (c3_29[3], c3_29[4], c4_29[4], c4_30[1]);
assign c4_29[5] = c3_29[5];
HA ha14 (c3_30[0], c3_30[1], c4_30[2], c4_31[0]);
assign c4_30[3] = c3_30[2];
assign c4_30[4] = c3_30[3];
assign c4_30[5] = c3_30[4];
assign c4_31[1] = c3_31[0];
assign c4_31[2] = c3_31[1];
assign c4_31[3] = c3_31[2];
assign c4_31[4] = c3_31[3];
assign c4_32[0] = c3_32[0];
assign c4_32[1] = c3_32[1];
assign c4_32[2] = c3_32[2];
assign c4_33[0] = c3_33[0];
assign c4_33[1] = c3_33[1];
assign c4_34[0] = c3_34[0];
assign c4_34[1] = c3_34[1];
assign c4_34[2] = c3_34[2];
assign c4_35[0] = c3_35[0];
assign c4_35[1] = c3_35[1];

/***** Dadda Tree Stage 5 *****/
wire [0:0] c5_0;
wire [1:0] c5_1;
wire [2:0] c5_2;
wire [3:0] c5_3;
wire [3:0] c5_4;
wire [3:0] c5_5;
wire [3:0] c5_6;
wire [3:0] c5_7;
wire [3:0] c5_8;
wire [3:0] c5_9;
wire [3:0] c5_10;
wire [3:0] c5_11;
wire [3:0] c5_12;
wire [3:0] c5_13;
wire [3:0] c5_14;
wire [3:0] c5_15;
wire [3:0] c5_16;
wire [3:0] c5_17;
wire [3:0] c5_18;
wire [3:0] c5_19;
wire [3:0] c5_20;
wire [3:0] c5_21;
wire [3:0] c5_22;
wire [3:0] c5_23;
wire [3:0] c5_24;
wire [3:0] c5_25;
wire [3:0] c5_26;
wire [3:0] c5_27;
wire [3:0] c5_28;
wire [3:0] c5_29;
wire [3:0] c5_30;
wire [3:0] c5_31;
wire [3:0] c5_32;
wire [2:0] c5_33;
wire [2:0] c5_34;
wire [1:0] c5_35;

assign c5_0[0] = c4_0[0];
assign c5_1[0] = c4_1[0];
assign c5_1[1] = c4_1[1];
assign c5_2[0] = c4_2[0];
assign c5_2[1] = c4_2[1];
assign c5_2[2] = c4_2[2];
assign c5_3[0] = c4_3[0];
assign c5_3[1] = c4_3[1];
assign c5_3[2] = c4_3[2];
assign c5_3[3] = c4_3[3];
HA ha15 (c4_4[0], c4_4[1], c5_4[0], c5_5[0]);
assign c5_4[1] = c4_4[2];
assign c5_4[2] = c4_4[3];
assign c5_4[3] = c4_4[4];
FA fa146 (c4_5[0], c4_5[1], c4_5[2], c5_5[1], c5_6[0]);
HA ha16 (c4_5[3], c4_5[4], c5_5[2], c5_6[1]);
assign c5_5[3] = c4_5[5];
FA fa147 (c4_6[0], c4_6[1], c4_6[2], c5_6[2], c5_7[0]);
FA fa148 (c4_6[3], c4_6[4], c4_6[5], c5_6[3], c5_7[1]);
FA fa149 (c4_7[0], c4_7[1], c4_7[2], c5_7[2], c5_8[0]);
FA fa150 (c4_7[3], c4_7[4], c4_7[5], c5_7[3], c5_8[1]);
FA fa151 (c4_8[0], c4_8[1], c4_8[2], c5_8[2], c5_9[0]);
FA fa152 (c4_8[3], c4_8[4], c4_8[5], c5_8[3], c5_9[1]);
FA fa153 (c4_9[0], c4_9[1], c4_9[2], c5_9[2], c5_10[0]);
FA fa154 (c4_9[3], c4_9[4], c4_9[5], c5_9[3], c5_10[1]);
FA fa155 (c4_10[0], c4_10[1], c4_10[2], c5_10[2], c5_11[0]);
FA fa156 (c4_10[3], c4_10[4], c4_10[5], c5_10[3], c5_11[1]);
FA fa157 (c4_11[0], c4_11[1], c4_11[2], c5_11[2], c5_12[0]);
FA fa158 (c4_11[3], c4_11[4], c4_11[5], c5_11[3], c5_12[1]);
FA fa159 (c4_12[0], c4_12[1], c4_12[2], c5_12[2], c5_13[0]);
FA fa160 (c4_12[3], c4_12[4], c4_12[5], c5_12[3], c5_13[1]);
FA fa161 (c4_13[0], c4_13[1], c4_13[2], c5_13[2], c5_14[0]);
FA fa162 (c4_13[3], c4_13[4], c4_13[5], c5_13[3], c5_14[1]);
FA fa163 (c4_14[0], c4_14[1], c4_14[2], c5_14[2], c5_15[0]);
FA fa164 (c4_14[3], c4_14[4], c4_14[5], c5_14[3], c5_15[1]);
FA fa165 (c4_15[0], c4_15[1], c4_15[2], c5_15[2], c5_16[0]);
FA fa166 (c4_15[3], c4_15[4], c4_15[5], c5_15[3], c5_16[1]);
FA fa167 (c4_16[0], c4_16[1], c4_16[2], c5_16[2], c5_17[0]);
FA fa168 (c4_16[3], c4_16[4], c4_16[5], c5_16[3], c5_17[1]);
FA fa169 (c4_17[0], c4_17[1], c4_17[2], c5_17[2], c5_18[0]);
FA fa170 (c4_17[3], c4_17[4], c4_17[5], c5_17[3], c5_18[1]);
FA fa171 (c4_18[0], c4_18[1], c4_18[2], c5_18[2], c5_19[0]);
FA fa172 (c4_18[3], c4_18[4], c4_18[5], c5_18[3], c5_19[1]);
FA fa173 (c4_19[0], c4_19[1], c4_19[2], c5_19[2], c5_20[0]);
FA fa174 (c4_19[3], c4_19[4], c4_19[5], c5_19[3], c5_20[1]);
FA fa175 (c4_20[0], c4_20[1], c4_20[2], c5_20[2], c5_21[0]);
FA fa176 (c4_20[3], c4_20[4], c4_20[5], c5_20[3], c5_21[1]);
FA fa177 (c4_21[0], c4_21[1], c4_21[2], c5_21[2], c5_22[0]);
FA fa178 (c4_21[3], c4_21[4], c4_21[5], c5_21[3], c5_22[1]);
FA fa179 (c4_22[0], c4_22[1], c4_22[2], c5_22[2], c5_23[0]);
FA fa180 (c4_22[3], c4_22[4], c4_22[5], c5_22[3], c5_23[1]);
FA fa181 (c4_23[0], c4_23[1], c4_23[2], c5_23[2], c5_24[0]);
FA fa182 (c4_23[3], c4_23[4], c4_23[5], c5_23[3], c5_24[1]);
FA fa183 (c4_24[0], c4_24[1], c4_24[2], c5_24[2], c5_25[0]);
FA fa184 (c4_24[3], c4_24[4], c4_24[5], c5_24[3], c5_25[1]);
FA fa185 (c4_25[0], c4_25[1], c4_25[2], c5_25[2], c5_26[0]);
FA fa186 (c4_25[3], c4_25[4], c4_25[5], c5_25[3], c5_26[1]);
FA fa187 (c4_26[0], c4_26[1], c4_26[2], c5_26[2], c5_27[0]);
FA fa188 (c4_26[3], c4_26[4], c4_26[5], c5_26[3], c5_27[1]);
FA fa189 (c4_27[0], c4_27[1], c4_27[2], c5_27[2], c5_28[0]);
FA fa190 (c4_27[3], c4_27[4], c4_27[5], c5_27[3], c5_28[1]);
FA fa191 (c4_28[0], c4_28[1], c4_28[2], c5_28[2], c5_29[0]);
FA fa192 (c4_28[3], c4_28[4], c4_28[5], c5_28[3], c5_29[1]);
FA fa193 (c4_29[0], c4_29[1], c4_29[2], c5_29[2], c5_30[0]);
FA fa194 (c4_29[3], c4_29[4], c4_29[5], c5_29[3], c5_30[1]);
FA fa195 (c4_30[0], c4_30[1], c4_30[2], c5_30[2], c5_31[0]);
FA fa196 (c4_30[3], c4_30[4], c4_30[5], c5_30[3], c5_31[1]);
FA fa197 (c4_31[0], c4_31[1], c4_31[2], c5_31[2], c5_32[0]);
HA ha17 (c4_31[3], c4_31[4], c5_31[3], c5_32[1]);
HA ha18 (c4_32[0], c4_32[1], c5_32[2], c5_33[0]);
assign c5_32[3] = c4_32[2];
assign c5_33[1] = c4_33[0];
assign c5_33[2] = c4_33[1];
assign c5_34[0] = c4_34[0];
assign c5_34[1] = c4_34[1];
assign c5_34[2] = c4_34[2];
assign c5_35[0] = c4_35[0];
assign c5_35[1] = c4_35[1];

/***** Dadda Tree Stage 6 *****/
wire [0:0] c6_0;
wire [1:0] c6_1;
wire [2:0] c6_2;
wire [2:0] c6_3;
wire [2:0] c6_4;
wire [2:0] c6_5;
wire [2:0] c6_6;
wire [2:0] c6_7;
wire [2:0] c6_8;
wire [2:0] c6_9;
wire [2:0] c6_10;
wire [2:0] c6_11;
wire [2:0] c6_12;
wire [2:0] c6_13;
wire [2:0] c6_14;
wire [2:0] c6_15;
wire [2:0] c6_16;
wire [2:0] c6_17;
wire [2:0] c6_18;
wire [2:0] c6_19;
wire [2:0] c6_20;
wire [2:0] c6_21;
wire [2:0] c6_22;
wire [2:0] c6_23;
wire [2:0] c6_24;
wire [2:0] c6_25;
wire [2:0] c6_26;
wire [2:0] c6_27;
wire [2:0] c6_28;
wire [2:0] c6_29;
wire [2:0] c6_30;
wire [2:0] c6_31;
wire [2:0] c6_32;
wire [2:0] c6_33;
wire [2:0] c6_34;
wire [2:0] c6_35;

assign c6_0[0] = c5_0[0];
assign c6_1[0] = c5_1[0];
assign c6_1[1] = c5_1[1];
assign c6_2[0] = c5_2[0];
assign c6_2[1] = c5_2[1];
assign c6_2[2] = c5_2[2];
HA ha19 (c5_3[0], c5_3[1], c6_3[0], c6_4[0]);
assign c6_3[1] = c5_3[2];
assign c6_3[2] = c5_3[3];
FA fa198 (c5_4[0], c5_4[1], c5_4[2], c6_4[1], c6_5[0]);
assign c6_4[2] = c5_4[3];
FA fa199 (c5_5[0], c5_5[1], c5_5[2], c6_5[1], c6_6[0]);
assign c6_5[2] = c5_5[3];
FA fa200 (c5_6[0], c5_6[1], c5_6[2], c6_6[1], c6_7[0]);
assign c6_6[2] = c5_6[3];
FA fa201 (c5_7[0], c5_7[1], c5_7[2], c6_7[1], c6_8[0]);
assign c6_7[2] = c5_7[3];
FA fa202 (c5_8[0], c5_8[1], c5_8[2], c6_8[1], c6_9[0]);
assign c6_8[2] = c5_8[3];
FA fa203 (c5_9[0], c5_9[1], c5_9[2], c6_9[1], c6_10[0]);
assign c6_9[2] = c5_9[3];
FA fa204 (c5_10[0], c5_10[1], c5_10[2], c6_10[1], c6_11[0]);
assign c6_10[2] = c5_10[3];
FA fa205 (c5_11[0], c5_11[1], c5_11[2], c6_11[1], c6_12[0]);
assign c6_11[2] = c5_11[3];
FA fa206 (c5_12[0], c5_12[1], c5_12[2], c6_12[1], c6_13[0]);
assign c6_12[2] = c5_12[3];
FA fa207 (c5_13[0], c5_13[1], c5_13[2], c6_13[1], c6_14[0]);
assign c6_13[2] = c5_13[3];
FA fa208 (c5_14[0], c5_14[1], c5_14[2], c6_14[1], c6_15[0]);
assign c6_14[2] = c5_14[3];
FA fa209 (c5_15[0], c5_15[1], c5_15[2], c6_15[1], c6_16[0]);
assign c6_15[2] = c5_15[3];
FA fa210 (c5_16[0], c5_16[1], c5_16[2], c6_16[1], c6_17[0]);
assign c6_16[2] = c5_16[3];
FA fa211 (c5_17[0], c5_17[1], c5_17[2], c6_17[1], c6_18[0]);
assign c6_17[2] = c5_17[3];
FA fa212 (c5_18[0], c5_18[1], c5_18[2], c6_18[1], c6_19[0]);
assign c6_18[2] = c5_18[3];
FA fa213 (c5_19[0], c5_19[1], c5_19[2], c6_19[1], c6_20[0]);
assign c6_19[2] = c5_19[3];
FA fa214 (c5_20[0], c5_20[1], c5_20[2], c6_20[1], c6_21[0]);
assign c6_20[2] = c5_20[3];
FA fa215 (c5_21[0], c5_21[1], c5_21[2], c6_21[1], c6_22[0]);
assign c6_21[2] = c5_21[3];
FA fa216 (c5_22[0], c5_22[1], c5_22[2], c6_22[1], c6_23[0]);
assign c6_22[2] = c5_22[3];
FA fa217 (c5_23[0], c5_23[1], c5_23[2], c6_23[1], c6_24[0]);
assign c6_23[2] = c5_23[3];
FA fa218 (c5_24[0], c5_24[1], c5_24[2], c6_24[1], c6_25[0]);
assign c6_24[2] = c5_24[3];
FA fa219 (c5_25[0], c5_25[1], c5_25[2], c6_25[1], c6_26[0]);
assign c6_25[2] = c5_25[3];
FA fa220 (c5_26[0], c5_26[1], c5_26[2], c6_26[1], c6_27[0]);
assign c6_26[2] = c5_26[3];
FA fa221 (c5_27[0], c5_27[1], c5_27[2], c6_27[1], c6_28[0]);
assign c6_27[2] = c5_27[3];
FA fa222 (c5_28[0], c5_28[1], c5_28[2], c6_28[1], c6_29[0]);
assign c6_28[2] = c5_28[3];
FA fa223 (c5_29[0], c5_29[1], c5_29[2], c6_29[1], c6_30[0]);
assign c6_29[2] = c5_29[3];
FA fa224 (c5_30[0], c5_30[1], c5_30[2], c6_30[1], c6_31[0]);
assign c6_30[2] = c5_30[3];
FA fa225 (c5_31[0], c5_31[1], c5_31[2], c6_31[1], c6_32[0]);
assign c6_31[2] = c5_31[3];
FA fa226 (c5_32[0], c5_32[1], c5_32[2], c6_32[1], c6_33[0]);
assign c6_32[2] = c5_32[3];
HA ha20 (c5_33[0], c5_33[1], c6_33[1], c6_34[0]);
assign c6_33[2] = c5_33[2];
HA ha21 (c5_34[0], c5_34[1], c6_34[1], c6_35[0]);
assign c6_34[2] = c5_34[2];
assign c6_35[1] = c5_35[0];
assign c6_35[2] = c5_35[1];

/***** Dadda Tree Stage 7 *****/
wire [0:0] c7_0;
wire [1:0] c7_1;
wire [1:0] c7_2;
wire [1:0] c7_3;
wire [1:0] c7_4;
wire [1:0] c7_5;
wire [1:0] c7_6;
wire [1:0] c7_7;
wire [1:0] c7_8;
wire [1:0] c7_9;
wire [1:0] c7_10;
wire [1:0] c7_11;
wire [1:0] c7_12;
wire [1:0] c7_13;
wire [1:0] c7_14;
wire [1:0] c7_15;
wire [1:0] c7_16;
wire [1:0] c7_17;
wire [1:0] c7_18;
wire [1:0] c7_19;
wire [1:0] c7_20;
wire [1:0] c7_21;
wire [1:0] c7_22;
wire [1:0] c7_23;
wire [1:0] c7_24;
wire [1:0] c7_25;
wire [1:0] c7_26;
wire [1:0] c7_27;
wire [1:0] c7_28;
wire [1:0] c7_29;
wire [1:0] c7_30;
wire [1:0] c7_31;
wire [1:0] c7_32;
wire [1:0] c7_33;
wire [1:0] c7_34;
wire [1:0] c7_35;
wire [0:0] c7_36;

assign c7_0[0] = c6_0[0];
assign c7_1[0] = c6_1[0];
assign c7_1[1] = c6_1[1];
HA ha22 (c6_2[0], c6_2[1], c7_2[0], c7_3[0]);
assign c7_2[1] = c6_2[2];
FA fa227 (c6_3[0], c6_3[1], c6_3[2], c7_3[1], c7_4[0]);
FA fa228 (c6_4[0], c6_4[1], c6_4[2], c7_4[1], c7_5[0]);
FA fa229 (c6_5[0], c6_5[1], c6_5[2], c7_5[1], c7_6[0]);
FA fa230 (c6_6[0], c6_6[1], c6_6[2], c7_6[1], c7_7[0]);
FA fa231 (c6_7[0], c6_7[1], c6_7[2], c7_7[1], c7_8[0]);
FA fa232 (c6_8[0], c6_8[1], c6_8[2], c7_8[1], c7_9[0]);
FA fa233 (c6_9[0], c6_9[1], c6_9[2], c7_9[1], c7_10[0]);
FA fa234 (c6_10[0], c6_10[1], c6_10[2], c7_10[1], c7_11[0]);
FA fa235 (c6_11[0], c6_11[1], c6_11[2], c7_11[1], c7_12[0]);
FA fa236 (c6_12[0], c6_12[1], c6_12[2], c7_12[1], c7_13[0]);
FA fa237 (c6_13[0], c6_13[1], c6_13[2], c7_13[1], c7_14[0]);
FA fa238 (c6_14[0], c6_14[1], c6_14[2], c7_14[1], c7_15[0]);
FA fa239 (c6_15[0], c6_15[1], c6_15[2], c7_15[1], c7_16[0]);
FA fa240 (c6_16[0], c6_16[1], c6_16[2], c7_16[1], c7_17[0]);
FA fa241 (c6_17[0], c6_17[1], c6_17[2], c7_17[1], c7_18[0]);
FA fa242 (c6_18[0], c6_18[1], c6_18[2], c7_18[1], c7_19[0]);
FA fa243 (c6_19[0], c6_19[1], c6_19[2], c7_19[1], c7_20[0]);
FA fa244 (c6_20[0], c6_20[1], c6_20[2], c7_20[1], c7_21[0]);
FA fa245 (c6_21[0], c6_21[1], c6_21[2], c7_21[1], c7_22[0]);
FA fa246 (c6_22[0], c6_22[1], c6_22[2], c7_22[1], c7_23[0]);
FA fa247 (c6_23[0], c6_23[1], c6_23[2], c7_23[1], c7_24[0]);
FA fa248 (c6_24[0], c6_24[1], c6_24[2], c7_24[1], c7_25[0]);
FA fa249 (c6_25[0], c6_25[1], c6_25[2], c7_25[1], c7_26[0]);
FA fa250 (c6_26[0], c6_26[1], c6_26[2], c7_26[1], c7_27[0]);
FA fa251 (c6_27[0], c6_27[1], c6_27[2], c7_27[1], c7_28[0]);
FA fa252 (c6_28[0], c6_28[1], c6_28[2], c7_28[1], c7_29[0]);
FA fa253 (c6_29[0], c6_29[1], c6_29[2], c7_29[1], c7_30[0]);
FA fa254 (c6_30[0], c6_30[1], c6_30[2], c7_30[1], c7_31[0]);
FA fa255 (c6_31[0], c6_31[1], c6_31[2], c7_31[1], c7_32[0]);
FA fa256 (c6_32[0], c6_32[1], c6_32[2], c7_32[1], c7_33[0]);
FA fa257 (c6_33[0], c6_33[1], c6_33[2], c7_33[1], c7_34[0]);
FA fa258 (c6_34[0], c6_34[1], c6_34[2], c7_34[1], c7_35[0]);
FA fa259 (c6_35[0], c6_35[1], c6_35[2], c7_35[1], c7_36[0]);

assign sum = {c7_35[0],c7_34[0],c7_33[0],c7_32[0],c7_31[0],c7_30[0],c7_29[0],c7_28[0],c7_27[0],c7_26[0],c7_25[0],c7_24[0],c7_23[0],c7_22[0],c7_21[0],c7_20[0],c7_19[0],c7_18[0],c7_17[0],c7_16[0],c7_15[0],c7_14[0],c7_13[0],c7_12[0],c7_11[0],c7_10[0],c7_9[0],c7_8[0],c7_7[0],c7_6[0],c7_5[0],c7_4[0],c7_3[0],c7_2[0],c7_1[0],c7_0[0]};
assign carry = {c7_35[1],c7_34[1],c7_33[1],c7_32[1],c7_31[1],c7_30[1],c7_29[1],c7_28[1],c7_27[1],c7_26[1],c7_25[1],c7_24[1],c7_23[1],c7_22[1],c7_21[1],c7_20[1],c7_19[1],c7_18[1],c7_17[1],c7_16[1],c7_15[1],c7_14[1],c7_13[1],c7_12[1],c7_11[1],c7_10[1],c7_9[1],c7_8[1],c7_7[1],c7_6[1],c7_5[1],c7_4[1],c7_3[1],c7_2[1],c7_1[1], 1'b0};

endmodule

module multiplier_9x18_lsb (
	input  clk,
	input  [8:0] data_x,
	input  [17:0] data_y,
	input  signed_x,
	input  signed_y,
	input  signed_c,
	input  flv0,
	input  flv1,
	input  flv2,
	input  suppress_sign_x,
	input  suppress_sign_y,
	input  suppress_sign_e,
	output [26:0] sum,
	output [26:0] carry
);

wire [17:0] PP [8:0];
wire [26:0] dadda_sum, dadda_carry;
reg [8:0] x;
reg [17:0] y;
reg sign_x;
reg sign_y;
reg sign_c;
reg [26:0] s;
reg [26:0] c;

always @ (*)
begin: reg_in_out
	x <= data_x;
	y <= data_y;
	sign_x <= signed_x;
	sign_y <= signed_y;
	sign_c <= signed_c;
	s <= dadda_sum;
	c <= dadda_carry;
end

arrayBlock_unsigned BLK0 (.A(y[0]), .B(x[0]), .mult(PP[0][0]));
arrayBlock_unsigned BLK1 (.A(y[1]), .B(x[0]), .mult(PP[0][1]));
arrayBlock_unsigned BLK2 (.A(y[2]), .B(x[0]), .mult(PP[0][2]));
arrayBlock_unsigned BLK3 (.A(y[3]), .B(x[0]), .mult(PP[0][3]));
arrayBlock_unsigned BLK4 (.A(y[4]), .B(x[0]), .mult(PP[0][4]));
arrayBlock_unsigned BLK5 (.A(y[5]), .B(x[0]), .mult(PP[0][5]));
arrayBlock_unsigned BLK6 (.A(y[6]), .B(x[0]), .mult(PP[0][6]));
arrayBlock_unsigned BLK7 (.A(y[7]), .B(x[0]), .mult(PP[0][7]));
arrayBlock_signed BLK8 (.A(y[8]), .B(x[0]), .signed_ctrl(sign_y & (flv1)), .mult(PP[0][8]));
arrayBlock_unsigned BLK9 (.A(y[9]), .B(x[0]), .mult(PP[0][9]));
arrayBlock_unsigned BLK10 (.A(y[10]), .B(x[0]), .mult(PP[0][10]));
arrayBlock_unsigned BLK11 (.A(y[11]), .B(x[0]), .mult(PP[0][11]));
arrayBlock_unsigned BLK12 (.A(y[12]), .B(x[0]), .mult(PP[0][12]));
arrayBlock_unsigned BLK13 (.A(y[13]), .B(x[0]), .mult(PP[0][13]));
arrayBlock_unsigned BLK14 (.A(y[14]), .B(x[0]), .mult(PP[0][14]));
arrayBlock_unsigned BLK15 (.A(y[15]), .B(x[0]), .mult(PP[0][15]));
arrayBlock_unsigned BLK16 (.A(y[16]), .B(x[0]), .mult(PP[0][16]));
arrayBlock_signed BLK17 (.A(y[17]), .B(x[0]), .signed_ctrl(sign_y & (flv0)), .mult(PP[0][17]));
arrayBlock_unsigned BLK18 (.A(y[0]), .B(x[1]), .mult(PP[1][0]));
arrayBlock_unsigned BLK19 (.A(y[1]), .B(x[1]), .mult(PP[1][1]));
arrayBlock_unsigned BLK20 (.A(y[2]), .B(x[1]), .mult(PP[1][2]));
arrayBlock_unsigned BLK21 (.A(y[3]), .B(x[1]), .mult(PP[1][3]));
arrayBlock_unsigned BLK22 (.A(y[4]), .B(x[1]), .mult(PP[1][4]));
arrayBlock_unsigned BLK23 (.A(y[5]), .B(x[1]), .mult(PP[1][5]));
arrayBlock_unsigned BLK24 (.A(y[6]), .B(x[1]), .mult(PP[1][6]));
arrayBlock_unsigned BLK25 (.A(y[7]), .B(x[1]), .mult(PP[1][7]));
arrayBlock_signed BLK26 (.A(y[8]), .B(x[1]), .signed_ctrl(sign_y & (flv1)), .mult(PP[1][8]));
arrayBlock_unsigned BLK27 (.A(y[9]), .B(x[1]), .mult(PP[1][9]));
arrayBlock_unsigned BLK28 (.A(y[10]), .B(x[1]), .mult(PP[1][10]));
arrayBlock_unsigned BLK29 (.A(y[11]), .B(x[1]), .mult(PP[1][11]));
arrayBlock_unsigned BLK30 (.A(y[12]), .B(x[1]), .mult(PP[1][12]));
arrayBlock_unsigned BLK31 (.A(y[13]), .B(x[1]), .mult(PP[1][13]));
arrayBlock_unsigned BLK32 (.A(y[14]), .B(x[1]), .mult(PP[1][14]));
arrayBlock_unsigned BLK33 (.A(y[15]), .B(x[1]), .mult(PP[1][15]));
arrayBlock_unsigned BLK34 (.A(y[16]), .B(x[1]), .mult(PP[1][16]));
arrayBlock_signed BLK35 (.A(y[17]), .B(x[1]), .signed_ctrl(sign_y & (flv0)), .mult(PP[1][17]));
arrayBlock_unsigned BLK36 (.A(y[0]), .B(x[2]), .mult(PP[2][0]));
arrayBlock_unsigned BLK37 (.A(y[1]), .B(x[2]), .mult(PP[2][1]));
arrayBlock_unsigned BLK38 (.A(y[2]), .B(x[2]), .mult(PP[2][2]));
arrayBlock_unsigned BLK39 (.A(y[3]), .B(x[2]), .mult(PP[2][3]));
arrayBlock_unsigned BLK40 (.A(y[4]), .B(x[2]), .mult(PP[2][4]));
arrayBlock_unsigned BLK41 (.A(y[5]), .B(x[2]), .mult(PP[2][5]));
arrayBlock_unsigned BLK42 (.A(y[6]), .B(x[2]), .mult(PP[2][6]));
arrayBlock_unsigned BLK43 (.A(y[7]), .B(x[2]), .mult(PP[2][7]));
arrayBlock_signed BLK44 (.A(y[8]), .B(x[2]), .signed_ctrl(sign_y & (flv1)), .mult(PP[2][8]));
arrayBlock_unsigned BLK45 (.A(y[9]), .B(x[2]), .mult(PP[2][9]));
arrayBlock_unsigned BLK46 (.A(y[10]), .B(x[2]), .mult(PP[2][10]));
arrayBlock_unsigned BLK47 (.A(y[11]), .B(x[2]), .mult(PP[2][11]));
arrayBlock_unsigned BLK48 (.A(y[12]), .B(x[2]), .mult(PP[2][12]));
arrayBlock_unsigned BLK49 (.A(y[13]), .B(x[2]), .mult(PP[2][13]));
arrayBlock_unsigned BLK50 (.A(y[14]), .B(x[2]), .mult(PP[2][14]));
arrayBlock_unsigned BLK51 (.A(y[15]), .B(x[2]), .mult(PP[2][15]));
arrayBlock_unsigned BLK52 (.A(y[16]), .B(x[2]), .mult(PP[2][16]));
arrayBlock_signed BLK53 (.A(y[17]), .B(x[2]), .signed_ctrl(sign_y & (flv0)), .mult(PP[2][17]));
arrayBlock_unsigned BLK54 (.A(y[0]), .B(x[3]), .mult(PP[3][0]));
arrayBlock_unsigned BLK55 (.A(y[1]), .B(x[3]), .mult(PP[3][1]));
arrayBlock_unsigned BLK56 (.A(y[2]), .B(x[3]), .mult(PP[3][2]));
arrayBlock_unsigned BLK57 (.A(y[3]), .B(x[3]), .mult(PP[3][3]));
arrayBlock_unsigned BLK58 (.A(y[4]), .B(x[3]), .mult(PP[3][4]));
arrayBlock_unsigned BLK59 (.A(y[5]), .B(x[3]), .mult(PP[3][5]));
arrayBlock_unsigned BLK60 (.A(y[6]), .B(x[3]), .mult(PP[3][6]));
arrayBlock_unsigned BLK61 (.A(y[7]), .B(x[3]), .mult(PP[3][7]));
arrayBlock_signed BLK62 (.A(y[8]), .B(x[3]), .signed_ctrl(sign_y & (flv1)), .mult(PP[3][8]));
arrayBlock_unsigned BLK63 (.A(y[9]), .B(x[3]), .mult(PP[3][9]));
arrayBlock_unsigned BLK64 (.A(y[10]), .B(x[3]), .mult(PP[3][10]));
arrayBlock_unsigned BLK65 (.A(y[11]), .B(x[3]), .mult(PP[3][11]));
arrayBlock_unsigned BLK66 (.A(y[12]), .B(x[3]), .mult(PP[3][12]));
arrayBlock_unsigned BLK67 (.A(y[13]), .B(x[3]), .mult(PP[3][13]));
arrayBlock_unsigned BLK68 (.A(y[14]), .B(x[3]), .mult(PP[3][14]));
arrayBlock_unsigned BLK69 (.A(y[15]), .B(x[3]), .mult(PP[3][15]));
arrayBlock_unsigned BLK70 (.A(y[16]), .B(x[3]), .mult(PP[3][16]));
arrayBlock_signed BLK71 (.A(y[17]), .B(x[3]), .signed_ctrl(sign_y & (flv0)), .mult(PP[3][17]));
arrayBlock_unsigned BLK72 (.A(y[0]), .B(x[4]), .mult(PP[4][0]));
arrayBlock_unsigned BLK73 (.A(y[1]), .B(x[4]), .mult(PP[4][1]));
arrayBlock_unsigned BLK74 (.A(y[2]), .B(x[4]), .mult(PP[4][2]));
arrayBlock_unsigned BLK75 (.A(y[3]), .B(x[4]), .mult(PP[4][3]));
arrayBlock_unsigned BLK76 (.A(y[4]), .B(x[4]), .mult(PP[4][4]));
arrayBlock_unsigned BLK77 (.A(y[5]), .B(x[4]), .mult(PP[4][5]));
arrayBlock_unsigned BLK78 (.A(y[6]), .B(x[4]), .mult(PP[4][6]));
arrayBlock_unsigned BLK79 (.A(y[7]), .B(x[4]), .mult(PP[4][7]));
arrayBlock_signed BLK80 (.A(y[8]), .B(x[4]), .signed_ctrl(sign_y & (flv1)), .mult(PP[4][8]));
arrayBlock_unsigned BLK81 (.A(y[9]), .B(x[4]), .mult(PP[4][9]));
arrayBlock_unsigned BLK82 (.A(y[10]), .B(x[4]), .mult(PP[4][10]));
arrayBlock_unsigned BLK83 (.A(y[11]), .B(x[4]), .mult(PP[4][11]));
arrayBlock_unsigned BLK84 (.A(y[12]), .B(x[4]), .mult(PP[4][12]));
arrayBlock_unsigned BLK85 (.A(y[13]), .B(x[4]), .mult(PP[4][13]));
arrayBlock_unsigned BLK86 (.A(y[14]), .B(x[4]), .mult(PP[4][14]));
arrayBlock_unsigned BLK87 (.A(y[15]), .B(x[4]), .mult(PP[4][15]));
arrayBlock_unsigned BLK88 (.A(y[16]), .B(x[4]), .mult(PP[4][16]));
arrayBlock_signed BLK89 (.A(y[17]), .B(x[4]), .signed_ctrl(sign_y & (flv0)), .mult(PP[4][17]));
arrayBlock_unsigned BLK90 (.A(y[0]), .B(x[5]), .mult(PP[5][0]));
arrayBlock_unsigned BLK91 (.A(y[1]), .B(x[5]), .mult(PP[5][1]));
arrayBlock_unsigned BLK92 (.A(y[2]), .B(x[5]), .mult(PP[5][2]));
arrayBlock_unsigned BLK93 (.A(y[3]), .B(x[5]), .mult(PP[5][3]));
arrayBlock_unsigned BLK94 (.A(y[4]), .B(x[5]), .mult(PP[5][4]));
arrayBlock_unsigned BLK95 (.A(y[5]), .B(x[5]), .mult(PP[5][5]));
arrayBlock_unsigned BLK96 (.A(y[6]), .B(x[5]), .mult(PP[5][6]));
arrayBlock_unsigned BLK97 (.A(y[7]), .B(x[5]), .mult(PP[5][7]));
arrayBlock_signed BLK98 (.A(y[8]), .B(x[5]), .signed_ctrl(sign_y & (flv1)), .mult(PP[5][8]));
arrayBlock_unsigned BLK99 (.A(y[9]), .B(x[5]), .mult(PP[5][9]));
arrayBlock_unsigned BLK100 (.A(y[10]), .B(x[5]), .mult(PP[5][10]));
arrayBlock_unsigned BLK101 (.A(y[11]), .B(x[5]), .mult(PP[5][11]));
arrayBlock_unsigned BLK102 (.A(y[12]), .B(x[5]), .mult(PP[5][12]));
arrayBlock_unsigned BLK103 (.A(y[13]), .B(x[5]), .mult(PP[5][13]));
arrayBlock_unsigned BLK104 (.A(y[14]), .B(x[5]), .mult(PP[5][14]));
arrayBlock_unsigned BLK105 (.A(y[15]), .B(x[5]), .mult(PP[5][15]));
arrayBlock_unsigned BLK106 (.A(y[16]), .B(x[5]), .mult(PP[5][16]));
arrayBlock_signed BLK107 (.A(y[17]), .B(x[5]), .signed_ctrl(sign_y & (flv0)), .mult(PP[5][17]));
arrayBlock_unsigned BLK108 (.A(y[0]), .B(x[6]), .mult(PP[6][0]));
arrayBlock_unsigned BLK109 (.A(y[1]), .B(x[6]), .mult(PP[6][1]));
arrayBlock_unsigned BLK110 (.A(y[2]), .B(x[6]), .mult(PP[6][2]));
arrayBlock_unsigned BLK111 (.A(y[3]), .B(x[6]), .mult(PP[6][3]));
arrayBlock_unsigned BLK112 (.A(y[4]), .B(x[6]), .mult(PP[6][4]));
arrayBlock_unsigned BLK113 (.A(y[5]), .B(x[6]), .mult(PP[6][5]));
arrayBlock_unsigned BLK114 (.A(y[6]), .B(x[6]), .mult(PP[6][6]));
arrayBlock_unsigned BLK115 (.A(y[7]), .B(x[6]), .mult(PP[6][7]));
arrayBlock_signed BLK116 (.A(y[8]), .B(x[6]), .signed_ctrl(sign_y & (flv1)), .mult(PP[6][8]));
arrayBlock_unsigned BLK117 (.A(y[9]), .B(x[6]), .mult(PP[6][9]));
arrayBlock_unsigned BLK118 (.A(y[10]), .B(x[6]), .mult(PP[6][10]));
arrayBlock_unsigned BLK119 (.A(y[11]), .B(x[6]), .mult(PP[6][11]));
arrayBlock_unsigned BLK120 (.A(y[12]), .B(x[6]), .mult(PP[6][12]));
arrayBlock_unsigned BLK121 (.A(y[13]), .B(x[6]), .mult(PP[6][13]));
arrayBlock_unsigned BLK122 (.A(y[14]), .B(x[6]), .mult(PP[6][14]));
arrayBlock_unsigned BLK123 (.A(y[15]), .B(x[6]), .mult(PP[6][15]));
arrayBlock_unsigned BLK124 (.A(y[16]), .B(x[6]), .mult(PP[6][16]));
arrayBlock_signed BLK125 (.A(y[17]), .B(x[6]), .signed_ctrl(sign_y & (flv0)), .mult(PP[6][17]));
arrayBlock_unsigned BLK126 (.A(y[0]), .B(x[7]), .mult(PP[7][0]));
arrayBlock_unsigned BLK127 (.A(y[1]), .B(x[7]), .mult(PP[7][1]));
arrayBlock_unsigned BLK128 (.A(y[2]), .B(x[7]), .mult(PP[7][2]));
arrayBlock_unsigned BLK129 (.A(y[3]), .B(x[7]), .mult(PP[7][3]));
arrayBlock_unsigned BLK130 (.A(y[4]), .B(x[7]), .mult(PP[7][4]));
arrayBlock_unsigned BLK131 (.A(y[5]), .B(x[7]), .mult(PP[7][5]));
arrayBlock_unsigned BLK132 (.A(y[6]), .B(x[7]), .mult(PP[7][6]));
arrayBlock_unsigned BLK133 (.A(y[7]), .B(x[7]), .mult(PP[7][7]));
arrayBlock_signed BLK134 (.A(y[8]), .B(x[7]), .signed_ctrl(sign_y & (flv1)), .mult(PP[7][8]));
arrayBlock_unsigned BLK135 (.A(y[9]), .B(x[7]), .mult(PP[7][9]));
arrayBlock_unsigned BLK136 (.A(y[10]), .B(x[7]), .mult(PP[7][10]));
arrayBlock_unsigned BLK137 (.A(y[11]), .B(x[7]), .mult(PP[7][11]));
arrayBlock_unsigned BLK138 (.A(y[12]), .B(x[7]), .mult(PP[7][12]));
arrayBlock_unsigned BLK139 (.A(y[13]), .B(x[7]), .mult(PP[7][13]));
arrayBlock_unsigned BLK140 (.A(y[14]), .B(x[7]), .mult(PP[7][14]));
arrayBlock_unsigned BLK141 (.A(y[15]), .B(x[7]), .mult(PP[7][15]));
arrayBlock_unsigned BLK142 (.A(y[16]), .B(x[7]), .mult(PP[7][16]));
arrayBlock_signed BLK143 (.A(y[17]), .B(x[7]), .signed_ctrl(sign_y & (flv0)), .mult(PP[7][17]));
arrayBlock_signed BLK144 (.A(y[0]), .B(x[8]), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][0]));
arrayBlock_signed BLK145 (.A(y[1]), .B(x[8]), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][1]));
arrayBlock_signed BLK146 (.A(y[2]), .B(x[8]), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][2]));
arrayBlock_signed BLK147 (.A(y[3]), .B(x[8]), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][3]));
arrayBlock_signed BLK148 (.A(y[4]), .B(x[8]), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][4]));
arrayBlock_signed BLK149 (.A(y[5]), .B(x[8]), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][5]));
arrayBlock_signed BLK150 (.A(y[6]), .B(x[8]), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][6]));
arrayBlock_signed BLK151 (.A(y[7]), .B(x[8]), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][7]));
arrayBlock_signed BLK152 (.A(y[8]), .B(x[8]), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][8]));
arrayBlock_signed BLK153 (.A(y[9]), .B(x[8]), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][9]));
arrayBlock_signed BLK154 (.A(y[10]), .B(x[8]), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][10]));
arrayBlock_signed BLK155 (.A(y[11]), .B(x[8]), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][11]));
arrayBlock_signed BLK156 (.A(y[12]), .B(x[8]), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][12]));
arrayBlock_signed BLK157 (.A(y[13]), .B(x[8]), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][13]));
arrayBlock_signed BLK158 (.A(y[14]), .B(x[8]), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][14]));
arrayBlock_signed BLK159 (.A(y[15]), .B(x[8]), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][15]));
arrayBlock_signed BLK160 (.A(y[16]), .B(x[8]), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][16]));
arrayBlock_signed BLK161 (.A(y[17]), .B(x[8]), .signed_ctrl(sign_c), .mult(PP[8][17]));

daddaTree_9x18_lsb DT (
	.PP0(PP[0]),
	.PP1(PP[1]),
	.PP2(PP[2]),
	.PP3(PP[3]),
	.PP4(PP[4]),
	.PP5(PP[5]),
	.PP6(PP[6]),
	.PP7(PP[7]),
	.PP8(PP[8]),
	.sx(sign_x),
	.sy(sign_y),
	.flv0(flv0),
	.flv1(flv1),
	.flv2(flv2),
	.suppress_sign_x(suppress_sign_x),
	.suppress_sign_y(suppress_sign_y),
	.suppress_sign_e(suppress_sign_e),
	.sum(dadda_sum),
	.carry(dadda_carry)
);

assign sum = s;
assign carry = c;
endmodule

module daddaTree_9x18_lsb (
	input  [17:0] PP0,
	input  [17:0] PP1,
	input  [17:0] PP2,
	input  [17:0] PP3,
	input  [17:0] PP4,
	input  [17:0] PP5,
	input  [17:0] PP6,
	input  [17:0] PP7,
	input  [17:0] PP8,
	input  sx,
	input  sy,
	input  flv0,
	input  flv1,
	input  flv2,
	input suppress_sign_x,
	input suppress_sign_y,
	input suppress_sign_e,
	output [26:0] sum,
	output [26:0] carry
);

/***** Dadda Tree Stage 1 *****/
wire [0:0] c1_0;
wire [1:0] c1_1;
wire [2:0] c1_2;
wire [3:0] c1_3;
wire [4:0] c1_4;
wire [5:0] c1_5;
wire [6:0] c1_6;
wire [7:0] c1_7;
wire [8:0] c1_8;
wire [8:0] c1_9;
wire [8:0] c1_10;
wire [8:0] c1_11;
wire [8:0] c1_12;
wire [8:0] c1_13;
wire [8:0] c1_14;
wire [8:0] c1_15;
wire [8:0] c1_16;
wire [8:0] c1_17;
wire [8:0] c1_18;
wire [7:0] c1_19;
wire [5:0] c1_20;
wire [4:0] c1_21;
wire [3:0] c1_22;
wire [2:0] c1_23;
wire [1:0] c1_24;
wire [2:0] c1_25;
wire [1:0] c1_26;

assign c1_0[0] = PP0[0];
assign c1_1[0] = PP0[1];
assign c1_1[1] = PP1[0];
assign c1_2[0] = PP0[2];
assign c1_2[1] = PP1[1];
assign c1_2[2] = PP2[0];
assign c1_3[0] = PP0[3];
assign c1_3[1] = PP1[2];
assign c1_3[2] = PP2[1];
assign c1_3[3] = PP3[0];
assign c1_4[0] = PP0[4];
assign c1_4[1] = PP1[3];
assign c1_4[2] = PP2[2];
assign c1_4[3] = PP3[1];
assign c1_4[4] = PP4[0];
assign c1_5[0] = PP0[5];
assign c1_5[1] = PP1[4];
assign c1_5[2] = PP2[3];
assign c1_5[3] = PP3[2];
assign c1_5[4] = PP4[1];
assign c1_5[5] = PP5[0];
assign c1_6[0] = PP0[6];
assign c1_6[1] = PP1[5];
assign c1_6[2] = PP2[4];
assign c1_6[3] = PP3[3];
assign c1_6[4] = PP4[2];
assign c1_6[5] = PP5[1];
assign c1_6[6] = PP6[0];
assign c1_7[0] = PP0[7];
assign c1_7[1] = PP1[6];
assign c1_7[2] = PP2[5];
assign c1_7[3] = PP3[4];
assign c1_7[4] = PP4[3];
assign c1_7[5] = PP5[2];
assign c1_7[6] = PP6[1];
assign c1_7[7] = PP7[0];
FA fa0 (PP0[8], PP1[7], PP2[6], c1_8[0], c1_9[0]);
HA ha0 (PP3[5], PP4[4], c1_8[1], c1_9[1]);
assign c1_8[2] = PP5[3];
assign c1_8[3] = PP6[2];
assign c1_8[4] = PP7[1];
assign c1_8[5] = PP8[0];
assign c1_8[6] = suppress_sign_x & sx & flv0;
assign c1_8[7] = sx & flv1;
assign c1_8[8] = sy & flv1;
FA fa1 (PP0[9], PP1[8], PP2[7], c1_9[2], c1_10[0]);
FA fa2 (PP3[6], PP4[5], PP5[4], c1_9[3], c1_10[1]);
assign c1_9[4] = PP6[3];
assign c1_9[5] = PP7[2];
assign c1_9[6] = PP8[1];
assign c1_9[7] = sx & flv2;
assign c1_9[8] = sy & flv2;
FA fa3 (PP0[10], PP1[9], PP2[8], c1_10[2], c1_11[0]);
assign c1_10[3] = PP3[7];
assign c1_10[4] = PP4[6];
assign c1_10[5] = PP5[5];
assign c1_10[6] = PP6[4];
assign c1_10[7] = PP7[3];
assign c1_10[8] = PP8[2];
HA ha1 (PP0[11], PP1[10], c1_11[1], c1_12[0]);
assign c1_11[2] = PP2[9];
assign c1_11[3] = PP3[8];
assign c1_11[4] = PP4[7];
assign c1_11[5] = PP5[6];
assign c1_11[6] = PP6[5];
assign c1_11[7] = PP7[4];
assign c1_11[8] = PP8[3];
HA ha2 (PP0[12], PP1[11], c1_12[1], c1_13[0]);
assign c1_12[2] = PP2[10];
assign c1_12[3] = PP3[9];
assign c1_12[4] = PP4[8];
assign c1_12[5] = PP5[7];
assign c1_12[6] = PP6[6];
assign c1_12[7] = PP7[5];
assign c1_12[8] = PP8[4];
HA ha3 (PP0[13], PP1[12], c1_13[1], c1_14[0]);
assign c1_13[2] = PP2[11];
assign c1_13[3] = PP3[10];
assign c1_13[4] = PP4[9];
assign c1_13[5] = PP5[8];
assign c1_13[6] = PP6[7];
assign c1_13[7] = PP7[6];
assign c1_13[8] = PP8[5];
HA ha4 (PP0[14], PP1[13], c1_14[1], c1_15[0]);
assign c1_14[2] = PP2[12];
assign c1_14[3] = PP3[11];
assign c1_14[4] = PP4[10];
assign c1_14[5] = PP5[9];
assign c1_14[6] = PP6[8];
assign c1_14[7] = PP7[7];
assign c1_14[8] = PP8[6];
HA ha5 (PP0[15], PP1[14], c1_15[1], c1_16[0]);
assign c1_15[2] = PP2[13];
assign c1_15[3] = PP3[12];
assign c1_15[4] = PP4[11];
assign c1_15[5] = PP5[10];
assign c1_15[6] = PP6[9];
assign c1_15[7] = PP7[8];
assign c1_15[8] = PP8[7];
FA fa4 (PP0[16], PP1[15], PP2[14], c1_16[1], c1_17[0]);
HA ha6 (PP3[13], PP4[12], c1_16[2], c1_17[1]);
assign c1_16[3] = PP5[11];
assign c1_16[4] = PP6[10];
assign c1_16[5] = PP7[9];
assign c1_16[6] = PP8[8];
assign c1_16[7] = sx & flv1;
assign c1_16[8] = sy & flv1;
FA_gated fa5 (PP0[17], PP1[16], PP2[15], ~(flv1), c1_17[2], c1_18[0]);
FA_gated fa6 (PP3[14], PP4[13], PP5[12], ~(flv1), c1_17[3], c1_18[1]);
HA_gated ha7 (PP6[11], PP7[10], ~(flv1), c1_17[4], c1_18[2]);
assign c1_17[5] = PP8[9];
assign c1_17[6] = suppress_sign_y & sy & flv0;
assign c1_17[7] = sx & flv1;
assign c1_17[8] = sy & flv1;
FA fa7 (PP1[17], PP2[16], PP3[15], c1_18[3], c1_19[0]);
assign c1_18[4] = PP4[14];
assign c1_18[5] = PP5[13];
assign c1_18[6] = PP6[12];
assign c1_18[7] = PP7[11];
assign c1_18[8] = PP8[10];
assign c1_19[1] = PP2[17];
assign c1_19[2] = PP3[16];
assign c1_19[3] = PP4[15];
assign c1_19[4] = PP5[14];
assign c1_19[5] = PP6[13];
assign c1_19[6] = PP7[12];
assign c1_19[7] = PP8[11];
assign c1_20[0] = PP3[17];
assign c1_20[1] = PP4[16];
assign c1_20[2] = PP5[15];
assign c1_20[3] = PP6[14];
assign c1_20[4] = PP7[13];
assign c1_20[5] = PP8[12];
assign c1_21[0] = PP4[17];
assign c1_21[1] = PP5[16];
assign c1_21[2] = PP6[15];
assign c1_21[3] = PP7[14];
assign c1_21[4] = PP8[13];
assign c1_22[0] = PP5[17];
assign c1_22[1] = PP6[16];
assign c1_22[2] = PP7[15];
assign c1_22[3] = PP8[14];
assign c1_23[0] = PP6[17];
assign c1_23[1] = PP7[16];
assign c1_23[2] = PP8[15];
assign c1_24[0] = PP7[17];
assign c1_24[1] = PP8[16];
assign c1_25[0] = PP8[17];
assign c1_25[1] = suppress_sign_e & sx & flv0;
assign c1_25[2] = suppress_sign_e & sy & flv0;
assign c1_26[0] = suppress_sign_e & sx & flv0;
assign c1_26[1] = suppress_sign_e & sy & flv0;

/***** Dadda Tree Stage 2 *****/
wire [0:0] c2_0;
wire [1:0] c2_1;
wire [2:0] c2_2;
wire [3:0] c2_3;
wire [4:0] c2_4;
wire [5:0] c2_5;
wire [5:0] c2_6;
wire [5:0] c2_7;
wire [5:0] c2_8;
wire [5:0] c2_9;
wire [5:0] c2_10;
wire [5:0] c2_11;
wire [5:0] c2_12;
wire [5:0] c2_13;
wire [5:0] c2_14;
wire [5:0] c2_15;
wire [5:0] c2_16;
wire [5:0] c2_17;
wire [5:0] c2_18;
wire [5:0] c2_19;
wire [5:0] c2_20;
wire [5:0] c2_21;
wire [4:0] c2_22;
wire [2:0] c2_23;
wire [1:0] c2_24;
wire [2:0] c2_25;
wire [1:0] c2_26;

assign c2_0[0] = c1_0[0];
assign c2_1[0] = c1_1[0];
assign c2_1[1] = c1_1[1];
assign c2_2[0] = c1_2[0];
assign c2_2[1] = c1_2[1];
assign c2_2[2] = c1_2[2];
assign c2_3[0] = c1_3[0];
assign c2_3[1] = c1_3[1];
assign c2_3[2] = c1_3[2];
assign c2_3[3] = c1_3[3];
assign c2_4[0] = c1_4[0];
assign c2_4[1] = c1_4[1];
assign c2_4[2] = c1_4[2];
assign c2_4[3] = c1_4[3];
assign c2_4[4] = c1_4[4];
assign c2_5[0] = c1_5[0];
assign c2_5[1] = c1_5[1];
assign c2_5[2] = c1_5[2];
assign c2_5[3] = c1_5[3];
assign c2_5[4] = c1_5[4];
assign c2_5[5] = c1_5[5];
HA ha8 (c1_6[0], c1_6[1], c2_6[0], c2_7[0]);
assign c2_6[1] = c1_6[2];
assign c2_6[2] = c1_6[3];
assign c2_6[3] = c1_6[4];
assign c2_6[4] = c1_6[5];
assign c2_6[5] = c1_6[6];
FA fa8 (c1_7[0], c1_7[1], c1_7[2], c2_7[1], c2_8[0]);
HA ha9 (c1_7[3], c1_7[4], c2_7[2], c2_8[1]);
assign c2_7[3] = c1_7[5];
assign c2_7[4] = c1_7[6];
assign c2_7[5] = c1_7[7];
FA fa9 (c1_8[0], c1_8[1], c1_8[2], c2_8[2], c2_9[0]);
FA fa10 (c1_8[3], c1_8[4], c1_8[5], c2_8[3], c2_9[1]);
HA ha10 (c1_8[6], c1_8[7], c2_8[4], c2_9[2]);
assign c2_8[5] = c1_8[8];
FA fa11 (c1_9[0], c1_9[1], c1_9[2], c2_9[3], c2_10[0]);
FA fa12 (c1_9[3], c1_9[4], c1_9[5], c2_9[4], c2_10[1]);
FA fa13 (c1_9[6], c1_9[7], c1_9[8], c2_9[5], c2_10[2]);
FA fa14 (c1_10[0], c1_10[1], c1_10[2], c2_10[3], c2_11[0]);
FA fa15 (c1_10[3], c1_10[4], c1_10[5], c2_10[4], c2_11[1]);
FA fa16 (c1_10[6], c1_10[7], c1_10[8], c2_10[5], c2_11[2]);
FA fa17 (c1_11[0], c1_11[1], c1_11[2], c2_11[3], c2_12[0]);
FA fa18 (c1_11[3], c1_11[4], c1_11[5], c2_11[4], c2_12[1]);
FA fa19 (c1_11[6], c1_11[7], c1_11[8], c2_11[5], c2_12[2]);
FA fa20 (c1_12[0], c1_12[1], c1_12[2], c2_12[3], c2_13[0]);
FA fa21 (c1_12[3], c1_12[4], c1_12[5], c2_12[4], c2_13[1]);
FA fa22 (c1_12[6], c1_12[7], c1_12[8], c2_12[5], c2_13[2]);
FA fa23 (c1_13[0], c1_13[1], c1_13[2], c2_13[3], c2_14[0]);
FA fa24 (c1_13[3], c1_13[4], c1_13[5], c2_13[4], c2_14[1]);
FA fa25 (c1_13[6], c1_13[7], c1_13[8], c2_13[5], c2_14[2]);
FA fa26 (c1_14[0], c1_14[1], c1_14[2], c2_14[3], c2_15[0]);
FA fa27 (c1_14[3], c1_14[4], c1_14[5], c2_14[4], c2_15[1]);
FA fa28 (c1_14[6], c1_14[7], c1_14[8], c2_14[5], c2_15[2]);
FA fa29 (c1_15[0], c1_15[1], c1_15[2], c2_15[3], c2_16[0]);
FA fa30 (c1_15[3], c1_15[4], c1_15[5], c2_15[4], c2_16[1]);
FA fa31 (c1_15[6], c1_15[7], c1_15[8], c2_15[5], c2_16[2]);
FA fa32 (c1_16[0], c1_16[1], c1_16[2], c2_16[3], c2_17[0]);
FA fa33 (c1_16[3], c1_16[4], c1_16[5], c2_16[4], c2_17[1]);
FA fa34 (c1_16[6], c1_16[7], c1_16[8], c2_16[5], c2_17[2]);
FA_gated fa35 (c1_17[0], c1_17[1], c1_17[2], ~(flv1), c2_17[3], c2_18[0]);
FA_gated fa36 (c1_17[3], c1_17[4], c1_17[5], ~(flv1), c2_17[4], c2_18[1]);
FA_gated fa37 (c1_17[6], c1_17[7], c1_17[8], ~(flv1), c2_17[5], c2_18[2]);
FA fa38 (c1_18[0], c1_18[1], c1_18[2], c2_18[3], c2_19[0]);
FA fa39 (c1_18[3], c1_18[4], c1_18[5], c2_18[4], c2_19[1]);
FA fa40 (c1_18[6], c1_18[7], c1_18[8], c2_18[5], c2_19[2]);
FA fa41 (c1_19[0], c1_19[1], c1_19[2], c2_19[3], c2_20[0]);
FA fa42 (c1_19[3], c1_19[4], c1_19[5], c2_19[4], c2_20[1]);
HA ha11 (c1_19[6], c1_19[7], c2_19[5], c2_20[2]);
FA fa43 (c1_20[0], c1_20[1], c1_20[2], c2_20[3], c2_21[0]);
HA ha12 (c1_20[3], c1_20[4], c2_20[4], c2_21[1]);
assign c2_20[5] = c1_20[5];
HA ha13 (c1_21[0], c1_21[1], c2_21[2], c2_22[0]);
assign c2_21[3] = c1_21[2];
assign c2_21[4] = c1_21[3];
assign c2_21[5] = c1_21[4];
assign c2_22[1] = c1_22[0];
assign c2_22[2] = c1_22[1];
assign c2_22[3] = c1_22[2];
assign c2_22[4] = c1_22[3];
assign c2_23[0] = c1_23[0];
assign c2_23[1] = c1_23[1];
assign c2_23[2] = c1_23[2];
assign c2_24[0] = c1_24[0];
assign c2_24[1] = c1_24[1];
assign c2_25[0] = c1_25[0];
assign c2_25[1] = c1_25[1];
assign c2_25[2] = c1_25[2];
assign c2_26[0] = c1_26[0];
assign c2_26[1] = c1_26[1];

/***** Dadda Tree Stage 3 *****/
wire [0:0] c3_0;
wire [1:0] c3_1;
wire [2:0] c3_2;
wire [3:0] c3_3;
wire [3:0] c3_4;
wire [3:0] c3_5;
wire [3:0] c3_6;
wire [3:0] c3_7;
wire [3:0] c3_8;
wire [3:0] c3_9;
wire [3:0] c3_10;
wire [3:0] c3_11;
wire [3:0] c3_12;
wire [3:0] c3_13;
wire [3:0] c3_14;
wire [3:0] c3_15;
wire [3:0] c3_16;
wire [3:0] c3_17;
wire [3:0] c3_18;
wire [3:0] c3_19;
wire [3:0] c3_20;
wire [3:0] c3_21;
wire [3:0] c3_22;
wire [3:0] c3_23;
wire [2:0] c3_24;
wire [2:0] c3_25;
wire [1:0] c3_26;

assign c3_0[0] = c2_0[0];
assign c3_1[0] = c2_1[0];
assign c3_1[1] = c2_1[1];
assign c3_2[0] = c2_2[0];
assign c3_2[1] = c2_2[1];
assign c3_2[2] = c2_2[2];
assign c3_3[0] = c2_3[0];
assign c3_3[1] = c2_3[1];
assign c3_3[2] = c2_3[2];
assign c3_3[3] = c2_3[3];
HA ha14 (c2_4[0], c2_4[1], c3_4[0], c3_5[0]);
assign c3_4[1] = c2_4[2];
assign c3_4[2] = c2_4[3];
assign c3_4[3] = c2_4[4];
FA fa44 (c2_5[0], c2_5[1], c2_5[2], c3_5[1], c3_6[0]);
HA ha15 (c2_5[3], c2_5[4], c3_5[2], c3_6[1]);
assign c3_5[3] = c2_5[5];
FA fa45 (c2_6[0], c2_6[1], c2_6[2], c3_6[2], c3_7[0]);
FA fa46 (c2_6[3], c2_6[4], c2_6[5], c3_6[3], c3_7[1]);
FA fa47 (c2_7[0], c2_7[1], c2_7[2], c3_7[2], c3_8[0]);
FA fa48 (c2_7[3], c2_7[4], c2_7[5], c3_7[3], c3_8[1]);
FA fa49 (c2_8[0], c2_8[1], c2_8[2], c3_8[2], c3_9[0]);
FA fa50 (c2_8[3], c2_8[4], c2_8[5], c3_8[3], c3_9[1]);
FA fa51 (c2_9[0], c2_9[1], c2_9[2], c3_9[2], c3_10[0]);
FA fa52 (c2_9[3], c2_9[4], c2_9[5], c3_9[3], c3_10[1]);
FA fa53 (c2_10[0], c2_10[1], c2_10[2], c3_10[2], c3_11[0]);
FA fa54 (c2_10[3], c2_10[4], c2_10[5], c3_10[3], c3_11[1]);
FA fa55 (c2_11[0], c2_11[1], c2_11[2], c3_11[2], c3_12[0]);
FA fa56 (c2_11[3], c2_11[4], c2_11[5], c3_11[3], c3_12[1]);
FA fa57 (c2_12[0], c2_12[1], c2_12[2], c3_12[2], c3_13[0]);
FA fa58 (c2_12[3], c2_12[4], c2_12[5], c3_12[3], c3_13[1]);
FA fa59 (c2_13[0], c2_13[1], c2_13[2], c3_13[2], c3_14[0]);
FA fa60 (c2_13[3], c2_13[4], c2_13[5], c3_13[3], c3_14[1]);
FA fa61 (c2_14[0], c2_14[1], c2_14[2], c3_14[2], c3_15[0]);
FA fa62 (c2_14[3], c2_14[4], c2_14[5], c3_14[3], c3_15[1]);
FA fa63 (c2_15[0], c2_15[1], c2_15[2], c3_15[2], c3_16[0]);
FA fa64 (c2_15[3], c2_15[4], c2_15[5], c3_15[3], c3_16[1]);
FA fa65 (c2_16[0], c2_16[1], c2_16[2], c3_16[2], c3_17[0]);
FA fa66 (c2_16[3], c2_16[4], c2_16[5], c3_16[3], c3_17[1]);
FA_gated fa67 (c2_17[0], c2_17[1], c2_17[2], ~(flv1), c3_17[2], c3_18[0]);
FA_gated fa68 (c2_17[3], c2_17[4], c2_17[5], ~(flv1), c3_17[3], c3_18[1]);
FA fa69 (c2_18[0], c2_18[1], c2_18[2], c3_18[2], c3_19[0]);
FA fa70 (c2_18[3], c2_18[4], c2_18[5], c3_18[3], c3_19[1]);
FA fa71 (c2_19[0], c2_19[1], c2_19[2], c3_19[2], c3_20[0]);
FA fa72 (c2_19[3], c2_19[4], c2_19[5], c3_19[3], c3_20[1]);
FA fa73 (c2_20[0], c2_20[1], c2_20[2], c3_20[2], c3_21[0]);
FA fa74 (c2_20[3], c2_20[4], c2_20[5], c3_20[3], c3_21[1]);
FA fa75 (c2_21[0], c2_21[1], c2_21[2], c3_21[2], c3_22[0]);
FA fa76 (c2_21[3], c2_21[4], c2_21[5], c3_21[3], c3_22[1]);
FA fa77 (c2_22[0], c2_22[1], c2_22[2], c3_22[2], c3_23[0]);
HA ha16 (c2_22[3], c2_22[4], c3_22[3], c3_23[1]);
HA ha17 (c2_23[0], c2_23[1], c3_23[2], c3_24[0]);
assign c3_23[3] = c2_23[2];
assign c3_24[1] = c2_24[0];
assign c3_24[2] = c2_24[1];
assign c3_25[0] = c2_25[0];
assign c3_25[1] = c2_25[1];
assign c3_25[2] = c2_25[2];
assign c3_26[0] = c2_26[0];
assign c3_26[1] = c2_26[1];

/***** Dadda Tree Stage 4 *****/
wire [0:0] c4_0;
wire [1:0] c4_1;
wire [2:0] c4_2;
wire [2:0] c4_3;
wire [2:0] c4_4;
wire [2:0] c4_5;
wire [2:0] c4_6;
wire [2:0] c4_7;
wire [2:0] c4_8;
wire [2:0] c4_9;
wire [2:0] c4_10;
wire [2:0] c4_11;
wire [2:0] c4_12;
wire [2:0] c4_13;
wire [2:0] c4_14;
wire [2:0] c4_15;
wire [2:0] c4_16;
wire [2:0] c4_17;
wire [2:0] c4_18;
wire [2:0] c4_19;
wire [2:0] c4_20;
wire [2:0] c4_21;
wire [2:0] c4_22;
wire [2:0] c4_23;
wire [2:0] c4_24;
wire [2:0] c4_25;
wire [2:0] c4_26;

assign c4_0[0] = c3_0[0];
assign c4_1[0] = c3_1[0];
assign c4_1[1] = c3_1[1];
assign c4_2[0] = c3_2[0];
assign c4_2[1] = c3_2[1];
assign c4_2[2] = c3_2[2];
HA ha18 (c3_3[0], c3_3[1], c4_3[0], c4_4[0]);
assign c4_3[1] = c3_3[2];
assign c4_3[2] = c3_3[3];
FA fa78 (c3_4[0], c3_4[1], c3_4[2], c4_4[1], c4_5[0]);
assign c4_4[2] = c3_4[3];
FA fa79 (c3_5[0], c3_5[1], c3_5[2], c4_5[1], c4_6[0]);
assign c4_5[2] = c3_5[3];
FA fa80 (c3_6[0], c3_6[1], c3_6[2], c4_6[1], c4_7[0]);
assign c4_6[2] = c3_6[3];
FA fa81 (c3_7[0], c3_7[1], c3_7[2], c4_7[1], c4_8[0]);
assign c4_7[2] = c3_7[3];
FA fa82 (c3_8[0], c3_8[1], c3_8[2], c4_8[1], c4_9[0]);
assign c4_8[2] = c3_8[3];
FA fa83 (c3_9[0], c3_9[1], c3_9[2], c4_9[1], c4_10[0]);
assign c4_9[2] = c3_9[3];
FA fa84 (c3_10[0], c3_10[1], c3_10[2], c4_10[1], c4_11[0]);
assign c4_10[2] = c3_10[3];
FA fa85 (c3_11[0], c3_11[1], c3_11[2], c4_11[1], c4_12[0]);
assign c4_11[2] = c3_11[3];
FA fa86 (c3_12[0], c3_12[1], c3_12[2], c4_12[1], c4_13[0]);
assign c4_12[2] = c3_12[3];
FA fa87 (c3_13[0], c3_13[1], c3_13[2], c4_13[1], c4_14[0]);
assign c4_13[2] = c3_13[3];
FA fa88 (c3_14[0], c3_14[1], c3_14[2], c4_14[1], c4_15[0]);
assign c4_14[2] = c3_14[3];
FA fa89 (c3_15[0], c3_15[1], c3_15[2], c4_15[1], c4_16[0]);
assign c4_15[2] = c3_15[3];
FA fa90 (c3_16[0], c3_16[1], c3_16[2], c4_16[1], c4_17[0]);
assign c4_16[2] = c3_16[3];
FA_gated fa91 (c3_17[0], c3_17[1], c3_17[2], ~(flv1), c4_17[1], c4_18[0]);
assign c4_17[2] = c3_17[3];
FA fa92 (c3_18[0], c3_18[1], c3_18[2], c4_18[1], c4_19[0]);
assign c4_18[2] = c3_18[3];
FA fa93 (c3_19[0], c3_19[1], c3_19[2], c4_19[1], c4_20[0]);
assign c4_19[2] = c3_19[3];
FA fa94 (c3_20[0], c3_20[1], c3_20[2], c4_20[1], c4_21[0]);
assign c4_20[2] = c3_20[3];
FA fa95 (c3_21[0], c3_21[1], c3_21[2], c4_21[1], c4_22[0]);
assign c4_21[2] = c3_21[3];
FA fa96 (c3_22[0], c3_22[1], c3_22[2], c4_22[1], c4_23[0]);
assign c4_22[2] = c3_22[3];
FA fa97 (c3_23[0], c3_23[1], c3_23[2], c4_23[1], c4_24[0]);
assign c4_23[2] = c3_23[3];
HA ha19 (c3_24[0], c3_24[1], c4_24[1], c4_25[0]);
assign c4_24[2] = c3_24[2];
HA ha20 (c3_25[0], c3_25[1], c4_25[1], c4_26[0]);
assign c4_25[2] = c3_25[2];
assign c4_26[1] = c3_26[0];
assign c4_26[2] = c3_26[1];

/***** Dadda Tree Stage 5 *****/
wire [0:0] c5_0;
wire [1:0] c5_1;
wire [1:0] c5_2;
wire [1:0] c5_3;
wire [1:0] c5_4;
wire [1:0] c5_5;
wire [1:0] c5_6;
wire [1:0] c5_7;
wire [1:0] c5_8;
wire [1:0] c5_9;
wire [1:0] c5_10;
wire [1:0] c5_11;
wire [1:0] c5_12;
wire [1:0] c5_13;
wire [1:0] c5_14;
wire [1:0] c5_15;
wire [1:0] c5_16;
wire [1:0] c5_17;
wire [1:0] c5_18;
wire [1:0] c5_19;
wire [1:0] c5_20;
wire [1:0] c5_21;
wire [1:0] c5_22;
wire [1:0] c5_23;
wire [1:0] c5_24;
wire [1:0] c5_25;
wire [1:0] c5_26;
wire [0:0] c5_27;

assign c5_0[0] = c4_0[0];
assign c5_1[0] = c4_1[0];
assign c5_1[1] = c4_1[1];
HA ha21 (c4_2[0], c4_2[1], c5_2[0], c5_3[0]);
assign c5_2[1] = c4_2[2];
FA fa98 (c4_3[0], c4_3[1], c4_3[2], c5_3[1], c5_4[0]);
FA fa99 (c4_4[0], c4_4[1], c4_4[2], c5_4[1], c5_5[0]);
FA fa100 (c4_5[0], c4_5[1], c4_5[2], c5_5[1], c5_6[0]);
FA fa101 (c4_6[0], c4_6[1], c4_6[2], c5_6[1], c5_7[0]);
FA fa102 (c4_7[0], c4_7[1], c4_7[2], c5_7[1], c5_8[0]);
FA fa103 (c4_8[0], c4_8[1], c4_8[2], c5_8[1], c5_9[0]);
FA fa104 (c4_9[0], c4_9[1], c4_9[2], c5_9[1], c5_10[0]);
FA fa105 (c4_10[0], c4_10[1], c4_10[2], c5_10[1], c5_11[0]);
FA fa106 (c4_11[0], c4_11[1], c4_11[2], c5_11[1], c5_12[0]);
FA fa107 (c4_12[0], c4_12[1], c4_12[2], c5_12[1], c5_13[0]);
FA fa108 (c4_13[0], c4_13[1], c4_13[2], c5_13[1], c5_14[0]);
FA fa109 (c4_14[0], c4_14[1], c4_14[2], c5_14[1], c5_15[0]);
FA fa110 (c4_15[0], c4_15[1], c4_15[2], c5_15[1], c5_16[0]);
FA fa111 (c4_16[0], c4_16[1], c4_16[2], c5_16[1], c5_17[0]);
FA_gated fa112 (c4_17[0], c4_17[1], c4_17[2], ~(flv1), c5_17[1], c5_18[0]);
FA fa113 (c4_18[0], c4_18[1], c4_18[2], c5_18[1], c5_19[0]);
FA fa114 (c4_19[0], c4_19[1], c4_19[2], c5_19[1], c5_20[0]);
FA fa115 (c4_20[0], c4_20[1], c4_20[2], c5_20[1], c5_21[0]);
FA fa116 (c4_21[0], c4_21[1], c4_21[2], c5_21[1], c5_22[0]);
FA fa117 (c4_22[0], c4_22[1], c4_22[2], c5_22[1], c5_23[0]);
FA fa118 (c4_23[0], c4_23[1], c4_23[2], c5_23[1], c5_24[0]);
FA fa119 (c4_24[0], c4_24[1], c4_24[2], c5_24[1], c5_25[0]);
FA fa120 (c4_25[0], c4_25[1], c4_25[2], c5_25[1], c5_26[0]);
FA fa121 (c4_26[0], c4_26[1], c4_26[2], c5_26[1], c5_27[0]);

assign sum = {c5_26[0],c5_25[0],c5_24[0],c5_23[0],c5_22[0],c5_21[0],c5_20[0],c5_19[0],c5_18[0],c5_17[0],c5_16[0],c5_15[0],c5_14[0],c5_13[0],c5_12[0],c5_11[0],c5_10[0],c5_9[0],c5_8[0],c5_7[0],c5_6[0],c5_5[0],c5_4[0],c5_3[0],c5_2[0],c5_1[0],c5_0[0]};
assign carry = {c5_26[1],c5_25[1],c5_24[1],c5_23[1],c5_22[1],c5_21[1],c5_20[1],c5_19[1],c5_18[1],c5_17[1],c5_16[1],c5_15[1],c5_14[1],c5_13[1],c5_12[1],c5_11[1],c5_10[1],c5_9[1],c5_8[1],c5_7[1],c5_6[1],c5_5[1],c5_4[1],c5_3[1],c5_2[1],c5_1[1], 1'b0};

endmodule

module multiplier_9x18_msb (
	input  clk,
	input  [8:0] data_x,
	input  [17:0] data_y,
	input  signed_x,
	input  signed_y,
	input  signed_c,
	input  flv0,
	input  flv1,
	input  flv2,
	input  suppress_sign_x,
	input  suppress_sign_y,
	input  suppress_sign_e,
	output [26:0] sum,
	output [26:0] carry
);

wire [17:0] PP [8:0];
wire [26:0] dadda_sum, dadda_carry;
reg [8:0] x;
reg [17:0] y;
reg sign_x;
reg sign_y;
reg sign_c;
reg [26:0] s;
reg [26:0] c;

always @ (*)
begin: reg_in_out
	x <= data_x;
	y <= data_y;
	sign_x <= signed_x;
	sign_y <= signed_y;
	sign_c <= signed_c;
	s <= dadda_sum;
	c <= dadda_carry;
end

arrayBlock_unsigned_gated BLK0 (.A(y[0]), .B(x[0]), .enable(flv0), .mult(PP[0][0]));
arrayBlock_unsigned_gated BLK1 (.A(y[1]), .B(x[0]), .enable(flv0), .mult(PP[0][1]));
arrayBlock_unsigned_gated BLK2 (.A(y[2]), .B(x[0]), .enable(flv0), .mult(PP[0][2]));
arrayBlock_unsigned_gated BLK3 (.A(y[3]), .B(x[0]), .enable(flv0), .mult(PP[0][3]));
arrayBlock_unsigned_gated BLK4 (.A(y[4]), .B(x[0]), .enable(flv0), .mult(PP[0][4]));
arrayBlock_unsigned_gated BLK5 (.A(y[5]), .B(x[0]), .enable(flv0), .mult(PP[0][5]));
arrayBlock_unsigned_gated BLK6 (.A(y[6]), .B(x[0]), .enable(flv0), .mult(PP[0][6]));
arrayBlock_unsigned_gated BLK7 (.A(y[7]), .B(x[0]), .enable(flv0), .mult(PP[0][7]));
arrayBlock_unsigned_gated BLK8 (.A(y[8]), .B(x[0]), .enable(flv0), .mult(PP[0][8]));
arrayBlock_unsigned_gated BLK9 (.A(y[9]), .B(x[0]), .enable(1'b1), .mult(PP[0][9]));
arrayBlock_unsigned_gated BLK10 (.A(y[10]), .B(x[0]), .enable(1'b1), .mult(PP[0][10]));
arrayBlock_unsigned_gated BLK11 (.A(y[11]), .B(x[0]), .enable(1'b1), .mult(PP[0][11]));
arrayBlock_signed_gated BLK12 (.A(y[12]), .B(x[0]), .enable(1'b1), .signed_ctrl(sign_y & (flv2)), .mult(PP[0][12]));
arrayBlock_unsigned_gated BLK13 (.A(y[13]), .B(x[0]), .enable(flv0 | flv1), .mult(PP[0][13]));
arrayBlock_unsigned_gated BLK14 (.A(y[14]), .B(x[0]), .enable(flv0 | flv1), .mult(PP[0][14]));
arrayBlock_unsigned_gated BLK15 (.A(y[15]), .B(x[0]), .enable(flv0 | flv1), .mult(PP[0][15]));
arrayBlock_unsigned_gated BLK16 (.A(y[16]), .B(x[0]), .enable(flv0 | flv1), .mult(PP[0][16]));
arrayBlock_signed_gated BLK17 (.A(y[17]), .B(x[0]), .enable(flv0 | flv1), .signed_ctrl(sign_y & (flv0 | flv1)), .mult(PP[0][17]));
arrayBlock_unsigned_gated BLK18 (.A(y[0]), .B(x[1]), .enable(flv0), .mult(PP[1][0]));
arrayBlock_unsigned_gated BLK19 (.A(y[1]), .B(x[1]), .enable(flv0), .mult(PP[1][1]));
arrayBlock_unsigned_gated BLK20 (.A(y[2]), .B(x[1]), .enable(flv0), .mult(PP[1][2]));
arrayBlock_unsigned_gated BLK21 (.A(y[3]), .B(x[1]), .enable(flv0), .mult(PP[1][3]));
arrayBlock_unsigned_gated BLK22 (.A(y[4]), .B(x[1]), .enable(flv0), .mult(PP[1][4]));
arrayBlock_unsigned_gated BLK23 (.A(y[5]), .B(x[1]), .enable(flv0), .mult(PP[1][5]));
arrayBlock_unsigned_gated BLK24 (.A(y[6]), .B(x[1]), .enable(flv0), .mult(PP[1][6]));
arrayBlock_unsigned_gated BLK25 (.A(y[7]), .B(x[1]), .enable(flv0), .mult(PP[1][7]));
arrayBlock_unsigned_gated BLK26 (.A(y[8]), .B(x[1]), .enable(flv0), .mult(PP[1][8]));
arrayBlock_unsigned_gated BLK27 (.A(y[9]), .B(x[1]), .enable(1'b1), .mult(PP[1][9]));
arrayBlock_unsigned_gated BLK28 (.A(y[10]), .B(x[1]), .enable(1'b1), .mult(PP[1][10]));
arrayBlock_unsigned_gated BLK29 (.A(y[11]), .B(x[1]), .enable(1'b1), .mult(PP[1][11]));
arrayBlock_signed_gated BLK30 (.A(y[12]), .B(x[1]), .enable(1'b1), .signed_ctrl(sign_y & (flv2)), .mult(PP[1][12]));
arrayBlock_unsigned_gated BLK31 (.A(y[13]), .B(x[1]), .enable(flv0 | flv1), .mult(PP[1][13]));
arrayBlock_unsigned_gated BLK32 (.A(y[14]), .B(x[1]), .enable(flv0 | flv1), .mult(PP[1][14]));
arrayBlock_unsigned_gated BLK33 (.A(y[15]), .B(x[1]), .enable(flv0 | flv1), .mult(PP[1][15]));
arrayBlock_unsigned_gated BLK34 (.A(y[16]), .B(x[1]), .enable(flv0 | flv1), .mult(PP[1][16]));
arrayBlock_signed_gated BLK35 (.A(y[17]), .B(x[1]), .enable(flv0 | flv1), .signed_ctrl(sign_y & (flv0 | flv1)), .mult(PP[1][17]));
arrayBlock_unsigned_gated BLK36 (.A(y[0]), .B(x[2]), .enable(flv0), .mult(PP[2][0]));
arrayBlock_unsigned_gated BLK37 (.A(y[1]), .B(x[2]), .enable(flv0), .mult(PP[2][1]));
arrayBlock_unsigned_gated BLK38 (.A(y[2]), .B(x[2]), .enable(flv0), .mult(PP[2][2]));
arrayBlock_unsigned_gated BLK39 (.A(y[3]), .B(x[2]), .enable(flv0), .mult(PP[2][3]));
arrayBlock_unsigned_gated BLK40 (.A(y[4]), .B(x[2]), .enable(flv0), .mult(PP[2][4]));
arrayBlock_unsigned_gated BLK41 (.A(y[5]), .B(x[2]), .enable(flv0), .mult(PP[2][5]));
arrayBlock_unsigned_gated BLK42 (.A(y[6]), .B(x[2]), .enable(flv0), .mult(PP[2][6]));
arrayBlock_unsigned_gated BLK43 (.A(y[7]), .B(x[2]), .enable(flv0), .mult(PP[2][7]));
arrayBlock_unsigned_gated BLK44 (.A(y[8]), .B(x[2]), .enable(flv0), .mult(PP[2][8]));
arrayBlock_unsigned_gated BLK45 (.A(y[9]), .B(x[2]), .enable(1'b1), .mult(PP[2][9]));
arrayBlock_unsigned_gated BLK46 (.A(y[10]), .B(x[2]), .enable(1'b1), .mult(PP[2][10]));
arrayBlock_unsigned_gated BLK47 (.A(y[11]), .B(x[2]), .enable(1'b1), .mult(PP[2][11]));
arrayBlock_signed_gated BLK48 (.A(y[12]), .B(x[2]), .enable(1'b1), .signed_ctrl(sign_y & (flv2)), .mult(PP[2][12]));
arrayBlock_unsigned_gated BLK49 (.A(y[13]), .B(x[2]), .enable(flv0 | flv1), .mult(PP[2][13]));
arrayBlock_unsigned_gated BLK50 (.A(y[14]), .B(x[2]), .enable(flv0 | flv1), .mult(PP[2][14]));
arrayBlock_unsigned_gated BLK51 (.A(y[15]), .B(x[2]), .enable(flv0 | flv1), .mult(PP[2][15]));
arrayBlock_unsigned_gated BLK52 (.A(y[16]), .B(x[2]), .enable(flv0 | flv1), .mult(PP[2][16]));
arrayBlock_signed_gated BLK53 (.A(y[17]), .B(x[2]), .enable(flv0 | flv1), .signed_ctrl(sign_y & (flv0 | flv1)), .mult(PP[2][17]));
arrayBlock_unsigned_gated BLK54 (.A(y[0]), .B(x[3]), .enable(flv0), .mult(PP[3][0]));
arrayBlock_unsigned_gated BLK55 (.A(y[1]), .B(x[3]), .enable(flv0), .mult(PP[3][1]));
arrayBlock_unsigned_gated BLK56 (.A(y[2]), .B(x[3]), .enable(flv0), .mult(PP[3][2]));
arrayBlock_unsigned_gated BLK57 (.A(y[3]), .B(x[3]), .enable(flv0), .mult(PP[3][3]));
arrayBlock_unsigned_gated BLK58 (.A(y[4]), .B(x[3]), .enable(flv0), .mult(PP[3][4]));
arrayBlock_unsigned_gated BLK59 (.A(y[5]), .B(x[3]), .enable(flv0), .mult(PP[3][5]));
arrayBlock_unsigned_gated BLK60 (.A(y[6]), .B(x[3]), .enable(flv0), .mult(PP[3][6]));
arrayBlock_unsigned_gated BLK61 (.A(y[7]), .B(x[3]), .enable(flv0), .mult(PP[3][7]));
arrayBlock_unsigned_gated BLK62 (.A(y[8]), .B(x[3]), .enable(flv0), .mult(PP[3][8]));
arrayBlock_signed_gated BLK63 (.A(y[9]), .B(x[3]), .enable(1'b1), .signed_ctrl(sign_x & (flv2)), .mult(PP[3][9]));
arrayBlock_signed_gated BLK64 (.A(y[10]), .B(x[3]), .enable(1'b1), .signed_ctrl(sign_x & (flv2)), .mult(PP[3][10]));
arrayBlock_signed_gated BLK65 (.A(y[11]), .B(x[3]), .enable(1'b1), .signed_ctrl(sign_x & (flv2)), .mult(PP[3][11]));
arrayBlock_unsigned_gated BLK66 (.A(y[12]), .B(x[3]), .enable(1'b1), .mult(PP[3][12]));
arrayBlock_unsigned_gated BLK67 (.A(y[13]), .B(x[3]), .enable(flv0 | flv1), .mult(PP[3][13]));
arrayBlock_unsigned_gated BLK68 (.A(y[14]), .B(x[3]), .enable(flv0 | flv1), .mult(PP[3][14]));
arrayBlock_unsigned_gated BLK69 (.A(y[15]), .B(x[3]), .enable(flv0 | flv1), .mult(PP[3][15]));
arrayBlock_unsigned_gated BLK70 (.A(y[16]), .B(x[3]), .enable(flv0 | flv1), .mult(PP[3][16]));
arrayBlock_signed_gated BLK71 (.A(y[17]), .B(x[3]), .enable(flv0 | flv1), .signed_ctrl(sign_y & (flv0 | flv1)), .mult(PP[3][17]));
arrayBlock_unsigned_gated BLK72 (.A(y[0]), .B(x[4]), .enable(flv0), .mult(PP[4][0]));
arrayBlock_unsigned_gated BLK73 (.A(y[1]), .B(x[4]), .enable(flv0), .mult(PP[4][1]));
arrayBlock_unsigned_gated BLK74 (.A(y[2]), .B(x[4]), .enable(flv0), .mult(PP[4][2]));
arrayBlock_unsigned_gated BLK75 (.A(y[3]), .B(x[4]), .enable(flv0), .mult(PP[4][3]));
arrayBlock_unsigned_gated BLK76 (.A(y[4]), .B(x[4]), .enable(flv0), .mult(PP[4][4]));
arrayBlock_unsigned_gated BLK77 (.A(y[5]), .B(x[4]), .enable(flv0), .mult(PP[4][5]));
arrayBlock_unsigned_gated BLK78 (.A(y[6]), .B(x[4]), .enable(flv0), .mult(PP[4][6]));
arrayBlock_unsigned_gated BLK79 (.A(y[7]), .B(x[4]), .enable(flv0), .mult(PP[4][7]));
arrayBlock_unsigned_gated BLK80 (.A(y[8]), .B(x[4]), .enable(flv0), .mult(PP[4][8]));
arrayBlock_unsigned_gated BLK81 (.A(y[9]), .B(x[4]), .enable(flv0 | flv1), .mult(PP[4][9]));
arrayBlock_unsigned_gated BLK82 (.A(y[10]), .B(x[4]), .enable(flv0 | flv1), .mult(PP[4][10]));
arrayBlock_unsigned_gated BLK83 (.A(y[11]), .B(x[4]), .enable(flv0 | flv1), .mult(PP[4][11]));
arrayBlock_unsigned_gated BLK84 (.A(y[12]), .B(x[4]), .enable(flv0 | flv1), .mult(PP[4][12]));
arrayBlock_unsigned_gated BLK85 (.A(y[13]), .B(x[4]), .enable(flv0 | flv1), .mult(PP[4][13]));
arrayBlock_unsigned_gated BLK86 (.A(y[14]), .B(x[4]), .enable(flv0 | flv1), .mult(PP[4][14]));
arrayBlock_unsigned_gated BLK87 (.A(y[15]), .B(x[4]), .enable(flv0 | flv1), .mult(PP[4][15]));
arrayBlock_unsigned_gated BLK88 (.A(y[16]), .B(x[4]), .enable(flv0 | flv1), .mult(PP[4][16]));
arrayBlock_signed_gated BLK89 (.A(y[17]), .B(x[4]), .enable(flv0 | flv1), .signed_ctrl(sign_y & (flv0 | flv1)), .mult(PP[4][17]));
arrayBlock_unsigned_gated BLK90 (.A(y[0]), .B(x[5]), .enable(flv0), .mult(PP[5][0]));
arrayBlock_unsigned_gated BLK91 (.A(y[1]), .B(x[5]), .enable(flv0), .mult(PP[5][1]));
arrayBlock_unsigned_gated BLK92 (.A(y[2]), .B(x[5]), .enable(flv0), .mult(PP[5][2]));
arrayBlock_unsigned_gated BLK93 (.A(y[3]), .B(x[5]), .enable(flv0), .mult(PP[5][3]));
arrayBlock_unsigned_gated BLK94 (.A(y[4]), .B(x[5]), .enable(flv0), .mult(PP[5][4]));
arrayBlock_unsigned_gated BLK95 (.A(y[5]), .B(x[5]), .enable(flv0), .mult(PP[5][5]));
arrayBlock_unsigned_gated BLK96 (.A(y[6]), .B(x[5]), .enable(flv0), .mult(PP[5][6]));
arrayBlock_unsigned_gated BLK97 (.A(y[7]), .B(x[5]), .enable(flv0), .mult(PP[5][7]));
arrayBlock_unsigned_gated BLK98 (.A(y[8]), .B(x[5]), .enable(flv0), .mult(PP[5][8]));
arrayBlock_unsigned_gated BLK99 (.A(y[9]), .B(x[5]), .enable(flv0 | flv1), .mult(PP[5][9]));
arrayBlock_unsigned_gated BLK100 (.A(y[10]), .B(x[5]), .enable(flv0 | flv1), .mult(PP[5][10]));
arrayBlock_unsigned_gated BLK101 (.A(y[11]), .B(x[5]), .enable(flv0 | flv1), .mult(PP[5][11]));
arrayBlock_unsigned_gated BLK102 (.A(y[12]), .B(x[5]), .enable(flv0 | flv1), .mult(PP[5][12]));
arrayBlock_unsigned_gated BLK103 (.A(y[13]), .B(x[5]), .enable(flv0 | flv1), .mult(PP[5][13]));
arrayBlock_unsigned_gated BLK104 (.A(y[14]), .B(x[5]), .enable(1'b1), .mult(PP[5][14]));
arrayBlock_unsigned_gated BLK105 (.A(y[15]), .B(x[5]), .enable(1'b1), .mult(PP[5][15]));
arrayBlock_unsigned_gated BLK106 (.A(y[16]), .B(x[5]), .enable(1'b1), .mult(PP[5][16]));
arrayBlock_signed_gated BLK107 (.A(y[17]), .B(x[5]), .enable(1'b1), .signed_ctrl(sign_y & (flv0 | flv1 | flv2)), .mult(PP[5][17]));
arrayBlock_unsigned_gated BLK108 (.A(y[0]), .B(x[6]), .enable(flv0), .mult(PP[6][0]));
arrayBlock_unsigned_gated BLK109 (.A(y[1]), .B(x[6]), .enable(flv0), .mult(PP[6][1]));
arrayBlock_unsigned_gated BLK110 (.A(y[2]), .B(x[6]), .enable(flv0), .mult(PP[6][2]));
arrayBlock_unsigned_gated BLK111 (.A(y[3]), .B(x[6]), .enable(flv0), .mult(PP[6][3]));
arrayBlock_unsigned_gated BLK112 (.A(y[4]), .B(x[6]), .enable(flv0), .mult(PP[6][4]));
arrayBlock_unsigned_gated BLK113 (.A(y[5]), .B(x[6]), .enable(flv0), .mult(PP[6][5]));
arrayBlock_unsigned_gated BLK114 (.A(y[6]), .B(x[6]), .enable(flv0), .mult(PP[6][6]));
arrayBlock_unsigned_gated BLK115 (.A(y[7]), .B(x[6]), .enable(flv0), .mult(PP[6][7]));
arrayBlock_unsigned_gated BLK116 (.A(y[8]), .B(x[6]), .enable(flv0), .mult(PP[6][8]));
arrayBlock_unsigned_gated BLK117 (.A(y[9]), .B(x[6]), .enable(flv0 | flv1), .mult(PP[6][9]));
arrayBlock_unsigned_gated BLK118 (.A(y[10]), .B(x[6]), .enable(flv0 | flv1), .mult(PP[6][10]));
arrayBlock_unsigned_gated BLK119 (.A(y[11]), .B(x[6]), .enable(flv0 | flv1), .mult(PP[6][11]));
arrayBlock_unsigned_gated BLK120 (.A(y[12]), .B(x[6]), .enable(flv0 | flv1), .mult(PP[6][12]));
arrayBlock_unsigned_gated BLK121 (.A(y[13]), .B(x[6]), .enable(flv0 | flv1), .mult(PP[6][13]));
arrayBlock_unsigned_gated BLK122 (.A(y[14]), .B(x[6]), .enable(1'b1), .mult(PP[6][14]));
arrayBlock_unsigned_gated BLK123 (.A(y[15]), .B(x[6]), .enable(1'b1), .mult(PP[6][15]));
arrayBlock_unsigned_gated BLK124 (.A(y[16]), .B(x[6]), .enable(1'b1), .mult(PP[6][16]));
arrayBlock_signed_gated BLK125 (.A(y[17]), .B(x[6]), .enable(1'b1), .signed_ctrl(sign_y & (flv0 | flv1 | flv2)), .mult(PP[6][17]));
arrayBlock_unsigned_gated BLK126 (.A(y[0]), .B(x[7]), .enable(flv0), .mult(PP[7][0]));
arrayBlock_unsigned_gated BLK127 (.A(y[1]), .B(x[7]), .enable(flv0), .mult(PP[7][1]));
arrayBlock_unsigned_gated BLK128 (.A(y[2]), .B(x[7]), .enable(flv0), .mult(PP[7][2]));
arrayBlock_unsigned_gated BLK129 (.A(y[3]), .B(x[7]), .enable(flv0), .mult(PP[7][3]));
arrayBlock_unsigned_gated BLK130 (.A(y[4]), .B(x[7]), .enable(flv0), .mult(PP[7][4]));
arrayBlock_unsigned_gated BLK131 (.A(y[5]), .B(x[7]), .enable(flv0), .mult(PP[7][5]));
arrayBlock_unsigned_gated BLK132 (.A(y[6]), .B(x[7]), .enable(flv0), .mult(PP[7][6]));
arrayBlock_unsigned_gated BLK133 (.A(y[7]), .B(x[7]), .enable(flv0), .mult(PP[7][7]));
arrayBlock_unsigned_gated BLK134 (.A(y[8]), .B(x[7]), .enable(flv0), .mult(PP[7][8]));
arrayBlock_unsigned_gated BLK135 (.A(y[9]), .B(x[7]), .enable(flv0 | flv1), .mult(PP[7][9]));
arrayBlock_unsigned_gated BLK136 (.A(y[10]), .B(x[7]), .enable(flv0 | flv1), .mult(PP[7][10]));
arrayBlock_unsigned_gated BLK137 (.A(y[11]), .B(x[7]), .enable(flv0 | flv1), .mult(PP[7][11]));
arrayBlock_unsigned_gated BLK138 (.A(y[12]), .B(x[7]), .enable(flv0 | flv1), .mult(PP[7][12]));
arrayBlock_unsigned_gated BLK139 (.A(y[13]), .B(x[7]), .enable(flv0 | flv1), .mult(PP[7][13]));
arrayBlock_unsigned_gated BLK140 (.A(y[14]), .B(x[7]), .enable(1'b1), .mult(PP[7][14]));
arrayBlock_unsigned_gated BLK141 (.A(y[15]), .B(x[7]), .enable(1'b1), .mult(PP[7][15]));
arrayBlock_unsigned_gated BLK142 (.A(y[16]), .B(x[7]), .enable(1'b1), .mult(PP[7][16]));
arrayBlock_signed_gated BLK143 (.A(y[17]), .B(x[7]), .enable(1'b1), .signed_ctrl(sign_y & (flv0 | flv1 | flv2)), .mult(PP[7][17]));
arrayBlock_signed_gated BLK144 (.A(y[0]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][0]));
arrayBlock_signed_gated BLK145 (.A(y[1]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][1]));
arrayBlock_signed_gated BLK146 (.A(y[2]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][2]));
arrayBlock_signed_gated BLK147 (.A(y[3]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][3]));
arrayBlock_signed_gated BLK148 (.A(y[4]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][4]));
arrayBlock_signed_gated BLK149 (.A(y[5]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][5]));
arrayBlock_signed_gated BLK150 (.A(y[6]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][6]));
arrayBlock_signed_gated BLK151 (.A(y[7]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][7]));
arrayBlock_signed_gated BLK152 (.A(y[8]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][8]));
arrayBlock_signed_gated BLK153 (.A(y[9]), .B(x[8]), .enable(flv0 | flv1), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][9]));
arrayBlock_signed_gated BLK154 (.A(y[10]), .B(x[8]), .enable(flv0 | flv1), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][10]));
arrayBlock_signed_gated BLK155 (.A(y[11]), .B(x[8]), .enable(flv0 | flv1), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][11]));
arrayBlock_signed_gated BLK156 (.A(y[12]), .B(x[8]), .enable(flv0 | flv1), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][12]));
arrayBlock_signed_gated BLK157 (.A(y[13]), .B(x[8]), .enable(flv0 | flv1), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][13]));
arrayBlock_signed_gated BLK158 (.A(y[14]), .B(x[8]), .enable(1'b1), .signed_ctrl(sign_x & (flv0 | flv1 | flv2)), .mult(PP[8][14]));
arrayBlock_signed_gated BLK159 (.A(y[15]), .B(x[8]), .enable(1'b1), .signed_ctrl(sign_x & (flv0 | flv1 | flv2)), .mult(PP[8][15]));
arrayBlock_signed_gated BLK160 (.A(y[16]), .B(x[8]), .enable(1'b1), .signed_ctrl(sign_x & (flv0 | flv1 | flv2)), .mult(PP[8][16]));
arrayBlock_signed_gated BLK161 (.A(y[17]), .B(x[8]), .enable(1'b1), .signed_ctrl(sign_c), .mult(PP[8][17]));

daddaTree_9x18_msb DT (
	.PP0(PP[0]),
	.PP1(PP[1]),
	.PP2(PP[2]),
	.PP3(PP[3]),
	.PP4(PP[4]),
	.PP5(PP[5]),
	.PP6(PP[6]),
	.PP7(PP[7]),
	.PP8(PP[8]),
	.sx(sign_x),
	.sy(sign_y),
	.flv0(flv0),
	.flv1(flv1),
	.flv2(flv2),
	.suppress_sign_x(suppress_sign_x),
	.suppress_sign_y(suppress_sign_y),
	.suppress_sign_e(suppress_sign_e),
	.sum(dadda_sum),
	.carry(dadda_carry)
);

assign sum = s;
assign carry = c;
endmodule

module daddaTree_9x18_msb (
	input  [17:0] PP0,
	input  [17:0] PP1,
	input  [17:0] PP2,
	input  [17:0] PP3,
	input  [17:0] PP4,
	input  [17:0] PP5,
	input  [17:0] PP6,
	input  [17:0] PP7,
	input  [17:0] PP8,
	input  sx,
	input  sy,
	input  flv0,
	input  flv1,
	input  flv2,
	input suppress_sign_x,
	input suppress_sign_y,
	input suppress_sign_e,
	output [26:0] sum,
	output [26:0] carry
);

/***** Dadda Tree Stage 1 *****/
wire [0:0] c1_0;
wire [1:0] c1_1;
wire [2:0] c1_2;
wire [3:0] c1_3;
wire [4:0] c1_4;
wire [5:0] c1_5;
wire [6:0] c1_6;
wire [7:0] c1_7;
wire [8:0] c1_8;
wire [8:0] c1_9;
wire [8:0] c1_10;
wire [8:0] c1_11;
wire [8:0] c1_12;
wire [8:0] c1_13;
wire [8:0] c1_14;
wire [8:0] c1_15;
wire [8:0] c1_16;
wire [8:0] c1_17;
wire [8:0] c1_18;
wire [7:0] c1_19;
wire [5:0] c1_20;
wire [4:0] c1_21;
wire [5:0] c1_22;
wire [2:0] c1_23;
wire [1:0] c1_24;
wire [6:0] c1_25;
wire [5:0] c1_26;

assign c1_0[0] = PP0[0];
assign c1_1[0] = PP0[1];
assign c1_1[1] = PP1[0];
assign c1_2[0] = PP0[2];
assign c1_2[1] = PP1[1];
assign c1_2[2] = PP2[0];
assign c1_3[0] = PP0[3];
assign c1_3[1] = PP1[2];
assign c1_3[2] = PP2[1];
assign c1_3[3] = PP3[0];
assign c1_4[0] = PP0[4];
assign c1_4[1] = PP1[3];
assign c1_4[2] = PP2[2];
assign c1_4[3] = PP3[1];
assign c1_4[4] = PP4[0];
assign c1_5[0] = PP0[5];
assign c1_5[1] = PP1[4];
assign c1_5[2] = PP2[3];
assign c1_5[3] = PP3[2];
assign c1_5[4] = PP4[1];
assign c1_5[5] = PP5[0];
assign c1_6[0] = PP0[6];
assign c1_6[1] = PP1[5];
assign c1_6[2] = PP2[4];
assign c1_6[3] = PP3[3];
assign c1_6[4] = PP4[2];
assign c1_6[5] = PP5[1];
assign c1_6[6] = PP6[0];
assign c1_7[0] = PP0[7];
assign c1_7[1] = PP1[6];
assign c1_7[2] = PP2[5];
assign c1_7[3] = PP3[4];
assign c1_7[4] = PP4[3];
assign c1_7[5] = PP5[2];
assign c1_7[6] = PP6[1];
assign c1_7[7] = PP7[0];
HA_gated ha0 (PP0[8], PP1[7], 1'b1, c1_8[0], c1_9[0]);
assign c1_8[1] = PP2[6];
assign c1_8[2] = PP3[5];
assign c1_8[3] = PP4[4];
assign c1_8[4] = PP5[3];
assign c1_8[5] = PP6[2];
assign c1_8[6] = PP7[1];
assign c1_8[7] = PP8[0];
assign c1_8[8] = suppress_sign_x & sx & flv0;
HA_gated ha1 (PP0[9], PP1[8], 1'b1, c1_9[1], c1_10[0]);
assign c1_9[2] = PP2[7];
assign c1_9[3] = PP3[6];
assign c1_9[4] = PP4[5];
assign c1_9[5] = PP5[4];
assign c1_9[6] = PP6[3];
assign c1_9[7] = PP7[2];
assign c1_9[8] = PP8[1];
HA_gated ha2 (PP0[10], PP1[9], 1'b1, c1_10[1], c1_11[0]);
assign c1_10[2] = PP2[8];
assign c1_10[3] = PP3[7];
assign c1_10[4] = PP4[6];
assign c1_10[5] = PP5[5];
assign c1_10[6] = PP6[4];
assign c1_10[7] = PP7[3];
assign c1_10[8] = PP8[2];
HA_gated ha3 (PP0[11], PP1[10], 1'b1, c1_11[1], c1_12[0]);
assign c1_11[2] = PP2[9];
assign c1_11[3] = PP3[8];
assign c1_11[4] = PP4[7];
assign c1_11[5] = PP5[6];
assign c1_11[6] = PP6[5];
assign c1_11[7] = PP7[4];
assign c1_11[8] = PP8[3];
FA fa0 (PP0[12], PP1[11], PP2[10], c1_12[1], c1_13[0]);
HA_gated ha4 (PP3[9], PP4[8], 1'b1, c1_12[2], c1_13[1]);
assign c1_12[3] = PP5[7];
assign c1_12[4] = PP6[6];
assign c1_12[5] = PP7[5];
assign c1_12[6] = PP8[4];
assign c1_12[7] = sx & flv2;
assign c1_12[8] = sy & flv2;
FA fa1 (PP0[13], PP1[12], PP2[11], c1_13[2], c1_14[0]);
assign c1_13[3] = PP3[10];
assign c1_13[4] = PP4[9];
assign c1_13[5] = PP5[8];
assign c1_13[6] = PP6[7];
assign c1_13[7] = PP7[6];
assign c1_13[8] = PP8[5];
HA_gated ha5 (PP0[14], PP1[13], 1'b1, c1_14[1], c1_15[0]);
assign c1_14[2] = PP2[12];
assign c1_14[3] = PP3[11];
assign c1_14[4] = PP4[10];
assign c1_14[5] = PP5[9];
assign c1_14[6] = PP6[8];
assign c1_14[7] = PP7[7];
assign c1_14[8] = PP8[6];
FA fa2 (PP0[15], PP1[14], PP2[13], c1_15[1], c1_16[0]);
HA_gated ha6 (PP3[12], PP4[11], 1'b1, c1_15[2], c1_16[1]);
assign c1_15[3] = PP5[10];
assign c1_15[4] = PP6[9];
assign c1_15[5] = PP7[8];
assign c1_15[6] = PP8[7];
assign c1_15[7] = sx & flv2;
assign c1_15[8] = sy & flv2;
FA_gated fa3 (PP0[16], PP1[15], PP2[14], ~(flv2), c1_16[2], c1_17[0]);
FA_gated fa4 (PP3[13], PP4[12], PP5[11], ~(flv2), c1_16[3], c1_17[1]);
assign c1_16[4] = PP6[10];
assign c1_16[5] = PP7[9];
assign c1_16[6] = PP8[8];
assign c1_16[7] = sx & flv2;
assign c1_16[8] = sy & flv2;
FA fa5 (PP0[17], PP1[16], PP2[15], c1_17[2], c1_18[0]);
FA fa6 (PP3[14], PP4[13], PP5[12], c1_17[3], c1_18[1]);
HA_gated ha7 (PP6[11], PP7[10], 1'b1, c1_17[4], c1_18[2]);
assign c1_17[5] = PP8[9];
assign c1_17[6] = suppress_sign_y & sy & flv0;
assign c1_17[7] = sx & flv1;
assign c1_17[8] = sy & flv1;
FA fa7 (PP1[17], PP2[16], PP3[15], c1_18[3], c1_19[0]);
assign c1_18[4] = PP4[14];
assign c1_18[5] = PP5[13];
assign c1_18[6] = PP6[12];
assign c1_18[7] = PP7[11];
assign c1_18[8] = PP8[10];
assign c1_19[1] = PP2[17];
assign c1_19[2] = PP3[16];
assign c1_19[3] = PP4[15];
assign c1_19[4] = PP5[14];
assign c1_19[5] = PP6[13];
assign c1_19[6] = PP7[12];
assign c1_19[7] = PP8[11];
assign c1_20[0] = PP3[17];
assign c1_20[1] = PP4[16];
assign c1_20[2] = PP5[15];
assign c1_20[3] = PP6[14];
assign c1_20[4] = PP7[13];
assign c1_20[5] = PP8[12];
assign c1_21[0] = PP4[17];
assign c1_21[1] = PP5[16];
assign c1_21[2] = PP6[15];
assign c1_21[3] = PP7[14];
assign c1_21[4] = PP8[13];
assign c1_22[0] = PP5[17];
assign c1_22[1] = PP6[16];
assign c1_22[2] = PP7[15];
assign c1_22[3] = PP8[14];
assign c1_22[4] = sx & flv2;
assign c1_22[5] = sy & flv2;
assign c1_23[0] = PP6[17];
assign c1_23[1] = PP7[16];
assign c1_23[2] = PP8[15];
assign c1_24[0] = PP7[17];
assign c1_24[1] = PP8[16];
assign c1_25[0] = PP8[17];
assign c1_25[1] = suppress_sign_e & sx & flv0;
assign c1_25[2] = suppress_sign_e & sy & flv0;
assign c1_25[3] = sx & flv1;
assign c1_25[4] = sy & flv1;
assign c1_25[5] = sx & flv2;
assign c1_25[6] = sy & flv2;
assign c1_26[0] = suppress_sign_e & sx & flv0;
assign c1_26[1] = suppress_sign_e & sy & flv0;
assign c1_26[2] = sx & flv1;
assign c1_26[3] = sy & flv1;
assign c1_26[4] = sx & flv2;
assign c1_26[5] = sy & flv2;

/***** Dadda Tree Stage 2 *****/
wire [0:0] c2_0;
wire [1:0] c2_1;
wire [2:0] c2_2;
wire [3:0] c2_3;
wire [4:0] c2_4;
wire [5:0] c2_5;
wire [5:0] c2_6;
wire [5:0] c2_7;
wire [5:0] c2_8;
wire [5:0] c2_9;
wire [5:0] c2_10;
wire [5:0] c2_11;
wire [5:0] c2_12;
wire [5:0] c2_13;
wire [5:0] c2_14;
wire [5:0] c2_15;
wire [5:0] c2_16;
wire [5:0] c2_17;
wire [5:0] c2_18;
wire [5:0] c2_19;
wire [5:0] c2_20;
wire [5:0] c2_21;
wire [5:0] c2_22;
wire [3:0] c2_23;
wire [1:0] c2_24;
wire [5:0] c2_25;
wire [5:0] c2_26;
wire [0:0] c2_27;

assign c2_0[0] = c1_0[0];
assign c2_1[0] = c1_1[0];
assign c2_1[1] = c1_1[1];
assign c2_2[0] = c1_2[0];
assign c2_2[1] = c1_2[1];
assign c2_2[2] = c1_2[2];
assign c2_3[0] = c1_3[0];
assign c2_3[1] = c1_3[1];
assign c2_3[2] = c1_3[2];
assign c2_3[3] = c1_3[3];
assign c2_4[0] = c1_4[0];
assign c2_4[1] = c1_4[1];
assign c2_4[2] = c1_4[2];
assign c2_4[3] = c1_4[3];
assign c2_4[4] = c1_4[4];
assign c2_5[0] = c1_5[0];
assign c2_5[1] = c1_5[1];
assign c2_5[2] = c1_5[2];
assign c2_5[3] = c1_5[3];
assign c2_5[4] = c1_5[4];
assign c2_5[5] = c1_5[5];
HA_gated ha8 (c1_6[0], c1_6[1], 1'b1, c2_6[0], c2_7[0]);
assign c2_6[1] = c1_6[2];
assign c2_6[2] = c1_6[3];
assign c2_6[3] = c1_6[4];
assign c2_6[4] = c1_6[5];
assign c2_6[5] = c1_6[6];
FA fa8 (c1_7[0], c1_7[1], c1_7[2], c2_7[1], c2_8[0]);
HA_gated ha9 (c1_7[3], c1_7[4], 1'b1, c2_7[2], c2_8[1]);
assign c2_7[3] = c1_7[5];
assign c2_7[4] = c1_7[6];
assign c2_7[5] = c1_7[7];
FA fa9 (c1_8[0], c1_8[1], c1_8[2], c2_8[2], c2_9[0]);
FA fa10 (c1_8[3], c1_8[4], c1_8[5], c2_8[3], c2_9[1]);
HA_gated ha10 (c1_8[6], c1_8[7], 1'b1, c2_8[4], c2_9[2]);
assign c2_8[5] = c1_8[8];
FA fa11 (c1_9[0], c1_9[1], c1_9[2], c2_9[3], c2_10[0]);
FA fa12 (c1_9[3], c1_9[4], c1_9[5], c2_9[4], c2_10[1]);
FA fa13 (c1_9[6], c1_9[7], c1_9[8], c2_9[5], c2_10[2]);
FA fa14 (c1_10[0], c1_10[1], c1_10[2], c2_10[3], c2_11[0]);
FA fa15 (c1_10[3], c1_10[4], c1_10[5], c2_10[4], c2_11[1]);
FA fa16 (c1_10[6], c1_10[7], c1_10[8], c2_10[5], c2_11[2]);
FA fa17 (c1_11[0], c1_11[1], c1_11[2], c2_11[3], c2_12[0]);
FA fa18 (c1_11[3], c1_11[4], c1_11[5], c2_11[4], c2_12[1]);
FA fa19 (c1_11[6], c1_11[7], c1_11[8], c2_11[5], c2_12[2]);
FA fa20 (c1_12[0], c1_12[1], c1_12[2], c2_12[3], c2_13[0]);
FA fa21 (c1_12[3], c1_12[4], c1_12[5], c2_12[4], c2_13[1]);
FA fa22 (c1_12[6], c1_12[7], c1_12[8], c2_12[5], c2_13[2]);
FA fa23 (c1_13[0], c1_13[1], c1_13[2], c2_13[3], c2_14[0]);
FA fa24 (c1_13[3], c1_13[4], c1_13[5], c2_13[4], c2_14[1]);
FA fa25 (c1_13[6], c1_13[7], c1_13[8], c2_13[5], c2_14[2]);
FA fa26 (c1_14[0], c1_14[1], c1_14[2], c2_14[3], c2_15[0]);
FA fa27 (c1_14[3], c1_14[4], c1_14[5], c2_14[4], c2_15[1]);
FA fa28 (c1_14[6], c1_14[7], c1_14[8], c2_14[5], c2_15[2]);
FA fa29 (c1_15[0], c1_15[1], c1_15[2], c2_15[3], c2_16[0]);
FA fa30 (c1_15[3], c1_15[4], c1_15[5], c2_15[4], c2_16[1]);
FA fa31 (c1_15[6], c1_15[7], c1_15[8], c2_15[5], c2_16[2]);
FA_gated fa32 (c1_16[0], c1_16[1], c1_16[2], ~(flv2), c2_16[3], c2_17[0]);
FA_gated fa33 (c1_16[3], c1_16[4], c1_16[5], ~(flv2), c2_16[4], c2_17[1]);
FA_gated fa34 (c1_16[6], c1_16[7], c1_16[8], ~(flv2), c2_16[5], c2_17[2]);
FA fa35 (c1_17[0], c1_17[1], c1_17[2], c2_17[3], c2_18[0]);
FA fa36 (c1_17[3], c1_17[4], c1_17[5], c2_17[4], c2_18[1]);
FA fa37 (c1_17[6], c1_17[7], c1_17[8], c2_17[5], c2_18[2]);
FA fa38 (c1_18[0], c1_18[1], c1_18[2], c2_18[3], c2_19[0]);
FA fa39 (c1_18[3], c1_18[4], c1_18[5], c2_18[4], c2_19[1]);
FA fa40 (c1_18[6], c1_18[7], c1_18[8], c2_18[5], c2_19[2]);
FA fa41 (c1_19[0], c1_19[1], c1_19[2], c2_19[3], c2_20[0]);
FA fa42 (c1_19[3], c1_19[4], c1_19[5], c2_19[4], c2_20[1]);
HA_gated ha11 (c1_19[6], c1_19[7], 1'b1, c2_19[5], c2_20[2]);
FA fa43 (c1_20[0], c1_20[1], c1_20[2], c2_20[3], c2_21[0]);
HA_gated ha12 (c1_20[3], c1_20[4], 1'b1, c2_20[4], c2_21[1]);
assign c2_20[5] = c1_20[5];
HA_gated ha13 (c1_21[0], c1_21[1], 1'b1, c2_21[2], c2_22[0]);
assign c2_21[3] = c1_21[2];
assign c2_21[4] = c1_21[3];
assign c2_21[5] = c1_21[4];
HA_gated ha14 (c1_22[0], c1_22[1], 1'b1, c2_22[1], c2_23[0]);
assign c2_22[2] = c1_22[2];
assign c2_22[3] = c1_22[3];
assign c2_22[4] = c1_22[4];
assign c2_22[5] = c1_22[5];
assign c2_23[1] = c1_23[0];
assign c2_23[2] = c1_23[1];
assign c2_23[3] = c1_23[2];
assign c2_24[0] = c1_24[0];
assign c2_24[1] = c1_24[1];
HA_gated ha15 (c1_25[0], c1_25[1], 1'b1, c2_25[0], c2_26[0]);
assign c2_25[1] = c1_25[2];
assign c2_25[2] = c1_25[3];
assign c2_25[3] = c1_25[4];
assign c2_25[4] = c1_25[5];
assign c2_25[5] = c1_25[6];
HA_gated ha16 (c1_26[0], c1_26[1], 1'b1, c2_26[1], c2_27[0]);
assign c2_26[2] = c1_26[2];
assign c2_26[3] = c1_26[3];
assign c2_26[4] = c1_26[4];
assign c2_26[5] = c1_26[5];

/***** Dadda Tree Stage 3 *****/
wire [0:0] c3_0;
wire [1:0] c3_1;
wire [2:0] c3_2;
wire [3:0] c3_3;
wire [3:0] c3_4;
wire [3:0] c3_5;
wire [3:0] c3_6;
wire [3:0] c3_7;
wire [3:0] c3_8;
wire [3:0] c3_9;
wire [3:0] c3_10;
wire [3:0] c3_11;
wire [3:0] c3_12;
wire [3:0] c3_13;
wire [3:0] c3_14;
wire [3:0] c3_15;
wire [3:0] c3_16;
wire [3:0] c3_17;
wire [3:0] c3_18;
wire [3:0] c3_19;
wire [3:0] c3_20;
wire [3:0] c3_21;
wire [3:0] c3_22;
wire [3:0] c3_23;
wire [2:0] c3_24;
wire [3:0] c3_25;
wire [3:0] c3_26;
wire [1:0] c3_27;

assign c3_0[0] = c2_0[0];
assign c3_1[0] = c2_1[0];
assign c3_1[1] = c2_1[1];
assign c3_2[0] = c2_2[0];
assign c3_2[1] = c2_2[1];
assign c3_2[2] = c2_2[2];
assign c3_3[0] = c2_3[0];
assign c3_3[1] = c2_3[1];
assign c3_3[2] = c2_3[2];
assign c3_3[3] = c2_3[3];
HA_gated ha17 (c2_4[0], c2_4[1], 1'b1, c3_4[0], c3_5[0]);
assign c3_4[1] = c2_4[2];
assign c3_4[2] = c2_4[3];
assign c3_4[3] = c2_4[4];
FA fa44 (c2_5[0], c2_5[1], c2_5[2], c3_5[1], c3_6[0]);
HA_gated ha18 (c2_5[3], c2_5[4], 1'b1, c3_5[2], c3_6[1]);
assign c3_5[3] = c2_5[5];
FA fa45 (c2_6[0], c2_6[1], c2_6[2], c3_6[2], c3_7[0]);
FA fa46 (c2_6[3], c2_6[4], c2_6[5], c3_6[3], c3_7[1]);
FA fa47 (c2_7[0], c2_7[1], c2_7[2], c3_7[2], c3_8[0]);
FA fa48 (c2_7[3], c2_7[4], c2_7[5], c3_7[3], c3_8[1]);
FA fa49 (c2_8[0], c2_8[1], c2_8[2], c3_8[2], c3_9[0]);
FA fa50 (c2_8[3], c2_8[4], c2_8[5], c3_8[3], c3_9[1]);
FA fa51 (c2_9[0], c2_9[1], c2_9[2], c3_9[2], c3_10[0]);
FA fa52 (c2_9[3], c2_9[4], c2_9[5], c3_9[3], c3_10[1]);
FA fa53 (c2_10[0], c2_10[1], c2_10[2], c3_10[2], c3_11[0]);
FA fa54 (c2_10[3], c2_10[4], c2_10[5], c3_10[3], c3_11[1]);
FA fa55 (c2_11[0], c2_11[1], c2_11[2], c3_11[2], c3_12[0]);
FA fa56 (c2_11[3], c2_11[4], c2_11[5], c3_11[3], c3_12[1]);
FA fa57 (c2_12[0], c2_12[1], c2_12[2], c3_12[2], c3_13[0]);
FA fa58 (c2_12[3], c2_12[4], c2_12[5], c3_12[3], c3_13[1]);
FA fa59 (c2_13[0], c2_13[1], c2_13[2], c3_13[2], c3_14[0]);
FA fa60 (c2_13[3], c2_13[4], c2_13[5], c3_13[3], c3_14[1]);
FA fa61 (c2_14[0], c2_14[1], c2_14[2], c3_14[2], c3_15[0]);
FA fa62 (c2_14[3], c2_14[4], c2_14[5], c3_14[3], c3_15[1]);
FA fa63 (c2_15[0], c2_15[1], c2_15[2], c3_15[2], c3_16[0]);
FA fa64 (c2_15[3], c2_15[4], c2_15[5], c3_15[3], c3_16[1]);
FA_gated fa65 (c2_16[0], c2_16[1], c2_16[2], ~(flv2), c3_16[2], c3_17[0]);
FA_gated fa66 (c2_16[3], c2_16[4], c2_16[5], ~(flv2), c3_16[3], c3_17[1]);
FA fa67 (c2_17[0], c2_17[1], c2_17[2], c3_17[2], c3_18[0]);
FA fa68 (c2_17[3], c2_17[4], c2_17[5], c3_17[3], c3_18[1]);
FA fa69 (c2_18[0], c2_18[1], c2_18[2], c3_18[2], c3_19[0]);
FA fa70 (c2_18[3], c2_18[4], c2_18[5], c3_18[3], c3_19[1]);
FA fa71 (c2_19[0], c2_19[1], c2_19[2], c3_19[2], c3_20[0]);
FA fa72 (c2_19[3], c2_19[4], c2_19[5], c3_19[3], c3_20[1]);
FA fa73 (c2_20[0], c2_20[1], c2_20[2], c3_20[2], c3_21[0]);
FA fa74 (c2_20[3], c2_20[4], c2_20[5], c3_20[3], c3_21[1]);
FA fa75 (c2_21[0], c2_21[1], c2_21[2], c3_21[2], c3_22[0]);
FA fa76 (c2_21[3], c2_21[4], c2_21[5], c3_21[3], c3_22[1]);
FA fa77 (c2_22[0], c2_22[1], c2_22[2], c3_22[2], c3_23[0]);
FA fa78 (c2_22[3], c2_22[4], c2_22[5], c3_22[3], c3_23[1]);
FA fa79 (c2_23[0], c2_23[1], c2_23[2], c3_23[2], c3_24[0]);
assign c3_23[3] = c2_23[3];
assign c3_24[1] = c2_24[0];
assign c3_24[2] = c2_24[1];
FA fa80 (c2_25[0], c2_25[1], c2_25[2], c3_25[0], c3_26[0]);
assign c3_25[1] = c2_25[3];
assign c3_25[2] = c2_25[4];
assign c3_25[3] = c2_25[5];
FA fa81 (c2_26[0], c2_26[1], c2_26[2], c3_26[1], c3_27[0]);
HA_gated ha19 (c2_26[3], c2_26[4], 1'b1, c3_26[2], c3_27[1]);
assign c3_26[3] = c2_26[5];

/***** Dadda Tree Stage 4 *****/
wire [0:0] c4_0;
wire [1:0] c4_1;
wire [2:0] c4_2;
wire [2:0] c4_3;
wire [2:0] c4_4;
wire [2:0] c4_5;
wire [2:0] c4_6;
wire [2:0] c4_7;
wire [2:0] c4_8;
wire [2:0] c4_9;
wire [2:0] c4_10;
wire [2:0] c4_11;
wire [2:0] c4_12;
wire [2:0] c4_13;
wire [2:0] c4_14;
wire [2:0] c4_15;
wire [2:0] c4_16;
wire [2:0] c4_17;
wire [2:0] c4_18;
wire [2:0] c4_19;
wire [2:0] c4_20;
wire [2:0] c4_21;
wire [2:0] c4_22;
wire [2:0] c4_23;
wire [2:0] c4_24;
wire [2:0] c4_25;
wire [2:0] c4_26;
wire [0:0] c4_27;

assign c4_0[0] = c3_0[0];
assign c4_1[0] = c3_1[0];
assign c4_1[1] = c3_1[1];
assign c4_2[0] = c3_2[0];
assign c4_2[1] = c3_2[1];
assign c4_2[2] = c3_2[2];
HA_gated ha20 (c3_3[0], c3_3[1], 1'b1, c4_3[0], c4_4[0]);
assign c4_3[1] = c3_3[2];
assign c4_3[2] = c3_3[3];
FA fa82 (c3_4[0], c3_4[1], c3_4[2], c4_4[1], c4_5[0]);
assign c4_4[2] = c3_4[3];
FA fa83 (c3_5[0], c3_5[1], c3_5[2], c4_5[1], c4_6[0]);
assign c4_5[2] = c3_5[3];
FA fa84 (c3_6[0], c3_6[1], c3_6[2], c4_6[1], c4_7[0]);
assign c4_6[2] = c3_6[3];
FA fa85 (c3_7[0], c3_7[1], c3_7[2], c4_7[1], c4_8[0]);
assign c4_7[2] = c3_7[3];
FA fa86 (c3_8[0], c3_8[1], c3_8[2], c4_8[1], c4_9[0]);
assign c4_8[2] = c3_8[3];
FA fa87 (c3_9[0], c3_9[1], c3_9[2], c4_9[1], c4_10[0]);
assign c4_9[2] = c3_9[3];
FA fa88 (c3_10[0], c3_10[1], c3_10[2], c4_10[1], c4_11[0]);
assign c4_10[2] = c3_10[3];
FA fa89 (c3_11[0], c3_11[1], c3_11[2], c4_11[1], c4_12[0]);
assign c4_11[2] = c3_11[3];
FA fa90 (c3_12[0], c3_12[1], c3_12[2], c4_12[1], c4_13[0]);
assign c4_12[2] = c3_12[3];
FA fa91 (c3_13[0], c3_13[1], c3_13[2], c4_13[1], c4_14[0]);
assign c4_13[2] = c3_13[3];
FA fa92 (c3_14[0], c3_14[1], c3_14[2], c4_14[1], c4_15[0]);
assign c4_14[2] = c3_14[3];
FA fa93 (c3_15[0], c3_15[1], c3_15[2], c4_15[1], c4_16[0]);
assign c4_15[2] = c3_15[3];
FA_gated fa94 (c3_16[0], c3_16[1], c3_16[2], ~(flv2), c4_16[1], c4_17[0]);
assign c4_16[2] = c3_16[3];
FA fa95 (c3_17[0], c3_17[1], c3_17[2], c4_17[1], c4_18[0]);
assign c4_17[2] = c3_17[3];
FA fa96 (c3_18[0], c3_18[1], c3_18[2], c4_18[1], c4_19[0]);
assign c4_18[2] = c3_18[3];
FA fa97 (c3_19[0], c3_19[1], c3_19[2], c4_19[1], c4_20[0]);
assign c4_19[2] = c3_19[3];
FA fa98 (c3_20[0], c3_20[1], c3_20[2], c4_20[1], c4_21[0]);
assign c4_20[2] = c3_20[3];
FA fa99 (c3_21[0], c3_21[1], c3_21[2], c4_21[1], c4_22[0]);
assign c4_21[2] = c3_21[3];
FA fa100 (c3_22[0], c3_22[1], c3_22[2], c4_22[1], c4_23[0]);
assign c4_22[2] = c3_22[3];
FA fa101 (c3_23[0], c3_23[1], c3_23[2], c4_23[1], c4_24[0]);
assign c4_23[2] = c3_23[3];
HA_gated ha21 (c3_24[0], c3_24[1], 1'b1, c4_24[1], c4_25[0]);
assign c4_24[2] = c3_24[2];
FA fa102 (c3_25[0], c3_25[1], c3_25[2], c4_25[1], c4_26[0]);
assign c4_25[2] = c3_25[3];
FA fa103 (c3_26[0], c3_26[1], c3_26[2], c4_26[1], c4_27[0]);
assign c4_26[2] = c3_26[3];

/***** Dadda Tree Stage 5 *****/
wire [0:0] c5_0;
wire [1:0] c5_1;
wire [1:0] c5_2;
wire [1:0] c5_3;
wire [1:0] c5_4;
wire [1:0] c5_5;
wire [1:0] c5_6;
wire [1:0] c5_7;
wire [1:0] c5_8;
wire [1:0] c5_9;
wire [1:0] c5_10;
wire [1:0] c5_11;
wire [1:0] c5_12;
wire [1:0] c5_13;
wire [1:0] c5_14;
wire [1:0] c5_15;
wire [1:0] c5_16;
wire [1:0] c5_17;
wire [1:0] c5_18;
wire [1:0] c5_19;
wire [1:0] c5_20;
wire [1:0] c5_21;
wire [1:0] c5_22;
wire [1:0] c5_23;
wire [1:0] c5_24;
wire [1:0] c5_25;
wire [1:0] c5_26;
wire [0:0] c5_27;

assign c5_0[0] = c4_0[0];
assign c5_1[0] = c4_1[0];
assign c5_1[1] = c4_1[1];
HA_gated ha22 (c4_2[0], c4_2[1], 1'b1, c5_2[0], c5_3[0]);
assign c5_2[1] = c4_2[2];
FA fa104 (c4_3[0], c4_3[1], c4_3[2], c5_3[1], c5_4[0]);
FA fa105 (c4_4[0], c4_4[1], c4_4[2], c5_4[1], c5_5[0]);
FA fa106 (c4_5[0], c4_5[1], c4_5[2], c5_5[1], c5_6[0]);
FA fa107 (c4_6[0], c4_6[1], c4_6[2], c5_6[1], c5_7[0]);
FA fa108 (c4_7[0], c4_7[1], c4_7[2], c5_7[1], c5_8[0]);
FA fa109 (c4_8[0], c4_8[1], c4_8[2], c5_8[1], c5_9[0]);
FA fa110 (c4_9[0], c4_9[1], c4_9[2], c5_9[1], c5_10[0]);
FA fa111 (c4_10[0], c4_10[1], c4_10[2], c5_10[1], c5_11[0]);
FA fa112 (c4_11[0], c4_11[1], c4_11[2], c5_11[1], c5_12[0]);
FA fa113 (c4_12[0], c4_12[1], c4_12[2], c5_12[1], c5_13[0]);
FA fa114 (c4_13[0], c4_13[1], c4_13[2], c5_13[1], c5_14[0]);
FA fa115 (c4_14[0], c4_14[1], c4_14[2], c5_14[1], c5_15[0]);
FA fa116 (c4_15[0], c4_15[1], c4_15[2], c5_15[1], c5_16[0]);
FA_gated fa117 (c4_16[0], c4_16[1], c4_16[2], ~(flv2), c5_16[1], c5_17[0]);
FA fa118 (c4_17[0], c4_17[1], c4_17[2], c5_17[1], c5_18[0]);
FA fa119 (c4_18[0], c4_18[1], c4_18[2], c5_18[1], c5_19[0]);
FA fa120 (c4_19[0], c4_19[1], c4_19[2], c5_19[1], c5_20[0]);
FA fa121 (c4_20[0], c4_20[1], c4_20[2], c5_20[1], c5_21[0]);
FA fa122 (c4_21[0], c4_21[1], c4_21[2], c5_21[1], c5_22[0]);
FA fa123 (c4_22[0], c4_22[1], c4_22[2], c5_22[1], c5_23[0]);
FA fa124 (c4_23[0], c4_23[1], c4_23[2], c5_23[1], c5_24[0]);
FA fa125 (c4_24[0], c4_24[1], c4_24[2], c5_24[1], c5_25[0]);
FA fa126 (c4_25[0], c4_25[1], c4_25[2], c5_25[1], c5_26[0]);
FA fa127 (c4_26[0], c4_26[1], c4_26[2], c5_26[1], c5_27[0]);

assign sum = {c5_26[0],c5_25[0],c5_24[0],c5_23[0],c5_22[0],c5_21[0],c5_20[0],c5_19[0],c5_18[0],c5_17[0],c5_16[0],c5_15[0],c5_14[0],c5_13[0],c5_12[0],c5_11[0],c5_10[0],c5_9[0],c5_8[0],c5_7[0],c5_6[0],c5_5[0],c5_4[0],c5_3[0],c5_2[0],c5_1[0],c5_0[0]};
assign carry = {c5_26[1],c5_25[1],c5_24[1],c5_23[1],c5_22[1],c5_21[1],c5_20[1],c5_19[1],c5_18[1],c5_17[1],c5_16[1],c5_15[1],c5_14[1],c5_13[1],c5_12[1],c5_11[1],c5_10[1],c5_9[1],c5_8[1],c5_7[1],c5_6[1],c5_5[1],c5_4[1],c5_3[1],c5_2[1],c5_1[1], 1'b0};

endmodule

module multiplier_9x9 (
	input  clk,
	input  [8:0] data_x,
	input  [8:0] data_y,
	input  signed_x,
	input  signed_y,
	input  flv0,
	input  flv1,
	output [17:0] sum,
	output [17:0] carry
);

wire [8:0] PP [8:0];
wire [17:0] dadda_sum, dadda_carry;
reg [8:0] x;
reg [8:0] y;
reg sign_x;
reg sign_y;
reg [17:0] s;
reg [17:0] c;

always @ (*)
begin: reg_in_out
	x <= data_x;
	y <= data_y;
	sign_x <= signed_x;
	sign_y <= signed_y;
	s <= dadda_sum;
	c <= dadda_carry;
end

arrayBlock_unsigned_gated BLK0 (.A(y[0]), .B(x[0]), .enable(1'b1), .mult(PP[0][0]));
arrayBlock_unsigned_gated BLK1 (.A(y[1]), .B(x[0]), .enable(1'b1), .mult(PP[0][1]));
arrayBlock_unsigned_gated BLK2 (.A(y[2]), .B(x[0]), .enable(1'b1), .mult(PP[0][2]));
arrayBlock_signed_gated BLK3 (.A(y[3]), .B(x[0]), .enable(1'b1), .signed_ctrl(sign_y & (flv1)), .mult(PP[0][3]));
arrayBlock_unsigned_gated BLK4 (.A(y[4]), .B(x[0]), .enable(flv0), .mult(PP[0][4]));
arrayBlock_unsigned_gated BLK5 (.A(y[5]), .B(x[0]), .enable(flv0), .mult(PP[0][5]));
arrayBlock_unsigned_gated BLK6 (.A(y[6]), .B(x[0]), .enable(flv0), .mult(PP[0][6]));
arrayBlock_unsigned_gated BLK7 (.A(y[7]), .B(x[0]), .enable(flv0), .mult(PP[0][7]));
arrayBlock_signed_gated BLK8 (.A(y[8]), .B(x[0]), .enable(flv0), .signed_ctrl(sign_y & (flv0)), .mult(PP[0][8]));
arrayBlock_unsigned_gated BLK9 (.A(y[0]), .B(x[1]), .enable(1'b1), .mult(PP[1][0]));
arrayBlock_unsigned_gated BLK10 (.A(y[1]), .B(x[1]), .enable(1'b1), .mult(PP[1][1]));
arrayBlock_unsigned_gated BLK11 (.A(y[2]), .B(x[1]), .enable(1'b1), .mult(PP[1][2]));
arrayBlock_signed_gated BLK12 (.A(y[3]), .B(x[1]), .enable(1'b1), .signed_ctrl(sign_y & (flv1)), .mult(PP[1][3]));
arrayBlock_unsigned_gated BLK13 (.A(y[4]), .B(x[1]), .enable(flv0), .mult(PP[1][4]));
arrayBlock_unsigned_gated BLK14 (.A(y[5]), .B(x[1]), .enable(flv0), .mult(PP[1][5]));
arrayBlock_unsigned_gated BLK15 (.A(y[6]), .B(x[1]), .enable(flv0), .mult(PP[1][6]));
arrayBlock_unsigned_gated BLK16 (.A(y[7]), .B(x[1]), .enable(flv0), .mult(PP[1][7]));
arrayBlock_signed_gated BLK17 (.A(y[8]), .B(x[1]), .enable(flv0), .signed_ctrl(sign_y & (flv0)), .mult(PP[1][8]));
arrayBlock_unsigned_gated BLK18 (.A(y[0]), .B(x[2]), .enable(1'b1), .mult(PP[2][0]));
arrayBlock_unsigned_gated BLK19 (.A(y[1]), .B(x[2]), .enable(1'b1), .mult(PP[2][1]));
arrayBlock_unsigned_gated BLK20 (.A(y[2]), .B(x[2]), .enable(1'b1), .mult(PP[2][2]));
arrayBlock_signed_gated BLK21 (.A(y[3]), .B(x[2]), .enable(1'b1), .signed_ctrl(sign_y & (flv1)), .mult(PP[2][3]));
arrayBlock_unsigned_gated BLK22 (.A(y[4]), .B(x[2]), .enable(flv0), .mult(PP[2][4]));
arrayBlock_unsigned_gated BLK23 (.A(y[5]), .B(x[2]), .enable(flv0), .mult(PP[2][5]));
arrayBlock_unsigned_gated BLK24 (.A(y[6]), .B(x[2]), .enable(flv0), .mult(PP[2][6]));
arrayBlock_unsigned_gated BLK25 (.A(y[7]), .B(x[2]), .enable(flv0), .mult(PP[2][7]));
arrayBlock_signed_gated BLK26 (.A(y[8]), .B(x[2]), .enable(flv0), .signed_ctrl(sign_y & (flv0)), .mult(PP[2][8]));
arrayBlock_signed_gated BLK27 (.A(y[0]), .B(x[3]), .enable(1'b1), .signed_ctrl(sign_x & (flv1)), .mult(PP[3][0]));
arrayBlock_signed_gated BLK28 (.A(y[1]), .B(x[3]), .enable(1'b1), .signed_ctrl(sign_x & (flv1)), .mult(PP[3][1]));
arrayBlock_signed_gated BLK29 (.A(y[2]), .B(x[3]), .enable(1'b1), .signed_ctrl(sign_x & (flv1)), .mult(PP[3][2]));
arrayBlock_unsigned_gated BLK30 (.A(y[3]), .B(x[3]), .enable(1'b1), .mult(PP[3][3]));
arrayBlock_unsigned_gated BLK31 (.A(y[4]), .B(x[3]), .enable(flv0), .mult(PP[3][4]));
arrayBlock_unsigned_gated BLK32 (.A(y[5]), .B(x[3]), .enable(flv0), .mult(PP[3][5]));
arrayBlock_unsigned_gated BLK33 (.A(y[6]), .B(x[3]), .enable(flv0), .mult(PP[3][6]));
arrayBlock_unsigned_gated BLK34 (.A(y[7]), .B(x[3]), .enable(flv0), .mult(PP[3][7]));
arrayBlock_signed_gated BLK35 (.A(y[8]), .B(x[3]), .enable(flv0), .signed_ctrl(sign_y & (flv0)), .mult(PP[3][8]));
arrayBlock_unsigned_gated BLK36 (.A(y[0]), .B(x[4]), .enable(flv0), .mult(PP[4][0]));
arrayBlock_unsigned_gated BLK37 (.A(y[1]), .B(x[4]), .enable(flv0), .mult(PP[4][1]));
arrayBlock_unsigned_gated BLK38 (.A(y[2]), .B(x[4]), .enable(flv0), .mult(PP[4][2]));
arrayBlock_unsigned_gated BLK39 (.A(y[3]), .B(x[4]), .enable(flv0), .mult(PP[4][3]));
arrayBlock_unsigned_gated BLK40 (.A(y[4]), .B(x[4]), .enable(flv0), .mult(PP[4][4]));
arrayBlock_unsigned_gated BLK41 (.A(y[5]), .B(x[4]), .enable(flv0), .mult(PP[4][5]));
arrayBlock_unsigned_gated BLK42 (.A(y[6]), .B(x[4]), .enable(flv0), .mult(PP[4][6]));
arrayBlock_unsigned_gated BLK43 (.A(y[7]), .B(x[4]), .enable(flv0), .mult(PP[4][7]));
arrayBlock_signed_gated BLK44 (.A(y[8]), .B(x[4]), .enable(flv0), .signed_ctrl(sign_y & (flv0)), .mult(PP[4][8]));
arrayBlock_unsigned_gated BLK45 (.A(y[0]), .B(x[5]), .enable(flv0), .mult(PP[5][0]));
arrayBlock_unsigned_gated BLK46 (.A(y[1]), .B(x[5]), .enable(flv0), .mult(PP[5][1]));
arrayBlock_unsigned_gated BLK47 (.A(y[2]), .B(x[5]), .enable(flv0), .mult(PP[5][2]));
arrayBlock_unsigned_gated BLK48 (.A(y[3]), .B(x[5]), .enable(flv0), .mult(PP[5][3]));
arrayBlock_unsigned_gated BLK49 (.A(y[4]), .B(x[5]), .enable(flv0), .mult(PP[5][4]));
arrayBlock_unsigned_gated BLK50 (.A(y[5]), .B(x[5]), .enable(1'b1), .mult(PP[5][5]));
arrayBlock_unsigned_gated BLK51 (.A(y[6]), .B(x[5]), .enable(1'b1), .mult(PP[5][6]));
arrayBlock_unsigned_gated BLK52 (.A(y[7]), .B(x[5]), .enable(1'b1), .mult(PP[5][7]));
arrayBlock_signed_gated BLK53 (.A(y[8]), .B(x[5]), .enable(1'b1), .signed_ctrl(sign_y & (flv0 | flv1)), .mult(PP[5][8]));
arrayBlock_unsigned_gated BLK54 (.A(y[0]), .B(x[6]), .enable(flv0), .mult(PP[6][0]));
arrayBlock_unsigned_gated BLK55 (.A(y[1]), .B(x[6]), .enable(flv0), .mult(PP[6][1]));
arrayBlock_unsigned_gated BLK56 (.A(y[2]), .B(x[6]), .enable(flv0), .mult(PP[6][2]));
arrayBlock_unsigned_gated BLK57 (.A(y[3]), .B(x[6]), .enable(flv0), .mult(PP[6][3]));
arrayBlock_unsigned_gated BLK58 (.A(y[4]), .B(x[6]), .enable(flv0), .mult(PP[6][4]));
arrayBlock_unsigned_gated BLK59 (.A(y[5]), .B(x[6]), .enable(1'b1), .mult(PP[6][5]));
arrayBlock_unsigned_gated BLK60 (.A(y[6]), .B(x[6]), .enable(1'b1), .mult(PP[6][6]));
arrayBlock_unsigned_gated BLK61 (.A(y[7]), .B(x[6]), .enable(1'b1), .mult(PP[6][7]));
arrayBlock_signed_gated BLK62 (.A(y[8]), .B(x[6]), .enable(1'b1), .signed_ctrl(sign_y & (flv0 | flv1)), .mult(PP[6][8]));
arrayBlock_unsigned_gated BLK63 (.A(y[0]), .B(x[7]), .enable(flv0), .mult(PP[7][0]));
arrayBlock_unsigned_gated BLK64 (.A(y[1]), .B(x[7]), .enable(flv0), .mult(PP[7][1]));
arrayBlock_unsigned_gated BLK65 (.A(y[2]), .B(x[7]), .enable(flv0), .mult(PP[7][2]));
arrayBlock_unsigned_gated BLK66 (.A(y[3]), .B(x[7]), .enable(flv0), .mult(PP[7][3]));
arrayBlock_unsigned_gated BLK67 (.A(y[4]), .B(x[7]), .enable(flv0), .mult(PP[7][4]));
arrayBlock_unsigned_gated BLK68 (.A(y[5]), .B(x[7]), .enable(1'b1), .mult(PP[7][5]));
arrayBlock_unsigned_gated BLK69 (.A(y[6]), .B(x[7]), .enable(1'b1), .mult(PP[7][6]));
arrayBlock_unsigned_gated BLK70 (.A(y[7]), .B(x[7]), .enable(1'b1), .mult(PP[7][7]));
arrayBlock_signed_gated BLK71 (.A(y[8]), .B(x[7]), .enable(1'b1), .signed_ctrl(sign_y & (flv0 | flv1)), .mult(PP[7][8]));
arrayBlock_signed_gated BLK72 (.A(y[0]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][0]));
arrayBlock_signed_gated BLK73 (.A(y[1]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][1]));
arrayBlock_signed_gated BLK74 (.A(y[2]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][2]));
arrayBlock_signed_gated BLK75 (.A(y[3]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][3]));
arrayBlock_signed_gated BLK76 (.A(y[4]), .B(x[8]), .enable(flv0), .signed_ctrl(sign_x & (flv0)), .mult(PP[8][4]));
arrayBlock_signed_gated BLK77 (.A(y[5]), .B(x[8]), .enable(1'b1), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][5]));
arrayBlock_signed_gated BLK78 (.A(y[6]), .B(x[8]), .enable(1'b1), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][6]));
arrayBlock_signed_gated BLK79 (.A(y[7]), .B(x[8]), .enable(1'b1), .signed_ctrl(sign_x & (flv0 | flv1)), .mult(PP[8][7]));
arrayBlock_unsigned_gated BLK80 (.A(y[8]), .B(x[8]), .enable(1'b1), .mult(PP[8][8]));

daddaTree_9x9 DT (
	.PP0(PP[0]),
	.PP1(PP[1]),
	.PP2(PP[2]),
	.PP3(PP[3]),
	.PP4(PP[4]),
	.PP5(PP[5]),
	.PP6(PP[6]),
	.PP7(PP[7]),
	.PP8(PP[8]),
	.sx(sign_x),
	.sy(sign_y),
	.flv0(flv0),
	.flv1(flv1),
	.sum(dadda_sum),
	.carry(dadda_carry)
);

assign sum = s;
assign carry = c;
endmodule

module daddaTree_9x9 (
	input  [8:0] PP0,
	input  [8:0] PP1,
	input  [8:0] PP2,
	input  [8:0] PP3,
	input  [8:0] PP4,
	input  [8:0] PP5,
	input  [8:0] PP6,
	input  [8:0] PP7,
	input  [8:0] PP8,
	input  sx,
	input  sy,
	input  flv0,
	input  flv1,
	output [17:0] sum,
	output [17:0] carry
);

/***** Dadda Tree Stage 1 *****/
wire [0:0] c1_0;
wire [1:0] c1_1;
wire [2:0] c1_2;
wire [5:0] c1_3;
wire [4:0] c1_4;
wire [5:0] c1_5;
wire [8:0] c1_6;
wire [8:0] c1_7;
wire [8:0] c1_8;
wire [8:0] c1_9;
wire [7:0] c1_10;
wire [5:0] c1_11;
wire [4:0] c1_12;
wire [5:0] c1_13;
wire [2:0] c1_14;
wire [1:0] c1_15;
wire [4:0] c1_16;
wire [3:0] c1_17;

assign c1_0[0] = PP0[0];
assign c1_1[0] = PP0[1];
assign c1_1[1] = PP1[0];
assign c1_2[0] = PP0[2];
assign c1_2[1] = PP1[1];
assign c1_2[2] = PP2[0];
assign c1_3[0] = PP0[3];
assign c1_3[1] = PP1[2];
assign c1_3[2] = PP2[1];
assign c1_3[3] = PP3[0];
assign c1_3[4] = sx & flv1;
assign c1_3[5] = sy & flv1;
assign c1_4[0] = PP0[4];
assign c1_4[1] = PP1[3];
assign c1_4[2] = PP2[2];
assign c1_4[3] = PP3[1];
assign c1_4[4] = PP4[0];
assign c1_5[0] = PP0[5];
assign c1_5[1] = PP1[4];
assign c1_5[2] = PP2[3];
assign c1_5[3] = PP3[2];
assign c1_5[4] = PP4[1];
assign c1_5[5] = PP5[0];
assign c1_6[0] = PP0[6];
assign c1_6[1] = PP1[5];
assign c1_6[2] = PP2[4];
assign c1_6[3] = PP3[3];
assign c1_6[4] = PP4[2];
assign c1_6[5] = PP5[1];
assign c1_6[6] = PP6[0];
assign c1_6[7] = sx & flv1;
assign c1_6[8] = sy & flv1;
HA_gated ha0 (PP0[7], PP1[6], ~(flv1), c1_7[0], c1_8[0]);
assign c1_7[1] = PP2[5];
assign c1_7[2] = PP3[4];
assign c1_7[3] = PP4[3];
assign c1_7[4] = PP5[2];
assign c1_7[5] = PP6[1];
assign c1_7[6] = PP7[0];
assign c1_7[7] = sx & flv1;
assign c1_7[8] = sy & flv1;
FA fa0 (PP0[8], PP1[7], PP2[6], c1_8[1], c1_9[0]);
HA_gated ha1 (PP3[5], PP4[4], 1'b1, c1_8[2], c1_9[1]);
assign c1_8[3] = PP5[3];
assign c1_8[4] = PP6[2];
assign c1_8[5] = PP7[1];
assign c1_8[6] = PP8[0];
assign c1_8[7] = sx & flv0;
assign c1_8[8] = sy & flv0;
HA_gated ha2 (PP1[8], PP2[7], 1'b1, c1_9[2], c1_10[0]);
assign c1_9[3] = PP3[6];
assign c1_9[4] = PP4[5];
assign c1_9[5] = PP5[4];
assign c1_9[6] = PP6[3];
assign c1_9[7] = PP7[2];
assign c1_9[8] = PP8[1];
assign c1_10[1] = PP2[8];
assign c1_10[2] = PP3[7];
assign c1_10[3] = PP4[6];
assign c1_10[4] = PP5[5];
assign c1_10[5] = PP6[4];
assign c1_10[6] = PP7[3];
assign c1_10[7] = PP8[2];
assign c1_11[0] = PP3[8];
assign c1_11[1] = PP4[7];
assign c1_11[2] = PP5[6];
assign c1_11[3] = PP6[5];
assign c1_11[4] = PP7[4];
assign c1_11[5] = PP8[3];
assign c1_12[0] = PP4[8];
assign c1_12[1] = PP5[7];
assign c1_12[2] = PP6[6];
assign c1_12[3] = PP7[5];
assign c1_12[4] = PP8[4];
assign c1_13[0] = PP5[8];
assign c1_13[1] = PP6[7];
assign c1_13[2] = PP7[6];
assign c1_13[3] = PP8[5];
assign c1_13[4] = sx & flv1;
assign c1_13[5] = sy & flv1;
assign c1_14[0] = PP6[8];
assign c1_14[1] = PP7[7];
assign c1_14[2] = PP8[6];
assign c1_15[0] = PP7[8];
assign c1_15[1] = PP8[7];
assign c1_16[0] = PP8[8];
assign c1_16[1] = sx & flv0;
assign c1_16[2] = sy & flv0;
assign c1_16[3] = sx & flv1;
assign c1_16[4] = sy & flv1;
assign c1_17[0] = sx & flv0;
assign c1_17[1] = sy & flv0;
assign c1_17[2] = sx & flv1;
assign c1_17[3] = sy & flv1;

/***** Dadda Tree Stage 2 *****/
wire [0:0] c2_0;
wire [1:0] c2_1;
wire [2:0] c2_2;
wire [5:0] c2_3;
wire [4:0] c2_4;
wire [5:0] c2_5;
wire [5:0] c2_6;
wire [5:0] c2_7;
wire [5:0] c2_8;
wire [5:0] c2_9;
wire [5:0] c2_10;
wire [5:0] c2_11;
wire [5:0] c2_12;
wire [5:0] c2_13;
wire [3:0] c2_14;
wire [1:0] c2_15;
wire [4:0] c2_16;
wire [3:0] c2_17;

assign c2_0[0] = c1_0[0];
assign c2_1[0] = c1_1[0];
assign c2_1[1] = c1_1[1];
assign c2_2[0] = c1_2[0];
assign c2_2[1] = c1_2[1];
assign c2_2[2] = c1_2[2];
assign c2_3[0] = c1_3[0];
assign c2_3[1] = c1_3[1];
assign c2_3[2] = c1_3[2];
assign c2_3[3] = c1_3[3];
assign c2_3[4] = c1_3[4];
assign c2_3[5] = c1_3[5];
assign c2_4[0] = c1_4[0];
assign c2_4[1] = c1_4[1];
assign c2_4[2] = c1_4[2];
assign c2_4[3] = c1_4[3];
assign c2_4[4] = c1_4[4];
assign c2_5[0] = c1_5[0];
assign c2_5[1] = c1_5[1];
assign c2_5[2] = c1_5[2];
assign c2_5[3] = c1_5[3];
assign c2_5[4] = c1_5[4];
assign c2_5[5] = c1_5[5];
FA fa1 (c1_6[0], c1_6[1], c1_6[2], c2_6[0], c2_7[0]);
HA_gated ha3 (c1_6[3], c1_6[4], 1'b1, c2_6[1], c2_7[1]);
assign c2_6[2] = c1_6[5];
assign c2_6[3] = c1_6[6];
assign c2_6[4] = c1_6[7];
assign c2_6[5] = c1_6[8];
FA_gated fa2 (c1_7[0], c1_7[1], c1_7[2], ~(flv1), c2_7[2], c2_8[0]);
FA_gated fa3 (c1_7[3], c1_7[4], c1_7[5], ~(flv1), c2_7[3], c2_8[1]);
HA_gated ha4 (c1_7[6], c1_7[7], ~(flv1), c2_7[4], c2_8[2]);
assign c2_7[5] = c1_7[8];
FA fa4 (c1_8[0], c1_8[1], c1_8[2], c2_8[3], c2_9[0]);
FA fa5 (c1_8[3], c1_8[4], c1_8[5], c2_8[4], c2_9[1]);
FA fa6 (c1_8[6], c1_8[7], c1_8[8], c2_8[5], c2_9[2]);
FA fa7 (c1_9[0], c1_9[1], c1_9[2], c2_9[3], c2_10[0]);
FA fa8 (c1_9[3], c1_9[4], c1_9[5], c2_9[4], c2_10[1]);
FA fa9 (c1_9[6], c1_9[7], c1_9[8], c2_9[5], c2_10[2]);
FA fa10 (c1_10[0], c1_10[1], c1_10[2], c2_10[3], c2_11[0]);
FA fa11 (c1_10[3], c1_10[4], c1_10[5], c2_10[4], c2_11[1]);
HA_gated ha5 (c1_10[6], c1_10[7], 1'b1, c2_10[5], c2_11[2]);
FA fa12 (c1_11[0], c1_11[1], c1_11[2], c2_11[3], c2_12[0]);
HA_gated ha6 (c1_11[3], c1_11[4], 1'b1, c2_11[4], c2_12[1]);
assign c2_11[5] = c1_11[5];
HA_gated ha7 (c1_12[0], c1_12[1], 1'b1, c2_12[2], c2_13[0]);
assign c2_12[3] = c1_12[2];
assign c2_12[4] = c1_12[3];
assign c2_12[5] = c1_12[4];
HA_gated ha8 (c1_13[0], c1_13[1], 1'b1, c2_13[1], c2_14[0]);
assign c2_13[2] = c1_13[2];
assign c2_13[3] = c1_13[3];
assign c2_13[4] = c1_13[4];
assign c2_13[5] = c1_13[5];
assign c2_14[1] = c1_14[0];
assign c2_14[2] = c1_14[1];
assign c2_14[3] = c1_14[2];
assign c2_15[0] = c1_15[0];
assign c2_15[1] = c1_15[1];
assign c2_16[0] = c1_16[0];
assign c2_16[1] = c1_16[1];
assign c2_16[2] = c1_16[2];
assign c2_16[3] = c1_16[3];
assign c2_16[4] = c1_16[4];
assign c2_17[0] = c1_17[0];
assign c2_17[1] = c1_17[1];
assign c2_17[2] = c1_17[2];
assign c2_17[3] = c1_17[3];

/***** Dadda Tree Stage 3 *****/
wire [0:0] c3_0;
wire [1:0] c3_1;
wire [2:0] c3_2;
wire [3:0] c3_3;
wire [3:0] c3_4;
wire [3:0] c3_5;
wire [3:0] c3_6;
wire [3:0] c3_7;
wire [3:0] c3_8;
wire [3:0] c3_9;
wire [3:0] c3_10;
wire [3:0] c3_11;
wire [3:0] c3_12;
wire [3:0] c3_13;
wire [3:0] c3_14;
wire [2:0] c3_15;
wire [3:0] c3_16;
wire [3:0] c3_17;
wire [0:0] c3_18;

assign c3_0[0] = c2_0[0];
assign c3_1[0] = c2_1[0];
assign c3_1[1] = c2_1[1];
assign c3_2[0] = c2_2[0];
assign c3_2[1] = c2_2[1];
assign c3_2[2] = c2_2[2];
FA fa13 (c2_3[0], c2_3[1], c2_3[2], c3_3[0], c3_4[0]);
assign c3_3[1] = c2_3[3];
assign c3_3[2] = c2_3[4];
assign c3_3[3] = c2_3[5];
FA fa14 (c2_4[0], c2_4[1], c2_4[2], c3_4[1], c3_5[0]);
assign c3_4[2] = c2_4[3];
assign c3_4[3] = c2_4[4];
FA fa15 (c2_5[0], c2_5[1], c2_5[2], c3_5[1], c3_6[0]);
HA_gated ha9 (c2_5[3], c2_5[4], 1'b1, c3_5[2], c3_6[1]);
assign c3_5[3] = c2_5[5];
FA fa16 (c2_6[0], c2_6[1], c2_6[2], c3_6[2], c3_7[0]);
FA fa17 (c2_6[3], c2_6[4], c2_6[5], c3_6[3], c3_7[1]);
FA_gated fa18 (c2_7[0], c2_7[1], c2_7[2], ~(flv1), c3_7[2], c3_8[0]);
FA_gated fa19 (c2_7[3], c2_7[4], c2_7[5], ~(flv1), c3_7[3], c3_8[1]);
FA fa20 (c2_8[0], c2_8[1], c2_8[2], c3_8[2], c3_9[0]);
FA fa21 (c2_8[3], c2_8[4], c2_8[5], c3_8[3], c3_9[1]);
FA fa22 (c2_9[0], c2_9[1], c2_9[2], c3_9[2], c3_10[0]);
FA fa23 (c2_9[3], c2_9[4], c2_9[5], c3_9[3], c3_10[1]);
FA fa24 (c2_10[0], c2_10[1], c2_10[2], c3_10[2], c3_11[0]);
FA fa25 (c2_10[3], c2_10[4], c2_10[5], c3_10[3], c3_11[1]);
FA fa26 (c2_11[0], c2_11[1], c2_11[2], c3_11[2], c3_12[0]);
FA fa27 (c2_11[3], c2_11[4], c2_11[5], c3_11[3], c3_12[1]);
FA fa28 (c2_12[0], c2_12[1], c2_12[2], c3_12[2], c3_13[0]);
FA fa29 (c2_12[3], c2_12[4], c2_12[5], c3_12[3], c3_13[1]);
FA fa30 (c2_13[0], c2_13[1], c2_13[2], c3_13[2], c3_14[0]);
FA fa31 (c2_13[3], c2_13[4], c2_13[5], c3_13[3], c3_14[1]);
FA fa32 (c2_14[0], c2_14[1], c2_14[2], c3_14[2], c3_15[0]);
assign c3_14[3] = c2_14[3];
assign c3_15[1] = c2_15[0];
assign c3_15[2] = c2_15[1];
HA_gated ha10 (c2_16[0], c2_16[1], 1'b1, c3_16[0], c3_17[0]);
assign c3_16[1] = c2_16[2];
assign c3_16[2] = c2_16[3];
assign c3_16[3] = c2_16[4];
HA_gated ha11 (c2_17[0], c2_17[1], 1'b1, c3_17[1], c3_18[0]);
assign c3_17[2] = c2_17[2];
assign c3_17[3] = c2_17[3];

/***** Dadda Tree Stage 4 *****/
wire [0:0] c4_0;
wire [1:0] c4_1;
wire [2:0] c4_2;
wire [2:0] c4_3;
wire [2:0] c4_4;
wire [2:0] c4_5;
wire [2:0] c4_6;
wire [2:0] c4_7;
wire [2:0] c4_8;
wire [2:0] c4_9;
wire [2:0] c4_10;
wire [2:0] c4_11;
wire [2:0] c4_12;
wire [2:0] c4_13;
wire [2:0] c4_14;
wire [2:0] c4_15;
wire [2:0] c4_16;
wire [2:0] c4_17;
wire [0:0] c4_18;

assign c4_0[0] = c3_0[0];
assign c4_1[0] = c3_1[0];
assign c4_1[1] = c3_1[1];
assign c4_2[0] = c3_2[0];
assign c4_2[1] = c3_2[1];
assign c4_2[2] = c3_2[2];
HA_gated ha12 (c3_3[0], c3_3[1], 1'b1, c4_3[0], c4_4[0]);
assign c4_3[1] = c3_3[2];
assign c4_3[2] = c3_3[3];
FA fa33 (c3_4[0], c3_4[1], c3_4[2], c4_4[1], c4_5[0]);
assign c4_4[2] = c3_4[3];
FA fa34 (c3_5[0], c3_5[1], c3_5[2], c4_5[1], c4_6[0]);
assign c4_5[2] = c3_5[3];
FA fa35 (c3_6[0], c3_6[1], c3_6[2], c4_6[1], c4_7[0]);
assign c4_6[2] = c3_6[3];
FA_gated fa36 (c3_7[0], c3_7[1], c3_7[2], ~(flv1), c4_7[1], c4_8[0]);
assign c4_7[2] = c3_7[3];
FA fa37 (c3_8[0], c3_8[1], c3_8[2], c4_8[1], c4_9[0]);
assign c4_8[2] = c3_8[3];
FA fa38 (c3_9[0], c3_9[1], c3_9[2], c4_9[1], c4_10[0]);
assign c4_9[2] = c3_9[3];
FA fa39 (c3_10[0], c3_10[1], c3_10[2], c4_10[1], c4_11[0]);
assign c4_10[2] = c3_10[3];
FA fa40 (c3_11[0], c3_11[1], c3_11[2], c4_11[1], c4_12[0]);
assign c4_11[2] = c3_11[3];
FA fa41 (c3_12[0], c3_12[1], c3_12[2], c4_12[1], c4_13[0]);
assign c4_12[2] = c3_12[3];
FA fa42 (c3_13[0], c3_13[1], c3_13[2], c4_13[1], c4_14[0]);
assign c4_13[2] = c3_13[3];
FA fa43 (c3_14[0], c3_14[1], c3_14[2], c4_14[1], c4_15[0]);
assign c4_14[2] = c3_14[3];
HA_gated ha13 (c3_15[0], c3_15[1], 1'b1, c4_15[1], c4_16[0]);
assign c4_15[2] = c3_15[2];
FA fa44 (c3_16[0], c3_16[1], c3_16[2], c4_16[1], c4_17[0]);
assign c4_16[2] = c3_16[3];
FA fa45 (c3_17[0], c3_17[1], c3_17[2], c4_17[1], c4_18[0]);
assign c4_17[2] = c3_17[3];

/***** Dadda Tree Stage 5 *****/
wire [0:0] c5_0;
wire [1:0] c5_1;
wire [1:0] c5_2;
wire [1:0] c5_3;
wire [1:0] c5_4;
wire [1:0] c5_5;
wire [1:0] c5_6;
wire [1:0] c5_7;
wire [1:0] c5_8;
wire [1:0] c5_9;
wire [1:0] c5_10;
wire [1:0] c5_11;
wire [1:0] c5_12;
wire [1:0] c5_13;
wire [1:0] c5_14;
wire [1:0] c5_15;
wire [1:0] c5_16;
wire [1:0] c5_17;
wire [0:0] c5_18;

assign c5_0[0] = c4_0[0];
assign c5_1[0] = c4_1[0];
assign c5_1[1] = c4_1[1];
HA_gated ha14 (c4_2[0], c4_2[1], 1'b1, c5_2[0], c5_3[0]);
assign c5_2[1] = c4_2[2];
FA fa46 (c4_3[0], c4_3[1], c4_3[2], c5_3[1], c5_4[0]);
FA fa47 (c4_4[0], c4_4[1], c4_4[2], c5_4[1], c5_5[0]);
FA fa48 (c4_5[0], c4_5[1], c4_5[2], c5_5[1], c5_6[0]);
FA fa49 (c4_6[0], c4_6[1], c4_6[2], c5_6[1], c5_7[0]);
FA_gated fa50 (c4_7[0], c4_7[1], c4_7[2], ~(flv1), c5_7[1], c5_8[0]);
FA fa51 (c4_8[0], c4_8[1], c4_8[2], c5_8[1], c5_9[0]);
FA fa52 (c4_9[0], c4_9[1], c4_9[2], c5_9[1], c5_10[0]);
FA fa53 (c4_10[0], c4_10[1], c4_10[2], c5_10[1], c5_11[0]);
FA fa54 (c4_11[0], c4_11[1], c4_11[2], c5_11[1], c5_12[0]);
FA fa55 (c4_12[0], c4_12[1], c4_12[2], c5_12[1], c5_13[0]);
FA fa56 (c4_13[0], c4_13[1], c4_13[2], c5_13[1], c5_14[0]);
FA fa57 (c4_14[0], c4_14[1], c4_14[2], c5_14[1], c5_15[0]);
FA fa58 (c4_15[0], c4_15[1], c4_15[2], c5_15[1], c5_16[0]);
FA fa59 (c4_16[0], c4_16[1], c4_16[2], c5_16[1], c5_17[0]);
FA fa60 (c4_17[0], c4_17[1], c4_17[2], c5_17[1], c5_18[0]);

assign sum = {c5_17[0],c5_16[0],c5_15[0],c5_14[0],c5_13[0],c5_12[0],c5_11[0],c5_10[0],c5_9[0],c5_8[0],c5_7[0],c5_6[0],c5_5[0],c5_4[0],c5_3[0],c5_2[0],c5_1[0],c5_0[0]};
assign carry = {c5_17[1],c5_16[1],c5_15[1],c5_14[1],c5_13[1],c5_12[1],c5_11[1],c5_10[1],c5_9[1],c5_8[1],c5_7[1],c5_6[1],c5_5[1],c5_4[1],c5_3[1],c5_2[1],c5_1[1], 1'b0};

endmodule

module multiplier_4x4 (
	input  clk,
	input  [3:0] data_x,
	input  [3:0] data_y,
	input  signed_x,
	input  signed_y,
	output [7:0] sum,
	output [7:0] carry
);

wire [3:0] PP [3:0];
wire [7:0] dadda_sum, dadda_carry;
reg [3:0] x;
reg [3:0] y;
reg sign_x;
reg sign_y;
reg [7:0] s;
reg [7:0] c;

always @ (*)
begin: reg_in_out
	x <= data_x;
	y <= data_y;
	sign_x <= signed_x;
	sign_y <= signed_y;
	s <= dadda_sum;
	c <= dadda_carry;
end

genvar i, j;
generate
for(i = 0; i < 4; i = i + 1)
begin: arrayV
	for(j = 0; j < 4; j = j + 1)
	begin: arrayH
		if((i == 3 && j <  3)) begin
			arrayBlock_signed BLKsx (.A(y[j]), .B(x[i]), .signed_ctrl(sign_x), .mult(PP[i][j]));
		end else if((j == 3 && i <  3)) begin
			arrayBlock_signed BLKsy (.A(y[j]), .B(x[i]), .signed_ctrl(sign_y), .mult(PP[i][j]));
		end else begin
			arrayBlock_unsigned BLKu (.A(y[j]), .B(x[i]), .mult(PP[i][j]));
		end
	end
end
endgenerate

daddaTree_4x4 DT (
	.PP0(PP[0]),
	.PP1(PP[1]),
	.PP2(PP[2]),
	.PP3(PP[3]),
	.sx(sign_x),
	.sy(sign_y),
	.sum(dadda_sum),
	.carry(dadda_carry)
);

assign sum = s;
assign carry = c;
endmodule

module daddaTree_4x4 (
	input  [3:0] PP0,
	input  [3:0] PP1,
	input  [3:0] PP2,
	input  [3:0] PP3,
	input  sx,
	input  sy,
	output [7:0] sum,
	output [7:0] carry
);

/***** Dadda Tree Stage 1 *****/
wire [0:0] c1_0;
wire [1:0] c1_1;
wire [2:0] c1_2;
wire [3:0] c1_3;
wire [3:0] c1_4;
wire [1:0] c1_5;
wire [2:0] c1_6;
wire [1:0] c1_7;

assign c1_0[0] = PP0[0];
assign c1_1[0] = PP0[1];
assign c1_1[1] = PP1[0];
assign c1_2[0] = PP0[2];
assign c1_2[1] = PP1[1];
assign c1_2[2] = PP2[0];
FA fa0 (PP0[3], PP1[2], PP2[1], c1_3[0], c1_4[0]);
assign c1_3[1] = PP3[0];
assign c1_3[2] = sx;
assign c1_3[3] = sy;
assign c1_4[1] = PP1[3];
assign c1_4[2] = PP2[2];
assign c1_4[3] = PP3[1];
assign c1_5[0] = PP2[3];
assign c1_5[1] = PP3[2];
assign c1_6[0] = PP3[3];
assign c1_6[1] = sx;
assign c1_6[2] = sy;
assign c1_7[0] = sx;
assign c1_7[1] = sy;

/***** Dadda Tree Stage 2 *****/
wire [0:0] c2_0;
wire [1:0] c2_1;
wire [2:0] c2_2;
wire [2:0] c2_3;
wire [2:0] c2_4;
wire [2:0] c2_5;
wire [2:0] c2_6;
wire [1:0] c2_7;

assign c2_0[0] = c1_0[0];
assign c2_1[0] = c1_1[0];
assign c2_1[1] = c1_1[1];
assign c2_2[0] = c1_2[0];
assign c2_2[1] = c1_2[1];
assign c2_2[2] = c1_2[2];
HA ha0 (c1_3[0], c1_3[1], c2_3[0], c2_4[0]);
assign c2_3[1] = c1_3[2];
assign c2_3[2] = c1_3[3];
FA fa1 (c1_4[0], c1_4[1], c1_4[2], c2_4[1], c2_5[0]);
assign c2_4[2] = c1_4[3];
assign c2_5[1] = c1_5[0];
assign c2_5[2] = c1_5[1];
assign c2_6[0] = c1_6[0];
assign c2_6[1] = c1_6[1];
assign c2_6[2] = c1_6[2];
assign c2_7[0] = c1_7[0];
assign c2_7[1] = c1_7[1];

/***** Dadda Tree Stage 3 *****/
wire [0:0] c3_0;
wire [1:0] c3_1;
wire [1:0] c3_2;
wire [1:0] c3_3;
wire [1:0] c3_4;
wire [1:0] c3_5;
wire [1:0] c3_6;
wire [1:0] c3_7;
wire [0:0] c3_8;

assign c3_0[0] = c2_0[0];
assign c3_1[0] = c2_1[0];
assign c3_1[1] = c2_1[1];
HA ha1 (c2_2[0], c2_2[1], c3_2[0], c3_3[0]);
assign c3_2[1] = c2_2[2];
FA fa2 (c2_3[0], c2_3[1], c2_3[2], c3_3[1], c3_4[0]);
FA fa3 (c2_4[0], c2_4[1], c2_4[2], c3_4[1], c3_5[0]);
FA fa4 (c2_5[0], c2_5[1], c2_5[2], c3_5[1], c3_6[0]);
FA fa5 (c2_6[0], c2_6[1], c2_6[2], c3_6[1], c3_7[0]);
HA ha2 (c2_7[0], c2_7[1], c3_7[1], c3_8[0]);

assign sum = {c3_7[0],c3_6[0],c3_5[0],c3_4[0],c3_3[0],c3_2[0],c3_1[0],c3_0[0]};
assign carry = {c3_7[1],c3_6[1],c3_5[1],c3_4[1],c3_3[1],c3_2[1],c3_1[1], 1'b0};

endmodule

module arrayBlock_signed_gated (input A, input B, input signed_ctrl, input enable, output mult);
	assign mult = enable & ((A & B) ^ signed_ctrl);
endmodule

module arrayBlock_signed (input A, input B, input signed_ctrl, output mult);
	assign mult = (A & B) ^ signed_ctrl;
endmodule

module arrayBlock_unsigned_gated (input A, input B, input enable, output mult);
	assign mult = enable & A & B;
endmodule

module arrayBlock_unsigned (input A, input B, output mult);
	assign mult = A & B;
endmodule

module HA_gated (input X, input Y, input kill, output S, output Cout);
	assign Cout = kill & X & Y;
	assign S = X ^ Y;
endmodule

module HA (input X, input Y, output S, output Cout);
	assign Cout = X & Y;
	assign S = X ^ Y;
endmodule

module FA_gated (input X, input Y, input Cin, input kill, output S, output Cout);
	assign Cout = kill & ((X & Y) | (X & Cin) | (Y & Cin));
	assign S = X ^ Y ^ Cin;
endmodule

module FA (input X, input Y, input Cin, output S, output Cout);
	assign Cout = (X & Y) | (X & Cin) | (Y & Cin);
	assign S = X ^ Y ^ Cin;
endmodule