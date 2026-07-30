#!/usr/bin/env python3
"""Tests for the selector-1096 chunk-1 full caller review."""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector1096_chunk1_review_v1.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(
    BUILDER_PATH,
    "pk_selector1096_chunk1_review_test_builder_v1",
)


class Selector1096Chunk1ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.frozen = BUILDER.build_report()
        cls.public_content = BUILDER.canonical_bytes(cls.report) + b"\n"
        cls.private = BUILDER.load_json_exact(
            BUILDER.PRIVATE_HANDOFF_PATH
        )

    def test_assignment_handoff_and_public_report_are_frozen(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.ASSIGNMENT_PATH),
            BUILDER.EXPECTED_ASSIGNMENT_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.ASSIGNMENT_PUBLIC_PATH),
            BUILDER.EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PRIVATE_HANDOFF_PATH),
            BUILDER.EXPECTED_PRIVATE_HANDOFF_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.public_content),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.DEFAULT_OUTPUT.read_bytes(),
            self.public_content,
        )
        self.assertEqual(
            self.frozen["proposal_candidate_sha256"],
            BUILDER.EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        )

    def test_all_59_sites_and_413_branches_are_recorded(self) -> None:
        self.assertEqual(
            self.private["counts"],
            {
                "accepted": 50,
                "accepted_assemblies": 350,
                "assemblies": 413,
                "keep": 4,
                "reject": 9,
                "rejected_assemblies": 63,
                "rewrite": 46,
                "sites": 59,
            },
        )
        rows = self.private["site_reviews"]
        self.assertEqual(len(rows), 59)
        self.assertEqual(
            sum(len(row["assemblies"]) for row in rows),
            413,
        )
        self.assertEqual(
            [row["ordinal"] for row in rows],
            list(range(56, 115)),
        )
        for row in rows:
            self.assertEqual(len(row["assemblies"]), 7)
            proof = row["control_and_protected_proof"]
            self.assertTrue(proof["record_control_gaps_preserved"])
            self.assertTrue(proof["outer_whitespace_preserved"])
            self.assertTrue(proof["literal_linebreak_count_preserved"])
            authority = row["multilingual_authority"]
            self.assertTrue(authority["jp_is_semantic_authority"])
            self.assertTrue(authority["speaker_tone_reviewed"])
            self.assertTrue(authority["historical_terms_reviewed"])
            self.assertEqual(authority["review_passes"], 2)

    def test_accepted_sites_pass_register_and_width_gates(self) -> None:
        accepted = [
            row for row in self.private["site_reviews"]
            if row["decision"] != "reject"
        ]
        rejected = [
            row for row in self.private["site_reviews"]
            if row["decision"] == "reject"
        ]
        self.assertEqual(len(accepted), 50)
        self.assertEqual(len(rejected), 9)
        for row in accepted:
            self.assertTrue(row["all_seven_register_branches_proven"])
            self.assertTrue(
                row["all_seven_width_branches_nonexpanding"]
            )
            for branch in row["assemblies"]:
                terminal = int(
                    branch["terminal_coordinate"].split(":")[1]
                )
                self.assertEqual(
                    branch["register_semantic"],
                    BUILDER.semantic_register(terminal),
                )
                self.assertTrue(branch["register_and_grammar_proven"])
                self.assertTrue(
                    branch["current_relative_raw_g1n_nonexpanding"]
                )
                self.assertTrue(branch["line_count_match"])
        for row in rejected:
            self.assertTrue(row["reject_reason"])
            self.assertFalse(
                row["all_seven_register_branches_proven"]
                and row["all_seven_width_branches_nonexpanding"]
            )

    def test_root_partition_rejects_the_shared_unsafe_record(self) -> None:
        accepted_roots = {
            row["root"]
            for row in self.private["site_reviews"]
            if row["decision"] != "reject"
        }
        rejected_roots = {
            row["root"]
            for row in self.private["site_reviews"]
            if row["decision"] == "reject"
        }
        self.assertEqual(len(accepted_roots), 50)
        self.assertEqual(len(rejected_roots), 8)
        self.assertTrue(accepted_roots.isdisjoint(rejected_roots))
        shared = [
            row for row in self.private["site_reviews"]
            if row["root"] == "15:1382"
        ]
        self.assertEqual(len(shared), 2)
        self.assertTrue(all(row["decision"] == "reject" for row in shared))

    def test_public_counts_and_multilingual_review_proof_match(self) -> None:
        result = self.report["result"]
        proof = self.report["proof"]
        self.assertEqual(result["accepted_site_count"], 50)
        self.assertEqual(result["rewrite_coordinate_count"], 46)
        self.assertEqual(result["keep_coordinate_count"], 4)
        self.assertEqual(result["reject_coordinate_count"], 9)
        self.assertEqual(result["accepted_root_count"], 50)
        self.assertEqual(result["rejected_root_count"], 8)
        self.assertEqual(
            result["potential_promotion_coordinate_count"],
            78,
        )
        self.assertEqual(result["blocked_pending_coordinate_count"], 13)
        self.assertEqual(
            result["accepted_current_a19_live_pending_count"],
            78,
        )
        self.assertEqual(
            result["accepted_live_after_selector538_plan_count"],
            72,
        )
        self.assertEqual(proof["assembly_branches_recorded"], 413)
        self.assertEqual(proof["accepted_assembly_branches"], 350)
        self.assertEqual(proof["rejected_assembly_branches"], 63)
        self.assertTrue(proof["all_59_sites_classified"])
        self.assertEqual(
            proof["auxiliary_language_available_counts"],
            {"en": 26, "jp": 59, "sc": 28, "tc": 29},
        )
        self.assertEqual(
            proof["blocker_reason_counts"],
            {
                "dynamic_terminal_width_constraint": 1,
                "fixed_connective_suffix_after_terminal": 3,
                "fixed_reason_suffix_after_terminal": 1,
                "noncaller_right_line_width_expansion": 3,
                "shared_root_contains_rejected_site": 1,
            },
        )
        self.assertEqual(
            proof["chunk1_pending_coordinate_sha256"],
            BUILDER.EXPECTED_PENDING_COORDINATE_SHA256,
        )

    def test_public_report_is_source_free_and_output_path_is_fixed(
        self,
    ) -> None:
        decoded = self.public_content.decode("ascii")
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                decoded,
            )
        )
        self.assertIsNone(
            re.search(r"\b\d+:\d+(?::\d+){0,2}\b", decoded)
        )
        self.assertNotIn('"translation"', decoded)
        self.assertNotIn('"exact_maps"', decoded)
        self.assertFalse(self.report["steam_write_performed"])
        self.assertEqual(
            self.report["guards"]["steam_archive_sha256_before"],
            self.report["guards"]["steam_archive_sha256_after"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                BUILDER.ReviewError,
                "fixed tracked path",
            ):
                BUILDER.main(
                    ["--output", str(Path(temporary) / "report.json")]
                )


if __name__ == "__main__":
    unittest.main()
