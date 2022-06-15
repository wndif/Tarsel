vlib work
vmap work work
vlog -sv tate_pairing_kgoliya_buggy1.v +cover=sbcet -coveropt 1
vlog -sv f3.v
vlog -sv f3m.v 
vlog -sv f32m.v 
vlog -sv f33m.v
vlog -sv f36m.v
vlog -sv fun.v 
vlog -sv test_duursma_lee_algo_t1.v

vsim -coverage test_duursma_lee_algo
run -all
coverage report -output report.txt -srcfile=tate_pairing_kgoliya_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}

quit -sim