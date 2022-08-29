vlib work
vmap work work
vlog out_stage_ssscrazy_buggy1.v +cover=sbcet -coveropt 1
vlog RS_dec.v
vlog BM_lamda.v
vlog GF_matrix_dec.v
vlog GF_matrix_ascending_binary.v
vlog input_syndromes.v
vlog lamda_roots.v
vlog transport_in2out.v
vlog DP_RAM.v
vlog BM_lamda.v
vlog error_correction.v
vlog Omega_Phy.v
vlog GF_mult_add_syndromes.v
vlog -sv RS_dec_tb_t1.v
vsim -coverage RS_dec_tb

run 1ns 
coverage report -output report/v0/report79905.txt -srcfile=out_stage_ssscrazy_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f