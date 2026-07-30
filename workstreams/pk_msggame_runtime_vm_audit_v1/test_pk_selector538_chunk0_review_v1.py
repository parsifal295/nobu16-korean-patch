#!/usr/bin/env python3
"""Tests for the selector 538 chunk-0 full caller review proposal."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector538_chunk0_review_v1.py"


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
    "pk_selector538_chunk0_review_test_builder_v1",
)


class Selector538Chunk0ReviewTests(unittest.TestCase):
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
        self.assertEqual(
            BUILDER.DEFAULT_OUTPUT.read_bytes(),
            self.public_content,
        )
        self.assertEqual(
            self.frozen["proposal_candidate_sha256"],
            BUILDER.EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        )

    def test_all_65_sites_and_455_branches_are_recorded(self) -> None:
        self.assertEqual(
            self.private["counts"],
            {
                "accepted": 35,
                "accepted_assemblies": 245,
                "assemblies": 455,
                "keep": 2,
                "reject": 30,
                "rejected_assemblies": 210,
                "rewrite": 33,
                "sites": 65,
            },
        )
        rows = self.private["site_reviews"]
        self.assertEqual(len(rows), 65)
        self.assertEqual(
            sum(len(row["assemblies"]) for row in rows),
            455,
        )
        self.assertEqual(
            [row["ordinal"] for row in rows],
            list(range(65)),
        )
        for row in rows:
            self.assertEqual(len(row["assemblies"]), 7)
            self.assertTrue(
                row["control_and_protected_proof"][
                    "record_control_gaps_preserved"
                ]
            )
            self.assertTrue(
                row["control_and_protected_proof"][
                    "outer_whitespace_preserved"
                ]
            )
            self.assertTrue(
                row["control_and_protected_proof"][
                    "literal_linebreak_count_preserved"
                ]
            )
            self.assertTrue(
                row["multilingual_authority"][
                    "jp_is_semantic_authority"
                ]
            )
            self.assertTrue(
                row["multilingual_authority"]["speaker_tone_reviewed"]
            )
            self.assertTrue(
                row["multilingual_authority"]["historical_terms_reviewed"]
            )

    def test_every_accepted_site_passes_all_seven_register_and_width_gates(
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
        self.assertEqual(len(accepted), 35)
        self.assertEqual(len(rejected), 30)
        for row in accepted:
            self.assertTrue(
                row["all_seven_register_branches_proven"]
            )
            self.assertTrue(
                row["all_seven_width_branches_nonexpanding"]
            )
            for branch in row["assemblies"]:
                self.assertTrue(
                    branch["register_and_grammar_proven"]
                )
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

    def test_public_report_is_source_free_and_proposal_only(self) -> None:
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
            BUILDER.sha256_file(
                BUILDER.DIALOGUE_TMP
                / (
                    "runtime_vm_integrated."
                    "post_bound_terminal_2546_checkpoint.private.v1.jsonl"
                )
            ),
            BUILDER.EXPECTED_LEDGER_SHA256,
        )

    def test_public_counts_digests_and_proofs_match_contract(self) -> None:
        result = self.report["result"]
        proof = self.report["proof"]
        self.assertEqual(result["accepted_site_count"], 35)
        self.assertEqual(result["rewrite_coordinate_count"], 33)
        self.assertEqual(result["keep_coordinate_count"], 2)
        self.assertEqual(result["reject_coordinate_count"], 30)
        self.assertEqual(result["accepted_root_count"], 35)
        self.assertEqual(result["rejected_root_count"], 30)
        self.assertEqual(
            result["potential_promotion_coordinate_count"],
            65,
        )
        self.assertEqual(result["blocked_pending_coordinate_count"], 79)
        self.assertEqual(proof["assembly_branches_recorded"], 455)
        self.assertEqual(proof["accepted_assembly_branches"], 245)
        self.assertEqual(proof["rejected_assembly_branches"], 210)
        self.assertTrue(
            proof[
                "all_accepted_current_relative_raw_g1n_nonexpanding"
            ]
        )
        self.assertTrue(proof["all_accepted_register_branches_proven"])
        self.assertTrue(proof["all_changed_record_control_gaps_preserved"])
        self.assertEqual(
            proof["auxiliary_language_available_counts"],
            {"en": 29, "jp": 65, "sc": 34, "tc": 34},
        )
        self.assertEqual(
            proof["assembly_canonical_sha256"],
            BUILDER.EXPECTED_ASSEMBLY_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
