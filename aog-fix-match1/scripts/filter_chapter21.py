import os

import pandas as pd


def filter_chapter21_aog():
    print("=" * 80)
    print("筛选21章零件的AOG记录")
    print("=" * 80)

    aog_path = "data/raw/mu_aog.csv"
    cmm21_path = "data/raw/TEMP_21_CMM_PNR_202604141359.csv"
    pn_mapper_path = "data/raw/pn_id_mapper.csv"
    output_path = "data/processed/aog_chapter21.csv"

    if not os.path.exists(aog_path):
        print(f"错误: 求援记录文件不存在 {aog_path}")
        return

    if not os.path.exists(cmm21_path):
        print(f"错误: 21章CMM_PNR文件不存在 {cmm21_path}")
        return

    if not os.path.exists(pn_mapper_path):
        print(f"错误: PNR映射文件不存在 {pn_mapper_path}")
        return

    print("\n📂 加载数据...")
    aog_df = pd.read_csv(aog_path)
    cmm21_df = pd.read_csv(cmm21_path)
    pn_mapper_df = pd.read_csv(pn_mapper_path)

    print(f"  AOG总记录: {len(aog_df)} 条")
    print(f"  21章零件清单: {len(cmm21_df)} 条")
    print(f"  PNR映射表: {len(pn_mapper_df)} 条")

    print("\n🔍 筛选21章零件...")
    aog_ch21 = aog_df[aog_df["MATNR"].isin(cmm21_df["PNR_CMM"])].copy()

    print(f"  筛选后记录: {len(aog_ch21)} 条")

    print("\n🔍 匹配PNR ID...")
    pn_mapper_unique = pn_mapper_df.drop_duplicates(subset="cur_pnr", keep="first")
    aog_ch21["PNR_ID"] = aog_ch21["MATNR"].map(
        pn_mapper_unique.set_index("cur_pnr")["matched_id"]
    )
    matched_count = aog_ch21["PNR_ID"].notna().sum()
    print(f"  成功匹配: {matched_count} 条")

    print("\n" + "-" * 40)
    print("按优先级统计")
    print("-" * 40)
    for pri in aog_ch21["ADPRI"].unique():
        subset = aog_ch21[aog_ch21["ADPRI"] == pri]
        print(f"  {pri}: {len(subset)} 条")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    aog_ch21.to_csv(output_path, index=False)
    print(f"\n💾 结果已保存: {output_path}")

    print("\n" + "=" * 80)
    print("筛选完成")
    print("=" * 80)


if __name__ == "__main__":
    filter_chapter21_aog()
