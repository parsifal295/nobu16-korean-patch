from __future__ import annotations

import importlib.util
import json
import shutil
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


if __name__ == "__main__":
    unittest.main()
