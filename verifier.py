import asyncio
import json

import didkit

import fileoper
import transferor

class Verifier:
    ''' Verify a verification credential or a verification presentation. '''
    def __init__(self, keyfile):        
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline()
            f.close()
        self.did = didkit.key_to_did("key", self.key)

    def verify_vc_file(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            jo = json.load(f)
            f.close()
        
        jostr = json.dumps(jo)
        asyncio.run(self.verify_content(jostr))
    
    async def verify_content(self, content: str):
        result = await didkit.verify_credential(content, json.dumps({}))
        print(result)
        
    def verify_vp_file(self, filename):
        ''' Verify a credential presentation. If no error, start a transfer operation. '''
        print(f"Verifing {filename}...")

        with open(filename, "r", encoding="utf-8") as f:
            jo = json.load(f)
            f.close()
        
        jostr = json.dumps(jo)
        asyncio.run(self.verify_vp_content(jostr))
    
    async def verify_vp_content(self, content: str):
        ''' Using didkit method to verify VP '''

        result = await didkit.verify_presentation(content, json.dumps({}))

        resobj = json.loads(result)
        if len(resobj["errors"]) == 0:
            do_transfer(content)
        else:
            print("Verification failed!")

def do_transfer(content: str):
    runner = transferor.Transferor()
    runner.run(content)

def main():
    actor = Verifier("user2.key")
    #actor.verify_vp_file("../User/req1.json")
    #actor.verify_vp_file("../User/reqwithtrans.json")
    actor.verify_vp_file("../User/trans0901signed_vp.json")

if __name__ == "__main__":
    main()
