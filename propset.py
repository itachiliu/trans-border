from enum import Enum
from transettings import TranSettings

class OrgType(Enum):
    ''' Organization '''
    COMMERCIAL = 1
    NGO = 2
    GOVERNMENT = 4
    CII = 8
    CONTROLLER = 16
    PROCESSOR = 32
    UNKNOWN = 100

def find_org(desc :str) -> OrgType:
    ''' Find the matched organization '''
    descl = str.lower(desc)
    match descl:
        case "no profit":
            return OrgType.NGO
        case "company" | "profit" | "commercial":
            return OrgType.COMMERCIAL
        case "government":
            return OrgType.GOVERNMENT

    if descl.find("cii") != -1:
        return OrgType.CII
    if descl.find("critical") != -1:
        return OrgType.CII
    
    if descl.find("controller") != -1:
        return OrgType.CONTROLLER
    if descl.find("processor") != -1:
        return OrgType.PROCESSOR
    return OrgType.UNKNOWN

class PropSet:
    pass

class UserPropSet(PropSet):
    user_location: str
    user_citizen: str

    def __init__(self, user_json):
        self.set_user(
            user_json["credentialSubject"]["userName"],
            user_json["credentialSubject"]["orgnization"]["name"],
            user_json["credentialSubject"]["orgnization"]["type"]
        )

    def set_location(self, loc: str):
        self.user_location = loc

    def set_citizen(self, v: str):
        self.user_citizen = v

    def set_user(self, name: str, org: str, orgtype: str):
        self.user_name = name
        self.user_org = org
        self.org_type = orgtype

class OrgPropSet:
    org_name: str
    org_desc: str
    org_type: OrgType

class SenderPropSet(UserPropSet):
    pass

class ReceiverPropSet(UserPropSet):
    pass

class SenderOrgPropSet(OrgPropSet):
    pass

class ReceiverOrgPropSet(OrgPropSet):
    pass

class TransDataPropSet(TranSettings):
    pass

class SenderConstraints:
    pass

class ReceiverConstraints:
    pass

class TransProps:
    ''' All properties of a transborder request '''
    sender_prop: SenderPropSet
    receiver_prop: ReceiverPropSet
    sender_org: OrgPropSet
    receiver_org: OrgPropSet

    def __init__(self, ts: TranSettings):
        self.trans_props = ts

    def set_sender_prop(self, user_json):
        self.sender_prop = SenderPropSet(user_json)

    def set_receiver_prop(self, user_json):
        self.receiver_prop = ReceiverPropSet(user_json)

    def set_sender_org(self, orgname: str, orgdesc: str):
        self.sender_org.org_name = orgname
        self.sender_org.org_desc = orgdesc
        self.sender_org.org_type = find_org(orgdesc)

    def set_receiver_org(self, orgname: str, orgdesc: str):
        self.receiver_org.org_name = orgname
        self.receiver_org.org_desc = orgdesc
        self.receiver_org.org_type = find_org(orgdesc)
