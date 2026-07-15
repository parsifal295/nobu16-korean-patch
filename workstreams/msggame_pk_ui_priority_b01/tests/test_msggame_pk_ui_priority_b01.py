from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msggame_pk_ui_priority_b01 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "9F64B7CBC810D6FDE6FC99D4C06032736EB4552C925E500042E778CAEBEE07D5",
    f"evidence/{batch.EVIDENCE_NAME}": "6B5527A881FD69380E942B93A4F1CED6F991B1829C92573EE58397CFCFAA770F",
    f"review/{batch.REVIEW_NAME}": "9959DF3DE6BF1701E976598914C2D3CD5EE74F8D6ADFB9A1C5D1A30A9F0DE382",
    batch.VALIDATION_NAME: "211CB15D69DE4575AD5EE2A9B5E5D07CC3F01A3FD82487E3472A3A2E3289F2CA",
}
EXPECTED_SELECTED_HASH = "CB5EFAF169E00B4EA19B125877E8F4DEC52917E4096CE0F5DE659E8BF9DC7017"
EXPECTED_TARGET_SHA256 = "6A04D6CCB2E51F2D9E96B729BD467C060637E1BA7182E611CC64A5BD514A8E28"
EXPECTED_CATEGORIES = {
    "battle_ui_and_system_help": 50,
    "management_tooltip_and_tutorial": 42,
    "menu_navigation_and_input": 7,
    "settings_unlock_and_configuration": 22,
    "ui_label_or_title": 29,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"JSON root is not an object: {path}")
    return value


def args(out_root: Path, progress: Path = batch.recovery.DEFAULT_PROGRESS) -> SimpleNamespace:
    return SimpleNamespace(
        pk_jp=batch.GAME_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        pk_sc=batch.recovery.DEFAULT_PK_SC,
        pk_en=batch.GAME_ROOT / "MSG_PK" / "EN" / "msggame.bin",
        progress=progress,
        target_catalog=batch.recovery.DEFAULT_TARGET_CATALOG,
        out_root=out_root,
    )


