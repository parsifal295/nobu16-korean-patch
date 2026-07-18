from __future__ import annotations

import unittest

from workstreams.pc_text_quality_wave30_bundle_v1 import build_pc_text_quality_wave30_bundle_v1 as bundle


class Wave30BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        bundle.validate_inputs()
        cls.payloads = bundle.composed_payloads()

    def test_input_profiles_are_exact_and_disjoint(self) -> None:
        self.assertEqual(bundle.WAVE28_PATHS & bundle.WAVE29_PATHS, frozenset())
        self.assertEqual(set(bundle.TARGET_PROFILE), set(bundle.PROFILE_PATHS))
        self.assertEqual(bundle.profile(bundle.WAVE27_ROOT), bundle.WAVE27_PROFILE)
        self.assertEqual(bundle.profile(bundle.WAVE28_ROOT), bundle.WAVE28_PROFILE)
        self.assertEqual(bundle.profile(bundle.WAVE29_ROOT), bundle.WAVE29_PROFILE)

    def test_composition_has_the_pinned_eleven_file_target_profile(self) -> None:
        actual = {
            path: (len(payload), bundle.sha256_bytes(payload))
            for path, payload in self.payloads.items()
        }
        self.assertEqual(actual, bundle.TARGET_PROFILE)

    def test_each_overlay_only_uses_its_candidate_paths(self) -> None:
        for path in bundle.PROFILE_PATHS:
            source = (bundle.WAVE27_ROOT / path).read_bytes()
            if path in bundle.WAVE28_PATHS:
                self.assertEqual(self.payloads[path], (bundle.WAVE28_ROOT / path).read_bytes())
                self.assertNotEqual(self.payloads[path], source)
            elif path in bundle.WAVE29_PATHS:
                self.assertEqual(self.payloads[path], (bundle.WAVE29_ROOT / path).read_bytes())
                self.assertNotEqual(self.payloads[path], source)
            else:
                self.assertEqual(self.payloads[path], source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
