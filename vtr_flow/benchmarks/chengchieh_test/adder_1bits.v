module adder_10bits(
    input a,    // 5-bit input a
    input b,    // 5-bit input b
    output sum, // 5-bit output sum
    output carry_out  // Carry out
);

    // Internal variable for full 6-bit addition to capture the carry
    wire [1:0] full_sum;

    assign full_sum = a + b;   // Perform 6-bit addition
    assign sum = full_sum[0]; // Assign the lower 5 bits to sum
    assign carry_out = full_sum[1]; // The 6th bit is the carry out

endmodule