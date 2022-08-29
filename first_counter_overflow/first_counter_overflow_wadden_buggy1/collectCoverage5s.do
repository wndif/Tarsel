vlib work
vmap work work
vlog first_counter_overflow_wadden_buggy1.v +cover=sbcet -coveropt 1
vlog first_counter_tb_t3.v +cover=sbcet -coveropt 1

vsim -coverage first_counter_tb

run 5ns

coverage report -output report5.txt -srcfile=first_counter_overflow_wadden_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f