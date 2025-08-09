import qlib
from qlib.data import D
from pathlib import Path
import os

def diagnose_qlib_data():
    """诊断qlib数据加载问题"""
    
    # 1. 检查数据目录结构
    data_dir = Path("~/data/qlib_data/etf_data").expanduser()
    print(f"检查数据目录: {data_dir}")
    print(f"目录存在: {data_dir.exists()}")
    
    if data_dir.exists():
        print("\n目录结构:")
        for item in data_dir.rglob("*"):
            if item.is_file():
                print(f"  {item.relative_to(data_dir)}")
    
    # 2. 检查关键文件
    calendar_file = data_dir / "calendars" / "day.txt"
    instruments_file = data_dir / "instruments" / "all.txt"
    
    print(f"\n关键文件检查:")
    print(f"日历文件存在: {calendar_file.exists()}")
    print(f"股票池文件存在: {instruments_file.exists()}")
    
    if instruments_file.exists():
        with open(instruments_file, 'r') as f:
            instruments = f.read().strip().split('\n')
        print(f"股票池中ETF数量: {len(instruments)}")
        print(f"前5只ETF: {instruments[:5]}")
    
    # 3. 初始化qlib并测试
    try:
        print(f"\n初始化qlib...")
        qlib.init(provider_uri=str(data_dir), region="cn")
        print("qlib初始化成功")
        
        # 测试instruments方法
        print(f"\n测试D.instruments():")
        result = D.instruments()
        print(f"D.instruments()返回类型: {type(result)}")
        print(f"D.instruments()返回内容: {result}")
        
        # 尝试不同的参数
        try:
            result2 = D.instruments(market="all")
            print(f"D.instruments(market='all')返回: {result2}")
        except Exception as e:
            print(f"D.instruments(market='all')出错: {e}")
        
        # 尝试直接读取instruments文件
        try:
            from qlib.data.provider import LocalInstrumentProvider
            provider = LocalInstrumentProvider()
            instruments_data = provider.list_instruments()
            print(f"直接从provider读取: {type(instruments_data)}, 长度: {len(instruments_data) if hasattr(instruments_data, '__len__') else 'N/A'}")
            if hasattr(instruments_data, '__len__') and len(instruments_data) > 0:
                print(f"前5只: {list(instruments_data)[:5]}")
        except Exception as e:
            print(f"直接读取provider出错: {e}")
            
        # 测试features方法
        if instruments_file.exists():
            with open(instruments_file, 'r') as f:
                first_etf = f.readline().strip()
            print(f"\n测试第一只ETF数据: {first_etf}")
            try:
                data = D.features(instruments=[first_etf], fields=["$close"], start_time="2023-03-20", end_time="2023-03-25")
                print(f"数据读取成功: {len(data)} 条记录")
                print(data.head())
            except Exception as e:
                print(f"数据读取失败: {e}")
        
    except Exception as e:
        print(f"qlib初始化失败: {e}")

if __name__ == "__main__":
    diagnose_qlib_data() 