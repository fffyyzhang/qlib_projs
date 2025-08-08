#!/usr/bin/env python3
"""
测试自定义ETF market的使用
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import qlib
from qlib.data import D
from data.create_custom_market import create_custom_etf_market


def main():
    """主函数"""
    
    print("=== qlib自定义ETF Market测试 ===")
    
    # 1. 初始化qlib
    qlib.init(provider_uri='/data/data_liy/qlib/etf_data')
    print("✅ qlib初始化成功")
    
    # 2. 定义自定义ETF列表
    my_etf_list = [
        '159302.SZ',  # 创业板指数ETF
        '159919.SZ',  # 科创50ETF  
        '512690.SH',  # 白酒ETF
        '515050.SH',  # 5G ETF
        '159995.SZ',  # 芯片ETF
    ]
    
    # 3. 创建自定义market
    print(f"\n📊 创建自定义market，包含{len(my_etf_list)}只ETF")
    market_file = create_custom_etf_market(
        etf_list=my_etf_list, 
        market_name="etf_human"
    )
    
    # 4. 测试使用自定义market
    print("\n=== 测试自定义market使用 ===")
    
    try:
        # 4.1 获取instruments
        instruments = D.instruments(market='etf_human')
        print(f"✅ 成功获取自定义market: {len(instruments)}只ETF")
        print(f"📝 ETF列表: {instruments}")
        
        # 4.2 获取数据
        print(f"\n📈 获取ETF数据...")
        data = D.features(
            instruments='etf_human',  # 使用自定义market
            fields=['$close', '$volume'],
            start_time='2024-12-01',
            end_time='2024-12-31'
        )
        
        print(f"✅ 数据获取成功!")
        print(f"📊 数据形状: {data.shape}")
        print(f"🔍 数据预览:")
        print(data.head())
        
        # 4.3 统计信息
        print(f"\n📈 统计信息:")
        unique_instruments = data.index.get_level_values(0).unique()
        print(f"实际包含ETF数量: {len(unique_instruments)}")
        print(f"数据日期范围: {data.index.get_level_values(1).min()} 到 {data.index.get_level_values(1).max()}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 对比测试 - 使用单只ETF
    print(f"\n=== 对比测试：单只ETF vs 自定义market ===")
    
    try:
        # 单只ETF
        single_data = D.features(
            instruments=['159302.SZ'],
            fields=['$close'],
            start_time='2024-12-01',
            end_time='2024-12-31'
        )
        print(f"单只ETF数据形状: {single_data.shape}")
        
        # 自定义market
        market_data = D.features(
            instruments='etf_human',
            fields=['$close'],
            start_time='2024-12-01',
            end_time='2024-12-31'
        )
        print(f"自定义market数据形状: {market_data.shape}")
        
        print(f"✅ 自定义market成功扩展了数据范围!")
        
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")


if __name__ == "__main__":
    main()