#!/usr/bin/env python3
"""Public scaffold tests for the Steam PK 1.1.7 JP v0.8.0 v5 candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_steam_jp_117_candidate_v5.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_117_candidate_v5_tested", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJP117CandidateV5ScaffoldTests(unittest.TestCase):
    def test_runtime_release_name_and_exact_fourteen_jp_target_vector(self) -> None:
        self.assertEqual(
            builder.DEFAULT_ZIP_NAME,
            "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip",
        )
        self.assertEqual(builder.TARGETS, builder.EXPECTED_TARGETS)
        self.assertEqual(len(builder.TARGETS), 14)
        self.assertEqual(tuple(sorted(builder.TARGETS)), builder.TARGETS)
        self.assertTrue(
            all(
                path.startswith("MSG/JP/")
                or path.startswith("MSG_PK/JP/")
                or path.startswith("RES_JP")
                for path in builder.TARGETS
            )
        )
        self.assertFalse(
            any("/SC/" in path or path.startswith("RES_SC") for path in builder.TARGETS)
        )
        self.assertIn(builder.BASE_MSGGAME_RESOURCE, builder.TARGETS)
        self.assertIn(builder.BASE_EV_STRDATA_RESOURCE, builder.TARGETS)

    def test_v5_expands_the_immutable_v3_vector_by_only_two_base_resources(self) -> None:
        self.assertEqual(
            hashlib.sha256(builder.V3.VERIFICATION_PATH.read_bytes()).hexdigest().upper(),
            builder.V3_VERIFICATION_SHA256,
        )
        verification = builder.load_v3_verification()
        self.assertEqual(verification["candidate_paths"], list(builder.V3_TARGETS))
        self.assertEqual(
            set(builder.V3_UNCHANGED_TARGETS),
            set(builder.V3_TARGETS)
            - {
                builder.MSGUI_RESOURCE,
                builder.MSGDATA_RESOURCE,
                builder.MSGEV_RESOURCE,
            },
        )
        self.assertEqual(len(builder.V3_UNCHANGED_TARGETS), 9)
        self.assertEqual(len(builder.IMMUTABLE_V07_TARGETS), 6)
        self.assertEqual(
            set(builder.TARGETS) - set(builder.V3_TARGETS),
            set(builder.BASE_TRANSFER_RESOURCES),
        )
        self.assertNotEqual(builder.BASE_RUNTIME_STOCK_ROOT, builder.STOCK_ROOT)
        self.assertEqual(builder.BASE_RUNTIME_STOCK_ROOT, builder.V3.V2.STEAM_ROOT)

    def test_base_msggame_switch_v13_transfer_contract_is_explicit(self) -> None:
        self.assertEqual(
            builder.BASE_MSGGAME_TRANSFER_PATH,
            builder.REPO
            / "workstreams"
            / "tutorial_dialogue_trace_msggame_v1"
            / "build_base_msggame_switch_v13_overlay.py",
        )
        module = builder.load_base_msggame_transfer()
        self.assertEqual(module.RESOURCE, builder.BASE_MSGGAME_RESOURCE)
        self.assertTrue(callable(module.build_blob))
        self.assertTrue(callable(module.verify))
        self.assertIsInstance(module.DEFAULT_SWITCH_ZIP, Path)
        self.assertEqual(module.EXPECTED_ELIGIBLE_COUNT, 22_924)
        self.assertEqual(
            module.EXPECTED_CANDIDATE["packed_sha256"],
            "72A81DABBDD5BC596356CF4F457B2235E439B2D27BD2FB00546842606531CE44",
        )

    def test_base_ev_strdata_switch_v13_transfer_contract_is_explicit(self) -> None:
        self.assertEqual(
            builder.BASE_EV_STRDATA_TRANSFER_PATH,
            builder.REPO
            / "workstreams"
            / "base_ev_strdata_jp_switch_v13_transfer_v1"
            / "build_base_ev_strdata_jp_switch_v13_transfer_v1.py",
        )
        module = builder.load_base_ev_strdata_transfer()
        self.assertEqual(module.RESOURCE, builder.BASE_EV_STRDATA_RESOURCE)
        self.assertTrue(callable(module.build_blob))
        self.assertTrue(callable(module.verify))
        self.assertIsInstance(module.DEFAULT_SWITCH_ZIP, Path)
        self.assertEqual(module.EXPECTED_SELECTED_COUNT, 13_045)
        self.assertEqual(module.EXPECTED_RESIDUAL_COUNT, 45)
        self.assertEqual(module.EXPECTED_CANDIDATE["packed_size"], 927_573)
        self.assertEqual(
            module.EXPECTED_CANDIDATE["packed_sha256"],
            "AD1A442C3588E791DB442548C2B7878ABB4D53A686C591A94AB7F4FAB719A886",
        )

    def test_missing_base_transfer_cannot_fallback_to_an_unpinned_resource(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            absent = Path(directory) / "absent_base_transfer.py"
            with self.assertRaises(builder.CandidateV5Error):
                builder._load_base_transfer(
                    "v5_absent_base_transfer",
                    absent,
                    builder.BASE_EV_STRDATA_RESOURCE,
                )

    def test_tracked_v5_verification_is_exact_fourteen_and_not_reused_from_v4(self) -> None:
        self.assertEqual(builder.VERIFICATION_PATH.name, "verification.v5.json")
        self.assertFalse((ROOT / "verification.v4.json").exists())
        value = builder.load_tracked_verification()
        self.assertEqual(value["schema"], builder.VERIFICATION_SCHEMA)
        self.assertEqual(value["candidate_file_count"], 14)
        self.assertEqual(value["candidate_paths"], list(builder.TARGETS))
        self.assertEqual(
            value["candidates"][builder.BASE_MSGGAME_RESOURCE],
            {
                "sha256": "72A81DABBDD5BC596356CF4F457B2235E439B2D27BD2FB00546842606531CE44",
                "size": 647418,
            },
        )
        self.assertEqual(
            value["candidates"][builder.BASE_EV_STRDATA_RESOURCE],
            {
                "sha256": "AD1A442C3588E791DB442548C2B7878ABB4D53A686C591A94AB7F4FAB719A886",
                "size": 927573,
            },
        )
        self.assertEqual(
            value["translation"]["base_msggame_switch_v13_transferred_entries"],
            22_924,
        )
        self.assertEqual(
            value["translation"]["base_ev_strdata_switch_v13_transferred_entries"],
            13_045,
        )
        self.assertEqual(
            value["predecessors"][builder.BASE_MSGGAME_RESOURCE]["sha256"],
            "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        )
        self.assertEqual(
            value["predecessors"][builder.BASE_EV_STRDATA_RESOURCE]["sha256"],
            "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
        )
        self.assertTrue(value["checks"]["base_msggame_switch_v13_transfer_integrated"])
        self.assertTrue(value["checks"]["base_ev_strdata_switch_v13_transfer_integrated"])
        self.assertTrue(value["checks"]["exact_fourteen_files"])
        self.assertFalse(value["checks"]["sc_container_used"])
        self.assertFalse(value["checks"]["steam_files_written"])

    def test_v5_zip_writer_requires_and_preserves_all_fourteen_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate"
            for index, relative in enumerate(builder.TARGETS):
                path = candidate / Path(relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"v5-{index}-{relative}".encode("utf-8"))
            destination = root / builder.DEFAULT_ZIP_NAME
            first = builder.make_zip(candidate, destination)
            first_blob = destination.read_bytes()
            destination.unlink()
            second = builder.make_zip(candidate, destination)
            self.assertEqual(first, second)
            self.assertEqual(first_blob, destination.read_bytes())

    def test_output_guards_reject_live_or_repository_destinations(self) -> None:
        for path in (builder.REPO, builder.REPO / "workstreams", builder.V3.V2.STEAM_ROOT):
            with self.subTest(path=path):
                with self.assertRaises(builder.CandidateV5Error):
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
