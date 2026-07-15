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
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_switch_msggame_v13_invariant_recovery as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "9EF7210B5AA5F6842494EA75D79874AC009A9452855E4EC0FE79744284C6E61C",
    f"evidence/{batch.EVIDENCE_NAME}": "43DBA66E21368E6BBD564921E8C46A782C511E1C947F12BE039BBC95174DB550",
    f"review/{batch.REVIEW_NAME}": "2C2F2603B01C14E5A706B35190ED5A76CFB1E1CF4E2D0BF9DB2ACDA7F81095D4",
    batch.VALIDATION_NAME: "1064934E869B1BDD5ADC1EE4963D705DDD99B9B6CBA8D4F097980A2195009623",
}
EXPECTED_TARGET_SHA256 = "1D1734FCF60222752E7D8A5CA1C4CC572765EBE3F0D6C118276EEB1F6B28DE96"
EXPECTED_CLASS_HASHES = {
    "edge_template": "6F425F691CC81A634D8E6A654BBF1707FF035DD4D5D2BD11D995B7F50799627B",
    "pc_pua_map": "D12478CAB9574E0DD96290C60F1872D5F3FC7757926B939877243667E46AEEE2",
    "public_whitespace_variant": "EE738F3423B1C397ADD6CA1C7EDF1F28B8E46AA12D3068E149FF0DDCD03896CE",
    "bullet_normalization": "3D65B71EB65183483412794B19F6F983D350F3E76BE58FE88D123BB92F1B0A1C",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"JSON root is not an object: {path}")
    return value


def args(out_root: Path, progress: Path = batch.DEFAULT_PROGRESS) -> SimpleNamespace:
    return SimpleNamespace(
        switch_v13_zip=batch.DEFAULT_V13_ZIP,
        switch_v11_zip=batch.DEFAULT_V11_ZIP,
        base_jp=batch.GAME_ROOT / "MSG" / "JP" / "msggame.bin",
        pk_jp=batch.GAME_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        pk_sc=batch.DEFAULT_PK_SC,
        progress=progress,
        target_catalog=batch.DEFAULT_TARGET_CATALOG,
        out_root=out_root,
    )


class SwitchMsggameV13InvariantRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME)
        cls.evidence = load(WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME)
        cls.review = load(WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME)
        cls.validation = load(WORKSTREAM_ROOT / batch.VALIDATION_NAME)

    def test_published_scope_and_class_hashes_are_pinned(self) -> None:
        self.assertEqual(580, self.overlay["entry_count"])
        self.assertEqual(batch.RESOURCE, self.overlay["resource"])
        self.assertTrue(self.overlay["migration_provenance"]["v13_text_identical_to_v11"])
        self.assertEqual(batch.EXPECTED, self.validation["selection"])
        self.assertEqual(580, self.evidence["entry_count"])
        self.assertEqual(580, self.review["selected_count"])
        self.assertEqual(1879, self.review["excluded_count"])
        for mode, expected_hash in EXPECTED_CLASS_HASHES.items():
            self.assertEqual(batch.EXPECTED[mode], self.validation["selection_classes"][mode]["count"])
            self.assertEqual(expected_hash, self.validation["selection_classes"][mode]["coordinates_sha256"])
        self.assertTrue(self.validation["proofs"]["later_overlays_source_free_target_only_and_disjoint"])

    def test_selected_coordinates_are_target_only_and_disjoint(self) -> None:
        selected = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.overlay["entries"]
        }
        self.assertEqual(580, len(selected))
        target = batch.load_target_catalog(batch.DEFAULT_TARGET_CATALOG)["coordinates"]
        existing = batch.collect_existing(batch.DEFAULT_PROGRESS)["coordinates"]
        excluded = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.review["entries"]
            if entry["status"] == "excluded"
        }
        self.assertTrue(selected <= target)
        self.assertTrue(selected.isdisjoint(existing))
        self.assertTrue(selected.isdisjoint(excluded))
        self.assertEqual(1879, len(excluded))

    def test_every_selected_replacement_has_exact_structure_and_roles(self) -> None:
        self.assertTrue(all(entry["invariants_exact_after_recovery"] for entry in self.evidence["entries"]))
        self.assertTrue(all(entry["delimiter_role_sequence_equal"] for entry in self.evidence["entries"]))
        for entry in self.overlay["entries"]:
            self.assertTrue(batch.prior.has_hangul_syllable(entry["ko"]))
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.script_counts(entry["ko"]))

    def test_unresolved_line_redistribution_and_annotations_remain_excluded(self) -> None:
        reasons = {}
        for entry in self.review["entries"]:
            if entry["status"] == "excluded":
                reasons[entry["reason"]] = reasons.get(entry["reason"], 0) + 1
        self.assertEqual(
            {"unresolved_invariant_mismatch": 1877, "unresolved_ideographic_annotation": 2},
            reasons,
        )
        self.assertTrue(self.validation["proofs"]["unresolved_internal_line_redistribution_not_transferred"])

    def test_artifacts_are_source_free_and_hash_pinned(self) -> None:
        for relative, expected in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            self.assertEqual(expected, digest(path), relative)
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                batch.script_counts(path.read_text(encoding="utf-8")),
                relative,
            )

    def test_isolated_builds_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            roots = [Path(temporary) / name for name in ("a", "b")]
            results = [batch.build(args(root)) for root in roots]
            self.assertEqual(580, results[0]["entry_count"])
            self.assertEqual(EXPECTED_TARGET_SHA256, results[0]["target_packed_sha256"])
            self.assertEqual(results[0]["target_packed_sha256"], results[1]["target_packed_sha256"])
            for relative in EXPECTED_HASHES:
                self.assertEqual((roots[0] / relative).read_bytes(), (roots[1] / relative).read_bytes())
                self.assertEqual((roots[0] / relative).read_bytes(), (WORKSTREAM_ROOT / relative).read_bytes())

    def test_self_registration_before_and_after_is_selection_stable(self) -> None:
        progress = load(batch.DEFAULT_PROGRESS)
        resource = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = []
            for name, registered in (("absent", False), ("registered", True)):
                globs = [item for item in resource["overlay_globs"] if item != batch.SELF_RELATIVE]
                if registered:
                    globs.append(batch.SELF_RELATIVE)
                resource["overlay_globs"] = globs
                progress_path = root / f"progress-{name}.json"
                progress_path.write_text(
                    json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                output = root / name
                result = batch.build(args(output, progress_path))
                self.assertEqual(int(registered), result["self_registration_count"])
                outputs.append(output)
            for relative in EXPECTED_HASHES:
                self.assertEqual((outputs[0] / relative).read_bytes(), (outputs[1] / relative).read_bytes())
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), (outputs[0] / relative).read_bytes())


if __name__ == "__main__":
    unittest.main()
