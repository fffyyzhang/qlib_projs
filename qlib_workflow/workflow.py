import pandas as pd


def process_data():
    f="/Users/liyuan/data/quant/raw/etf_daily.csv"
    df=pd.read_csv(f)
    df.rename(columns={"vol":"volume"},inplace=True)
    df.to_csv(f,index=False)


if __name__ == "__main__":
    process_data()