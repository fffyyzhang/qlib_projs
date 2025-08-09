#!/usr/bin/env python3
"""
ETF均线偏离度分析研究
分析所有关键ETF的均线偏离数据，找出每日偏离度最大的标的
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


def load_etf_selection():
    """加载ETF筛选列表"""
    #select_file = "/data/data_liy/quant/etf/etf_human_select.csv"
    select_file = os.path.join(DIR_DATA, "../research/etf_human_select.csv")
    df = pd.read_csv(select_file)
    selected_df = df[df['human'] == 1][['ts_code', 'extname']].copy()
    selected_etfs = selected_df['ts_code'].tolist()
    # 创建代码到名称的映射字典
    etf_name_map = dict(zip(selected_df['ts_code'], selected_df['extname']))
    print(f"选中的ETF数量: {len(selected_etfs)}")
    return selected_etfs, etf_name_map

def load_etf_data(etf_codes):
    """加载ETF历史数据"""
    data_dir = os.path.join(DIR_DATA, "etf_daily")
    all_data = []
    
    for etf_code in etf_codes:
        file_path = f"{data_dir}/{etf_code}.csv"
        if Path(file_path).exists():
            try:
                df = pd.read_csv(file_path)
                df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
                df = df[['ts_code', 'trade_date', 'close']].copy()
                all_data.append(df)
                print(f"加载 {etf_code}: {len(df)} 条记录")
            except Exception as e:
                print(f"加载 {etf_code} 失败: {e}")
        else:
            print(f"文件不存在: {file_path}")
    
    # 合并所有数据
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values(['ts_code', 'trade_date'])
        print(f"总数据量: {len(combined_df)} 条")
        return combined_df
    else:
        return pd.DataFrame()

def calculate_ma_bias(df):
    """计算均线偏离度指标"""
    print("计算均线偏离度指标...")
    
    # 按ETF代码分组计算移动平均
    periods = [5, 10, 20, 30, 60, 120, 200]
    
    for period in periods:
        ma_col = f'ma_{period}'
        bias_col = f'ma_bias_{period}'
        
        # 计算移动平均
        df[ma_col] = df.groupby('ts_code')['close'].transform(
            lambda x: x.rolling(window=period, min_periods=period).mean()
        )
        
        # 计算偏离度 (修正需求文档中的错误，应该是close/对应的ma)
        df[bias_col] = df['close'] / df[ma_col]
        
        print(f"完成 {bias_col} 计算")
    
    # 删除中间计算列
    ma_cols = [f'ma_{p}' for p in periods]
    df = df.drop(columns=ma_cols)
    
    return df

def analyze_daily_max_bias(df, etf_name_map):
    """分析每日偏离度最大的标的"""
    print("分析每日偏离度最大的标的...")
    
    bias_cols = ['ma_bias_5', 'ma_bias_10', 'ma_bias_20', 'ma_bias_30', 'ma_bias_60', 'ma_bias_120']
    
    # 只保留有完整指标的数据
    df_clean = df.dropna(subset=bias_cols).copy()
    print(f"有效数据量: {len(df_clean)}")
    
    # 使用vectorized操作提高效率
    daily_max = []
    
    # 按日期分组并使用idxmax()
    grouped = df_clean.groupby('trade_date')
    total_dates = len(grouped)
    
    for i, (date, group) in enumerate(grouped):
        if i % 100 == 0:  # 每100天显示一次进度
            print(f"处理进度: {i}/{total_dates} ({i/total_dates*100:.1f}%)")
            
        row = {'trade_date': date}
        
        for bias_col in bias_cols:
            # 使用idxmax直接找到最大值的索引
            max_idx = group[bias_col].idxmax()
            etf_code = group.loc[max_idx, 'ts_code']
            
            # 使用ETF名称替代代码
            etf_name = etf_name_map.get(etf_code, etf_code)  # 如果找不到名称则保留代码
            
            row[f'{bias_col}_max_etf'] = etf_name
            row[f'{bias_col}_max_value'] = group.loc[max_idx, bias_col]
        
        daily_max.append(row)
    
    result_df = pd.DataFrame(daily_max)
    result_df = result_df.sort_values('trade_date')
    
    print(f"日级别分析结果: {len(result_df)} 个交易日")
    return result_df

def save_results(df):
    """保存分析结果"""
    output_file = os.path.join(DIR_DATA, "../research/etf_ma_bias_research.csv")
    
    # 确保目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # 保存结果
    df.to_csv(output_file, index=False)
    print(f"结果已保存到: {output_file}")
    
    # 显示统计信息
    print(f"\n=== 分析结果统计 ===")
    print(f"分析期间: {df['trade_date'].min()} 到 {df['trade_date'].max()}")
    print(f"交易日数量: {len(df)}")
    
    # 统计各ETF在不同指标上的表现
    bias_periods = [5, 10, 20, 30, 60, 120]
    for period in bias_periods:
        col = f'ma_bias_{period}_max_etf'
        if col in df.columns:
            top_etfs = df[col].value_counts().head(5)
            print(f"\nMA{period}偏离度最大ETF TOP5:")
            for etf_name, count in top_etfs.items():
                print(f"  {etf_name}: {count}次")

def main():
    """主函数"""
    print("=== ETF均线偏离度分析研究 ===")
    
    # 1. 加载ETF筛选列表
    etf_codes, etf_name_map = load_etf_selection()
    if not etf_codes:
        print("❌ 没有找到需要分析的ETF")
        return
    
    # 2. 加载ETF数据
    df = load_etf_data(etf_codes)
    if df.empty:
        print("❌ 没有加载到ETF数据")
        return
    
    # 3. 计算均线偏离度
    df = calculate_ma_bias(df)
    
    # 4. 分析每日最大偏离度
    daily_result = analyze_daily_max_bias(df, etf_name_map)
    
    # 5. 保存结果
    save_results(daily_result)
    
    print("✅ 分析完成!")

if __name__ == "__main__":
    main()
