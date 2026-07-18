"""Regression coverage for the Issue #61 policy percent-literal repair."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_issue_61_policy_percent_v1.py"
SPEC = importlib.util.spec_from_file_location("issue_61_policy_percent_v1", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class Issue61PolicyPercentTests(unittest.TestCase):
    def test_scope_vectors_are_exact_and_inside_the_complete_policy_ranges(self) -> None:
        builder.assert_scope_constants()
        self.assertEqual(len(builder.PK_PERCENT_IDS), 49)
        self.assertEqual(len(builder.SHARED_PERCENT_SLOTS), 39)
        self.assertEqual(len(builder.policy_coordinates(builder.PK_MSGDATA)), 196)
        self.assertEqual(len(builder.policy_coordinates(builder.SHARED_STRDATA)), 134)
        self.assertEqual(
            builder.canonical_hash(sorted(builder.PK_PERCENT_IDS)),
            builder.PK_PERCENT_IDS_SHA256,
        )
        self.assertEqual(
            builder.canonical_hash(sorted(builder.SHARED_PERCENT_SLOTS)),
            builder.SHARED_PERCENT_SLOTS_SHA256,
        )

    def test_unsafe_percent_scanner_leaves_printf_tokens_and_fullwidth_literals_alone(self) -> None:
        fullwidth = builder.load_fullwidth_support()
        self.assertEqual(builder.unsafe_ascii_percent_indexes("효과 %+d％", fullwidth), ())
        self.assertEqual(builder.unsafe_ascii_percent_indexes("효과 %+d%", fullwidth), (6,))
        self.assertEqual(builder.unsafe_ascii_percent_indexes("100%", fullwidth), (3,))
        self.assertEqual(builder.unsafe_ascii_percent_indexes("%%", fullwidth), ())

    def test_restore_literal_percent_requires_the_historical_after_hash(self) -> None:
        fullwidth = builder.load_fullwidth_support()
        predecessor = "효과 %+d%"
        source = "효과 %+d％"
        entry = {
            "after_utf16le_sha256": fullwidth.text_hash(predecessor),
            "before_utf16le_sha256": fullwidth.text_hash(source),
            "character_operations": [
                {
                    "operation_type": "fullwidth_ascii",
                    "char_index": len(predecessor) - 1,
                    "from": "U+FF05",
                    "to": "U+0025",
                }
            ],
        }
        self.assertEqual(builder.restore_literal_percent(predecessor, entry, fullwidth), source)
        with self.assertRaises(builder.Issue61Error):
            builder.restore_literal_percent("효과 %+d% 변경", entry, fullwidth)

    def test_live_candidate_restores_all_88_policy_cells_to_the_v09_oracle(self) -> None:
        payloads, audit = builder.prepare_candidate(
            builder.DEFAULT_STEAM_ROOT,
            require_pinned_targets=True,
        )
        self.assertEqual(set(payloads), set(builder.CHANGED_PATHS))
        self.assertEqual(audit["candidate_profile"], builder.TARGET_SPECS)
        self.assertEqual(len(audit["changes"]), 88)
        self.assertTrue(audit["predecessor_unchanged_after_prepare"])
        policy = audit["policy"]
        self.assertEqual(
            policy["predecessor"][builder.PK_MSGDATA]["unsafe_ascii_percent_character_count"],
            49,
        )
        self.assertEqual(
            policy["predecessor"][builder.SHARED_STRDATA]["unsafe_ascii_percent_character_count"],
            39,
        )
        for source_name in ("candidate", "v0_9_source"):
            self.assertEqual(
                policy[source_name][builder.PK_MSGDATA]["unsafe_ascii_percent_character_count"],
                0,
            )
            self.assertEqual(
                policy[source_name][builder.SHARED_STRDATA]["unsafe_ascii_percent_character_count"],
                0,
            )

    def test_build_and_verify_stay_in_private_tmp_and_emit_the_exact_11_file_profile(self) -> None:
        builder.TMP_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".issue61-policy-percent-test-", dir=builder.TMP_ROOT) as raw:
            base = Path(raw)
            output_root = base / "candidate"
            audit_path = base / "audit.v1.json"
            manifest_path = base / "build_manifest.v1.json"
            manifest = builder.build_candidate(
                builder.DEFAULT_STEAM_ROOT,
                output_root,
                audit_path,
                manifest_path,
            )
            self.assertEqual(manifest["candidate_profile"], builder.TARGET_SPECS)
            self.assertTrue(manifest["steam_predecessor_unchanged_after_build"])
            builder.assert_candidate_tree(output_root, builder.TARGET_SPECS, "test")
            report = builder.verify_candidate(builder.DEFAULT_STEAM_ROOT, output_root)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["changed_coordinate_count"], 88)


if __name__ == "__main__":
    unittest.main()
