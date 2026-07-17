from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_steam_jp_msgev_full_layout_v2.py")
SPEC = importlib.util.spec_from_file_location("steam_jp_msgev_full_layout_v2", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def fake_advance(char: str) -> int:
    return 24 if char == " " or ord(char) < 0x80 else 48


class FullEventLayoutV2Test(unittest.TestCase):
    def test_colored_name_span_keeps_internal_space(self) -> None:
        marked = "\x1bCA아사쿠라 요시카게\x1bCZ를\0견제한다"
        words, preferred = builder.words_from_marked(marked)
        self.assertEqual(words, ["\x1bCA아사쿠라 요시카게\x1bCZ를", "견제한다"])
        self.assertEqual(preferred, {0})

    def test_runtime_reservation_is_added_to_literal_width(self) -> None:
        word = "\x1bCA[b75]\x1bCZ가"
        actual, reserved = builder.word_widths([word], fake_advance, {"[b75]": 456})
        self.assertEqual(actual, [168])
        self.assertEqual(reserved, [504])

    def test_solver_uses_reserved_runtime_width(self) -> None:
        words = ["\x1bCA[b75]\x1bCZ가", "나", "다"]
        layout = builder.solve_layout(words, {0}, fake_advance, {"[b75]": 456}, 2)
        self.assertIsNotNone(layout)
        assert layout is not None
        self.assertLessEqual(max(layout.reserved_widths), builder.MAX_LINE_PX)

    def test_manual_target_requires_token_order_preservation(self) -> None:
        source = "\x1bCA[b75]\x1bCZ가 \x1bCB[b110]\x1bCZ를 만난다"
        good = "\x1bCA[b75]\x1bCZ가\n\x1bCB[b110]\x1bCZ를 만난다"
        bad = "\x1bCB[b110]\x1bCZ를\n\x1bCA[b75]\x1bCZ가 만난다"
        self.assertEqual(builder.protected_signature(good), builder.protected_signature(source))
        self.assertNotEqual(builder.protected_signature(bad), builder.protected_signature(source))

    def test_reviewed_clause_break_is_preferred_when_it_fits(self) -> None:
        target = "가나다\n라마바사"
        result = builder.reflow_manual_text(target, 2, fake_advance, {})
        self.assertIsNotNone(result)
        assert result is not None
        rendered, _layout = result
        self.assertEqual(rendered, target)


if __name__ == "__main__":
    unittest.main()
