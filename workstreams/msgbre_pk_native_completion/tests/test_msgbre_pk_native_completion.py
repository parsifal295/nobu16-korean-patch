from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1] / "build_msgbre_pk_native_completion.py"
)
SPEC = importlib.util.spec_from_file_location("msgbre_pk_native_completion", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class MsgbrePkNativeCompletionTests(unittest.TestCase):
    def args_for(self, out_root: Path, *, progress: Path | None = None) -> argparse.Namespace:
        return argparse.Namespace(
            stock_sc=builder.LOCAL_STOCK_SC_BACKUP,
            stock_jp=builder.GAME_ROOT / "MSG_PK" / "JP" / "msgbre.bin",
            stock_en=builder.GAME_ROOT / "MSG_PK" / "EN" / "msgbre.bin",
            stock_tc=builder.GAME_ROOT / "MSG_PK" / "TC" / "msgbre.bin",
            target_catalog=(
                builder.REPO_ROOT
                / "data"
                / "public"
                / "translation_target_keys.v0.1.json"
            ),
            progress=(
                progress
                or builder.REPO_ROOT
                / "data"
                / "public"
                / "translation_progress.v0.1.json"
            ),
            out_root=out_root,
        )

    def temporary_output(self):
        return tempfile.TemporaryDirectory(
            prefix="test-msgbre-native-", dir=builder.REPO_ROOT / "tmp"
        )

    def test_exact_target_and_prior_claim_gap(self) -> None:
        target_ids, target = builder.load_exact_target_keys(
            builder.REPO_ROOT
            / "data"
            / "public"
            / "translation_target_keys.v0.1.json"
        )
        claims, progress = builder.audit_progress_registration(
            builder.REPO_ROOT
            / "data"
            / "public"
            / "translation_progress.v0.1.json",
            target_ids,
        )
        self.assertEqual(target_ids, set(range(2217)))
        self.assertEqual(target["target_keys_sha256"], builder.EXPECTED_TARGET_KEYS_SHA256)
        self.assertEqual(claims, target_ids.difference(builder.SELECTED_IDS))
        self.assertFalse(claims.intersection(builder.SELECTED_IDS))
        self.assertTrue(progress["completion_after_registration"])
        self.assertEqual(progress["simulated_with_candidate_count"], 2217)

    def test_all_eleven_translations_are_buildable_and_preserve_invariants(self) -> None:
        with self.temporary_output() as directory:
            root = Path(directory)
            result = builder.build_once(self.args_for(root), root)
            overlay = json.loads(
                (root / "public" / builder.OVERLAY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(result["entry_count"], 11)
            self.assertEqual(
                [entry["id"] for entry in overlay["entries"]], builder.SELECTED_IDS
            )
            self.assertTrue(all(builder.HANGUL_RE.search(entry["ko"]) for entry in overlay["entries"]))
            self.assertTrue(all(builder.source_script_free(entry["ko"]) for entry in overlay["entries"]))
            evidence = json.loads(
                (root / "evidence" / builder.EVIDENCE_NAME).read_text(encoding="utf-8")
            )
            self.assertTrue(
                all(entry["message_invariants_preserved"] for entry in evidence["entries"])
            )
            self.assertTrue(
                all(
                    entry["custom_bracket_signature_preserved"]
                    for entry in evidence["entries"]
                )
            )

    def test_custom_quote_pairs_are_preserved_for_the_two_quoted_rows(self) -> None:
        sources = {
            language: builder.load_pinned_table(path, language)[2]
            for language, path in {
                "SC": builder.LOCAL_STOCK_SC_BACKUP,
                "JP": builder.GAME_ROOT / "MSG_PK" / "JP" / "msgbre.bin",
                "EN": builder.GAME_ROOT / "MSG_PK" / "EN" / "msgbre.bin",
                "TC": builder.GAME_ROOT / "MSG_PK" / "TC" / "msgbre.bin",
            }.items()
        }
        for entry_id in builder.SELECTED_IDS:
            source_signature = builder.custom_bracket_signature(
                sources["SC"].texts[entry_id]
            )
            target_signature = builder.custom_bracket_signature(
                builder.TRANSLATIONS[entry_id]
            )
            self.assertEqual(source_signature, target_signature, entry_id)
            self.assertEqual(
                source_signature,
                ["“", "”"] if entry_id in (2212, 2214) else [],
                entry_id,
            )

    def test_public_artifacts_are_source_script_free_and_hash_only(self) -> None:
        with self.temporary_output() as directory:
            root = Path(directory)
            builder.build_once(self.args_for(root), root)
            for path in (
                root / "public" / builder.OVERLAY_NAME,
                root / "evidence" / builder.EVIDENCE_NAME,
                root / "review" / builder.REVIEW_NAME,
                root / builder.VALIDATION_NAME,
            ):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(
                    builder.script_counts(text),
                    {"cjk_unified_count": 0, "kana_count": 0},
                    path.name,
                )
                payload = json.loads(text)
                stack = [payload]
                forbidden_keys = {
                    "source_text",
                    "source_jp_text",
                    "source_sc_text",
                    "source_en_text",
                    "source_tc_text",
                }
                while stack:
                    value = stack.pop()
                    if isinstance(value, dict):
                        self.assertFalse(forbidden_keys.intersection(value), path.name)
                        stack.extend(value.values())
                    elif isinstance(value, list):
                        stack.extend(value)

    def test_progress_registration_is_stable_before_and_after_self_registration(self) -> None:
        source_progress = (
            builder.REPO_ROOT
            / "data"
            / "public"
            / "translation_progress.v0.1.json"
        )
        progress = json.loads(source_progress.read_text(encoding="utf-8"))
        resource = next(
            item for item in progress["resources"] if item["path"] == builder.RESOURCE
        )
        resource["overlay_globs"] = [
            item
            for item in resource["overlay_globs"]
            if item != builder.SELF_OVERLAY_PATH
        ]
        with self.temporary_output() as directory:
            root = Path(directory)
            absent = root / "progress_absent.json"
            present = root / "progress_present.json"
            absent.write_text(
                json.dumps(progress, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            resource["overlay_globs"].append(builder.SELF_OVERLAY_PATH)
            present.write_text(
                json.dumps(progress, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            target_ids, _ = builder.load_exact_target_keys(
                builder.REPO_ROOT
                / "data"
                / "public"
                / "translation_target_keys.v0.1.json"
            )
            absent_claims, absent_snapshot = builder.audit_progress_registration(
                absent, target_ids
            )
            present_claims, present_snapshot = builder.audit_progress_registration(
                present, target_ids
            )
            self.assertEqual(absent_claims, present_claims)
            self.assertFalse(absent_snapshot["candidate_registered_in_current_progress"])
            self.assertTrue(present_snapshot["candidate_registered_in_current_progress"])
            self.assertEqual(
                absent_snapshot["simulated_with_candidate_ids_sha256"],
                present_snapshot["simulated_with_candidate_ids_sha256"],
            )
            self.assertTrue(absent_snapshot["registration_order_independent"])
            self.assertTrue(present_snapshot["registration_order_independent"])

    def test_build_is_deterministic_and_inputs_are_unchanged(self) -> None:
        with self.temporary_output() as first_dir, self.temporary_output() as second_dir:
            first_root = Path(first_dir)
            second_root = Path(second_dir)
            args = self.args_for(first_root)
            before = builder.input_snapshot(args)
            first = builder.build_once(args, first_root)
            second = builder.build_once(self.args_for(second_root), second_root)
            self.assertEqual(first["files"], second["files"])
            self.assertEqual(first["target"], second["target"])
            self.assertEqual(builder.input_snapshot(args), before)


if __name__ == "__main__":
    unittest.main()
