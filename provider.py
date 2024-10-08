import asyncio
import json
from datetime import datetime, timezone

import didkit

import fileoper
import transettings

from simplevdr import get_user_id

class Provider:
    ''' Sign user's transborder VC'''
    
    def __init__(self, keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline()
            f.close()
        self.did = didkit.key_to_did("key", self.key)
        self.is_valid = False

    def create_trans_request(self, receiver: str, approver1: str, outfile: str):
        ''' create a transfer request json file. outfile: transfer json. '''
        
        # sender: str, receiver: str, approver1: str
        send_did = get_user_id(receiver)
        receiver_did = self.did
        approv_did = get_user_id(approver1)
        settings = transettings.create_demo_setting(send_did, receiver_did, approv_did)
        
        asyncio.run(self.fill_trans_req(settings, outfile))
        print(f'VC File {outfile} generated.')

    async def fill_trans_req(self, trans: transettings.TranSettings, outfile: str):
        ''' Sign a verification credential. outfile: transfer VC. '''

        issuance_date = datetime.now().replace(microsecond=0)

        credential = {
            "id": "http://example.org/credentials/transborder",
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            "type": ["VerifiableCredential", "OperCredential"],
            "issuer": trans.approver,
            "issuanceDate": issuance_date.isoformat() + "Z",
            "expirationDate": trans.expirationTime,
            "credentialSubject": {
                "@context": [{"userName": "https://schema.org/Text"},
                    {"transferTime": "https://schema.org/Text"},
                    {"origArea": "https://schema.org/Text"},
                    {"destArea": "https://schema.org/Text"},
                    {"dataType": "https://schema.org/Text"},
                    {"dataVolume": "https://schema.org/Text"},
                    {"dataUnit": "https://schema.org/Text"},
                    {"dataHash": "https://schema.org/Text"},
                    {"reason": "https://schema.org/Text"},
                    {"approverInfo": "https://schema.org/Text"},
                    {"receiver": "https://schema.org/Text"},
                    {"receiverKey": "https://schema.org/Text"},
                    {"transferId": "https://schema.org/Text"}],
                "id": self.did,
                "userName": trans.senderId,
                "transferTime": trans.expectTime,
                "origArea": trans.origArea,
                "destArea": trans.destArea,
                "dataType": trans.dataType,
                "dataVolume": trans.dataVolume,
                "dataUnit": trans.dataUnit,
                "dataHash": trans.dataHash, 
                "reason": trans.reason,
                "approverInfo": trans.approver,
                "receiver": trans.receiverId,
                "receiverKey": trans.receiverKey,
                "transferId": trans.ticketId
            },
        }

        credstr = json.dumps(credential)
        fileoper.write_text_file(outfile, credstr)

    def verify_vp_file(self, filename) -> bool:
        ''' Verify a credential presentation. If no error, start a transfer operation. '''
        print(f"Verifing {filename}...")

        with open(filename, "r", encoding="utf-8") as f:
            jo = json.load(f)
            f.close()
        
        jostr = json.dumps(jo)
        asyncio.run(self.verify_vp_content(jostr))

        return self.is_valid
    
    async def verify_vp_content(self, content: str):
        ''' Using didkit method to verify VP '''

        result = await didkit.verify_presentation(content, json.dumps({}))

        resobj = json.loads(result)
        if len(resobj["errors"]) == 0:
            #do_transfer(content)
            self.is_valid = True
        else:
            print("Verification failed!")
            self.is_valid = False
