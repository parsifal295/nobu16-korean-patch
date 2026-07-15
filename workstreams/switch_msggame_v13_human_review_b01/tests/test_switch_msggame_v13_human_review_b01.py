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

import build_switch_msggame_v13_human_review_b01 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "8F1450EE1E06F26E8A2AC004E1562241F2150CF3FEF0EA10BD8B5786DDA05A3B",
    f"evidence/{batch.EVIDENCE_NAME}": "32310644D9A00D5CC02DA6C846A98A2C466A5527455A47CCA483425CF1E53803",
    f"review/{batch.REVIEW_NAME}": "C5F0456FF1BD563722713DD2E28CEFF6E9907323A653684EAA248BEFD4A1CBA8",
    batch.VALIDATION_NAME: "A9F125404FB2DA4250EE055D6D9E9FC984B7F7EF18A668D4630129AC28D28F1C",
}
EXPECTED_SELECTED_HASH = "D734E31CF4348AEB4095E70F33CDF71E75A66F356A1176A205714A1775098FA6"
EXPECTED_EXCLUDED_HASH = "9DE3C10F9A1230B8918B30DC27194555A92DA716DA2D77DDAD7B7CA651DCE7BF"
EXPECTED_TARGET_SHA256 = "23465C6487F67E4A165EF3C89D2298096822F508C3EB0AAD7977D103FE5D1E8D"


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


class SwitchMsggameV13HumanReviewB01Tests(unittest.TestCase):
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
        self.assertEqual(53, len(translated))
        self.assertEqual(47, len(excluded))
        self.assertTrue(translated.isdisjoint(excluded))
        self.assertEqual(set(window), translated | excluded)
        self.assertEqual(EXPECTED_SELECTED_HASH, self.validation["coordinate_sets"]["selected_sha256"])
        self.assertEqual(EXPECTED_EXCLUDED_HASH, self.validation["coordinate_sets"]["excluded_sha256"])
        self.assertTrue(self.validation["proofs"]["later_overlays_source_free_target_only_and_disjoint"])

    def test_selected_scope_is_exact_target_and_disjoint_from_existing(self) -> None:
        selected = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.overlay["entries"]
        }
        target = batch.recovery.load_target_catalog(batch.recovery.DEFAULT_TARGET_CATALOG)["coordinates"]
        existing = batch.collect_existing(batch.recovery.DEFAULT_PROGRESS)["coordinates"]
        self.assertEqual(53, self.overlay["entry_count"])
        self.assertEqual(set(batch.TRANSLATIONS), selected)
        self.assertTrue(selected <= target)
        self.assertTrue(selected.isdisjoint(existing))

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

    def test_ambiguous_fragments_remain_excluded(self) -> None:
        reasons: dict[str, int] = {}
        for entry in self.review["entries"]:
            if entry["status"] == "excluded":
                reasons[entry["reason"]] = reasons.get(entry["reason"], 0) + 1
        self.assertEqual(47, sum(reasons.values()))
        self.assertIn("non_language_format_fragment", reasons)
        self.assertIn("dynamic_target_order_ambiguous", reasons)
        self.assertIn("switch_record_alignment_absent_and_word_order_crosses_dynamic_boundary", reasons)
        self.assertTrue(self.validation["proofs"]["ambiguous_coordinates_excluded"])

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
            self.assertEqual(53, results[0]["entry_count"])
            self.assertEqual(EXPECTED_TARGET_SHA256, results[0]["target_packed_sha256"])
            self.assertEqual(results[0]["target_packed_sha256"], results[1]["target_packed_sha256"])
            for relative in EXPECTED_HASHES:
                self.assertEqual((roots[0] / relative).read_bytes(), (roots[1] / relative).read_bytes())
                self.assertEqual((roots[0] / relative).read_bytes(), (WORKSTREAM_ROOT / relative).read_bytes())

    def test_self_registration_before_and_after_is_output_stable(self) -> None:
        progress = load(batch.recovery.DEFAULT_PROGRESS)
        resource = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
        original_globs = list(resource["overlay_globs"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs: list[Path] = []
            for name, registered in (("absent", False), ("registered", True)):
                globs = [item for item in original_globs if item != batch.SELF_RELATIVE]
                if registered:
                    globs.append(batch.SELF_RELATIVE)
                resource["overlay_globs"] = globs
                progress_path = root / f"progress-{name}.json"
                progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                output = root / name
                result = batch.build(args(output, progress_path))
                self.assertEqual(int(registered), result["self_registration_count"])
                outputs.append(output)
            for relative in EXPECTED_HASHES:
                self.assertEqual((outputs[0] / relative).read_bytes(), (outputs[1] / relative).read_bytes())
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), (outputs[0] / relative).read_bytes())


if __name__ == "__main__":
    unittest.main()
