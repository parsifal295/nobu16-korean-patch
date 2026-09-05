"""Source-free regression checks for the approved v0.95 public records."""

from __future__ import annotations

import collections
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "workstreams/v095_image_completion_v1"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class V095PublicCompletionTests(unittest.TestCase):
    def test_all_46_approved_titles_have_only_public_metadata(self) -> None:
        payload = read_json(COMPLETION / "tactic_titles.v1.json")
        rows = payload["entries"]
        self.assertEqual(payload["count"], 46)
        self.assertEqual(len(rows), 46)
        self.assertEqual(collections.Counter(row["family"] for row in rows), {"base": 35, "pk": 11})
        self.assertEqual(len({row["id"] for row in rows}), 46)
        self.assertEqual(len({row["approved_base_sha256"] for row in rows}), 46)
        for family, count in (("base", 35), ("pk", 11)):
            self.assertEqual(
                sorted(row["group_index"] for row in rows if row["family"] == family),
                list(range(count)),
            )
        for row in rows:
            self.assertEqual(set(row), {
                "id", "family", "group_index", "canonical_message_id",
                "runtime_text", "image_text", "approved_base_sha256",
            })
            self.assertRegex(row["approved_base_sha256"], r"^[0-9A-F]{64}$")

    def test_only_approved_don_ton_exception_differs(self) -> None:
        rows = read_json(COMPLETION / "tactic_titles.v1.json")["entries"]
        differences = [row for row in rows if row["runtime_text"] != row["image_text"]]
        exceptions = read_json(COMPLETION / "title_text_image_exceptions.v3.json")["exceptions"]
        self.assertEqual([row["id"] for row in differences], ["base_030"])
        self.assertEqual(set(exceptions), {"base_030"})
        row, contract = differences[0], exceptions["base_030"]
        for key in ("runtime_text", "image_text", "canonical_message_id"):
            self.assertEqual(row[key], contract[key])
        self.assertEqual(row["runtime_text"], "돈보키리")
        self.assertEqual(row["image_text"], "톤보키리")
        self.assertEqual(contract["preserved_message_coordinates"], [14164, 15274])

    def test_image_counts_and_permanent_exclusions_agree(self) -> None:
        receipt = read_json(COMPLETION / "validation.v1.json")
        audit = receipt["initial_image_audit"]
        progress = read_json(ROOT / "workstreams/jp_atlas_residual_audit_v1/progress.v1.json")
        self.assertEqual(receipt["tactic_images"]["state_placements"], 46 * 2 * 3)
        self.assertEqual(receipt["title_binary"]["state_slots"], 276)
        for suffix, total, complete, remaining in (
            ("families", 9, 8, 1), ("text_texture_placements", 304, 300, 4),
        ):
            self.assertEqual(audit["actionable_" + suffix], total)
            self.assertEqual(audit["completed_" + suffix], complete)
            self.assertEqual(audit["remaining_" + suffix], remaining)
            self.assertEqual(progress["completion"]["completed_" + suffix], complete)
            self.assertEqual(progress["completion"]["remaining_" + suffix], remaining)
            self.assertEqual(complete + remaining, total)
        self.assertEqual(audit["help_gameplay_capture_bundles"], "permanently_excluded")

    def test_receipt_distinguishes_file_checks_from_runtime_qa(self) -> None:
        receipt = read_json(COMPLETION / "validation.v1.json")
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(set(receipt["issues"]), {"122", "123", "124", "125"})
        self.assertTrue(all(value is False for value in receipt["source_policy"].values()))
        steam = receipt["steam"]
        self.assertEqual(steam["verified_resource_files"], 147)
        self.assertEqual(steam["verified_install_state_files"], 151)
        self.assertEqual(steam["runtime_image_qa_status"], "NOT_PERFORMED")
        self.assertIsNone(steam["selected_resolution"])
        self.assertFalse(steam["full_process_restart_completed_after_apply"])
        for bundle in receipt["bundles"].values():
            self.assertEqual(bundle["apply_verify_restore"], "PASS")
            self.assertRegex(bundle["sha256"], r"^[0-9A-F]{64}$")
        self.assertEqual(receipt["package"]["entry_count"], 13)
        self.assertEqual(receipt["package"]["fresh_extract_checksums_passed"], 12)

    def test_full_region_audit_has_no_gaps_and_preserves_shared_strdata(self) -> None:
        workstream = ROOT / "workstreams/issue_124_region_names_v1"
        audit_path = workstream / "audit.issue124_region_names.v2.json"
        audit = read_json(audit_path)
        validation = read_json(workstream / "validation.issue124_region_names.v2.json")
        self.assertEqual(hashlib.sha256(audit_path.read_bytes()).hexdigest().upper(), validation["audit_sha256"])
        rows = audit["rows"]
        self.assertEqual(audit["row_count"], 2014)
        self.assertEqual([row["id"] for row in rows], list(range(9947, 11961)))
        self.assertEqual(collections.Counter(row["classification"] for row in rows), {
            "special_shared_label": 720, "full_place_transcription": 1294,
        })
        self.assertEqual(sum(row["msgdata_changed"] for row in rows), 306)
        self.assertEqual(sum(row["display_changed"] for row in rows), 240)
        self.assertEqual(sum(row["reading_changed"] for row in rows), 108)
        self.assertTrue(all(value is False for value in audit["distribution_policy"].values()))
        for row in rows:
            self.assertEqual(row["reading_id"], row["id"] + 2014)
            self.assertEqual(row["strdata_action"], "preserve_read_only")
            for key in ("strdata_display", "strdata_reading"):
                self.assertEqual(row["before_ko"][key], row["after_ko"][key])
            for source_hash in row["source_evidence_utf16le_sha256"].values():
                self.assertRegex(source_hash, r"^[0-9A-F]{64}$")
            if row["classification"] == "special_shared_label":
                self.assertFalse(row["msgdata_changed"])
                self.assertEqual(row["before_ko"], row["after_ko"])
            else:
                # The approved builder preserves each slot's original edge spacing.
                self.assertEqual(row["after_ko"]["display"].strip(), row["after_ko"]["reading"].strip())
                for key in ("display", "reading"):
                    before, after = row["before_ko"][key], row["after_ko"][key]
                    self.assertEqual(len(before) - len(before.lstrip()), len(after) - len(after.lstrip()))
                    self.assertEqual(len(before) - len(before.rstrip()), len(after) - len(after.rstrip()))


if __name__ == "__main__":
    unittest.main()
