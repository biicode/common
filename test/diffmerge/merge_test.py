import unittest
from biicode.common.model.renames import Renames
from biicode.common.model.brl.cell_name import CellName
from biicode.common.diffmerge.merge import SetThreeWayMerge
from biicode.common.diffmerge.text_merge import three_way_merge_text
from nose_parameterized import parameterized
import itertools
from biicode.common.output_stream import OutputStream


class SetThreeWayMergeText(SetThreeWayMerge):
    '''Merge elements str '''

    def merge_elements(self, common, base, other):
        """Must return a tuple with:
          1. the merge of el1 and el2
          2. If there was a conflict in merge"""
        if common is None:
            common = ""
        return three_way_merge_text(common, base, other, self.base_name, self.other_name)


class MergeTest(unittest.TestCase):

    def setUp(self):
        self.common = {"file1.h": "Content of file1.h\n",
                       "file2.h": "Content of file2.h\n",
                       "file3.h": "Content of file3.h\n",
                       "file4.h": "Content of file4.h\n"
                       }
        self._biiout = OutputStream()
        self.merger = SetThreeWayMergeText(base_name="base", other_name="other",
                                           biiout=self._biiout)

    @parameterized.expand(
        list(itertools.product(*[['delete', 'create', 'modify'],
                                 [True, False]]))
    )
    def test_simple_ff(self, action, use_other):
        base_resources = self.common.copy()
        other_resources = self.common.copy()
        if action == 'delete':
            base_resources.pop("file3.h")
        elif action == 'modify':
            base_resources['file1.h'] = 'Updated file1.h\n'
        else:
            base_resources['filenew.h'] = 'New file\n'
        if use_other:
            base_resources, other_resources = other_resources, base_resources

        ret = self.merger.merge(base_resources, other_resources, self.common)
        if use_other:
            self.assertNotEqual(base_resources, ret)
            self.assertEqual(other_resources, ret)
        else:
            self.assertEqual(base_resources, ret)
            self.assertNotEqual(other_resources, ret)
        self.assertNotIn("CONFLICT", str(self._biiout))

    @parameterized.expand(
        [('delete',), ('create',), ('modify',)]
    )
    def test_double_ff(self, action):
        '''The same change in both base and other'''
        base_resources = self.common.copy()
        if action == 'delete':
            base_resources.pop("file3.h")
        elif action == 'modify':
            base_resources['file1.h'] = 'Updated file1.h\n'
        else:
            base_resources['filenew.h'] = 'New file\n'
        other_resources = base_resources.copy()
        ret = self.merger.merge(base_resources, other_resources, self.common)
        self.assertEqual(base_resources, ret)
        self.assertEqual(other_resources, ret)
        self.assertNotIn("CONFLICT", str(self._biiout))

    @parameterized.expand(
        [(True,), (False,)]
    )
    def test_multi_ff(self, use_other):
        '''The same change in both base and other'''
        base_resources = self.common.copy()
        other_resources = base_resources.copy()

        base_resources.pop("file3.h")
        base_resources['file1.h'] = 'Updated file1.h\n'
        base_resources['filenew.h'] = 'New file\n'

        if use_other:
            base_resources, other_resources = other_resources, base_resources

        ret = self.merger.merge(base_resources, other_resources, self.common)
        if use_other:
            self.assertNotEqual(base_resources, ret)
            self.assertEqual(other_resources, ret)
        else:
            self.assertEqual(base_resources, ret)
            self.assertNotEqual(other_resources, ret)
        self.assertNotIn("CONFLICT", str(self._biiout))

    @parameterized.expand(
        [(True,), (False,)]
    )
    def test_mixed_ff(self, use_other):
        '''The same change in both base and other'''
        base_resources = self.common.copy()
        other_resources = base_resources.copy()

        base_resources.pop("file3.h")
        base_resources['file1.h'] = 'Updated file1.h\n'
        base_resources['filenew.h'] = 'New file\n'

        other_resources['filenew2.h'] = "New file 2\n"
        other_resources['file2.h'] = 'Updated file2.h\n'

        result = base_resources.copy()
        result['filenew2.h'] = "New file 2\n"
        result['file2.h'] = 'Updated file2.h\n'

        if use_other:
            base_resources, other_resources = other_resources, base_resources

        ret = self.merger.merge(base_resources, other_resources, self.common)

        self.assertEqual(result, ret)
        self.assertNotIn("CONFLICT", str(self._biiout))

    @parameterized.expand(
        list(itertools.product(*[['delete', 'modify'],
                                 [True, False]]))
    )
    def test_simple_modify_conflict(self, action, use_other):
        base_resources = self.common.copy()
        other_resources = self.common.copy()
        base_resources['file1.h'] = 'Updated file1.h\n'
        base_resources.pop('file2.h')
        base_resources['filenew.h'] = 'New file\n'
        result = base_resources.copy()

        if action == 'delete':
            other_resources.pop("file1.h")
            result['file1.h'] = 'Updated file1.h\n'
        else:
            other_resources['file1.h'] = 'Updated file12.h\n'
            if not use_other:
                result['file1.h'] = '<<<<<<<<<<<<<<<<<<<<<<<<< base\n' \
                                'Updated file1.h\n\n'            \
                                '=========================\n'       \
                                'Updated file12.h\n\n'             \
                                '>>>>>>>>>>>>>>>>>>>>>>>>> other\n'
            else:
                result['file1.h'] = '<<<<<<<<<<<<<<<<<<<<<<<<< base\n' \
                                'Updated file12.h\n\n'            \
                                '=========================\n'       \
                                'Updated file1.h\n\n'             \
                                '>>>>>>>>>>>>>>>>>>>>>>>>> other\n'
        if use_other:
            base_resources, other_resources = other_resources, base_resources

        ret = self.merger.merge(base_resources, other_resources, self.common)
        self.assertEqual(result, ret)
        self.assertIn("CONFLICT", str(self._biiout))

    def test_create_conflict(self):
        base_resources = self.common.copy()
        other_resources = self.common.copy()

        base_resources['file1.h'] = 'Updated file1.h'
        base_resources["fileNew.h"] = "pipiriripipi"

        other_resources['file1.h'] = 'Updated file12.h'
        other_resources["fileNew.h"] = "New cool file2"

        ret = self.merger.merge(base_resources, other_resources, self.common)
        self.assertNotEqual(base_resources, ret)
        self.assertNotEqual(other_resources, ret)
        self.assertIn("CONFLICT", str(self._biiout))
        self.assertTrue("<<<<<<<" in ret["fileNew.h"] and \
                        "New cool file2" in ret["fileNew.h"] and \
                        "pipiriripipi" in ret["fileNew.h"])
        self.assertTrue("<<<<<<<" in ret["file1.h"] and \
                        "Updated file1.h" in ret["file1.h"] and \
                        "Updated file12.h" in ret["file1.h"])

    def test_conflict_resolved_ok(self):

        base_resources = self.common.copy()
        other_resources = self.common.copy()

        base_resources['file1.h'] = "Content of file1.h\nAdded At End\n"
        other_resources['file1.h'] = 'Added at begining\nContent of file1.h\n'

        ret = self.merger.merge(base_resources, other_resources, self.common)
        self.assertNotEqual(base_resources, ret)
        self.assertNotEqual(other_resources, ret)
        self.assertNotIn("CONFLICT", str(self._biiout))
        self.assertEqual("Added at begining\nContent of file1.h\nAdded At End\n", ret['file1.h'])

    @parameterized.expand(
        list(itertools.product(*[['delete', 'modify'],
                                 [True, False]]))
    )
    def test_rename_no_change(self, action, use_other):
        base_resources = self.common.copy()
        other_resources = self.common.copy()
        result = base_resources.copy()
        base_resources["file45.h"] = base_resources["file1.h"]
        base_resources.pop("file1.h", None)
        base_renames = Renames()
        base_renames[CellName("file1.h")] = CellName("file45.h")
        other_renames = Renames()
        if action == 'delete':
            other_resources.pop("file1.h")
            result.pop("file1.h", None)
        elif action == 'modify':
            other_resources['file1.h'] = 'Updated file1.h\n'
            result.pop("file1.h", None)
            result["file45.h"] = 'Updated file1.h\n'
        if use_other:
            base_resources, other_resources = other_resources, base_resources
            base_renames, other_renames = other_renames, base_renames

        ret = self.merger.merge(base_resources, other_resources, self.common,
                                base_renames, other_renames)
        self.assertEqual(result, ret)
        self.assertNotIn("CONFLICT", str(self._biiout))

    @parameterized.expand(
        list(itertools.product(*[['delete', 'modify'],
                                 [True, False]]))
    )
    def test_rename_conflict(self, action, use_other):
        base_resources = self.common.copy()
        other_resources = self.common.copy()
        result = base_resources.copy()
        base_resources["file45.h"] = 'Updated file1.h\n'
        base_resources.pop("file1.h", None)
        base_renames = Renames()
        base_renames[CellName("file1.h")] = CellName("file45.h")
        other_renames = Renames()
        if action == 'delete':
            other_resources.pop("file1.h")
            result.pop("file1.h", None)
            result["file45.h"] = 'Updated file1.h\n'
        elif action == 'modify':
            other_resources['file1.h'] = 'Updated file12.h\n'
            result.pop("file1.h", None)
            result["file45.h"] = '<<<<<<<<<<<<<<<<<<<<<<<<< base\n' \
                                'Updated file12.h\n\n'            \
                                '=========================\n'       \
                                'Updated file1.h\n\n'             \
                                '>>>>>>>>>>>>>>>>>>>>>>>>> other\n'
        if use_other:
            base_resources, other_resources = other_resources, base_resources
            base_renames, other_renames = other_renames, base_renames
        ret = self.merger.merge(base_resources, other_resources, self.common,
                                base_renames, other_renames)
        self.assertEqual(result, ret)
        self.assertIn("CONFLICT", str(self._biiout))

    @parameterized.expand(
        list(itertools.product(*[[None, 'modify', 'double_modify'],
                                 [True, False]]))
    )
    def test_same_rename(self, action, use_other):
        base_resources = self.common.copy()
        base_resources["file45.h"] = base_resources["file1.h"]
        base_resources.pop("file1.h", None)
        base_renames = Renames()
        base_renames[CellName("file1.h")] = CellName("file45.h")

        result = base_resources.copy()
        other_resources = base_resources.copy()
        other_renames = base_renames.copy()

        if action == 'modify':
            other_resources['file45.h'] = 'Updated file1.h\n'
            result["file45.h"] = 'Updated file1.h\n'
        elif action == 'double_modify':
            other_resources['file45.h'] = 'Updated file1.h\n'
            base_resources['file45.h'] = 'Updated file1.h\n'
            result["file45.h"] = 'Updated file1.h\n'
        if use_other:
            base_resources, other_resources = other_resources, base_resources
            base_renames, other_renames = other_renames, base_renames

        ret = self.merger.merge(base_resources, other_resources, self.common,
                                base_renames, other_renames)
        self.assertEqual(result, ret)
        self.assertNotIn("CONFLICT", str(self._biiout))

    @parameterized.expand(
        list(itertools.product(*[[None, 'modify', 'double_modify'],
                                 [True, False]]))
    )
    def test_different_rename_same_old(self, action, use_other):
        base_resources = self.common.copy()
        base_resources.pop("file1.h")
        result = base_resources.copy()
        other_resources = base_resources.copy()
        base_resources["file45.h"] = "Content of file1.h\n"
        other_resources["file54.h"] = "Content of file1.h\n"

        base_renames = Renames()
        base_renames[CellName("file1.h")] = CellName("file45.h")

        other_renames = Renames()
        other_renames[CellName("file1.h")] = CellName("file54.h")

        msg = 'Updated file1.h\n'
        if action == 'modify':
            base_resources['file45.h'] = msg
        elif action == 'double_modify':
            base_resources['file45.h'] = msg
            other_resources['file54.h'] = msg
        else:
            msg = "Content of file1.h\n"
        if use_other:
            base_resources, other_resources = other_resources, base_resources
            base_renames, other_renames = other_renames, base_renames
            result["file54.h"] = msg
        else:
            result["file45.h"] = msg
        ret = self.merger.merge(base_resources, other_resources, self.common,
                                base_renames, other_renames)
        self.assertEqual(result, ret)
        self.assertNotIn("CONFLICT", str(self._biiout))

    @parameterized.expand(
        list(itertools.product(*[['modify', 'double_modify'],
                                 [True, False]]))
    )
    def test_different_rename_same_new(self, action, use_other):
        base_resources = self.common.copy()
        other_resources = base_resources.copy()
        result = base_resources.copy()

        base_resources.pop("file1.h")
        base_resources["file45.h"] = "Content of file1.h\n"
        other_resources.pop("file2.h")
        other_resources["file45.h"] = "Content of file2.h\n"

        result.pop("file1.h")
        result.pop("file2.h")
        base_renames = Renames()
        base_renames[CellName("file1.h")] = CellName("file45.h")
        other_renames = Renames()
        other_renames[CellName("file2.h")] = CellName("file45.h")

        if action == 'modify':
            base_resources['file45.h'] = 'Updated file 45\n'
            result["file45.h"] = 'Updated file 45\n'
        elif action == 'double_modify':
            msg = 'Updated file45.h\n'
            base_resources['file45.h'] = msg
            other_resources['file45.h'] = msg
            result["file45.h"] = msg

        if use_other:
            base_resources, other_resources = other_resources, base_resources
            base_renames, other_renames = other_renames, base_renames

        ret = self.merger.merge(base_resources, other_resources, self.common,
                                base_renames, other_renames)
        self.assertEqual(result, ret)
        self.assertNotIn("CONFLICT", str(self._biiout))

    @parameterized.expand(
        list(itertools.product(*[[None, 'modify'],
                                 [True, False]]))
    )
    def test_different_rename_same_new_conflict(self, action, use_other):
        base_resources = self.common.copy()
        other_resources = base_resources.copy()
        result = base_resources.copy()

        base_resources.pop("file1.h")
        base_resources["file45.h"] = "Content of file1.h\n"
        other_resources.pop("file2.h")
        other_resources["file45.h"] = "Content of file2.h\n"

        result.pop("file1.h")
        result.pop("file2.h")
        base_renames = Renames()
        base_renames[CellName("file1.h")] = CellName("file45.h")
        other_renames = Renames()
        other_renames[CellName("file2.h")] = CellName("file45.h")

        n1, n2 = (1, 2) if not use_other else (2, 1)
        if action == 'modify':
            base_resources['file45.h'] = 'File45.h updated 1\n'
            other_resources['file45.h'] = 'File45.h updated 2\n'
            result["file45.h"] = '<<<<<<<<<<<<<<<<<<<<<<<<< base\n' \
                                'File45.h updated %d\n\n'\
                                '=========================\n'\
                                'File45.h updated %d\n\n'\
                                '>>>>>>>>>>>>>>>>>>>>>>>>> other\n' % (n1, n2)
        else:
            result['file45.h'] = '<<<<<<<<<<<<<<<<<<<<<<<<< base\n' \
                                'Content of file%d.h\n\n'\
                                '=========================\n'\
                                'Content of file%d.h\n\n'\
                                '>>>>>>>>>>>>>>>>>>>>>>>>> other\n' % (n1, n2)

        if use_other:
            base_resources, other_resources = other_resources, base_resources
            base_renames, other_renames = other_renames, base_renames

        ret = self.merger.merge(base_resources, other_resources, self.common,
                                base_renames, other_renames)
        self.assertIn("CONFLICT", str(self._biiout))
        self.assertEqual(result, ret)
