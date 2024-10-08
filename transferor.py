import json
import asyncio
from datetime import datetime
from enum import Enum

import didkit

class CredentialType(Enum):
    ''' Verification Credential Types '''
    USER = 1
    OPER = 2
    PRESENTATION = 3
    VERIFIABLE = 4
    UNKNOWN = 5

def getCredentialType(vc) -> CredentialType:
    arr = vc["type"]
    if len(arr) == 0:
        return CredentialType.UNKNOWN
    for item in arr:
        if item == "UserCredential":
            return CredentialType.USER
        elif item == "OperCredential":
            return CredentialType.OPER
        elif item == "VerifiablePresentation":
            return CredentialType.PRESENTATION
    return CredentialType.UNKNOWN

class Transferor:
    ''' Transfer files to receiver with the settings of a credential presentation. '''

    def __init__(self):
        self.vp_valid = False
        self.vp_content = ""
        pass

    def do_transfer(self, vpfile: str):
        res = self.verify_vp_file(vpfile)
        if res is False:
            return
        self.run(self.vp_content)

    def verify_vp_file(self, filename) -> bool:
        ''' Verify a credential presentation. If no error, start a transfer operation. '''
        print(f"Verifing {filename}...")

        with open(filename, "r", encoding="utf-8") as f:
            jo = json.load(f)
            f.close()
        
        jostr = json.dumps(jo)
        self.vp_content = jostr
        asyncio.run(self.verify_vp_content(jostr))

        return self.vp_valid
    
    async def verify_vp_content(self, content: str):
        ''' Using didkit method to verify VP '''

        result = await didkit.verify_presentation(content, json.dumps({}))

        resobj = json.loads(result)
        if len(resobj["errors"]) == 0:
            self.vp_valid = True
        else:
            print("Verification failed!")
            self.vp_valid = False

    def run(self, prensentation: str):
        ''' 
        Transfer files to receiver with the settings of a credential presentation. 
        Param: VP Content
        '''
        preobj = json.loads(prensentation)
        vcs = preobj['verifiableCredential']
        if len(vcs) == 0:
            print("[ERR] VP format error!")
            return

        oper_cred = {}

        for item in vcs:
            tp = getCredentialType(item)
            if tp == CredentialType.USER:
                valid_user = self.is_user_expired(item)
                if valid_user is False:
                    print("[ERR] Invalid user!")
                    return
            elif tp == CredentialType.OPER:
                valid_oper = self.verify_oper(item)
                if valid_oper is False:
                    print("[ERR] Invalid operation!")
                    return
                self.verify_oper(item)
                oper_cred = item

        self.start_transmission(oper_cred)

    def is_user_expired(self, user_cred) -> bool:
        ''' Verify an user based on his properties '''
        user_name = user_cred["credentialSubject"]["userName"]
        expire_str = user_cred["expirationDate"]
        if expire_str == "":
            # No Expiration
            return True

        if expire_str.endswith("Z"):
            expire_str = expire_str[:len(expire_str)-1] # Remove last Z

        print(f'Expiration time: {expire_str}')
        expire_date = datetime.fromisoformat(expire_str)
        cur_date = datetime.now()
        if cur_date > expire_date:
            print(f'user {user_name} expired!')
            return False
        return True

    def verify_oper(self, operCred) -> bool:
        ''' Verify an Operation Credential '''
        return True

    def start_transmission(self, operCred):
        print("Transmission started.")

def print_content(jsc):
    for key in jsc:
        v = jsc[key]
        print(f'Key: {key}: Val: {v}')
