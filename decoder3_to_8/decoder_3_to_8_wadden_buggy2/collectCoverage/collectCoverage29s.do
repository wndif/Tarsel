vlib work
vmap work work
vlog decoder_3_to_8_wadden_buggy2.v +cover=sbcet -coveropt 1
vlog decoder_3_to_8_tb.v +cover=sbcet -coveropt 1

vsim -coverage tb_decoder_3to8

run 27ns
coverage clear
run 2ns

coverage report -output report/report29.txt -srcfile=decoder_3_to_8_wadden_buggy2.v -detail -annotate -assert -directive -cvg -code {s b c e t}

quit -sim
quit -f