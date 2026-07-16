#!/usr/bin/env python3
"""Public contract tests for the Steam PK 1.1.7 JP v0.8.0 v4 candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_steam_jp_117_candidate_v4.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_117_candidate_v4_tested", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJP117CandidateV4Tests(unittest.TestCase):
    def test_runtime_release_name_and_exact_jp_target_vector(self) -> None:
        self.assertEqual(
            builder.DEFAULT_ZIP_NAME,
            "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip",
        )
        self.assertEqual(builder.TARGETS, builder.EXPECTED_TARGETS)
        self.assertEqual(len(builder.TARGETS), 12)
        self.assertTrue(
            all(path.startswith("MSG/JP/") or path.startswith("MSG_PK/JP/") or path.startswith("RES_JP") for path in builder.TARGETS)
        )
        self.assertFalse(any("/SC/" in path or path.startswith("RES_SC") for path in builder.TARGETS))

    def test_v3_verification_is_immutable_and_only_three_paths_can_change(self) -> None:
        self.assertEqual(
            hashlib.sha256(builder.V3.VERIFICATION_PATH.read_bytes()).hexdigest().upper(),
            builder.V3_VERIFICATION_SHA256,
        )
        verification = builder.load_v3_verification()
        self.assertEqual(verification["candidate_paths"], list(builder.TARGETS))
        self.assertEqual(
            set(builder.V3_UNCHANGED_TARGETS),
            set(builder.TARGETS)
            - {builder.MSGUI_RESOURCE, builder.MSGDATA_RESOURCE, builder.MSGEV_RESOURCE},
        )
        self.assertEqual(len(builder.V3_UNCHANGED_TARGETS), 9)
        self.assertNotIn(builder.MSGUI_RESOURCE, builder.IMMUTABLE_V07_TARGETS)
        self.assertEqual(len(builder.IMMUTABLE_V07_TARGETS), 6)

    def test_issue_components_target_the_expected_resources_and_pins(self) -> None:
        scenario = builder.load_scenario()
        clan = builder.load_clan()
        tactics = builder.load_tactics()
        office = builder.load_office()
        msgev_residual = builder.load_msgev_residual()
        self.assertEqual(scenario.RESOURCE, builder.MSGUI_RESOURCE)
        self.assertEqual(clan.RESOURCE, builder.MSGDATA_RESOURCE)
        self.assertEqual(tactics.RESOURCE, builder.MSGDATA_RESOURCE)
        self.assertEqual(office.RESOURCE, builder.MSGDATA_RESOURCE)
        self.assertEqual(msgev_residual.RESOURCE, builder.MSGEV_RESOURCE)
        self.assertEqual(scenario.ENTRY_ID, 1051)
        self.assertEqual(clan.NORMALIZED_ENTRY_COUNT, 159)
        self.assertEqual(tuple(tactics.TARGET_IDS), (15520, 15521, 15522, 15524, 15525, 15526, 15527, 15528, 15529, 15530))
        self.assertEqual(tactics.CLAN_NORMALIZED_BASELINE_PIN, clan.OUTPUT_CANDIDATE_PIN)
        self.assertEqual(
            tactics.OUTPUT_CANDIDATE_PIN["packed_sha256"],
            "4E0B1009789D6EF3935DA359932D73685447890784796BE3702D50C8D64E4387",
        )
        self.assertEqual(office.DISPLAY_PAIR_COUNT, 146)
        self.assertEqual(office.TARGET_CONTRACT_COUNT, 292)
        self.assertEqual(builder.EXPECTED_OFFICE_DISPLAY_DELTA_COUNT, 113)
        self.assertEqual(builder.EXPECTED_OFFICE_READING_DELTA_COUNT, 8)
        self.assertEqual(builder.EXPECTED_OFFICE_DELTA_COUNT, 121)
        self.assertEqual(
            builder.EXPECTED_OFFICE_COMPOSED_CANDIDATE_PIN["packed_sha256"],
            "2D1BEFF03972777FBA5EE0B8FEF24E6A03B285DA466A4DA439794D21587A0F69",
        )
        self.assertEqual(
            builder.EXPECTED_OFFICE_DISPLAY_READING_ANCHORS,
            (
                (16_399, 16_670, "관백", "간파쿠"),
                (16_402, 16_673, "우대신", "우다이진"),
                (16_404, 16_675, "대납언", "다이나곤"),
                (16_613, 16_884, "정이대장군", "세이이다이쇼군"),
            ),
        )
        self.assertEqual(
            builder.EXPECTED_MSGEV_RESIDUAL_COMPOSED_CANDIDATE_PIN["packed_sha256"],
            "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5",
        )
        self.assertEqual(builder.EXPECTED_MSGEV_RESIDUAL_DELTA_COUNT, 66)
        self.assertEqual(len(msgev_residual.TARGET_IDS), 66)

    def test_component_composition_is_pinned_and_preserves_clan_labels(self) -> None:
        if not builder.STOCK_ROOT.is_dir():
            self.skipTest("private pristine Steam 1.1.7 stock is unavailable")
        scenario = builder.load_scenario()
        v3_msgui, _metadata = scenario.baseline_blob(builder.STOCK_ROOT)
        scenario_candidate, scenario_meta = builder.build_scenario_hotfix(
            builder.STOCK_ROOT, v3_msgui
        )
        self.assertEqual(scenario_meta["delta_count"], 1)
        self.assertEqual(
            builder._changed_ids(scenario.MSGUI, v3_msgui, scenario_candidate), [1051]
        )

        v3_common, _common_meta = builder.V3.build_common(builder.STOCK_ROOT)
        msgev_residual = builder.load_msgev_residual()
        msgev_candidate, msgev_meta = builder.build_msgev_residual_hotfix(
            builder.STOCK_ROOT, v3_common["msgev.bin"]
        )
        self.assertEqual(msgev_meta["event_story_delta_count"], 50)
        self.assertEqual(msgev_meta["event_label_delta_count"], 16)
        self.assertEqual(msgev_meta["delta_count"], 66)
        self.assertTrue(msgev_meta["non_target_texts_preserved"])
        self.assertEqual(
            builder.full_packed_spec(msgev_residual.COMMON, msgev_candidate),
            builder.EXPECTED_MSGEV_RESIDUAL_COMPOSED_CANDIDATE_PIN,
        )
        msgdata_candidate, msgdata_meta = builder.build_msgdata_hotfixes(
            builder.STOCK_ROOT, v3_common["msgdata.bin"]
        )
        tactic_meta = msgdata_meta["tactics_reading"]
        office_meta = msgdata_meta["office_titles_core"]
        self.assertEqual(tactic_meta["clan_delta_count"], 159)
        self.assertEqual(tactic_meta["tactics_delta_count"], 10)
        self.assertTrue(tactic_meta["all_active_tactics_reading_slots_no_latin"])
        self.assertEqual(office_meta["display_delta_count"], 113)
        self.assertEqual(office_meta["reading_delta_count"], 8)
        self.assertEqual(office_meta["delta_count"], 121)
        self.assertTrue(office_meta["deferred_domains"]["geographic_title_categories"])
        self.assertTrue(office_meta["deferred_domains"]["bakufu_16614_16624"])
        office = builder.load_office()
        self.assertEqual(
            builder.full_packed_spec(office.COMMON, msgdata_candidate),
            builder.EXPECTED_OFFICE_COMPOSED_CANDIDATE_PIN,
        )
        _header, raw = office.COMMON.decompress_wrapper(msgdata_candidate)
        table = office.COMMON.parse_message_table(raw)
        for display_id, reading_id, display, reading in builder.EXPECTED_OFFICE_DISPLAY_READING_ANCHORS:
            self.assertEqual(table.texts[display_id], display)
            self.assertEqual(table.texts[reading_id], reading)

    def test_zip_writer_requires_and_preserves_all_twelve_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate"
            for index, relative in enumerate(builder.TARGETS):
                path = candidate / Path(relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"v4-{index}-{relative}".encode("utf-8"))
            destination = root / builder.DEFAULT_ZIP_NAME
            first = builder.V3.V2.make_zip(candidate, destination)
            first_blob = destination.read_bytes()
            destination.unlink()
            second = builder.V3.V2.make_zip(candidate, destination)
            self.assertEqual(first, second)
            self.assertEqual(first_blob, destination.read_bytes())

    def test_output_guards_reject_live_or_repository_destinations(self) -> None:
        for path in (builder.REPO, builder.REPO / "workstreams", builder.V3.V2.STEAM_ROOT):
            with self.subTest(path=path):
                with self.assertRaises(builder.CandidateV4Error):
                    builder.validate_destination(path)

    def test_tracked_verification_is_exact_jp_only_and_source_free(self) -> None:
        value = builder.load_tracked_verification()
        self.assertEqual(value["schema"], builder.VERIFICATION_SCHEMA)
        self.assertEqual(value["runtime"], {
            "distribution": "Steam",
            "language_route": "JP",
            "pk_version": "1.1.7",
            "steam_build_id": 18_823_764,
        })
        self.assertEqual(value["candidate_file_count"], 12)
        self.assertEqual(value["candidate_paths"], list(builder.TARGETS))
        self.assertEqual(set(value["candidates"]), set(builder.TARGETS))
        self.assertEqual(value["translation"]["scenario_calendar_month_delta_entries"], 1)
        self.assertEqual(value["translation"]["msgev_residual_event_story_delta_entries"], 50)
        self.assertEqual(value["translation"]["msgev_residual_event_label_delta_entries"], 16)
        self.assertEqual(value["translation"]["msgev_residual_wave09_delta_entries"], 66)
        self.assertEqual(value["translation"]["clan_label_normalization_delta_entries"], 159)
        self.assertEqual(value["translation"]["tactics_reading_delta_entries"], 10)
        self.assertEqual(value["translation"]["office_titles_core_display_delta_entries"], 113)
        self.assertEqual(value["translation"]["office_titles_core_reading_delta_entries"], 8)
        self.assertEqual(value["translation"]["office_titles_core_delta_entries"], 121)
        self.assertEqual(
            value["candidates"][builder.MSGUI_RESOURCE],
            {"sha256": "29D0C6CCC262E7AB757AA5D0819224370DEDEF4CF250E89FC88B24E600EF2169", "size": 121608},
        )
        self.assertEqual(
            value["candidates"][builder.MSGDATA_RESOURCE],
            {"sha256": "2D1BEFF03972777FBA5EE0B8FEF24E6A03B285DA466A4DA439794D21587A0F69", "size": 496999},
        )
        self.assertEqual(
            value["candidates"][builder.MSGEV_RESOURCE],
            {"sha256": "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5", "size": 1040799},
        )
        checks = value["checks"]
        self.assertTrue(checks["v3_baseline_candidate_exact"])
        self.assertTrue(checks["scenario_date_id1051_integrated"])
        self.assertTrue(checks["msgev_residual_wave09_66_integrated"])
        self.assertTrue(checks["clan_label_normalization_159_integrated"])
        self.assertTrue(checks["tactics_reading_hotfix_integrated"])
        self.assertTrue(checks["office_titles_core_121_integrated"])
        self.assertTrue(checks["office_titles_geographic_and_bakufu_deferred"])
        self.assertTrue(checks["exact_twelve_files"])
        self.assertFalse(checks["sc_container_used"])
        self.assertFalse(checks["steam_files_written"])
        self.assertNotIn("commercial_source_text", json.dumps(value, ensure_ascii=False))

    def test_public_workstream_contains_no_game_binary(self) -> None:
        forbidden = {".bin", ".g1n", ".ttf", ".otf", ".zip", ".pixels"}
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in forbidden
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
