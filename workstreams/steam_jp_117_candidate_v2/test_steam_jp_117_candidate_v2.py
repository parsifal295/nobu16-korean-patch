from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "nobu16_test_steam_jp_117_candidate_v2",
    ROOT / "build_steam_jp_117_candidate_v2.py",
)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJP117CandidateV2Tests(unittest.TestCase):
    def test_port_stock_root_is_explicit_and_has_no_live_default(self) -> None:
        parser = builder.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["build"])
        parsed = parser.parse_args(
            ["build", "--port-stock-root", "private-pristine-port-stock"]
        )
        self.assertEqual(parsed.port_stock_root, Path("private-pristine-port-stock"))

    def test_runtime_and_exact_target_vector(self) -> None:
        self.assertEqual(builder.BASE.STEAM_PK_VERSION, "1.1.7")
        self.assertEqual(builder.BASE.STEAM_BUILD_ID, 18_823_764)
        # Importing v1 must preserve its reviewed ten-file behavior.
        self.assertEqual(len(builder.BASE.TARGETS), 10)
        self.assertEqual(builder.BASE.TARGETS, builder.BASE.EXPECTED_TARGETS)
        self.assertEqual(len(builder.TARGETS), 12)
        self.assertEqual(builder.TARGETS, builder.EXPECTED_TARGETS)
        self.assertEqual(
            set(builder.TARGETS) - set(builder.BASE.TARGETS),
            {
                "RES_JP_PK_PORT/res_lang_pk_port1.bin",
                "RES_JP_PK_PORT/res_lang_pk_port2.bin",
            },
        )
        self.assertTrue(
            all(
                "/SC/" not in path and not path.startswith("RES_SC")
                for path in builder.TARGETS
            )
        )

    def test_msgui_supplement_is_pinned_and_disjoint(self) -> None:
        supplement = builder.load_msgui_supplement()
        _contract, foundation, _blob = builder.BASE.MSGUI.load_frozen_inputs(
            builder.BASE.MSGUI.DEFAULT_CONTRACT
        )
        foundation_ids = {int(entry["id"]) for entry in foundation}
        supplement_ids = {int(entry["id"]) for entry in supplement}
        self.assertEqual(len(supplement_ids), builder.SUPPLEMENT_COUNT)
        self.assertFalse(foundation_ids & supplement_ids)
        self.assertEqual(
            len(foundation_ids | supplement_ids), builder.MSGUI_MAPPED
        )

    def test_stock_msgui_and_complete_msggame_when_private_stock_exists(self) -> None:
        if not builder.STOCK_ROOT.is_dir():
            self.skipTest("Steam 1.1.7 transaction stock backup is unavailable")
        _msgui, msgui = builder.build_msgui(builder.STOCK_ROOT)
        self.assertEqual(msgui["mapped_entries"], 4_036)
        self.assertEqual(msgui["effective_changes"], 3_955)
        self.assertEqual(msgui["unmapped_entries"], 1)
        _msggame, msggame = builder.build_msggame(builder.STOCK_ROOT)
        self.assertEqual(msggame["applied_entries"], 28_272)
        self.assertEqual(msggame["remaining_jp_semantic"], 0)
        self.assertEqual(msggame["wave07_entries"], 4_061)

    def test_font_routes_are_derived_from_the_reviewed_jp_evidence(self) -> None:
        evidence = json.loads(builder.FONT_EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(
            builder.sha256(builder.FONT_EVIDENCE.read_bytes()),
            builder.FONT_EVIDENCE_SHA256,
        )
        routes = evidence["expected_private_outputs"]["routes"]
        self.assertEqual(
            {row["logical_path"] for row in routes},
            set(builder.FONT_RESOURCES),
        )
        self.assertEqual(len(routes), 4)
        configured = builder.configure_font_candidates(builder.DEFAULT_FONT_ROOT)
        self.assertEqual(set(configured["routes"]), set(builder.FONT_RESOURCES))

    def test_local_zip_writer_requires_and_preserves_all_twelve_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate"
            for index, relative in enumerate(builder.TARGETS):
                path = candidate / Path(relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"payload-{index}".encode("ascii"))
            destination = root / "candidate.zip"
            spec = builder.make_zip(candidate, destination)
            self.assertEqual(spec, builder.BASE.file_spec(destination))
            with zipfile.ZipFile(destination) as archive:
                self.assertEqual(archive.namelist(), list(builder.TARGETS))
                self.assertEqual(
                    archive.read("RES_JP_PK_PORT/res_lang_pk_port2.bin"),
                    b"payload-11",
                )
            (candidate / "RES_JP_PK_PORT/res_lang_pk_port2.bin").unlink()
            with self.assertRaises(builder.CandidateV2Error):
                builder.make_zip(candidate, root / "missing-port.zip")

    def test_tracked_verification_is_exact_and_jp_only(self) -> None:
        value = json.loads(builder.VERIFICATION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(value["schema"], builder.VERIFICATION_SCHEMA)
        self.assertEqual(value["runtime"]["pk_version"], "1.1.7")
        self.assertEqual(value["runtime"]["steam_build_id"], 18_823_764)
        self.assertEqual(value["runtime"]["language_route"], "JP")
        self.assertEqual(value["candidate_file_count"], 12)
        self.assertEqual(value["candidate_paths"], list(builder.TARGETS))
        self.assertEqual(set(value["candidates"]), set(builder.TARGETS))
        self.assertEqual(value["translation"]["msgui_mapped"], 4_036)
        self.assertEqual(value["translation"]["msgui_unmapped"], 1)
        self.assertEqual(value["translation"]["msggame_applied"], 28_272)
        self.assertEqual(value["translation"]["msggame_remaining_jp_semantic"], 0)
        self.assertEqual(
            value["candidates"]["MSG_PK/JP/msggame.bin"]["sha256"],
            "6316E2B288F798B747D983DB08E6C2A477C6FC60DE319D3C7C302102C6384A84",
        )
        self.assertEqual(value["zip"]["name"], builder.DEFAULT_ZIP_NAME)
        self.assertEqual(len(value["zip"]["sha256"]), 64)
        self.assertTrue(
            all(char in "0123456789ABCDEF" for char in value["zip"]["sha256"])
        )
        self.assertGreater(value["zip"]["size"], 0)
        self.assertEqual(value["zip"]["member_count"], 12)
        self.assertTrue(value["checks"]["exact_twelve_files"])
        self.assertFalse(value["checks"]["sc_container_used"])

    def test_runtime_qa_evidence_matches_the_tested_exact_twelve_scope(self) -> None:
        qa = json.loads((ROOT / "runtime_qa.v2.json").read_text(encoding="utf-8"))
        self.assertEqual(qa["schema"], "nobu16.kr.steam-jp-1.1.7-runtime-qa.v2")
        self.assertEqual(qa["runtime"]["pk_version"], "1.1.7")
        self.assertEqual(qa["runtime"]["steam_build_id"], 18_823_764)
        self.assertEqual(qa["runtime"]["language_route"], "JP")
        self.assertEqual(qa["runtime"]["executable"], "NOBU16PK.exe")
        self.assertEqual(qa["runtime"]["launcher_language_observed"], "日本語")
        self.assertEqual(qa["artifacts"]["zip"]["file_count"], 12)
        self.assertEqual(
            qa["artifacts"]["zip"]["sha256"],
            "F245F23882BD9C676B705DCA9DA5E1443BEE05EA88A12F7BA9E7692BEA100584",
        )
        install = qa["installation_verification"]
        self.assertTrue(install["installed_candidates"]["valid"])
        self.assertEqual(install["installed_candidates"]["exact_file_count"], 12)
        predecessors = install["pre_v0_7_predecessor_backups"]
        self.assertTrue(predecessors["valid"])
        self.assertEqual(predecessors["valid_file_count"], 12)
        issue = qa["issue_41"]
        self.assertEqual(issue["result"], "PASS")
        self.assertFalse(issue["hangul_question_mark_substitution_detected"])
        self.assertTrue(issue["resolution_dependent_symptom_absent_in_tested_qhd_configs"])
        same_session = qa["visual_evidence"]["same_session_mode_validation"]
        self.assertTrue(same_session["same_game_process"])
        self.assertEqual(same_session["windowed_qhd"]["result"], "PASS")
        self.assertEqual(same_session["borderless_qhd"]["result"], "PASS")
        cold = qa["visual_evidence"]["cold_restart_validation"]
        self.assertEqual(cold["mode"], "borderless_qhd")
        self.assertEqual(cold["validated_screens"], ["title", "menu"])
        self.assertEqual(cold["result"], "PASS")
        self.assertFalse(qa["visual_evidence"]["contains_screenshot_payload"])
        captures = [
            same_session["windowed_qhd"]["settings_capture_sha256"],
            same_session["borderless_qhd"]["settings_capture_sha256"],
            cold["cold_title_capture_sha256"],
            cold["cold_menu_capture_sha256"],
        ]
        self.assertTrue(
            all(
                len(value) == 64
                and all(character in "0123456789ABCDEF" for character in value)
                for value in captures
            )
        )
        safety = qa["safety"]
        self.assertTrue(safety["file_only"])
        self.assertTrue(
            all(
                safety[key] is False
                for key in (
                    "process_memory_access",
                    "dll_injection",
                    "hooking",
                    "executable_modified",
                    "registry_modified",
                )
            )
        )

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
