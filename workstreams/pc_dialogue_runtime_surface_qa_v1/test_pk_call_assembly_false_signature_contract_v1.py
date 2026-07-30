#!/usr/bin/env python3
"""Regressions for the exact PK call-assembly false-signature contract."""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


BUILD = load_module(
    "pk_call_assembly_false_signature_contract_builder_test_subject",
    HERE / "build_pk_call_assembly_false_signature_contract_v1.py",
)
AUDIT = load_module(
    "pk_call_assembly_false_signature_contract_audit_test_subject",
    HERE / "audit_call_assembly_boundaries_v1.py",
)
CONTRACT_PATH = (
    HERE
    / "pk_call_assembly_false_signature_contract.source_free.v1.json"
)


class PkCallAssemblyFalseSignatureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            CONTRACT_PATH.read_text(encoding="utf-8")
        )

    def test_contract_is_source_free_and_digest_pinned(self) -> None:
        self.assertEqual(self.contract["schema"], BUILD.SCHEMA)
        self.assertTrue(self.contract["source_free"])
        self.assertFalse(self.contract["private_text_included"])
        self.assertEqual(self.contract["entry_count"], 131)
        self.assertEqual(
            self.contract["entry_sha256"],
            "A27F4EA328B26802186C1760C1BCC8DAF67862889C5083629B358919FC9F5C40",
        )
        self.assertEqual(
            self.contract["coordinate_rule_sha256"],
            "5E625BD912C88AE412104638029B527C692BCE66E598CEB0697E8B3DF6125B4E",
        )
        self.assertEqual(
            self.contract["review_class_counts"],
            {
                "non_side_false_positive": 33,
                "selector_side_legitimate": 98,
            },
        )
        self.assertEqual(
            self.contract["rule_counts"],
            {
                "deut_bare_copula": 15,
                "finite_suffix_before_same_sentence_hangul": 17,
                "rendered_missing_exist_stem_before_bare_formal": 1,
                "rendered_selector_side_role_smell": 98,
            },
        )
        serialized = CONTRACT_PATH.read_text(encoding="utf-8")
        self.assertFalse(any(ord(character) > 127 for character in serialized))
        for entry in self.contract["entries"]:
            self.assertNotIn("assembled", entry)
            self.assertNotIn("previous_literal", entry)
            self.assertNotIn("call_variant", entry)
            self.assertNotIn("next_literal", entry)

    def test_loader_accepts_every_reviewed_exact_signature(self) -> None:
        expected = {
            row["finding_signature_sha256"]
            for row in self.contract["entries"]
        }
        self.assertEqual(AUDIT.PK_REVIEWED_FALSE_SIGNATURES, expected)
        for row in self.contract["entries"]:
            self.assertEqual(
                AUDIT.finding_signature_sha256(row),
                row["finding_signature_sha256"],
            )
            finding = AUDIT.CallAssemblyIssue(
                **{
                    field: row[field]
                    for field in AUDIT.SOURCE_FREE_FINDING_FIELDS
                }
            )
            self.assertTrue(AUDIT.is_reviewed_false_signature(finding))

    def test_rule_or_content_or_coordinate_change_is_not_suppressed(
        self,
    ) -> None:
        row = self.contract["entries"][0]
        finding = AUDIT.CallAssemblyIssue(
            **{
                field: row[field]
                for field in AUDIT.SOURCE_FREE_FINDING_FIELDS
            }
        )
        mutations = (
            dataclasses.replace(
                finding,
                rule=f"{finding.rule}_different",
            ),
            dataclasses.replace(
                finding,
                assembled_sha256="0" * 64,
            ),
            dataclasses.replace(
                finding,
                block_id=finding.block_id + 1000,
            ),
            dataclasses.replace(
                finding,
                component_index=finding.component_index + 1,
            ),
        )
        self.assertTrue(AUDIT.is_reviewed_false_signature(finding))
        for mutation in mutations:
            self.assertFalse(
                AUDIT.is_reviewed_false_signature(mutation),
                mutation,
            )

    def test_contract_application_is_candidate_hash_independent(self) -> None:
        application = self.contract["application_contract"]
        self.assertFalse(application["candidate_file_hash_required"])
        self.assertTrue(application["exact_finding_signature_required"])
        self.assertTrue(application["rule_only_suppression_forbidden"])
        self.assertTrue(
            application["coordinate_rule_only_suppression_forbidden"]
        )
        # Candidate SHA is deliberately absent from both the signature fields
        # and the suppression predicate.  A rebuild may change elsewhere while
        # an unchanged reviewed finding remains exactly recognized.
        self.assertNotIn(
            "candidate_sha256",
            AUDIT.SOURCE_FREE_FINDING_FIELDS,
        )

    def test_contract_digest_detects_tampering(self) -> None:
        entries = [dict(row) for row in self.contract["entries"]]
        entries[0]["assembled_sha256"] = "0" * 64
        self.assertNotEqual(
            AUDIT.false_signature_contract_entry_digest(entries),
            AUDIT.PK_FALSE_SIGNATURE_ENTRY_SHA256,
        )
        self.assertNotEqual(
            AUDIT.finding_signature_sha256(entries[0]),
            entries[0]["finding_signature_sha256"],
        )

    @unittest.skipUnless(
        BUILD.DEFAULT_INPUT.exists(),
        "private reviewed report is intentionally not tracked",
    )
    def test_private_review_rebuilds_exact_contract(self) -> None:
        rebuilt = BUILD.build(BUILD.DEFAULT_INPUT)
        self.assertEqual(
            BUILD.canonical_json(rebuilt),
            CONTRACT_PATH.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
