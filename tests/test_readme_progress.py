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
        self.assertIn("인물·이벤트 대사 번역 품질을 전수 감사", rendered)
        self.assertIn("이벤트 스크립트 줄바꿈 검수·보정과 이미지 번역은 진행 중입니다.", rendered)
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
        self.assertIn("현재 공개 안정판은 [v0.14.0]", readme)
        self.assertNotIn("현재 공개 안정판은 [v0.12.0]", readme)
        self.assertIn("`APPLY_KOREAN_PATCH.bat` 한 번", readme)
        self.assertIn("게임 파일 무결성 확인", readme)
        self.assertIn("Steam JP 1.1.7 순정 파일에서만 가능", readme)
        self.assertIn("패치 완료! Steam에서 게임을 시작하세요.", readme)
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

    def test_readme_documents_the_v0113_text_and_npc_repairs(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("## v0.11.3 — NPC 표기·인물 대사·이벤트 줄바꿈 보정", readme)
        self.assertIn("`덴령` → `전령`", readme)
        self.assertIn("`상사람` → `상인`", readme)
        self.assertIn("`선교모로` → `선교사`", readme)
        self.assertIn("`소성씨` → `시동`", readme)
        self.assertIn("`가인` → `가신`", readme)

    def test_readme_documents_the_v0114_policy_percent_recovery(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("## v0.11.4 — 정책 효과 퍼센트 단위 복구", readme)
        self.assertIn("정책 효과 **196개**", readme)
        self.assertIn("공통 정책 효과 **134개**", readme)
        self.assertIn("총 **88개**", readme)
        self.assertIn("성 개발률 25%마다 부대 능력 상승", readme)
        self.assertIn("F43F0B6066EE48F398BACD6A8579EEEBFE5929837FB020703E83D3AA5899AFBB", readme)

    def test_readme_documents_the_v0115_princess_name_validation_fix(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("## v0.11.5 — 가공 히메 한글 작명 허용", readme)
        self.assertIn("Issue #62", readme)
        self.assertIn("문자 검사 네 곳", readme)
        self.assertIn("성+이름 합산 길이 제한", readme)
        self.assertIn("2E098ECB…1797C", readme)
        self.assertIn("7CA2F1D5…AFDB2", readme)
        self.assertIn("3840×2160 창 모드", readme)
        self.assertIn(
            "5B9CF5E245808DB532B60C27C847254F3A22987FF57A75467ED34C8C5942127D",
            readme,
        )

    def test_readme_does_not_advertise_the_withdrawn_v0116_release(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertNotIn(
            "## v0.11.6 — NPC 표기·인물 대사·이벤트 줄바꿈·상단 헤더 누적 보정",
            readme,
        )
        self.assertIn("이벤트 26건과 인물 대사 51건", readme)
        self.assertIn("개발 Steam JP 설치본에 적용해 부팅·저장 불러오기까지 확인했습니다.", readme)
        self.assertIn("v0.13.0 번역 품질 개선 범위에 포함하며", readme)
        self.assertIn("실제 대사·이벤트 화면 QA와 후속 런타임 항목 검수는 계속 진행 중입니다.", readme)

    def test_readme_documents_the_v0120_dynamic_map_labels(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("## v0.12.0 — 지도 성·지명 가로쓰기와 동적 라벨 폭", readme)
        self.assertIn("실제 UTF-16 문자열을 NUL까지", readme)
        self.assertIn("공백과 `성`", readme)
        self.assertIn("고정 최대 글자 수 제한이 없습니다", readme)
        self.assertIn("`001~003`이 이미 적용된", readme)
        self.assertIn("`004`만 적용", readme)
        self.assertIn("완전히 종료하고 새 프로세스로 재실행", readme)
        self.assertIn("3자·5자·6자·7자", readme)
        self.assertIn("최장\n  9자 표시 문자열", readme)
        self.assertIn(
            "624B507EB239F82A2BD9CD5856B8FA0048CDFE3BE285FFF549A5E6C05E2766A4",
            readme,
        )

    def test_readme_documents_the_v0130_candidate_scope(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn(
            "## v0.13.0 — 번역 품질 개선·고해상도 지도 라벨·명소 가로쓰기",
            readme,
        )
        self.assertIn("이벤트 대사 **26건**", readme)
        self.assertIn("인물 대사 **51건**", readme)
        self.assertIn("총\n  **77건**", readme)
        self.assertIn("MSG/JP/ev_strdata.bin", readme)
        self.assertIn("MSG_PK/JP/msggame.bin", readme)
        self.assertIn("Issue #68", readme)
        self.assertIn("Issue #70", readme)
        self.assertIn("아쓰타 신궁", readme)
        self.assertIn("기존 `004`는 v0.12.0 사용자에게 이미 설치된 불변 패치", readme)
        self.assertIn("새 `005`에 고해상도 라벨과 명소 가로쓰기", readme)
        self.assertIn("v0.12.0 사용자는 v0.13.0 파일을 게임 폴더에 덮어쓴 뒤 반드시 새", readme)
        self.assertIn("`APPLY_STATIC_EXE_PATCHES.bat`를 다시 실행해야 합니다", readme)
        self.assertIn("파일만 덮어쓰면\nEXE의 `005`는 적용되지 않습니다", readme)
        self.assertIn(
            "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6",
            readme,
        )
        self.assertIn(
            "A62410EB857001306EE699FD85CE429AC9A8966619F742FA4AB07BB413308255",
            readme,
        )
        self.assertIn("(380,395,760 bytes)", readme)

    def test_readme_documents_the_v0131_release(self) -> None:
        readme = README.read_text(encoding="utf-8")
        for text in (
            "## v0.13.1 — 지도 성 이름 뒤 상태 아이콘 동적 정렬",
            "Issue #72",
            "전투 준비·방위 거점·공략 목표 아이콘",
            "병사수",
            "v0.13.0 설치본에서는 `006`만",
            "완전히 종료한 뒤 새 프로세스로 재실행",
            "7A670A03ACAB2CED43D8F27392CD1F31DB92CD16CB6B0EF04909B8E519A57FDF",
            "(380,397,094 bytes)",
        ):
            self.assertIn(text, readme)


if __name__ == "__main__":
    unittest.main()
