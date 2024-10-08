import asyncio
import json

from datetime import datetime, timedelta

import didkit

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

    trans_vc_signed_vp = "user1_signed_vp.json"
    actor.sign_self_vp("user1.json", trans_vc_signed_vp)

def transborder_demo():
    ''' A demo transfer: 
    1. A user signs a VP about his VC
    2. The user ask provider to check the VP
    3. Provider checks the user's VP;
    4. If valid, starts the transborder request;
    '''
    authorize_demo()

    prov = Provider("user3.key")
    is_valid = prov.verify_vp_file("user1_signed_vp.json")
    if is_valid is False:
        return

    trans_vc_file = "trans0928.json"
    trans_vc_signed = "trans0928signed.json"
    trans_vc_signed_vp = "trans0928signed_vp.json"

    prov.create_trans_request("user3", "user4", trans_vc_file)

    revw = Reviewer("user4.key")

    should_allow = revw.check_rules(trans_vc_file)
    if should_allow == Decision.REJECT:
        return

    revw.sign_file(trans_vc_file, trans_vc_signed)
    revw.sign_transborder_vp("user4.json", trans_vc_signed, trans_vc_signed_vp)

    it_person = Transferor()
    it_person.do_transfer(trans_vc_signed_vp)

def main():
    ''' Entrance '''
    transborder_demo()

if __name__ == "__main__":
    main()
