#!/usr/bin/env python3
"""Tests for the private 2546 simple-caller retranslation proposal."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_bound_terminal_2546_simple_caller_"
    "retranslation_proposal_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(
    "pk_bound_terminal_2546_simple_caller_proposal_test_builder",
    BUILDER_PATH,
)


class SimpleCallerRetranslationProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.private_content,
            cls.public_content,
            cls.private,
            cls.public,
        ) = BUILDER.build_outputs()

    def test_outputs_are_frozen_and_match_disk(self) -> None:
        self.assertEqual(
            BUILDER.sha256_bytes(self.private_content.encode("utf-8")),
            BUILDER.EXPECTED_PRIVATE_OUTPUT_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.public_content.encode("ascii")),
            BUILDER.EXPECTED_PUBLIC_OUTPUT_SHA256,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PRIVATE_OUTPUT.read_text(encoding="utf-8"),
            self.private_content,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii"),
            self.public_content,
        )

    def test_private_review_covers_every_root_coordinate_and_register(
        self,
    ) -> None:
        self.assertEqual(len(self.private["roots"]), 9)
        self.assertEqual(
            len(self.private["manifests"]["decisions"]),
            28,
        )
        self.assertEqual(
            len(self.private["manifests"]["assemblies"]),
            63,
        )
        self.assertEqual(
            self.private["counts"]["pending_coordinate_verdicts"],
            {"keep": 9, "rewrite": 14, "reject": 0},
        )
        self.assertEqual(
            self.private["counts"]["verified_coordinate_verdicts"],
            {"keep": 2, "rewrite": 3, "reject": 0},
        )
        for root in self.private["roots"]:
            self.assertEqual(root["verdict"], "rewrite")
            self.assertEqual(len(root["register_assemblies"]), 7)
            self.assertTrue(
                root["proof"][
                    "all_7_register_assemblies_grammar_pass"
                ]
            )
            self.assertTrue(
                root["proof"][
                    "all_7_register_assemblies_current_relative_"
                    "raw_g1n_nonexpanding"
                ]
            )
            for assembly in root["register_assemblies"]:
                self.assertTrue(
                    assembly["current_relative_nonexpanding"]
                )
                self.assertTrue(
                    all(
                        delta <= 0
                        for delta in assembly["width_delta_px"]
                    )
                )

    def test_public_report_is_source_free_and_proposal_only(self) -> None:
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3130-\u318f\u3400-\u4dbf"
                r"\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                self.public_content,
            )
        )
        self.assertIsNone(
            re.search(r"\b\d+:\d+(?::\d+)?\b", self.public_content)
        )
        policy = self.public["distribution_policy"]
        self.assertFalse(
            policy["tracked_report_contains_commercial_source_text"]
        )
        self.assertFalse(
            policy["tracked_report_contains_translated_dialogue_text"]
        )
        self.assertFalse(
            policy["tracked_report_contains_exact_coordinates"]
        )
        self.assertTrue(self.public["integration"]["proposal_only"])
        self.assertFalse(
            self.public["integration"][
                "shared_runtime_vm_integration_modified"
            ]
        )
        self.assertFalse(self.public["steam_write_performed"])

    def test_public_counts_and_seals_match_contract(self) -> None:
        self.assertEqual(
            self.public["bindings"]["checkpoint_private_sha256"],
            BUILDER.EXPECTED_CHECKPOINT_SHA256,
        )
        self.assertEqual(
            self.public["bindings"]["checkpoint_candidate_sha256"],
            BUILDER.EXPECTED_CHECKPOINT_CANDIDATE_SHA256,
        )
        self.assertEqual(
            self.public["bindings"]["proposal_candidate_sha256"],
            BUILDER.EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        )
        self.assertEqual(
            self.public["bindings"]["residual_ledger_sha256"],
            BUILDER.EXPECTED_LEDGER_SHA256,
        )
        self.assertEqual(self.public["scope"]["blocker_roots"], 9)
        self.assertEqual(self.public["scope"]["pending_rows"], 23)
        self.assertEqual(
            self.public["proposal"]["potential_runtime_promotion_rows"],
            23,
        )
        self.assertEqual(
            self.public["proposal"][
                "required_verification_renewal_rows"
            ],
            5,
        )
        self.assertEqual(
            self.public["proposal"]["coordinate_verdict_counts"],
            {"keep": 11, "rewrite": 17, "reject": 0},
        )
        self.assertEqual(
            self.public["proof"]["register_assemblies"],
            63,
        )
        self.assertLessEqual(
            self.public["proof"]["maximum_width_delta_px"],
            0,
        )

    def test_output_path_boundary_rejects_private_escape(self) -> None:
        args = argparse.Namespace(
            private_output=WORKSTREAM / "private.json",
            public_output=BUILDER.DEFAULT_PUBLIC_OUTPUT,
        )
        with self.assertRaises(BUILDER.ProposalError):
            BUILDER.validate_output_paths(args)

    def test_public_validator_rejects_body_text(self) -> None:
        bad_public = json.loads(self.public_content)
        bad_public["leak"] = "\ud55c\uae00"
        bad_content = BUILDER.canonical_json(
            bad_public,
            source_free=False,
        )
        with self.assertRaises(BUILDER.ProposalError):
            BUILDER.validate_outputs(
                self.private_content,
                bad_content,
                self.private,
                bad_public,
            )


if __name__ == "__main__":
    unittest.main()
