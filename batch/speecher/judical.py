from raw_info import get_default_law_info
from requester import *


def run(today):
    law_info = get_default_law_info([
        "민법",
        "상법",
        "민사집행법",
        "민사소송법",
        "부동산등기법",
        "헌법",
        "공탁법",
        "상업등기법",
        "가족관계등록법",
        "비송사건절차법",
        "형법",
        "형사소송법",
    ], {})
    # law_info = [
    #     {"name": "민법", "id": "civil", "url": get_url_by_mst(246569), "range": {}},
    #     {
    #         "name": "상법",
    #         "id": "commercial",
    #         "url": get_url_by_mst(224883),
    #         "range": {},
    #     },
    #     {
    #         "name": "민사집행법",
    #         "id": "civil_execution",
    #         "url": get_url_by_mst(238793),
    #         "range": {},
    #     },
    #     {
    #         "name": "민사소송법",
    #         "id": "civil_procedure",
    #         "url": get_url_by_mst(223439),
    #         "range": {},
    #     },
    #     {
    #         "name": "부동산등기법",
    #         "id": "real_estimate",
    #         "url": get_url_by_mst(213783),
    #         "range": {},
    #     },
    #     {
    #         "name": "헌법",
    #         "id": "constitution",
    #         "url": get_url_by_mst(61603),
    #         "range": {},
    #     },
    #     {"name": "공탁법", "id": "deposit", "url": get_url_by_mst(223437), "range": {}},
    #     {
    #         "name": "상업등기법",
    #         "id": "commercial_registration",
    #         "url": get_url_by_mst(218961),
    #         "range": {},
    #     },
    #     {
    #         "name": "가족관계등록법",
    #         "id": "family_registration",
    #         "url": get_url_by_mst(238211),
    #         "range": {},
    #     },
    #     {
    #         "name": "비송사건절차법",
    #         "id": "non_contentious",
    #         "url": get_url_by_mst(213789),
    #         "range": {},
    #     },
    #     {"name": "형법", "id": "criminal", "url": get_url_by_mst(223445), "range": {}},
    #     {
    #         "name": "형사소송법",
    #         "id": "criminal_procedure",
    #         "url": get_url_by_mst(242053),
    #         "range": {},
    #     },
    # ]

    for info in law_info:
        fetch(f"output/{today}/judical", info)

    # fsPromises.readFile("data.xml", "utf-8").then(
    #     function(value) {
    #         parseString(value, function(err, result){
    #             const data = parseXml(result)
    #             fsPromises.writeFile("data.json", JSON.stringify(data))
    #         })
    #     }
    # )