from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_text_quality_wave45_safe_static_transaction_envelope_v1.py"
SPEC = importlib.util.spec_from_file_location("wave45_safe_static_transaction_envelope_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 45 builder")
wave45 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave45
SPEC.loader.exec_module(wave45)


class Wave45SafeStaticTransactionEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.envelope = wave45.prepare_candidate()

    def test_exact_pc_only_text_audit_file_set(self) -> None:
        self.assertEqual(set(self.envelope.files), set(wave45.EXPECTED_RELATIVES))
        self.assertEqual(len(self.envelope.files), 11)
        self.assertEqual(self.envelope.audit["replaced_relatives"], list(wave45.REPLACED_RELATIVES))
        self.assertEqual(len(self.envelope.audit["retained_relatives"]), 7)
        self.assertEqual(self.envelope.audit["wave42_changed_cell_count"], 26)
        self.assertEqual(self.envelope.audit["wave44_changed_record_count"], 51)

    def test_only_declared_resources_differ_from_current(self) -> None:
        for relative, payload in self.envelope.files.items():
            with self.subTest(relative=relative):
                current = (wave45.GAME_ROOT / Path(relative)).read_bytes()
                if relative in wave45.REPLACED_RELATIVES:
                    self.assertNotEqual(payload, current)
                else:
                    self.assertEqual(payload, current)

    def test_pinned_profiles_and_private_guard(self) -> None:
        for relative, payload in self.envelope.files.items():
            with self.subTest(relative=relative):
                self.assertEqual(wave45.profile_of(payload), wave45.TARGET_PROFILES[relative])
        with self.assertRaises(wave45.Wave45Error):
            wave45.require_private(wave45.REPO, "repo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
