"""Regression tests for the offline Steam JP v0.10.0 image candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_steam_jp_117_image_candidate_v1.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_117_image_candidate_v1", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJP117ImageCandidateV1Tests(unittest.TestCase):
    def make_tmp_dir(self) -> Path:
        directory = Path(
            tempfile.mkdtemp(prefix=".steam-jp-117-image-test-", dir=builder.TMP_ROOT)
        )
        self.addCleanup(
            lambda: builder.safe_rmtree(
                directory, "test temporary cleanup", ignore_errors=True
            )
        )
        return directory

    def test_runtime_scope_and_no_installation_commands(self) -> None:
        self.assertEqual(builder.DEFAULT_ZIP_NAME, "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.0.zip")
        self.assertEqual(builder.REPLACED_RESOURCE, "RES_JP/res_lang.bin")
        self.assertEqual(len(builder.TARGETS), 14)
        self.assertEqual(builder.TARGETS, tuple(sorted(builder.TARGETS)))
        self.assertTrue(all("/JP/" in path or path.startswith("RES_JP") for path in builder.TARGETS))
        self.assertFalse(any("/SC/" in path or path.startswith("RES_SC") for path in builder.TARGETS))
        parser = builder.build_parser()
        commands = next(action for action in parser._actions if action.dest == "command")
        self.assertEqual(set(commands.choices), {"bootstrap", "verify", "build"})

    def test_pinned_v09_manifest_and_zip_agree(self) -> None:
        self.assertEqual(
            builder.DEFAULT_V09_INPUT_ROOT,
            builder.TMP_ROOT / "steam_jp_117_image_candidate_v1_inputs" / "v0.9.0",
        )
        self.assertTrue(builder.DEFAULT_V09_INPUT_ROOT.is_relative_to(builder.TMP_ROOT))
        self.assertNotIn("guard_final", builder.DEFAULT_V09_INPUT_ROOT.as_posix())
        self.assertTrue(builder.DEFAULT_BASELINE_ZIP.is_file())
        self.assertTrue(builder.DEFAULT_BASELINE_MANIFEST.is_file())
        manifest = builder.load_v09_manifest(builder.DEFAULT_BASELINE_MANIFEST)
        self.assertEqual(manifest["runtime"], builder.EXPECTED_RUNTIME)
        self.assertEqual(manifest["candidate_paths"], list(builder.TARGETS))
        self.assertEqual(
            manifest["candidates"][builder.REPLACED_RESOURCE],
            builder.TITLE_SOURCE_FONT_BASELINE,
        )
        self.assertEqual(
            manifest["predecessors"][builder.REPLACED_RESOURCE],
            builder.STOCK_RES_LANG_PREDECESSOR,
        )
        builder.validate_v09_zip(builder.DEFAULT_BASELINE_ZIP, manifest)

    def test_inputs_are_distinct_regular_files_before_staging(self) -> None:
        paths = builder.require_safe_distinct_inputs(
            builder.DEFAULT_BASELINE_ZIP,
            builder.DEFAULT_BASELINE_MANIFEST,
            builder.DEFAULT_TITLE_CANDIDATE,
        )
        self.assertEqual(paths[0], builder.DEFAULT_BASELINE_ZIP.resolve())
        self.assertEqual(paths[1], builder.DEFAULT_BASELINE_MANIFEST.resolve())
        self.assertEqual(paths[2], builder.DEFAULT_TITLE_CANDIDATE.resolve())
        with self.assertRaises(builder.ImageCandidateError):
            builder.require_safe_distinct_inputs(
                builder.DEFAULT_BASELINE_ZIP,
                builder.DEFAULT_BASELINE_ZIP,
                builder.DEFAULT_TITLE_CANDIDATE,
            )

    def test_title_image_input_is_pinned_to_v09_font_baseline(self) -> None:
        validation = builder.load_title_validation()
        candidate = builder.validate_title_candidate(builder.DEFAULT_TITLE_CANDIDATE)
        self.assertEqual(candidate, builder.TITLE_CANDIDATE_PIN)
        self.assertEqual(
            validation["pins"]["steam_jp_font_baseline"],
            builder.TITLE_SOURCE_FONT_BASELINE,
        )
        self.assertEqual(
            validation["pins"]["steam_jp_title_candidate"],
            builder.TITLE_CANDIDATE_PIN,
        )

    def test_full_offline_composition_matches_tracked_verification(self) -> None:
        expected = builder.load_tracked_verification()
        directory = self.make_tmp_dir()
        _manifest, actual = builder.build_staged(
            builder.DEFAULT_BASELINE_ZIP,
            builder.DEFAULT_BASELINE_MANIFEST,
            builder.DEFAULT_TITLE_CANDIDATE,
            directory,
            None,
        )
        self.assertEqual(actual, expected)

    def test_live_guard_covers_exact_targets_and_both_executables(self) -> None:
        self.assertEqual(builder.LIVE_GUARD_PATHS[:-2], builder.TARGETS)
        self.assertEqual(builder.LIVE_GUARD_PATHS[-2:], ("NOBU16.exe", "NOBU16PK.exe"))

    def test_candidate_tree_and_zip_reject_extra_members(self) -> None:
        directory = self.make_tmp_dir()
        root = directory / "candidate"
        root.mkdir()
        for relative in builder.TARGETS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(relative.encode("ascii"))
        self.assertEqual(builder.candidate_paths(root), list(builder.TARGETS))
        extra = root / "exefs" / "main"
        extra.parent.mkdir(parents=True)
        extra.write_bytes(b"not allowed")
        with self.assertRaises(builder.ImageCandidateError):
            builder.candidate_paths(root)

    def test_deterministic_zip_has_exact_members_only(self) -> None:
        directory = self.make_tmp_dir()
        root = directory / "candidate"
        root.mkdir()
        for relative in builder.TARGETS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((relative + "\n").encode("ascii"))
        first = directory / "first.zip"
        second = directory / "second.zip"
        self.assertEqual(builder.make_zip(root, first), builder.make_zip(root, second))
        self.assertEqual(first.read_bytes(), second.read_bytes())
        builder.assert_zip_matches(root, first)

    def test_reparse_helpers_reject_symlink_and_junction_without_privilege(self) -> None:
        probe = self.make_tmp_dir() / "probe"
        with mock.patch.object(Path, "is_symlink", return_value=True):
            self.assertEqual(builder._reparse_kind(probe), "symlink")
        with (
            mock.patch.object(Path, "is_symlink", return_value=False),
            mock.patch.object(Path, "is_junction", return_value=True),
        ):
            self.assertEqual(builder._reparse_kind(probe), "junction")

    def test_tmp_component_and_cleanup_reject_mocked_junction_without_deleting(self) -> None:
        root = self.make_tmp_dir()
        staging = root / "staging"
        nested = staging / "nested"
        nested.mkdir(parents=True)

        def mocked_reparse(path: Path) -> str | None:
            return "junction" if Path(path) == nested else None

        with (
            mock.patch.object(builder, "TMP_ROOT", root),
            mock.patch.object(builder, "_reparse_kind", side_effect=mocked_reparse),
        ):
            with self.assertRaises(builder.ImageCandidateError):
                builder.assert_safe_tmp_path(nested / "file.bin", "mocked junction target")
            with self.assertRaises(builder.ImageCandidateError):
                builder.safe_rmtree(staging, "mocked junction cleanup")
        self.assertTrue(staging.is_dir())

    def test_destination_guard_rejects_repository_and_game_locations(self) -> None:
        self.assertEqual(
            builder.ensure_safe_tmp_directory(builder.TMP_ROOT, "test tmp root"),
            builder.TMP_ROOT.resolve(),
        )
        for path in (builder.REPO, builder.REPO / "workstreams", builder.DEFAULT_LIVE_GAME_ROOT):
            with self.subTest(path=path):
                with self.assertRaises(builder.ImageCandidateError):
                    builder.validate_destination(path)

    def test_source_free_public_workstream_contains_no_game_binary(self) -> None:
        validation = json.loads((ROOT / "validation.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(validation["schema"], builder.VALIDATION_SCHEMA)
        self.assertTrue(validation["source_free"])
        self.assertTrue(validation["file_only"])
        self.assertFalse(validation["game_install_modified"])
        self.assertEqual(
            validation["baseline_v0_9"]["shared_default_input_root"],
            "tmp/steam_jp_117_image_candidate_v1_inputs/v0.9.0",
        )
        self.assertTrue(
            validation["baseline_v0_9"]["default_input_uses_inherited_acl_bucket"]
        )
        self.assertTrue(validation["constraints"]["archive_members_exactly_fourteen"])
        self.assertFalse(validation["constraints"]["steam_files_written"])
        forbidden = {".bin", ".g1n", ".ttf", ".otf", ".zip", ".pixels", ".png", ".pyc"}
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in forbidden
        ]
        self.assertEqual(offenders, [])
        self.assertFalse((ROOT / "__pycache__").exists())


if __name__ == "__main__":
    unittest.main()
