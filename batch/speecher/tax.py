from raw_info import get_default_law_info
from requester import *
from law_range import *


def run(today):
    range_info = {
        "상법": tax_commercial_range,
        "민법": tax_civil_range,
    }
    law_info = get_default_law_info([
        "국세기본법",
        "법인세법",
        "소득세법",
        "부가가치세법",
        "국세징수법",
        "국제조세조정법",
        "조세범처벌법",
        "상법",
        "민법",
        "행정소송법",
        "상속세및증여세법",
        "개별소비세법",
        "지방세법",
        "조세특례제한법",
    ], range_info)
    # law_info = [
    #     {"name": "국세기본법", "id": "national", "url": get_url_by_mst(247433), "range": {}},
    #     {"name": "법인세법", "id": "corporate", "url": get_url_by_mst(247463), "range": {}},
    #     {"name": "소득세법", "id": "income", "url": get_url_by_mst(247467), "range": {}},
    #     {"name": "부가가치세법", "id": "vat", "url": get_url_by_mst(247465), "range": {}},
    #     {"name": "국세징수법", "id": "collection", "url": get_url_by_mst(248481), "range": {}},
    #     {
    #         "name": "국제조세조정법",
    #         "id": "international",
    #         "url": get_url_by_mst(247437),
    #         "range": {},
    #     },
    #     {"name": "조세범처벌법", "id": "crime", "url": get_url_by_mst(224875), "range": {}},
    #     {
    #         "name": "상법-회사",
    #         "id": "commercial",
    #         "url": get_url_by_mst(224883),
    #         "range": tax_commercial_range,
    #     },
    #     {
    #         "name": "민법-총칙",
    #         "id": "civil",
    #         "url": get_url_by_mst(246569),
    #         "range": tax_civil_range,
    #     },
    #     {
    #         "name": "행정소송법",
    #         "id": "administrative",
    #         "url": get_url_by_mst(195052),
    #         "range": {},
    #     },
    #     {
    #         "name": "상속세및증여세법",
    #         "id": "inheritance",
    #         "url": get_url_by_mst(247439),
    #         "range": {},
    #     },
    #     {"name": "개별소비세법", "id": "excise", "url": get_url_by_mst(247457), "range": {}},
    #     {"name": "지방세법", "id": "local", "url": get_url_by_mst(251647), "range": {}},
    #     {
    #         "name": "조세특례제한법",
    #         "id": "registration",
    #         "url": get_url_by_mst(251641),
    #         "range": {},
    #     },
    # ]

    for info in law_info:
        if info["name"] == "상법":
            info["name"] = "상법-회사"
        elif info["name"] == "민법":
            info["name"] = "민법-총칙"
        fetch(f"output/{today}/tax", info)

    # fsPromises.readFile("data.xml", "utf-8").then(
    #     function(value) {
    #         parseString(value, function(err, result){
    #             const data = parseXml(result)
    #             fsPromises.writeFile("data.json", JSON.stringify(data))
    #         })
    #     }
    # )
