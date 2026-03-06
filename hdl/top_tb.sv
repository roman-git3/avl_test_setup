`timescale 1ns/1ps

module top_tb;

initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, u_simple_adder); // 'simple_adder' is your top module name
end

logic [7:0] a;
logic [7:0] b;
logic [8:0] sum;

simple_adder u_simple_adder (
    .a(a), // Example input
    .b(b), // Example input
    .sum(sum)     // Output will be observed in the testbench
);

endmodule