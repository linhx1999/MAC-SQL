from __future__ import annotations

import unittest
from core.spider_export import prediction_lines


class SpiderExportTest(unittest.TestCase):
    def test_order_duplicates_missing_and_failure(self):
        records = [{'idx': 2, 'pred': 'SELECT 2'}, {'idx': 0, 'pred': 'SELECT 0'},
                   {'idx': 2, 'pred': "SELECT 'two  spaces'\nFROM t"},
                   {'idx': 3, 'pred': 'SELECT NULL', 'error_type': 'thinking_budget_exhausted'}]
        lines = prediction_lines(records, 4)
        self.assertEqual(lines[0], 'SELECT 0\n')
        self.assertEqual(lines[1], 'SELECT * FROM __mac_failed_prediction__\n')
        self.assertEqual(lines[2], "SELECT 'two  spaces' FROM t\n")
        self.assertEqual(lines[3], lines[1])

    def test_out_of_range_index_rejected(self):
        with self.assertRaises(ValueError):
            prediction_lines([{'idx': 3, 'pred': 'SELECT 1'}], 2)
