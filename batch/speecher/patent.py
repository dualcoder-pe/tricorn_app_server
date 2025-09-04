from law_range import patent_civil_range
from raw_info import get_default_law_info
from requester import *


def run(today):
    range_info = {"민법": patent_civil_range}

    law_info_list = get_default_law_info([
        "민법",
        "특허법",
        "상표법",
        "디자인보호법"
    ], range_info)
    # law_info = [
    #     {"name": "특허법", "id": "patent", "url": get_url_by_mst(244995), "range": {}},
    #     {
    #         "name": "상표법",
    #         "id": "trademark",
    #         "url": get_url_by_mst(244973),
    #         "range": {},
    #     },
    #     {
    #         "name": "민법",
    #         "id": "civil",
    #         "url": get_url_by_mst(246569),
    #         "range": patent_civil_range,
    #     },
    #     {
    #         "name": "디자인보호법",
    #         "id": "design",
    #         "url": get_url_by_mst(244971),
    #         "range": {},
    #     },
    # ]

    for info in law_info_list:
        fetch(f"output/{today}/patent", info)

    # fsPromises.readFile("data.xml", "utf-8").then(
    #     function(value) {
    #         parseString(value, function(err, result){
    #             const data = parseXml(result)
    #             fsPromises.writeFile("data.json", JSON.stringify(data))
    #         })
    #     }
    # )
