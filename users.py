import asyncio
import time

import didkit
import fileoper
import issuer

class Users:
    """ Create several users."""

    def issuer_batch_oper(self, usernum: int):
        self.issuer1 = issuer.Issuer("key.jwk")
        print("Issuer: " + self.issuer1.did)

        self.create_users_batch(usernum)

    def create_users_batch(self, usernum: int):
        for i in range(usernum):
            keyx = didkit.generate_ed25519_key()            
            username = f"user{i}"
            fname = username + ".key"
            userjson = username + ".json"
            fileoper.write_text_file(fname, keyx)
            self.issuer1.sign_user(username, keyx, userjson)
            #asyncio.run(self.sign_user(username, keyx, userjson))
            time.sleep(2)
            
        print(f"{usernum} users created.")
        self.issuer1.save_users("allusers.json")

def main():
    us = Users()
    us.issuer_batch_oper(5)

if __name__ == "__main__":
    main()
