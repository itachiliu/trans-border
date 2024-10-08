
class CbprRegions:
    ' All regions listed on CBPR '
    all_regions = {}

    def __init__(self):
        arr = ["United States", "Canada", "Japan", "Republic of Korea",
                            "Philippines", "Singapore", "Taiwan"]
        for item in arr:
            itemu = item.upper()
            self.all_regions[itemu] = 1

    def find(self, regionname: str) -> bool:
        regionu = regionname.upper()
        return regionu in self.all_regions # Case in-sensitive

cbpr_list = CbprRegions()

def is_cbpr(region: str) -> bool:
    ' https://www.bsigroup.com/zh-CN/about-bsi/media-centre/press-releases/2021/december/--bsiapec/ '
    return cbpr_list.find(region)
