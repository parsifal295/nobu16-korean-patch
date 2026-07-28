#!/usr/bin/env python3
"""Regression tests for the selector-568 current81B4 family closure."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = WORKSTREAM / "build_pk_selector568_family_consolidated_closure_v1.py"
os.environ.setdefault(
    "NOBU16_DIALOGUE_STEAM_ROOT",
    str(
        WORKSTREAM.parents[1]
        / "tmp"
        / "pc_dialogue_full_retranslation_v0150"
        / "development_steam_root_pre_base_runtime_apply_13a404f"
    ),
)


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "pk_selector568_family_consolidated_test_builder", BUILDER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector568FamilyConsolidatedClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = B.build_outputs()
        cls.family = cls.bundle["family"]
        cls.updated = {
            str(row["coordinate"]): row for row in cls.bundle["updated_rows"]
        }
        cls.evidence = {
            str(row["coordinate"]): row for row in cls.bundle["evidence_rows"]
        }
        cls.official_rows, cls.official = B.load_official()

    def test_frozen_inputs_and_outputs(self) -> None:
        self.assertEqual(
            B.sha256_file(B.OFFICIAL_PRIVATE_PATH),
            B.EXPECTED_OFFICIAL_PRIVATE_SHA256,
        )
        self.assertEqual(
            B.sha256_file(B.SELECTOR538_EVIDENCE_PATH),
            B.EXPECTED_SELECTOR538_EVIDENCE_SHA256,
        )
        self.assertEqual(
            B.sha256_file(B.GHIDRA_CONTRACT_PATH),
            B.EXPECTED_GHIDRA_CONTRACT_SHA256,
        )
        self.assertEqual(
            B.output_hashes(self.bundle),
            (
                B.EXPECTED_AUDIT_OUTPUT_SHA256,
                B.EXPECTED_PROMOTION_OUTPUT_SHA256,
                B.EXPECTED_DECISION_OUTPUT_SHA256,
                B.EXPECTED_EVIDENCE_OUTPUT_SHA256,
                B.EXPECTED_CROSS_PRIVATE_SHA256,
            ),
        )

    def test_exact_union_overlap_and_translation_conflicts(self) -> None:
        self.assertEqual(len(self.family["decisions"]), 503)
        self.assertEqual(len(self.family["promotions"]), 242)
        self.assertEqual(len(self.family["actual_promotions"]), 225)
        self.assertEqual(len(self.family["superseded_promotions"]), 17)
        self.assertEqual(len(self.family["renewals"]), 261)
        self.assertEqual(len(self.family["overrides"]), 156)
        self.assertEqual(
            [row["translation_difference_rows"] for row in self.family["pairwise"]],
            [59, 79, 50],
        )
        self.assertTrue(
            all(row["decision_overlap_rows"] == 261 for row in self.family["pairwise"])
        )
        self.assertTrue(
            all(row["promotion_overlap_rows"] == 0 for row in self.family["pairwise"])
        )
        self.assertTrue(
            all(row["override_overlap_rows"] == 0 for row in self.family["pairwise"])
        )
        self.assertEqual(
            Counter(self.family["action_by_coordinate"].values()),
            Counter(B.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(len(self.family["override_owner"]), 156)
        self.assertEqual(len(set(self.family["override_owner"])), 156)

    def test_joint_accepted_assemblies_and_candidate(self) -> None:
        candidate = self.bundle["candidate"]
        self.assertEqual(candidate["official_sha256"], B.EXPECTED_OFFICIAL_CANDIDATE_SHA256)
        self.assertEqual(candidate["family_sha256"], B.EXPECTED_FAMILY_CANDIDATE_SHA256)
        self.assertEqual(
            len(candidate["accepted_assembly_manifest"]),
            B.EXPECTED_ACCEPTED_ASSEMBLIES,
        )
        self.assertEqual(
            candidate["accepted_assembly_sha256"],
            B.EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
        )
        self.assertEqual(
            [len(chunk["validated"]["accepted_sites"]) for chunk in self.bundle["chunks"]],
            [62, 47, 60],
        )
        for branch in candidate["accepted_assembly_manifest"]:
            reviewed_widths = branch[5]
            current_widths = branch[6]
            self.assertEqual(len(reviewed_widths), len(current_widths))
            self.assertTrue(
                all(reviewed <= current for reviewed, current in zip(reviewed_widths, current_widths))
            )

    def test_selector538_evidence_is_exactly_superseded(self) -> None:
        overlap = self.family["selector538_overlap"]
        self.assertEqual(len(overlap), 36)
        self.assertEqual(
            B.coordinate_digest(overlap),
            B.EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256,
        )
        self.assertEqual(len(overlap & self.family["promotions"]), 17)
        self.assertEqual(len(overlap & self.family["renewals"]), 19)
        for coordinate in overlap:
            binding = self.evidence[coordinate][
                "selector538_family_evidence_supersession"
            ]
            self.assertTrue(binding["prior_runtime_vm_verification_exact_match"])
            self.assertEqual(
                binding["evidence_file_sha256"],
                B.EXPECTED_SELECTOR538_EVIDENCE_SHA256,
            )

    def test_cross_family_correlation_and_ownership_guard(self) -> None:
        cross = self.bundle["cross"]["value"]
        self.assertEqual(cross["branch_count"], 14)
        self.assertEqual(len(cross["records"]), 2)
        guard = cross["correlation_guard"]
        self.assertTrue(guard["ordinal_correlated_pairs_authoritative"])
        self.assertTrue(guard["selector_expression_bytecode_shapes_identical"])
        self.assertEqual(len(guard["node_pairs"]), 6)
        self.assertEqual(
            {row["zero_normalized_bytecode_sha256"] for row in guard["node_pairs"]},
            set(B.EXPECTED_DISPATCH_SHAPE_SHA256.values()),
        )
        for record in cross["records"]:
            self.assertEqual(len(record["branches"]), 7)
            self.assertTrue(record["external1096_not_overridden_by_selector568_family"])
            for ordinal, branch in enumerate(record["branches"]):
                self.assertEqual(branch["ordinal"], ordinal)
                self.assertTrue(branch["current_relative_raw_g1n_nonexpanding"])
                self.assertTrue(all(delta <= 0 for delta in branch["line_deltas_px"]))
        self.assertEqual(
            B.coordinate_digest(self.family["external1096"]),
            B.EXPECTED_EXTERNAL1096_COORDINATE_SHA256,
        )
        for coordinate in self.family["external1096"]:
            self.assertNotIn(coordinate, self.family["overrides"])
            self.assertNotIn(B.OVERRIDE_FIELD, self.updated[coordinate])
            self.assertEqual(
                self.updated[coordinate]["translation"],
                self.official[("pk_msggame", coordinate)]["translation"],
            )
        for coordinate in self.family["selector568_cross"]:
            self.assertIn(coordinate, self.family["overrides"])
            self.assertIn(B.OVERRIDE_FIELD, self.updated[coordinate])

    def test_private_rows_and_pending_projection(self) -> None:
        self.assertEqual(len(self.updated), 503)
        self.assertEqual(set(self.updated), set(self.evidence))
        for coordinate, row in self.updated.items():
            self.assertEqual(row["runtime_vm_verification"], self.evidence[coordinate])
            self.assertEqual(row["runtime_review"], "verified")
            self.assertEqual(row["semantic_review"], "approved")
        merged = {
            (str(row["resource"]), str(row["coordinate"])): dict(row)
            for row in self.official_rows
        }
        for row in self.updated.values():
            merged[(str(row["resource"]), str(row["coordinate"]))] = row
        self.assertEqual(len(merged), B.EXPECTED_ROWS)
        self.assertEqual(
            sum(row.get("runtime_review") == "pending" for row in merged.values()),
            B.EXPECTED_PENDING_AFTER,
        )

    def test_source_free_reports_and_isolated_paths(self) -> None:
        coordinate_pattern = re.compile(r"\b\d+:\d+:\d+\b")
        cjk_pattern = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7a3]")
        for report in (self.bundle["audit"], self.bundle["promotion"]):
            encoded = json.dumps(report, ensure_ascii=False, sort_keys=True)
            self.assertIsNone(coordinate_pattern.search(encoded))
            self.assertIsNone(cjk_pattern.search(encoded))
            self.assertFalse(report["steam_write_performed"])
        self.assertEqual(self.bundle["steam_before"], self.bundle["steam_after"])
        self.assertTrue(str(B.DEFAULT_DECISION_OUTPUT).startswith(str(B.DIALOGUE_TMP)))
        self.assertTrue(str(B.DEFAULT_EVIDENCE_OUTPUT).startswith(str(B.DIALOGUE_TMP)))
        self.assertTrue(str(B.DEFAULT_CROSS_OUTPUT).startswith(str(B.DIALOGUE_TMP)))
        self.assertNotIn(
            "runtime_vm_integrated.private.v1.jsonl",
            {
                B.DEFAULT_AUDIT_OUTPUT.name,
                B.DEFAULT_PROMOTION_OUTPUT.name,
                B.DEFAULT_DECISION_OUTPUT.name,
                B.DEFAULT_EVIDENCE_OUTPUT.name,
                B.DEFAULT_CROSS_OUTPUT.name,
            },
        )


if __name__ == "__main__":
    unittest.main()
