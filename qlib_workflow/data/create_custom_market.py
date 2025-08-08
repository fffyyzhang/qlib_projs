#!/usr/bin/env python3
"""
创建自定义ETF market的最简单方法
"""

import os
from pathlib import Path


def create_custom_etf_market(etf_list, market_name="etf_human", qlib_data_path="/data/data_liy/qlib/etf_data"):
    """
    创建自定义ETF市场
    
    Args:
        etf_list: ETF代码列表，如 ['159302.SZ', '159919.SZ', '512690.SH']
        market_name: 市场名称，如 'etf_human'
        qlib_data_path: qlib数据路径
    """
    
    # 1. 确定instruments目录路径
    instruments_dir = Path(qlib_data_path) / "instruments"
    instruments_dir.mkdir(exist_ok=True)
    
    # 2. 创建market文件
    market_file = instruments_dir / f"{market_name}.txt"
    
    # 3. 写入ETF列表
    with open(market_file, 'w') as f:
        for etf_code in etf_list:
            f.write(f"{etf_code}\n")
    
    print(f"✅ 成功创建自定义market: {market_name}")
    print(f"📁 文件路径: {market_file}")
    print(f"📊 包含ETF数量: {len(etf_list)}")
    print(f"📝 ETF列表: {etf_list}")
    
    return str(market_file)


def test_custom_market():
    """测试自定义市场"""
    
    # 定义你的ETF列表
    my_etf_list = [
        '159302.SZ',  # 创业板指数ETF
        '159919.SZ',  # 科创50ETF  
        '512690.SH',  # 白酒ETF
        '515050.SH',  # 5G ETF
        '159995.SZ',  # 芯片ETF
        '516160.SH',  # 新能源ETF
        '159869.SZ',  # 新能源车ETF
        '159928.SZ',  # 消费ETF
    ]
    
    # 创建自定义market
    market_file = create_custom_etf_market(
        etf_list=my_etf_list, 
        market_name="etf_human"
    )
    
    # 测试使用
    print("\n" + "="*50)
    print("📋 使用方法:")
    print("1. 在qlib中直接使用:")
    print("   D.instruments(market='etf_human')")
    print("   D.features(instruments='etf_human', fields=['$close'], ...)")
    print("\n2. 或者明确指定:")
    print("   from qlib.data import D")
    print("   instruments = D.instruments(market='etf_human')")
    print("   print(f'自定义market包含{len(instruments)}只ETF')")
    
    return market_file


if __name__ == "__main__":
    # 运行测试
    test_custom_market()
    
    # 也可以直接调用函数创建
    # create_custom_etf_market(['159302.SZ', '159919.SZ'], 'my_etf')