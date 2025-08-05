"""
ETF价格突然启动检测指标
基于qlib表达式系统实现多重技术指标组合
"""

import qlib
from qlib.data import D
import pandas as pd
import numpy as np


class PriceStartupIndicator:
    """ETF价格突然启动检测指标"""
    
    def __init__(self):
        """初始化指标参数"""
        # 成交量相关参数
        self.volume_ma_period = 20  # 成交量移动平均周期
        self.volume_threshold = 1.05  # 成交量放大倍数
        
        # 价格相关参数  
        self.price_ma_period = 10   # 价格移动平均周期
        self.price_threshold = 0.01  # 价格上涨阈值(2%)
        
        # 突破相关参数
        self.resistance_period = 20  # 阻力位计算周期
        self.breakout_threshold = 0.002  # 突破阈值(0.5%)
        
        # 波动率参数
        self.volatility_period = 10  # 波动率计算周期
        self.volatility_threshold = 1.03  # 波动率放大倍数
    
        
    def get_volume_surge_signal(self):
        """成交量放大信号"""
        return f"($volume / Mean($volume, {self.volume_ma_period}) > {self.volume_threshold})"
    
    def get_price_momentum_signal(self):
        """价格动量信号"""
        return f"(($close / Ref($close, 1) - 1) > {self.price_threshold})"
    
    def get_resistance_breakout_signal(self):
        """阻力位突破信号"""
        return f"($close > Max($high, {self.resistance_period}) * (1 + {self.breakout_threshold}))"
    
    def get_volatility_expansion_signal(self):
        """波动率扩张信号"""
        return f"(Std($close, {self.volatility_period}) > Mean(Std($close, {self.volatility_period}), {self.volatility_period * 2}) * {self.volatility_threshold})"
    
    def get_price_trend_signal(self):
        """价格趋势信号"""
        return f"($close > Ref($close, 1))"
    
    def get_comprehensive_startup_signal(self):
        """综合启动信号 - 组合多个子信号"""
        volume_signal = self.get_volume_surge_signal()
        momentum_signal = self.get_price_momentum_signal()
        breakout_signal = self.get_resistance_breakout_signal()
        volatility_signal = self.get_volatility_expansion_signal()
        trend_signal = self.get_price_trend_signal()
        
        # 综合信号：至少满足3个条件
        return f"({volume_signal} + {momentum_signal} + {breakout_signal} + {volatility_signal} + {trend_signal}) >= 3"
    
    def get_startup_strength_score(self):
        """启动强度评分 - 返回0-5的评分"""
        volume_signal = self.get_volume_surge_signal()
        momentum_signal = self.get_price_momentum_signal()
        breakout_signal = self.get_resistance_breakout_signal()
        volatility_signal = self.get_volatility_expansion_signal()
        trend_signal = self.get_price_trend_signal()
        
        return f"({volume_signal} + {momentum_signal} + {breakout_signal} + {volatility_signal} + {trend_signal})"
    
    def get_all_signals(self):
        """获取所有信号的字典"""
        return {
            'volume_surge': self.get_volume_surge_signal(),
            'price_momentum': self.get_price_momentum_signal(),
            'resistance_breakout': self.get_resistance_breakout_signal(),
            'volatility_expansion': self.get_volatility_expansion_signal(),
            'price_trend': self.get_price_trend_signal(),
            'comprehensive_signal': self.get_comprehensive_startup_signal(),
            'startup_strength': self.get_startup_strength_score()
        }
    
    def analyze_etf_startup(self, instruments, start_time, end_time):
        """分析ETF启动信号"""
        signals = self.get_all_signals()
        
        # 构建查询字段
        fields = [
            '$close', '$open', '$high', '$low', '$volume',
            signals['volume_surge'],
            signals['price_momentum'], 
            signals['resistance_breakout'],
            signals['volatility_expansion'],
            signals['price_trend'],
            signals['comprehensive_signal'],
            signals['startup_strength']
        ]
        
        # 获取数据
        data = D.features(
            instruments=instruments,
            fields=fields,
            start_time=start_time,
            end_time=end_time
        )
        
        # 重命名列以便理解
        if len(data.columns) >= 12:
            data.columns = [
                'close', 'open', 'high', 'low', 'volume',
                'volume_surge', 'price_momentum', 'resistance_breakout',
                'volatility_expansion', 'price_trend', 
                'startup_signal', 'startup_strength'
            ]
        
        return data
    
    def get_startup_summary(self, data):
        """获取启动信号汇总统计"""
        startup_days = data[data['startup_signal'] == 1]
        
        summary = {
            'total_days': len(data),
            'startup_days': len(startup_days),
            'startup_ratio': len(startup_days) / len(data) if len(data) > 0 else 0,
            'avg_startup_strength': startup_days['startup_strength'].mean() if len(startup_days) > 0 else 0,
            'max_startup_strength': startup_days['startup_strength'].max() if len(startup_days) > 0 else 0
        }
        
        # 各子信号统计
        if len(startup_days) > 0:
            signal_stats = {
                'volume_surge_rate': startup_days['volume_surge'].mean(),
                'momentum_rate': startup_days['price_momentum'].mean(),
                'breakout_rate': startup_days['resistance_breakout'].mean(),
                'volatility_rate': startup_days['volatility_expansion'].mean(),
                'trend_rate': startup_days['price_trend'].mean()
            }
            summary.update(signal_stats)
        
        return summary


def create_startup_fields():
    """创建用于qlib的启动信号字段表达式"""
    indicator = PriceStartupIndicator()
    
    fields = {
        # 基础价量数据
        'close': '$close',
        'open': '$open', 
        'high': '$high',
        'low': '$low',
        'volume': '$volume',
        
        # 技术指标
        'volume_ma20': f'Mean($volume, {indicator.volume_ma_period})',
        'price_ma10': f'Mean($close, {indicator.price_ma_period})',
        'price_return': '($close / Ref($close, 1) - 1)',
        'volume_ratio': f'($volume / Mean($volume, {indicator.volume_ma_period}))',
        'resistance_level': f'Max($high, {indicator.resistance_period})',
        
        # 启动信号
        'volume_surge': indicator.get_volume_surge_signal(),
        'price_momentum': indicator.get_price_momentum_signal(), 
        'resistance_breakout': indicator.get_resistance_breakout_signal(),
        'volatility_expansion': indicator.get_volatility_expansion_signal(),
        'price_trend': indicator.get_price_trend_signal(),
        
        # 综合信号
        'startup_signal': indicator.get_comprehensive_startup_signal(),
        'startup_strength': indicator.get_startup_strength_score()
    }
    
    return fields


if __name__ == "__main__":
    # 使用示例
    print("ETF价格突然启动检测指标")
    print("=" * 50)
    
    # 创建指标实例
    indicator = PriceStartupIndicator()
    
    # 显示所有信号表达式
    signals = indicator.get_all_signals()
    for name, expr in signals.items():
        print(f"\n{name}:")
        print(expr)
    
    print("\n" + "=" * 50)
    print("可直接在qlib中使用的字段表达式:")
    
    fields = create_startup_fields()
    for name, expr in fields.items():
        print(f"'{name}': '{expr}'")