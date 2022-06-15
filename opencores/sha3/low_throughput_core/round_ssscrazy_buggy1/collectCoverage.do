vlib work
vmap work work
vlog round_ssscrazy_buggy1.v +cover=sbcet -coveropt 1
vlog keccak.v
vlog f_permutation.v
vlog padder1.v
vlog padder.v
vlog rconst.v
vlog round.v
vlog test_keccak_t1.v

vsim -coverage test_keccak

run -all

coverage report -output report.txt -srcfile=round_ssscrazy_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}
