#!/usr/bin/env python3
"""Regression checks for the source-free SeoulHangang PC PK font pipeline."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PATCH_ROOT = Path(__file__).resolve().parents[1]
GAME_ROOT = PATCH_ROOT.parent
WORKSTREAM = PATCH_ROOT / "workstreams" / "font_seoulhangang_v1"
STOCK = GAME_ROOT / "KR_PATCH_BACKUP" / "officer_names_v0_1" / "stock" / "font.stock.bak"
LOCAL_OFFICIAL_FONT = PATCH_ROOT / "tmp" / "third_party_fonts" / "SeoulHangangM.ttf"


def load_builder():
    path = WORKSTREAM / "build_seoulhangang_v1.py"
    spec = importlib.util.spec_from_file_location("test_font_seoulhangang_v1_builder", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILD = load_builder()


class SeoulHangangV1Tests(unittest.TestCase):
    def read_json(self, name: str) -> dict:
        return json.loads((WORKSTREAM / name).read_text(encoding="utf-8"))

    def test_pinned_public_demand_covers_all_pk_progress_resources(self) -> None:
        demand = BUILD.load_default_overlay_demand()
        self.assertEqual(93, demand["source_count"])
        self.assertEqual(75_491, demand["source_entry_count"])
        self.assertEqual(1_389, demand["codepoint_count"])
        self.assertEqual(1_232, demand["hangul_syllable_count"])
        self.assertEqual(
            "7FDC3F9C72D5FF3416EAA905B581549434BC3A5577C3587CC5351E4C4676CC16",
            demand["codepoints_sha256"],
        )
        self.assertEqual(
            [
                ("MSG_PK/SC/msgui.bin", 1, 4037),
                ("MSG_PK/SC/msgev.bin", 35, 13178),
                ("MSG_PK/SC/msgdata.bin", 10, 21152),
                ("MSG_PK/SC/msgbre.bin", 14, 2217),
                ("MSG_PK/SC/msgire.bin", 1, 122),
                ("MSG_PK/SC/msgstf.bin", 1, 8),
                ("MSG_PK/SC/msggame.bin", 29, 10352),
                ("MSG/SC/strdata.bin", 2, 24425),
            ],
            [
                (item["resource"], item["source_count"], item["entry_count"])
                for item in demand["resource_catalog"]
            ],
        )
        self.assertEqual(
            "902C83FF51AB28593C1129A3DD364603D7CB5DB79A0AC548DC0CD64D969D7B38",
            demand["source_catalog_sha256"],
        )
        self.assertEqual(93, len(demand["sources"]))
        sources = {item["path"]: item for item in demand["sources"]}
        self.assertEqual(
            "2A2EE0488CCF6BB70DBBDA2B00A005821DB4CD5C5C8300E4A30F9DF52890295C",
            sources["workstreams/switch_msgev_v11_cjk_cleanup/public/msgev_ko_switch_v11_cjk_kana_cleanup_20.v1.json"]["sha256"],
        )
        self.assertEqual(
            "BFEFB590F10B073E9510F598BDFDCC840DDEDC165B637F9F0FEA0CB6B2675FC1",
            sources["workstreams/switch_msgbre_v11/public/msgbre_ko_switch_v11_strict_transfer.v0.1.json"]["sha256"],
        )
        self.assertEqual(
            "2C4B1F7C52D5B04EE915693C20D4662011E18A3B6535212905609B3ABBA9FE98",
            sources["workstreams/switch_strdata_v13_direct_transfer/public/strdata_ko_switch_v13_direct_transfer_24424.v1.json"]["sha256"],
        )

    def test_plan_is_deterministic_when_the_local_pristine_backup_exists(self) -> None:
        if not STOCK.is_file():
            self.skipTest("local pristine RES_SC backup is unavailable")
        stock = BUILD.require_stock_archive(STOCK)
        demand = BUILD.load_default_overlay_demand()
        plan_a = BUILD.build_plan(stock, demand)
        plan_b = BUILD.build_plan(stock, demand)
        self.assertEqual(BUILD.encode_json(plan_a), BUILD.encode_json(plan_b))
        self.assertEqual(1306, plan_a["raster_codepoint_count"])
        self.assertEqual(
            [(6, 0, 1237), (6, 1, 1306), (7, 0, 1237), (7, 1, 1306)],
            [(item["entry"], item["table"], item["count"]) for item in plan_a["append_contract"]],
        )
        manifest = self.read_json("manifest.v1.json")
        pinned = manifest["pinned_public_korean_demand"]
        self.assertEqual(plan_a["raster_codepoints_sha256"], pinned["raster_codepoints_sha256"])
        self.assertEqual(plan_a["demand"]["source_catalog_sha256"], pinned["source_catalog_sha256"])
        self.assertEqual(plan_a["demand"]["resource_catalog"], pinned["resource_catalog"])
        for key in (
            "source_count",
            "source_entry_count",
            "codepoint_count",
            "codepoints_sha256",
            "hangul_syllable_count",
            "hangul_syllables_sha256",
            "non_hangul_count",
            "non_hangul_sha256",
        ):
            self.assertEqual(plan_a["demand"][key], pinned[key])
        self.assertEqual(plan_a["raster_codepoint_count"], pinned["raster_codepoint_count"])
        self.assertEqual(plan_a["append_contract"], pinned["append_contract"])
        self.assertEqual(demand["codepoints"], plan_a["glyph_demand_codepoints"])
        self.assertEqual(demand["codepoints_sha256"], plan_a["glyph_demand_codepoints_sha256"])

    def test_switch_evidence_proves_no_raw_copy_route(self) -> None:
        evidence = self.read_json("evidence/switch_pc_g1n_compatibility.v1.json")
        self.assertFalse(evidence["raw_copy_compatible"])
        self.assertTrue(evidence["inspection"]["read_only"])
        self.assertFalse(evidence["inspection"]["switch_resource_exported"])
        self.assertEqual([3, 3], [entry["table_count"] for entry in evidence["switch"]["font_entries"]])
        self.assertEqual([2, 2], [entry["table_count"] for entry in evidence["pc"]["font_entries"]])
        self.assertIn("entry_6_table_count", evidence["raw_copy_reasons"])

    def test_manifest_keeps_font_and_rasters_out_of_public_payload(self) -> None:
        manifest = self.read_json("manifest.v1.json")
        policy = manifest["public_payload_policy"]
        self.assertTrue(all(value is False for value in policy.values()))
        self.assertEqual(BUILD.SEOUL_HANGANG_M_SHA256, manifest["font_source"]["file_sha256"])
        self.assertIn("공공누리 제1유형", manifest["font_source"]["license"])
        verification = self.read_json("verification.v1.json")
        self.assertTrue(verification["candidate_byte_identical"])
        self.assertTrue(verification["full_pk_glyph_demand_coverage"])
        self.assertTrue(verification["g1n_structural_validation"])
        self.assertFalse(verification["installed_game_files_modified"])
        coverage = verification["candidate"]["glyph_demand_coverage"]
        self.assertEqual(1389, coverage["codepoint_count"])
        self.assertEqual(
            [(6, 0), (6, 1), (7, 0), (7, 1)],
            [(table["entry"], table["table"]) for table in coverage["tables"]],
        )
        self.assertEqual(
            [1389, 1389, 1389, 1389],
            [table["mapped_demand_count"] for table in coverage["tables"]],
        )
        self.assertEqual(
            [0, 0, 0, 0],
            [table["missing_demand_count"] for table in coverage["tables"]],
        )

    def test_renderer_excludes_game_controls_and_rejects_cjk_or_bad_esc(self) -> None:
        self.assertEqual({ord("가")}, BUILD.renderable_characters("가\x1bC1\ue008", "fixture"))
        with self.assertRaises(BUILD.FontBuildError):
            BUILD.renderable_characters("가\x1bX", "fixture")
        with self.assertRaises(BUILD.FontBuildError):
            BUILD.renderable_characters("가日", "fixture")

    def test_output_root_cannot_be_a_live_game_tree_or_source_parent(self) -> None:
        with self.assertRaises(BUILD.FontBuildError):
            BUILD.validate_output_root(PATCH_ROOT / "not-a-private-output", ())
        with self.assertRaises(BUILD.FontBuildError):
            BUILD.validate_output_root(STOCK.parent, (STOCK,))

    @unittest.skipUnless(LOCAL_OFFICIAL_FONT.is_file(), "official SeoulHangang M is not present in ignored local input")
    def test_optional_local_raster_smoke_is_byte_deterministic(self) -> None:
        BUILD.require_official_font(LOCAL_OFFICIAL_FONT)
        powershell = Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
        if not powershell.is_file():
            self.skipTest("Windows PowerShell is unavailable")
        with tempfile.TemporaryDirectory(prefix="nobu16-seoulhangang-test-") as temp:
            root = Path(temp)
            request = BUILD.raster_request(LOCAL_OFFICIAL_FONT, [0x3161, 0xAC00, 0xFF65])
            request_path = root / "request.json"
            request_path.write_text(json.dumps(request, ensure_ascii=True), encoding="utf-8")
            outputs = []
            for name in ("a", "b"):
                output = root / name
                result = subprocess.run(
                    [
                        str(powershell), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                        "-File", str(WORKSTREAM / "rasterize_seoulhangang_v1.ps1"),
                        "-RequestPathInput", str(request_path), "-OutputDirectory", str(output),
                    ],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                )
                self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)
                outputs.append(output)
            for name in ("glyph_pixels_entry_6.pixels", "glyph_pixels_entry_7.pixels", "raster_result.json"):
                left = (outputs[0] / name).read_bytes()
                right = (outputs[1] / name).read_bytes()
                self.assertEqual(left, right)
                self.assertEqual(64, len(hashlib.sha256(left).hexdigest()))


if __name__ == "__main__":
    unittest.main()
