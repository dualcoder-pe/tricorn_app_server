import unittest


def flat_map(func, lst):
    return [item for sublist in map(func, lst) for item in sublist]
    # print(type(lst))
    # print(type(lst[0]['brand']))
    # res = []
    # for sublist in values:
    #     for item in sublist:
    #         res.append(item)
    # return res


class FunctionalUtilTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_flat_map_logic(self):
        self.assertEqual(flat_map(lambda x: [x, x + 1], [1, 2, 3]), [1, 2, 2, 3, 3, 4], 'incorrect flat map logic')
