vlib work
vmap work work
vlog padder_ssscrazy_buggy1.v +cover=sbcet -coveropt 1
vlog keccak.v
vlog f_permutation.v
vlog padder1.v
vlog rconst.v
vlog round.v
vlog test_padder_t1.v
vsim -coverage test_padder
run 10ns 
coverage report -output report/v0/report10.txt -srcfile=padder_ssscrazy_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f