#!/usr/bin/env python3
"""Regression tests for the source-free SeoulHangang demand-pin refresher."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


PATCH_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = (
    PATCH_ROOT
    / "workstreams"
    / "font_seoulhangang_v1"
    / "refresh_demand_pin.py"
)


def load_tool() -> Any:
    spec = importlib.util.spec_from_file_location(
        "test_refresh_font_demand_pin_tool", TOOL_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TOOL = load_tool()


class DemandPinRefreshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="nobu16-font-pin-test-")
        self.addCleanup(self.temporary.cleanup)
        self.game_root = Path(self.temporary.name)
        self.project_root = self.game_root / "KR_PATCH_WORK"
        self.project_root.mkdir()
        self.stock = (
            self.game_root
            / "KR_PATCH_BACKUP"
            / "officer_names_v0_1"
            / "stock"
            / "font.stock.bak"
        )
        self.stock.parent.mkdir(parents=True)
        self.stock.write_bytes(b"synthetic-pristine-stock")
        self.stock_sha256 = hashlib.sha256(self.stock.read_bytes()).hexdigest().upper()
        self.progress_path = (
            self.project_root / "data" / "public" / "translation_progress.v0.1.json"
        )
        self.progress_path.parent.mkdir(parents=True)
        self.overlay_paths: dict[str, Path] = {}
        resources = []
        for index, resource in enumerate(TOOL.EXPECTED_PK_RESOURCES):
            relative = Path("fixtures") / f"overlay_{index}.json"
            path = self.project_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            self._write_overlay(path, resource, "\uac00A")
            self.overlay_paths[resource] = path
            resources.append(
                {
                    "path": resource,
                    "kind": "strings",
                    "overlay_globs": [relative.as_posix()],
                }
            )
        shared_resource = TOOL.EXPECTED_SHARED_RESOURCES[0]
        shared_relative = Path("fixtures") / "shared_overlay.json"
        shared_path = self.project_root / shared_relative
        self._write_overlay(shared_path, shared_resource, "\uac00A")
        self.overlay_paths[shared_resource] = shared_path
        resources.append(
            {
                "path": "RES_SC/res_lang.bin",
                "kind": "stages",
                "done": 0,
                "total": 1,
            }
        )
        self._write_json(
            self.progress_path,
            {
                "schema": "nobu16.kr.translation-progress.v0.1",
                "resources": resources,
                "shared_strings": [
                    {
                        "path": shared_resource,
                        "kind": "strings",
                        "overlay_globs": [shared_relative.as_posix()],
                    }
                ],
            },
        )
        self.manifest_path = (
            self.project_root
            / "workstreams"
            / "font_seoulhangang_v1"
            / "manifest.v1.json"
        )
        self.manifest_path.parent.mkdir(parents=True)

    @staticmethod
    def _write_json(path: Path, value: Any) -> None:
        path.write_text(
            json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
        )

    def _write_overlay(self, path: Path, resource: str, ko: str) -> None:
        self._write_json(
            path,
            {
                "schema": "nobu16.kr.common-message-overlay.v1",
                "resource": resource,
                "distribution_policy": {
                    "contains_commercial_source_text": False,
                    "contains_complete_game_resource": False,
                },
                "entry_count": 1,
                "entries": [{"id": 0, "ko": ko}],
            },
        )

    @staticmethod
    def _preflight(
        _stock_blob: bytes, hangul: list[int], non_hangul: list[int]
    ) -> tuple[None, dict[str, Any], dict[int, dict[int, list[int]]]]:
        all_points = sorted(set(hangul) | set(non_hangul))
        hangul_points = sorted(hangul)
        return (
            None,
            {},
            {
                6: {0: hangul_points, 1: all_points},
                7: {0: hangul_points, 1: all_points},
            },
        )

    def _compute(self) -> dict[str, Any]:
        return TOOL.compute_pin(
            self.project_root,
            expected_stock_sha256=self.stock_sha256,
            preflight_stock=self._preflight,
        )

    def _check_or_write(self, write: bool) -> dict[str, Any]:
        return TOOL.check_or_write(
            project_root=self.project_root,
            manifest_path=self.manifest_path,
            write=write,
            expected_stock_sha256=self.stock_sha256,
            preflight_stock=self._preflight,
        )

    def test_computation_is_deterministic_and_contains_only_source_free_metrics(self) -> None:
        first = self._compute()
        second = self._compute()
        self.assertEqual(first, second)
        self.assertEqual(8, first["source_count"])
        self.assertEqual(8, first["source_entry_count"])
        self.assertEqual(2, first["codepoint_count"])
        self.assertEqual(1, first["hangul_syllable_count"])
        self.assertEqual(1, first["non_hangul_count"])
        self.assertEqual(2, first["raster_codepoint_count"])
        self.assertEqual(
            list(TOOL.EXPECTED_FONT_RESOURCES),
            [row["resource"] for row in first["resource_catalog"]],
        )
        self.assertEqual(
            [(6, 0, 1), (6, 1, 2), (7, 0, 1), (7, 1, 2)],
            [
                (row["entry"], row["table"], row["count"])
                for row in first["append_contract"]
            ],
        )
        self.assertFalse(any(key.startswith("_") for key in first))
        serialized = json.dumps(first, ensure_ascii=False)
        self.assertNotIn("ko", serialized)
        self.assertNotIn("\uac00", serialized)

    def test_default_check_is_read_only_and_write_changes_only_the_pin(self) -> None:
        original_pin = self._compute()
        unrelated = {
            "schema": TOOL.MANIFEST_SCHEMA,
            "status": "sentinel-status",
            "pinned_public_korean_demand": original_pin,
            "runtime_validation": {"performed": False, "note": "preserve me"},
        }
        self._write_json(self.manifest_path, unrelated)

        changed_overlay = self.overlay_paths["MSG_PK/SC/msggame.bin"]
        self._write_overlay(changed_overlay, "MSG_PK/SC/msggame.bin", "\uac00\ub098A")
        before_check = self.manifest_path.read_bytes()
        checked = self._check_or_write(write=False)
        self.assertEqual("stale", checked["status"])
        self.assertEqual(before_check, self.manifest_path.read_bytes())

        written = self._check_or_write(write=True)
        self.assertEqual("updated", written["status"])
        after = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual("sentinel-status", after["status"])
        self.assertEqual(
            {"performed": False, "note": "preserve me"}, after["runtime_validation"]
        )
        self.assertEqual(self._compute(), after["pinned_public_korean_demand"])
        self.assertEqual("current", self._check_or_write(write=False)["status"])

    def test_rejects_non_source_free_policy_and_forbidden_script(self) -> None:
        target = self.overlay_paths["MSG_PK/SC/msgev.bin"]
        value = json.loads(target.read_text(encoding="utf-8"))
        value["distribution_policy"]["contains_commercial_source_text"] = True
        self._write_json(target, value)
        with self.assertRaises(TOOL.BASE.FontBuildError):
            TOOL.collect_overlay_demand(self.project_root)

        self._write_overlay(target, "MSG_PK/SC/msgev.bin", "\u5bb6")
        with self.assertRaises(TOOL.BASE.FontBuildError):
            TOOL.collect_overlay_demand(self.project_root)

    def test_rejects_scope_changes_and_duplicate_overlay_registration(self) -> None:
        original = json.loads(self.progress_path.read_text(encoding="utf-8"))
        progress = json.loads(json.dumps(original))
        progress["resources"] = progress["resources"][1:]
        self._write_json(self.progress_path, progress)
        with self.assertRaisesRegex(TOOL.DemandPinError, "seven PK string resources"):
            TOOL.collect_overlay_demand(self.project_root)

        progress = json.loads(json.dumps(original))
        first_path = progress["resources"][0]["overlay_globs"][0]
        progress["resources"][1]["overlay_globs"] = [first_path]
        self._write_json(self.progress_path, progress)
        with self.assertRaisesRegex(TOOL.DemandPinError, "listed more than once"):
            TOOL.collect_overlay_demand(self.project_root)

    def test_rejects_any_other_base_game_message_resource(self) -> None:
        progress = json.loads(self.progress_path.read_text(encoding="utf-8"))
        progress["shared_strings"][0]["path"] = "MSG/SC/ev_strdata.bin"
        self._write_json(self.progress_path, progress)
        with self.assertRaisesRegex(
            TOOL.DemandPinError, "only MSG/SC/strdata.bin"
        ):
            TOOL.collect_overlay_demand(self.project_root)

        progress["shared_strings"] = []
        self._write_json(self.progress_path, progress)
        with self.assertRaisesRegex(
            TOOL.DemandPinError, "only MSG/SC/strdata.bin"
        ):
            TOOL.collect_overlay_demand(self.project_root)

    def test_stock_input_is_fixed_to_officer_names_backup(self) -> None:
        wrong = self.project_root / "tmp" / "font.stock.bak"
        wrong.parent.mkdir()
        wrong.write_bytes(self.stock.read_bytes())
        with self.assertRaisesRegex(TOOL.DemandPinError, "officer_names_v0_1"):
            TOOL.compute_pin(
                self.project_root,
                stock_path=wrong,
                expected_stock_sha256=self.stock_sha256,
                preflight_stock=self._preflight,
            )


if __name__ == "__main__":
    unittest.main()
