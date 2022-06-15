vlib work
vmap work work
vlog mux_4_1_kgoliya_buggy1.v +cover=sbcet -coveropt 1
vlog mux_4_1_tb.v +cover=sbcet -coveropt 1

vsim -coverage tb_4to1_mux

run -all

coverage report -output report.txt -srcfile=mux_4_1_kgoliya_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}

quit -sim