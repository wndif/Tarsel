vlib work
vmap work work
vlog mux_4_1_wadden_buggy2.v +cover=sbcet -coveropt 1
vlog mux_4_1_tb.v +cover=sbcet -coveropt 1
vsim -coverage tb_4to1_mux
run 5ns 
coverage report -output report/v0/report5.txt -srcfile=mux_4_1_wadden_buggy2.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f