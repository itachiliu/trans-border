import asyncio
import json
import time
from datetime import datetime, time as dt_time, timedelta  # 避免名称冲突


import didkit

import UserKeyUpload
from reviewer import Reviewer
from transferor import Transferor
from provider import Provider
from ruleset import Decision

import fileoper

class User:
    """User representing an user who has an unique DID and can init Transfer Request."""

    def __init__(self, keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline()
            f.close()
        self.did = didkit.key_to_did("key", self.key)

    def sign_self_vp(self, vcfile: str, outvpfile: str):
        asyncio.run(self.do_sign_self_vp(vcfile, outvpfile))

    async def do_sign_self_vp(self, vcfile: str, outfile: str):
        ''' Sign a verification presentation. vcfile: user VC. transfile: transfer VC. '''
        # verifiableCredential
        with open(vcfile, "r", encoding="utf-8") as f:
            jo = json.load(f)
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
            "verifiableCredential": [jo]
        }

        didkit_options = {
            "proofPurpose": "authentication",
            "verificationMethod": verification_method,
        }

        purified = str(presentation1).replace("'", '"')

        signed_presentation = await didkit.issue_presentation(
            purified,
            str(didkit_options).replace("'", '"'),
            self.key
        )
        fileoper.write_text_file(outfile, signed_presentation)

def do_transfer(content: str):
    runner = Transferor()
    runner.run(content)

def authorize_demo():
    ''' A demo authorization: 
    1. A user signs a VP about his VC
    2. The user ask provider to check the VP
    '''
    actor = User("user1.key")
    print("User: " + actor.did)
    '''
    User DID Upload to Blockchain
    '''
    present_seconds = time.time()
    UserKeyUpload.SetJson(actor.did)
    present_seconds_self_signed = time.time()
    print(f"User上链时间：{present_seconds_self_signed - present_seconds}")

    trans_vc_signed_vp = "user1_signed_vp.json"
    present_seconds = time.time()

    actor.sign_self_vp("user1.json", trans_vc_signed_vp)
    present_seconds_self_signed = time.time()

    print(f"自签名时间：{present_seconds_self_signed - present_seconds}")

def transborder_demo():
    ''' A demo transfer: 
    1. A user signs a VP about his VC
    2. The user ask provider to check the VP
    3. Provider checks the user's VP;
    4. If valid, starts the transborder request;



    '''
    '''
    用户Sign a verification presentation
    '''
    authorize_demo()

    '''
    Provider Create and Sign o-VC
    '''
    prov = Provider("user3.key")
    is_valid = prov.verify_vp_file("user1_signed_vp.json")
    if is_valid is False:
        return




    '''
    '''


    trans_vc_file = "trans0928.json"
    trans_vc_signed = "trans0928signed.json"
    trans_vc_signed_vp = "trans0928signed_vp.json"

    prov.create_trans_request("user3", "user4", trans_vc_file)


    '''
    Rule Judgment
    '''
    revw = Reviewer("user4.key")
    star_time = time.time()
    should_allow = revw.check_rules(trans_vc_file)
    if should_allow == Decision.REJECT:
        return
    end_time = time.time()
    elapsed_time = end_time - star_time
    print(f"规则判断时间：{elapsed_time}")


    '''
    Reviewer审核 o-VC 时间 Reviewer Verify o-VC
    '''
    revw.sign_file(trans_vc_file, trans_vc_signed)

    '''
    签发vp的时间 Reviewer Create and Sign o-VP
    '''
    revw.sign_transborder_vp("user4.json", trans_vc_signed, trans_vc_signed_vp)

    '''
    Transferor Verify o-VP
    '''
    it_person = Transferor()
    it_person.do_transfer(trans_vc_signed_vp)

def main():
    ''' Entrance '''
    transborder_demo()

if __name__ == "__main__":
    main()
