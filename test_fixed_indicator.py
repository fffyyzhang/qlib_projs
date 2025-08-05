#!/usr/bin/env python3
"""
测试修复后的ETF启动指标
"""

import sys
import os
sys.path.append('qlib_workflow')

try:
    import qlib
    from qlib.data import D
    from indicators.price_startup_indicator import PriceStartupIndicator, create_startup_fields
    
    print("✅ 导入模块成功")
    
    # 初始化qlib
    qlib.init(provider_uri='/data/data_liy/qlib/etf_data')
    print("✅ qlib初始化成功")
    
    # 创建指标实例
    indicator = PriceStartupIndicator()
    print("✅ 指标实例创建成功")
    
    # 测试各个子信号表达式
    print("\n=== 测试各个信号表达式 ===")
    signals = indicator.get_all_signals()
    
    for name, expr in signals.items():
        print(f"{name}: {expr}")
    
    # 测试字段创建
    print("\n=== 测试字段创建 ===")
    fields = create_startup_fields()
    print(f"创建了 {len(fields)} 个字段")
    
    # 测试简单查询
    print("\n=== 测试简单查询 ===")
    test_fields = [
        fields['close'],
        fields['volume'],
        fields['volume_surge']
    ]
    
    print("测试字段:")
    for i, field in enumerate(test_fields):
        print(f"  {i+1}. {field}")
    
    # 执行查询
    result = D.features(
        instruments=['159302.SZ'],
        fields=test_fields,
        start_time='2024-12-01',
        end_time='2024-12-31'
    )
    
    print(f"\n✅ 查询成功！数据形状: {result.shape}")
    print("最近5行数据:")
    print(result.tail())
    
    # 测试完整启动信号查询
    print("\n=== 测试完整启动信号查询 ===")
    startup_fields = [
        fields['close'],
        fields['startup_signal'],
        fields['startup_strength']
    ]
    
    startup_result = D.features(
        instruments=['159302.SZ'],
        fields=startup_fields,
        start_time='2024-11-01',
        end_time='2024-12-31'
    )
    
    startup_result.columns = ['收盘价', '启动信号', '启动强度']
    print(f"✅ 启动信号查询成功！数据形状: {startup_result.shape}")
    
    # 查看是否有启动信号
    signal_count = startup_result['启动信号'].sum()
    print(f"检测到启动信号次数: {signal_count}")
    
    if signal_count > 0:
        print("\n启动信号详情:")
        signals_detail = startup_result[startup_result['启动信号'] == 1]
        print(signals_detail)
    
    print("\n🎉 所有测试通过！指标修复成功！")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()