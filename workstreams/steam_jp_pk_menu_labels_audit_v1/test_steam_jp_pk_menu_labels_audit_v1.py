from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_pk_menu_labels_audit_v1",
    WORKSTREAM / "build_steam_jp_pk_menu_labels_audit_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def walk(value: object):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key, nested
            yield from walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk(nested)


class SteamJpPkMenuLabelsAuditTests(unittest.TestCase):
    def test_manifest_is_source_free_and_excludes_logo_title_entries(self) -> None:
        manifest = AUDIT.load_manifest()
        self.assertEqual(manifest["schema"], AUDIT.SCHEMA)
        self.assertEqual(manifest["scope"]["target_outer_entry"], 18)
        self.assertTrue({3, 24}.issubset(set(manifest["scope"]["excluded_outer_entries"])))
        self.assertFalse(manifest["scope"]["game_install_write_allowed"])
        self.assertFalse(manifest["scope"]["git_or_release_write_allowed"])
        self.assertFalse(manifest["scope"]["candidate_generation_enabled"])
        for key, value in walk(manifest):
            self.assertNotEqual(key, "payload")
            self.assertFalse(isinstance(value, (bytes, bytearray, memoryview)))

    def test_difference_metrics_detects_exact_bbox(self) -> None:
        left = bytes(512 * 128 * 4)
        right = bytearray(left)
        for x, y in ((3, 5), (9, 5), (9, 11)):
            offset = (y * 512 + x) * 4
            right[offset : offset + 4] = b"\x01\x02\x03\xFF"
        metrics = AUDIT.difference_metrics(left, bytes(right))
        self.assertEqual(metrics["changed_pixel_count"], 3)
        self.assertEqual(metrics["difference_bbox_inclusive"], [3, 5, 9, 11])

    def test_candidate_gate_is_hard_disabled(self) -> None:
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.build_command(object())

    def test_catalog_is_exactly_43_source_free_hash_rows(self) -> None:
        manifest = AUDIT.load_manifest()
        catalog = AUDIT.load_catalog()
        AUDIT.validate_catalog(catalog, manifest)
        self.assertEqual(catalog["target_resource"], "RES_JP_PK/res_lang_pk.bin")
        self.assertEqual(catalog["target_outer_entry"], 18)
        self.assertEqual(catalog["review_required_slots"], [1, 2, 19])
        self.assertFalse(catalog["candidate_eligible_now"])
        rows = catalog["slots"]
        self.assertEqual([row["slot"] for row in rows], list(range(43)))
        self.assertTrue((WORKSTREAM / "catalog.v1.json").read_bytes().isascii())
        for row in rows:
            self.assertEqual(set(row), {"slot", "input_payload_sha256", "dimensions", "ko_output_utf16le_sha256"})
            self.assertEqual(row["dimensions"], [512, 128])
            self.assertTrue(AUDIT.valid_sha256(row["input_payload_sha256"]))
            self.assertTrue(AUDIT.valid_sha256(row["ko_output_utf16le_sha256"]))

    def test_report_validation_rejects_candidate_or_logo_scope(self) -> None:
        manifest = AUDIT.load_manifest()
        report = {
            "schema": AUDIT.SCHEMA,
            "file_only": True,
            "game_install_modified": False,
            "git_or_release_modified": False,
            "target": {
                "resource": "RES_JP_PK/res_lang_pk.bin",
                "outer_entry": 18,
                "logo_or_title_art_touched": False,
                "excluded_outer_entries": [3, 24],
            },
            "candidate_generation": {"enabled": False, "candidate_created": False},
            "inputs": {
                language: {
                    "before": {"size": value["size"], "sha256": value["sha256"]},
                    "after": {"size": value["size"], "sha256": value["sha256"]},
                    "unchanged_during_read": True,
                    "outer_18_sha256": "0" * 64,
                }
                for language, value in manifest["inputs"].items()
            },
            "structure": manifest["structure_contract"],
            "slots": [
                {
                    "slot": slot,
                    "candidate_eligible": False,
                    "language_payloads": {
                        language: {"wrapper_sha256": "0" * 64, "raw_sha256": "0" * 64, "payload_sha256": "0" * 64}
                        for language in AUDIT.LANGUAGE_ORDER
                    },
                }
                for slot in range(43)
            ],
            "source_free_guarantees": manifest["source_free_guarantees"],
        }
        report["report_sha256"] = AUDIT.stable_hash(report)
        AUDIT.validate_report(report, manifest)
        report["candidate_generation"] = {"enabled": True, "candidate_created": False}
        report["report_sha256"] = AUDIT.stable_hash({key: value for key, value in report.items() if key != "report_sha256"})
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.validate_report(report, manifest)

    def test_workstream_has_only_metadata_and_code(self) -> None:
        allowed = {".json", ".md", ".py"}
        self.assertEqual({path.suffix for path in WORKSTREAM.iterdir() if path.is_file()}, allowed)
        manifest = json.loads((WORKSTREAM / "manifest.v1.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["source_free_guarantees"]["metadata_only"])


if __name__ == "__main__":
    unittest.main()
