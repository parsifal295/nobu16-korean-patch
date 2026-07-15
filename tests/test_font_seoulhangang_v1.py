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

    def test_pinned_public_demand_has_switch_strict_imports(self) -> None:
        demand = BUILD.load_default_overlay_demand()
        self.assertEqual(33_256, demand["source_entry_count"])
        self.assertEqual(1_238, demand["codepoint_count"])
        self.assertEqual(1_101, demand["hangul_syllable_count"])
        self.assertEqual(
            "B0B920BF63E1E5B90D2446CF43F3BD5260B093CFF229F7D450A7AE1D30CE13CE",
            demand["codepoints_sha256"],
        )
        self.assertEqual(
            [4037, 7025, 16176, 6018],
            [source["entry_count"] for source in demand["sources"]],
        )
        self.assertTrue(all("switch_" in source["path"] for source in demand["sources"][1:]))

    def test_plan_is_deterministic_when_the_local_pristine_backup_exists(self) -> None:
        if not STOCK.is_file():
            self.skipTest("local pristine RES_SC backup is unavailable")
        stock = BUILD.require_stock_archive(STOCK)
        demand = BUILD.load_default_overlay_demand()
        plan_a = BUILD.build_plan(stock, demand)
        plan_b = BUILD.build_plan(stock, demand)
        self.assertEqual(BUILD.encode_json(plan_a), BUILD.encode_json(plan_b))
        self.assertEqual(1171, plan_a["raster_codepoint_count"])
        self.assertEqual(
            [(6, 0, 1106), (6, 1, 1171), (7, 0, 1106), (7, 1, 1171)],
            [(item["entry"], item["table"], item["count"]) for item in plan_a["append_contract"]],
        )
        manifest = self.read_json("manifest.v1.json")
        self.assertEqual(plan_a["raster_codepoints_sha256"], manifest["pinned_public_korean_demand"]["raster_codepoints_sha256"])

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
        self.assertTrue(verification["g1n_structural_validation"])
        self.assertFalse(verification["installed_game_files_modified"])

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
