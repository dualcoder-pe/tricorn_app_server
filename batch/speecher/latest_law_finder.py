from logging import raiseExceptions

import requests

from raw_info import default_law_info

# 스크립트로 쓰인 파일.
# 법 이름이 실제 법 이름과 완벽하게 합치하지 않는 경우 검색 안됨.
def run():
    result = {}
    for name in default_law_info.keys():
        url = f"https://www.law.go.kr/DRF/lawSearch.do?OC=dualcoder.pe&target=law&type=JSON&query=\"{name}\""
        res = requests.get(url)
        need_check = False
        if res.status_code == 200:
            data = res.json()
            try:
                law_list = data["LawSearch"]["law"] if "law" in data["LawSearch"] else None

                if law_list is None:
                    url = f"https://www.law.go.kr/DRF/lawSearch.do?OC=dualcoder.pe&target=law&type=JSON&query={name}"
                    res = requests.get(url)
                    data = res.json()
                    law_list = data["LawSearch"]["law"] if "law" in data["LawSearch"] else None
                    if law_list is None:
                        raise Exception("Failed to get law list")
                    need_check = True

                if type(law_list) is list:
                    if len(law_list) < 0:
                        print(f"empty law list {name}")
                        print(data)
                    for law in law_list:
                        if "법령명한글" not in law:
                            print(f"{name} law problem \n {law} / {law_list} \n {data}")
                        if type(law) != dict:
                            print(f"{name} law problem \n {law} / {law_list} \n {data}")
                        if law["법령명한글"] == name:
                            result[name] = law["법령ID"]
                        elif need_check:
                            print(law)
                elif type(law_list) is dict:
                    law = law_list
                    if law["법령명한글"] == name:
                        result[name] = law["법령ID"]
                else:
                    print(f"law_list type problem {law_list}")
            except Exception as e:
                print(e)
                print(data)
    print(result)

if __name__ == "__main__":
    run()