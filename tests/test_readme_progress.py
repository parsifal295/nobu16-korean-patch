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

    def test_render_is_compact_and_keeps_only_user_relevant_status(self) -> None:
        rendered = readme_progress.render()
        self.assertIn("v0.10.0 공개 현황", rendered)
        self.assertIn("JP 경로 14개 파일", rendered)
        self.assertIn("고신뢰 좌표 2,489 / 2,498 한글 반영", rendered)
        self.assertIn("의도적 원문 유지", rendered)
        self.assertIn("추가 수동 검토 | 394건", rendered)
        self.assertIn("이벤트 줄바꿈 정리 · 기존 글꼴 폭 유지", rendered)
        self.assertIn("게임 전체의 번역 완료율은 아닙니다", rendered)
        self.assertIn("해당 이벤트 장면은 다시 확인하지 않았습니다", rendered)
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
        self.assertIn("현재 공개 안정판은 [v0.10.0]", readme)
        self.assertIn("비공식 팬메이드", readme)
        self.assertIn("KOEI TECMO GAMES", readme)
        self.assertNotIn("<!-- active-text-audit:start -->", readme)


if __name__ == "__main__":
    unittest.main()
