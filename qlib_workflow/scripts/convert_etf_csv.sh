#!/bin/bash
cd /Users/liyuan/dev/proj_liy/qlib/scripts

python dump_bin.py dump_all \
--csv_path  ~/data/quant/raw/etf_daily \
--qlib_dir ~/data/qlib_data/etf_data \
-d trade_date \
--symbol_field_name ts_code \
--include_fields open,close,high,low,volume \
--max_workers 8 


#python dump_bin.py dump_all --csv_path ~/data/quant/raw/etf_daily --qlib_dir ~/data/qlib_data/etf_data_test -d trade_date --symbol_field_name ts_code --include_fields open,close,high,low,volume --limit_nums 3