
from enum import Enum
from propset import TransProps, OrgType
from cbpr import is_cbpr

class Region(Enum):
    ''' Different jurisdiction with different laws '''
    EEA = 1
    CHINA = 2
    INDIA = 3
    RUSSIA = 4
    SINGAPORE= 5
    VIETNAM = 6
    JAPAN = 7
    KOREA = 8
    HONGKONG = 9
    UK = 10
    USA = 11
    CANADA = 12
    MACRO = 14
    UNKNOWN = 100

def find_region(desc :str) -> Region:
    ''' Find the matched jurisdiction '''
    descl = str.lower(desc)
    res = Region.UNKNOWN
    match descl:
        case "austria" | "belgium" | "bulgaria" | "croatia" | "republic of cyprus":
            res =  Region.EEA
        case "czech republic" | "denmark" | "estonia" | "finland":
            res =  Region.EEA
        case "france" | "germany" | "greece" | "hungary" | "ireland":
            res =  Region.EEA
        case "italy" | "latvia" | "lithuania" | "luxembourg" | "malta":
            res =  Region.EEA
        case "netherlands" | "poland" | "portugal" | "romania" | "slovakia":
            res =  Region.EEA
        case "slovenia" | "spain" | "sweden":
            res =  Region.EEA
        case "iceland" | "liechtenstein" | "norway":
            # Not in EU, but in EEA
            res =  Region.EEA
        case "china":
            res =  Region.CHINA
        case "india":
            res =  Region.INDIA
        case "russia":
            res =  Region.RUSSIA
        case "singapore":
            res =  Region.SINGAPORE
        case "vietnam":
            res =  Region.VIETNAM
        case "japan":
            res =  Region.JAPAN
        case "canada":
            res =  Region.CANADA
        case "united kingdom" | "uk" | "the united kingdom":
            res =  Region.UK
        case "the united states" | "united states" | "usa":
            res =  Region.USA
        case "korea" | "republic of korea":
            res =  Region.KOREA
        case "hongkong" | "hong kong":
            res =  Region.HONGKONG
        case "macro" | "aomen":
            res =  Region.MACRO
        case _:
            res = Region.UNKNOWN
        
    #print(f"DBG: Region: {desc}, result: {res}")
    return res

class Decision(Enum):
    ''' Decision on trasfer request '''
    GO = 1
    REJECT = 2
    RISK = 3
    TBD = 4
    UNKNOWN = 100

class Rule:
    def check(self, req: TransProps) -> Decision:
        return Decision.TBD

class AllowRule(Rule):
    ' If matches then allow '

class DenyRule(Rule):
    ' If matches then deny '

class RiskRule(Rule):
    ' Not forbidded by law, but with concerns '

class Rules:
    allow_rules = []
    deny_rules = []
    risk_rules = []

    def add_allow(self, rl: Rule):
        self.allow_rules.append(rl)

    def add_deny(self, rl: Rule):
        self.deny_rules.append(rl)

    def add_risk(self, rl: Rule):
        self.risk_rules.append(rl)

    def judge(self, req: TransProps) -> Decision:
        ' Give a decision based on rules '
        for rl in self.deny_rules:
            res = rl.check(req)
            if res == Decision.REJECT:
                return Decision.REJECT

        for rl in self.allow_rules:
            res = rl.check(req)
            if res == Decision.GO:
                return Decision.GO
            if res == Decision.REJECT:
                print(f"Fobidden in an allow rule: {req.trans_props}")
                return Decision.REJECT

        for rl in self.risk_rules:
            res = rl.check(req)
            if res == Decision.RISK:
                return Decision.RISK
            if res == Decision.REJECT:
                print(f"Fobidden in a risk rule: {req.trans_props}")
                return Decision.REJECT
            if res == Decision.GO:
                print(f"Allowed in a risk rule: {req.trans_props}")
                return Decision.GO

        print(f"Ticket {req.trans_props.ticketId} cannot be decided automatically!")
        return Decision.TBD

