module adder_10bits(
    input [4:0] a,    // 5-bit input a
    input [4:0] b,    // 5-bit input b
    output [4:0] sum, // 5-bit output sum
    output carry_out  // Carry out
);

    // Internal variable for full 6-bit addition to capture the carry
    wire [3:0] full_sum;

    assign full_sum = a + b;   // Perform 6-bit addition
    assign sum = full_sum[4:0]; // Assign the lower 5 bits to sum
    assign carry_out = full_sum[5]; // The 6th bit is the carry out

endmodule