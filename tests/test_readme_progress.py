from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROGRESS = ROOT / "data" / "public" / "steam_jp_117_progress.v1.json"
CANDIDATE_PROGRESS = ROOT / "data" / "public" / "steam_jp_117_candidate_v10_progress.v1.json"
SPEC = importlib.util.spec_from_file_location(
    "readme_progress", ROOT / "tools" / "update_readme_progress.py"
)
assert SPEC and SPEC.loader
readme_progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readme_progress)


class ReadmeProgressTests(unittest.TestCase):
    def test_runtime_contract_is_steam_jp_117_release(self) -> None:
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        self.assertEqual(payload["release"], "v0.9.0")
        self.assertEqual(
            payload["runtime"],
            {
                "distribution": "Steam",
                "pk_version": "1.1.7",
                "steam_build_id": 18823764,
                "language_route": "JP",
                "launcher_language": "Japanese",
            },
        )

    def test_translation_accounting_includes_the_base_dialogue_routes(self) -> None:
        translation = readme_progress.load_progress()["translation"]
        msgui = translation["msgui"]
        self.assertEqual(
            msgui["safely_mapped"],
            msgui["effective_changes"] + msgui["source_equal_noops"],
        )
        self.assertEqual(
            msgui["catalog_entries"], msgui["safely_mapped"] + msgui["withheld"]
        )

        common = translation["common_messages"]
        self.assertEqual(common["source_union_effective_coordinates"], 43169)
        self.assertEqual(common["applied"], 40581)
        self.assertEqual(
            common["source_union_effective_coordinates"],
            common["applied"]
            + common["source_equal_structural_noops"]
            + common["format_contract_blocked"]
            + common["alignment_gap"],
        )
        self.assertEqual(
            common["review_backlog"],
            common["format_contract_blocked"] + common["alignment_gap"],
        )

        pk_msggame = translation["pk_msggame"]
        self.assertEqual(
            pk_msggame["semantic_targets"],
            pk_msggame["applied"] + pk_msggame["remaining"],
        )
        self.assertEqual((pk_msggame["applied"], pk_msggame["remaining"]), (28272, 0))

        base_msggame = translation["base_msggame"]
        self.assertEqual(base_msggame["resource"], "MSG/JP/msggame.bin")
        self.assertEqual(
            base_msggame["strict_switch_v13_transfer"] + base_msggame["residual"],
            base_msggame["source_script_literals"],
        )
        self.assertEqual(
            (base_msggame["strict_switch_v13_transfer"], base_msggame["residual"]),
            (23194, 62),
        )

        base_ev = translation["base_ev_strdata"]
        self.assertEqual(base_ev["resource"], "MSG/JP/ev_strdata.bin")
        self.assertEqual(
            base_ev["strict_switch_v13_transfer"] + base_ev["residual"],
            base_ev["switch_hangul_candidates"],
        )
        self.assertEqual(
            (base_ev["strict_switch_v13_transfer"], base_ev["residual"]),
            (13085, 5),
        )

    def test_render_is_japanese_route_only_and_marks_release_as_screen_verified(self) -> None:
        rendered = readme_progress.render()
        self.assertIn("기본 지도·튜토리얼 `MSG/JP/msggame.bin`", rendered)
        self.assertIn("기본 이벤트 `MSG/JP/ev_strdata.bin`", rendered)
        self.assertIn("정확히 14파일", rendered)
        self.assertIn("Steam 실적용과 14개 복원 백업, 실제 한글 화면 검증을 모두 완료", rendered)
        self.assertNotIn("MSG/SC", rendered)
        self.assertNotIn("MSG_PK/SC", rendered)
        self.assertNotIn("RES_SC", rendered)
        self.assertNotIn("100.0% 완료", rendered)

    def test_release_qa_records_live_apply_and_screen_verification(self) -> None:
        qa = readme_progress.load_progress()["runtime_qa"]
        self.assertEqual(qa["candidate_verification"], "PASS")
        self.assertEqual(qa["candidate_file_count"], 14)
        self.assertTrue(qa["steam_install_applied"])
        self.assertEqual(qa["steam_apply_transaction"], "PASS")
        self.assertEqual(qa["steam_apply_backup_entries"], 14)
        self.assertEqual(qa["screen_qa"], "PASS")
        self.assertEqual(qa["manual_korean_screen_output"], "PASS")
        self.assertTrue(qa["release_published"])
        self.assertTrue(qa["file_only"])
        self.assertFalse(qa["memory_patch"])
        self.assertFalse(qa["dll_injection"])
        self.assertFalse(qa["hooking"])
        self.assertFalse(qa["executable_modified"])
        self.assertFalse(qa["registry_modified"])

    def test_v010_candidate_audit_and_final_rebase_are_tied_to_frozen_evidence(self) -> None:
        payload = json.loads(CANDIDATE_PROGRESS.read_text(encoding="utf-8"))
        candidate = readme_progress.load_candidate_progress()
        self.assertEqual(candidate, payload)
        self.assertEqual(payload["candidate_release"], "v0.10.0")
        self.assertEqual(payload["status"], "steam_applied_release_pending")
        self.assertEqual(payload["baseline_release"], "v0.9.0")

        translation = payload["translation"]
        self.assertEqual(
            (
                translation["high_confidence_scope"],
                translation["korean_applied"],
                translation["official_credit_preserved"],
                translation["runtime_structure_preserved"],
                translation["manual_translation_hold"],
            ),
            (2498, 2489, 6, 3, 0),
        )
        self.assertEqual(
            translation["candidate_high_confidence_remaining"],
            translation["official_credit_preserved"]
            + translation["runtime_structure_preserved"],
        )
        self.assertEqual(
            payload["candidate"],
            {
                "file_count": 14,
                "zip_name": "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.0.zip",
                "zip_sha256": "B18A5B2B4AE40BBD80BB8613BE3E6CD81DF7EDD3B7E7434A9446AFD576E2C117",
                "zip_size": 356864822,
            },
        )
        final = payload["final_composition"]
        self.assertEqual(final["font_widths"]["policy"], "original_widths_retained")
        self.assertEqual(final["font_widths"]["resource_count"], 4)
        self.assertEqual(final["event_linebreak_rebase"]["coordinate_count"], 4)
        self.assertEqual(final["event_linebreak_rebase"]["hard_break_token_count"], 6)
        self.assertTrue(payload["candidate_qa"]["steam_install_applied"])
        self.assertEqual(
            payload["candidate_qa"]["screen_qa"],
            "NOT_RERUN_AFTER_FONT_ROLLBACK_AND_EVENT_REBASE",
        )
        self.assertFalse(payload["candidate_qa"]["release_published"])

    def test_v010_render_distinguishes_final_rebase_from_release_and_screen_qa(self) -> None:
        rendered = readme_progress.render_candidate()
        self.assertIn("v0.10.0 Steam 적용 후보 — GitHub 릴리스 대기", rendered)
        self.assertIn("한국어 적용 | 2,489", rendered)
        self.assertIn("공식 크레딧 보존 | 6", rendered)
        self.assertIn("런타임 구조 보존 | 3", rendered)
        self.assertIn("글꼴 폭 조정은 포함하지 않고", rendered)
        self.assertIn("4개 좌표에서 6개만 공백으로 리베이스", rendered)
        self.assertIn("Steam 설치본에는 적용했지만", rendered)
        self.assertIn(
            "설치=True, 화면 QA=NOT_RERUN_AFTER_FONT_ROLLBACK_AND_EVENT_REBASE, 배포=False",
            rendered,
        )
        self.assertIn("GitHub 공개 범위 확인이 남아 있습니다", rendered)
        self.assertIn("게임 전체 번역 완료율이 아닙니다", rendered)
        self.assertNotIn("게임 전체 번역 완료율입니다", rendered)
        self.assertNotIn("21 맵", rendered)
        self.assertNotIn("907개", rendered)

    def test_readme_progress_is_current(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", "tools/update_readme_progress.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_readme_explains_japanese_selection_and_rights(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("**Japanese**", readme)
        self.assertIn("비공식 팬메이드", readme)
        self.assertIn("KOEI TECMO GAMES", readme)
        self.assertNotIn("Simplified Chinese", readme)

    def test_readme_distinguishes_the_published_v09_and_local_v010_candidate(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("현재 공개 안정판은 [v0.9.0]", readme)
        self.assertIn("v0.10.0 Steam 적용 후보 — GitHub 릴리스 대기", readme)
        self.assertIn("<!-- translation-progress:start -->", readme)
        self.assertIn("<!-- active-text-audit:start -->", readme)


if __name__ == "__main__":
    unittest.main()
