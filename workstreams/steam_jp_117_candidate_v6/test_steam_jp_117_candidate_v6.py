#!/usr/bin/env python3
"""Regression tests for the Steam JP v0.9.0 exact-14 candidate wrapper."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_steam_jp_117_candidate_v6.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_117_candidate_v6_tested", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJP117CandidateV6Tests(unittest.TestCase):
    def test_runtime_release_name_and_exact_fourteen_jp_target_vector(self) -> None:
        self.assertEqual(
            builder.DEFAULT_ZIP_NAME,
            "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip",
        )
        self.assertEqual(builder.TARGETS, builder.EXPECTED_TARGETS)
        self.assertEqual(builder.REPLACED_RESOURCES, (
            "MSG/JP/ev_strdata.bin", "MSG/JP/msggame.bin"
        ))
        self.assertEqual(len(builder.TARGETS), 14)
        self.assertTrue(all("/JP/" in path or path.startswith("RES_JP") for path in builder.TARGETS))
        self.assertFalse(any("/SC/" in path or path.startswith("RES_SC") for path in builder.TARGETS))

    def test_v08_baseline_and_stock_root_are_pinned(self) -> None:
        verification = builder.load_v5_verification()
        self.assertEqual(verification["candidate_file_count"], 14)
        self.assertEqual(verification["zip"], {
            "member_count": 14,
            **builder.BASELINE_RELEASE_PIN,
        })
        self.assertNotEqual(builder.DEFAULT_STOCK_ROOT, builder.DEFAULT_LIVE_GAME_ROOT)
        self.assertTrue((builder.DEFAULT_STOCK_ROOT / "MSG/JP/msggame.bin").is_file())
        self.assertTrue((builder.DEFAULT_STOCK_ROOT / "MSG/JP/ev_strdata.bin").is_file())

    def test_wave11_interfaces_are_explicit_and_pinned(self) -> None:
        msggame = builder.load_wave_module(
            "v6_msggame_test", builder.MSGGAME_WAVE11_PATH, builder.BASE_MSGGAME_RESOURCE
        )
        ev_strdata = builder.load_wave_module(
            "v6_ev_test", builder.EV_STRDATA_WAVE11_PATH, builder.BASE_EV_STRDATA_RESOURCE
        )
        self.assertEqual(msggame.EXPECTED_CANDIDATE["packed_sha256"], "E54D7AB55CB981B7973FBF8657A276520EBFA881D3439BE94A2D14086B293177")
        self.assertEqual(ev_strdata.EXPECTED_CANDIDATE["packed_sha256"], "9ED892E85AF18EB3BC965A834853969BC06F486A2466A83F3CEBED1B8D5433C0")
        self.assertTrue(msggame.DEFAULT_SWITCH_ZIP.is_file())
        self.assertTrue(ev_strdata.DEFAULT_SWITCH_ZIP.is_file())
        self.assertEqual(
            builder.WAVE11_BUILDER_SHA256[builder.BASE_MSGGAME_RESOURCE],
            builder.sha256(builder.MSGGAME_WAVE11_PATH.read_bytes()),
        )
        self.assertEqual(
            builder.WAVE11_BUILDER_SHA256[builder.BASE_EV_STRDATA_RESOURCE],
            builder.sha256(builder.EV_STRDATA_WAVE11_PATH.read_bytes()),
        )

    def test_full_composition_matches_tracked_verification(self) -> None:
        expected = builder.load_tracked_verification()
        with tempfile.TemporaryDirectory() as directory:
            _manifest, actual = builder.build_staged(
                builder.DEFAULT_BASELINE_ZIP,
                builder.DEFAULT_STOCK_ROOT,
                Path(directory),
                None,
            )
        self.assertEqual(actual, expected)

    def test_live_guard_covers_all_targets_and_both_executables(self) -> None:
        self.assertEqual(builder.LIVE_GUARD_PATHS[:-2], builder.TARGETS)
        self.assertEqual(builder.LIVE_GUARD_PATHS[-2:], ("NOBU16.exe", "NOBU16PK.exe"))

    def test_candidate_vector_rejects_non_exact_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(builder.CandidateV6Error):
                builder.candidate_paths(root)

    def test_output_guards_reject_repository_and_live_game_roots(self) -> None:
        for path in (builder.REPO, builder.REPO / "workstreams", builder.DEFAULT_STOCK_ROOT):
            with self.subTest(path=path):
                with self.assertRaises(builder.CandidateV6Error):
                    builder.validate_destination(path)

    def test_public_workstream_contains_no_game_binary_or_cached_bytecode(self) -> None:
        forbidden = {".bin", ".g1n", ".ttf", ".otf", ".zip", ".pixels", ".pyc"}
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in forbidden
        ]
        self.assertEqual(offenders, [])
        self.assertFalse((ROOT / "__pycache__").exists())


if __name__ == "__main__":
    unittest.main()
