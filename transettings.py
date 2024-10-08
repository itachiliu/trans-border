from datetime import datetime, timedelta, timezone
import uuid
import random
import time

class TranSettings:
    ''' Settings for a transborder request '''
    ticketId: str
    senderId: str
    receiverId: str
    receiverKey: str
    expectTime: str
    expirationTime: str
    origArea: str
    destArea: str
    dataType: str
    dataVolume: str
    dataUnit: str
    dataHash: str
    reason: str
    approver: str

    def check_expiration(self) -> bool:
        expiration = parse_datatime(self.expirationTime)
        cur_date = datetime.now()
        if cur_date > expiration:
            print(f'Transborder request {self.expirationTime} expired!')
            return False
        return True
    
    def from_vc(self, vcobj):
        self.senderId = vcobj["credentialSubject"]["userName"]
        self.receiverId = vcobj["credentialSubject"]["receiver"]
        self.receiverKey = vcobj["credentialSubject"]["receiverKey"]
        self.expectTime = vcobj["credentialSubject"]["transferTime"]
        self.expirationTime = vcobj["expirationDate"]
        self.origArea = vcobj["credentialSubject"]["origArea"]
        self.destArea = vcobj["credentialSubject"]["destArea"]
        self.dataType = vcobj["credentialSubject"]["dataType"]
        self.dataVolume = vcobj["credentialSubject"]["dataVolume"]
        self.dataUnit = vcobj["credentialSubject"]["dataUnit"]
        self.dataHash = vcobj["credentialSubject"]["dataHash"]
        self.reason = vcobj["credentialSubject"]["reason"]
        self.ticketId = vcobj["credentialSubject"]["transferId"]

    def print_info(self):
        print(f"{self.origArea} to {self.destArea}: {self.dataType} {self.reason} ({self.dataVolume} {self.dataUnit}) {self.ticketId}")

# "did:key:z6MkkGB18uq5uE7CpJ5UVVFkWoXwr8T7MLBM9GfL18UzG6GJ"
def create_demo_setting(sender: str, receiver: str, approver1: str) -> TranSettings:
    ''' Demo ticket '''
    print(f"DBG:Sender:{sender}, Rev: {receiver}, Approver:{approver1}")
    
    #issuance_date = datetime.now(timezone.utc).replace(microsecond=0)
    issuance_date = datetime.now().replace(microsecond=0)
    expiration_date = issuance_date + timedelta(weeks=2)
    expected_date = issuance_date + timedelta(weeks=1)
    
    settings = TranSettings()
    settings.ticketId = str(uuid.uuid1())
    settings.senderId = sender
    settings.receiverId = "Bob"
    settings.receiverKey = receiver
    settings.expectTime = expected_date.isoformat() + "Z"
    settings.expirationTime = expiration_date.isoformat() + "Z"
    settings.origArea = "Germany"
    settings.destArea = "Singapore"
    settings.dataType = "User Privacy"
    settings.dataVolume = "10000"
    settings.dataUnit = "person"
    settings.dataHash = "5usHGst9SANMEViiINEDrZ37UZY="
    settings.reason = "user consent"
    
    # IMPORTANT!
    settings.approver = approver1
    return settings

def parse_datatime(dtstr : str) -> datetime:
    '''
    2024-10-04T14:10:49Z ==> datetime format
    '''
    if dtstr == "":
        # invalid
        print(f"{dtstr} is invalid!")
        return datetime.date(1920,1,1)

    if dtstr.endswith("Z"):
        dtstr = dtstr[:len(dtstr)-1] # Remove last Z

    #print(f'[DBG] Parsed time: {dtstr}')
    return datetime.fromisoformat(dtstr)

def random_region() -> str:
    ' return a random region '
    all_regions = ["Germany", "Belgium", "France", "United Kingdom", 
                      "United States", "China", "Singapore", "India", "Vietnam",
                      "Hong Kong", "Macro", "Japan", "Canada"]
    total = len(all_regions)
    idx = random.randint(0, total-1)
    return all_regions[idx]

def random_reason() -> str:
    ' return a random reason '
    all_values = ["user consent", "Adequate level", "binding corporate rules", 
                      "standard contractual clauses", "code of conduct"]
    total = len(all_values)
    idx = random.randint(0, total-1)
    return all_values[idx]

class TransGenerator:
    def generate_settings(self, number: int):
        allsettings = []
        issuance_date = datetime.now().replace(microsecond=0)
        expiration_date = issuance_date + timedelta(weeks=2)
        expected_date = issuance_date + timedelta(weeks=1)

        i = 0
        while i < number:
            aset = TranSettings()
            aset.ticketId = str(uuid.uuid4())
            aset.senderId = "sender1" # Not important
            aset.receiverId = "Bob"
            aset.receiverKey = "receiver1" # Not important
            aset.expectTime = expected_date.isoformat() + "Z"
            aset.expirationTime = expiration_date.isoformat() + "Z"
            aset.origArea = random_region()
            aset.destArea = random_region()
            aset.dataType = "User Privacy"
            aset.dataVolume = "10000"
            aset.dataUnit = "person"
            aset.dataHash = "5usHGst9SANMEViiINEDrZ37UZY="
            aset.reason = random_reason()

            allsettings.append(aset)

            time.sleep(0.05) # for random functions
            i=i+1

        return allsettings
