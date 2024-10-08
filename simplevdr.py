import json

class SimpleVDR:
    def __init__(self, filename):
        with open(filename, "r") as f:
            self.all_users = json.load(f)
            f.close()
        print(f"Total {len(self.all_users)} users loaded.")

    def find_user(self, userkey: str):
        if len(userkey) == 0:
            return ""
        if userkey in self.all_users:
            return self.all_users[userkey]
        return None

    all_users: list

a_vdr = SimpleVDR("allusers.json")

def get_user_id(username: str) -> str:
    didval = a_vdr.find_user(username)
    if None is didval:
        return ""
    return didval
