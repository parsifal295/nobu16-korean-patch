#!/usr/bin/env python3
"""Regression tests for the exact PK terminal+caller closure layer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = (
    SCRIPT.parent / "build_pk_bound_terminal_caller_full_closure_v1.py"
)


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pk_bound_terminal_caller_full_closure_builder_test_v1",
        BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load caller closure builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class BoundTerminalCallerFullClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.steam_before = {
            "base": B.HONORIFIC.live_hash(B.LIVE_STEAM_BASE),
            "pk": B.HONORIFIC.live_hash(B.LIVE_STEAM_PK),
        }
        (
            cls.decision_content,
            cls.evidence_content,
            cls.audit_content,
            cls.promotion_content,
            cls.audit,
            cls.bundle,
        ) = B.build_outputs()
        B.validate_outputs(
            decision_content=cls.decision_content,
            evidence_content=cls.evidence_content,
            audit_content=cls.audit_content,
            promotion_content=cls.promotion_content,
            audit=cls.audit,
            bundle=cls.bundle,
        )

    def test_exact_source_owned_map(self) -> None:
        source = BUILDER_PATH.read_text(encoding="utf-8")
        compact = json.dumps(
            B.TRANSLATION_OVERRIDES,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(len(B.TRANSLATION_OVERRIDES), 261)
        self.assertEqual(
            hashlib.sha256(compact).hexdigest().upper(),
            B.EXPECTED_OVERRIDE_MAP_COMPACT_JSON_SHA256,
        )
        self.assertIn("TRANSLATION_OVERRIDES = {", source)
        self.assertNotIn("base64", source)
        self.assertNotIn("zlib", source)
        self.assertEqual(
            set(B.TRANSLATION_OVERRIDES)
            - self.bundle["analysis"]["ledger_override_coordinates"],
            B.EXPECTED_UNTRACKED_LITERAL_OVERRIDES,
        )

    def test_candidate_and_full_assembly_are_frozen(self) -> None:
        analysis = self.bundle["analysis"]
        self.assertEqual(
            B.sha256_bytes(analysis["candidate_blob"]),
            B.EXPECTED_PK_CANDIDATE_SHA256,
        )
        self.assertEqual(len(analysis["targets"]), 150)
        self.assertEqual(len(analysis["affected"]), 204)
        self.assertEqual(
            analysis["assembly_manifest_sha256"],
            B.EXPECTED_ASSEMBLY_HASH_MANIFEST_SHA256,
        )
        self.assertEqual(
            sum(
                summary["call_sites"] * 7
                for summary in analysis["selector_summary"].values()
            ),
            994,
        )

    def test_all_affected_verified_rows_are_renewed(self) -> None:
        analysis = self.bundle["analysis"]
        expected = set(
            B.member_coordinates(
                analysis["affected_verified_roots"],
                analysis["verified_by_root"],
            )
        )
        renewed = {
            str(row["coordinate"])
            for row in self.bundle["updated_rows"]
            if bool(
                row.get("runtime_vm_verification", {}).get(
                    "preexisting_verified_evidence_renewed"
                )
            )
        }
        self.assertEqual(len(expected), 120)
        self.assertEqual(renewed, expected)

    def test_promotion_is_exactly_41_and_pending_is_8600(self) -> None:
        promotion = self.bundle["promotion"]
        self.assertEqual(
            promotion["result"]["runtime_promotion_rows"],
            41,
        )
        self.assertEqual(
            promotion["result"]["runtime_promotion_roots"],
            23,
        )
        self.assertEqual(promotion["result"]["pending_rows_after"], 8600)
        self.assertEqual(
            self.bundle["analysis"]["machine_roots"]
            - self.bundle["analysis"]["eligible_roots"],
            {(6, 3941)},
        )

    def test_reports_are_source_free_and_outputs_match(self) -> None:
        B.assert_source_free_report(self.audit)
        B.assert_source_free_report(self.bundle["promotion"])
        self.assertFalse(
            any(B.contains_body_key(row) for row in self.bundle["evidence_rows"])
        )
        expected = {
            B.DEFAULT_AUDIT_OUTPUT: self.audit_content,
            B.DEFAULT_PROMOTION_OUTPUT: self.promotion_content,
            B.DEFAULT_DECISION_OUTPUT: self.decision_content,
            B.DEFAULT_EVIDENCE_OUTPUT: self.evidence_content,
        }
        for path, content in expected.items():
            self.assertTrue(path.is_file())
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_no_base_or_steam_write(self) -> None:
        self.assertTrue(
            all(
                row["resource"] == "pk_msggame"
                for row in self.bundle["updated_rows"]
            )
        )
        self.assertFalse(self.audit["steam_write_performed"])
        self.assertFalse(
            self.bundle["promotion"]["steam_write_performed"]
        )
        self.assertEqual(
            self.steam_before,
            {
                "base": B.HONORIFIC.live_hash(B.LIVE_STEAM_BASE),
                "pk": B.HONORIFIC.live_hash(B.LIVE_STEAM_PK),
            },
        )


if __name__ == "__main__":
    unittest.main()
