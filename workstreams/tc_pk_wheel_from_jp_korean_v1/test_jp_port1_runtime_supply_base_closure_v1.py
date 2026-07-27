#!/usr/bin/env python3

from __future__ import annotations

import unittest

import build_jp_port1_runtime_supply_base_closure_v1 as target


class RuntimeSupplyBaseClosureTests(unittest.TestCase):
    def test_source_and_target_cover_six_states(self) -> None:
        self.assertEqual(target.SOURCE_RECORDS, tuple(range(48, 54)))
        self.assertEqual(target.TARGET_RECORDS, tuple(range(32, 38)))

    def test_low_and_high_resource42_outers_are_explicit(self) -> None:
        self.assertEqual(target.TARGET_OUTERS, {1: 36, 2: 37})


if __name__ == "__main__":
    unittest.main()
