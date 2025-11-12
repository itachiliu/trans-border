import pandas as pd
import os

def merge_performance_logs():
    # 读取主性能结果（包含 avg_cpu_percent 和 peak_memory_mb）
    if not os.path.exists("performance_results.csv"):
        raise FileNotFoundError("performance_results.csv not found!")
    df_main = pd.read_csv("performance_results.csv")

    # 读取 Provider 上传时间
    if os.path.exists("provider_upload_times.csv"):
        df_prov = pd.read_csv("provider_upload_times.csv")
        df_prov = df_prov.rename(columns={"Upload o-VC to Blockchain": "Provider Upload o-VC"})
    else:
        df_prov = pd.DataFrame(columns=["run_id", "Provider Upload o-VC"])

    # 读取 Reviewer 上传时间
    if os.path.exists("reviewer_upload_times.csv"):
        df_rev = pd.read_csv("reviewer_upload_times.csv")
        df_rev = df_rev.rename(columns={"Upload o-VP to Blockchain": "Reviewer Upload o-VP"})
    else:
        df_rev = pd.DataFrame(columns=["run_id", "Reviewer Upload o-VP"])

    # 合并：以主表为主，左连接其他两个（自动保留 avg_cpu_percent, peak_memory_mb 等所有字段）
    df_merged = df_main.merge(df_prov, on="run_id", how="left")
    df_merged = df_merged.merge(df_rev, on="run_id", how="left")

    # 保存结果
    output_file = "final_performance_summary.csv"
    df_merged.to_csv(output_file, index=False, float_format="%.6f")
    print(f"✅ 合并完成！结果已保存到 {output_file}")
    print(f"📊 共 {len(df_merged)} 条记录（含 CPU 和内存指标）")

if __name__ == "__main__":
    merge_performance_logs()