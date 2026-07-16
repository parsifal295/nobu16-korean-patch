"""Project-authored Korean for the three P1 rows without a base-event twin.

All other rows in this bounded batch are reused only when their active JP
UTF-16LE hash is exactly equal to a source-free base-event Korean overlay.
No Japanese source text is retained here.
"""

from __future__ import annotations


MANUAL_KO = {
    2356: "이브라힘",
    3643: "그러나 그 과정에서 \x1bCB우에스기\x1bCZ 가신과 \x1bCC에치고\x1bCZ의 국인들과\n여러 차례 충돌을 빚어, 반드시 나라 안에서\n지지를 얻었던 것은 아니었다.",
    3767: "일찍부터 \x1bCA하루카게\x1bCZ의 통치에 적잖은 불만을\n품고 있던 \x1bCB나가오\x1bCZ 가신 다수는, \x1bCA[bm1448]\x1bCZ의\n당주 취임을 바라게 되었으나――.",
}
