#!/usr/bin/env python3
"""Tests for the selector 538 chunk-3 full caller review proposal."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector538_chunk3_review_v1.py"


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
    "pk_selector538_chunk3_review_test_builder_v1",
)


class Selector538Chunk3ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.frozen = BUILDER.build_report()
        cls.public_content = BUILDER.canonical_bytes(cls.report) + b"\n"
        cls.private = BUILDER.load_json_exact(BUILDER.PRIVATE_HANDOFF_PATH)

    def test_assignment_private_handoff_and_public_report_are_frozen(
        self,
    ) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.ASSIGNMENT_PATH),
            BUILDER.EXPECTED_ASSIGNMENT_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PRIVATE_HANDOFF_PATH),
            BUILDER.EXPECTED_PRIVATE_HANDOFF_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.public_content),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(BUILDER.DEFAULT_OUTPUT.read_bytes(), self.public_content)
        self.assertEqual(
            self.frozen["proposal_candidate_sha256"],
            BUILDER.EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        )

    def test_all_70_sites_and_490_branches_are_recorded(self) -> None:
        self.assertEqual(
            self.private["counts"],
            {
                "accepted": 38,
                "accepted_assemblies": 266,
                "assemblies": 490,
                "keep": 1,
                "reject": 32,
                "rejected_assemblies": 224,
                "rewrite": 37,
                "sites": 70,
            },
        )
        rows = self.private["site_reviews"]
        self.assertEqual(len(rows), 70)
        self.assertEqual(sum(len(row["assemblies"]) for row in rows), 490)
        self.assertEqual(
            [row["ordinal"] for row in rows],
            list(range(207, 277)),
        )
        for row in rows:
            self.assertEqual(len(row["assemblies"]), 7)
            control = row["control_and_protected_proof"]
            self.assertTrue(control["record_control_gaps_preserved"])
            self.assertTrue(control["outer_whitespace_preserved"])
            self.assertTrue(control["literal_linebreak_count_preserved"])
            authority = row["multilingual_authority"]
            self.assertTrue(authority["jp_is_semantic_authority"])
            self.assertTrue(authority["speaker_tone_reviewed"])
            self.assertTrue(authority["historical_terms_reviewed"])
        self.assertEqual(
            self.report["proof"]["auxiliary_language_available_counts"],
            {"en": 52, "jp": 70, "sc": 51, "tc": 51},
        )

    def test_every_accepted_site_passes_all_seven_assembly_gates(
        self,
    ) -> None:
        accepted = [
            row for row in self.private["site_reviews"]
            if row["decision"] != "reject"
        ]
        rejected = [
            row for row in self.private["site_reviews"]
            if row["decision"] == "reject"
        ]
        self.assertEqual(len(accepted), 38)
        self.assertEqual(len(rejected), 32)
        self.assertEqual(
            sum(len(row["assemblies"]) for row in accepted),
            266,
        )
        for row in accepted:
            self.assertTrue(row["all_seven_register_branches_proven"])
            self.assertTrue(row["all_seven_width_branches_nonexpanding"])
            for branch in row["assemblies"]:
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
        self.assertEqual(
            self.report["proof"]["accepted_assembly_canonical_sha256"],
            BUILDER.EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
        )

    def test_prior_chunk_exact_map_overlaps_are_zero_or_identical(self) -> None:
        empty_digest = BUILDER.EXPECTED_CHUNK0_OVERLAP_SHA256
        for chunk_id in (0, 1):
            key = f"chunk{chunk_id}_exact_map_overlap"
            overlap = self.private[key]
            self.assertEqual(overlap["coordinate_count"], 0)
            self.assertTrue(overlap["all_overlapping_values_identical"])
            self.assertEqual(overlap["canonical_sha256"], empty_digest)
            self.assertEqual(self.report["proof"][key], overlap)

    def test_exact_runtime_closure_classification_is_frozen(self) -> None:
        result = self.report["result"]
        proof = self.report["proof"]
        self.assertEqual(result["accepted_site_count"], 38)
        self.assertEqual(result["accepted_root_count"], 37)
        self.assertEqual(result["rewrite_coordinate_count"], 37)
        self.assertEqual(result["keep_coordinate_count"], 1)
        self.assertEqual(result["reject_coordinate_count"], 32)
        self.assertEqual(result["rejected_root_count"], 32)
        self.assertEqual(result["runtime_promotion_coordinate_count"], 89)
        self.assertEqual(result["runtime_promotion_root_count"], 28)
        self.assertEqual(result["rejected_pending_root_count"], 24)
        self.assertEqual(result["blocked_pending_coordinate_count"], 53)
        self.assertEqual(
            result["verification_renewal_coordinate_count"],
            420,
        )
        self.assertEqual(result["verification_renewal_root_count"], 204)
        self.assertEqual(result["exact_override_coordinate_count"], 37)
        self.assertEqual(result["decision_delta_coordinate_count"], 509)
        self.assertEqual(result["runtime_review_pending_before"], 8213)
        self.assertEqual(result["runtime_review_pending_after"], 8124)
        self.assertEqual(
            proof["runtime_action_counts"],
            {
                "runtime_promotion": 70,
                "translation_override_and_runtime_promotion": 19,
                "translation_override_and_verification_renewal": 18,
                "verification_renewal": 402,
            },
        )
        self.assertEqual(
            proof["runtime_action_manifest_canonical_sha256"],
            BUILDER.EXPECTED_ACTION_SHA256,
        )

    def test_public_report_is_source_free_and_read_only(self) -> None:
        decoded = self.public_content.decode("ascii")
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3130-\u318f\u3400-\u4dbf"
                r"\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                decoded,
            )
        )
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+)?\b", decoded))
        self.assertNotIn('"translation"', decoded)
        self.assertNotIn('"exact_maps"', decoded)
        policy = self.report["distribution_policy"]
        self.assertFalse(
            policy["tracked_report_contains_commercial_source_text"]
        )
        self.assertFalse(
            policy["tracked_report_contains_translated_dialogue_text"]
        )
        self.assertFalse(
            policy["tracked_report_contains_translation_map_keys"]
        )
        self.assertFalse(self.report["steam_write_performed"])
        self.assertEqual(
            self.report["guards"]["steam_archive_sha256_before"],
            self.report["guards"]["steam_archive_sha256_after"],
        )
        self.assertEqual(
            self.report["inputs"]["integrated_ledger_sha256"],
            BUILDER.EXPECTED_LEDGER_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
