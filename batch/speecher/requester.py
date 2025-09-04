import os

import requests
import json
from xml.etree import ElementTree

from xml_parser import parse_xml


def get_url_by_mst(num):
    return f"https://www.law.go.kr/DRF/lawService.do?OC=dualcoder.pe&target=law&MST={num}&type=XML"


def get_url_by_id(num):
    return f"https://www.law.go.kr/DRF/lawService.do?OC=dualcoder.pe&target=law&ID={num}&type=XML"


def fetch(dir_path, info):
    """
    주어진 법률 정보(info)를 사용하여 법률 데이터를 요청하고 JSON 파일로 저장합니다.

    - law_id를 사용하여 법률 서비스 URL을 생성합니다.
    - 지정된 dir_path에 해당 법률의 id를 파일 이름으로 하는 JSON 파일이 이미 존재하면,
      네트워크 요청 및 파일 생성을 건너뜁니다.
    - 요청이 성공하면 XML 응답을 파싱하고 지정된 range에 따라 데이터를 처리합니다.
    - 처리된 데이터를 JSON 형식으로 파일에 저장합니다. 디렉토리가 없으면 생성합니다.
    - 요청이 실패하면 오류 메시지를 출력합니다.

    Args:
        dir_path (str): JSON 파일을 저장할 디렉토리 경로.
        info (dict): 처리할 법률 정보. 다음 키를 포함해야 합니다:
            - 'id' (str): 법률의 고유 ID (파일 이름으로 사용됨).
            - 'law_id' (str): 법률 서비스 API 요청에 사용될 법령 ID.
            - 'range' (dict): xml_parser.parse_xml 함수에 전달될 범위 정보.
    """
    file_path = f"{dir_path}/{info['id']}.json"

    # 파일이 이미 존재하는지 확인
    if os.path.exists(file_path):
        print(f"Skipping: File already exists at {file_path}")
        return  # 파일이 존재하면 함수 종료

    # law_id가 비어있는 경우 요청을 건너<0xEB><0x9A><0x8D>니다. (선택적: law_id가 채워질 때까지 실행 방지)
    if not info.get("law_id"):
        print(f"Skipping: law_id is missing for {info.get('name', info['id'])}")
        return

    url = get_url_by_id(info["law_id"])
    print(
        f"Requesting: {info.get('name', info['id'])} from {url}"
    )  # 어떤 법을 요청하는지 로그 추가
    res = requests.get(url)

    if res.status_code == 200:
        result = ElementTree.fromstring(res.content)
        data = parse_xml(result, info["range"])

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(file_path, "w") as f:
            json.dump(data, f, ensure_ascii=False)
    else:
        print(f"Failed to fetch data from {url}")
