import asyncio
import json
from datetime import datetime, timedelta, timezone

import didkit

import fileoper
from ruleset import RuleChecker
from ruleset import Decision
from transettings import TranSettings
from propset import TransProps

class Reviewer:
    ''' Sign user's transborder VC'''
    
    def __init__(self, keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline()
            f.close()
        self.did = didkit.key_to_did("key", self.key)
        self.is_valid = False

    def check_rules(self, filename: str) -> Decision:
        ''' TODO check transborder rules '''
        with open(filename, "r", encoding="utf-8") as f:
            jo = json.load(f)
            f.close()
        
        print(f'''{jo["issuer"]}''')
        rc = RuleChecker()
        ticket = TranSettings()
        ticket.from_vc(jo)
        tps = TransProps(ticket)

        return rc.judge(tps)

    def sign_file(self, filename: str, outfile: str):
        ''' Sign user's transborder VC'''
        with open(filename, "r", encoding="utf-8") as f:
            jo = json.load(f)
            f.close()
        
        jostr = json.dumps(jo)
        asyncio.run(self.sign_content(jostr, outfile))

    async def sign_content(self, content: str, outfile: str):
        signed_credential = await didkit.issue_credential(
            content,
            json.dumps({}),
            self.key)
        fileoper.write_text_file(outfile, signed_credential)

    def sign_transborder_vp(self, vcfile: str, ovcfile: str, outvpfile: str):
        asyncio.run(self.do_sign_transborder_vp(vcfile,  ovcfile, outvpfile))

    async def do_sign_transborder_vp(self, vcfile: str, transfile: str, outfile: str):
        ''' Sign a verification presentation. vcfile: user VC. transfile: transfer VC. '''
        # verifiableCredential
        with open(vcfile, "r", encoding="utf-8") as f:
            jo = json.load(f)
            f.close()

        with open(transfile, "r", encoding="utf-8") as f:
            transo = json.load(f)
            f.close()

        verification_method = await didkit.key_to_verification_method("key", self.key)
        issuance_date = datetime.now().replace(microsecond=0)
        expiration_date = issuance_date + timedelta(weeks=2)

        # didkit-python-main\tests\test_main.py
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

        purified = str(presentation1).replace("'", '"')
        #print(purified)
        
        signed_presentation = await didkit.issue_presentation(
            purified,
            str(didkit_options).replace("'", '"'),
            self.key
        )
        fileoper.write_text_file(outfile, signed_presentation)
