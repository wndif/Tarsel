vlib work
vmap work work
vlog lshift_reg_wadden_buggy2.v +cover=sbcet -coveropt 1
vlog lshift_reg_tb_t1.v +cover=sbcet -coveropt 1

vsim -coverage tb

run 180ns
coverage clear
run 10ns

coverage report -output report/v0/report190.txt -srcfile=lshift_reg_wadden_buggy2.v -detail -annotate -assert -directive -cvg -code {s b c e t}

quit -sim
quit -f