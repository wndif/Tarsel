vlib work
vmap work work
vlog i2c_slave_model_wadden_buggy2.v +cover=sbcet -coveropt 1
vlog i2c_master_bit_ctrl.v
vlog i2c_master_top.v 
vlog wb_master_model.v 
vlog i2c_master_byte_ctrl.v 
vlog tst_bench_top_t1.v
vsim -coverage tst_bench_top
run 113145ns
coverage clear
run 10ns 
coverage report -output report/v0/report113155.txt -srcfile=i2c_slave_model_wadden_buggy2.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f