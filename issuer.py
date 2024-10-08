import asyncio
import json
import time
from datetime import datetime, timedelta, timezone

import didkit
import fileoper

class Issuer:
    """Issuer representing an issuer who can manage users."""

    def __init__(self, keyfile):        
        with open(keyfile, "r", encoding="utf-8") as f:
            self.key = f.readline()
            f.close()
        self.did = didkit.key_to_did("key", self.key)
        self.allusers = dict()

    def create_users_batch(self, usernum: int):
        for i in range(usernum):
            keyx = didkit.generate_ed25519_key()            
            username = f"user{i}"
            fname = username + ".key"
            userjson = username + ".json"
            fileoper.write_text_file(fname, keyx)
            asyncio.run(self.sign_user(username, keyx, userjson))
            time.sleep(2)
            
        print(f"{usernum} users created.")

    def sign_user(self, username: str, userkey: str, outfile: str):
        asyncio.run(self.sign_a_user(username, userkey, outfile))

    async def sign_a_user(self, username: str, userkey: str, outfile: str):
        user_did = didkit.key_to_did("key", userkey)
        verification_method = await didkit.key_to_verification_method("key", self.key)
        issuance_date = datetime.now().replace(microsecond=0)
        expiration_date = issuance_date + timedelta(weeks=24)

        credential = {
            "id": "http://example.org/credentials/user",
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1",
            ],
            "type": ["VerifiableCredential", "UserCredential"],
            "issuer": self.did,
            "issuanceDate": issuance_date.isoformat() + "Z",
            "expirationDate": expiration_date.isoformat() + "Z",
            "credentialSubject": {
                "@context": [{"userName": "https://schema.org/Text"},{"orgnization": "https://schema.org/Org"}],
                "id": user_did,
                "userName": username,
                "orgnization": {
                    "type": "No profit",
                    "name": "Example.Org"
                }
            },
        }
        
        # add user
        self.allusers[username] = user_did

        didkit_options = {
            "proofPurpose": "assertionMethod",
            "verificationMethod": verification_method,
        }

        signed_credential = await didkit.issue_credential(
            str(credential).replace("'", '"'),
            str(didkit_options).replace("'", '"'),
            self.key,
        )
        fileoper.write_text_file(outfile, signed_credential)
        
    def save_users(self, outfilename: str):
        ''' Convert and write JSON object to file '''
        with open(outfilename, "w") as fobj: 
            json.dump(self.allusers, fobj)
