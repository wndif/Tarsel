vlib work
vmap work work
vlog mux_4_1_wadden_buggy1.v +cover=sbcet -coveropt 1
vlog mux_4_1_tb.v +cover=sbcet -coveropt 1
vsim -coverage tb_4to1_mux
run 635ns
coverage clear
run 10ns 
coverage report -output report/v0/report645.txt -srcfile=mux_4_1_wadden_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f