class RuleChecker:
    ''' Check a transborder request and give a decision '''

    def judge(self, req: TransProps) -> Decision:
        ''' Check a transborder request and give a decision. True means allow. '''
        if req.trans_props.check_expiration() is False:
            return Decision.REJECT

        req.trans_props.print_info()
        des = Decision.TBD

        orig_region = find_region(req.trans_props.origArea)
        match orig_region:
            case Region.EEA:
                gdpr = GdprRules()
                des =  gdpr.judge(req)
            case Region.UK:
                gdpr = UkGdprRules()
                des =  gdpr.judge(req)
            case Region.CANADA:
                rl = CanadaRules()
                des =  rl.judge(req)
            case Region.USA:
                rl = UsaRules()
                des =  rl.judge(req)
            case Region.VIETNAM:
                rl = VietnamRules()
                des =  rl.judge(req)
            case Region.INDIA:
                rl = IndianRules()
                des =  rl.judge(req)
            case Region.CHINA:
                rl = ChinaRules()
                des =  rl.judge(req)
            case Region.JAPAN:
                rl = JapanRules()
                des =  rl.judge(req)
            case Region.SINGAPORE:
                rl = SingaporeRules()
                des =  rl.judge(req)
            case Region.MACRO:
                rl = MacroRules()
                des =  rl.judge(req)
            case _:
                # TODO implementation
                print(f"INFO: Cannot find checker for region: {req.trans_props.origArea}")

        print("---------------------")
        return des

class RuleSameRegion(AllowRule):
    def check(self, req: TransProps) -> Decision:
        dest_region = find_region(req.trans_props.destArea)
        orig_region = find_region(req.trans_props.origArea)

        if dest_region == orig_region:
            return Decision.GO
        return Decision.TBD

class RuleGdprAdequacy(AllowRule):
    def check(self, req: TransProps) -> Decision:
        ''' GDPR Article 45 '''
        descl = str.lower(req.trans_props.destArea)
        match descl:
            case "andorra" | "argentina" | "faroe islands" | "guernsey" | "israel" | "isle of man" | "japan":
                print(f"Ticket has valid adequacy: {req.trans_props.ticketId}")
                return Decision.GO
            case "jersey" | "new zealand" | "republic of korea" | "switzerland " | "the united kingdom" | "uruguay":
                print(f"Ticket has valid adequacy: {req.trans_props.ticketId}")
                return Decision.GO
            case "united kingdom":
                # alias
                print(f"Ticket has valid adequacy: {req.trans_props.ticketId}")
                return Decision.GO
            case "canada":
                return eu_to_canada(req)
            case "the united states" | "united states" | "usa":
                return eu_to_us(req)
            case _:
                print(f"Ticket out of adequacy: {req.trans_props.ticketId}")
                return Decision.TBD

class RuleGdprBcrs(AllowRule):
    def check(self, req: TransProps) -> Decision:
        ''' Binding corporate rules (Article 46) '''
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("bcrs") != -1:
            print(f"Ticket has valid BCRs: {req.trans_props.ticketId}")
            return Decision.GO
        if reasonl.find("binding corporate rules") != -1:
            print(f"Ticket has valid BCRs: {req.trans_props.ticketId}")
            return Decision.GO
        return Decision.TBD

class RuleGdprSCCs(AllowRule):
    def check(self, req: TransProps) -> Decision:
        ''' standard contractual clauses (Article 46) '''
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("sccs") != -1:
            print(f"Ticket has valid SCCs: {req.trans_props.ticketId}")
            return Decision.GO
        if reasonl.find("standard contractual clauses") != -1:
            print(f"Ticket has valid SCCs: {req.trans_props.ticketId}")
            return Decision.GO
        return Decision.TBD

class RuleGdprCoC(AllowRule):
    def check(self, req: TransProps) -> Decision:
        ''' an approved code of conduct pursuant to Article 40 '''
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("code of conduct") != -1:
            print(f"Ticket has valid CoC: {req.trans_props.ticketId}")
            return Decision.GO
        return Decision.TBD

class GdprRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_allow(RuleGdprAdequacy())
        self.add_allow(RuleGdprBcrs())
        self.add_allow(RuleGdprSCCs())
        self.add_allow(RuleGdprCoC())

def eu_to_canada(req: TransProps) -> Decision:
    ''' To Canada transborder '''
    print("EU to CA: Checking the type of organizations...")
    if hasattr(req, "sender_prop") is False:
        return Decision.TBD
    if hasattr(req, "receiver_prop") is False:
        return Decision.TBD

    org1 = find_org(req.sender_prop.org_type)
    org2 = find_org(req.receiver_prop.org_type)
    if org1 != OrgType.COMMERCIAL:
        return Decision.TBD
    if org2 != OrgType.COMMERCIAL:
        return Decision.TBD
    print(f"Go! Ticket within two commercial organizations: {req.trans_props.ticketId}")
    return Decision.GO

def eu_to_us(req: TransProps) -> Decision:
    ''' To US transborder '''
    print("EU to US: Checking the type of organizations...")
    if hasattr(req, "sender_prop") is False:
        return Decision.TBD
    if hasattr(req, "receiver_prop") is False:
        return Decision.TBD

    org1 = find_org(req.sender_prop.org_type)
    org2 = find_org(req.receiver_prop.org_type)
    if org1 != OrgType.COMMERCIAL:
        return Decision.TBD
    if org2 != OrgType.COMMERCIAL:
        return Decision.TBD

    reasonl = req.trans_props.reason.lower()
    if reasonl.find("safe harbor") != -1:
        # invalid on 2015 by EU court
        print(f"Ticket has an invalid reason (Safe Harbor): {req.trans_props.ticketId}")
        return Decision.TBD

    if reasonl.find("privacy shield") != -1:
        # invalid on 2020 by EU court
        print(f"Ticket has an invalid reason (privacy shield): {req.trans_props.ticketId}")
        return Decision.TBD

    if reasonl.find("data privacy framework") != -1:
        # Enable on 2023-07 by EU and USA
        print(f"Ticket has a valid reason (DPF): {req.trans_props.ticketId}")
        return Decision.GO

    return Decision.TBD

class UkGdprRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_allow(RuleUkGdprAdequacy())
        self.add_allow(RuleUkGdprBcrs())
        self.add_allow(RuleUkGdprSCCs())
        self.add_allow(RuleUkGdprCoC())

class RuleUkGdprAdequacy(AllowRule):
    eugdpr = RuleGdprAdequacy()
    def check(self, req: TransProps) -> Decision:
        dest = find_region(req.trans_props.destArea)
        if dest == Region.EEA:
            # UK and EEA
            return Decision.GO

        res = self.eugdpr.check(req)
        if res == Decision.GO:
            return Decision.GO
        
        descl = str.lower(req.trans_props.destArea)
        match descl:
            case "Gibraltar" | "korea":
                print(f"Ticket has valid adequacy: {req.trans_props.ticketId}")
                return Decision.GO
            case "canada":
                return uk_to_canada(req)
            case "the united states" | "united states" | "usa":
                return uk_to_us(req)
            case _:
                print(f"Ticket out of adequacy: {req.trans_props.ticketId}")
                return Decision.TBD

def uk_to_canada(req: TransProps) -> Decision:
    return eu_to_canada(req)

def uk_to_us(req: TransProps) -> Decision:
    return eu_to_us(req)

class RuleUkGdprBcrs(RuleGdprBcrs):
    ' Same as in EU '

class RuleUkGdprSCCs(AllowRule):
    def check(self, req: TransProps) -> Decision:
        ''' standard contractual clauses '''
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("sccs") != -1:
            print(f"Ticket has valid SCCs: {req.trans_props.ticketId}")
            return Decision.GO
        if reasonl.find("standard contractual clauses") != -1:
            print(f"Ticket has valid SCCs: {req.trans_props.ticketId}")
            return Decision.GO
        if reasonl.find("international data transfer agreement") != -1:
            print(f"Ticket has valid IDTAs: {req.trans_props.ticketId}")
            return Decision.GO
        return Decision.TBD
    
