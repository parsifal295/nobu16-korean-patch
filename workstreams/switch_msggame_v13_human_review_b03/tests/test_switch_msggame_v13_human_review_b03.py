from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_switch_msggame_v13_human_review_b03 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "6279D3C7D7139EED15670309F7DAD3E993359821985DA3194E392439B3C77302",
    f"evidence/{batch.EVIDENCE_NAME}": "F955B464F69D0949036E4BEC95D82742458EA22967032F448CBA8F6388935F7C",
    f"review/{batch.REVIEW_NAME}": "8128B5DBFB2E4E20365A9BA7A5AE12D2CAC99A17D693656020C334214664B917",
    batch.VALIDATION_NAME: "B8BCA4A3EC3D678E0177BF36900FC79044B510300FE089EB5505E453AACE0113",
}
EXPECTED_SELECTED_HASH = "8621BF3F6BCD119A51226C18CB10BAA10F69BFEADE204D44139BEFD2C2A34BCD"
EXPECTED_EXCLUDED_HASH = "92E61691EDE558A96854BBB85F638088BBDD4E5B4C12FB6C4ABD6851AC365C7A"
EXPECTED_TARGET_SHA256 = "2E8AE6D3265E6F5C0A47B32D362FA7BB82CA6CBD40FFEA0E4819AE550D75720B"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"JSON root is not an object: {path}")
    return value


def args(out_root: Path, progress: Path = batch.recovery.DEFAULT_PROGRESS) -> SimpleNamespace:
    return SimpleNamespace(
        switch_v13_zip=batch.recovery.DEFAULT_V13_ZIP,
        switch_v11_zip=batch.recovery.DEFAULT_V11_ZIP,
        base_jp=batch.GAME_ROOT / "MSG" / "JP" / "msggame.bin",
        pk_jp=batch.GAME_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        pk_sc=batch.recovery.DEFAULT_PK_SC,
        progress=progress,
        target_catalog=batch.recovery.DEFAULT_TARGET_CATALOG,
        out_root=out_root,
    )


