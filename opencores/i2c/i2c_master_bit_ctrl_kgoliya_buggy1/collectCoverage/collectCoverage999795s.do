vlib work
vmap work work
vlog i2c_master_bit_ctrl_kgoliya_buggy1.v +cover=sbcet -coveropt 1
vlog i2c_master_top.v +cover=sbcet -coveropt 1
vlog wb_master_model.v +cover=sbcet -coveropt 1
vlog i2c_slave_model.v +cover=sbcet -coveropt 1
vlog i2c_master_byte_ctrl.v +cover=sbcet -coveropt 1
vlog -sv tst_bench_top_t1.v +cover=sbcet -coveropt 1
vsim -coverage tst_bench_top
run 999785ns
coverage clear
run 10ns 
coverage report -output report/v0/report999795.txt -srcfile=i2c_master_bit_ctrl_kgoliya_buggy1.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f