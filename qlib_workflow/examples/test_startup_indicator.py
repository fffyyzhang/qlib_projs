"""
测试ETF价格突然启动检测指标
"""

import qlib
from qlib.data import D
import pandas as pd
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from indicators.price_startup_indicator import PriceStartupIndicator, create_startup_fields


def test_single_etf():
    """测试单个ETF的启动信号"""
    print("=== 测试单个ETF启动信号检测 ===")
    
    # 初始化qlib (请根据实际路径调整)
    qlib.init(provider_uri='/data/data_liy/qlib/etf_data')
    
    # 创建指标实例
    indicator = PriceStartupIndicator()
    
    # 测试ETF
    instruments = ['159302.SZ']  # 创业板指数ETF
    start_time = '2023-01-01'
    end_time = '2024-12-31'
    
    print(f"分析标的: {instruments[0]}")
    print(f"时间范围: {start_time} 到 {end_time}")
    
    try:
        # 获取启动信号数据
        data = indicator.analyze_etf_startup(instruments, start_time, end_time)
        
        print(f"\n数据形状: {data.shape}")
        print(f"列名: {list(data.columns)}")
        
        # 显示前几行数据
        print("\n前5行数据:")
        print(data.head())
        
        # 获取启动信号汇总
        summary = indicator.get_startup_summary(data)
        
        print(f"\n=== 启动信号统计 ===")
        print(f"总交易日数: {summary['total_days']}")
        print(f"启动信号日数: {summary['startup_days']}")
        print(f"启动信号比例: {summary['startup_ratio']:.2%}")
        print(f"平均启动强度: {summary.get('avg_startup_strength', 0):.2f}")
        print(f"最高启动强度: {summary.get('max_startup_strength', 0):.0f}")
        
        # 各子信号统计
        if 'volume_surge_rate' in summary:
            print(f"\n=== 子信号统计 ===")
            print(f"成交量放大信号出现率: {summary['volume_surge_rate']:.2%}")
            print(f"价格动量信号出现率: {summary['momentum_rate']:.2%}")
            print(f"阻力突破信号出现率: {summary['breakout_rate']:.2%}")
            print(f"波动率扩张信号出现率: {summary['volatility_rate']:.2%}")
            print(f"价格趋势信号出现率: {summary['trend_rate']:.2%}")
        
        # 显示最近的启动信号日期
        startup_dates = data[data['startup_signal'] == 1].index.get_level_values(1)
        if len(startup_dates) > 0:
            print(f"\n=== 最近5次启动信号日期 ===")
            for date in startup_dates[-5:]:
                strength = data.loc[(instruments[0], date), 'startup_strength']
                close_price = data.loc[(instruments[0], date), 'close']
                print(f"{date.strftime('%Y-%m-%d')}: 强度={strength:.0f}, 收盘价={close_price:.2f}")
        
        return data
        
    except Exception as e:
        print(f"错误: {e}")
        return None


def test_multiple_etfs():
    """测试多个ETF的启动信号"""
    print("\n=== 测试多个ETF启动信号对比 ===")
    
    # 测试多个ETF
    etf_list = ['159302.SZ', '159919.SZ', '512690.SH']  # 创业板指数、科创50、白酒ETF
    etf_names = ['创业板指数ETF', '科创50ETF', '白酒ETF']
    
    start_time = '2024-01-01'
    end_time = '2024-12-31'
    
    indicator = PriceStartupIndicator()
    results = {}
    
    for etf_code, etf_name in zip(etf_list, etf_names):
        try:
            data = indicator.analyze_etf_startup([etf_code], start_time, end_time)
            summary = indicator.get_startup_summary(data)
            results[etf_name] = summary
            
            print(f"\n{etf_name} ({etf_code}):")
            print(f"  启动信号比例: {summary['startup_ratio']:.2%}")
            print(f"  平均启动强度: {summary.get('avg_startup_strength', 0):.2f}")
            
        except Exception as e:
            print(f"{etf_name} 分析失败: {e}")
    
    return results


def show_startup_fields():
    """显示可用的启动信号字段"""
    print("\n=== 可用的qlib字段表达式 ===")
    
    fields = create_startup_fields()
    
    print("\n基础数据字段:")
    basic_fields = ['close', 'open', 'high', 'low', 'volume']
    for field in basic_fields:
        if field in fields:
            print(f"  {field}: {fields[field]}")
    
    print("\n技术指标字段:")
    tech_fields = ['volume_ma20', 'price_ma10', 'price_return', 'volume_ratio', 'resistance_level']
    for field in tech_fields:
        if field in fields:
            print(f"  {field}: {fields[field]}")
    
    print("\n启动信号字段:")
    signal_fields = ['volume_surge', 'price_momentum', 'resistance_breakout', 
                    'volatility_expansion', 'price_trend']
    for field in signal_fields:
        if field in fields:
            print(f"  {field}: {fields[field]}")
    
    print("\n综合信号字段:")
    final_fields = ['startup_signal', 'startup_strength']
    for field in final_fields:
        if field in fields:
            print(f"  {field}: {fields[field]}")


def demo_manual_query():
    """演示手动查询启动信号"""
    print("\n=== 手动查询启动信号演示 ===")
    
    # 创建指标实例
    indicator = PriceStartupIndicator()
    
    # 构建查询字段
    fields = [
        '$close',
        '$volume', 
        indicator.get_volume_surge_signal().strip(),
        indicator.get_comprehensive_startup_signal().strip(),
        indicator.get_startup_strength_score().strip()
    ]
    
    print("查询字段:")
    for i, field in enumerate(fields):
        print(f"  {i+1}. {field}")
    
    # 执行查询
    try:
        data = D.features(
            instruments=['159302.SZ'],
            fields=fields,
            start_time='2024-01-01',
            end_time='2024-12-31'
        )
        
        print(f"\n查询结果形状: {data.shape}")
        print("最近5行数据:")
        print(data.tail())
        
    except Exception as e:
        print(f"查询失败: {e}")


if __name__ == "__main__":
    print("ETF价格突然启动检测指标测试")
    print("=" * 60)
    
    # 显示可用字段
    show_startup_fields()
    
    # 演示手动查询
    demo_manual_query()
    
    # 测试单个ETF
    test_single_etf()
    
    # 测试多个ETF对比
    test_multiple_etfs()
    
    print("\n测试完成!")