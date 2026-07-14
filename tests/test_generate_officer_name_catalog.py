from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS = PROJECT_ROOT / "KR_PATCH_WORK" / "tools"
sys.path.insert(0, str(TOOLS))

import generate_officer_name_catalog as names  # noqa: E402


class OfficerNameTransliterationTests(unittest.TestCase):
    def test_confirmed_manual_overrides_are_source_pinned(self) -> None:
        expected = {
            162: "안요지 우지타네",
            231: "이즈모노 오쿠니",
            516: "오카모토 겐이츠",
            843: "고마츠",
            1179: "조슌인",
            1302: "치지와 미게루",
            1584: "네고로 긴세키사이",
            1666: "반 단에몬",
            1674: "히코츠루",
            1739: "호조 겐안",
            1752: "호조인 인에이",
            1831: "마에다 겐이",
            2134: "유지 사다토키",
        }
        self.assertEqual(set(expected), set(names.MANUAL_OVERRIDES))
        for entry_id, korean in expected.items():
            with self.subTest(entry_id=entry_id):
                override = names.MANUAL_OVERRIDES[entry_id]
                self.assertEqual(
                    {"source_utf16le_sha256", "ko"},
                    set(override),
                )
                self.assertEqual(korean, override["ko"])
                pins = override["source_utf16le_sha256"]
                self.assertEqual({"SC", "JP", "EN"}, set(pins))
                for pin in pins.values():
                    self.assertRegex(pin, r"\A[0-9A-F]{64}\Z")

    def test_manual_override_accepts_matching_synthetic_source_pins(self) -> None:
        entry_id = 9000
        source = {"SC": "SC-fixture", "JP": "JP-fixture", "EN": "EN-fixture"}
        synthetic = {
            entry_id: {
                "source_utf16le_sha256": {
                    language: hashlib.sha256(text.encode("utf-16le"))
                    .hexdigest()
                    .upper()
                    for language, text in source.items()
                },
                "ko": "TARGET VALUE",
            }
        }
        with patch.dict(names.MANUAL_OVERRIDES, synthetic, clear=True):
            self.assertEqual(
                "TARGET VALUE",
                names.pinned_manual_override(
                    entry_id,
                    source["SC"],
                    source["JP"],
                    source["EN"],
                ),
            )

    def test_manual_override_rejects_a_source_pin_mismatch(self) -> None:
        entry_id = 9000
        source = {"SC": "SC-fixture", "JP": "JP-fixture", "EN": "EN-fixture"}
        synthetic = {
            entry_id: {
                "source_utf16le_sha256": {
                    language: hashlib.sha256(text.encode("utf-16le"))
                    .hexdigest()
                    .upper()
                    for language, text in source.items()
                },
                "ko": "TARGET VALUE",
            }
        }
        with patch.dict(names.MANUAL_OVERRIDES, synthetic, clear=True):
            with self.assertRaisesRegex(
                names.OfficerNameError,
                r"manual override source pin differs at id 9000: SC",
            ):
                names.pinned_manual_override(
                    entry_id,
                    "tampered",
                    source["JP"],
                    source["EN"],
                )

    def test_user_selected_spellings(self) -> None:
        self.assertEqual("오다", names.romaji_to_hangul("Oda"))
        self.assertEqual("노부나가", names.romaji_to_hangul("Nobunaga"))
        self.assertEqual("이시다", names.romaji_to_hangul("Ishida"))
        self.assertEqual("미츠나리", names.romaji_to_hangul("Mitsunari"))
        self.assertEqual("아츠지", names.romaji_to_hangul("Atsuji"))
        self.assertEqual("사다유키", names.romaji_to_hangul("Sadayuki"))

    def test_popular_stop_and_long_vowel_style(self) -> None:
        self.assertEqual("다케다", names.kana_to_hangul("たけだ"))
        self.assertEqual("도쿠가와", names.kana_to_hangul("とくがわ"))
        self.assertEqual("가토", names.kana_to_hangul("かとう"))
        self.assertEqual("오우치", names.kana_to_hangul("おおうち"))
        self.assertEqual("류조지", names.kana_to_hangul("りゅうぞうじ"))
        self.assertEqual("소운", names.kana_to_hangul("そううん"))
        self.assertEqual("한베에", names.kana_to_hangul("はんべえ"))
        self.assertEqual("조소카베", names.kana_to_hangul("ちょうそかべ"))

    def test_geminate_and_syllabic_n(self) -> None:
        self.assertEqual("잇시키", names.kana_to_hangul("いっしき"))
        self.assertEqual("핫토리", names.kana_to_hangul("はっとり"))
        self.assertEqual("겐신", names.kana_to_hangul("けんしん"))

    def test_reading_split_prefers_game_order_and_corrects_en_surname(self) -> None:
        parts, method = names.split_reading("おだのぶなが", "Nobunaga Oda")
        self.assertEqual(["おだ", "のぶなが"], parts)
        self.assertEqual("reading_exact", method)

        parts, method = names.split_reading(
            "あけちみつやす",
            "Mitsuyasu Dota",
            allow_alternate_surname=True,
        )
        self.assertEqual(["あけち", "みつやす"], parts)
        self.assertEqual("reading_given_suffix", method)

    def test_long_vowel_stays_on_the_correct_side_of_space(self) -> None:
        parts, method = names.split_reading("ないとうおきもり", "Okimori Naitª")
        self.assertEqual(["ないとう", "おきもり"], parts)
        self.assertEqual("reading_exact", method)
        self.assertEqual("나이토 오키모리", " ".join(names.kana_to_hangul(part) for part in parts))

        parts, method = names.split_reading("やぎゅうじゅうべえ", "J¨bei Yagy¨")
        self.assertEqual(["やぎゅう", "じゅうべえ"], parts)
        self.assertEqual("reading_exact", method)
        self.assertEqual("야규 주베에", " ".join(names.kana_to_hangul(part) for part in parts))

    def test_title_and_mononym_remain_unspaced(self) -> None:
        self.assertEqual(
            (["おつやのかた"], "unspaced_name"),
            names.split_reading("おつやのかた", "Otsuya Lady"),
        )
        self.assertEqual(
            (["がらしゃ"], "unspaced_name"),
            names.split_reading("がらしゃ", "Gracia"),
        )


if __name__ == "__main__":
    unittest.main()
