#!/usr/bin/env python3
"""Tests for the consolidated selector-538 chunks 0..3 closure."""

from __future__ import annotations

import copy
import importlib.util
import re
import sys
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = (
    SCRIPT.parent
    / "build_pk_selector538_family_consolidated_closure_v1.py"
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
    "pk_selector538_family_consolidated_closure_test_builder_v1",
)


class Selector538FamilyConsolidatedClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = BUILDER.build_outputs()
        cls.analysis = cls.bundle["analysis"]
        cls.updates = {
            row["coordinate"]: row
            for row in cls.bundle["updated_rows"]
        }
        cls.frozen = BUILDER.load_frozen_chunks()
        cls.chunks = cls.frozen["chunks"]

    def test_all_outputs_are_exactly_frozen(self) -> None:
        expected = {
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
        for path, (digest, content) in expected.items():
            with self.subTest(path=path):
                self.assertEqual(BUILDER.sha256_file(path), digest)
                self.assertEqual(
                    path.read_bytes(), content.encode("utf-8")
                )
        self.assertEqual(
            self.bundle["candidate_sha256"],
            BUILDER.EXPECTED_FAMILY_CANDIDATE_SHA256,
        )

    def test_family_union_and_pairwise_contract_is_exact(self) -> None:
        self.assertEqual(
            len(self.analysis["decisions"]),
            BUILDER.EXPECTED_DECISION_ROWS,
        )
        self.assertEqual(
            len(self.analysis["promotions"]),
            BUILDER.EXPECTED_PROMOTION_ROWS,
        )
        self.assertEqual(
            len(self.analysis["renewals"]),
            BUILDER.EXPECTED_RENEWAL_ROWS,
        )
        self.assertEqual(
            len(self.analysis["overrides"]),
            BUILDER.EXPECTED_OVERRIDE_ROWS,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(self.analysis["decisions"]),
            BUILDER.EXPECTED_DECISION_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(self.analysis["promotions"]),
            BUILDER.EXPECTED_PROMOTION_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(self.analysis["renewals"]),
            BUILDER.EXPECTED_RENEWAL_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(self.analysis["overrides"]),
            BUILDER.EXPECTED_OVERRIDE_COORDINATE_SHA256,
        )
        self.assertEqual(len(self.analysis["pairwise"]), 6)
        for pair in self.analysis["pairwise"]:
            with self.subTest(pair=pair):
                self.assertEqual(
                    pair["decision_overlap_rows"],
                    BUILDER.EXPECTED_PAIRWISE_DECISION_OVERLAP,
                )
                self.assertEqual(
                    pair["decision_overlap_sha256"],
                    BUILDER.EXPECTED_RENEWAL_COORDINATE_SHA256,
                )
                self.assertEqual(pair["promotion_overlap_rows"], 0)
                self.assertEqual(pair["override_overlap_rows"], 0)
                self.assertEqual(
                    pair["promotion_overlap_sha256"],
                    BUILDER.EXPECTED_EMPTY_COORDINATE_SHA256,
                )
                self.assertEqual(
                    pair["override_overlap_sha256"],
                    BUILDER.EXPECTED_EMPTY_COORDINATE_SHA256,
                )

    def test_chunk0_supersession_and_incremental_delta_are_exact(self) -> None:
        self.assertEqual(
            len(self.analysis["later_promotions"]),
            BUILDER.EXPECTED_INCREMENTAL_PROMOTION_ROWS,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(self.analysis["later_promotions"]),
            BUILDER.EXPECTED_LATER_PROMOTION_COORDINATE_SHA256,
        )
        self.assertEqual(
            len(self.analysis["later_renewal_overrides"]),
            BUILDER.EXPECTED_SUPERSEDED_RENEWAL_ROWS,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(
                self.analysis["later_renewal_overrides"]
            ),
            BUILDER.EXPECTED_SUPERSEDED_RENEWAL_COORDINATE_SHA256,
        )
        self.assertEqual(
            len(self.analysis["retained_chunk0_renewals"]),
            BUILDER.EXPECTED_RETAINED_CHUNK0_RENEWAL_ROWS,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(
                self.analysis["retained_chunk0_renewals"]
            ),
            BUILDER.EXPECTED_RETAINED_CHUNK0_RENEWAL_COORDINATE_SHA256,
        )
        self.assertEqual(
            len(self.analysis["later_effective_delta"]),
            BUILDER.EXPECTED_LATER_EFFECTIVE_DELTA_ROWS,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(
                self.analysis["later_effective_delta"]
            ),
            BUILDER.EXPECTED_LATER_EFFECTIVE_DELTA_COORDINATE_SHA256,
        )

    def test_shared_renewals_keep_the_unique_override_owner(self) -> None:
        chunk0_rows = self.chunks[0]["decision_rows"]
        winners = Counter()
        for coordinate in self.analysis["renewals"]:
            owner = self.analysis["renewal_winner_map"][coordinate]
            winners[owner] += 1
            expected = (
                self.chunks[owner]["decision_rows"][coordinate][
                    "translation"
                ]
                if owner
                else chunk0_rows[coordinate]["translation"]
            )
            self.assertEqual(
                self.updates[coordinate]["translation"],
                expected,
                coordinate,
            )
        self.assertEqual(
            dict(sorted(winners.items())),
            {0: 351, 1: 29, 2: 22, 3: 18},
        )
        self.assertEqual(
            BUILDER.canonical_sha256(
                self.analysis["renewal_winner_map"]
            ),
            BUILDER.EXPECTED_RENEWAL_WINNER_MAP_SHA256,
        )

    def test_actions_and_predecessor_supersession_are_bound_per_row(
        self,
    ) -> None:
        actions = Counter(
            row["runtime_vm_verification"]["action"]
            for row in self.bundle["updated_rows"]
        )
        self.assertEqual(dict(actions), BUILDER.EXPECTED_ACTION_COUNTS)
        predecessor_rows = BUILDER.index_rows(
            BUILDER.load_jsonl(BUILDER.PREDECESSOR_PRIVATE_PATH)
        )
        chunk0_rows = self.chunks[0]["decision_rows"]
        for row in self.bundle["updated_rows"]:
            coordinate = row["coordinate"]
            vm = row["runtime_vm_verification"]
            baseline = predecessor_rows[("pk_msggame", coordinate)]
            official = (
                chunk0_rows[coordinate]
                if coordinate in chunk0_rows
                else baseline
            )
            with self.subTest(coordinate=coordinate):
                self.assertEqual(
                    vm["predecessor_binding"][
                        "baseline_row_sha256"
                    ],
                    BUILDER.canonical_sha256(baseline),
                )
                self.assertEqual(
                    vm["predecessor_binding"]["official_row_sha256"],
                    BUILDER.canonical_sha256(official),
                )
                self.assertEqual(
                    vm["predecessor_binding"][
                        "chunk0_exactly_superseded"
                    ],
                    coordinate in chunk0_rows,
                )

    def test_pairwise_and_override_mutations_are_rejected(self) -> None:
        chunks = [
            {
                "decision_rows": copy.deepcopy(chunk["decision_rows"]),
                "overrides": set(chunk["overrides"]),
                "promotions": set(chunk["promotions"]),
                "renewals": set(chunk["renewals"]),
            }
            for chunk in self.chunks
        ]
        coordinate = next(iter(chunks[0]["promotions"]))
        chunks[1]["promotions"].add(coordinate)
        chunks[1]["decision_rows"][coordinate] = copy.deepcopy(
            chunks[0]["decision_rows"][coordinate]
        )
        with self.assertRaisesRegex(
            BUILDER.ClosureError, "decision overlap"
        ):
            BUILDER.analyze_family(chunks)

        chunks = [
            {
                "decision_rows": copy.deepcopy(chunk["decision_rows"]),
                "overrides": set(chunk["overrides"]),
                "promotions": set(chunk["promotions"]),
                "renewals": set(chunk["renewals"]),
            }
            for chunk in self.chunks
        ]
        coordinate = next(iter(chunks[0]["overrides"]))
        chunks[1]["overrides"].add(coordinate)
        with self.assertRaisesRegex(
            BUILDER.ClosureError, "override overlap"
        ):
            BUILDER.analyze_family(chunks)

    def test_public_reports_are_source_free_and_never_write_steam(
        self,
    ) -> None:
        combined = (
            self.bundle["audit_content"]
            + self.bundle["promotion_content"]
        )
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3130-\u318f\u3400-\u4dbf"
                r"\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                combined,
            )
        )
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+)?\b", combined))
        self.assertNotIn('"translation"', combined)
        self.assertNotIn('"exact_maps"', combined)
        self.assertFalse(self.bundle["audit"]["steam_write_performed"])
        self.assertFalse(
            self.bundle["promotion"]["steam_write_performed"]
        )


if __name__ == "__main__":
    unittest.main()
