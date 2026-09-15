`timescale 1ns/1ps
// Value-dump testbench for updown_counter.
//
// Tarsel2 requires a value-dump testbench: it writes one CSV row per sample
// period (header "time,<signals>") and never aborts on mismatch. The dump is
// compared row by row against golden_output.txt, and the divergence timeline
// is what drives the time-window slicing.
module updown_counter_tb;
    reg clk = 0;
    reg rst = 1;
    reg en  = 0;
    reg up  = 1;
    reg load = 0;
    reg [7:0] data_in = 0;
    wire [7:0] count;
    integer output_file;

    updown_counter dut(.clk(clk), .rst(rst), .en(en), .up(up),
                        .load(load), .data_in(data_in), .count(count));

    always #5 clk = ~clk;

    initial begin
        output_file = $fopen("output.txt", "w");
        $fwrite(output_file, "time,count\n");
        #12 rst = 0; en = 1; up = 1;        // start counting up
        repeat (6) begin #10; $fwrite(output_file, "%0t,%0d\n", $time, count); end
        up = 0;                              // switch to count down
        repeat (4) begin #10; $fwrite(output_file, "%0t,%0d\n", $time, count); end
        load = 1; data_in = 8'd200;         // parallel load
        #10; $fwrite(output_file, "%0t,%0d\n", $time, count);
        load = 0;
        repeat (2) begin #10; $fwrite(output_file, "%0t,%0d\n", $time, count); end
        $fclose(output_file);
        $finish;
    end
endmodule
