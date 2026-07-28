#!/usr/bin/env python3
"""Tests for the immutable PK selector-610 review assignment."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector610_assignment_v1.py"


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pk_selector610_assignment_test_builder_v1", BUILDER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_builder()


class Selector610AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.private_content,
            cls.public_content,
            cls.manifest,
            cls.report,
        ) = BUILDER.build_outputs()
        BUILDER.validate_outputs(
            cls.private_content, cls.public_content, frozen=True
        )

    def test_frozen_inputs_outputs_and_ranking_handoff(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(
            self.report["inputs"]["official_integrated_ledger_sha256"],
            BUILDER.EXPECTED_INPUT_SHA256["ledger"],
        )
        self.assertEqual(self.report["scope"]["selector"], 610)

    def test_coverage_and_source_only_repair_register_are_exact(self) -> None:
        coverage = self.report["coverage"]
        self.assertEqual(coverage["candidate_call_site_count"], 230)
        self.assertEqual(coverage["candidate_call_root_count"], 230)
        self.assertEqual(coverage["source_call_site_count"], 243)
        self.assertEqual(coverage["source_only_repair_site_count"], 13)
        self.assertEqual(coverage["potential_current_pending_rows"], 192)
        self.assertEqual(
            len(self.manifest["scope"]["source_only_repair_sites"]), 13
        )

    def test_owned_overlap_and_template_partition_are_exact(self) -> None:
        coverage = self.report["coverage"]
        self.assertEqual(coverage["owned_overlap_root_count"], 30)
        self.assertEqual(coverage["owned_overlap_pending_rows"], 60)
        self.assertEqual(
            coverage["owned_overlap_selector_counts"],
            {
                "538": {"pending_root_count": 25, "pending_row_count": 50},
                "568": {"pending_root_count": 3, "pending_row_count": 7},
                "1096": {"pending_root_count": 1, "pending_row_count": 2},
                "1174": {"pending_root_count": 1, "pending_row_count": 1},
            },
        )
        chunks = self.report["assignment"]["chunks"]
        self.assertEqual(
            [
                (
                    row["site_count"],
                    row["pending_root_count"],
                    row["pending_row_upper_bound"],
                    row["owned_overlap_root_count"],
                    row["template_root_count"],
                    row["workload_weight"],
                )
                for row in chunks
            ],
            [
                (77, 36, 91, 5, 0, 1663),
                (77, 29, 53, 1, 0, 1666),
                (76, 24, 48, 24, 24, 1669),
            ],
        )

    def test_chunks_are_root_disjoint_and_exhaustive(self) -> None:
        chunks = self.manifest["chunks"]
        for left in range(3):
            for right in range(left + 1, 3):
                self.assertFalse(
                    set(chunks[left]["roots"]) & set(chunks[right]["roots"])
                )
        self.assertEqual(
            set().union(*(set(row["sites"]) for row in chunks)),
            set(self.manifest["scope"]["candidate_call_sites"]),
        )
        template_roots = {
            f"15:{record_id}" for record_id in range(1385, 1409)
        }
        self.assertTrue(template_roots <= set(chunks[2]["roots"]))
        self.assertFalse(
            template_roots
            & set(chunks[0]["roots"] + chunks[1]["roots"])
        )

    def test_public_is_source_free_and_steam_write_is_false(self) -> None:
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                self.public_content,
            )
        )
        self.assertIsNone(
            re.search(r"\b\d+:\d+(?::\d+){0,2}\b", self.public_content)
        )
        self.assertNotIn('"translation"', self.public_content)
        self.assertFalse(self.report["steam_write_performed"])

    def test_dispatch_contract_is_fixed_seven_way(self) -> None:
        dispatch = self.report["dispatch_contract"]
        self.assertTrue(dispatch["source_candidate_identical"])
        self.assertEqual(dispatch["node_count"], 13)
        self.assertEqual(dispatch["edge_count"], 13)
        self.assertEqual(dispatch["terminal_count"], 7)
        self.assertEqual(
            dispatch["terminal_coordinate_sha256"],
            BUILDER.EXPECTED_TERMINAL_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
