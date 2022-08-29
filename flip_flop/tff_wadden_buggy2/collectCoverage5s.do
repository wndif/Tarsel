vlib work
vmap work work
vlog tff_wadden_buggy2.v +cover=sbcet -coveropt 1
vlog -sv tff_tb.v +cover=sbcet -coveropt 1

vsim -coverage tb

run 5ns

coverage report -output report/v0/report5.txt -srcfile=tff_wadden_buggy2.v -detail -annotate -assert -directive -cvg -code {s b c e t}

quit -sim
quit -f