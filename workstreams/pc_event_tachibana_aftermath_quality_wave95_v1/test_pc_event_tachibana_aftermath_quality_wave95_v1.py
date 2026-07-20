#!/usr/bin/env python3
"""Regression checks for the private W95 Tachibana-aftermath candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_event_tachibana_aftermath_quality_wave95_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave95_under_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class Wave95Tests(unittest.TestCase):
    def test_scope_target_and_reservation_contract(self) -> None:
        builder.validate_static_targets()
        self.assertEqual(builder.SCENE_IDS, tuple(range(8392, 8442)))
        self.assertEqual(len(builder.CHANGED_IDS), 25)
        self.assertEqual(len(builder.RETAINED_IDS), 25)
        self.assertEqual(set(builder.CHANGED_IDS) | set(builder.RETAINED_IDS), set(builder.SCENE_IDS))
        self.assertFalse(set(builder.CHANGED_IDS) & set(builder.RETAINED_IDS))
        self.assertEqual(builder.STALE_PRE_LF_REBUILD_PROFILE["sha256"], "3F2A6B1EA2CF6C137AE6AD4E58C676774D2FD363816BD531C5A414853109BFB9")
        expected_reservations = {
            "[bm1222]": ("다카하시 무네토라", 408),
            "[b1222]": ("다카하시 무네토라", 408),
            "[b1221]": ("다카하시 조운", 312),
            "[bm1730]": ("벳키 아키츠라", 312),
            "[b1730]": ("벳키 아키츠라", 312),
        }
        self.assertEqual(set(builder.SCENE_RUNTIME_RESERVATIONS), set(expected_reservations))
        for token, (display, raw) in expected_reservations.items():
            reservation = builder.SCENE_RUNTIME_RESERVATIONS[token]
            self.assertEqual(reservation["display"], display)
            self.assertEqual(reservation["reserved_raw_g1n_width_px"], raw)
            self.assertTrue(reservation["scene_limited"])
            self.assertFalse(reservation["runtime_proven"])

    def test_all_fifty_rows_are_reservation_aware_and_within_gate(self) -> None:
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(tuple(bundle.changed), builder.CHANGED_IDS)
        self.assertEqual(len(bundle.rows), 50)
        for row in bundle.rows:
            entry_id = row["entry_id"]
            self.assertEqual(
                tuple(line["raw_g1n_width_px"] for line in row["target_lines"]),
                builder.SCENE_RAW_WIDTHS[entry_id],
            )
            self.assertGreaterEqual(row["target_manual_line_count"], 1)
            self.assertLessEqual(row["target_manual_line_count"], 4)
            self.assertFalse(row["runtime_proven"])
            for line in row["target_lines"]:
                self.assertLessEqual(line["raw_g1n_width_px"], 960)
                self.assertFalse(line["over_live_raw_960px"])
        rows = {row["entry_id"]: row for row in bundle.rows}
        self.assertEqual(
            tuple(row["entry_id"] for row in bundle.rows if row["lf_only_reflow"]),
            builder.LF_ONLY_IDS,
        )
        for entry_id in builder.LF_ONLY_IDS:
            self.assertEqual(
                builder.LINEBREAK_RE.sub(" ", rows[entry_id]["target_ko"]),
                builder.LINEBREAK_RE.sub(" ", rows[entry_id]["w94_current_ko"]),
            )
        self.assertEqual(rows[8394]["target_lines"][0]["display_string"], "다카하시 무네토라가 이끄는 오토모군은")
        self.assertEqual(rows[8399]["target_lines"][2]["display_string"], "벳키 아키츠라의 데릴사위 겸 양자가 되어")
        self.assertEqual(rows[8440]["runtime_reservations"][0]["reserved_raw_g1n_width_px"], 408)

    def test_profile_and_private_candidate_are_exact(self) -> None:
        self.assertIsNotNone(builder.EXPECTED_OUTPUT_PROFILE)
        bundle = builder.prepare(require_output_profile=True)
        self.assertEqual(bundle.profile, builder.EXPECTED_OUTPUT_PROFILE)
        result = builder.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["event_profile"], builder.EXPECTED_OUTPUT_PROFILE)
        self.assertFalse(result["steam_game_resource_written"])
        self.assertFalse(result["git_operation_performed"])
        self.assertFalse(result["network_operation_performed"])
        self.assertFalse(result["runtime_proven"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
