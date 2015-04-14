import unittest

from biicode.common.diffmerge.differ import similarity, compute_diff
from biicode.common.diffmerge.differ import text_unified_diff
from biicode.common.diffmerge.compare import compare


class DifferTest(unittest.TestCase):

    def test_string_similarity(self):
        base = '\n'.join([str(i) for i in range(0, 10)])
        other = base
        EPS = 0.0001
        for i in range(0, 10):
            other = other.replace(str(i), '*')
            sim = similarity(base, other)
            self.assertGreater((10 - i) / 10.0, sim)
            self.assertLessEqual((9 - i) / 10.0, sim + EPS)

    def test_diff_text(self):
        base = {'f1': 'Hola que tal\nBien Gracias\n',
                'f2': 'Hasta luego\n'}
        other = {'f1': 'Hola que tal\nBien, Bien\n',
                 'f3': 'Hasta luego lucas\n'}

        changes = compare(base, other)
        diff = compute_diff(changes, text_unified_diff)
        self.assertIn('-Hasta luego', diff.deleted['f2'])
        self.assertIn('+Hasta luego lucas', diff.created['f3'])
        self.assertIn('-Bien Gracias', diff.modified['f1'])
        self.assertIn('+Bien, Bien', diff.modified['f1'])

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
