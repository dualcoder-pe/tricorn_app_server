from typing import Optional


default_law_info: dict = {
    # patent.py
    "특허법": {"id": "patent", "law_id": "001455"},
    "상표법": {"id": "trademark", "law_id": "001870"},
    "민법": {"id": "civil", "law_id": "001706"},
    "디자인보호법": {"id": "design", "law_id": "001871"},
    # judical.py
    "상법": {"id": "commercial", "law_id": "001702"},
    "민사집행법": {"id": "civil_execution", "law_id": "009290"},
    "민사소송법": {"id": "civil_procedure", "law_id": "001700"},
    "부동산등기법": {"id": "real_estimate", "law_id": "001697"},
    "헌법": {"id": "constitution", "law_id": "001444"},
    "공탁법": {"id": "deposit", "law_id": "001212"},
    "상업등기법": {"id": "commercial_registration", "law_id": "010503"},
    "가족관계등록법": {"id": "family_registration", "law_id": "010444"},
    "비송사건절차법": {"id": "non_contentious", "law_id": "001699"},
    "형법": {"id": "criminal", "law_id": "001692"},
    "형사소송법": {"id": "criminal_procedure", "law_id": "001671"},
    # labor.py
    "근로기준법": {"id": "standards", "law_id": "001872"},
    "파견법": {"id": "dispatch", "law_id": "000122"},
    "기간제법": {"id": "periodic", "law_id": "010356"},
    "산업안전보건법": {"id": "safety", "law_id": "001766"},
    "직업안정법": {"id": "security", "law_id": "001765"},
    "남녀고용평등법": {"id": "equal", "law_id": "000130"},
    "최저임금법": {"id": "minimum", "law_id": "000129"},
    "퇴직급여법": {"id": "retirement", "law_id": "009883"},
    "임금채권보장법": {"id": "wage", "law_id": "000128"},
    "근로복지기본법": {"id": "welfare", "law_id": "009252"},
    "외국인고용법": {"id": "foreign", "law_id": "009542"},
    "노동조합법": {"id": "union", "law_id": "000143"},
    "근로자참여법": {"id": "participation", "law_id": "000141"},
    "노동위원회법": {"id": "commission", "law_id": "000139"},
    "공무원노조법": {"id": "officials_union", "law_id": "009884"},
    "교원노조법": {"id": "teachers_union", "law_id": "001967"},
    "사회보장기본법": {"id": "social", "law_id": "000204"},
    "고용보험법": {"id": "employment_insurance", "law_id": "001761"},
    "산재보험법": {"id": "compensation", "law_id": "001760"},
    "국민연금법": {"id": "pension", "law_id": "001781"},
    "국민건강보험법": {"id": "health_insurance", "law_id": "001971"},
    "고용산재보험료징수법": {"id": "insurance_premium", "law_id": "009589"},
    "행정소송법": {
        "id": "administrative_procedure",
        "law_id": "001218",
    },
    "행정심판법": {"id": "administrative_appeals", "law_id": "001363"},
    # lawyer.py
    "행정법": {"id": "administrative", "law_id": "014041"},
    "국제거래법": {"id": "private_international", "law_id": "001236"},
    # realtor.py
    "주택임대차보호법": {"id": "juim", "law_id": "001248"},
    "집합건물법": {"id": "jiphop", "law_id": "001262"},
    "가등기담보법": {"id": "gadeungki", "law_id": "001257"},
    "부동산실명법": {"id": "silkwon", "law_id": "001178"},
    "상가임대차보호법": {"id": "sangim", "law_id": "009276"},
    # tax.py
    "국세기본법": {"id": "national", "law_id": "001586"},
    "법인세법": {"id": "corporate", "law_id": "001563"},
    "소득세법": {"id": "income", "law_id": "001565"},
    "부가가치세법": {"id": "vat", "law_id": "001571"},
    "국세징수법": {"id": "collection", "law_id": "001585"},
    "국제조세조정법": {"id": "international", "law_id": "000603"},
    "조세범처벌법": {"id": "crime", "law_id": "001583"},
    "상속세및증여세법": {"id": "inheritance", "law_id": "001561"},
    "개별소비세법": {"id": "excise", "law_id": "001570"},
    "지방세법": {"id": "local", "law_id": "001649"},
    "조세특례제한법": {"id": "registration", "law_id": "001584"},  # tax.py 기준 ID 사용
    # tax.py에서 이름이 다른 중복 ID 항목("상법-회사", "민법-총칙")은 기존 "상법", "민법"을 유지하므로 추가하지 않음
}


def get_default_law_info(name_list: list[str], range_info: dict) -> list[dict]:
    result_list = []
    for name in name_list:
        law_info = {"name": name}
        law_info.update(default_law_info[name])
        if name in range_info:
            law_info["range"] = range_info[name]
        else:
            law_info["range"] = {}
        result_list.append(law_info)
    return result_list
