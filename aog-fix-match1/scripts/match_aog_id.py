import pandas as pd

aog_df = pd.read_csv("./data/raw/求援数据.csv")
mapper_df = pd.read_csv("./data/raw/pn_id_mapper.csv")

# 根据 pn 匹配 PNR_ID
aog_df = (
    aog_df.merge(
        mapper_df[["cur_pnr", "matched_id"]],
        left_on="pn",
        right_on="cur_pnr",
        how="left",
    )
    .rename(columns={"matched_id": "PNR_ID"})
    .drop(columns=["cur_pnr"])
)

# 筛选出 aog_status 不为 Doing 和 Cancle 的记录
aog_df = aog_df[~aog_df["aog_status"].isin(["Doing", "Cancel"])]


# 保存结果
aog_df.to_csv("./data/analysis/求援数据_with_pnr_id.csv", index=False)
print(
    f"匹配完成，共 {len(aog_df)} 条记录，成功匹配 {aog_df['PNR_ID'].notna().sum()} 条"
)
