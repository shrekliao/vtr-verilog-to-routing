module adder_10bits(
    input [9:0] a,    // 10-bit input a
    input [9:0] b,    // 10-bit input b
    output [9:0] sum, // 10-bit output sum
    output carry_out  // Carry out
);

    // Internal variable for full 11-bit addition to capture the carry
    wire [10:0] full_sum;

    assign full_sum = a + b;   // Perform 11-bit addition
    assign sum = full_sum[9:0]; // Assign the lower 10 bits to sum
    assign carry_out = full_sum[10]; // The 11th bit is the carry out

endmodule