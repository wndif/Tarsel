`timescale 1ns / 100ps
/**********************************************************************
 * Date: Aug. 28, 1999
 * File: Test Decoder 3 to 8.v   (440 Examples)
 *
 * Testbench to generate some stimulus and display the results for the
 * 3-to-8 decoder module.
 **********************************************************************/
//*********************************************************
  module tb_decoder_3to8;
//*********************************************************  
     wire  Y7, Y6, Y5, Y4, Y3, Y2, Y1, Y0;
     reg   A, B, C;
     reg   en;
     reg   clk, instrumented_clk;
     reg   [7:0]count[18:0];
     integer i;
     // Instantiate the Decoder (named DUT {device under test})
     decoder_3to8  DUT(Y7,Y6,Y5,Y4,Y3,Y2,Y1,Y0, A, B, C, en);
  
     integer f;
     initial  begin
        count[0] = 1; 
        count[1] = 3; 
        count[2] = 5; 
        count[3] = 7; 
        count[4] = 9; 
        count[5] = 11; 
        count[6] = 13; 
        count[7] = 15; 
        count[8] = 17; 
        count[9] = 19; 
        count[10] = 21; 
        count[11] = 23; 
        count[12] = 25; 
        count[13] = 27; 
        count[14] = 29; 
        count[15] = 31; 
        count[16] = 33; 
        count[17] = 35; 
        count[18] = 37; 
        count[19] = 39; 
        count[20] = 41; 
        count[21] = 43; 
        count[22] = 45; 
        count[23] = 47; 
        count[24] = 49; 
        count[25] = 51; 
        count[26] = 53; 
        clk = 0;
        instrumented_clk = 0;
        f = $fopen("output_decoder_3_to_8_tb_t1.txt");
        $fwrite(f, "time,Y7,Y6,Y5,Y4,Y3,Y2,Y1,Y0\n");
        $timeformat(-9, 1, " ns", 6); #1;
        A  = 1'b0;       // time = 0
        B  = 1'b0;
        C  = 1'b0;
        en = 1'b0;
        #9;
        en = 1'b1;      // time = 10
        #10;
        A  = 1'b0;
        B  = 1'b1; 
        C  = 1'b0;      // time = 20
        #10;
        A  = 1'b1;
        B  = 1'b0;      
        C  = 1'b0;      // time = 30
        #10;
        A  = 1'b1;
        B  = 1'b1;
        C  = 1'b0;      // time = 40
        #5;
        en = 1'b0;      // time = 45
        #10;
        $fclose(f);
	$finish;
    end
    
    

    //initial begin
       // #count[i];
       // $finish;
    //end

    //  always @(A or B or C or en)
    always @(posedge clk)
     $fwrite(f, "%g,%b,%b,%b,%b,%b,%b,%b,%b\n", $time,Y7,Y6,Y5,Y4,Y3,Y2,Y1,Y0);

    always @(A or B or C or en)  
     $monitor("t=%t en=%b ABC=%b%b%b Y=%b%b%b%b%b%b%b%b",
$time,en,A,B,C,Y7,Y6,Y5,Y4,Y3,Y2,Y1,Y0);

    always #1 clk = ~clk;
    always #1 instrumented_clk = ~instrumented_clk;
    
  endmodule
