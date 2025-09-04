from raw_info import get_default_law_info
from requester import *
from law_range import realtor_civil_range


def run(today):
    range_info = {
        "민법": realtor_civil_range
    }
    law_info = get_default_law_info([
        "민법",
        "주택임대차보호법",
        "집합건물법",
        "가등기담보법",
        "부동산실명법",
        "상가임대차보호법",
    ], range_info)
    # law_info = [
    #     {
    #         "name": "민법",
    #         "id": "civil",
    #         "url": get_url_by_mst(246569),
    #         "range": realtor_civil_range,
    #     },
    #     {"name": "주택임대차보호법", "id": "juim", "url": get_url_by_mst(183533), "range": {}},
    #     {"name": "집합건물법", "id": "jiphop", "url": get_url_by_mst(179712), "range": {}},
    #     {
    #         "name": "가등기담보법",
    #         "id": "gadeungki",
    #         "url": get_url_by_mst(188538),
    #         "range": {},
    #     },
    #     {"name": "부동산실명법", "id": "silkwon", "url": get_url_by_mst(178980), "range": {}},
    #     {"name": "상가임대차보호법", "id": "sangim", "url": get_url_by_mst(183687), "range": {}},
    # ]

    for info in law_info:
        fetch(f"output/{today}/realtor", info)
