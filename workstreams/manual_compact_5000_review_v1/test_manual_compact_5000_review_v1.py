#!/usr/bin/env python3
"""Read-only regression checks for the 5xxx manual-compaction review artifact."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILDER_PATH = WORKSTREAM / "build_manual_compact_5000_review_v1.py"
OLD_5777_BASELINE_PATH = (
    REPO
    / "tmp"
    / "pc_event_5777_kanegasaki_decompact_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)


def load_builder() -> object:
    spec = importlib.util.spec_from_file_location("manual_compact_5000_review_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class ManualCompact5000ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact = json.loads(B.OUTPUT_PATH.read_text(encoding="utf-8"))
        cls.rows = {row["id"]: row for row in cls.artifact["entries"]}
        _profile, cls.static007 = B.profile(B.CURRENT_KO_PATH)
        _profile, cls.old_5777 = B.profile(OLD_5777_BASELINE_PATH)
        cls.historical = json.loads(B.HISTORICAL_MANIFEST.read_text(encoding="utf-8"))
        cls.historical_by_id = {row["id"]: row for row in cls.historical["entries"]}
        _profile, cls.legacy = B.profile(B.LEGACY_PRECOMPACTION_KO_PATH)

    def test_scope_and_static007_profile(self) -> None:
        self.assertEqual(self.artifact["scope"]["manual_compact_target_count"], 164)
        self.assertEqual(len(self.rows), 164)
        current = self.artifact["sources"]["current_ko_static007_3line_successor"]
        self.assertEqual(current["packed_sha256"], B.EXPECTED_CURRENT_PROFILE["packed_sha256"])
        self.assertEqual(current["raw_sha256"], B.EXPECTED_CURRENT_PROFILE["raw_sha256"])

    def test_5777_preserves_static007_three_line_correction(self) -> None:
        expected = (
            "\x1bCC가네가사키\x1bCZ의 위기에서 벗어난 \x1bCA오다 노부나가\x1bCZ는\n"
            "\x1bCC기후\x1bCZ로 돌아오자마자 태세를 정비해,\n"
            "\x1bCB아자이 가문\x1bCZ 토벌 의지를 분명히 밝혔다."
        )
        row = self.rows[5777]
        self.assertEqual(self.static007[5777], expected)
        self.assertEqual(row["current_ko_at_static007_3line_baseline"], expected)
        self.assertEqual(row["proposed_ko"], expected)
        self.assertEqual(row["target_line_count"], 3)
        self.assertEqual(row["restoration_strategy"], "preserve_post_compaction_current_quality_revision")

    def test_baseline_change_is_limited_to_5777(self) -> None:
        changed = [
            entry_id
            for entry_id, (old, current) in enumerate(zip(self.old_5777, self.static007))
            if old != current
        ]
        self.assertEqual(changed, [5777])

    def test_all_other_5xxx_decisions_do_not_drift(self) -> None:
        for entry_id, row in self.rows.items():
            if entry_id == 5777:
                continue
            historical_compact = self.historical_by_id[entry_id]["ko"]
            current = self.old_5777[entry_id]
            expected = (
                B.normalize_linebreaks(current)
                if current != historical_compact
                else B.normalize_legacy_layout(self.legacy[entry_id])
            )
            if entry_id in B.SEMANTIC_REFLOW_OVERRIDES:
                expected = B.SEMANTIC_REFLOW_OVERRIDES[entry_id]
            self.assertEqual(row["current_ko_at_static007_3line_baseline"], current, entry_id)
            self.assertEqual(row["proposed_ko"], expected, entry_id)

    def test_layout_and_5164_reflow_evidence(self) -> None:
        for row in self.rows.values():
            self.assertLessEqual(row["target_line_count"], 4, row["id"])
            self.assertFalse(row["any_line_exceeds_912px"], row["id"])
            for line in row["target_lines"]:
                self.assertLessEqual(line["raw_g1n_width_px"], 1440, row["id"])
                self.assertLessEqual(line["effective_width_px"], 912, row["id"])
                self.assertFalse(line["exceeds_912px"], row["id"])
        reflow = self.rows[5164]["legacy_layout_before_semantic_reflow"]
        self.assertIsNotNone(reflow)
        self.assertEqual(reflow["lines"][1]["raw_g1n_width_px"], 2016)
        self.assertEqual(reflow["lines"][1]["effective_width_px"], 1260)
        self.assertEqual(
            [line["raw_g1n_width_px"] for line in self.rows[5164]["target_lines"]],
            [816, 1056, 936],
        )


if __name__ == "__main__":
    unittest.main()