class SwitchMsggameV13HumanReviewB03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME)
        cls.evidence = load(WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME)
        cls.review = load(WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME)
        cls.validation = load(WORKSTREAM_ROOT / batch.VALIDATION_NAME)

    def test_review_window_is_pinned_and_fully_partitioned(self) -> None:
        translated = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.review["entries"]
            if entry["status"] == "translated"
        }
        excluded = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.review["entries"]
            if entry["status"] == "excluded"
        }
        window, _items = batch.review_window()
        self.assertEqual(130, len(translated))
        self.assertEqual(20, len(excluded))
        self.assertTrue(translated.isdisjoint(excluded))
        self.assertEqual(set(window), translated | excluded)
        self.assertEqual(EXPECTED_SELECTED_HASH, self.validation["coordinate_sets"]["selected_sha256"])
        self.assertEqual(EXPECTED_EXCLUDED_HASH, self.validation["coordinate_sets"]["excluded_sha256"])
        self.assertTrue(self.validation["proofs"]["later_overlays_source_free_target_only_and_disjoint"])

    def test_selected_scope_is_target_only_and_disjoint_from_every_registered_overlay(self) -> None:
        selected = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.overlay["entries"]
        }
        target = batch.recovery.load_target_catalog(batch.recovery.DEFAULT_TARGET_CATALOG)["coordinates"]
        existing = batch.collect_existing(batch.recovery.DEFAULT_PROGRESS)
        self.assertEqual(130, self.overlay["entry_count"])
        self.assertEqual(set(batch.TRANSLATIONS), selected)
        self.assertTrue(selected <= target)
        self.assertTrue(selected.isdisjoint(existing["all_coordinates"]))
        self.assertEqual(10_019, len(existing["predecessor_coordinates"]))

    def test_every_replacement_preserves_the_exact_sc_contract(self) -> None:
        pk_sc = batch.recovery.prior.load_standard_source(batch.recovery.DEFAULT_PK_SC, "pk_sc")
        literals = batch.recovery.literal_map(pk_sc["archive"])
        for entry in self.overlay["entries"]:
            coordinate = (entry["block_id"], entry["record_id"], entry["literal_id"])
            source = literals[coordinate].text
            replacement = entry["ko"]
            self.assertEqual([], batch.recovery.invariant_mismatches(source, replacement), coordinate)
            self.assertEqual(
                batch.recovery.msggame_translation.bracket_sequence(source),
                batch.recovery.msggame_translation.bracket_sequence(replacement),
                coordinate,
            )
            self.assertEqual(batch.recovery.delimiter_roles(source), batch.recovery.delimiter_roles(replacement))
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.recovery.script_counts(replacement))
            self.assertTrue(batch.recovery.prior.has_hangul_syllable(replacement))

    def test_only_joint_boundary_cases_remain_excluded(self) -> None:
        reasons: dict[str, int] = {}
        for entry in self.review["entries"]:
            if entry["status"] == "excluded":
                reasons[entry["reason"]] = reasons.get(entry["reason"], 0) + 1
        self.assertEqual(20, sum(reasons.values()))
        self.assertEqual(
            {
                "cross_literal_korean_word_order_not_safe_in_isolation": 5,
                "sc_dynamic_value_order_requires_joint_sibling_rewrite": 15,
            },
            reasons,
        )

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
            self.assertEqual(130, results[0]["entry_count"])
            self.assertEqual(EXPECTED_TARGET_SHA256, results[0]["target_packed_sha256"])
            self.assertEqual(results[0]["target_packed_sha256"], results[1]["target_packed_sha256"])
            for relative in EXPECTED_HASHES:
                self.assertEqual((roots[0] / relative).read_bytes(), (roots[1] / relative).read_bytes())
                self.assertEqual((roots[0] / relative).read_bytes(), (WORKSTREAM_ROOT / relative).read_bytes())

    def test_self_and_later_registration_do_not_feed_selection(self) -> None:
        progress = load(batch.recovery.DEFAULT_PROGRESS)
        resource = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
        original_globs = list(resource["overlay_globs"])
        with tempfile.TemporaryDirectory(dir=batch.REPO_ROOT / "tmp") as repository_temp, tempfile.TemporaryDirectory() as output_temp:
            repository_temp_path = Path(repository_temp)
            successor_path = repository_temp_path / "successor.json"
            successor = {
                "schema": batch.recovery.OVERLAY_SCHEMA,
                "overlay_id": "test_source_free_disjoint_successor",
                "resource": batch.RESOURCE,
                "entry_count": 1,
                "distribution_policy": {
                    "contains_commercial_source_text": False,
                    "contains_complete_game_resource": False,
                },
                "entries": [{"block_id": 0, "record_id": 1290, "literal_id": 0, "ko": "후속 검증"}],
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
                resource["overlay_globs"] = [item for item in original_globs if item != batch.SELF_RELATIVE] + extras
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

    def test_bad_successors_are_rejected_without_feeding_selection(self) -> None:
        cases = {
            "source_text": {"block_id": 0, "record_id": 1352, "literal_id": 0, "ko": "返回"},
            "outside_target": {"block_id": 0, "record_id": 0, "literal_id": 0, "ko": "후속"},
            "self_overlap": {"block_id": 6, "record_id": 4482, "literal_id": 2, "ko": "후속"},
        }
        original = load(batch.recovery.DEFAULT_PROGRESS)
        original_resource = next(item for item in original["resources"] if item["path"] == batch.RESOURCE)
        original_globs = list(original_resource["overlay_globs"])
        with tempfile.TemporaryDirectory(dir=batch.REPO_ROOT / "tmp") as repository_temp:
            repository_temp_path = Path(repository_temp)
            for name, entry in cases.items():
                with self.subTest(name=name):
                    successor_path = repository_temp_path / f"{name}.json"
                    successor = {
                        "schema": batch.recovery.OVERLAY_SCHEMA,
                        "overlay_id": f"test_invalid_{name}",
                        "resource": batch.RESOURCE,
                        "entry_count": 1,
                        "distribution_policy": {
                            "contains_commercial_source_text": False,
                            "contains_complete_game_resource": False,
                        },
                        "entries": [entry],
                    }
                    successor_path.write_text(
                        json.dumps(successor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                    )
                    progress = json.loads(json.dumps(original))
                    resource = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
                    resource["overlay_globs"] = original_globs + [
                        successor_path.relative_to(batch.REPO_ROOT).as_posix()
                    ]
                    progress_path = repository_temp_path / f"progress-{name}.json"
                    progress_path.write_text(
                        json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                    )
                    with self.assertRaises(batch.recovery.RecoveryError):
                        batch.collect_existing(progress_path)


if __name__ == "__main__":
    unittest.main()
