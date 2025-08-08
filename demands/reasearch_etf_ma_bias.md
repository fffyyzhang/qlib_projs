分析我的所有etf文件的均线偏离数据

# 确定列表
首先读取一个过滤列表，
/data/data_liy/quant/etf/etf_human_select.csv
选取这个文件中所有human=1的行的ts_code，作为需要分析的关键etf的代码列表

# 读取全量数据
我的etf文件在/data/data_liy/quant/raw/etf_daily 文件夹中，文件夹中每个csv文件是一个etf的日线历史数据，文件的标题是ts_code即etf文件的代码，

每个文件的格式是这样的
ts_code,trade_date,pre_close,open,high,low,close,change,pct_chg,volume,amount,stock_name
560650.SH,20250718,0.871,0.88,0.88,0.873,0.879,0.008,0.9185,4518.0,396.475,核心50ETF
560650.SH,20250717,0.862,0.864,0.871,0.864,0.871,0.009,1.0441,4283.0,371.472,核心50ETF

遍历这个文件夹，只读取关键etf的数据，把这些数据合并到一个pandas dataframe中，形成完整数据dataframe
只分析close数据

# 数据分析
## 指标计算
在完整数据dataframe中，对于每个ts_code，构建如下特征分析
1 . ma_bias_5：即close/ma_5, 即当前收盘价与历史5日收盘价均线的比例
2. ma_bias_10：即close/ma_5, 即当前收盘价与历史10日收盘价均线的比例
3. ma_bias_20：即close/ma_5, 即当前收盘价与历史20日收盘价均线的比例
4. ma_bias_30：即close/ma_5, 即当前收盘价与历史30日收盘价均线的比例
4. ma_bias_60：即close/ma_5, 即当前收盘价与历史60日收盘价均线的比例
4. ma_bias_120：即close/ma_5, 即当前收盘价与历史120日收盘价均线的比例

## 合并分析
完成所有指标计算后，对于每个交易日，所有ts_code中ma_bias_5 、ma_bias_10....ma_bias_120 数值最大的标的
形成日级别分析后，把这个数据写入/data/data_liy/quant/research/etf_ma_bias_research.csv文件中


