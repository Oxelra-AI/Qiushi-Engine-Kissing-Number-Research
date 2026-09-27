"""The added dimensions have complete data, consistent counts and distinct scopes."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def module(relative, name):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(value)
    finally:
        sys.path.remove(str(path.parent))
    return value


class Additions(unittest.TestCase):
    def test_recorded_replay_covers_the_full_plan(self):
        plan = json.loads((ROOT / 'tools/replay_plan.json').read_text())['jobs']
        receipt = json.loads((ROOT / 'evidence/verification.json').read_text())
        self.assertTrue(receipt['passed'])
        self.assertTrue(receipt['inputs_unchanged'])
        self.assertEqual(receipt['suite'], 'all')
        self.assertCountEqual([job['id'] for job in plan],
                              [check['id'] for check in receipt['checks']])
        self.assertTrue(all(check['passed'] and check['exit_code'] == 0
                            for check in receipt['checks']))
        original = json.loads((ROOT / 'evidence/livestream-verification.json').read_text())
        self.assertTrue(original['passed'])
        self.assertEqual(len(original['checks']), 13)

    def test_nine_completed_additions_and_one_comparison(self):
        rows = json.loads((ROOT / 'research/comparisons/additional-dimensions.json').read_text())['results']
        self.assertEqual([r['dimension'] for r in rows], [18, 25, 27, 49, 50, 51, 52, 53, 54, 55])
        self.assertEqual([r['dimension'] for r in rows if r['difference'] > 0], [25, 27, 49, 50, 51, 52, 53, 54, 55])
        for row in rows:
            self.assertEqual(row['qiushi_lower_bound'] - row['external_lower_bound'], row['difference'])
        catalog = json.loads((ROOT / 'constructions/catalog/results.json').read_text())['results']
        self.assertNotIn(18, [r['dimension'] for r in catalog])

    def test_dimension25_receipt_and_rejections(self):
        receipt = json.loads((ROOT / 'constructions/d25/verification.json').read_text())
        self.assertTrue(receipt['passed'])
        self.assertTrue(receipt['negative_tests_passed'])
        self.assertEqual(receipt['points'], 197580)
        self.assertEqual(len(receipt['negative_tests']), 2)

    def test_search_graph_preserves_label_constraints(self):
        search = module('constructions/d27/search.py', 'd27_search_test')
        vectors = np.array([[1, 0], [0, 1], [-1, 0]])
        edges = np.array([[0, 1]])
        self.assertEqual(len(search.check_selection(vectors, edges, vectors, np.array([0, 1, 0]))), 3)
        with self.assertRaises(ValueError):
            search.check_selection(vectors, edges, vectors, np.array([0, 0, 1]))
        with self.assertRaises(ValueError):
            search.check_selection(vectors, edges, vectors[[0, 0]], np.array([0, 1]))

    def test_p48_augmentation_rejects_corruption(self):
        search = module('constructions/p48/search.py', 'p48_search_test')
        c = np.load(ROOT / 'constructions/p48/data/class_p48_7077.npy').astype(np.int64)
        g = np.load(ROOT / 'constructions/p48/data/p48p_gram.npy').astype(np.int64)
        self.assertEqual(search.augmentation(c, g)['added_rows'], 8)
        c[-1] = c[0]
        with self.assertRaises(ValueError):
            search.augmentation(c, g)
        with self.assertRaises(ValueError):
            search.multiply(np.array([[2**62]], dtype=np.int64), np.array([[4]], dtype=np.int64))

    def test_union_counts_and_increment_decomposition(self):
        record = json.loads((ROOT / 'research/data/p48-search.json').read_text())
        comparisons = {str(row['dimension']): row for row in json.loads(
            (ROOT / 'research/comparisons/additional-dimensions.json').read_text())['results']}
        expected = {'49': (16, 0), '50': (48, 2), '51': (96, 18), '52': (192, 64),
                    '53': (320, 154), '54': (572, 296), '55': (996, 414)}
        for dimension, row in record['families'].items():
            self.assertEqual(sum(row['assigned_sizes']), row['union'])
            self.assertEqual(7077 * row['images'] - row['union'], row['overlap_loss'])
            self.assertEqual(row['union'] - row['same_family_original_class_union'], row['extra_lines_from_augmentation'])
            self.assertEqual(52416000 + 2 * row['union'] + 2 * row['images'], row['points'])
            old_union = (comparisons[dimension]['external_lower_bound'] - 52416000 - 2 * row['images']) // 2
            gains = (2 * row['extra_lines_from_augmentation'],
                     2 * (row['same_family_original_class_union'] - old_union))
            self.assertEqual(gains, expected[dimension])
            self.assertEqual(sum(gains), comparisons[dimension]['difference'])
        self.assertEqual(record['families']['50']['overlap_loss'], 0)


if __name__ == '__main__':
    unittest.main()
