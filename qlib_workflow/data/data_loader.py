import qlib
from qlib.data import D

class DataLoader:
    def __init__(self, instruments="csi300", start_time="2008-01-01", end_time="2020-08-01"):
        self.instruments = instruments
        self.start_time = start_time
        self.end_time = end_time
    
    def load_data(self, fields=None):
        """加载股票数据"""
        if fields is None:
            fields = ["$open", "$high", "$low", "$close", "$volume"]
        
        data = D.features(
            instruments=self.instruments,
            fields=fields,
            start_time=self.start_time,
            end_time=self.end_time
        )
        return data
    
    def load_labels(self, label_expr="Ref($close, -1)/$close - 1"):
        """加载标签数据"""
        labels = D.features(
            instruments=self.instruments,
            fields=[label_expr],
            start_time=self.start_time,
            end_time=self.end_time
        )
        return labels 