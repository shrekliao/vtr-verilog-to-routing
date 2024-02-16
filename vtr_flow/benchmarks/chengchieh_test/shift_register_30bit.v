module shift_register_10bit(
    input clk,            // Clock input
    input reset,          // Reset input
    input [29:0] data_in,  // 30-bit input data
    input load,           // Load input to load data
    output reg [29:0] data_out // 10-bit shifted output data
);

    // On rising edge of clock or high reset
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            // Reset the shift register to all zeros
            data_out <= 30'b0;
        end
        else if (load) begin
            // Load the input data into the register
            data_out <= data_in;
        end
        else begin
            // Shift right on each clock cycle
            data_out <= data_out >> 1;
        end
    end

endmodule