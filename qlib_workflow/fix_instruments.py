#!/usr/bin/env python3
"""
修复instruments文件格式
将包含日期的格式转换为qlib期望的格式
"""

import os
from pathlib import Path

def fix_instruments_file(data_dir="~/data/qlib_data/etf_data"):
    """修复instruments文件格式"""
    data_path = Path(data_dir).expanduser()
    instruments_file = data_path / "instruments" / "all.txt"
    
    if not instruments_file.exists():
        print(f"文件不存在: {instruments_file}")
        return False
    
    print(f"修复instruments文件: {instruments_file}")
    
    # 读取原始文件
    with open(instruments_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"原始文件有 {len(lines)} 行")
    
    # 提取股票代码（第一列）
    instruments = []
    for line in lines:
        line = line.strip()
        if line:
            # 分割制表符或空格，取第一部分作为股票代码
            parts = line.split('\t') if '\t' in line else line.split()
            if parts:
                instrument = parts[0].strip()
                if instrument:
                    instruments.append(instrument)
    
    print(f"提取到 {len(instruments)} 只ETF代码")
    print(f"前5只: {instruments[:5]}")
    
    # 备份原文件
    backup_file = instruments_file.with_suffix('.txt.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        with open(instruments_file, 'r', encoding='utf-8') as original:
            f.write(original.read())
    print(f"原文件已备份到: {backup_file}")
    
    # 写入修复后的文件
    with open(instruments_file, 'w', encoding='utf-8') as f:
        for instrument in instruments:
            f.write(f"{instrument}\n")
    
    print(f"文件修复完成!")
    print(f"修复后格式预览:")
    with open(instruments_file, 'r', encoding='utf-8') as f:
        preview = f.readlines()[:5]
        for i, line in enumerate(preview):
            print(f"  {i+1}: {line.strip()}")
    
    return True

def test_qlib_after_fix(data_dir="~/data/qlib_data/etf_data"):
    """修复后测试qlib是否能正常工作"""
    try:
        import qlib
        from qlib.data import D
        
        data_path = str(Path(data_dir).expanduser())
        print(f"\n重新初始化qlib: {data_path}")
        qlib.init(provider_uri=data_path, region="cn")
        
        # 测试instruments方法
        print("\n测试D.instruments():")
        result = D.instruments()
        print(f"类型: {type(result)}")
        print(f"内容: {result}")
        
        # 如果返回的是list，说明修复成功
        if isinstance(result, list):
            print(f"✅ 成功！获取到 {len(result)} 只ETF")
            print(f"前5只: {result[:5]}")
            
            # 测试数据读取
            if result:
                first_etf = result[0]
                print(f"\n测试读取第一只ETF数据: {first_etf}")
                try:
                    data = D.features(
                        instruments=[first_etf], 
                        fields=["$close"], 
                        start_time="2023-03-20", 
                        end_time="2023-03-25"
                    )
                    print(f"数据读取成功: {len(data)} 条记录")
                    if len(data) > 0:
                        print(data.head())
                except Exception as e:
                    print(f"数据读取失败: {e}")
        else:
            print("❌ 仍然返回配置对象，可能还有其他问题")
            
    except Exception as e:
        print(f"qlib测试失败: {e}")

if __name__ == "__main__":
    # 修复文件格式
    if fix_instruments_file():
        # 测试修复结果
        test_qlib_after_fix() 