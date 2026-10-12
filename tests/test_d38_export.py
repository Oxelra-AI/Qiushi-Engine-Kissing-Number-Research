import importlib.util
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("export_d38", ROOT / "constructions/d38/export_vectors.py")
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


class Export38Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.metadata = export.integer_rows(ROOT / "constructions/d38/base-data",
                                                    ROOT / "constructions/d38/added-lines.txt")

    def test_full_count_and_layers(self):
        self.assertEqual(self.rows.shape, (591900, 52))
        self.assertEqual([(x["start"], x["stop"]) for x in self.metadata["layers"]],
                         [(0, 589680), (589680, 591612), (591612, 591900)])

    def test_subspace_and_rank(self):
        self.assertTrue(np.array_equal(self.rows[:, 24:38], self.rows[:, 38:]))
        # The added shell spans all 24 head directions; the axes span all 14 tails.
        # SymPy's rank is exact, including the large axis numerators.
        from sympy import Matrix
        self.assertEqual(Matrix(self.rows[591612:591756, :24].tolist()).rank(), 24)
        directions = np.loadtxt(ROOT / "constructions/d38/base-data/dim14_directions.txt",
                                delimiter=",", dtype=np.int64)
        self.assertEqual(Matrix(directions.tolist()).rank(), 14)

    def test_integer_angle_rule_on_each_layer(self):
        indices = list(range(0, 589680, 6000)) + list(range(589680, 591612, 100)) + list(range(591612, 591900))
        selected = self.rows[indices].astype(object)
        norms = [sum(int(x)**2 for x in row) for row in selected]
        products = selected @ selected.T
        for i in range(len(selected)):
            for j in range(i):
                dot = int(products[i, j])
                self.assertTrue(dot <= 0 or 4 * dot * dot <= norms[i] * norms[j])


if __name__ == "__main__":
    unittest.main()
