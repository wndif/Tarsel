vlib work
vmap work work
vlog BM_lamda_ssscrazy_buggy1.v +cover=sbcet -coveropt 1
vlog RS_dec.v +cover=sbcet -coveropt 1
vlog GF_matrix_dec.v +cover=sbcet -coveropt 1
vlog GF_matrix_ascending_binary.v +cover=sbcet -coveropt 1
vlog input_syndromes.v +cover=sbcet -coveropt 1
vlog lamda_roots.v +cover=sbcet -coveropt 1
vlog transport_in2out.v +cover=sbcet -coveropt 1
vlog DP_RAM.v +cover=sbcet -coveropt 1
vlog out_stage.v +cover=sbcet -coveropt 1
vlog error_correction.v +cover=sbcet -coveropt 1
vlog Omega_Phy.v +cover=sbcet -coveropt 1
vlog GF_mult_add_syndromes.v +cover=sbcet -coveropt 1
vlog -sv RS_dec_tb_t1.v +cover=sbcet -coveropt 1
vsim -coverage RS_dec_tb
run 32975ns
coverage clear
run 10ns 
coverage report -output report/v0/report32985.txt -srcfile=BM_lamda_ssscrazy_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f