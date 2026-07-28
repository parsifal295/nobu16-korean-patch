#!/usr/bin/env python3
"""Tests for the PK selector-1174 chunk-0 semantic/runtime review."""

from __future__ import annotations

import importlib.util
import json
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

    def test_all_55_sites_and_385_selected_branches_are_proven(self) -> None:
        rows = self.evidence["site_reviews"]
        self.assertEqual(len(rows), 55)
        self.assertEqual([row["ordinal"] for row in rows], list(range(55)))
        self.assertEqual(
            sum(len(row["assemblies"]) for row in rows),
            385,
        )
        self.assertEqual(
            Counter(row["decision"] for row in rows),
            Counter({"rewrite": 54, "keep": 1}),
        )
        for row in rows:
            self.assertTrue(
                row["all_seven_grammar_and_spacing_branches_proven"]
            )
            self.assertTrue(
                row["all_seven_width_branches_nonexpanding"]
            )
            control = row["control_and_encoding_proof"]
            self.assertTrue(control["literal_linebreak_counts_preserved"])
            self.assertTrue(control["record_control_gaps_preserved"])
            self.assertTrue(control["reviewed_utf16le_encodable"])
            authority = row["multilingual_authority"]
            self.assertTrue(authority["fresh_review_completed"])
            self.assertTrue(authority["historical_factuality_reviewed"])
            self.assertTrue(authority["jp_is_semantic_authority"])
            self.assertTrue(authority["speaker_tone_reviewed"])
            for branch in row["assemblies"]:
                self.assertEqual(branch["reviewed_terminal"], "")
                self.assertEqual(
                    branch["terminal_semantic"],
                    "korean_zero_width_honorific_prefix",
                )
                self.assertTrue(branch["grammar_and_spacing_proven"])
                self.assertTrue(branch["line_count_match"])
                self.assertTrue(
                    branch["current_relative_raw_g1n_nonexpanding"]
                )

    def test_multilingual_and_historical_authority_was_exhaustive(self) -> None:
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
        historical = {
            row["site"]: row["historical_terms_reviewed"]
            for row in rows
            if row["historical_terms_reviewed"]
        }
        self.assertEqual(historical, {"6:4875:1:0": ["感状", "감장"]})

    def test_spacing_and_predicate_stems_are_runtime_aware(self) -> None:
        by_site = {
            row["site"]: row for row in self.evidence["site_reviews"]
        }
        self.assertEqual(
            by_site["6:1430:2:0"]["reviewed_left_translation"],
            "\n반드시 ",
        )
        self.assertEqual(
            by_site["6:1430:2:0"]["reviewed_right_translation"],
            "기대에 부응하",
        )
        self.assertEqual(
            by_site["6:4848:2:0"]["reviewed_left_translation"],
            "\n곧 ",
        )
        self.assertEqual(
            by_site["6:4848:2:0"]["reviewed_right_translation"],
            "준비",
        )
        self.assertEqual(
            by_site["7:2491:3:0"]["reviewed_left_translation"],
            "의 안을 ",
        )
        self.assertEqual(
            by_site["7:2491:3:0"]["reviewed_right_translation"],
            "봐 ",
        )

    def test_cross_overlap_is_renewed_not_promoted_twice(self) -> None:
        assignment = BUILDER.load_json(BUILDER.ASSIGNMENT_PATH)
        overlap = set(
            assignment["chunks"][0]["cross_family_overlap_coordinates"]
        )
        overlap_rows = [
            row for row in self.decisions
            if row["coordinate"] in overlap
        ]
        self.assertEqual(len(overlap_rows), 5)
        self.assertEqual(
            Counter(row["action"] for row in overlap_rows),
            Counter(
                {
                    "cross_translation_override_and_verification_renewal": 2,
                    "cross_verification_renewal": 3,
                }
            ),
        )
        for row in overlap_rows:
            self.assertEqual(
                row["overlap_owner"],
                "selector568_1096_cross_family",
            )
            self.assertNotIn("runtime_promotion", row["action"])

    def test_disjoint_promotions_and_existing_renewals_are_exact(self) -> None:
        actions = Counter(row["action"] for row in self.decisions)
        self.assertEqual(
            actions,
            Counter(
                {
                    "cross_translation_override_and_verification_renewal": 2,
                    "cross_verification_renewal": 3,
                    "runtime_promotion": 33,
                    "translation_override_and_runtime_promotion": 69,
                    "translation_override_and_verification_renewal": 45,
                }
            ),
        )
        self.assertEqual(len(self.decisions), 152)
        self.assertEqual(
            len(
                {
                    row["coordinate"] for row in self.decisions
                    if "runtime_promotion" in row["action"]
                }
            ),
            102,
        )
        self.assertFalse(
            any("hold" in row["action"] for row in self.decisions)
        )
        for row in self.decisions:
            self.assertEqual(row["runtime_review"], "verified")
            self.assertEqual(row["fresh_semantic_review"], "approved")
            self.assertEqual(
                row["reviewed_utf16le_sha256"],
                BUILDER.utf16le_sha256(row["reviewed_translation"]),
            )

    def test_overlay_is_reversible_and_deterministic(self) -> None:
        digests = self.evidence["digests"]
        self.assertEqual(
            digests["reviewed_candidate_sha256"],
            BUILDER.EXPECTED_REVIEWED_CANDIDATE_SHA256,
        )
        self.assertEqual(
            digests["reverse_overlay_sha256"],
            BUILDER.EXPECTED_CROSS_CANDIDATE_SHA256,
        )
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

    def test_public_report_is_source_free_and_not_event_layout(self) -> None:
        decoded = self.outputs["public_content"].decode("ascii")
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
        self.assertNotIn('"reviewed_translation"', decoded)
        self.assertNotIn("max_line_px", decoded)
        self.assertEqual(self.public["resource"], "MSG_PK/JP/msggame.bin")
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
