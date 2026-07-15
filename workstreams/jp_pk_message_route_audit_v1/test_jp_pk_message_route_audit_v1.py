from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
REPO_ROOT = WORKSTREAM.parents[1]
GAME_ROOT = REPO_ROOT.parent
MODULE_PATH = WORKSTREAM / "build_jp_pk_message_route_audit_v1.py"
SPEC = importlib.util.spec_from_file_location("jp_pk_message_route_audit_v1", MODULE_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class JpPkMessageRouteAuditV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validation = json.loads(
            (WORKSTREAM / "translation_validation.v1.json").read_text(encoding="utf-8")
        )
        cls.evidence = json.loads(
            (WORKSTREAM / "evidence/jp_pk_message_route_evidence.v1.json").read_text(
                encoding="utf-8"
            )
        )
        cls.review = json.loads(
            (WORKSTREAM / "review/jp_pk_message_native_blocked_review.v1.json").read_text(
                encoding="utf-8"
            )
        )
        cls.routes = json.loads(
            (WORKSTREAM / "public/jp_pk_message_native_route_map.v1.json").read_text(
                encoding="utf-8"
            )
        )

    def test_validation_proves_full_eight_container_mirror(self) -> None:
        scope = self.validation["scope"]
        self.assertTrue(self.validation["passed"])
        self.assertEqual(8, scope["source_resource_count"])
        self.assertEqual(8, scope["target_resource_count"])
        self.assertEqual(83_586, scope["overlay_effective_coordinate_count"])
        self.assertEqual(83_586, scope["mirror_transferred_count"])
        self.assertEqual(0, scope["mirror_blocked_count"])
        self.assertFalse(self.validation["proofs"]["runtime_compatibility_claimed"])

    def test_overlay_union_includes_pending_completed_batches_once(self) -> None:
        union = builder.load_overlay_union()
        self.assertEqual(83_658, sum(union.operation_counts.values()))
        self.assertEqual(83_586, sum(len(rows) for rows in union.entries.values()))
        self.assertEqual(
            "218C1FB47DCCDAE07A3B10C6664EAC2A0E426DA8733A46143BC6D92B8CF682B3",
            union.manifest_sha256,
        )
        for resource, supplements in builder.SUPPLEMENTAL_OVERLAYS.items():
            paths = [row["path"] for row in union.manifest[resource]]
            for supplement in supplements:
                self.assertEqual(1, paths.count(supplement))

    def test_native_routes_partition_union_and_keep_blocked_out(self) -> None:
        scope = self.validation["scope"]
        self.assertEqual(
            scope["overlay_effective_coordinate_count"],
            scope["native_transferable_count"] + scope["native_blocked_count"],
        )
        classification = self.routes["classification"]
        self.assertEqual(self.routes["entry_count"], classification["entry_count"])
        self.assertEqual(
            self.review["local_blocked_count"], classification["blocked_count"]
        )
        self.assertEqual(
            classification["detailed_rows_sha256"],
            self.review["classification"]["detailed_rows_sha256"],
        )
        for resource in classification["resources"]:
            self.assertEqual(
                resource["entry_count"],
                resource["transferable_count"] + resource["blocked_count"],
            )
            self.assertTrue(
                all(row[1] for row in resource["blocked_entries"])
            )

    def test_compact_native_route_map_stays_below_pr_size_limit(self) -> None:
        route_path = WORKSTREAM / "public/jp_pk_message_native_route_map.v1.json"
        self.assertLess(route_path.stat().st_size, 15_000_000)

    def test_public_artifacts_are_source_free_and_have_no_binary(self) -> None:
        zero = {"embedded_nul_count": 0, "kana_count": 0, "cjk_unified_count": 0}
        self.assertTrue(
            all(scan == zero for scan in self.validation["source_free_scan"].values())
        )
        self.assertFalse(any(WORKSTREAM.rglob("*.bin")))
        completed = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={REPO_ROOT.as_posix()}",
                "ls-files",
                WORKSTREAM.relative_to(REPO_ROOT).as_posix(),
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertNotIn(".bin", completed.stdout.lower())

    def test_adapter_rejects_wrong_stock_hash_and_blocked_route(self) -> None:
        with self.assertRaisesRegex(ValueError, "JP stock SHA-256 mismatch"):
            # Keep this assertion independent of the game installation.
            builder.build_native_candidate(
                "msgui",
                b"not-a-resource",
                {},
                {},
                expected_stock_sha256="0" * 64,
            )
        stock_path = GAME_ROOT / "MSG_PK/JP/msgire.bin"
        if not stock_path.exists():
            self.skipTest("private JP stock resource is unavailable")
        stock = stock_path.read_bytes()
        with self.assertRaisesRegex(ValueError, "audit rejected"):
            builder.build_native_candidate(
                "msgire",
                stock,
                {0: "검사"},
                {0: "blocked_control_format_contract"},
                expected_stock_sha256=builder.sha256(stock),
            )

    def test_private_mirror_candidate_strictly_parses_and_contains_union(self) -> None:
        candidate_root = (
            REPO_ROOT
            / "tmp"
            / "jp_pk_message_route_audit_v1_candidate_a_20260715"
            / "mirror"
        )
        if not candidate_root.exists():
            self.skipTest("private mirror candidate is unavailable")
        union = builder.load_overlay_union()
        resource_rows = {
            row["source_resource"]: row
            for row in self.evidence["mirror_route"]["resources"]
        }
        self.assertEqual(set(builder.SC_RESOURCES), set(resource_rows))
        for resource in builder.SC_RESOURCES:
            blob = (candidate_root / builder.TARGET_BY_SOURCE[resource]).read_bytes()
            stats, _texts = builder.structure(resource, blob)
            self.assertEqual(
                resource_rows[resource]["mirror_target"]["packed_sha256"],
                stats["packed_sha256"],
            )
            builder.verify_overlay_inclusion(resource, blob, union.entries[resource])


if __name__ == "__main__":
    unittest.main()