class MsggamePkUiPriorityB01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME)
        cls.evidence = load(WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME)
        cls.review = load(WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME)
        cls.validation = load(WORKSTREAM_ROOT / batch.VALIDATION_NAME)

    def test_ui_pool_is_exactly_pinned_and_categorized(self) -> None:
        selected = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.overlay["entries"]
        }
        categories = Counter(
            entry["category"] for entry in self.review["entries"] if entry["status"] == "translated"
        )
        self.assertEqual(150, len(selected))
        self.assertEqual(set(batch.TRANSLATIONS), selected)
        self.assertEqual(EXPECTED_SELECTED_HASH, self.validation["coordinate_sets"]["selected_sha256"])
        self.assertEqual(EXPECTED_CATEGORIES, dict(categories))
        self.assertEqual(EXPECTED_CATEGORIES, self.validation["category_counts"])

    def test_selected_scope_is_target_only_and_disjoint_from_predecessors(self) -> None:
        selected = set(batch.TRANSLATIONS)
        target = batch.recovery.load_target_catalog(batch.recovery.DEFAULT_TARGET_CATALOG)["coordinates"]
        existing = batch.collect_existing(batch.recovery.DEFAULT_PROGRESS)
        self.assertTrue(selected <= target)
        self.assertTrue(selected.isdisjoint(existing["all_coordinates"]))
        self.assertEqual(10_149, len(existing["predecessor_coordinates"]))
        self.assertEqual(10_299, self.validation["progress_effect"]["post_batch_translated_count"])
        self.assertEqual(6_183, self.validation["progress_effect"]["post_batch_remaining_count"])

    def test_every_replacement_is_a_complete_single_literal_record_and_preserves_contract(self) -> None:
        pk_sc = batch.recovery.prior.load_standard_source(batch.recovery.DEFAULT_PK_SC, "pk_sc")
        literals = batch.recovery.literal_map(pk_sc["archive"])
        record_counts = Counter(coordinate[:2] for coordinate in literals)
        for entry in self.overlay["entries"]:
            coordinate = (entry["block_id"], entry["record_id"], entry["literal_id"])
            source = literals[coordinate].text
            replacement = entry["ko"]
            self.assertEqual(1, record_counts[coordinate[:2]], coordinate)
            self.assertEqual(0, coordinate[2], coordinate)
            self.assertEqual([], batch.recovery.invariant_mismatches(source, replacement), coordinate)
            self.assertEqual(
                batch.recovery.msggame_translation.bracket_sequence(source),
                batch.recovery.msggame_translation.bracket_sequence(replacement),
                coordinate,
            )
            self.assertEqual(batch.recovery.delimiter_roles(source), batch.recovery.delimiter_roles(replacement))
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.recovery.script_counts(replacement))
            self.assertTrue(batch.recovery.prior.has_hangul_syllable(replacement))

    def test_return_coordinate_is_proved_dynamic_narrative_and_excluded(self) -> None:
        false_positive = self.evidence["false_positive_audit"]
        coordinate = (
            false_positive["block_id"],
            false_positive["record_id"],
            false_positive["literal_id"],
        )
        self.assertEqual(batch.FALSE_POSITIVE, coordinate)
        self.assertNotIn(coordinate, batch.TRANSLATIONS)
        self.assertFalse(false_positive["standalone_ui_button"])
        self.assertTrue(false_positive["dynamic_value_between_sc_literals"])
        self.assertEqual(2, false_positive["sc_literal_count"])
        self.assertEqual(1, false_positive["jp_literal_count"])
        self.assertEqual(2, false_positive["en_literal_count"])
        self.assertEqual(batch.FALSE_POSITIVE_SKELETON_PIN, false_positive["sc_record_skeleton_sha256"])
        self.assertEqual(
            false_positive["sc_record_skeleton_sha256"],
            false_positive["en_record_skeleton_sha256"],
        )
        excluded = [entry for entry in self.review["entries"] if entry["status"] == "excluded"]
        self.assertEqual(1, len(excluded))
        self.assertEqual("dynamic_narrative_false_positive_return_to_castle", excluded[0]["reason"])

    def test_artifacts_are_source_free_and_hash_pinned(self) -> None:
        for relative, expected in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            self.assertEqual(expected, digest(path), relative)
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                batch.recovery.script_counts(path.read_text(encoding="utf-8")),
                relative,
            )

    def test_isolated_builds_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            roots = [Path(temporary) / name for name in ("a", "b")]
            results = [batch.build(args(root)) for root in roots]
            self.assertEqual(150, results[0]["entry_count"])
            self.assertEqual(EXPECTED_TARGET_SHA256, results[0]["target_packed_sha256"])
            self.assertEqual(results[0]["target_packed_sha256"], results[1]["target_packed_sha256"])
            for relative in EXPECTED_HASHES:
                self.assertEqual((roots[0] / relative).read_bytes(), (roots[1] / relative).read_bytes())
                self.assertEqual((roots[0] / relative).read_bytes(), (WORKSTREAM_ROOT / relative).read_bytes())

    def test_self_and_successor_registration_do_not_feed_selection(self) -> None:
        progress = load(batch.recovery.DEFAULT_PROGRESS)
        resource = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
        original_globs = [item for item in resource["overlay_globs"] if item != batch.SELF_RELATIVE]
        with tempfile.TemporaryDirectory(dir=batch.REPO_ROOT / "tmp") as repository_temp, tempfile.TemporaryDirectory() as output_temp:
            repository_temp_path = Path(repository_temp)
            successor_path = repository_temp_path / "successor.json"
            successor = {
                "resource": batch.RESOURCE,
                "entries": [{"block_id": 0, "record_id": 0, "literal_id": 0, "ko": "검증"}],
            }
            successor_path.write_text(json.dumps(successor, ensure_ascii=False), encoding="utf-8")
            successor_relative = successor_path.relative_to(batch.REPO_ROOT).as_posix()
            output_root = Path(output_temp)
            outputs: list[Path] = []
            for name, extras in (
                ("absent", []),
                ("registered", [batch.SELF_RELATIVE]),
                ("successor", [successor_relative]),
            ):
                resource["overlay_globs"] = original_globs + extras
                progress_path = output_root / f"progress-{name}.json"
                progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                output = output_root / name
                result = batch.build(args(output, progress_path))
                self.assertEqual(int(name == "registered"), result["self_registration_count"])
                outputs.append(output)
            for relative in EXPECTED_HASHES:
                self.assertEqual((outputs[0] / relative).read_bytes(), (outputs[1] / relative).read_bytes())
                self.assertEqual((outputs[0] / relative).read_bytes(), (outputs[2] / relative).read_bytes())
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), (outputs[0] / relative).read_bytes())


if __name__ == "__main__":
    unittest.main()
