from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_steam_jp_msgev_full_layout_v1.py")
SPEC = importlib.util.spec_from_file_location("steam_jp_msgev_full_layout", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def fake_advance(char: str) -> int:
    return 24 if char == " " or ord(char) < 0x80 else 48


class FullEventLayoutTest(unittest.TestCase):
    def test_general_hangul_join_is_manual(self) -> None:
        self.assertEqual(builder.newline_operation("도쿠가와를\n따라야", next(builder.LINEBREAK_RE.finditer("도쿠가와를\n따라야"))), "manual")

    def test_punctuation_and_color_particle_are_structural(self) -> None:
        punctuation = "전해진 이상,\n도쿠가와를"
        self.assertEqual(builder.newline_operation(punctuation, next(builder.LINEBREAK_RE.finditer(punctuation))), "space")
        colored = "\x1bCB도쿠가와\x1bCZ\n은 적이다"
        self.assertEqual(builder.newline_operation(colored, next(builder.LINEBREAK_RE.finditer(colored))), "concat")

    def test_layout_uses_only_word_boundaries_and_honors_budget(self) -> None:
        marked = "가나 다라\0라마 바사\0아자 차카"
        words, preferred = builder.parse_marked_words(marked)
        solution = builder.best_layout(words, preferred, fake_advance, 2, True)
        self.assertIsNotNone(solution)
        assert solution is not None
        target = builder.render_layout(words, solution)
        self.assertLessEqual(max(builder.visual_line_widths(target, fake_advance)), builder.MAX_LINE_PX)
        self.assertEqual(builder.layout_skeleton(target), builder.layout_skeleton(marked.replace("\0", " ")))

    def test_reviewed_compact_override_fits_original_font_budget(self) -> None:
        target = builder.MANUAL_COMPACT_OVERRIDES[10564]
        self.assertEqual(builder.visual_line_widths(target, fake_advance), [816, 888, 768])

    def test_protected_signature_is_layout_stable(self) -> None:
        before = "\x1bCB이름\x1bCZ은 %d명이다\n[NAME1]"
        after = "\x1bCB이름\x1bCZ은 %d명이다 [NAME1]"
        self.assertEqual(builder.protected_signature(before), builder.protected_signature(after))
        self.assertEqual(builder.layout_skeleton(before), builder.layout_skeleton(after))


if __name__ == "__main__":
    unittest.main()
