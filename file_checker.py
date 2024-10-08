import hashlib
import base64
import sys
from pathlib import Path

def hash_file(filename: str):
    ''' Hash a file, using BLAKE hash algorithm '''
    with open(filename, "rb") as f:
        content = f.read()
        f.close()
    h = hashlib.blake2b(digest_size=20)
    h.update(content)
    res = h.digest()

    base64_bytes = base64.b64encode(res) 
    base64_string = base64_bytes.decode("ascii")   
    print(f"Encoded Hash for file {filename}: {base64_string}")

def hash_file_sha256(filename: str):
    ''' Hash a file, using SHA256 algorithm '''
    with open(filename,"rb") as f:
        bytes1 = f.read() # read entire file as bytes
    readable_hash = hashlib.sha256(bytes1).hexdigest()
    print(readable_hash)
    
    base64_bytes = base64.b64encode(hashlib.sha256(bytes1).digest())
    base64_string = base64_bytes.decode("ascii")
    print(f"Encoded Hash for file {filename}: {base64_string}")

def hash_obj(content: str):
    ''' Hash a string, using BLAKE hash algorithm '''
    h = hashlib.blake2b(digest_size=20)
    h.update(content.encode('utf-8'))
    res = h.digest()
        
    base64_bytes = base64.b64encode(res) 
    base64_string = base64_bytes.decode("ascii")   
    print(f"Encoded string: {base64_string}")

def main():
    #hash_file("user2.json")
    #hash_file("1.jpg")
    if len(sys.argv) != 2:
        print("Usage: python file.py [filepath]")
        return
    fullpath = sys.argv[1]
    origfile = Path(fullpath)
    if origfile.exists:
        hash_file_sha256(fullpath)


if __name__ == "__main__":
    main()
