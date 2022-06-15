vlib work
vmap work work
vlog keccak_wadden_buggy1.v +cover=sbcet -coveropt 1
vlog padder.v
vlog f_permutation.v
vlog padder1.v
vlog rconst.v
vlog round.v
vlog test_keccak_t1.v
vsim -coverage test_keccak
run 290ns
coverage clear
run 20ns 
coverage report -output report/v0/report310.txt -srcfile=keccak_wadden_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f