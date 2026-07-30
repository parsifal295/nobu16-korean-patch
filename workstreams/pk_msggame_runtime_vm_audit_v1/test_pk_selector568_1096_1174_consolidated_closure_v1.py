#!/usr/bin/env python3
"""Regression tests for the selector-568/1096/1174 direct consolidation."""

from __future__ import annotations

import copy
import importlib.util
import itertools
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = (
    SCRIPT.parent
    / "build_pk_selector568_1096_1174_consolidated_closure_v1.py"
)


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
    "pk_selector568_1096_1174_consolidated_test_builder_v1",
)


class Selector56810961174ConsolidatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = BUILDER.build_outputs()
        BUILDER.validate_frozen(cls.bundle)

    def test_frozen_inputs_and_outputs_match(self) -> None:
        inputs = {
            BUILDER.OFFICIAL_PRIVATE_PATH:
                BUILDER.EXPECTED_OFFICIAL_PRIVATE_SHA256,
            BUILDER.OFFICIAL_PUBLIC_PATH:
                BUILDER.EXPECTED_OFFICIAL_PUBLIC_SHA256,
            BUILDER.CROSS_DECISION_PATH:
                BUILDER.EXPECTED_CROSS_DECISION_SHA256,
            BUILDER.CROSS_EVIDENCE_PATH:
                BUILDER.EXPECTED_CROSS_EVIDENCE_SHA256,
            BUILDER.CHUNK0_BUILDER_PATH:
                BUILDER.EXPECTED_CHUNK0_BUILDER_SHA256,
            BUILDER.CHUNK0_DECISION_PATH:
                BUILDER.EXPECTED_CHUNK0_DECISION_SHA256,
            BUILDER.CHUNK0_EVIDENCE_PATH:
                BUILDER.EXPECTED_CHUNK0_EVIDENCE_SHA256,
            BUILDER.CHUNK0_PUBLIC_PATH:
                BUILDER.EXPECTED_CHUNK0_PUBLIC_SHA256,
            BUILDER.CHUNK1_BUILDER_PATH:
                BUILDER.EXPECTED_CHUNK1_BUILDER_SHA256,
            BUILDER.CHUNK1_PRIVATE_GENERATOR_PATH:
                BUILDER.EXPECTED_CHUNK1_PRIVATE_GENERATOR_SHA256,
            BUILDER.CHUNK1_PRIVATE_PATH:
                BUILDER.EXPECTED_CHUNK1_PRIVATE_SHA256,
            BUILDER.CHUNK1_PUBLIC_PATH:
                BUILDER.EXPECTED_CHUNK1_PUBLIC_SHA256,
        }
        for path, digest in inputs.items():
            self.assertIsNotNone(digest)
            self.assertEqual(BUILDER.sha256_file(path), digest)
        outputs = {
            BUILDER.DEFAULT_AUDIT_OUTPUT: (
                BUILDER.EXPECTED_AUDIT_OUTPUT_SHA256,
                self.bundle["audit_content"],
            ),
            BUILDER.DEFAULT_PROMOTION_OUTPUT: (
                BUILDER.EXPECTED_PROMOTION_OUTPUT_SHA256,
                self.bundle["promotion_content"],
            ),
            BUILDER.DEFAULT_DECISION_OUTPUT: (
                BUILDER.EXPECTED_DECISION_OUTPUT_SHA256,
                self.bundle["decision_content"],
            ),
            BUILDER.DEFAULT_EVIDENCE_OUTPUT: (
                BUILDER.EXPECTED_EVIDENCE_OUTPUT_SHA256,
                self.bundle["evidence_content"],
            ),
        }
        for path, (digest, content) in outputs.items():
            self.assertIsNotNone(digest)
            self.assertEqual(BUILDER.sha256_file(path), digest)
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_direct_union_removes_cross_only_overpromotion(self) -> None:
        inputs = self.bundle["inputs"]
        union = self.bundle["union"]
        cross = set(inputs["cross_map"])
        chunk0 = set(inputs["chunk0_map"])
        chunk1 = set(inputs["chunk1_map"])
        self.assertEqual(len(cross), 920)
        self.assertEqual(len(chunk0), 152)
        self.assertEqual(len(cross & chunk0), 6)
        self.assertEqual(len(cross & chunk1), 17)
        self.assertFalse(chunk0 & chunk1)
        self.assertEqual(
            len(inputs["chunk0_overlap"])
            + len(inputs["cross_renewals1"]),
            18,
        )
        self.assertEqual(len(union["union"]), 1173)
        self.assertEqual(len(union["promotions"]), 628)
        self.assertEqual(len(union["renewals"]), 545)
        self.assertEqual(
            self.bundle["audit"]["result"]["pending_rows_after"], 7268
        )
        self.assertEqual(
            self.bundle["audit"]["proof"]["demotion_rows"], 0
        )

    def test_owner_resolution_is_order_independent(self) -> None:
        reference = self.bundle["union"]
        for order in itertools.permutations(("cross", "chunk0", "chunk1")):
            resolved = BUILDER.resolve_union(self.bundle["inputs"], order)
            self.assertEqual(
                resolved["final_translation"],
                reference["final_translation"],
            )
            self.assertEqual(resolved["promotions"], reference["promotions"])
            self.assertEqual(resolved["renewals"], reference["renewals"])

    def test_all_promotions_use_normal_integrated_row_contract(self) -> None:
        union = self.bundle["union"]
        rows = {
            str(row["coordinate"]): row
            for row in self.bundle["updated_rows"]
        }
        evidence = {
            str(row["coordinate"]): row
            for row in self.bundle["evidence_rows"]
        }
        self.assertEqual(set(rows), union["union"])
        self.assertEqual(set(evidence), union["union"])
        for coordinate in union["promotions"]:
            row = rows[coordinate]
            self.assertEqual(row["scope_classification"], "retranslated")
            self.assertEqual(row["layout_review"], "runtime_verified")
            self.assertEqual(row["runtime_review"], "verified")
            self.assertEqual(row["semantic_review"], "approved")
            self.assertTrue(
                evidence[coordinate]["current81b4_rebase"][
                    "actual_runtime_promotion"
                ]
            )
        for coordinate, row in rows.items():
            self.assertEqual(
                row["runtime_vm_verification"],
                evidence[coordinate],
            )
            self.assertEqual(
                row["schema"],
                self.bundle["inputs"]["official"][
                    ("pk_msggame", coordinate)
                ]["schema"],
            )

    def test_all_assembly_and_repair_proofs_are_bound(self) -> None:
        assemblies = self.bundle["assemblies"]
        proof = self.bundle["audit"]["proof"]
        self.assertEqual(proof["cross_accepted_assembly_rows"], 2114)
        self.assertEqual(
            proof["cross_accepted_assembly_sha256"],
            BUILDER.EXPECTED_CROSS_ASSEMBLY_SHA256,
        )
        self.assertEqual(
            len(assemblies["selector1174_manifest"]), 805
        )
        self.assertEqual(
            len(assemblies["chunk0_overlap_branch_manifest"]), 14
        )
        self.assertEqual(
            len(assemblies["repair_selector1174_manifest"]), 14
        )
        self.assertEqual(len(assemblies["dependency_manifest"]), 7)
        self.assertEqual(len(assemblies["repair_roots"]), 2)
        self.assertEqual(len(assemblies["repair_coordinates"]), 10)
        self.assertEqual(len(assemblies["repair_overrides"]), 4)
        self.assertTrue(
            assemblies["repair_overrides"]
            <= self.bundle["inputs"]["required_cross_overrides1"]
        )

    def test_archive_is_single_build_reversible_and_control_safe(self) -> None:
        candidate = self.bundle["candidate"]
        self.assertEqual(
            candidate["reverse_sha256"],
            BUILDER.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        )
        self.assertEqual(
            candidate["final_sha256"],
            BUILDER.EXPECTED_FINAL_CANDIDATE_SHA256,
        )
        self.assertEqual(
            candidate["final_sha256"],
            self.bundle["audit"]["result"]["final_candidate_sha256"],
        )
        self.assertTrue(
            self.bundle["audit"]["proof"][
                "single_archive_rebuild_from_resolved_coordinate_union"
            ]
        )
        self.assertTrue(
            self.bundle["audit"]["proof"]["record_control_gaps_preserved"]
        )

    def test_tamper_changes_the_frozen_candidate(self) -> None:
        tampered_inputs = copy.deepcopy(self.bundle["inputs"])
        coordinate = next(iter(tampered_inputs["disjoint_promotions1"]))
        tampered_inputs["chunk1_map"][coordinate] += " "
        with self.assertRaises(BUILDER.ConsolidatedError):
            BUILDER.resolve_union(tampered_inputs)

    def test_two_full_runs_are_byte_identical(self) -> None:
        second = BUILDER.build_outputs()
        self.assertEqual(
            BUILDER.output_hashes(second),
            BUILDER.output_hashes(self.bundle),
        )
        self.assertEqual(
            second["candidate"]["final_sha256"],
            self.bundle["candidate"]["final_sha256"],
        )

    def test_reports_are_source_free_steam_unchanged_and_check_passes(
        self,
    ) -> None:
        combined = (
            self.bundle["audit_content"]
            + self.bundle["promotion_content"]
        )
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
                r"\uf900-\ufaff]",
                combined,
            )
        )
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+)?\b", combined))
        self.assertNotIn('"translation"', combined)
        self.assertFalse(self.bundle["audit"]["steam_write_performed"])
        self.assertFalse(self.bundle["promotion"]["steam_write_performed"])
        self.assertEqual(
            self.bundle["steam_before"], self.bundle["steam_after"]
        )
        self.assertEqual(BUILDER.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
