#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(REPO_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_common_message_overlay as common  # noqa: E402
import build_wave07_j04 as build  # noqa: E402
from translations import TRANSLATIONS  # noqa: E402


SOURCE_SCRIPT = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
ENTRY_FIELDS = {
    "block_id",
    "record_id",
    "literal_id",
    "source_jp_utf16le_sha256",
    "ko",
}


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def forbidden_sc_keys(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            folded = key.lower()
            if (
                folded == "source_sc"
                or folded.startswith("source_sc_")
                or folded == "stock_sc"
                or folded.startswith("stock_sc_")
            ):
                found.append(key)
            found.extend(forbidden_sc_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(forbidden_sc_keys(child))
    return found


class Wave07J04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _, cls.private_entries = build.load_private(build.DEFAULT_PRIVATE)
        cls.overlay = read_json(build.OVERLAY_PATH)
        cls.validation = read_json(build.VALIDATION_PATH)
        cls.review = read_json(build.REVIEW_PATH)

    def test_partition_is_exact_and_disjoint(self) -> None:
        selected, others = build.load_partition()
        private = {build.coordinate(entry) for entry in self.private_entries}
        overlay = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.overlay["entries"]
        }
        self.assertEqual(build.COORDINATE_COUNT, len(selected))
        self.assertEqual(selected, private)
        self.assertEqual(selected, overlay)
        self.assertTrue(selected.isdisjoint(others))
        self.assertEqual(
            build.COORDINATES_SHA256,
            build.canonical_hash([list(item) for item in sorted(selected)]),
        )

    def test_representatives_cover_every_unique_source_hash(self) -> None:
        first_by_hash: dict[str, tuple[int, int, int]] = {}
        for entry in self.private_entries:
            digest = build.text_hash(entry["jp"])
            first_by_hash.setdefault(digest, build.coordinate(entry))
        self.assertEqual(build.UNIQUE_SOURCE_HASH_COUNT, len(first_by_hash))
        self.assertEqual(set(first_by_hash.values()), set(TRANSLATIONS))
        self.assertEqual(build.UNIQUE_SOURCE_HASH_COUNT, len(TRANSLATIONS))

    def test_overlay_schema_hashes_invariants_and_repeat_consistency(self) -> None:
        self.assertEqual(build.OVERLAY_SCHEMA, self.overlay["schema"])
        self.assertEqual(build.RESOURCE, self.overlay["resource"])
        self.assertEqual("JP", self.overlay["base_language"])
        self.assertEqual(build.STOCK_JP, self.overlay["stock_jp"])
        self.assertEqual(build.COORDINATE_COUNT, self.overlay["entry_count"])
        private = {
            build.coordinate(entry): entry for entry in self.private_entries
        }
        korean_by_hash: dict[str, str] = {}
        for entry in self.overlay["entries"]:
            self.assertEqual(ENTRY_FIELDS, set(entry))
            current = (entry["block_id"], entry["record_id"], entry["literal_id"])
            source = private[current]["jp"]
            self.assertEqual(build.text_hash(source), entry["source_jp_utf16le_sha256"])
            self.assertFalse(common.invariant_mismatches(source, entry["ko"]))
            prior = korean_by_hash.setdefault(entry["source_jp_utf16le_sha256"], entry["ko"])
            self.assertEqual(prior, entry["ko"])
        self.assertEqual(build.UNIQUE_SOURCE_HASH_COUNT, len(korean_by_hash))

    def test_public_artifacts_are_source_free(self) -> None:
        paths = [
            ROOT / "translations.py",
            build.OVERLAY_PATH,
            build.VALIDATION_PATH,
            build.REVIEW_PATH,
            ROOT / "README_KO.md",
        ]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(SOURCE_SCRIPT.search(text), path)
            if path.suffix == ".json":
                self.assertEqual([], forbidden_sc_keys(json.loads(text)), path)
        policy = self.overlay["distribution_policy"]
        self.assertFalse(policy["contains_commercial_source_text"])
        self.assertFalse(policy["contains_complete_game_resource"])

    def test_validation_and_review_evidence_are_complete(self) -> None:
        self.assertEqual("pass", self.validation["status"])
        self.assertEqual(0, self.validation["translation_contract"]["untranslated_count"])
        self.assertEqual(0, self.validation["invariant_contract"]["mismatch_count"])
        self.assertTrue(self.validation["coordinate_contract"]["partition_exact_match"])
        self.assertTrue(self.validation["coordinate_contract"]["other_batches_disjoint"])
        integration = self.validation["steam_1_1_7_integration"]
        self.assertEqual(build.INTEGRATED_ENTRY_COUNT, integration["combined_entry_count"])
        self.assertEqual(
            build.INTEGRATED_REMAINING_COUNT,
            integration["remaining_jp_semantic_count"],
        )
        self.assertEqual(
            build.INTEGRATED_CANDIDATE_SHA256,
            integration["candidate_sha256"],
        )
        self.assertTrue(integration["non_literal_structure_preserved"])
        self.assertTrue(integration["deterministic_rebuild"])
        self.assertFalse(integration["installed_game_file_written"])
        self.assertEqual("complete", self.review["status"])
        self.assertEqual(
            build.COORDINATE_COUNT,
            self.review["manual_context_review"]["reviewed_coordinate_count"],
        )
        gates = self.review["quality_gates"]
        self.assertEqual(0, gates["source_script_leak_count"])
        self.assertTrue(
            all(value for key, value in gates.items() if key != "source_script_leak_count")
        )

    def test_builder_outputs_are_deterministic_and_current(self) -> None:
        first = build.build_artifacts(build.DEFAULT_PRIVATE)
        second = build.build_artifacts(build.DEFAULT_PRIVATE)
        self.assertEqual(
            {path: build.json_bytes(value) for path, value in first.items()},
            {path: build.json_bytes(value) for path, value in second.items()},
        )
        build.verify_artifacts(first)
        overlay_blob = build.OVERLAY_PATH.read_bytes()
        self.assertEqual(
            hashlib.sha256(overlay_blob).hexdigest().upper(),
            self.validation["overlay"]["sha256"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
