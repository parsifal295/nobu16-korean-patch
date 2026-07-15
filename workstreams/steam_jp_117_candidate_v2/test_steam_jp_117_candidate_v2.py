from __future__ import annotations

import importlib.util
import json
import sys
import unittest
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
    def test_runtime_and_exact_target_vector(self) -> None:
        self.assertEqual(builder.BASE.STEAM_PK_VERSION, "1.1.7")
        self.assertEqual(builder.BASE.STEAM_BUILD_ID, 18_823_764)
        self.assertEqual(len(builder.BASE.TARGETS), 10)
        self.assertEqual(builder.BASE.TARGETS, builder.BASE.EXPECTED_TARGETS)
        self.assertTrue(
            all("/SC/" not in path and not path.startswith("RES_SC") for path in builder.BASE.TARGETS)
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
            set(builder.BASE.RUNTIME.FONT_RESOURCES),
        )
        self.assertEqual(evidence["official_font_pin"]["SeoulHangangEB.ttf"]["assignment"], "every 48-cell table")
        self.assertEqual(evidence["official_font_pin"]["SeoulHangangB.ttf"]["assignment"], "every 32-cell table")

    def test_tracked_verification_is_exact_and_jp_only(self) -> None:
        value = json.loads(builder.VERIFICATION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(value["schema"], builder.VERIFICATION_SCHEMA)
        self.assertEqual(value["runtime"]["pk_version"], "1.1.7")
        self.assertEqual(value["runtime"]["steam_build_id"], 18_823_764)
        self.assertEqual(value["runtime"]["language_route"], "JP")
        self.assertEqual(value["candidate_file_count"], 10)
        self.assertEqual(value["candidate_paths"], list(builder.BASE.TARGETS))
        self.assertEqual(set(value["candidates"]), set(builder.BASE.TARGETS))
        self.assertEqual(value["translation"]["msgui_mapped"], 4_036)
        self.assertEqual(value["translation"]["msgui_unmapped"], 1)
        self.assertEqual(value["translation"]["msggame_applied"], 28_272)
        self.assertEqual(value["translation"]["msggame_remaining_jp_semantic"], 0)
        self.assertEqual(
            value["candidates"]["MSG_PK/JP/msggame.bin"]["sha256"],
            "6316E2B288F798B747D983DB08E6C2A477C6FC60DE319D3C7C302102C6384A84",
        )
        self.assertEqual(value["zip"]["name"], builder.DEFAULT_ZIP_NAME)
        self.assertEqual(
            value["zip"]["sha256"],
            "38752EAC593A8E64E2AD0BA93818F417ACF982E96F97B65879EEDA47198B45F2",
        )
        self.assertEqual(value["zip"]["size"], 238_208_364)
        self.assertEqual(value["zip"]["member_count"], 10)
        self.assertFalse(value["checks"]["sc_container_used"])

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
