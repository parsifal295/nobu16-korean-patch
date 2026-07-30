#!/usr/bin/env python3
"""Regression tests for the source-free Base morph-pair contract."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "call_assembly_morph_contract_test_subject",
    HERE / "audit_call_assembly_boundaries_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class CallAssemblyMorphContractTests(unittest.TestCase):
    def test_known_base_collision_is_detected_without_kiwi(self) -> None:
        self.assertEqual(
            AUDIT.reviewed_morph_pair_collisions(
                "base_msggame",
                (1, 17),
                "어머, 벌써 벚꽃의 계절네",
            ),
            (
                (
                    "coda_noun_followed_by_bare_final_ending",
                    "어머, 벌써 벚꽃의 계절네",
                ),
            ),
        )
        self.assertEqual(
            AUDIT.reviewed_morph_pair_collisions(
                "pk_msggame",
                (1, 17),
                "어머, 벌써 벚꽃의 계절네",
            ),
            (),
        )

    def test_exact_archaic_allowlist_contains_only_reviewed_two(self) -> None:
        reviewed = {
            (
                (6, 3432),
                "올해도 쉬지 않고 정진하겠사와요",
            ),
            (
                (7, 1096),
                "여기서는 원군을 청하옵시다",
            ),
        }
        self.assertEqual(
            {
                (coordinate, text)
                for coordinate, text in reviewed
                if not AUDIT.reviewed_morph_pair_collisions(
                    "base_msggame",
                    coordinate,
                    text,
                )
            },
            reviewed,
        )
        self.assertEqual(len(AUDIT.BASE_MORPH_PAIR_EXACT_ALLOWLIST), 2)

    def test_contract_digest_and_tamper_detection_are_pinned(self) -> None:
        payload = json.loads(
            AUDIT.BASE_MORPH_PAIR_CONTRACT_PATH.read_text(encoding="utf-8")
        )
        entries = sorted(
            payload["entries"],
            key=lambda row: (
                int(row["block_id"]),
                int(row["record_id"]),
                str(row["class"]),
                str(row["signature_sha256"]),
                str(row["segment_sha256"]),
            ),
        )
        body = "\n".join(
            (
                f"{int(row['block_id'])}:{int(row['record_id'])}:"
                f"{row['class']}:{row['signature_sha256']}:"
                f"{row['segment_sha256']}"
            )
            for row in entries
        )
        self.assertEqual(
            AUDIT.sha256_bytes(body.encode("utf-8")),
            AUDIT.BASE_MORPH_PAIR_ENTRY_SHA256,
        )

        tampered = [dict(row) for row in entries]
        tampered[0]["segment_sha256"] = "0" * 64
        tampered_body = "\n".join(
            (
                f"{int(row['block_id'])}:{int(row['record_id'])}:"
                f"{row['class']}:{row['signature_sha256']}:"
                f"{row['segment_sha256']}"
            )
            for row in tampered
        )
        self.assertNotEqual(
            AUDIT.sha256_bytes(tampered_body.encode("utf-8")),
            AUDIT.BASE_MORPH_PAIR_ENTRY_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
