import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "data" / "public" / "steam_jp_117_progress.v1.json"
TRANSLATION_PROGRESS = ROOT / "data" / "public" / "translation_progress.v0.1.json"
FONT_DEMAND_MANIFEST = ROOT / "workstreams" / "font_seoulhangang_v1" / "manifest.v1.json"
SPEC = importlib.util.spec_from_file_location(
    "readme_progress", ROOT / "tools" / "update_readme_progress.py"
)
assert SPEC and SPEC.loader
readme_progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readme_progress)


class ReadmeProgressTests(unittest.TestCase):
    def test_runtime_contract_is_steam_jp_117(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        self.assertEqual(payload["release"], "v0.7.1")
        self.assertEqual(
            payload["runtime"],
            {
                "distribution": "Steam",
                "pk_version": "1.1.7",
                "steam_build_id": 18823764,
                "language_route": "JP",
                "launcher_language": "日本語 / Japanese",
            },
        )

    def test_translation_accounting_is_exact(self):
        translation = readme_progress.load_progress()["translation"]
        msgui = translation["msgui"]
        self.assertEqual(msgui["safely_mapped"], 4036)
        self.assertEqual(msgui["effective_changes"], 3955)
        self.assertEqual(msgui["source_equal_noops"], 81)
        self.assertEqual(msgui["withheld"], 1)
        self.assertEqual(
            msgui["safely_mapped"],
            msgui["effective_changes"] + msgui["source_equal_noops"],
        )
        self.assertEqual(
            msgui["catalog_entries"], msgui["safely_mapped"] + msgui["withheld"]
        )

        common = translation["common_messages"]
        self.assertEqual(common["source_union_effective_coordinates"], 43169)
        self.assertEqual(common["applied"], 40487)
        self.assertEqual(common["source_equal_structural_noops"], 1796)
        self.assertEqual(common["format_contract_blocked"], 730)
        self.assertEqual(common["alignment_gap"], 156)
        self.assertEqual(common["review_backlog"], 886)
        self.assertEqual(common["known_internal_dummy"], 2)
        self.assertEqual(common["reviewed_semantic_gaps_pending"], 94)
        self.assertEqual(common["officer_surnames_recovered"], 980)
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
        self.assertEqual(common["duplicate_context_collapsed"], 50)

        msggame = translation["msggame"]
        self.assertEqual(
            msggame["semantic_targets"], msggame["applied"] + msggame["remaining"]
        )
        self.assertEqual((msggame["applied"], msggame["remaining"]), (28272, 0))

        strdata = translation["strdata"]
        self.assertEqual(strdata["safe_targets"], strdata["applied"] + strdata["withheld"])
        self.assertEqual((strdata["applied"], strdata["withheld"]), (24524, 1))
        self.assertEqual(translation["fonts"], {"containers": 4, "verified": 4})

    def test_render_is_japanese_runtime_only(self):
        rendered = readme_progress.render()
        self.assertIn("Steam PK v1.1.7", rendered)
        self.assertIn("`msgui.bin` | 안전 이식 4,036 / 4,037 (99.98%)", rendered)
        self.assertIn("`msggame.bin` | 적용 28,272 / 28,272 (100.0%)", rendered)
        self.assertIn("`strdata.bin` | 안전 이식 24,524 / 24,525", rendered)
        self.assertIn("한국어 변경 40,487 · 구조 확인 1,796 / 원천 합집합 43,169", rendered)
        self.assertIn("검토 886", rendered)
        self.assertIn("인물 성씨 누락 980건을 복구", rendered)
        self.assertIn("검토된 의미 간극 94건", rendered)
        self.assertIn("이번 오류수정 릴리즈에 포함하지 않았습니다", rendered)
        self.assertIn("형식 계약 검토 730건, 정렬 간극 156건", rendered)
        self.assertIn("내부 더미 2건이 포함", rendered)
        self.assertIn("일본어 경로 한글 폰트 | 4 / 4 포함", rendered)
        self.assertIn("Steam PK v1.1.7 일본어 경로", rendered)
        self.assertIn("메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변조는 사용하지 않습니다.", rendered)
        self.assertIn("보류 1건은 번역 대상 문구가 아닌 비의미 공백 1자 레코드", rendered)
        self.assertNotIn("미해결 0", rendered)
        self.assertNotIn("unresolved=0", rendered)
        self.assertNotIn("전역 100%", rendered)
        self.assertNotIn("종료 확인창", rendered)
        self.assertNotIn("아직 번역되지 않은 일본어 UI", rendered)
        self.assertNotIn("MSG_PK/SC", rendered)
        self.assertNotIn("RES_SC", rendered)
        self.assertNotIn("비Steam", rendered)

    def test_runtime_qa_is_recorded(self):
        qa = readme_progress.load_progress()["runtime_qa"]
        self.assertEqual(qa["current_release_live_apply"], "FILE_PASS")
        self.assertEqual(qa["officer_surname_binary_recomposition"], "PASS")
        self.assertEqual(qa["v0_7_1_screen_qa"], "PENDING")
        self.assertEqual(qa["evidence_release"], "v0.7.0")
        self.assertTrue(qa["steam_install_applied"])
        self.assertTrue(qa["exact_twelve_target_hashes"])
        self.assertEqual(qa["pre_v0_7_predecessor_backups_valid"], 12)
        self.assertEqual(qa["launcher_update_label"], "Update 1.1.7")
        self.assertTrue(qa["korean_title_prompt_observed"])
        self.assertTrue(qa["korean_main_menu_observed"])
        self.assertTrue(qa["known_untranslated_ui_observed"])
        self.assertEqual(qa["qhd_windowed"], "PASS")
        self.assertEqual(qa["qhd_borderless"], "PASS")
        self.assertEqual(qa["cold_restart"], "PASS")

    def test_four_jp_font_stages_and_progress_pin_are_complete(self):
        raw = TRANSLATION_PROGRESS.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        rows = {
            row["path"]: row
            for row in payload["resources"]
            if row.get("kind") == "stages" and row.get("path", "").startswith("RES_JP")
        }
        expected_paths = {
            "RES_JP/res_lang.bin",
            "RES_JP_PK/res_lang_pk.bin",
            "RES_JP_PK_PORT/res_lang_pk_port1.bin",
            "RES_JP_PK_PORT/res_lang_pk_port2.bin",
        }
        self.assertEqual(set(rows), expected_paths)
        for path in expected_paths:
            self.assertEqual((rows[path]["done"], rows[path]["total"]), (2, 2))
            self.assertIn("QA 완료", rows[path]["note"])

        manifest = json.loads(FONT_DEMAND_MANIFEST.read_text(encoding="utf-8"))
        pin = manifest["pinned_public_korean_demand"]["translation_progress"]
        self.assertEqual(pin["path"], "data/public/translation_progress.v0.1.json")
        self.assertEqual(pin["sha256"], hashlib.sha256(raw).hexdigest().upper())

    def test_readme_progress_is_current(self):
        result = subprocess.run(
            [sys.executable, "-B", "tools/update_readme_progress.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_render_has_no_simplified_chinese_runtime_instruction(self):
        block = readme_progress.render()
        self.assertIn("일본어 경로 한글 폰트", block)
        self.assertNotIn("MSG/SC", block)
        self.assertNotIn("MSG_PK/SC", block)
        self.assertNotIn("RES_SC", block)


if __name__ == "__main__":
    unittest.main()
