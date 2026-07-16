#!/usr/bin/env python3
"""Regression tests for the isolated Steam JP exact-14 v0.10.0 builder."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_steam_jp_117_candidate_v7.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_117_candidate_v7_tested", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJP117CandidateV7Tests(unittest.TestCase):
    def test_release_name_and_exact_fourteen_jp_vector(self) -> None:
        self.assertEqual(builder.DEFAULT_ZIP_NAME, "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.0.zip")
        self.assertEqual(builder.TARGETS, builder.EXPECTED_TARGETS)
        self.assertEqual(len(builder.TARGETS), 14)
        self.assertEqual(len(builder.REPLACED_RESOURCES), 12)
        self.assertEqual(builder.RETAINED_RESOURCES, ("MSG_PK/JP/msggame.bin", "MSG_PK/JP/msgire.bin"))
        self.assertTrue(all("/JP/" in path or path.startswith("RES_JP") for path in builder.TARGETS))
        self.assertFalse(any("/SC/" in path or path.startswith("RES_SC") for path in builder.TARGETS))

    def test_baseline_is_pinned_v09_release_not_a_game_directory(self) -> None:
        v6 = builder.load_v6_verification()
        self.assertEqual(v6["candidate_file_count"], 14)
        self.assertEqual(v6["zip"], {"member_count": 14, **builder.BASELINE_RELEASE_PIN})
        self.assertTrue(builder.DEFAULT_BASELINE_ZIP.is_file())
        self.assertNotIn("SteamLibrary", str(builder.DEFAULT_BASELINE_ZIP))
        self.assertNotIn("live-game", BUILDER_PATH.read_text(encoding="utf-8"))
        self.assertNotIn("--live-game-root", BUILDER_PATH.read_text(encoding="utf-8"))

    def test_component_builder_and_p103_artifact_pins(self) -> None:
        self.assertEqual(
            builder.BUILDER_PINS["msgdata_p1"][1],
            "22804D1B15BCDF43E15846629F7995C5C925F618C3FCB61E29439DDE4F2F6444",
        )
        for key in ("msgui_p0", "strdata_p0", "msgdata_p1", "msgev_p1", "base_msggame_p2", "tail", "font_parser"):
            path, expected = builder.BUILDER_PINS[key]
            with self.subTest(key=key):
                self.assertEqual(builder.path_spec(path)["sha256"], expected)
        expected_p103 = {
            "msgev_p1_03_overlay": "D42EA1A00954F1EDDEDCD008D293247B932401D3C91DEB19C3A6782969ED1BB9",
            "msgev_p1_03_contract": "B61B12931F4E299E3DF56308BB602A8D7E70CB1A4068E6915CD7C5119DB46755",
            "msgev_p1_03_validation": "974B26E37645B680AED541C9FB81E3CAFB152A9216A82E5A882743BBEE229B79",
        }
        for key, expected in expected_p103.items():
            with self.subTest(key=key):
                self.assertEqual(builder.require_artifact(key)["sha256"], expected)

    def test_direct_helper_graph_is_pinned_and_exercised(self) -> None:
        expected_keys = {
            "lz4_wrapper",
            "message_table",
            "message_invariants",
            "msggame_format",
            "strdata_format",
            "p2_exact_reuse_catalog",
            "tail_exact_reuse_catalog",
            "font_overlay_demand_parser",
            "font_demand_refresh",
            "font_v6_parser",
            "font_file_only_recipe",
            "active_text_residual_audit",
        }
        self.assertEqual(set(builder.DIRECT_HELPER_PINS), expected_keys)
        observed = builder.require_direct_helpers()
        self.assertEqual(set(observed), expected_keys)
        for key, (_path, expected_sha256) in builder.DIRECT_HELPER_PINS.items():
            with self.subTest(key=key):
                self.assertEqual(observed[key]["sha256"], expected_sha256)

    def test_readme_supersede_is_one_existing_p0_coordinate(self) -> None:
        entry, contract, metadata = builder.load_readme_supersede()
        self.assertEqual((entry["block_id"], entry["slot_id"]), (2, 1950))
        self.assertTrue(entry["ko"].endswith(" "))
        self.assertEqual(len(entry["ko"]) - len(entry["ko"].rstrip()), 1)
        self.assertEqual(contract["supersedes"]["p0_translated_entry_count"], 1400)
        self.assertEqual(metadata["validation"]["checks"]["coordinate_2_1950_supersedes_existing_p0_entry"], True)

    def test_font_input_manifest_and_four_route_pins(self) -> None:
        _manifest, routes = builder.font_manifest()
        self.assertEqual(tuple(routes), builder.FONT_RESOURCES)
        for relative in builder.FONT_RESOURCES:
            with self.subTest(relative=relative):
                self.assertEqual(routes[relative]["candidate_sha256"], builder.FONT_CANDIDATE_PINS[relative]["sha256"])
                self.assertEqual(routes[relative]["candidate_size"], builder.FONT_CANDIDATE_PINS[relative]["size"])
        self.assertEqual(sum(len(route["targets"]) for route in routes.values()) * 3, 21)

    def test_manual_layout_is_required_and_final_validation_is_fail_closed(self) -> None:
        self.assertTrue(builder.MANUAL_LAYOUT_BUILDER_SHA256, "manual layout source pin must be frozen for v0.10")
        _module, _contract, entries, _packed, _raw, _table, metadata = builder.load_manual_layout(
            self._materialized_v09_root()
        )
        self.assertEqual(metadata["counts"]["applied_entry_count"], len(entries))
        self.assertEqual(metadata["counts"]["manual_review_hold_count"], 0)
        self.assertEqual(metadata["counts"]["runtime_preservation_count"], 3)

    def test_full_composition_matches_tracked_verification(self) -> None:
        expected = builder.load_tracked_verification()
        with tempfile.TemporaryDirectory(dir=builder.TMP) as directory:
            _manifest, actual = builder.build_staged(builder.DEFAULT_BASELINE_ZIP, Path(directory))
        self.assertEqual(actual, expected)

    def test_output_guard_rejects_workspace_and_tmp_root(self) -> None:
        for path in (builder.REPO, builder.REPO / "workstreams", builder.TMP):
            with self.subTest(path=path):
                with self.assertRaises(builder.CandidateV7Error):
                    builder.validate_destination(path)

    def test_staging_guard_rejects_workspace_and_non_tmp_paths(self) -> None:
        v6 = builder.load_v6_verification()
        for path in (builder.REPO, builder.REPO / "workstreams", ROOT):
            with self.subTest(path=path):
                with self.assertRaises(builder.CandidateV7Error):
                    builder.materialize_baseline(builder.DEFAULT_BASELINE_ZIP, path, v6)
                with self.assertRaises(builder.CandidateV7Error):
                    builder.build_staged(builder.DEFAULT_BASELINE_ZIP, path)

    def test_public_workstream_has_no_game_binary_or_cached_bytecode(self) -> None:
        forbidden = {".bin", ".g1n", ".ttf", ".otf", ".zip", ".pixels", ".pyc"}
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in forbidden
        ]
        self.assertEqual(offenders, [])
        self.assertFalse((ROOT / "__pycache__").exists())

    def _materialized_v09_root(self) -> Path:
        """Return a disposable exact-14 v0.9 tree for one frozen input loader."""

        temporary = tempfile.TemporaryDirectory(dir=builder.TMP)
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        v6 = builder.load_v6_verification()
        return builder.materialize_baseline(builder.DEFAULT_BASELINE_ZIP, root, v6)


if __name__ == "__main__":
    unittest.main()
