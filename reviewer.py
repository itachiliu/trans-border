import asyncio
import csv
import json
import os
import time
from datetime import datetime, timedelta

import didkit

import HashMethod
import VPHashUpload
import fileoper
from ruleset import RuleChecker, Decision
from transettings import TranSettings
from propset import TransProps


class Reviewer:
    ''' Sign user's transborder VC'''

    def __init__(self, keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline().strip()
        self.did = didkit.key_to_did("key", self.key)
        self.is_valid = False

    def check_rules(self, filename: str) -> Decision:
        with open(filename, "r", encoding="utf-8") as f:
            jo = json.load(f)

        print(f'''{jo["issuer"]}''')
        rc = RuleChecker()
        ticket = TranSettings()
        ticket.from_vc(jo)
        tps = TransProps(ticket)

        return rc.judge(tps)

    def sign_file(self, filename: str, outfile: str):
        with open(filename, "r", encoding="utf-8") as f:
            jo = json.load(f)

        jostr = json.dumps(jo)
        asyncio.run(self.sign_content(jostr, outfile))

    async def sign_content(self, content: str, outfile: str):
        start_time = time.time()
        signed_credential = await didkit.issue_credential(
            content,
            json.dumps({}),
            self.key)
        fileoper.write_text_file(outfile, signed_credential)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Reviewer审核 o-VC 时间：{elapsed_time}")

    # ===== 修改：增加 run_id 参数 =====
    def sign_transborder_vp(self, vcfile: str, ovcfile: str, outvpfile: str, run_id: int = None):
        asyncio.run(self.do_sign_transborder_vp(vcfile, ovcfile, outvpfile, run_id))

    async def do_sign_transborder_vp(self, vcfile: str, transfile: str, outfile: str, run_id: int = None):

        star_time = time.time()
        with open(vcfile, "r", encoding="utf-8") as f:
            jo = json.load(f)

        with open(transfile, "r", encoding="utf-8") as f:
            transo = json.load(f)

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
            "verifiableCredential": [jo, transo]
        }

        didkit_options = {
            "proofPurpose": "authentication",
            "verificationMethod": verification_method,
        }

        purified = json.dumps(presentation1)  # 更安全的方式，避免 str().replace
        options_str = json.dumps(didkit_options)

        signed_presentation = await didkit.issue_presentation(
            purified,
            options_str,
            self.key
        )
        fileoper.write_text_file(outfile, signed_presentation)

        end_time = time.time()
        elapsed_time = end_time - star_time
        print(f" Transferor Verify o-VP Time：{elapsed_time}")

        # === vp hash 上链 ===
        hashTransferorSign = HashMethod.hash_file(outfile)
        print("tranferor sign user vc:" + hashTransferorSign)
        start_time = time.time()
        VPHashUpload.SetJson(hashTransferorSign)
        end_time = time.time()
        upload_time = end_time - start_time
        print(f"Upload o-VP to Blockchain：{upload_time}")

        # === 新增：保存到独立 CSV ===
        print(f"run ID：{run_id}")
        self._log_vp_upload_time(run_id, upload_time)

    def _log_vp_upload_time(self, run_id: int, elapsed: float):
        """Append o-VP upload time to reviewer_upload_times.csv"""
        csv_file = "reviewer_upload_times.csv"
        file_exists = os.path.isfile(csv_file)

        with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["run_id", "Upload o-VP to Blockchain"])
            writer.writerow([run_id if run_id is not None else "N/A", f"{elapsed:.6f}"])