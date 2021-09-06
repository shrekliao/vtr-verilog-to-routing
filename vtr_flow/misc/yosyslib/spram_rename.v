`timescale 1ps/1ps

// depth and data may need to be splited
module singlePortRam(clk, we, addr, data, out);

    parameter ADDR_WIDTH = 1;
    parameter DATA_WIDTH = 1;

    input clk;
    input we;
    input [ADDR_WIDTH - 1:0] addr;
    input [DATA_WIDTH - 1:0] data;
    
    output reg [DATA_WIDTH - 1:0] out;    

	single_port_ram uut (
                    .clk(clk), 
                    .we(we), 
                    .addr(addr), 
                    .data(data), 
                    .out(out)
                );

endmodule

(* blackbox *)
module single_port_ram(clk, data, addr, we, out);

    localparam ADDR_WIDTH = `MEM_MAXADDR;
    localparam DATA_WIDTH = 1;

    input clk;
    input we;
    input [ADDR_WIDTH-1:0] addr;
    input [DATA_WIDTH-1:0] data;
    
    output reg [DATA_WIDTH-1:0] out;
    /*
    reg [DATA_WIDTH-1:0] RAM [(1<<ADDR_WIDTH)-1:0];

    always @(posedge clk)
    begin
        if (we)
                RAM[addr] <= data;
                
        out <= RAM[addr];
    end
    */
endmodule
