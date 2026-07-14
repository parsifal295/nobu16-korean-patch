from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS = PROJECT_ROOT / "KR_PATCH_WORK" / "tools"
sys.path.insert(0, str(TOOLS))

import generate_officer_name_catalog as names  # noqa: E402


class OfficerNameTransliterationTests(unittest.TestCase):
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
