import pandas as pd

aog_exchange = pd.read_csv("./data/processed/aog_with_exchange_match.csv")
exchange_df = pd.read_csv("./data/raw/21章拆换记录.csv")
# 去除 换行符
exchange_df["ZZCHYY"] = exchange_df["ZZCHYY"].str.replace("\n", " ")

df = pd.merge(aog_exchange, exchange_df, on="CHID", how="left")
df.to_csv("./data/analysis/aog_with_exchange_match.csv", index=False)
