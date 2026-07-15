from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "nobu16_test_steam_jp_117_candidate_v1",
    ROOT / "build_steam_jp_117_candidate_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJP117CandidateTests(unittest.TestCase):
    def test_exact_target_vector(self) -> None:
        self.assertEqual(builder.TARGETS, builder.EXPECTED_TARGETS)
        self.assertEqual(len(builder.TARGETS), 10)
        self.assertEqual(
            sum(path.startswith("MSG_PK/JP/") for path in builder.TARGETS), 7
        )

    def test_runtime_label(self) -> None:
        self.assertEqual(builder.STEAM_PK_VERSION, "1.1.7")
        self.assertEqual(builder.STEAM_BUILD_ID, 18_823_764)

    def test_component_contracts_are_jp_only(self) -> None:
        self.assertEqual(builder.MSGGAME.RESOURCE, "MSG_PK/JP/msggame.bin")
        self.assertEqual(builder.MSGUI.RESOURCE, "MSG_PK/JP/msgui.bin")
        self.assertFalse(
            json.loads(
                (
                    builder.REPO
                    / "workstreams"
                    / "steam_jp_runtime_skeleton_v1"
                    / "validation.v1.json"
                ).read_text(encoding="utf-8")
            )["sc_container_read"]
        )

    def test_predecessor_vector_when_steam_is_available(self) -> None:
        if not builder.STEAM_ROOT.is_dir():
            self.skipTest("Steam 1.1.7 installation is unavailable")
        observed = builder.predecessor_vector(builder.STEAM_ROOT)
        self.assertEqual(set(observed), set(builder.TARGETS))

    def test_tracked_verification_is_exact_and_jp_only(self) -> None:
        value = json.loads((ROOT / "verification.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(value["runtime"]["pk_version"], "1.1.7")
        self.assertEqual(value["candidate_paths"], list(builder.TARGETS))
        self.assertEqual(value["candidate_file_count"], 10)
        self.assertEqual(set(value["candidates"]), set(builder.TARGETS))
        self.assertFalse(value["checks"]["sc_container_used"])
        self.assertEqual(value["zip"]["member_count"], 10)


if __name__ == "__main__":
    unittest.main()
