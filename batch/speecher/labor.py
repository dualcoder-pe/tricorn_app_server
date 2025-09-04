from law_range import *
from raw_info import get_default_law_info
from requester import fetch


def run(today):
    range_info = {"민법": labor_civil_range}
    law_info = get_default_law_info([
        "근로기준법",
        "파견법",
        "기간제법",
        "산업안전보건법",
        "직업안정법",
        "남녀고용평등법",
        "최저임금법",
        "퇴직급여법",
        "임금채권보장법",
        "근로복지기본법",
        "외국인고용법",
        "노동조합법",
        "근로자참여법",
        "노동위원회법",
        "공무원노조법",
        "교원노조법",
        "민법",
        "사회보장기본법",
        "고용보험법",
        "산재보험법",
        "국민연금법",
        "국민건강보험법",
        "고용산재보험료징수법",
        "행정소송법",
        "행정심판법",
        "민사소송법",
    ], range_info)
    # law_info = [
    #     {"name": "근로기준법", "id": "standards", "url": get_url_by_mst(232199), "range": {}},
    #     {"name": "파견법", "id": "dispatch", "url": get_url_by_mst(223983), "range": {}},
    #     {"name": "기간제법", "id": "periodic", "url": get_url_by_mst(232201), "range": {}},
    #     {"name": "산업안전보건법", "id": "safety", "url": get_url_by_mst(234717), "range": {}},
    #     {"name": "직업안정법", "id": "security", "url": get_url_by_mst(234805), "range": {}},
    #     {"name": "남녀고용평등법", "id": "equal", "url": get_url_by_mst(232225), "range": {}},
    #     {"name": "최저임금법", "id": "minimum", "url": get_url_by_mst(218303), "range": {}},
    #     {"name": "퇴직급여법", "id": "retirement", "url": get_url_by_mst(239311), "range": {}},
    #     {"name": "임금채권보장법", "id": "wage", "url": get_url_by_mst(231379), "range": {}},
    #     {
    #         "name": "근로복지기본법",
    #         "id": "welfare",
    #         "url": get_url_by_mst(243061),
    #         "range": {},
    #     },
    #     {"name": "외국인고용법", "id": "foreign", "url": get_url_by_mst(243065), "range": {}},
    #     {"name": "노동조합법", "id": "union", "url": get_url_by_mst(228175), "range": {}},
    #     {
    #         "name": "근로자참여법",
    #         "id": "participation",
    #         "url": get_url_by_mst(243063),
    #         "range": {},
    #     },
    #     {
    #         "name": "노동위원회법",
    #         "id": "commission",
    #         "url": get_url_by_mst(232203),
    #         "range": {},
    #     },
    #     {
    #         "name": "공무원노조법",
    #         "id": "officials_union",
    #         "url": get_url_by_mst(228167),
    #         "range": {},
    #     },
    #     {
    #         "name": "교원노조법",
    #         "id": "teachers_union",
    #         "url": get_url_by_mst(228169),
    #         "range": {},
    #     },
    #     {
    #         "name": "민법",
    #         "id": "civil",
    #         "url": get_url_by_mst(246569),
    #         "range": labor_civil_range,
    #     },
    #     {"name": "사회보장기본법", "id": "social", "url": get_url_by_mst(232647), "range": {}},
    #     {
    #         "name": "고용보험법",
    #         "id": "employment_insurance",
    #         "url": get_url_by_mst(247483),
    #         "range": {},
    #     },
    #     {
    #         "name": "산재보험법",
    #         "id": "compensation",
    #         "url": get_url_by_mst(243043),
    #         "range": {},
    #     },
    #     {"name": "국민연금법", "id": "pension", "url": get_url_by_mst(251711), "range": {}},
    #     {
    #         "name": "국민건강보험법",
    #         "id": "health_insurance",
    #         "url": get_url_by_mst(246841),
    #         "range": {},
    #     },
    #     {
    #         "name": "고용산재보험료징수법",
    #         "id": "insurance_premium",
    #         "url": get_url_by_mst(247481),
    #         "range": {},
    #     },
    #     {
    #         "name": "행정소송법",
    #         "id": "administrative_procedure",
    #         "url": get_url_by_mst(195052),
    #         "range": {},
    #     },
    #     {
    #         "name": "행정심판법",
    #         "id": "administrative_appeals",
    #         "url": get_url_by_mst(249041),
    #         "range": {},
    #     },
    #     {
    #         "name": "민사소송법",
    #         "id": "civil_procedure",
    #         "url": get_url_by_mst(223439),
    #         "range": {},
    #     },
    # ]

    for info in law_info:
        # print(f"\"{info['name']}\",")
        fetch(f"output/{today}/labor", info)

    # fsPromises.readFile("data.xml", "utf-8").then(
    #     function(value) {
    #         parseString(value, function(err, result){
    #             const data = parseXml(result)
    #             fsPromises.writeFile("data.json", JSON.stringify(data))
    #         })
    #     }
    # )
