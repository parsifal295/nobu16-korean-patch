#!/usr/bin/env python3
"""Public contract tests for the Steam PK 1.1.7 JP-route v0.8.0 candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_steam_jp_117_candidate_v3.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_117_candidate_v3_tested", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJP117CandidateV3Tests(unittest.TestCase):
    def test_runtime_version_zip_name_and_exact_target_vector(self) -> None:
        self.assertEqual(
            builder.DEFAULT_ZIP_NAME,
            "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip",
        )
        self.assertEqual(builder.TARGETS, builder.EXPECTED_TARGETS)
        self.assertEqual(len(builder.TARGETS), 12)
        self.assertTrue(all("/JP/" in path or path.startswith("RES_JP") for path in builder.TARGETS))
        self.assertFalse(any("/SC/" in path or path.startswith("RES_SC") for path in builder.TARGETS))

    def test_v07_verification_is_immutable_and_non_common_scope_is_exact(self) -> None:
        previous = builder.load_v07_verification()
        self.assertEqual(
            builder.sha256(builder.V07_VERIFICATION_PATH.read_bytes()),
            builder.V07_VERIFICATION_SHA256,
        )
        self.assertEqual(
            set(builder.IMMUTABLE_V07_TARGETS),
            {
                "MSG/JP/strdata.bin",
                "MSG_PK/JP/msggame.bin",
                "MSG_PK/JP/msgui.bin",
                "RES_JP/res_lang.bin",
                "RES_JP_PK/res_lang_pk.bin",
                "RES_JP_PK_PORT/res_lang_pk_port1.bin",
                "RES_JP_PK_PORT/res_lang_pk_port2.bin",
            },
        )
        self.assertEqual(
            builder.immutable_v07_candidate_pins(),
            {
                path: previous["candidates"][path]
                for path in builder.IMMUTABLE_V07_TARGETS
            },
        )

    def test_wave08_integration_interface_and_accounting(self) -> None:
        integration = builder.load_wave08_integration()
        self.assertTrue(callable(integration.build_all))
        if not builder.STOCK_ROOT.is_dir():
            self.skipTest("private pristine Steam 1.1.7 stock is unavailable")
        candidates, metadata = builder.build_common(builder.STOCK_ROOT)
        self.assertEqual(tuple(candidates), builder.COMMON_FILES)
        self.assertEqual(metadata["applied_entries"], 40_581)
        self.assertEqual(metadata["wave08_semantic_delta_entries"], 94)
        self.assertEqual(metadata["surname_recovery_delta_entries"], 980)
        self.assertEqual(metadata["wave08_reviewed_semantic_gap_remaining"], 0)
        self.assertEqual(metadata["retained_internal_dummy_entries"], 2)
        self.assertEqual(metadata["excluded_source_equal_contract_entries"], 1_796)
        self.assertEqual(metadata["format_contract_blocked_entries"], 730)
        self.assertEqual(metadata["alignment_gap_entries"], 62)
        self.assertEqual(metadata["review_backlog_entries"], 792)
        self.assertEqual(metadata["source_union_effective_entries"], 43_169)
        self.assertEqual(
            metadata["applied_entries"]
            + metadata["excluded_source_equal_contract_entries"]
            + metadata["format_contract_blocked_entries"]
            + metadata["alignment_gap_entries"],
            metadata["source_union_effective_entries"],
        )
        self.assertEqual(set(metadata["candidates"]), set(builder.COMMON_FILES))

    def test_msgdata_officer_surname_and_given_name_compose_in_korean(self) -> None:
        if not builder.STOCK_ROOT.is_dir():
            self.skipTest("private pristine Steam 1.1.7 stock is unavailable")
        candidates, metadata = builder.build_common(builder.STOCK_ROOT)
        probe = metadata["officer_name_probe"]
        self.assertEqual(probe["surname_id"], 84)
        self.assertEqual(probe["given_name_id"], 1_266)
        self.assertEqual(probe["surname_ko"], "오다 ")
        self.assertEqual(probe["given_name_ko"], "노부나가")
        self.assertEqual(probe["composed_ko"], "오다 노부나가")
        integration = builder.load_wave08_integration()
        _wrapper, raw = integration.COMMON.decompress_wrapper(candidates["msgdata.bin"])
        table = integration.COMMON.parse_message_table(raw)
        self.assertEqual(table.texts[84] + table.texts[1_266], "오다 노부나가")

    def test_high_resolution_font_routes_remain_byte_pinned_to_v07(self) -> None:
        configured = builder.V2.configure_font_candidates(builder.DEFAULT_FONT_ROOT)
        previous = builder.load_v07_verification()["candidates"]
        self.assertEqual(set(configured["routes"]), set(builder.FONT_RESOURCES))
        self.assertEqual(
            configured["routes"],
            {path: previous[path] for path in builder.FONT_RESOURCES},
        )

    def test_zip_writer_requires_and_preserves_all_twelve_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate"
            for index, relative in enumerate(builder.TARGETS):
                path = candidate / Path(relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"v3-{index}-{relative}".encode("utf-8"))
            destination = root / builder.DEFAULT_ZIP_NAME
            first = builder.V2.make_zip(candidate, destination)
            first_blob = destination.read_bytes()
            destination.unlink()
            second = builder.V2.make_zip(candidate, destination)
            self.assertEqual(first, second)
            self.assertEqual(first_blob, destination.read_bytes())

    def test_output_guards_reject_live_or_repository_destinations(self) -> None:
        for path in (builder.REPO, builder.REPO / "workstreams", builder.V2.STEAM_ROOT):
            with self.subTest(path=path):
                with self.assertRaises(builder.CandidateV3Error):
                    builder.validate_destination(path)

    def test_tracked_verification_is_exact_jp_only_and_source_free(self) -> None:
        value = builder.load_tracked_verification()
        self.assertEqual(value["schema"], builder.VERIFICATION_SCHEMA)
        self.assertEqual(value["runtime"]["distribution"], "Steam")
        self.assertEqual(value["runtime"]["pk_version"], "1.1.7")
        self.assertEqual(value["runtime"]["steam_build_id"], 18_823_764)
        self.assertEqual(value["runtime"]["language_route"], "JP")
        self.assertEqual(value["candidate_file_count"], 12)
        self.assertEqual(value["candidate_paths"], list(builder.TARGETS))
        self.assertEqual(set(value["candidates"]), set(builder.TARGETS))
        translation = value["translation"]
        self.assertEqual(translation["common_messages_applied"], 40_581)
        self.assertEqual(
            translation["common_messages_wave08_semantic_delta_entries"], 94
        )
        self.assertEqual(
            translation["common_messages_surname_recovery_delta_entries"], 980
        )
        self.assertEqual(
            translation[
                "common_messages_wave08_reviewed_semantic_gap_remaining"
            ],
            0,
        )
        self.assertEqual(
            translation["common_messages_retained_internal_dummy_entries"], 2
        )
        self.assertEqual(
            translation["common_messages_excluded_source_equal_contract_entries"],
            1_796,
        )
        self.assertEqual(
            translation["common_messages_format_contract_blocked_entries"], 730
        )
        self.assertEqual(
            translation["common_messages_alignment_gap_entries"], 62
        )
        self.assertEqual(
            translation["common_messages_review_backlog_entries"], 792
        )
        self.assertEqual(
            translation["common_messages_source_union_effective_entries"],
            43_169,
        )
        self.assertNotIn("common_messages_unresolved", translation)
        self.assertEqual(value["zip"]["name"], builder.DEFAULT_ZIP_NAME)
        self.assertEqual(value["zip"]["member_count"], 12)
        checks = value["checks"]
        self.assertTrue(checks["v0_7_0_non_common_candidates_exact"])
        self.assertTrue(checks["high_resolution_seoul_hangang_four_routes_exact"])
        self.assertTrue(checks["wave08_common_messages_integrated"])
        self.assertTrue(checks["officer_surnames_980_integrated"])
        self.assertTrue(checks["officer_name_id84_id1266_composition_verified"])
        self.assertTrue(checks["exact_twelve_files"])
        self.assertFalse(checks["sc_container_used"])
        self.assertFalse(checks["steam_files_written"])
        encoded = json.dumps(value, ensure_ascii=False)
        self.assertNotIn("commercial_source_text", encoded)

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
