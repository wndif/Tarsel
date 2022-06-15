/*
    Copyright 2011, City University of Hong Kong
    Author is Homer (Dongsheng) Hsing.
 
    This file is part of Tate Bilinear Pairing Core.
 
    Tate Bilinear Pairing Core is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
 
    Tate Bilinear Pairing Core is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.
 
    You should have received a copy of the GNU Lesser General Public License
    along with Tate Bilinear Pairing Core.  If not, see http://www.gnu.org/licenses/lgpl.txt
*/
 
// fun.v: Have you got fun reading the code ?
 // PX is the irreducible polynomial
// turn "00000001111111111111111" into "00000001000000000000000"
module func6(clk, reset, in, out);
    `define MOST 2*`M+1:2*`M
    `define M     97          // M is the degree of the irreducible polynomial
    `define WIDTH (2*`M-1)    // width for a GF(3^M) element
    `define W2    (4*`M-1)    // width for a GF(3^{2*M}) element
    `define W3    (6*`M-1)    // width for a GF(3^{3*M}) element
    `define W6    (12*`M-1)   // width for a GF(3^{6*M}) element
    `define PX    196'h4000000000000000000000000000000000000000001000002 
    input clk, reset, in;
    output out;
    reg reg1, reg2;
    always @ (posedge clk)
        if (reset)
          begin
            reg1 <= 0; reg2 <= 0;
          end
        else
          begin
            reg2 <= reg1; reg1 <= in;
          end
    assign out = {reg2,reg1}==2'b01 ? 1 : 0;
endmodule