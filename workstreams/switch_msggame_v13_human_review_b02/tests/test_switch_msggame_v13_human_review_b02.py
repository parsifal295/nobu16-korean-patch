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

import build_switch_msggame_v13_human_review_b02 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "1656637F64B7EA30C284AA9DE229A636A93CD14E90EF92F25A1FB6F838F47359",
    f"evidence/{batch.EVIDENCE_NAME}": "427FF6899ED94E4B89E9AB844A00C654ED2DC4895EC592D5679BBB256F7D89A3",
    f"review/{batch.REVIEW_NAME}": "2C2F8FF899E685DCE64B72020ADAE0F1AB9A8CDE31C249D7F1A002A8BA9BE71D",
    batch.VALIDATION_NAME: "C2D35D9AA4E8BD2D7D5311696F660D67B56CA0F04A6ED4D5076A325E78DD5D8B",
}
EXPECTED_SELECTED_HASH = "13C30CC6D6118211BC318B3CFDAF2A268B26A97698921E369FE13C9D7CCC5A2D"
EXPECTED_EXCLUDED_HASH = "BD1860A0AD47449FF1F4F65FD0045F7DF8A2E3B44DC065CB0CEE0DE5C3BAE6E5"
EXPECTED_TARGET_SHA256 = "C1025343C05338B62F3C95F920FD15E17F1646C24547275E87FC113121231AE8"


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


class SwitchMsggameV13HumanReviewB02Tests(unittest.TestCase):
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
        self.assertEqual(68, len(translated))
        self.assertEqual(32, len(excluded))
        self.assertTrue(translated.isdisjoint(excluded))
        self.assertEqual(set(window), translated | excluded)
        self.assertEqual(EXPECTED_SELECTED_HASH, self.validation["coordinate_sets"]["selected_sha256"])
        self.assertEqual(EXPECTED_EXCLUDED_HASH, self.validation["coordinate_sets"]["excluded_sha256"])
        self.assertTrue(self.validation["proofs"]["later_overlays_source_free_target_only_and_disjoint"])

    def test_selected_scope_is_target_only_and_disjoint_from_all_prior_overlays(self) -> None:
        selected = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.overlay["entries"]
        }
        target = batch.recovery.load_target_catalog(batch.recovery.DEFAULT_TARGET_CATALOG)["coordinates"]
        existing = batch.collect_existing(batch.recovery.DEFAULT_PROGRESS)["coordinates"]
        b01 = load(batch.REPO_ROOT / batch.B01_RELATIVE)
        b01_coordinates = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in b01["entries"]
        }
        self.assertEqual(68, self.overlay["entry_count"])
        self.assertEqual(set(batch.TRANSLATIONS), selected)
        self.assertTrue(selected <= target)
        self.assertTrue(selected.isdisjoint(existing))
        self.assertTrue(selected.isdisjoint(b01_coordinates))

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
        self.assertEqual(32, sum(reasons.values()))
        self.assertGreaterEqual(len(reasons), 2)
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
            self.assertEqual(68, results[0]["entry_count"])
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
