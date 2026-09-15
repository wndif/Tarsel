// updown_counter: 8-bit up/down counter with parallel load and enable
//
// REFERENCE (correct) version, used only to produce golden_output.txt.
// The example's faulty version is updown_counter_buggy.v, which differs
// from this file on line 20 only.
module updown_counter (
    input  wire        clk,
    input  wire        rst,
    input  wire        en,
    input  wire        up,      // 1=up, 0=down
    input  wire        load,
    input  wire [7:0]  data_in,
    output reg  [7:0]  count
);

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            count <= 8'd0;
        end else if (load) begin
            count <= data_in;
        end else if (en) begin
            if (up) begin
                count <= count + 8'd1;
            end else begin
                count <= count - 8'd1;
            end
        end
    end

endmodule
