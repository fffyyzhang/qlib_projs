import pandas as pd
import qlib
from qlib.data import D
import numpy as np
import struct
from pathlib import Path


class ETFDataConverter:
    def __init__(self, source_file="~/data/quant/raw/etf_daily.csv", 
                 output_dir="~/data/qlib_data/etf_data"):
        self.source_file = Path(source_file).expanduser()
        self.output_dir = Path(output_dir).expanduser()
        
    def load_raw_data(self):
        """加载原始ETF数据"""
        df = pd.read_csv(self.source_file)
        
        # 数据预处理
        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df = df.set_index(['ts_code', 'trade_date']).sort_index()
        
        return df
    
    def create_calendar(self, df):
        """创建日历文件"""
        calendar_dir = self.output_dir / "calendars"
        calendar_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取所有交易日期
        all_dates = df.index.get_level_values(1).unique().sort_values()
        
        # 保存日历文件
        calendar_file = calendar_dir / "day.txt"
        with open(calendar_file, 'w') as f:
            for date in all_dates:
                f.write(f"{date.strftime('%Y-%m-%d')}\n")
        
        print(f"创建日历文件: {calendar_file}")
        return all_dates
    
    def create_instruments(self, df):
        """创建股票池文件"""
        instruments_dir = self.output_dir / "instruments"
        instruments_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取所有ETF代码
        all_instruments = df.index.get_level_values(0).unique().sort_values()
        
        # 保存所有ETF文件
        instruments_file = instruments_dir / "all.txt"
        with open(instruments_file, 'w') as f:
            for instrument in all_instruments:
                f.write(f"{instrument}\n")
        
        print(f"创建股票池文件: {instruments_file}")
        return all_instruments
    
    def save_feature_bin(self, data, output_file):
        """保存特征数据为bin格式"""
        with open(output_file, 'wb') as f:
            for value in data:
                if pd.isna(value):
                    # NaN值用特殊标记
                    f.write(struct.pack('<f', float('nan')))
                else:
                    f.write(struct.pack('<f', float(value)))
    
    def convert_to_qlib_format(self):
        """转换为qlib数据格式"""
        df = self.load_raw_data()
        
        # 创建日历和股票池
        all_dates = self.create_calendar(df)
        all_instruments = self.create_instruments(df)
        
        # 创建features目录
        features_dir = self.output_dir / "features"
        features_dir.mkdir(parents=True, exist_ok=True)
        
        # qlib字段映射
        field_mapping = {
            'open': 'open',
            'high': 'high', 
            'low': 'low',
            'close': 'close',
            'vol': 'volume',
            'amount': 'money'
        }
        
        print(f"开始转换 {len(all_instruments)} 只ETF数据...")
        
        for instrument in all_instruments:
            # 创建股票目录
            instrument_dir = features_dir / instrument.lower()
            instrument_dir.mkdir(exist_ok=True)
            
            # 获取该股票的数据
            if instrument in df.index.get_level_values(0):
                instrument_data = df.loc[instrument].reindex(all_dates, fill_value=np.nan)
                
                # 保存各个字段的bin文件
                for csv_field, qlib_field in field_mapping.items():
                    if csv_field in instrument_data.columns:
                        output_file = instrument_dir / f"{qlib_field}.day.bin"
                        self.save_feature_bin(instrument_data[csv_field].values, output_file)
        
        print(f"数据转换完成，保存到: {features_dir}")
        return str(self.output_dir)
    
    def run(self):
        """运行转换流程"""
        if not self.source_file.exists():
            print(f"源文件不存在: {self.source_file}")
            return None
            
        return self.convert_to_qlib_format()


if __name__ == "__main__":
    converter = ETFDataConverter()
    result = converter.run()
    
    if result:
        print(f"ETF数据转换成功！")
        print(f"数据位置: {result}")
        
        # 初始化qlib验证数据
        qlib.init(provider_uri=result, region="cn")
        print("qlib初始化完成，可以使用转换后的数据")
        
        # 测试数据是否可用
        try:
            data = D.features(instruments="all", fields=["$close"], start_time="2023-03-20", end_time="2023-03-25")
            print(f"数据测试成功，获取到 {len(data)} 条记录")
        except Exception as e:
            print(f"数据测试失败: {e}") 