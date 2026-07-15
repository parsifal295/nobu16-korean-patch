from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKSTREAM = ROOT / "workstreams" / "strdata_pk_shared_manual_b01"
MODULE_PATH = WORKSTREAM / "build_strdata_pk_shared_manual_b01.py"
SPEC = importlib.util.spec_from_file_location(
    "build_strdata_pk_shared_manual_b01_for_tests", MODULE_PATH
)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)
GAME_ROOT = ROOT.parent


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class StrdataPkSharedManualB01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = builder.direct.load_inputs(GAME_ROOT, builder.DEFAULT_SWITCH_ZIP)
        cls.classified = builder.direct.classify_direct(cls.inputs)
        cls.models = builder.make_models(cls.inputs, cls.classified, ROOT)
        cls.overlay = json.loads(
            (WORKSTREAM / "public" / builder.OVERLAY_NAME).read_text(encoding="utf-8")
        )
        cls.evidence = json.loads(
            (WORKSTREAM / "evidence" / builder.EVIDENCE_NAME).read_text(encoding="utf-8")
        )
        cls.review = json.loads(
            (WORKSTREAM / "review" / builder.REVIEW_NAME).read_text(encoding="utf-8")
        )
        cls.validation = json.loads(
            (WORKSTREAM / builder.VALIDATION_NAME).read_text(encoding="utf-8")
        )

    def test_selection_is_exactly_the_disjoint_manual_ui_gap(self) -> None:
        selection = self.models["selection"]
        self.assertEqual(24_425, selection["published_predecessor_coverage"])
        self.assertEqual(2_265, selection["remaining_before_b00_exclusion"])
        self.assertEqual(100, selection["b00_excluded_count"])
        self.assertEqual(2_165, selection["eligible_remaining"])
        self.assertEqual(206, selection["selected_count"])
        self.assertEqual(
            builder.EXPECTED["selected_coordinates_sha256"],
            selection["selected_coordinates_sha256"],
        )
        coordinates = [
            (entry["block_id"], entry["slot_id"]) for entry in self.overlay["entries"]
        ]
        self.assertEqual(coordinates, sorted(set(coordinates)))
        self.assertTrue(all(block_id in (0, 1) for block_id, _slot_id in coordinates))
        self.assertFalse(any(block_id == 0 and slot_id < 100 for block_id, slot_id in coordinates))
        self.assertFalse(set(coordinates) & set(self.models["predecessor_values"]))

    def test_committed_source_free_artifacts_are_exact_models(self) -> None:
        self.assertEqual(builder.encode_json(self.models["overlay"]), (WORKSTREAM / "public" / builder.OVERLAY_NAME).read_bytes())
        self.assertEqual(builder.encode_json(self.models["evidence"]), (WORKSTREAM / "evidence" / builder.EVIDENCE_NAME).read_bytes())
        self.assertEqual(builder.encode_json(self.models["review"]), (WORKSTREAM / "review" / builder.REVIEW_NAME).read_bytes())
        for path in (
            WORKSTREAM / "public" / builder.OVERLAY_NAME,
            WORKSTREAM / "evidence" / builder.EVIDENCE_NAME,
            WORKSTREAM / "review" / builder.REVIEW_NAME,
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(builder.HAN_OR_KANA_RE.search(text), path)
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(self.overlay["distribution_policy"]["contains_complete_game_resource"])

    def test_all_entries_preserve_format_and_have_review_evidence(self) -> None:
        pc_sc = self.classified["pc_sc"]
        evidence_by_coordinate = {
            (row["block_id"], row["slot_id"]): row for row in self.evidence["entries"]
        }
        review_by_coordinate = {
            (row["block_id"], row["slot_id"]): row for row in self.review["entries"]
        }
        self.assertEqual(206, len(evidence_by_coordinate))
        self.assertEqual(206, len(review_by_coordinate))
        for entry in self.overlay["entries"]:
            coordinate = (entry["block_id"], entry["slot_id"])
            self.assertEqual(
                builder.text_hash(pc_sc[coordinate]),
                entry["source_sc_utf16le_sha256"],
            )
            self.assertEqual([], builder.common.invariant_mismatches(pc_sc[coordinate], entry["ko"]))
            self.assertIsNone(builder.HAN_OR_KANA_RE.search(entry["ko"]))
            self.assertTrue(any(0xAC00 <= ord(character) <= 0xD7A3 for character in entry["ko"]))
            self.assertTrue(evidence_by_coordinate[coordinate]["format_invariants_equal"])
            self.assertEqual("reviewed", review_by_coordinate[coordinate]["status"])

    def test_ui_priority_categories_cover_every_selected_coordinate(self) -> None:
        expected = {
            "battle_or_management_ui": 8,
            "event_caption": 21,
            "hud_label_or_status_help": 18,
            "menu_dialog_or_system_prompt": 42,
            "policy_effect_or_help": 27,
            "scenario_description": 5,
            "ui_asset_label": 85,
        }
        self.assertEqual(expected, self.models["category_counts"])
        self.assertEqual(206, sum(expected.values()))
        self.assertEqual(
            {"manual-switch-semantic-acceptance": 18, "manual-translation-override": 188},
            self.models["translation_method_counts"],
        )

    def test_high_risk_ui_samples_are_semantically_and_structurally_fixed(self) -> None:
        values = {
            (entry["block_id"], entry["slot_id"]): entry["ko"]
            for entry in self.overlay["entries"]
        }
        self.assertEqual("시작 메뉴로 돌아가시겠습니까?", values[(1, 2823)])
        self.assertEqual(
            "수행 중인 임무가 없습니다.\n\n지도에서 출진 목적지를 선택하십시오.",
            values[(1, 2840)],
        )
        self.assertEqual("성하 시설 \x1bC3%s\x1bCZ의 상업 %+d", values[(0, 22350)])
        self.assertEqual("군량 %d, %s에 양도(%d→%d)", values[(1, 3120)])
        self.assertEqual("호화 평성\ue0033", values[(0, 17802)])
        self.assertEqual("\x1bCQ\ue020\x1bCZ공성 중(강공)", values[(1, 3462)])

    def test_candidate_a_b_is_deterministic_and_preserves_every_other_coordinate(self) -> None:
        integrated = {**self.models["predecessor_values"], **self.models["values"]}
        candidate_a, stats_a = builder.build_candidate(self.inputs, integrated)
        candidate_b, stats_b = builder.build_candidate(self.inputs, integrated)
        self.assertEqual(candidate_a, candidate_b)
        self.assertEqual(stats_a, stats_b)
        self.assertEqual(self.validation["candidate"], stats_a)
        _wrapper, raw = builder.decompress_wrapper(candidate_a)
        rebuilt = builder.coordinate_texts(builder.parse_strdata(raw))
        pristine = self.classified["pc_sc"]
        changed = {coordinate for coordinate in pristine if pristine[coordinate] != rebuilt[coordinate]}
        self.assertEqual(set(integrated), changed)
        self.assertTrue(all(rebuilt[coordinate] == replacement for coordinate, replacement in integrated.items()))
        self.assertTrue(all(rebuilt[coordinate] == pristine[coordinate] for coordinate in pristine if coordinate not in integrated))

    def test_progress_registration_is_stable_absent_self_and_successor(self) -> None:
        targets, _snapshot = builder.load_target_catalog(builder.TARGET_CATALOG)
        predecessor_coordinates = set(self.models["predecessor_values"])
        with tempfile.TemporaryDirectory(prefix="n16-strdata-manual-progress-") as temporary:
            repo = Path(temporary)
            progress_path = repo / "progress.json"
            patterns = [row["path"] for row in builder.PREDECESSORS]

            def write_progress() -> None:
                progress_path.write_bytes(
                    builder.encode_json(
                        {
                            "shared_strings": [
                                {"path": builder.RESOURCE, "overlay_globs": list(patterns)}
                            ]
                        }
                    )
                )

            write_progress()
            absent = builder.audit_progress_registration(
                progress_path,
                repo,
                self.classified["pc_sc"],
                targets,
                predecessor_coordinates,
                self.models["overlay"],
            )
            self.assertEqual(0, absent["self_registration_count"])

            self_path = repo / builder.SELF_LOGICAL_PATH
            self_path.parent.mkdir(parents=True, exist_ok=True)
            self_path.write_bytes(builder.encode_json(self.models["overlay"]))
            patterns.append(builder.SELF_LOGICAL_PATH)
            write_progress()
            registered = builder.audit_progress_registration(
                progress_path,
                repo,
                self.classified["pc_sc"],
                targets,
                predecessor_coordinates,
                self.models["overlay"],
            )
            self.assertEqual(1, registered["self_registration_count"])

            successor_coordinate = (0, 0)
            self.assertIn(successor_coordinate, targets)
            self.assertNotIn(successor_coordinate, predecessor_coordinates)
            self.assertNotIn(successor_coordinate, self.models["values"])
            successor = {
                "schema": builder.OVERLAY_SCHEMA,
                "overlay_id": "synthetic-followup",
                "resource": builder.RESOURCE,
                "base_language": "SC",
                "entry_count": 1,
                "distribution_policy": {
                    "contains_commercial_source_text": False,
                    "contains_complete_game_resource": False,
                },
                "defaults": {"status": "reviewed"},
                "entries": [
                    {
                        "block_id": 0,
                        "slot_id": 0,
                        "source_sc_utf16le_sha256": builder.text_hash(
                            self.classified["pc_sc"][successor_coordinate]
                        ),
                        "ko": self.classified["safe_values"][successor_coordinate],
                    }
                ],
            }
            successor_logical = "workstreams/future/public/successor.json"
            successor_path = repo / successor_logical
            successor_path.parent.mkdir(parents=True, exist_ok=True)
            successor_path.write_bytes(builder.encode_json(successor))
            patterns.append(successor_logical)
            write_progress()
            followed = builder.audit_progress_registration(
                progress_path,
                repo,
                self.classified["pc_sc"],
                targets,
                predecessor_coordinates,
                self.models["overlay"],
            )
            self.assertEqual(1, followed["self_registration_count"])
            self.assertEqual(1, followed["successor_overlay_count"])
            self.assertEqual(1, followed["successor_coordinate_count"])
            self.assertTrue(followed["successors_excluded_from_predecessor_selection"])

    def test_builder_uses_no_user_untracked_strdata_dependency(self) -> None:
        original = builder.direct.EXISTING_B00
        try:
            builder.direct.EXISTING_B00 = ROOT / "does-not-exist" / "user-b00.json"
            models = builder.make_models(self.inputs, self.classified, ROOT)
        finally:
            builder.direct.EXISTING_B00 = original
        self.assertEqual(self.models["overlay"], models["overlay"])
        self.assertEqual(self.models["selection"], models["selection"])

    def test_full_build_writes_only_private_outputs(self) -> None:
        watched = [
            GAME_ROOT / "MSG" / "SC" / "strdata.bin",
            GAME_ROOT / "MSG" / "JP" / "strdata.bin",
            builder.PROGRESS,
            ROOT / "README.md",
            ROOT / "workstreams" / "font_seoulhangang_v1" / "manifest.v1.json",
        ]
        before = {path: file_sha256(path) for path in watched}
        with tempfile.TemporaryDirectory(prefix="n16-strdata-manual-build-") as temporary:
            root = Path(temporary)
            validation = builder.build(
                GAME_ROOT,
                builder.DEFAULT_SWITCH_ZIP,
                ROOT,
                root / "artifacts",
                root / "candidate" / builder.RESOURCE,
                builder.PROGRESS,
            )
            self.assertEqual(206, validation["selection"]["selected_count"])
            self.assertTrue((root / "candidate" / builder.RESOURCE).is_file())
            self.assertEqual(
                self.validation["candidate"]["target_packed_sha256"],
                validation["candidate"]["target_packed_sha256"],
            )
        after = {path: file_sha256(path) for path in watched}
        self.assertEqual(before, after)

    def test_committed_validation_records_required_safety_and_coverage(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertEqual(file_sha256(MODULE_PATH), self.validation["generator"]["sha256"])
        self.assertEqual(
            {"target_count": 26_690, "before": 24_425, "added": 206, "after": 24_631, "remaining": 2_059},
            self.validation["coverage"],
        )
        self.assertEqual(0, self.validation["format_contract"]["han_or_kana_in_public_artifacts"])
        self.assertTrue(self.validation["format_contract"]["all_selected_invariants_equal"])
        self.assertTrue(self.validation["format_contract"]["all_nonselected_coordinates_preserved"])
        self.assertTrue(self.validation["reproducibility"]["in_memory_candidate_a_b_equal"])
        for artifact in self.validation["artifacts"].values():
            path = WORKSTREAM / artifact["path"]
            self.assertEqual(path.stat().st_size, artifact["size"])
            self.assertEqual(file_sha256(path), artifact["sha256"])
        self.assertTrue(all(value is False for value in self.validation["safety"].values()))


if __name__ == "__main__":
    unittest.main()
