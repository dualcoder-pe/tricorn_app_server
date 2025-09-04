from raw_info import get_default_law_info
from requester import *


def run(today):
    law_info = get_default_law_info([
        "헌법",
        "행정법",
        "민법",
        "민사소송법",
        "상법",
        "형법",
        "형사소송법",
        "국제거래법",
    ], {})
    # law_info = [
    #     {"name": "헌법", "id": "constitution", "url": get_url_by_mst(61603), "range": {}},
    #     {"name": "행정법", "id": "administrative", "url": get_url_by_mst(246871), "range": {}},
    #     {"name": "민법", "id": "civil", "url": get_url_by_mst(246569), "range": {}},
    #     {
    #         "name": "민사소송법",
    #         "id": "civil_procedure",
    #         "url": get_url_by_mst(223439),
    #         "range": {},
    #     },
    #     {"name": "상법", "id": "commercial", "url": get_url_by_mst(224883), "range": {}},
    #     {"name": "형법", "id": "criminal", "url": get_url_by_mst(223445), "range": {}},
    #     {
    #         "name": "형사소송법",
    #         "id": "criminal_procedure",
    #         "url": get_url_by_mst(242053),
    #         "range": {},
    #     },
    #     {
    #         "name": "국제거래법",
    #         "id": "private_international",
    #         "url": get_url_by_mst(238791),
    #         "range": {},
    #     },
    # ]

    for info in law_info:
        fetch(f"output/{today}/lawyer", info)

    # fsPromises.readFile("data.xml", "utf-8").then(
    #     function(value) {
    #         parseString(value, function(err, result){
    #             const data = parseXml(result)
    #             fsPromises.writeFile("data.json", JSON.stringify(data))
    #         })
    #     }
    # )