class RuleUkGdprCoC(RuleGdprCoC):
    ' Same as in EU '

class CanadaRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_risk(RuleCaOPC())

class RuleCaOPC(RiskRule):
    ' Rules by OPC (Canada) '   
    concern_regions = [Region.CHINA, Region.RUSSIA] # Only for DEMO

    def check(self, req: TransProps) -> Decision:
        dest = find_region(req.trans_props.destArea)
        if dest in self.concern_regions:
            # UK and EEA
            return Decision.RISK

class UsaRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_risk(RuleUsaFtc())

class RuleUsaFtc(RiskRule):
    ' Rules by FTC '   
    concern_regions = [Region.CHINA, Region.RUSSIA] # Only for DEMO

    def check(self, req: TransProps) -> Decision:
        dest = find_region(req.trans_props.destArea)
        if dest in self.concern_regions:
            # UK and EEA
            return Decision.RISK

class VietnamRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_allow(RuleVnLocalStorage())

class RuleLocalStorage(AllowRule):    
    def check(self, req: TransProps) -> Decision:
        ''' Several contries require local storage of personal data. 
         If fulfilled, transborder action can be permitted. '''
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("local storage") != -1:
            return Decision.GO
        return Decision.RISK

class RuleVnLocalStorage(RuleLocalStorage):
    ''' 53/2022/ND‑CP (local storage) '''

class RuleInLocalStorage(RuleLocalStorage):
    ''' Digital Personal Data Protection Act, 2023 (Article 40: local storage) '''

class IndianRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_allow(RuleInLocalStorage())
        self.add_deny(RuleInFinancial())
        self.add_deny(RuleInBlacklist())

class RuleInFinancial(DenyRule):
    def check(self, req: TransProps) -> Decision:
        desc = req.trans_props.dataType.lower()
        if desc.find("financial") != -1:
            return Decision.REJECT
        if desc.find("payment") != -1:
            return Decision.REJECT

class RuleInBlacklist(DenyRule):
    'Article 16 clause 1 of DPDP Act'
    def check(self, req: TransProps) -> Decision:
        'Article 16 clause 1'
        blacklist = [] # The banned regions' name
        if req.trans_props.destArea in blacklist:
            return Decision.REJECT
        return Decision.TBD

class SingaporeRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_allow(RuleSgInTransit())

        # Personal Data Protection Regulations, 2021, Article 26
        self.add_allow(RuleUserConcent())
        self.add_allow(RuleSgDpas())
        self.add_allow(RuleSgCoC())
        self.add_allow(RuleSgCerts())

class RuleInTransit(AllowRule):    
    def check(self, req: TransProps) -> Decision:
        ' From outside and to outside, no additional processing '
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("only transit") != -1:
            return Decision.GO
        return Decision.RISK

class RuleSgInTransit(RuleInTransit):
    ' Personal Data Protection Regulations, 2021, Article 10 '

class RuleUserConcent(AllowRule):    
    def check(self, req: TransProps) -> Decision:
        ' Several regions allow user concent as a valid reason'
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("user concent") != -1:
            return Decision.GO
        return Decision.RISK

class RuleSgDpas(AllowRule):    
    def check(self, req: TransProps) -> Decision:
        ' Personal Data Protection Regulations, 2021, Article 26 '
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("dpa") != -1:
            return Decision.GO
        if reasonl.find("data processing agreement") != -1:
            return Decision.GO
        return Decision.RISK

class RuleSgCoC(RuleGdprCoC):
    ' Same as in EU '

class RuleSgCerts(AllowRule):
    ' Personal Data Protection Regulations, 2021, Article 26. Should be changed to constraints '
    def check(self, req: TransProps) -> Decision:
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("apec cbpr") != -1:
            return Decision.GO
        if reasonl.find("apec prp") != -1:
            return Decision.GO
        return Decision.RISK

class ChinaRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_allow(RuleCnInTransit())
        self.add_allow(RuleCnFTZs())
        self.add_allow(RuleCnBusinessNeeds())
        self.add_allow(RuleCnNoPIIs())

        self.add_risk(RuleCnImportant())
        self.add_risk(RuleCnCIIs())
        self.add_risk(RuleCnNoCIIs())

class RuleCnInTransit(RuleInTransit):
    ' Facilitate and regulate regulations for cross-border data flows, March 2024, Article 4 '

class RuleCnNoPIIs(AllowRule):
    ' Facilitate and regulate regulations for cross-border data flows, March 2024, Article 3 '
    def check(self, req: TransProps) -> Decision:
        if is_pii(req.trans_props.dataType):
            return Decision.RISK
        if is_cn_important(req.trans_props.dataType):
            return Decision.RISK
        return Decision.GO

class RuleCnBusinessNeeds(AllowRule):
    ' Facilitate and regulate regulations for cross-border data flows, March 2024, Article 5 '
    def check(self, req: TransProps) -> Decision:
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("contract") != -1:
            return Decision.GO
        if reasonl.find("hr") != -1:
            return Decision.GO
        if reasonl.find("human resource") != -1:
            return Decision.GO
        if reasonl.find("emergency") != -1:
            return Decision.GO
        return Decision.TBD

class RuleCnFTZs(AllowRule):
    ' Facilitate and regulate regulations for cross-border data flows, March 2024, Article 6 '
    def check(self, req: TransProps) -> Decision:
        reasonl = req.trans_props.reason.lower()
        if reasonl.find("free trade zone") != -1:
            return Decision.GO
        if reasonl.find("ftz") != -1:
            return Decision.GO
        return Decision.TBD

class RuleCnImportant(RiskRule):
    ' Facilitate and regulate regulations for cross-border data flows, March 2024, Article 2 '
    def check(self, req: TransProps) -> Decision:
        if is_cn_important(req.trans_props.dataType):
            return Decision.RISK
        return Decision.TBD

class RuleCnCIIs(RiskRule):
    ' Facilitate and regulate regulations for cross-border data flows, March 2024, Article 7 '
    def check(self, req: TransProps) -> Decision:
        if hasattr(req, "receiver_org") is False:
            return Decision.TBD
        
        if req.receiver_org.org_type != OrgType.CII:
            return Decision.TBD
        
        if is_pii(req.trans_props.dataType) or is_cn_important(req.trans_props.dataType):
            if reason_security_assessment(req.trans_props.reason) is False:
                return Decision.REJECT
            else:
                # SHOULD review the assessment report
                return Decision.TBD
        
        return Decision.TBD

class RuleCnNoCIIs(RiskRule):
    ' Facilitate and regulate regulations for cross-border data flows, March 2024, Article 7 '
    ' Should be reviewed manually. '

def is_pii(datadesc: str) -> bool:
    desc = datadesc.lower()
    if desc.find("pii") != -1:
        return True
    if desc.find("personal") != -1:
        return True
    return False

def is_cn_important(datadesc: str) -> bool:
    desc = datadesc.lower()
    if desc.find("important") != -1:
        return True
    return False

def reason_security_assessment(reason: str) -> bool:
    reasonl = reason.lower()
    return reasonl.find("security assessment") != -1

class JapanRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_allow(RuleCBPR())

class RuleCBPR(AllowRule):
    ' Global Cross-Border Privacy Rules Declaration, Apr. 2022 '

    def check(self, req: TransProps) -> Decision:
        res = is_cbpr(req.trans_props.destArea)
        if res is True:
            return Decision.GO
        return Decision.TBD

class MacroRules(Rules):
    def __init__(self):
        self.add_allow(RuleSameRegion())
        self.add_allow(RuleGreaterBayArea())

class RuleGreaterBayArea(AllowRule):
    def check(self, req: TransProps) -> Decision:
        # TODO Agreements of Great Bay Area (Guangdong, Hong Kong and Macro)
        return Decision.TBD
