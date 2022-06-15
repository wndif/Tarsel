vlib work
vmap work work
vlog sdram_controller_kgoliya_buggy2.v +cover=sbcet -coveropt 1
vlog sdram_controller_tb_t1.v +cover=sbcet -coveropt 1
vsim -coverage sdram_controller_tb
run 467ns
coverage clear
run 2ns 
coverage report -output report/v0/report469.txt -srcfile=sdram_controller_kgoliya_buggy2.v -detail -annotate -assert -directive -cvg -code {s b c e t}
quit -sim
quit -f