import asyncio
import csv
import json
import time
from datetime import datetime, timedelta

import didkit

import UserKeyUpload
from reviewer import Reviewer
from transferor import Transferor
from provider import Provider
from ruleset import Decision

import fileoper

import psutil
import threading
import time

class ResourceMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.cpu_percentages = []
        self.max_memory_mb = 0
        self._monitoring = False
        self._thread = None

    def _monitor(self):
        while self._monitoring:
            try:
                cpu = self.process.cpu_percent(interval=0.01)  # 短间隔采样
                mem_info = self.process.memory_info()
                mem_mb = mem_info.rss / (1024 * 1024)  # RSS in MB
                self.cpu_percentages.append(cpu)
                if mem_mb > self.max_memory_mb:
                    self.max_memory_mb = mem_mb
            except Exception:
                pass  # 进程可能已退出
            time.sleep(0.01)

    def start(self):
        self._monitoring = True
        self._thread = threading.Thread(target=self._monitor, daemon=True)
        self._thread.start()

    def stop(self):
        self._monitoring = False
        if self._thread:
            self._thread.join(timeout=0.1)
        avg_cpu = sum(self.cpu_percentages) / len(self.cpu_percentages) if self.cpu_percentages else 0.0
        return {
            "avg_cpu_percent": avg_cpu,
            "peak_memory_mb": self.max_memory_mb
        }


class User:
    """User representing an user who has an unique DID and can init Transfer Request."""

    def __init__(self, keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline().strip()
        self.did = didkit.key_to_did("key", self.key)

    def sign_self_vp(self, vcfile: str, outvpfile: str):
        asyncio.run(self.do_sign_self_vp(vcfile, outvpfile))

    async def do_sign_self_vp(self, vcfile: str, outfile: str):
        with open(vcfile, "r", encoding="utf-8") as f:
            jo = json.load(f)

        verification_method = await didkit.key_to_verification_method("key", self.key)
        issuance_date = datetime.now().replace(microsecond=0)
        expiration_date = issuance_date + timedelta(weeks=2)

        presentation1 = {
            "id": "http://example.org/credentials/req",
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            "type": ["VerifiablePresentation"],
            "holder": self.did,
            "verifiableCredential": [jo]
        }

        didkit_options = {
            "proofPurpose": "authentication",
            "verificationMethod": verification_method,
        }

        purified = json.dumps(presentation1)
        signed_presentation = await didkit.issue_presentation(
            purified,
            json.dumps(didkit_options),
            self.key
        )
        fileoper.write_text_file(outfile, signed_presentation)


def do_transfer(content: str):
    runner = Transferor()
    runner.run(content)


def transborder_demo_single_run(run_id: int):
    # 启动资源监控
    monitor = ResourceMonitor()
    monitor.start()
    times = {
        "run_id": run_id,
        "User上链": 0.0,
        "自签名时间": 0.0,
        "Provider Create o-VC": 0.0,
        "Rule Judgment": 0.0,
        "Reviewer Verify o-VC": 0.0,
        "Reviewer Create and Sign o-VP": 0.0,
        "Transferor Verify o-VP": 0.0,
        "avg_cpu_percent": 0.0,  # ← 新增
        "peak_memory_mb": 0.0  # ← 新增
    }
    try:
    # === 1. User DID Upload to Blockchain ===
        actor = User("user1.key")
        start = time.time()
        UserKeyUpload.SetJson(actor.did)
        times["User上链"] = time.time() - start

        # === 2. User 自签名 VP ===
        start = time.time()
        actor.sign_self_vp("user1.json", "user1_signed_vp.json")
        times["自签名时间"] = time.time() - start

        # === 3. Provider 验证 VP 并创建 o-VC ===
        prov = Provider("user3.key")
        if not prov.verify_vp_file("user1_signed_vp.json"):
            raise RuntimeError("Provider failed to verify user VP")

        start = time.time()
        prov.create_trans_request("user3", "user4", "trans0928.json", run_id)
        times["Provider Create o-VC"] = time.time() - start

        # === 4. Rule Judgment ===
        revw = Reviewer("user4.key")
        start = time.time()
        should_allow = revw.check_rules("trans0928.json")
        times["Rule Judgment"] = time.time() - start
        if should_allow == Decision.REJECT:
            raise RuntimeError("Rules rejected the request")

        # === 5. Reviewer 签名 o-VC (Verify o-VC) ===
        start = time.time()
        revw.sign_file("trans0928.json", "trans0928signed.json")
        times["Reviewer Verify o-VC"] = time.time() - start

        # === 6. Reviewer 创建并签名 o-VP ===
        start = time.time()
        revw.sign_transborder_vp("user4.json", "trans0928signed.json", "trans0928signed_vp.json", run_id)
        times["Reviewer Create and Sign o-VP"] = time.time() - start

        # === 7. Transferor 验证 o-VP ===
        it_person = Transferor()
        start = time.time()
        it_person.do_transfer("trans0928signed_vp.json")
        times["Transferor Verify o-VP"] = time.time() - start
    finally:
        # 停止监控并记录资源使用
        resource_stats = monitor.stop()
        times["avg_cpu_percent"] = resource_stats["avg_cpu_percent"]
        times["peak_memory_mb"] = resource_stats["peak_memory_mb"]

    return times


def main():
    NUM_RUNS = 50
    csv_file = "performance_results.csv"
    fieldnames = [
        "run_id",
        "User上链",
        "自签名时间",
        "Provider Create o-VC",
        "Rule Judgment",
        "Reviewer Verify o-VC",
        "Reviewer Create and Sign o-VP",
        "Transferor Verify o-VP",
        "avg_cpu_percent",      # ← 新增
        "peak_memory_mb"        # ← 新增
    ]

    all_results = []

    print(f"Starting {NUM_RUNS} runs...")
    for i in range(1, NUM_RUNS + 1):
        try:
            print(f"Run {i}/{NUM_RUNS}")
            result = transborder_demo_single_run(i)
            all_results.append(result)
        except Exception as e:
            print(f"Run {i} failed: {e}")
            # 可选择跳过或终止
            continue

    # 写入 CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    # 计算平均值
    avg = {key: 0.0 for key in fieldnames if key != "run_id"}
    valid_runs = len(all_results)
    for result in all_results:
        for key in avg:
            avg[key] += result[key]

    for key in avg:
        avg[key] /= valid_runs

    print("\n=== Average Times (seconds) ===")
    for key, val in avg.items():
        print(f"{key}: {val:.6f}")

    print(f"\nResults saved to {csv_file}")


if __name__ == "__main__":
    main()