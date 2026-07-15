from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "nobu16_test_msggame_wave07_integration", ROOT / "build_wave07_integration.py"
)
assert SPEC is not None and SPEC.loader is not None
integration = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = integration
SPEC.loader.exec_module(integration)


class Wave07IntegrationTests(unittest.TestCase):
    def test_contextual_variant_allowlist_is_exact(self) -> None:
        variants = integration.allowed_variants()
        digest = "11D6CB6698EA92B9016B4B9C6CE4D9C4B1CA93725177B86422D5F216BBC4F100"
        self.assertEqual({digest}, set(variants))
        self.assertEqual(
            {
                (6, 4568, 1): "라 불리는",
                (6, 4569, 1): "라 불리는",
                (6, 4617, 4): "일",
                (9, 833, 0): "라 불리는",
                (9, 834, 0): "라 불리는",
                (9, 859, 0): "라 불리는",
                (9, 860, 0): "라 불리는",
                (9, 3993, 0): "라 불리는",
                (9, 3994, 0): "라 불리는",
            },
            variants[digest],
        )

    def test_partition_is_exact_and_disjoint(self) -> None:
        batches = integration.partition_coordinates()
        self.assertEqual(
            {key: len(value) for key, value in batches.items()},
            integration.EXPECTED_BATCH_COUNTS,
        )
        self.assertEqual(len(set().union(*batches.values())), integration.EXPECTED_TOTAL)

    def test_public_overlays_cover_each_batch(self) -> None:
        stock = integration.resolve_stock(None)
        _specs, result = integration.validate_batches(stock.read_bytes())
        self.assertEqual(result["coordinate_count"], integration.EXPECTED_TOTAL)
        self.assertEqual(len(result["overlay_rows"]), 5)

    def test_complete_candidate_is_deterministic_and_has_no_jp_semantic_remaining(self) -> None:
        stock = integration.resolve_stock(None)
        first, manifest, result = integration.build_complete(stock)
        second, second_manifest, second_result = integration.build_complete(stock)
        self.assertEqual(first, second)
        self.assertEqual(manifest, second_manifest)
        self.assertEqual(result, second_result)
        self.assertEqual(manifest["translation"]["applied_entry_count"], 28_272)
        self.assertEqual(manifest["translation"]["remaining_jp_semantic_count"], 0)
        self.assertTrue(manifest["checks"]["non_literal_structure_preserved"])
        self.assertFalse(manifest["checks"]["sc_container_used"])


if __name__ == "__main__":
    unittest.main()
