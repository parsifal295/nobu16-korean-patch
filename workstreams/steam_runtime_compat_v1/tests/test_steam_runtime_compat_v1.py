from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


WORKSTREAM = Path(__file__).resolve().parents[1]
COLLECTOR = WORKSTREAM / "Collect-SteamRuntimeCompat.ps1"
EXPECTED = WORKSTREAM / "expected_release.v0.4.1.json"
SCHEMA = WORKSTREAM / "result.schema.v1.json"
README = WORKSTREAM / "README_KO.md"

EXPECTED_V041_PINS = {
    "MSG/SC/strdata.bin": (
        952378,
        "40E435DA4929D5CD5B3085F6CFA2646F492FF121F7DFB65DD16A3ED4DD51C3EB",
    ),
    "MSG_PK/SC/msgbre.bin": (
        478591,
        "69CF70A59F4F1D1EFB35A4123E4BA5B7092AA65DF629C5BE7D8317B97DB3CD29",
    ),
    "MSG_PK/SC/msgdata.bin": (
        487028,
        "E2435AB3EE0A1D39BD473FADF37BACD38C23E1740E0B9898B5844F77A6012662",
    ),
    "MSG_PK/SC/msgev.bin": (
        1030659,
        "596B47864D69D32446BFEF56177D3CCC615132E2BBFDB8154C9D83F78808CE48",
    ),
    "MSG_PK/SC/msggame.bin": (
        1233957,
        "8D4417737975203A4CFF7EB0185DB1959F09D56B5F394CFD8136A58B3E7783C3",
    ),
    "MSG_PK/SC/msgire.bin": (
        23136,
        "045B6ADDD7CF01401A3C10FA69A737B6C32259FA95007584E6A3E32CF2142D2A",
    ),
    "MSG_PK/SC/msgstf.bin": (
        16289,
        "C4A18BC5F7F7FCB8D9913D1AABC0C775059B09CE41261AFE38FB23F15146C195",
    ),
    "MSG_PK/SC/msgui.bin": (
        116027,
        "C683AE9355A43F9A2104E49A6179363727CE0A550682F906C224A44F506826AC",
    ),
    "RES_SC/res_lang.bin": (
        189750493,
        "706563F2BFB3D8BD63B8859366E69066E0FEEFE1A989A14B967BD4649152E271",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def snapshot_tree(root: Path) -> dict[str, tuple[int, int, str]]:
    snapshot: dict[str, tuple[int, int, str]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            stat = path.stat()
            snapshot[path.relative_to(root).as_posix()] = (
                stat.st_size,
                stat.st_mtime_ns,
                sha256(path.read_bytes()),
            )
    return snapshot


def decode_powershell_output(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16", "cp949", "mbcs"):
        try:
            return data.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    raise AssertionError("PowerShell output was not decodable")


def assert_result_shape(test: unittest.TestCase, result: dict) -> None:
    required_top = {
        "schema_version",
        "collector_version",
        "collected_at_utc",
        "game_root",
        "runtime_executable",
        "platform",
        "launcher",
        "steam",
        "expected_release",
        "files",
        "summary",
        "policy",
    }
    test.assertEqual(required_top, set(result))
    test.assertEqual("1.1", result["schema_version"])
    test.assertEqual("1.1.0", result["collector_version"])
    test.assertFalse(result["game_root"]["absolute_path_included"])
    runtime_executable = result["runtime_executable"]
    test.assertEqual("NOBU16PK.exe", runtime_executable["relative_path"])
    test.assertIsInstance(runtime_executable["exists"], bool)
    if runtime_executable["sha256"] is not None:
        test.assertRegex(runtime_executable["sha256"], r"^[0-9A-F]{64}$")
    locale = result["platform"]["windows_system_locale"]
    test.assertTrue(locale["values_are_culture_defaults"])
    nls = result["platform"]["system_nls_code_pages"]
    test.assertTrue(nls["registry_read_only"])
    test.assertEqual(
        "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Nls\\CodePage",
        nls["key"],
    )
    for field, name in (("acp", "ACP"), ("oemcp", "OEMCP"), ("maccp", "MACCP")):
        test.assertEqual(name, nls[field]["name"])
        test.assertIsInstance(nls[field]["present"], bool)
    test.assertIsInstance(result["files"], list)
    test.assertGreaterEqual(len(result["files"]), 7)
    for row in result["files"]:
        test.assertRegex(row["relative_path"], r"^(?![A-Za-z]:)(?!/).+")
        test.assertIsInstance(row["exists"], bool)
        if row["sha256"] is not None:
            test.assertRegex(row["sha256"], r"^[0-9A-F]{64}$")
    policy = result["policy"]
    test.assertTrue(policy["stdout_only"])
    test.assertFalse(policy["filesystem_writes"])
    test.assertTrue(policy["registry_reads"])
    test.assertFalse(policy["registry_writes"])
    test.assertFalse(policy["process_launches"])
    test.assertFalse(policy["network_access"])
    test.assertFalse(policy["game_process_access"])
    test.assertFalse(policy["executable_modification"])


class SteamRuntimeCompatV1Tests(unittest.TestCase):
    maxDiff = None

    def test_expected_v041_release_pins_are_exact_and_source_free(self) -> None:
        metadata = json.loads(EXPECTED.read_text(encoding="utf-8"))
        self.assertEqual("1.0", metadata["schema_version"])
        self.assertEqual("v0.4.1", metadata["release"]["tag"])
        self.assertEqual(
            "NOBU16_PK_Korean_Patch_v0.4.1.zip",
            metadata["release"]["asset_name"],
        )
        self.assertEqual(130249279, metadata["release"]["asset_size"])
        self.assertEqual(
            "BF5092A47E72A521D6BE630C9A222DA9F949AEDC03390FFD8D5BCEF7291AE655",
            metadata["release"]["asset_sha256"],
        )
        pins = {
            row["relative_path"]: (row["size"], row["sha256"])
            for row in metadata["files"]
        }
        self.assertEqual(EXPECTED_V041_PINS, pins)
        self.assertEqual(len(pins), len(metadata["files"]))
        self.assertEqual(
            {
                "contains_game_payload": False,
                "contains_text_extraction": False,
                "source_free_hash_and_size_metadata_only": True,
            },
            metadata["metadata_policy"],
        )
        self.assertNotIn("F:\\Games", EXPECTED.read_text(encoding="utf-8"))

    def test_schema_is_draft_202012_and_covers_collector_contract(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema", schema["$schema"]
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            {
                "schema_version",
                "collector_version",
                "collected_at_utc",
                "game_root",
                "runtime_executable",
                "platform",
                "launcher",
                "steam",
                "expected_release",
                "files",
                "summary",
                "policy",
            },
            set(schema["required"]),
        )
        self.assertIn("fileProbe", schema["$defs"])
        self.assertIn("appManifest", schema["$defs"])
        self.assertIn("registryEntry", schema["$defs"])
        self.assertIn("runtimeExecutable", schema["$defs"])
        self.assertIn("systemNlsCodePages", schema["$defs"])
        self.assertIn("nlsCodePageValue", schema["$defs"])
        self.assertEqual("1.1", schema["properties"]["schema_version"]["const"])

    def test_collector_source_contains_no_mutating_or_process_commands(self) -> None:
        source = COLLECTOR.read_text(encoding="utf-8")
        forbidden_commands = (
            "Set-Content",
            "Add-Content",
            "Out-File",
            "Export-Clixml",
            "Export-Csv",
            "New-Item",
            "Remove-Item",
            "Copy-Item",
            "Move-Item",
            "Rename-Item",
            "Set-Item",
            "Clear-Item",
            "Set-ItemProperty",
            "New-ItemProperty",
            "Remove-ItemProperty",
            "Clear-ItemProperty",
            "Start-Process",
            "Stop-Process",
            "Invoke-WebRequest",
            "Invoke-RestMethod",
            "Set-WinSystemLocale",
        )
        for command in forbidden_commands:
            self.assertIsNone(
                re.search(rf"(?im)(?<![A-Za-z0-9_-]){re.escape(command)}(?![A-Za-z0-9_-])", source),
                command,
            )
        for forbidden_api in (
            r"\.SetValue\(",
            r"CreateSubKey",
            r"DeleteSubKey",
            r"\[System\.IO\.File\]::Write",
            r"\[System\.IO\.File\]::Create",
            r"OpenWrite",
            r"CreateRemoteThread",
            r"SetWindowsHookEx",
        ):
            self.assertIsNone(re.search(forbidden_api, source, re.IGNORECASE), forbidden_api)

        self.assertIn(
            "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Nls\\CodePage", source
        )
        for value_name in ("ACP", "OEMCP", "MACCP"):
            self.assertIn(value_name, source)
        for forbidden_steam_action in ("steam.exe", "steam://", "app_update", "validate"):
            self.assertNotIn(forbidden_steam_action.casefold(), source.casefold())

    def test_readme_keeps_manual_verify_outside_collector_and_captures_stock_hash(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("게임 파일 무결성 검사", readme)
        self.assertIn("manual_steam_verify_complete_patch_not_reapplied", readme)
        self.assertIn("NOBU16_stock_after_manual_steam_verify.json", readme)
        self.assertIn("RES_SC/res_lang.bin", readme)
        self.assertIn("Get-FileHash", readme)
        self.assertIn("%TEMP%", readme)
        self.assertIn("수집기는 Steam 무결성 검사를 실행하거나 Steam을 제어하지 않는다", readme)

    def test_fixture_collects_steam_metadata_matches_pins_and_changes_nothing(self) -> None:
        powershell = shutil.which("powershell.exe") or shutil.which("powershell")
        if powershell is None:
            self.skipTest("Windows PowerShell is unavailable")

        with tempfile.TemporaryDirectory(prefix="steam_runtime_compat_v1_") as td:
            base = Path(td)
            steamapps = base / "library" / "steamapps"
            game_root = steamapps / "common" / "NOBU16"
            game_root.mkdir(parents=True)

            fixture_files = {
                "NOBU16PK.exe": b"fixture-pk-executable",
                "RES_SC/res_lang.bin": b"fixture-font-archive",
                "MSG_PK/SC/msgui.bin": b"fixture-msgui-table",
                "RES_SC_PK/res_lang_pk.bin": b"fixture-pk-resource",
            }
            for relative_path, data in fixture_files.items():
                target = game_root / Path(relative_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)

            appmanifest = steamapps / "appmanifest_1336980.acf"
            appmanifest.write_text(
                '\n'.join(
                    (
                        '"AppState"',
                        "{",
                        '    "appid"        "1336980"',
                        '    "buildid"      "19023019"',
                        '    "InstalledDepots"',
                        "    {",
                        '        "2164240"',
                        "        {",
                        '            "manifest" "9999999999999999999"',
                        "        }",
                        "    }",
                        '    "UserConfig"',
                        "    {",
                        '        "language" "japanese"',
                        "    }",
                        '    "MountedConfig"',
                        "    {",
                        '        "language" "schinese"',
                        "    }",
                        "}",
                    )
                ),
                encoding="utf-8",
            )

            synthetic_metadata = base / "expected.fixture.json"
            synthetic_metadata.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "release": {
                            "tag": "fixture-v1",
                            "asset_name": "fixture.zip",
                            "asset_size": 1,
                            "asset_sha256": "A" * 64,
                        },
                        "files": [
                            {
                                "relative_path": relative_path,
                                "role": "fixture",
                                "size": len(data),
                                "sha256": sha256(data),
                            }
                            for relative_path, data in (
                                ("RES_SC/res_lang.bin", fixture_files["RES_SC/res_lang.bin"]),
                                ("MSG_PK/SC/msgui.bin", fixture_files["MSG_PK/SC/msgui.bin"]),
                            )
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            before = snapshot_tree(base)
            completed = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    os.fspath(COLLECTOR),
                    "-GameRoot",
                    os.fspath(game_root),
                    "-ExpectedReleaseMetadataPath",
                    os.fspath(synthetic_metadata),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            stderr = decode_powershell_output(completed.stderr)
            self.assertEqual(0, completed.returncode, stderr)
            result = json.loads(decode_powershell_output(completed.stdout))
            after = snapshot_tree(base)
            self.assertEqual(before, after)

            assert_result_shape(self, result)
            self.assertEqual("NOBU16", result["game_root"]["leaf_name"])
            self.assertTrue(result["game_root"]["under_steamapps_common"])
            self.assertNotIn(os.fspath(base), json.dumps(result))

            steam = result["steam"]
            self.assertTrue(steam["detected_from_nearby_appmanifest"])
            manifest = steam["appmanifest"]
            self.assertTrue(manifest["present"])
            self.assertEqual("1336980", manifest["app_id"])
            self.assertEqual("19023019", manifest["build_id"])
            self.assertEqual("japanese", manifest["user_language"])
            self.assertEqual("schinese", manifest["mounted_language"])
            self.assertEqual(["2164240"], manifest["installed_depot_ids"])

            summary = result["summary"]
            self.assertEqual(2, summary["expected_release_file_count"])
            self.assertEqual(2, summary["matched_release_file_count"])
            self.assertTrue(summary["all_expected_release_files_match"])
            self.assertEqual([], summary["mismatch_or_missing_paths"])
            self.assertTrue(summary["font_archive_matches_release"])
            self.assertTrue(summary["msgui_matches_release"])

            files = {row["relative_path"]: row for row in result["files"]}
            self.assertEqual(
                sha256(fixture_files["NOBU16PK.exe"]), files["NOBU16PK.exe"]["sha256"]
            )
            runtime_executable = result["runtime_executable"]
            self.assertTrue(runtime_executable["exists"])
            self.assertEqual(
                len(fixture_files["NOBU16PK.exe"]), runtime_executable["size"]
            )
            self.assertEqual(
                sha256(fixture_files["NOBU16PK.exe"]), runtime_executable["sha256"]
            )
            self.assertEqual(
                files["NOBU16PK.exe"]["size"], runtime_executable["size"]
            )
            self.assertEqual(
                files["NOBU16PK.exe"]["sha256"], runtime_executable["sha256"]
            )
            self.assertTrue(files["RES_SC/res_lang.bin"]["matches_expected_release"])
            self.assertTrue(files["MSG_PK/SC/msgui.bin"]["matches_expected_release"])
            self.assertIsNone(files["RES_SC_PK/res_lang_pk.bin"]["matches_expected_release"])

            registry_entries = result["launcher"]["registry_entries"]
            self.assertEqual(4, len(registry_entries))
            self.assertTrue(all(isinstance(row, dict) for row in registry_entries))

            nls = result["platform"]["system_nls_code_pages"]
            self.assertTrue(nls["key_exists"])
            self.assertIsNone(nls["read_error_type"])
            for field in ("acp", "oemcp", "maccp"):
                self.assertTrue(nls[field]["present"])
                self.assertIsInstance(nls[field]["raw_value"], (str, int))
                self.assertIsInstance(nls[field]["parsed_code_page"], int)
                self.assertGreater(nls[field]["parsed_code_page"], 0)


if __name__ == "__main__":
    unittest.main()
