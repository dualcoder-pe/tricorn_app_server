import re


def parse_xml(source, law_range):
    law_name = source.find('.//법령명_한글').text.strip()
    history = f"[시행 {source.find('.//시행일자').text.strip()}] [법률 제 {source.find('.//공포번호').text.strip()}호, {source.find('.//시행일자').text.strip()}, {source.find('.//제개정구분').text.strip()}]"

    law_data = [{
        "type": "Law",
        "title": law_name,
        "history": history,
    }]

    all_include = len(law_range) == 0
    part_include = all_include or True
    chapter_include = all_include or True
    section_include = all_include or True

    part_index = -1
    chapter_index = -1
    section_index = -1

    for element in source.findall('.//조문단위'):
        text = element.find('.//조문내용').text.strip()
        row_type = get_type(text)
        row = {}

        if row_type:
            row["type"] = row_type

            if not all_include:
                # 편을 포함하는지 체크
                part_range = law_range["Part"]
                if row_type == "Part" and len(part_range) > 0:
                    part_index = int(get_type_index(text, row_type))
                    # print(f"{part_index}편 포함")

                    # 편을 포함할지 결정
                    part_include = False
                    for entry in part_range:
                        if list(entry.keys())[0] == part_index:
                            part_include = True
                            break

                # 편을 포함하지 않으면 skip
                if not part_include:
                    # print(f"{part_index}편 제외")
                    continue

                chapter_range = []
                for parts in part_range:
                    if list(parts.keys())[0] == part_index and "Chapter" in list(parts[part_index].keys()):
                        chapter_range = parts[part_index]["Chapter"]

                # 장을 포함하는지 체크
                if row_type == "Chapter" and len(chapter_range) > 0:
                    chapter_index = int(get_type_index(text, row_type))
                    # print(f"{part_index}편 {chapter_index}장")

                    # 장을 포함할지 결정
                    chapter_include = False
                    for entry in chapter_range:
                        if chapter_index == list(entry.keys())[0]:
                            chapter_include = True

                # 장을 포함하지 않으면 skip
                if not chapter_include:
                    # print(f"{part_index}편 {chapter_index}장 제외")
                    continue

                section_range = []
                for chapters in chapter_range:
                    if list(chapters.keys())[0] == chapter_index and "Section" in list(chapters[chapter_index].keys()):
                        section_range = chapters[chapter_index]["Section"]

                # 절을 포함하는지 체크
                if row_type == "Section" and len(section_range) > 0:
                    section_index = int(get_type_index(text, row_type))
                    # print(f"{part_index}편 {chapter_index}장 {section_index}절")

                    # 절을 포함할지 결정
                    section_include = False
                    for entry in section_range:
                        if section_index == list(entry.keys())[0]:
                            section_include = True

                # 절을 포함하지 않으면 skip
                if not section_include:
                    # print(f"{part_index}편 {chapter_index}장 {section_index}절 제외")
                    continue

            if row_type == "Part":
                row["title"] = remove_revision(text)
            elif row_type == "Chapter" or row_type == "Section":
                row["title"] = remove_revision(text)
            else:
                row["title"] = get_article_title(text)
                cleansing(row, get_article(text))

                if element.find('.//조문참고자료') is not None:
                    row["history"] = element.find('.//조문참고자료').text.strip().replace("\t", "").replace("\n", "")

                if element.find('.//항') is not None:
                    row["children"] = []
                    for paragraph in element.findall('.//항'):
                        new_paragraph = {}
                        if paragraph.find('.//항내용') is not None:
                            new_paragraph["type"] = "Paragraph"
                            src_text = paragraph.find('.//항내용').text.strip()
                            # 가독성을 위해 항은 숫자 뒤에 점 붙여줌
                            cleansing(new_paragraph, f"{src_text[0]}.{src_text[1:]}")

                        if paragraph.find('.//호') is not None:
                            new_paragraph["children"] = []
                            for subParagraph in paragraph.findall('.//호'):
                                new_sub_paragraph = {}
                                if subParagraph.find('.//호내용') is not None:
                                    new_sub_paragraph["type"] = "SubParagraph"
                                    cleansing(new_sub_paragraph, subParagraph.find('.//호내용').text.strip())

                                if subParagraph.find('.//목') is not None:
                                    new_sub_paragraph["children"] = []
                                    for clause in subParagraph.findall('.//목'):
                                        new_clause = {"type": "Clause"}
                                        cleansing(new_clause, clause.find('.//목내용').text.strip())
                                        new_sub_paragraph["children"].append(new_clause)

                                new_paragraph["children"].append(new_sub_paragraph)

                        row["children"].append(new_paragraph)

            law_data.append(row)

    return {
        "dataset": {
            "data": law_data,
        },
    }


def remove_revision(text):
    revision = get_revision(text)
    if revision:
        return text.replace(revision, "").strip()
    else:
        return text


def get_article_title(text):
    if ")" in text:
        return text[:text.index(")") + 1].replace("「", "").replace("」", "").strip()
    elif " 삭제" in text:
        return text[:text.index(" 삭제")].strip()
    elif "조" in text:
        return text[:text.index("조") + 1].strip()
    else:
        raise Exception("Failed to get article title")


def get_article(text):
    if ")" in text:
        return text[text.index(")") + 1:].strip()
    elif "삭제" in text:
        return "삭제"
    elif "조" in text:
        return text[text.index("조") + 1:].strip()
    else:
        raise Exception("Failed to get article")


def cleansing(obj, text):
    if text == "삭제":
        obj["content"] = text
        return

    revision = get_revision(text)
    if revision:
        content = text.replace(revision, "").strip()
    else:
        content = text

    if content:
        content = re.compile("[一-鿕]").sub('', content) \
            .replace("ㆍ", ", ") \
            .replace("\t", "") \
            .replace("\n", "") \
            .replace("\"", "") \
            .replace("「", "") \
            .replace("」", "") \
            .replace("</img>", "") \
            .replace("()", "") \
            .replace("      ", "\n") \
            .strip()
        obj["content"] = content

    if revision:
        obj["revision"] = re.compile("^<img.*").sub('', revision)


def get_revision(text):
    match = re.search(r'<.+?>', text)
    if match:
        return match.group()
    return ""


def get_type(text):
    str_without_numbers = re.sub(r'[0-9]', '', text)
    if str_without_numbers.startswith("제편"):
        return "Part"
    elif str_without_numbers.startswith("제장"):
        return "Chapter"
    elif str_without_numbers.startswith("제절"):
        return "Section"
    elif str_without_numbers.startswith("제조"):
        return "Article"
    else:
        return ""


def get_type_index(text, law_type):
    if law_type == "Part":
        return text[text.index("제") + 1:text.index("편")].strip()
    elif law_type == "Chapter":
        return text[text.index("제") + 1:text.index("장")].strip()
    elif law_type == "Section":
        return text[text.index("제") + 1:text.index("절")].strip()
    elif law_type == "Article":
        return text[text.index("제") + 1:text.index("조")].strip()
    else:
        return ""
