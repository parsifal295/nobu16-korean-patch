from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
RELEASE_PROGRESS = ROOT / "data" / "public" / "steam_jp_117_candidate_v10_progress.v1.json"
SPEC = importlib.util.spec_from_file_location(
    "readme_progress", ROOT / "tools" / "update_readme_progress.py"
)
assert SPEC and SPEC.loader
readme_progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readme_progress)


class ReadmeProgressTests(unittest.TestCase):
    def test_v010_release_ledger_has_the_public_progress_facts(self) -> None:
        payload = readme_progress.load_release_progress()
        self.assertEqual(payload, json.loads(RELEASE_PROGRESS.read_text(encoding="utf-8")))
        self.assertEqual(payload["candidate_release"], "v0.10.0")
        self.assertEqual(payload["status"], "released")
        self.assertEqual(payload["candidate"]["file_count"], 14)

        translation = payload["translation"]
        self.assertEqual(
            (
                translation["active_text_tables"],
                translation["korean_applied"],
                translation["high_confidence_scope"],
            ),
            (10, 2489, 2498),
        )
        self.assertEqual(
            translation["candidate_high_confidence_remaining"],
            translation["official_credit_preserved"]
            + translation["runtime_structure_preserved"],
        )

    def test_render_states_that_text_translation_is_complete(self) -> None:
        rendered = readme_progress.render()
        self.assertIn("v0.10.0 — 텍스트 번역 완료", rendered)
        self.assertIn("게임 내 번역 대상 텍스트 번역을 완료했습니다.", rendered)
        self.assertIn("순정 PC 일본어 원문과 PC EN/SC/TC 대조", rendered)
        self.assertIn("스위치판 한글은 기준으로 사용하지 않습니다.", rendered)
        self.assertIn("고확신 오역만 별도 검증 후 수정합니다.", rendered)
        self.assertIn("이벤트 스크립트 줄바꿈 전수 검수·보정은 완료했습니다.", rendered)
        self.assertIn("이미지 번역은 진행 중입니다.", rendered)
        self.assertNotIn("2,489", rendered)
        self.assertNotIn("추가 수동 검토", rendered)
        self.assertNotIn("SHA-256", rendered)
        self.assertNotIn("후보 ZIP", rendered)
        self.assertNotIn("설치=True", rendered)
        self.assertNotIn("RES_JP", rendered)

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

    def test_readme_keeps_installation_release_and_rights_information(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("**Japanese**", readme)
        self.assertIn("현재 공개 안정판은 [v0.11.1]", readme)
        self.assertIn("비공식 팬메이드", readme)
        self.assertIn("KOEI TECMO GAMES", readme)
        self.assertNotIn("<!-- active-text-audit:start -->", readme)

    def test_readme_documents_the_v0110_static_officer_editor_fix(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("build `18823764`", readme)
        self.assertIn(
            "29BC1ED66D27B9AEF5EB6CE3D126BA2BDBF86099E12B09615FE9F988F41E2246",
            readme,
        )
        self.assertIn("한 번 교체", readme)
        self.assertIn("메모리를 건드리는 helper가 아닙니다", readme)
        self.assertIn("NOBU16PK.exe.staticfix.original_1.1.7", readme)
        self.assertIn("RESTORE_ORIGINAL_NOBU16PK_EXE.bat", readme)
        self.assertIn("Steam 보호 래퍼", readme)
        self.assertIn("NotSigned", readme)
        self.assertIn("2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C", readme)
        self.assertIn("성명에 사용할 수 없는 문자가 포함되어 있습니다", readme)
        self.assertIn("성명 합계 6자 제한", readme)
        self.assertIn("가가와 미초카게", readme)
        self.assertIn("1920×1080 창 모드", readme)
        self.assertIn("완전히 종료·재실행", readme)
        self.assertIn("한글 IME 입력이나 새 한글 이름 작성 기능을 추가하지 않습니다", readme)
        self.assertIn("성명·읽기 필드를 바꾸지 말고", readme)
        self.assertIn("매 게임 세션마다 별도 실행 파일을 실행할 필요가 없습니다", readme)

    def test_readme_documents_the_v0111_installer_hotfix(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("## v0.11.1 — 설치기 경로·한글 오류 출력 수정", readme)
        self.assertIn("`%~dp0`", readme)
        self.assertIn("경로에 잘못된 문자가 있습니다", readme)
        self.assertIn("UTF-8 BOM", readme)
        self.assertIn("게임 리소스 15개와 정적 EXE의 다섯 패치 지점", readme)


if __name__ == "__main__":
    unittest.main()
