vlib work
vmap work work
vlog fsm_full_ssscrazy_buggy1.v +cover=sbcet -coveropt 1
vlog -sv fsm_full_tb_t1.v +cover=sbcet -coveropt 1

vsim -coverage fsm_full_tb

run 4ns

coverage report -output report/v0/report4.txt -srcfile=fsm_full_ssscrazy_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}

quit -sim
quit -f