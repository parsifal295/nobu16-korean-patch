from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release_templates/v0.95"


class V095ReleasePublicationTests(unittest.TestCase):
    def test_public_package_is_a_document_only_refresh(self) -> None:
        manifest = json.loads((RELEASE / "release_manifest.v1.json").read_text(encoding="utf-8"))
        previous = json.loads((ROOT / "workstreams/v095_image_completion_v1/validation.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.95.0")
        self.assertEqual(manifest["tag"], "v0.95.0")
        self.assertEqual(manifest["package"]["entry_count"], 13)
        self.assertEqual(manifest["package"]["verified_payload_checksums"], 12)
        self.assertEqual(len(manifest["payload_sha256"]), 12)
        self.assertEqual(manifest["previous_approved_package_sha256"], previous["package"]["sha256"])
        self.assertEqual(manifest["changed_entries"], [
            "README_KO.txt", "STATIC_PATCH_CHANGELOG_KO.md", "SHA256SUMS.txt",
        ])
        self.assertTrue(manifest["non_document_payloads_match_previous_approved_package"])
        self.assertEqual(manifest["unchanged_binary_payload_count"], 10)
        for bundle in previous["bundles"].values():
            self.assertEqual(manifest["payload_sha256"][bundle["filename"]], bundle["sha256"])
        for value in [manifest["package"]["sha256"], *manifest["payload_sha256"].values()]:
            self.assertRegex(value, r"^[0-9A-F]{64}$")

    def test_release_notes_and_bundled_changelog_agree(self) -> None:
        notes = (ROOT / "RELEASE_NOTES_v0.95.0_KO.md").read_text(encoding="utf-8")
        self.assertEqual(notes, (RELEASE / "STATIC_PATCH_CHANGELOG_KO.md").read_text(encoding="utf-8"))
        for term in ("돈보키리", "톤보키리", "아직 일본어", "개전", "게임화면 캡처", "모든 화면을 실게임에서 확인한 것은 아닙니다"):
            self.assertIn(term, notes)
        self.assertNotIn("BC7", notes)
        self.assertNotIn("SHA-256", notes)

    def test_installation_uses_the_released_package_not_source_archives(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide = (RELEASE / "README_KO.txt").read_text(encoding="utf-8")
        self.assertIn("releases/download/v0.95.0/NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.95.0.zip", readme)
        self.assertIn("Source code (zip)", readme)
        self.assertNotIn("배포 준비 완료", readme)
        for text in (readme, guide):
            for term in ("1. 패치 설정 후 적용", "2. 원본으로 복구", "3. 현재 설치 상태 확인", "KR_PATCH_BACKUP", "NOBU16PK_XINPUT.exe"):
                self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
