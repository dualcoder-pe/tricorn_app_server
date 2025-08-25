import unittest
from typing import Optional


def is_none_or_empty(value) -> bool:
    return value is None or value == ""


def safe_dict_value(data: dict, keys: list, default=None):
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data


def safe_int(num, default: Optional[int] = None):
    if num is not None:
        try:
            return int(num)
        except ValueError:
            return default
    else:
        return default


def split_list_params(param: Optional[str]) -> Optional[list[str]]:
    if is_none_or_empty(param):
        return None
    elif "," in param:
        return param.split(",")
    else:
        return [param]


def version_compare(x: str, y: str) -> int:
    """
    :param x: major.minor.patch
    :param y: major.minor.patch
    :return:
    -1 if x > y
    0 if x == y
    1 if x < y
    """
    x_list = x.split(".")
    y_list = y.split(".")

    for i in range(len(x_list)):
        if int(x_list[i]) > int(y_list[i]):
            return -1
        elif int(x_list[i]) < int(y_list[i]):
            return 1
    return 0


class OpUtilTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_safe_dict_value(self):
        value = dict()
        value["1"] = {"a": 1}
        self.assertEqual(safe_dict_value(value, ["1"]), {"a": 1}, 'incorrect safe_dict_value logic')
        self.assertEqual(safe_dict_value(value, ["1", "a"]), 1, 'incorrect safe_dict_value logic')
        self.assertEqual(safe_dict_value(value, ["2"]), None, 'incorrect safe_dict_value logic')
        self.assertEqual(safe_dict_value(value, ["2"], 1), 1, 'incorrect safe_dict_value logic')
        self.assertEqual(safe_dict_value(value, ["1", "b"]), None, 'incorrect safe_dict_value logic')
        self.assertEqual(safe_dict_value(value, ["1", "b"], "a"), "a", 'incorrect safe_dict_value logic')

    def test_safe_int_value(self):
        self.assertEqual(safe_int(1), 1, 'incorrect safe_int logic')
        self.assertEqual(safe_int(1, 2), 1, 'incorrect safe_int logic')
        self.assertEqual(safe_int(None), None, 'incorrect safe_int logic')
        self.assertEqual(safe_int(None, 2), 2, 'incorrect safe_int logic')
        self.assertEqual(safe_int("1"), 1, 'incorrect safe_int logic')
        self.assertEqual(safe_int("1", 2), 1, 'incorrect safe_int logic')
        self.assertEqual(safe_int(""), None, 'incorrect safe_int logic')
        self.assertEqual(safe_int("", 2), 2, 'incorrect safe_int logic')

    def test_version_compare(self):
        self.assertEqual(version_compare('1.0.0', '1.0.1'), 1, 'incorrect compare')
        self.assertEqual(version_compare('1.0.0', '0.9.9'), -1, 'incorrect compare')
        self.assertEqual(version_compare('1.0.0', '1.0.0'), 0, 'incorrect compare')
        self.assertEqual(version_compare('2.0.1', '1.0.1'), -1, 'incorrect compare')
        self.assertEqual(version_compare('1.0.9', '1.0.10'), 1, 'incorrect compare')
