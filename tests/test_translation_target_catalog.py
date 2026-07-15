import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from tools import build_translation_target_catalog as target_catalog


ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "public" / "translation_target_keys.v0.1.json"

EXPECTED = {
    "MSG_PK/SC/msgui.bin": (4037, "C09FE9CBAC9753CCFECE01B3E038D43E0A3E9EC2AC218F788351905EE332EED1"),
    "MSG_PK/SC/msgev.bin": (12906, "00D725442F097A6F369FC3AC662C753976EAA07C714FDF6F436A7EF8B62E7C89"),
    "MSG_PK/SC/msgdata.bin": (25534, "B541D484A26F0B6F4306D46A344A29846331CEBC7C6381F18122F0A161C59D3E"),
    "MSG_PK/SC/msgbre.bin": (2217, "FDD3B10B6434607F642C979F804E804D7B3684FD538C92212E38E0EF4C76A5B0"),
    "MSG_PK/SC/msgire.bin": (122, "762F5705CCA9E0107A8C2A46DE726E9C543F8EEC25E67740DA92EE9B53009C1B"),
    "MSG_PK/SC/msgstf.bin": (8, "29101EBF1EAD685029508789EEE51C4D4FFF65524064D8E32A48EFDED7036982"),
    "MSG_PK/SC/msggame.bin": (16482, "60D7053C25D2AEA8D565A22BC7AFA7C18F233698EFB0975B54996665A02931AF"),
    "MSG/SC/strdata.bin": (26690, "45DEA7C11E0369AA628B592FEEE375334B60BC493932601516E169689923BBC5"),
}
EXPECTED_AGGREGATE_HASH = "F0FDA016B64FF5622E3D66021DAAC293E5B89E44D671E728D3766ABF6D25A8EA"


class TranslationTargetCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.resources = {resource["path"]: resource for resource in cls.catalog["resources"]}

    def test_exact_target_counts_and_hashes(self):
        actual = {
            path: (resource["target_count"], resource["target_keys_sha256"])
            for path, resource in self.resources.items()
        }
        self.assertEqual(EXPECTED, actual)
        self.assertEqual(87996, self.catalog["target_total"])
        self.assertEqual(7, self.catalog["pk_private_resource_count"])
        self.assertEqual(61306, self.catalog["pk_private_target_total"])
        self.assertEqual(1, self.catalog["shared_runtime_resource_count"])
        self.assertEqual(26690, self.catalog["shared_runtime_target_total"])
        self.assertEqual(EXPECTED_AGGREGATE_HASH, self.catalog["all_target_keys_sha256"])

    def test_catalog_contains_only_source_free_keys_and_hashes(self):
        self.assertTrue(self.catalog["source_free"])
        self.assertFalse(self.catalog["contains_source_text"])
        for resource in self.resources.values():
            if resource["key_kind"] == "id":
                keys = resource["target_ids"]
                self.assertTrue(all(type(value) is int for value in keys))
                self.assertEqual(keys, sorted(set(keys)))
                self.assertNotIn("target_coordinates", resource)
            elif resource["key_kind"] in {
                "msggame_coordinate",
                "block_slot_coordinate",
            }:
                keys = resource["target_coordinates"]
                coordinate_size = (
                    3 if resource["key_kind"] == "msggame_coordinate" else 2
                )
                self.assertTrue(
                    all(
                        isinstance(value, list)
                        and len(value) == coordinate_size
                        and all(type(part) is int for part in value)
                        for value in keys
                    )
                )
                coordinate_tuples = [tuple(value) for value in keys]
                self.assertEqual(coordinate_tuples, sorted(set(coordinate_tuples)))
                self.assertNotIn("target_ids", resource)
            else:
                self.fail(f"unexpected target key kind: {resource['key_kind']}")
            self.assertEqual(resource["target_count"], len(keys))
            self.assertEqual(resource["target_keys_sha256"], target_catalog.canonical_hash(keys))
            self.assertNotIn("text", resource)
            self.assertNotIn("translation", resource)

    def test_msgui_has_exactly_3940_pristine_plus_97_activations(self):
        resource = self.resources["MSG_PK/SC/msgui.bin"]
        self.assertEqual(3940, resource["pristine_visible_nonblank"])
        self.assertEqual(97, resource["intentional_activation_count"])
        self.assertEqual(
            list(target_catalog.MSGUI_INTENTIONAL_ACTIVATION_IDS),
            resource["intentional_activation_ids"],
        )
        self.assertTrue(set(resource["intentional_activation_ids"]).issubset(resource["target_ids"]))

    def test_msggame_inventory_is_explicit(self):
        resource = self.resources["MSG_PK/SC/msggame.bin"]
        self.assertEqual(21581, resource["record_total"])
        self.assertEqual(25598, resource["total_slots"])
        self.assertEqual(16482, resource["pristine_visible_nonblank"])
        self.assertEqual("msggame_coordinate", resource["key_kind"])

    def test_pk_loaded_shared_strdata_inventory_is_explicit(self):
        resource = self.resources["MSG/SC/strdata.bin"]
        self.assertEqual("pk_loaded_shared_base", resource["runtime_scope"])
        self.assertEqual("block_slot_coordinate", resource["key_kind"])
        self.assertEqual([25069, 4100, 3000, 122, 20], resource["block_slot_counts"])
        self.assertEqual(32311, resource["total_slots"])
        self.assertEqual(26690, resource["pristine_visible_nonblank"])
        self.assertEqual(0, resource["intentional_activation_count"])
        self.assertEqual([], resource["intentional_activation_coordinates"])

    def test_defaults_are_backup_only_and_never_live_msg_pk(self):
        officer = target_catalog.DEFAULT_OFFICER_BACKUP_ROOT.as_posix().lower()
        transaction = target_catalog.DEFAULT_TRANSACTION_BACKUP_ROOT.as_posix().lower()
        shared = target_catalog.DEFAULT_SHARED_TRANSACTION_BACKUP_ROOT.as_posix().lower()
        self.assertIn("kr_patch_backup", officer)
        self.assertIn("kr_patch_backup", transaction)
        self.assertIn("kr_patch_backup", shared)
        self.assertIn("originals/msg_pk/sc", transaction)
        self.assertNotEqual(transaction, (target_catalog.GAME_ROOT / "MSG_PK" / "SC").as_posix().lower())
        self.assertNotEqual(shared, target_catalog.GAME_ROOT.as_posix().lower())

    def test_shared_strdata_lookup_fails_closed_without_exact_transaction_backup(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                target_catalog.TargetCatalogError,
                "missing exact pristine transaction backup",
            ):
                target_catalog.read_pinned_shared_strdata(pathlib.Path(temporary))

    def test_pristine_backups_reproduce_public_catalog_when_available(self):
        if not (
            target_catalog.DEFAULT_OFFICER_BACKUP_ROOT.is_dir()
            and target_catalog.DEFAULT_TRANSACTION_BACKUP_ROOT.is_dir()
            and target_catalog.DEFAULT_SHARED_TRANSACTION_BACKUP_ROOT.is_dir()
        ):
            self.skipTest("private pristine backup roots are not available")
        rebuilt = target_catalog.build_catalog(
            officer_backup_root=target_catalog.DEFAULT_OFFICER_BACKUP_ROOT,
            transaction_backup_root=target_catalog.DEFAULT_TRANSACTION_BACKUP_ROOT,
            shared_transaction_backup_root=target_catalog.DEFAULT_SHARED_TRANSACTION_BACKUP_ROOT,
        )
        self.assertEqual(self.catalog, rebuilt)

    def test_generator_check_mode(self):
        if not (
            target_catalog.DEFAULT_OFFICER_BACKUP_ROOT.is_dir()
            and target_catalog.DEFAULT_TRANSACTION_BACKUP_ROOT.is_dir()
            and target_catalog.DEFAULT_SHARED_TRANSACTION_BACKUP_ROOT.is_dir()
        ):
            self.skipTest("private pristine backup roots are not available")
        result = subprocess.run(
            [sys.executable, "-B", "tools/build_translation_target_catalog.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
