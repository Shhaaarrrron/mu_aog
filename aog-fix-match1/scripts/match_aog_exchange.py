import os

import pandas as pd


def match_aog_exchange():
    print("=" * 80)
    print("AOG与换件记录匹配")
    print("=" * 80)

    aog_path = "data/processed/aog_chapter21.csv"
    exchange_path = "data/raw/21章拆换记录.csv"

    if not os.path.exists(aog_path):
        print(f"错误: AOG文件不存在 {aog_path}")
        return

    if not os.path.exists(exchange_path):
        print(f"错误: 换件记录文件不存在 {exchange_path}")
        return

    print("\n📂 加载数据...")
    aog_df = pd.read_csv(aog_path)
    exchange_df = pd.read_csv(exchange_path)

    print(f"  AOG记录: {len(aog_df)} 条")
    print(f"  换件记录: {len(exchange_df)} 条")

    aog_df["CHID"] = ""
    aog_df["剩余数量"] = aog_df["MENGE"]

    exchange_df["ZCHDAT"] = exchange_df["ZCHDAT"].astype(str)
    aog_df["ZZJRRQ"] = aog_df["ZZJRRQ"].astype(str).str.strip()
    aog_df["ZZGHRQ"] = aog_df["ZZGHRQ"].astype(str).str.strip()
    aog_df["ZZGHRQ"] = aog_df["ZZGHRQ"].replace("", pd.NA)

    exchange_install = exchange_df[
        exchange_df["ZUMATNR"].notna() & (exchange_df["ZUMATNR"] != "")
    ].copy()

    print("\n🔍 开始匹配...")
    match_count = 0

    for idx, exchange_row in exchange_install.iterrows():
        zu_matnr = exchange_row["ZUMATNR"]
        zchdat = exchange_row["ZCHDAT"]

        candidates = aog_df[
            (aog_df["MATNR"] == zu_matnr)
            & (aog_df["ZZJRRQ"] <= zchdat)
            & (aog_df["剩余数量"] > 0)
        ]

        if len(candidates) > 0:
            if candidates["ZZGHRQ"].isna().all():
                matched_aog = candidates.iloc[0]
            else:
                valid_candidates = candidates[
                    (candidates["ZZGHRQ"].isna())
                    | (candidates["ZZGHRQ"] == "")
                    | (candidates["ZZGHRQ"] == "nan")
                    | (candidates["ZZGHRQ"] >= zchdat)
                ]
                if len(valid_candidates) > 0:
                    matched_aog = valid_candidates.iloc[0]
                else:
                    continue
        else:
            continue

        aog_idx = matched_aog.name
        if aog_df.at[aog_idx, "CHID"] == "":
            aog_df.at[aog_idx, "CHID"] = [exchange_row["CHID"]]
        else:
            aog_df.at[aog_idx, "CHID"].append(exchange_row["CHID"])
        aog_df.at[aog_idx, "剩余数量"] -= 1
        match_count += 1

    print(f"\n✅ 匹配完成: {match_count} 条求援记录成功匹配")

    output_path = "data/processed/aog_with_exchange_match.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    aog_df.to_csv(output_path, index=False)
    print(f"💾 结果已保存: {output_path}")

    print("\n" + "-" * 40)
    print("匹配结果统计")
    print("-" * 40)
    matched = aog_df[aog_df["CHID"] != ""]
    print(f"  已匹配: {len(matched)} 条")
    print(f"  未匹配: {len(aog_df) - len(matched)} 条")
    print(f"  匹配率: {len(matched) / len(aog_df) * 100:.1f}%")

    print("\n" + "-" * 40)
    print("按优先级统计匹配情况")
    print("-" * 40)
    for pri in aog_df["ADPRI"].unique():
        subset = aog_df[aog_df["ADPRI"] == pri]
        matched_count = len(subset[subset["CHID"] != ""])
        print(
            f"  {pri}: {matched_count}/{len(subset)} ({matched_count / len(subset) * 100:.1f}%)"
        )

    print("\n" + "-" * 40)
    print("样例数据 (前10条匹配记录)")
    print("-" * 40)
    if len(matched) > 0:
        sample = matched.head(10)[["EBELN", "MATNR", "ZZJRRQ", "ZZGHRQ", "CHID"]]
        for _, row in sample.iterrows():
            print(
                f"  订单:{row['EBELN']} | 件号:{row['MATNR']} | 求援:{row['ZZJRRQ']} | 还回:{row['ZZGHRQ']} | 换件CHID:{row['CHID']}"
            )

    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)


if __name__ == "__main__":
    match_aog_exchange()
