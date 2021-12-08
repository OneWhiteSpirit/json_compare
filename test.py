from json.decoder import JSONDecodeError
from pathlib import Path
import unittest
from diff import TreeNode, main, create_tree_from_JSON, diff


class TestJSONCompare(unittest.TestCase):

    def setUp(self) -> None:
        global empty_file_path, file_a_path, file_b_path

        empty_file_path = str(Path('test_files/empty.json').absolute())
        file_a_path = str(Path('test_files/File-A.json').absolute())
        file_b_path = str(Path('test_files/File-B.json').absolute())

    def assertDifferent(self, expected: dict, actual: dict, expected_diffs: list):
        diffs = diff(create_tree_from_JSON(expected),
                     create_tree_from_JSON(actual))
        if not any(d in diffs.__str__() for d in expected_diffs):
            message = f"""Expected object {expected} and actual objects {actual} 
            should be considered equal, but the following differences 
            were reported: {diffs}"""
            self.fail(message)

    def assertNotDifferent(self, expected: dict, actual: dict):
        diffs = diff(create_tree_from_JSON(expected),
                     create_tree_from_JSON(actual))
        actual_output = diffs.__str__()
        if actual_output:
            message = f"""Expected object {expected} and actual objects {actual} 
            should be considered not equal, but the following differences 
            were reported: {diffs}"""
            self.fail(message)

    def assertTreeNodeDifferent(self, actual: TreeNode, expected_diffs: list):
        actual_output = actual.__str__()
        if not any(d in actual_output for d in expected_diffs):
            message = f"""Expected object {expected_diffs} and actual objects {actual_output} 
            should be considered equal, but not all differences 
            were matched"""
            self.fail(message)

    def assertTreeNodeNotDifferent(self, actual: TreeNode):
        actual_output = actual.__str__()
        if actual_output:
            message = f"""Actual objects {actual_output} 
            should be empty, but it is not"""
            self.fail(message)

    def test_not_valid_args(self):
        self.assertRaises(RuntimeError, main, [])
        self.assertRaises(SystemExit, main, [""])
        self.assertRaises(SystemExit, main, ["not_valid_path"])
        self.assertRaises(SystemExit, main, [file_a_path])

    def test_no_valid_path(self):
        test_path = "not_valid_path"
        self.assertRaises(FileNotFoundError, main,
                          [file_a_path, test_path])
        self.assertRaises(FileNotFoundError, main,
                          [test_path, file_b_path])

    def test_empty_json(self):
        self.assertRaises(JSONDecodeError, main, [
                          empty_file_path, file_b_path])
        self.assertRaises(JSONDecodeError, main, [
                          file_a_path, empty_file_path])

    def test_json(self):
        self.assertTreeNodeDifferent(
            main([file_a_path, file_b_path]),
            [
                '\'firstName\' - (Deleted)',
                '\'John\' - (Deleted)',
                'True - (Deleted)',
                'False - (Inserted)',
                '\'age\' - (Deleted)',
                '27 - (Deleted)',
                '\'New York\' - (Deleted)',
                '\'Chicago\' - (Inserted)',
                '\'NY\' - (Deleted)',
                '\'IL\' - (Inserted)',
                '\'postalCode\' - (Deleted)',
                '\'10021-3100\' - (Deleted)',
                '\'Age\' - (Inserted)',
                '27 - (Inserted)',
                '\'first_name\' - (Inserted)',
                '\'Alex\' - (Inserted)'
            ]
        )

        equal_a_path = str(Path('test_files/Equal-A.json').absolute())
        equal_b_path = str(Path('test_files/Equal-B.json').absolute())
        self.assertTreeNodeNotDifferent(
            main([equal_a_path, equal_b_path])
        )

    def test_trivial_equal(self):
        self.assertNotDifferent(dict(val=42), dict(val=42))

    def test_equal_trees(self):
        self.assertNotDifferent({'foo': ['bar', 3, 1.2], 'bipples': None}, {
                                'foo': ['bar', 3, 1.2], 'bipples': None})

    def test_unequal_trees(self):
        self.assertDifferent(
            dict(a=1, b=[dict(x=10, y=11)]),
            dict(a=1, b=[dict(x=10, z=11)]),
            ['\'y\' - (Deleted)', '11 - (Deleted)',
             '\'z\' - (Inserted)', '11 - (Inserted)'],
        )

    def test_unequal_trees_longer_expected(self):
        self.assertDifferent(
            dict(a=1, b=[dict(x=10, y=11, z=12)]),
            dict(a=1, b=[dict(x=10, y=11)]),
            ['\'z\' - (Deleted)', '12 - (Deleted)'],
        )

    def test_unequal_trees_longer_actual(self):
        self.assertDifferent(
            dict(a=1, b=[dict(x=10, y=11)]),
            dict(a=1, b=[dict(x=10, y=11, z=12)]),
            ['\'z\' - (Inserted)', '12 - (Inserted)'],
        )


if __name__ == '__main__':
    unittest.main(exit=False)
