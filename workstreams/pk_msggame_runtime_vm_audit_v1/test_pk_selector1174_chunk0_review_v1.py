#!/usr/bin/env python3
"""Source-free tests for the selector-1174 chunk-0 review validator."""

from __future__ import annotations

import copy
import importlib.util
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector1174_chunk0_review_v1.py"


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
    "pk_selector1174_chunk0_review_test_builder_v1",
)


class Selector1174Chunk0ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = BUILDER.build_outputs()
        BUILDER.validate_frozen(cls.outputs)
        cls.evidence = cls.outputs["evidence"]
        cls.public = cls.outputs["public"]
        cls.decisions = cls.outputs["decision_rows"]

    def test_frozen_private_and_public_artifacts_match(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PRIVATE_DECISIONS_PATH),
            BUILDER.EXPECTED_DECISION_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PRIVATE_EVIDENCE_PATH),
            BUILDER.EXPECTED_EVIDENCE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.PRIVATE_DECISIONS_PATH.read_bytes(),
            self.outputs["decisions_content"],
        )
        self.assertEqual(
            BUILDER.PRIVATE_EVIDENCE_PATH.read_bytes(),
            self.outputs["evidence_content"],
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_bytes(),
            self.outputs["public_content"],
        )

    def test_review_counts_and_runtime_proofs_are_exact(self) -> None:
        counts = self.evidence["counts"]
        self.assertEqual(
            counts,
            {
                "accepted_sites": 55,
                "assembly_branches": 385,
                "cross_owned_renewals": 5,
                "decision_rows": 152,
                "disjoint_runtime_promotions": 102,
                "holds": 0,
                "keep_sites": 1,
                "rewrite_sites": 54,
                "roots": 54,
                "sites": 55,
                "translation_overrides": 116,
            },
        )
        rows = self.evidence["site_reviews"]
        self.assertEqual(len(rows), 55)
        self.assertEqual([row["ordinal"] for row in rows], list(range(55)))
        self.assertEqual(sum(len(row["assemblies"]) for row in rows), 385)
        self.assertEqual(
            Counter(row["decision"] for row in rows),
            Counter({"rewrite": 54, "keep": 1}),
        )
        self.assertTrue(
            all(
                row["all_seven_grammar_and_spacing_branches_proven"]
                and row["all_seven_width_branches_nonexpanding"]
                and row["control_and_encoding_proof"][
                    "record_control_gaps_preserved"
                ]
                and row["control_and_encoding_proof"][
                    "literal_linebreak_counts_preserved"
                ]
                and row["multilingual_authority"][
                    "historical_factuality_reviewed"
                ]
                and row["multilingual_authority"]["speaker_tone_reviewed"]
                for row in rows
            )
        )
        self.assertTrue(
            all(
                branch["grammar_and_spacing_proven"]
                and branch["line_count_match"]
                and branch["current_relative_raw_g1n_nonexpanding"]
                for row in rows
                for branch in row["assemblies"]
            )
        )

    def test_multilingual_coverage_is_exhaustive(self) -> None:
        rows = self.evidence["site_reviews"]
        available = {
            language: sum(
                row["multilingual_authority"][language]["available"]
                for row in rows
            )
            for language in ("jp", "sc", "tc", "en")
        }
        self.assertEqual(
            available,
            {"jp": 55, "sc": 17, "tc": 17, "en": 13},
        )
        self.assertEqual(
            sum(bool(row["historical_terms_reviewed"]) for row in rows),
            1,
        )

    def test_overlap_and_promotion_actions_are_exact(self) -> None:
        actions = Counter(row["action"] for row in self.decisions)
        self.assertEqual(actions, Counter(BUILDER.EXPECTED_ACTION_COUNTS))
        self.assertEqual(len(self.decisions), 152)
        self.assertEqual(
            sum("runtime_promotion" in row["action"] for row in self.decisions),
            102,
        )
        self.assertEqual(
            sum(row["overlap_owner"] is not None for row in self.decisions),
            5,
        )
        self.assertFalse(any("hold" in row["action"] for row in self.decisions))
        self.assertTrue(
            all(
                row["runtime_review"] == "verified"
                and row["fresh_semantic_review"] == "approved"
                and row["historical_factuality_review"] == "approved"
                and row["speaker_tone_review"] == "approved"
                for row in self.decisions
            )
        )

    def test_candidate_reverse_overlay_and_digests_are_frozen(self) -> None:
        digests = self.evidence["digests"]
        self.assertEqual(
            digests["reviewed_candidate_sha256"],
            BUILDER.EXPECTED_REVIEWED_CANDIDATE_SHA256,
        )
        self.assertEqual(
            digests["reverse_overlay_sha256"],
            BUILDER.EXPECTED_CROSS_CANDIDATE_SHA256,
        )
        self.assertEqual(
            digests["decision_coordinate_sha256"],
            BUILDER.EXPECTED_DECISION_COORDINATE_SHA256,
        )
        self.assertEqual(
            digests["override_coordinate_sha256"],
            BUILDER.EXPECTED_OVERRIDE_COORDINATE_SHA256,
        )
        self.assertEqual(
            digests["assembly_canonical_sha256"],
            BUILDER.EXPECTED_ASSEMBLY_SHA256,
        )

    def test_two_runs_are_identical(self) -> None:
        second = BUILDER.build_outputs()
        self.assertEqual(
            second["decisions_content"],
            self.outputs["decisions_content"],
        )
        self.assertEqual(
            second["evidence_content"],
            self.outputs["evidence_content"],
        )
        self.assertEqual(
            second["public_content"],
            self.outputs["public_content"],
        )

    def test_tampered_decision_stream_is_rejected(self) -> None:
        tampered = self.outputs["decisions_content"] + b"\n"
        with self.assertRaisesRegex(
            BUILDER.ReviewError,
            "decision bytes drifted",
        ):
            BUILDER.validate_decision_bytes(
                tampered,
                self.outputs["decisions_content"],
            )
        altered_rows = copy.deepcopy(self.decisions)
        altered_rows[0]["runtime_review"] = "changed"
        altered = b"".join(
            BUILDER.canonical_bytes(row) + b"\n" for row in altered_rows
        )
        with self.assertRaisesRegex(BUILDER.ReviewError, "approval drifted"):
            BUILDER.build_outputs(decisions_content=altered)

    def test_tampered_evidence_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.evidence)
        tampered["counts"]["decision_rows"] += 1
        with self.assertRaisesRegex(BUILDER.ReviewError, "counts drifted"):
            BUILDER.build_outputs(evidence=tampered)

    def test_public_report_is_source_free(self) -> None:
        decoded = self.outputs["public_content"].decode("ascii")
        policy = self.public["distribution_policy"]
        self.assertFalse(policy["tracked_builder_contains_dialogue_bodies"])
        self.assertFalse(policy["tracked_test_contains_dialogue_bodies"])
        self.assertTrue(policy["tracked_validator_uses_frozen_private_hashes"])
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
        self.assertNotIn('"reviewed_translation"', decoded)
        self.assertFalse(self.public["steam_write_performed"])
        self.assertEqual(
            self.public["guards"]["steam_archive_sha256_before"],
            self.public["guards"]["steam_archive_sha256_after"],
        )

    def test_output_paths_are_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                BUILDER.ReviewError,
                "public output must use its fixed path",
            ):
                BUILDER.main(
                    [
                        "--public-output",
                        str(Path(temporary) / "public.json"),
                    ]
                )


if __name__ == "__main__":
    unittest.main()
