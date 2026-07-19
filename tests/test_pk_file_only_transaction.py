from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "pk_file_only_transaction.py"
SPEC = importlib.util.spec_from_file_location("pk_file_only_transaction", MODULE_PATH)
assert SPEC and SPEC.loader
tx = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tx)


class PkFileOnlyTransactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="n16_pk_transaction_"))
        self.game = self.root / "game"
        self.candidates_root = self.root / "candidates"
        self.manifest_path = self.root / "candidate.transaction.json"
        self._write(self.game / "MSG_PK" / "SC" / "msgui.bin", b"stock-msgui")
        self._write(self.game / "RES_SC" / "res_lang.bin", b"stock-font")
        # A sentinel confirms that the base-game resource tree is never even
        # part of the local transaction's target set.
        self._write(self.game / "MSG" / "SC" / "ev_strdata.bin", b"base-sentinel")
        self._write(self.candidates_root / "MSG_PK" / "SC" / "msgui.bin", b"target-msgui")
        self._write(self.candidates_root / "RES_SC" / "res_lang.bin", b"target-font")

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    @staticmethod
    def _write(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    @staticmethod
    def _make_directory_link(link: Path, target: Path) -> bool:
        link.parent.mkdir(parents=True, exist_ok=True)
        target.mkdir(parents=True, exist_ok=True)
        try:
            if os.name == "nt":
                completed = subprocess.run(
                    ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                return completed.returncode == 0 and link.exists()
            link.symlink_to(target, target_is_directory=True)
            return True
        except OSError:
            return False

    def _candidates(self) -> dict[str, Path]:
        return {
            "MSG_PK/SC/msgui.bin": self.candidates_root / "MSG_PK" / "SC" / "msgui.bin",
            "RES_SC/res_lang.bin": self.candidates_root / "RES_SC" / "res_lang.bin",
        }

    def _manifest(self) -> tuple[dict, str, Path]:
        manifest = tx.make_manifest(self.game, "fixture-v1", self._candidates())
        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        return loaded, manifest_hash, backup

    def _prepare_jp_profile(
        self,
    ) -> tuple[dict[str, Path], dict[str, bytes], dict[Path, bytes]]:
        candidate_root = self.root / "jp-candidates"
        candidates: dict[str, Path] = {}
        predecessors: dict[str, bytes] = {}
        for relative in sorted(tx.JP_ALLOWED_TARGETS):
            predecessor = ("stock::" + relative).encode()
            target = ("target::" + relative).encode()
            installed = self.game.joinpath(*relative.split("/"))
            candidate = candidate_root.joinpath(*relative.split("/"))
            self._write(installed, predecessor)
            self._write(candidate, target)
            candidates[relative] = candidate
            predecessors[relative] = predecessor
        sentinels = {
            self.game / "MSG" / "JP" / "ev_strdata.bin": b"jp-base-event-sentinel",
            self.game / "RES_JP" / "res_lang_exp.bin": b"jp-exp-sentinel",
            self.game / "RES_JP_PK" / "res_lang_exp_pk.bin": b"jp-pk-exp-sentinel",
            self.game
            / "RES_JP_PK_PORT"
            / "res_lang_pk_port3.bin": b"jp-pk-port3-sentinel",
            self.game / "NOBU16PK.exe": b"executable-sentinel",
        }
        for path, payload in sentinels.items():
            self._write(path, payload)
        return candidates, predecessors, sentinels

    def _prepare_jp_full_profile(
        self,
    ) -> tuple[dict[str, Path], dict[str, bytes], dict[Path, bytes]]:
        candidates, predecessors, sentinels = self._prepare_jp_profile()
        # ``ev_strdata.bin`` is deliberately a sentinel in the legacy JP
        # fixture.  The full profile explicitly owns it, together with the
        # base map/tutorial dialogue archive.
        sentinels.pop(self.game / "MSG" / "JP" / "ev_strdata.bin")
        for relative in sorted(tx.JP_BASE_DIALOGUE_TARGETS):
            predecessor = ("stock::" + relative).encode()
            target = ("target::" + relative).encode()
            installed = self.game.joinpath(*relative.split("/"))
            candidate = (self.root / "jp-candidates").joinpath(*relative.split("/"))
            self._write(installed, predecessor)
            self._write(candidate, target)
            candidates[relative] = candidate
            predecessors[relative] = predecessor
        extra_base = self.game / "MSG" / "JP" / "unlisted.bin"
        self._write(extra_base, b"jp-base-unlisted-sentinel")
        sentinels[extra_base] = b"jp-base-unlisted-sentinel"
        return candidates, predecessors, sentinels

    def _prepare_jp_text_audit_profile(
        self,
    ) -> tuple[dict[str, Path], dict[str, bytes], dict[Path, bytes]]:
        candidate_root = self.root / "jp-text-audit-candidates"
        candidates: dict[str, Path] = {}
        predecessors: dict[str, bytes] = {}
        for relative in sorted(tx.JP_TEXT_AUDIT_ALLOWED_TARGETS):
            predecessor = ("stock::" + relative).encode()
            target = ("target::" + relative).encode()
            installed = self.game.joinpath(*relative.split("/"))
            candidate = candidate_root.joinpath(*relative.split("/"))
            self._write(installed, predecessor)
            self._write(candidate, target)
            candidates[relative] = candidate
            predecessors[relative] = predecessor
        sentinels = {
            self.game / "RES_JP" / "res_lang.bin": b"jp-font-sentinel",
            self.game / "RES_JP_PK" / "res_lang_pk.bin": b"jp-pk-font-sentinel",
            self.game / "RES_JP_PK_PORT" / "res_lang_pk_port1.bin": b"jp-port-font-sentinel",
            self.game / "NOBU16PK.exe": b"executable-sentinel",
        }
        for path, payload in sentinels.items():
            self._write(path, payload)
        return candidates, predecessors, sentinels

    def _prepare_jp_four_file_text_profile(
        self,
    ) -> tuple[dict[str, Path], dict[str, bytes], dict[Path, bytes]]:
        candidate_root = self.root / "jp-four-file-text-candidates"
        candidates: dict[str, Path] = {}
        predecessors: dict[str, bytes] = {}
        for relative in sorted(tx.JP_FOUR_FILE_TEXT_ALLOWED_TARGETS):
            predecessor = ("stock::" + relative).encode()
            target = ("target::" + relative).encode()
            installed = self.game.joinpath(*relative.split("/"))
            candidate = candidate_root.joinpath(*relative.split("/"))
            self._write(installed, predecessor)
            self._write(candidate, target)
            candidates[relative] = candidate
            predecessors[relative] = predecessor
        sentinels = {
            self.game / "MSG" / "JP" / "ev_strdata.bin": b"jp-base-event-sentinel",
            self.game / "MSG" / "JP" / "strdata.bin": b"jp-base-shared-sentinel",
            self.game / "MSG_PK" / "JP" / "msgbre.bin": b"jp-battle-sentinel",
            self.game / "MSG_PK" / "JP" / "msgire.bin": b"jp-incident-sentinel",
            self.game / "MSG_PK" / "JP" / "msgstf.bin": b"jp-staff-sentinel",
            self.game / "RES_JP" / "res_lang.bin": b"jp-font-sentinel",
            self.game / "RES_JP_PK" / "res_lang_pk.bin": b"jp-pk-font-sentinel",
            self.game
            / "RES_JP_PK_PORT"
            / "res_lang_pk_port1.bin": b"jp-port-font-sentinel",
            self.game / "NOBU16PK.exe": b"executable-sentinel",
        }
        for path, payload in sentinels.items():
            self._write(path, payload)
        return candidates, predecessors, sentinels

    def test_plan_dry_run_apply_restore_is_complete_and_base_unchanged(self) -> None:
        manifest, manifest_hash, backup = self._manifest()
        raw = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(raw["target_scope"], tx.TARGET_SCOPE)
        self.assertEqual([entry["path"] for entry in raw["entries"]], [
            "MSG_PK/SC/msgui.bin",
            "RES_SC/res_lang.bin",
        ])
        self.assertEqual([entry["mode"] for entry in raw["entries"]], ["replace", "replace"])
        # The hash-only manifest must not retain the candidate's local source path.
        self.assertNotIn(str(self.candidates_root), self.manifest_path.read_text(encoding="utf-8"))

        dry_run = tx.dry_run(self.game, backup, manifest, self._candidates())
        self.assertEqual(dry_run["status"], "PASS")
        self.assertTrue(dry_run["would_apply"])
        self.assertFalse(dry_run["writes_performed"])
        self.assertEqual(dry_run["scope"]["msg_pk_sc_count"], 1)
        self.assertEqual(dry_run["scope"]["res_sc_count"], 1)
        self.assertEqual(dry_run["scope"]["base_msg_sc_count"], 0)
        self.assertFalse(dry_run["scope"]["all_seven_msg_pk_sc_included"])
        self.assertFalse(backup.exists())

        with mock.patch.object(tx, "assert_game_stopped"):
            applied = tx.apply_transaction(self.game, backup, manifest, manifest_hash, self._candidates())
        self.assertEqual(applied["result"], "applied")
        self.assertEqual((self.game / "MSG_PK" / "SC" / "msgui.bin").read_bytes(), b"target-msgui")
        self.assertEqual((self.game / "RES_SC" / "res_lang.bin").read_bytes(), b"target-font")
        self.assertEqual((self.game / "MSG" / "SC" / "ev_strdata.bin").read_bytes(), b"base-sentinel")
        self.assertTrue((backup / "originals" / "MSG_PK" / "SC" / "msgui.bin").is_file())
        self.assertTrue((backup / "originals" / "RES_SC" / "res_lang.bin").is_file())

        with mock.patch.object(tx, "assert_game_stopped"):
            restored = tx.restore_transaction(self.game, backup, manifest, manifest_hash)
        self.assertEqual(restored["result"], "restored")
        self.assertEqual((self.game / "MSG_PK" / "SC" / "msgui.bin").read_bytes(), b"stock-msgui")
        self.assertEqual((self.game / "RES_SC" / "res_lang.bin").read_bytes(), b"stock-font")
        self.assertEqual((self.game / "MSG" / "SC" / "ev_strdata.bin").read_bytes(), b"base-sentinel")

    def test_unlisted_base_game_and_unknown_pk_targets_are_rejected(self) -> None:
        self._write(self.candidates_root / "MSG" / "SC" / "ev_strdata.bin", b"forbidden")
        with self.assertRaisesRegex(tx.TransactionError, "outside PK scope"):
            tx.make_manifest(
                self.game,
                "fixture-v1",
                {"MSG/SC/ev_strdata.bin": self.candidates_root / "MSG" / "SC" / "ev_strdata.bin"},
            )

    def test_exact_shared_strdata_target_is_allowed_and_restorable(self) -> None:
        installed = self.game / "MSG" / "SC" / "strdata.bin"
        candidate = self.candidates_root / "MSG" / "SC" / "strdata.bin"
        self._write(installed, b"stock-shared-strdata")
        self._write(candidate, b"target-shared-strdata")
        candidates = {"MSG/SC/strdata.bin": candidate}
        manifest = tx.make_manifest(self.game, "shared-strdata-v1", candidates)
        self.assertEqual(tx.scope_report(manifest)["base_msg_sc_count"], 1)
        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        self.assertTrue(tx.dry_run(self.game, backup, loaded, candidates)["would_apply"])
        with mock.patch.object(tx, "assert_game_stopped"):
            tx.apply_transaction(self.game, backup, loaded, manifest_hash, candidates)
        self.assertEqual(installed.read_bytes(), b"target-shared-strdata")
        with mock.patch.object(tx, "assert_game_stopped"):
            tx.restore_transaction(self.game, backup, loaded, manifest_hash)
        self.assertEqual(installed.read_bytes(), b"stock-shared-strdata")
        self._write(self.candidates_root / "MSG_PK" / "SC" / "unknown.bin", b"forbidden")
        with self.assertRaisesRegex(tx.TransactionError, "outside PK scope"):
            tx.make_manifest(
                self.game,
                "fixture-v1",
                {"MSG_PK/SC/unknown.bin": self.candidates_root / "MSG_PK" / "SC" / "unknown.bin"},
            )

    def test_dry_run_reports_mixed_vector_without_writing(self) -> None:
        manifest, _, backup = self._manifest()
        (self.game / "MSG_PK" / "SC" / "msgui.bin").write_bytes(b"target-msgui")
        report = tx.dry_run(self.game, backup, manifest, self._candidates())
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["installed_state"], "mixed")
        self.assertEqual((self.game / "RES_SC" / "res_lang.bin").read_bytes(), b"stock-font")
        self.assertFalse(backup.exists())

    def test_restore_refuses_unknown_file_without_overwriting_it(self) -> None:
        manifest, manifest_hash, backup = self._manifest()
        with mock.patch.object(tx, "assert_game_stopped"):
            tx.apply_transaction(self.game, backup, manifest, manifest_hash, self._candidates())
        self._write(self.game / "RES_SC" / "res_lang.bin", b"manual-unknown-edit")
        with self.assertRaisesRegex(tx.TransactionError, "unknown or missing"):
            with mock.patch.object(tx, "assert_game_stopped"):
                tx.restore_transaction(self.game, backup, manifest, manifest_hash)
        self.assertEqual((self.game / "RES_SC" / "res_lang.bin").read_bytes(), b"manual-unknown-edit")
        self.assertEqual((self.game / "MSG_PK" / "SC" / "msgui.bin").read_bytes(), b"target-msgui")

    def test_apply_refuses_running_game_before_backup_or_resource_write(self) -> None:
        manifest, manifest_hash, backup = self._manifest()
        with mock.patch.object(tx, "running_game_processes", return_value=["nobu16pk.exe"]):
            with self.assertRaisesRegex(tx.TransactionError, "close the game"):
                tx.apply_transaction(self.game, backup, manifest, manifest_hash, self._candidates())
        self.assertFalse(backup.exists())
        self.assertEqual((self.game / "MSG_PK" / "SC" / "msgui.bin").read_bytes(), b"stock-msgui")
        self.assertEqual((self.game / "RES_SC" / "res_lang.bin").read_bytes(), b"stock-font")

    def test_duplicate_and_base_path_manifest_are_rejected_before_dry_run(self) -> None:
        _, _, _ = self._manifest()
        duplicate = self.root / "duplicate.json"
        duplicate.write_text(
            '{"schema":"x","Schema":"x"}', encoding="utf-8", newline="\n"
        )
        with self.assertRaisesRegex(tx.TransactionError, "duplicate or case-colliding"):
            tx.read_manifest(duplicate)

        invalid = {
            "schema": tx.MANIFEST_SCHEMA,
            "release_id": "fixture-v1",
            "file_only": True,
            "process_memory_access": False,
            "dll_injection": False,
            "hooking": False,
            "executable_modified": False,
            "registry_modified": False,
            "target_scope": tx.TARGET_SCOPE,
            "entries": [{
                "path": "MSG/SC/ev_strdata.bin",
                "mode": "replace",
                "predecessor": {"size": 1, "sha256": "A" * 64},
                "target": {"size": 2, "sha256": "B" * 64},
            }],
        }
        invalid_path = self.root / "invalid-base.json"
        tx.write_atomic_json(invalid_path, invalid)
        with self.assertRaisesRegex(tx.TransactionError, "outside PK scope"):
            tx.read_manifest(invalid_path)

    def test_already_target_candidate_is_retained_in_a_composite_transaction(self) -> None:
        # This models an interrupted/manual first-stage MSGUI update.  A later
        # full PK composite may pin it as a retained member while atomically
        # applying the remaining files, rather than blindly overwriting it.
        self._write(self.game / "MSG_PK" / "SC" / "msgui.bin", b"target-msgui")
        manifest = tx.make_manifest(self.game, "fixture-v1", self._candidates())
        modes = {entry["path"]: entry["mode"] for entry in manifest["entries"]}
        self.assertEqual(modes["MSG_PK/SC/msgui.bin"], "retain")
        self.assertEqual(modes["RES_SC/res_lang.bin"], "replace")
        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        self.assertTrue(tx.dry_run(self.game, backup, loaded, self._candidates())["would_apply"])
        with mock.patch.object(tx, "assert_game_stopped"):
            tx.apply_transaction(self.game, backup, loaded, manifest_hash, self._candidates())
        self.assertEqual((self.game / "MSG_PK" / "SC" / "msgui.bin").read_bytes(), b"target-msgui")
        self.assertEqual((self.game / "RES_SC" / "res_lang.bin").read_bytes(), b"target-font")
        with mock.patch.object(tx, "assert_game_stopped"):
            tx.restore_transaction(self.game, backup, loaded, manifest_hash)
        self.assertEqual((self.game / "MSG_PK" / "SC" / "msgui.bin").read_bytes(), b"target-msgui")
        self.assertEqual((self.game / "RES_SC" / "res_lang.bin").read_bytes(), b"stock-font")

    def test_all_retain_plan_is_rejected_as_an_explicit_no_op(self) -> None:
        candidates, _predecessors, _sentinels = self._prepare_jp_profile()
        all_retain = tx.make_manifest(self.game, "jp-all-retain-manual-v1", candidates)
        for entry in all_retain["entries"]:
            entry["mode"] = "retain"
            entry["predecessor"] = dict(entry["target"])
        with self.assertRaisesRegex(tx.TransactionError, "all-retain no-op transaction"):
            tx.validate_manifest(all_retain)

        for relative, candidate in candidates.items():
            installed = self.game.joinpath(*relative.split("/"))
            installed.write_bytes(candidate.read_bytes())

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = tx.main([
                "plan",
                "--game-root", str(self.game),
                "--release-id", "jp-already-installed-v1",
                "--manifest", str(self.manifest_path),
                "--candidate-root", str(self.root / "jp-candidates"),
            ])

        self.assertEqual(exit_code, 2)
        self.assertIn("all-retain no-op transaction", output.getvalue())
        self.assertFalse(self.manifest_path.exists())

    def test_candidate_root_collects_only_the_allowed_pk_scope(self) -> None:
        self._write(self.candidates_root / "MSG" / "SC" / "ev_strdata.bin", b"forbidden")
        found = tx.collect_candidate_root(self.candidates_root)
        self.assertEqual(set(found), {"MSG_PK/SC/msgui.bin", "RES_SC/res_lang.bin"})
        self.assertNotIn("MSG/SC/ev_strdata.bin", found)

    def test_full_seven_message_scope_is_reported_exactly(self) -> None:
        candidates = self._candidates()
        for name in tx.SC_MESSAGE_FILES:
            relative = f"MSG_PK/SC/{name}"
            if relative in candidates:
                continue
            self._write(self.game / "MSG_PK" / "SC" / name, ("stock-" + name).encode())
            candidate = self.candidates_root / "MSG_PK" / "SC" / name
            self._write(candidate, ("target-" + name).encode())
            candidates[relative] = candidate
        manifest = tx.make_manifest(self.game, "full-fixture-v1", candidates)
        report = tx.scope_report(manifest)
        self.assertEqual(report["msg_pk_sc_count"], 7)
        self.assertEqual(report["res_sc_count"], 1)
        self.assertEqual(report["base_msg_sc_count"], 0)
        self.assertTrue(report["all_seven_msg_pk_sc_included"])

    def test_exact_jp_port_plan_dry_run_apply_restore_and_sentinels(self) -> None:
        candidates, predecessors, sentinels = self._prepare_jp_profile()
        candidate_root = self.root / "jp-candidates"
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = tx.main([
                "plan",
                "--game-root", str(self.game),
                "--release-id", "jp-fixture-v1",
                "--manifest", str(self.manifest_path),
                "--candidate-root", str(candidate_root),
            ])
        self.assertEqual(exit_code, 0, output.getvalue())
        manifest, manifest_hash = tx.read_manifest(self.manifest_path)
        self.assertEqual(manifest["target_scope"], tx.JP_PORT_TARGET_SCOPE)
        self.assertEqual({entry["path"] for entry in manifest["entries"]}, tx.JP_ALLOWED_TARGETS)
        scope = tx.scope_report(manifest)
        self.assertEqual(scope["runtime_language"], "JP")
        self.assertEqual(scope["msg_pk_jp_count"], 7)
        self.assertEqual(scope["base_msg_jp_count"], 1)
        self.assertEqual(scope["res_jp_count"], 1)
        self.assertEqual(scope["res_jp_pk_count"], 1)
        self.assertEqual(scope["res_jp_pk_port_count"], 2)
        self.assertTrue(scope["all_seven_msg_pk_jp_included"])
        self.assertEqual(scope["jp_10_file_count"], 10)
        self.assertFalse(scope["jp_10_file_complete"])
        self.assertEqual(scope["jp_12_file_count"], 12)
        self.assertTrue(scope["jp_12_file_complete"])

        backup = tx.default_backup_root(self.game, manifest["release_id"])
        report = tx.dry_run(self.game, backup, manifest, candidates)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["installed_state"], "predecessor")
        self.assertTrue(report["would_apply"])
        self.assertFalse(report["writes_performed"])
        self.assertFalse(backup.exists())

        with mock.patch.object(tx, "assert_game_stopped"):
            applied = tx.apply_transaction(
                self.game, backup, manifest, manifest_hash, candidates
            )
        self.assertEqual(applied["result"], "applied")
        for relative, candidate in candidates.items():
            installed = self.game.joinpath(*relative.split("/"))
            self.assertEqual(installed.read_bytes(), candidate.read_bytes())
            self.assertTrue(backup.joinpath("originals", *relative.split("/")).is_file())
        for path, payload in sentinels.items():
            self.assertEqual(path.read_bytes(), payload)

        with mock.patch.object(tx, "assert_game_stopped"):
            restored = tx.restore_transaction(self.game, backup, manifest, manifest_hash)
        self.assertEqual(restored["result"], "restored")
        for relative, predecessor in predecessors.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(), predecessor
            )
        for path, payload in sentinels.items():
            self.assertEqual(path.read_bytes(), payload)

    def test_exact_jp_full_plan_apply_restore_includes_base_dialogues(self) -> None:
        candidates, predecessors, sentinels = self._prepare_jp_full_profile()
        manifest = tx.make_manifest(self.game, "jp-full-dialogue-v1", candidates)
        self.assertEqual(manifest["target_scope"], tx.JP_FULL_TARGET_SCOPE)
        self.assertEqual(
            {entry["path"] for entry in manifest["entries"]},
            tx.JP_FULL_ALLOWED_TARGETS,
        )
        scope = tx.scope_report(manifest)
        self.assertEqual(scope["runtime_language"], "JP")
        self.assertEqual(scope["base_msg_jp_count"], 3)
        self.assertEqual(scope["base_msg_jp_dialogue_count"], 2)
        self.assertEqual(scope["jp_14_file_count"], 14)
        self.assertTrue(scope["jp_14_file_complete"])
        self.assertFalse(scope["jp_12_file_complete"])

        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        report = tx.dry_run(self.game, backup, loaded, candidates)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["would_apply"])

        with mock.patch.object(tx, "assert_game_stopped"):
            applied = tx.apply_transaction(
                self.game, backup, loaded, manifest_hash, candidates
            )
        self.assertEqual(applied["result"], "applied")
        for relative, candidate in candidates.items():
            installed = self.game.joinpath(*relative.split("/"))
            self.assertEqual(installed.read_bytes(), candidate.read_bytes())
            self.assertTrue(backup.joinpath("originals", *relative.split("/")).is_file())
        for path, payload in sentinels.items():
            self.assertEqual(path.read_bytes(), payload)

        with mock.patch.object(tx, "assert_game_stopped"):
            restored = tx.restore_transaction(
                self.game, backup, loaded, manifest_hash
            )
        self.assertEqual(restored["result"], "restored")
        for relative, predecessor in predecessors.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(), predecessor
            )
        for path, payload in sentinels.items():
            self.assertEqual(path.read_bytes(), payload)

    def test_exact_jp_text_audit_plan_apply_restore_without_fonts(self) -> None:
        candidates, predecessors, sentinels = self._prepare_jp_text_audit_profile()
        self.assertEqual(
            set(tx.collect_candidate_root(self.root / "jp-text-audit-candidates")),
            set(candidates),
        )
        manifest = tx.make_manifest(self.game, "jp-text-audit-v1", candidates)
        self.assertEqual(manifest["target_scope"], tx.JP_TEXT_AUDIT_TARGET_SCOPE)
        self.assertEqual(
            {entry["path"] for entry in manifest["entries"]},
            tx.JP_TEXT_AUDIT_ALLOWED_TARGETS,
        )
        scope = tx.scope_report(manifest)
        self.assertEqual(scope["runtime_language"], "JP")
        self.assertEqual(scope["msg_pk_jp_count"], 8)
        self.assertEqual(scope["base_msg_jp_count"], 3)
        self.assertTrue(scope["all_eight_text_audit_msg_pk_jp_included"])
        self.assertEqual(scope["jp_11_text_audit_file_count"], 11)
        self.assertTrue(scope["jp_11_text_audit_file_complete"])
        self.assertFalse(scope["jp_14_file_complete"])

        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        self.assertTrue(tx.dry_run(self.game, backup, loaded, candidates)["would_apply"])
        with mock.patch.object(tx, "assert_game_stopped"):
            applied = tx.apply_transaction(
                self.game, backup, loaded, manifest_hash, candidates
            )
        self.assertEqual(applied["result"], "applied")
        for relative, candidate in candidates.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(),
                candidate.read_bytes(),
            )
            self.assertTrue(backup.joinpath("originals", *relative.split("/")).is_file())
        for path, payload in sentinels.items():
            self.assertEqual(path.read_bytes(), payload)

        with mock.patch.object(tx, "assert_game_stopped"):
            restored = tx.restore_transaction(
                self.game, backup, loaded, manifest_hash
            )
        self.assertEqual(restored["result"], "restored")
        for relative, predecessor in predecessors.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(), predecessor
            )
        for path, payload in sentinels.items():
            self.assertEqual(path.read_bytes(), payload)

    def test_exact_jp_four_file_text_plan_dry_run_apply_restore_and_sentinels(
        self,
    ) -> None:
        candidates, predecessors, sentinels = self._prepare_jp_four_file_text_profile()
        candidate_root = self.root / "jp-four-file-text-candidates"
        self.assertEqual(set(tx.collect_candidate_root(candidate_root)), set(candidates))

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = tx.main(
                [
                    "plan",
                    "--game-root",
                    str(self.game),
                    "--release-id",
                    "jp-four-file-text-v1",
                    "--manifest",
                    str(self.manifest_path),
                    "--candidate-root",
                    str(candidate_root),
                ]
            )
        self.assertEqual(exit_code, 0, output.getvalue())
        manifest, manifest_hash = tx.read_manifest(self.manifest_path)
        self.assertEqual(manifest["target_scope"], tx.JP_FOUR_FILE_TEXT_TARGET_SCOPE)
        self.assertEqual(
            {entry["path"] for entry in manifest["entries"]},
            tx.JP_FOUR_FILE_TEXT_ALLOWED_TARGETS,
        )
        self.assertEqual(
            tx.runtime_profile_for_scope(tx.JP_FOUR_FILE_TEXT_TARGET_SCOPE), "JP"
        )
        scope = tx.scope_report(manifest)
        self.assertEqual(scope["runtime_language"], "JP")
        self.assertEqual(scope["msg_pk_jp_count"], 3)
        self.assertEqual(scope["base_msg_jp_count"], 1)
        self.assertEqual(scope["base_msg_jp_dialogue_count"], 1)
        self.assertEqual(scope["jp_4_event_dialogue_text_file_count"], 4)
        self.assertTrue(scope["jp_4_event_dialogue_text_file_complete"])
        self.assertFalse(scope["jp_11_text_audit_file_complete"])
        self.assertFalse(scope["jp_14_file_complete"])

        backup = tx.default_backup_root(self.game, manifest["release_id"])
        dry_run = tx.dry_run(self.game, backup, manifest, candidates)
        self.assertEqual(dry_run["status"], "PASS")
        self.assertEqual(dry_run["installed_state"], "predecessor")
        self.assertTrue(dry_run["would_apply"])
        self.assertFalse(dry_run["writes_performed"])
        self.assertFalse(backup.exists())

        with mock.patch.object(tx, "assert_game_stopped"):
            applied = tx.apply_transaction(
                self.game, backup, manifest, manifest_hash, candidates
            )
        self.assertEqual(applied["result"], "applied")
        for relative, candidate in candidates.items():
            installed = self.game.joinpath(*relative.split("/"))
            self.assertEqual(installed.read_bytes(), candidate.read_bytes())
            self.assertTrue(backup.joinpath("originals", *relative.split("/")).is_file())
        for path, payload in sentinels.items():
            self.assertEqual(path.read_bytes(), payload)

        with mock.patch.object(tx, "assert_game_stopped"):
            restored = tx.restore_transaction(
                self.game, backup, manifest, manifest_hash
            )
        self.assertEqual(restored["result"], "restored")
        for relative, predecessor in predecessors.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(), predecessor
            )
        for path, payload in sentinels.items():
            self.assertEqual(path.read_bytes(), payload)

    def test_jp_four_file_text_rejects_three_and_five_file_variants(self) -> None:
        candidates, _, _ = self._prepare_jp_four_file_text_profile()
        exact_manifest = tx.make_manifest(self.game, "jp-four-file-text-v1", candidates)
        selected = sorted(candidates)
        three = {relative: candidates[relative] for relative in selected[:3]}
        extra_relative = "MSG_PK/JP/msgbre.bin"
        extra_candidate = (
            self.root / "jp-four-file-text-candidates" / "MSG_PK" / "JP" / "msgbre.bin"
        )
        self._write(
            self.game.joinpath(*extra_relative.split("/")),
            b"stock::MSG_PK/JP/msgbre.bin",
        )
        self._write(extra_candidate, b"target::MSG_PK/JP/msgbre.bin")
        five = {**candidates, extra_relative: extra_candidate}

        for name, variant in (("three", three), ("five", five)):
            with self.subTest(variant=name):
                direct_arguments = [
                    f"{relative}={candidate}"
                    for relative, candidate in variant.items()
                ]
                with self.assertRaisesRegex(
                    tx.TransactionError, "event/dialogue text 4-file profile"
                ):
                    tx.parse_candidate_args(direct_arguments)
                with self.assertRaisesRegex(
                    tx.TransactionError, "event/dialogue text 4-file profile"
                ):
                    tx.make_manifest(self.game, f"jp-four-file-{name}-v1", variant)

                malformed = json.loads(json.dumps(exact_manifest))
                if name == "three":
                    omitted = selected[-1]
                    malformed["entries"] = [
                        entry
                        for entry in malformed["entries"]
                        if entry["path"] != omitted
                    ]
                else:
                    malformed["entries"].append(
                        {
                            "path": extra_relative,
                            "mode": "replace",
                            "predecessor": tx.file_spec(
                                self.game.joinpath(*extra_relative.split("/"))
                            ),
                            "target": tx.file_spec(extra_candidate),
                        }
                    )
                with self.assertRaisesRegex(
                    tx.TransactionError, "event/dialogue text 4-file profile"
                ):
                    tx.validate_manifest(malformed)

        candidate_root = self.root / "jp-four-file-text-candidates"
        extra_candidate.unlink()
        omitted = selected[-1]
        candidates[omitted].unlink()
        with self.assertRaisesRegex(
            tx.TransactionError, "event/dialogue text 4-file profile"
        ):
            tx.collect_candidate_root(candidate_root)
        self._write(candidates[omitted], ("target::" + omitted).encode())
        self._write(extra_candidate, b"target::MSG_PK/JP/msgbre.bin")
        with self.assertRaisesRegex(
            tx.TransactionError, "event/dialogue text 4-file profile"
        ):
            tx.collect_candidate_root(candidate_root)

        wrong_scope = json.loads(json.dumps(exact_manifest))
        wrong_scope["target_scope"] = tx.JP_FULL_TARGET_SCOPE
        with self.assertRaisesRegex(tx.TransactionError, "exact JP 14-file profile"):
            tx.validate_manifest(wrong_scope)

    def test_jp_four_file_text_apply_failure_rolls_back_and_preserves_sentinels(
        self,
    ) -> None:
        candidates, predecessors, sentinels = self._prepare_jp_four_file_text_profile()
        manifest = tx.make_manifest(self.game, "jp-four-file-rollback-v1", candidates)
        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        original_copy_atomic = tx.copy_atomic
        failed = False

        def fail_during_second_live_write(
            source, destination, expected, label, *, before_replace=None
        ):
            nonlocal failed
            if label == "apply MSG_PK/JP/msgdata.bin" and not failed:
                failed = True
                raise OSError("injected JP four-file apply failure")
            return original_copy_atomic(
                source,
                destination,
                expected,
                label,
                before_replace=before_replace,
            )

        with mock.patch.object(tx, "assert_game_stopped"), mock.patch.object(
            tx, "copy_atomic", side_effect=fail_during_second_live_write
        ):
            with self.assertRaisesRegex(tx.TransactionError, "was rolled back"):
                tx.apply_transaction(
                    self.game, backup, loaded, manifest_hash, candidates
                )
        self.assertTrue(failed)
        for relative, predecessor in predecessors.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(), predecessor
            )
        for path, payload in sentinels.items():
            self.assertEqual(path.read_bytes(), payload)
        state = tx.read_strict_json(tx.state_path(backup))
        self.assertEqual(state["status"], "restored")

    def test_jp_subset_is_rejected_at_every_manifest_entrypoint(self) -> None:
        candidates, _, _ = self._prepare_jp_profile()
        full_manifest = tx.make_manifest(self.game, "jp-full-v1", candidates)
        omitted = "RES_JP_PK_PORT/res_lang_pk_port2.bin"
        partial = {
            relative: candidate
            for relative, candidate in candidates.items()
            if relative != omitted
        }

        direct_arguments = [
            f"{relative}={candidate}" for relative, candidate in partial.items()
        ]
        with self.assertRaisesRegex(tx.TransactionError, "exact JP"):
            tx.parse_candidate_args(direct_arguments)
        with self.assertRaisesRegex(tx.TransactionError, "exact JP"):
            tx.make_manifest(self.game, "jp-partial-v1", partial)

        partial_manifest = json.loads(json.dumps(full_manifest))
        partial_manifest["entries"] = [
            entry
            for entry in partial_manifest["entries"]
            if entry["path"] != omitted
        ]
        with self.assertRaisesRegex(tx.TransactionError, "exact JP"):
            tx.validate_manifest(partial_manifest)

        candidates[omitted].unlink()
        with self.assertRaisesRegex(tx.TransactionError, "exact JP"):
            tx.collect_candidate_root(self.root / "jp-candidates")

    def test_exact_eleven_file_jp_port_profile_is_rejected(self) -> None:
        candidates, _, _ = self._prepare_jp_profile()
        omitted = "RES_JP_PK_PORT/res_lang_pk_port2.bin"
        eleven = {
            relative: candidate
            for relative, candidate in candidates.items()
            if relative != omitted
        }
        self.assertEqual(len(eleven), 11)
        self.assertEqual(
            set(eleven),
            tx.JP_LEGACY_ALLOWED_TARGETS
            | {"RES_JP_PK_PORT/res_lang_pk_port1.bin"},
        )
        with self.assertRaisesRegex(tx.TransactionError, "12-file profile"):
            tx.make_manifest(self.game, "jp-eleven-v1", eleven)

    def test_jp_candidate_root_rejects_forbidden_extra_files(self) -> None:
        self._prepare_jp_profile()
        candidate_root = self.root / "jp-candidates"
        forbidden = (
            "NOBU16PK.exe",
            "MSG/JP/unlisted.bin",
            "RES_JP/res_lang_exp.bin",
            "RES_JP_PK/res_lang_exp_pk.bin",
            "RES_JP_PK_PORT/res_lang_pk_port3.bin",
        )
        for relative in forbidden:
            with self.subTest(relative=relative):
                extra = candidate_root.joinpath(*relative.split("/"))
                self._write(extra, b"forbidden-extra")
                with self.assertRaisesRegex(tx.TransactionError, "unexpected file"):
                    tx.collect_candidate_root(candidate_root)
                extra.unlink()

    def test_candidate_root_direct_candidate_and_backup_reparse_are_rejected(self) -> None:
        candidates, _, _ = self._prepare_jp_profile()
        direct_target = self.root / "direct-link-target"
        direct_link = self.root / "direct-link"
        if not self._make_directory_link(direct_link, direct_target):
            self.skipTest("directory symlink/junction creation is unavailable")

        relative = "RES_JP_PK/res_lang_pk.bin"
        linked_candidate = direct_link / "res_lang_pk.bin"
        self._write(linked_candidate, candidates[relative].read_bytes())
        linked_candidates = dict(candidates)
        linked_candidates[relative] = linked_candidate
        with self.assertRaisesRegex(tx.TransactionError, "symlink/reparse"):
            tx.make_manifest(self.game, "jp-linked-candidate-v1", linked_candidates)

        candidate_root_link = self.root / "jp-candidates-link"
        self.assertTrue(
            self._make_directory_link(candidate_root_link, self.root / "jp-candidates")
        )
        with self.assertRaisesRegex(tx.TransactionError, "symlink/reparse"):
            tx.collect_candidate_root(candidate_root_link)

        backup_parent = self.game / "KR_PATCH_BACKUP"
        backup_target = backup_parent / "real-backup"
        backup_link = backup_parent / "linked-backup"
        self.assertTrue(self._make_directory_link(backup_link, backup_target))
        with self.assertRaisesRegex(tx.TransactionError, "symlink/reparse"):
            tx.validate_backup_root(self.game, backup_link)

    def test_jp_apply_failure_rolls_back_the_complete_predecessor_vector(self) -> None:
        candidates, predecessors, _ = self._prepare_jp_profile()
        manifest = tx.make_manifest(self.game, "jp-rollback-v1", candidates)
        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        original_copy_atomic = tx.copy_atomic
        failed = False

        def fail_during_second_live_write(
            source, destination, expected, label, *, before_replace=None
        ):
            nonlocal failed
            if label == "apply MSG_PK/JP/msgbre.bin" and not failed:
                failed = True
                raise OSError("injected JP apply failure")
            return original_copy_atomic(
                source,
                destination,
                expected,
                label,
                before_replace=before_replace,
            )

        with mock.patch.object(tx, "assert_game_stopped"), mock.patch.object(
            tx, "copy_atomic", side_effect=fail_during_second_live_write
        ):
            with self.assertRaisesRegex(tx.TransactionError, "was rolled back"):
                tx.apply_transaction(
                    self.game, backup, loaded, manifest_hash, candidates
                )
        self.assertTrue(failed)
        for relative, predecessor in predecessors.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(), predecessor
            )
        state = tx.read_strict_json(tx.state_path(backup))
        self.assertEqual(state["status"], "restored")

    def test_jp_post_replace_exception_is_rolled_back(self) -> None:
        candidates, predecessors, _ = self._prepare_jp_profile()
        manifest = tx.make_manifest(self.game, "jp-post-replace-v1", candidates)
        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        original_copy_atomic = tx.copy_atomic
        failed = False

        def fail_after_verified_live_write(
            source, destination, expected, label, *, before_replace=None
        ):
            nonlocal failed
            original_copy_atomic(
                source,
                destination,
                expected,
                label,
                before_replace=before_replace,
            )
            if label == "apply MSG/JP/strdata.bin" and not failed:
                failed = True
                raise OSError("injected after verified live replacement")

        with mock.patch.object(tx, "assert_game_stopped"), mock.patch.object(
            tx, "copy_atomic", side_effect=fail_after_verified_live_write
        ):
            with self.assertRaisesRegex(tx.TransactionError, "was rolled back"):
                tx.apply_transaction(
                    self.game, backup, loaded, manifest_hash, candidates
                )
        self.assertTrue(failed)
        for relative, predecessor in predecessors.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(), predecessor
            )
        state = tx.read_strict_json(tx.state_path(backup))
        self.assertEqual(state["status"], "restored")

    def test_game_launch_after_staging_prevents_the_first_live_replacement(self) -> None:
        candidates, predecessors, _ = self._prepare_jp_profile()
        manifest = tx.make_manifest(self.game, "jp-pre-replace-guard-v1", candidates)
        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        guard_calls = 0

        def game_starts_before_replace() -> None:
            nonlocal guard_calls
            guard_calls += 1
            if guard_calls == 3:
                raise tx.TransactionError("injected game launch before live replace")

        with mock.patch.object(
            tx, "assert_game_stopped", side_effect=game_starts_before_replace
        ):
            with self.assertRaisesRegex(tx.TransactionError, "was rolled back"):
                tx.apply_transaction(
                    self.game, backup, loaded, manifest_hash, candidates
                )

        self.assertEqual(guard_calls, 3)
        for relative, predecessor in predecessors.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(), predecessor
            )
        self.assertFalse(
            any(self.game.rglob(".*.n16kr.*.tmp")),
            "failed guarded staging must not leave a live-tree temporary",
        )
        state = tx.read_strict_json(tx.state_path(backup))
        self.assertEqual(state["status"], "restored")

    def test_jp_live_candidates_and_backup_roots_are_rejected(self) -> None:
        candidates, _, _ = self._prepare_jp_profile()
        live_font = (
            self.game / "RES_JP_PK_PORT" / "res_lang_pk_port1.bin"
        )
        live_candidates = dict(candidates)
        live_candidates["RES_JP_PK_PORT/res_lang_pk_port1.bin"] = live_font
        with self.assertRaisesRegex(tx.TransactionError, "live PK resource tree"):
            tx.make_manifest(
                self.game,
                "jp-live-root-v1",
                live_candidates,
            )
        with self.assertRaisesRegex(tx.TransactionError, "inside a PK resource tree"):
            tx.validate_backup_root(
                self.game, self.game / "RES_JP_PK_PORT" / "transaction-backup"
            )
        self.assertEqual(set(candidates), tx.JP_ALLOWED_TARGETS)

    def test_jp_rejects_mixed_profile_expansion_event_and_executable_targets(self) -> None:
        candidates, _, _ = self._prepare_jp_profile()
        mixed = {
            "MSG_PK/SC/msgui.bin": self.candidates_root / "MSG_PK" / "SC" / "msgui.bin",
            "MSG_PK/JP/msgui.bin": candidates["MSG_PK/JP/msgui.bin"],
        }
        with self.assertRaisesRegex(tx.TransactionError, "must not mix SC and JP"):
            tx.make_manifest(self.game, "mixed-v1", mixed)
        self._write(
            self.root / "jp-candidates" / "MSG_PK" / "SC" / "msgui.bin",
            b"mixed-root-sentinel",
        )
        with self.assertRaisesRegex(tx.TransactionError, "must not mix SC and JP"):
            tx.collect_candidate_root(self.root / "jp-candidates")

        forbidden = (
            "MSG/JP/unlisted.bin",
            "RES_JP/res_lang_exp.bin",
            "RES_JP_PK/res_lang_exp_pk.bin",
            "RES_JP_PK_PORT/res_lang_pk_port3.bin",
            "NOBU16PK.exe",
        )
        for relative in forbidden:
            with self.subTest(relative=relative), self.assertRaisesRegex(
                tx.TransactionError, "outside PK scope"
            ):
                tx.make_manifest(
                    self.game,
                    "jp-forbidden-v1",
                    {relative: self.game.joinpath(*relative.split("/"))},
                )

    def test_manifest_scope_and_entries_must_use_the_same_profile(self) -> None:
        candidates, _, _ = self._prepare_jp_profile()
        manifest = tx.make_manifest(self.game, "jp-scope-v1", candidates)
        manifest["target_scope"] = tx.TARGET_SCOPE
        with self.assertRaisesRegex(tx.TransactionError, "same runtime profile"):
            tx.validate_manifest(manifest)

        wrong_jp_scope = tx.make_manifest(
            self.game, "jp-wrong-exact-scope-v1", candidates
        )
        wrong_jp_scope["target_scope"] = tx.JP_TARGET_SCOPE
        with self.assertRaisesRegex(tx.TransactionError, "exact legacy JP 10-file"):
            tx.validate_manifest(wrong_jp_scope)

        legacy_candidates = {
            relative: candidate
            for relative, candidate in candidates.items()
            if relative in tx.JP_LEGACY_ALLOWED_TARGETS
        }
        wrong_port_scope = tx.make_manifest(
            self.game, "jp-wrong-port-scope-v1", legacy_candidates
        )
        wrong_port_scope["target_scope"] = tx.JP_PORT_TARGET_SCOPE
        with self.assertRaisesRegex(tx.TransactionError, "exact JP 12-file"):
            tx.validate_manifest(wrong_port_scope)

        sc_manifest = tx.make_manifest(self.game, "sc-scope-v1", self._candidates())
        sc_manifest["target_scope"] = tx.JP_TARGET_SCOPE
        with self.assertRaisesRegex(tx.TransactionError, "same runtime profile"):
            tx.validate_manifest(sc_manifest)

    def test_legacy_exact_ten_file_jp_manifest_still_applies_and_restores(self) -> None:
        candidates, predecessors, _ = self._prepare_jp_profile()
        legacy_candidates = {
            relative: candidate
            for relative, candidate in candidates.items()
            if relative in tx.JP_LEGACY_ALLOWED_TARGETS
        }
        port_predecessors = {
            relative: predecessors[relative]
            for relative in tx.JP_PORT_FONT_TARGETS
        }
        manifest = tx.make_manifest(
            self.game, "legacy-jp-ten-v1", legacy_candidates
        )
        self.assertEqual(manifest["target_scope"], tx.JP_TARGET_SCOPE)
        self.assertEqual(
            {entry["path"] for entry in manifest["entries"]},
            tx.JP_LEGACY_ALLOWED_TARGETS,
        )
        scope = tx.scope_report(manifest)
        self.assertTrue(scope["jp_10_file_complete"])
        self.assertFalse(scope["jp_12_file_complete"])
        self.assertEqual(scope["res_jp_pk_port_count"], 0)

        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        with mock.patch.object(tx, "assert_game_stopped"):
            applied = tx.apply_transaction(
                self.game,
                backup,
                loaded,
                manifest_hash,
                legacy_candidates,
            )
        self.assertEqual(applied["result"], "applied")
        for relative, predecessor in port_predecessors.items():
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(),
                predecessor,
            )
            self.assertFalse(
                backup.joinpath("originals", *relative.split("/")).exists()
            )

        with mock.patch.object(tx, "assert_game_stopped"):
            restored = tx.restore_transaction(
                self.game, backup, loaded, manifest_hash
            )
        self.assertEqual(restored["result"], "restored")
        for relative in tx.JP_LEGACY_ALLOWED_TARGETS:
            self.assertEqual(
                self.game.joinpath(*relative.split("/")).read_bytes(),
                predecessors[relative],
            )

    def test_legacy_sc_manifest_still_applies_and_restores(self) -> None:
        manifest = tx.make_manifest(self.game, "legacy-sc-v1", self._candidates())
        manifest["target_scope"] = tx.LEGACY_TARGET_SCOPE
        manifest = tx.validate_manifest(manifest)
        tx.write_atomic_json(self.manifest_path, manifest)
        loaded, manifest_hash = tx.read_manifest(self.manifest_path)
        backup = tx.default_backup_root(self.game, loaded["release_id"])
        self.assertEqual(tx.scope_report(loaded)["runtime_language"], "SC")
        with mock.patch.object(tx, "assert_game_stopped"):
            tx.apply_transaction(
                self.game, backup, loaded, manifest_hash, self._candidates()
            )
            tx.restore_transaction(self.game, backup, loaded, manifest_hash)
        self.assertEqual(
            (self.game / "MSG_PK" / "SC" / "msgui.bin").read_bytes(),
            b"stock-msgui",
        )
        self.assertEqual(
            (self.game / "RES_SC" / "res_lang.bin").read_bytes(), b"stock-font"
        )


if __name__ == "__main__":
    unittest.main()
