// updown_counter: 8-bit up/down counter with parallel load and enable
//
// BUGGY VERSION used by the Tarsel2 example.
// Single injected fault on line 20: the parallel load stores data_in + 1
// instead of data_in. Everything else matches the reference version.
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
            count <= data_in + 8'd1;   // FAULT: should be `count <= data_in;`
        end else if (en) begin
            if (up) begin
                count <= count + 8'd1;
            end else begin
                count <= count - 8'd1;
            end
        end
    end

endmodule
