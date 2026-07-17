#!/usr/bin/env python3
"""Build source-gated strdata translation-quality candidates.

The audit pairs every target coordinate with the pristine PC Japanese source
at the same coordinate.  It reads only that source and the current Steam PC
Korean target; neither Switch Korean nor an older Korean backup is an input.
The script never rebuilds a game resource.  ``--write`` emits a review-only,
ASCII JSONL file below ``KR_PATCH_WORK/tmp`` after all safeguards pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_JP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG"
    / "JP"
    / "strdata.bin"
)
LIVE_KO = STEAM / "MSG" / "JP" / "strdata.bin"
TMP_ROOT = REPO / "tmp"
DEFAULT_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "strdata_quality_findings.v1.jsonl"

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata  # noqa: E402


ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")


@dataclass(frozen=True)
class Change:
    replacements: tuple[tuple[str, str], ...]
    issue_type: str
    rationale: str
    source_markers: tuple[str, ...]


# Coordinates are (strdata block, ID).  Every replacement is exact and local:
# surrounding tags, line breaks, control tokens, and existing terminology stay
# untouched.  One coordinate (2, 2019) deliberately combines the overlapping
# 落城 and 自害 corrections into one review row.
CHANGES: dict[tuple[int, int], Change] = {
    # 討ち取る: defeating/suppressing is not sufficient where the source says
    # the named person was killed in battle.
    (2, 11): Change(
        (("가와카미 히사아키라를 토벌했다", "가와카미 히사아키라를 베어 죽였다"),),
        "사망 의미 약화",
        "討ち取った는 가와카미 히사아키라를 베어 죽였다는 전공 서술이다.",
        ("討ち取",),
    ),
    (2, 66): Change(
        (("반 나오유키를 토벌하는", "반 나오유키를 베어 죽이는"),),
        "사망 의미 약화",
        "討ち取る는 반 나오유키를 베어 죽인 사건을 뜻한다.",
        ("討ち取",),
    ),
    (2, 302): Change(
        (("동군에 포박되어 토벌당했다", "동군에 포박되어 살해당했다"),),
        "사망 의미 약화",
        "捕縛され討ち取られた는 포박 뒤 살해된 결말이다.",
        ("討ち取",),
    ),
    (2, 303): Change(
        (("사네히사의 아우 다다토키를 물리치는", "사네히사의 아우 다다토키를 베어 죽이는"),),
        "사망 의미 누락",
        "討ち取る는 단순 격퇴가 아니라 다다토키를 베어 죽인 사건이다.",
        ("討ち取",),
    ),
    (2, 681): Change(
        (("반 단에몬을 토벌하였으나", "반 단에몬을 베어 죽였으나"),),
        "사망 의미 약화",
        "討ち取る는 반 단에몬을 베어 죽였다는 뜻이다.",
        ("討ち取",),
    ),
    (2, 1368): Change(
        (("유아사 고스케를 물리치는", "유아사 고스케를 베어 죽이는"),),
        "사망 의미 누락",
        "討ち取る는 유아사 고스케를 베어 죽인 사건이다.",
        ("討ち取",),
    ),
    (2, 1446): Change(
        (("이케다 쓰네오키를 토벌하는", "이케다 쓰네오키를 베어 죽이는"),),
        "사망 의미 약화",
        "討ち取る는 이케다 쓰네오키를 베어 죽인 사건이다.",
        ("討ち取",),
    ),
    (2, 1475): Change(
        (("모토히로를 토벌하여 그 수급", "모토히로를 베어 죽여 그 수급"),),
        "사망 의미 약화",
        "討ち取って首級を挙げた는 모토히로를 베어 수급을 거둔 전공이다.",
        ("討ち取",),
    ),
    (2, 1517): Change(
        (("미야케 다카시게를 토벌하는", "미야케 다카시게를 베어 죽이는"),),
        "사망 의미 누락",
        "討ち取る는 미야케 다카시게를 베어 죽인 사건이다.",
        ("討ち取",),
    ),
    (2, 2097): Change(
        (("모리 요시나리를 토벌하였으나", "모리 요시나리를 베어 죽였으나"),),
        "사망 의미 약화",
        "討ち取る는 모리 요시나리를 베어 죽였다는 뜻이다.",
        ("討ち取",),
    ),

    # 討たれ: a death at another person's or army's hands, not a generic
    # "subjugation".  IDs 705 and 1198 also restore the active first clause.
    (2, 56): Change(
        (("잇코잇키 세력에게 토벌당하였다", "잇코잇키 세력에게 살해당했다"),),
        "사망 의미 약화",
        "討たれた는 잇코잇키 세력에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 236): Change(
        (("오토모군에게 아들 지카우지를 잃었을 때", "아들 지카우지가 오토모군에게 살해당했을 때"),),
        "가해 주체 누락",
        "大友軍に子・親氏を討たれた는 지카우지가 오토모군에게 살해된 사건이다.",
        ("討たれ",),
    ),
    (2, 342): Change(
        (("나오이에에게 토벌되었다", "나오이에에게 살해되었다"),),
        "사망 의미 약화",
        "討たれた는 나오이에에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 446): Change(
        (("아들 마스쓰구가 토벌되고", "아들 마스쓰구가 살해되고"),),
        "사망 의미 약화",
        "討たれ는 마스쓰가 살해된 사건을 뜻한다.",
        ("討たれ",),
    ),
    (2, 493): Change(
        (("데루미치에게 토벌되었다", "데루미치에게 살해되었다"),),
        "사망 의미 약화",
        "討たれた는 테루미치에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 604): Change(
        (("패하여 토벌당했다", "패하여 살해당했다"),),
        "사망 의미 약화",
        "敗れて討たれた는 패전 뒤 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 693): Change(
        (("오다 군에게 토벌당하였다고 한다", "오다 군에게 살해당했다고 한다"),),
        "사망 의미 약화",
        "討たれたという는 오다 군에게 살해되었다는 전승이다.",
        ("討たれ",),
    ),
    (2, 705): Change(
        (
            ("도모카즈를 토벌했으나", "도모카즈를 죽였으나"),
            ("도모카즈의 동생 아키노리에게 토벌되었다", "도모카즈의 동생 아키노리에게 살해되었다"),
        ),
        "사망 의미 약화",
        "討った 뒤 討たれた의 교차 서술로, 두 인물의 사망 관계를 보존해야 한다.",
        ("討たれ",),
    ),
    (2, 720): Change(
        (("소린의 모략에 의해 토벌되었다", "소린의 모략으로 살해되었다"),),
        "사망 의미 약화",
        "謀略により討たれた는 소린의 모략으로 살해된 사건이다.",
        ("討たれ",),
    ),
    (2, 1075): Change(
        (("나오이에에게 토벌되었다", "나오이에에게 살해되었다"),),
        "사망 의미 약화",
        "討たれた는 나오이에에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 1130): Change(
        (("아키타네에게 토벌되었다", "아키타네에게 살해되었다"),),
        "사망 의미 약화",
        "討たれた는 아키타네에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 1147): Change(
        (("가쓰이에에게 토벌되어 수급", "가쓰이에에게 살해되어 수급"),),
        "사망 의미 약화",
        "討たれ首級は의 수급 문맥은 가쓰이에에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 1198): Change(
        (
            ("쓰구나리를 토벌했으나", "쓰구나리를 죽였으나"),
            ("쓰구나리의 아들 미쓰나리에게 토벌당했다", "쓰구나리의 아들 미쓰나리에게 살해당했다"),
        ),
        "사망 의미 약화",
        "討った 뒤 討たれた의 교차 서술로, 두 인물의 사망 관계를 보존해야 한다.",
        ("討たれ",),
    ),
    (2, 1213): Change(
        (("부친 도하루가 토벌되자", "부친 도하루가 살해되자"),),
        "사망 의미 약화",
        "父・道春が討たれる는 부친 도하루가 살해된 사건이다.",
        ("討たれ",),
    ),
    (2, 1312): Change(
        (("겐신에게 토벌되었다", "겐신에게 살해되었다"),),
        "사망 의미 약화",
        "討たれた는 겐신에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 1397): Change(
        (("시바타 가쓰이에에게 베여, 수급은", "시바타 가쓰이에에게 살해되어, 수급은"),),
        "문장 연결 오류",
        "討たれ、首級は의 피동·연결 관계를 자연스럽게 복원한다.",
        ("討たれ",),
    ),
    (2, 1600): Change(
        (("히사쓰나에게 토벌되었다", "히사쓰나에게 살해되었다"),),
        "사망 의미 약화",
        "討たれた는 히사쓰나에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 1639): Change(
        (("패해 토벌되었다", "패해 살해되었다"),),
        "사망 의미 약화",
        "敗れ討たれた는 패전 뒤 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 1691): Change(
        (("요시타카가 스에 하루카타에게 토벌된 뒤", "요시타카가 스에 하루카타에게 살해된 뒤"),),
        "사망 의미 약화",
        "요시타카가 討たれた 뒤의 상황을 설명하는 문맥이다.",
        ("討たれ",),
    ),
    (2, 1960): Change(
        (("다다이에의 군세에 토벌되었다", "다다이에의 군세에 살해되었다"),),
        "사망 의미 약화",
        "討たれた는 다다이에의 군세에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 2051): Change(
        (("아군 무장이 토벌당하자", "아군 무장이 살해당하자"),),
        "사망 의미 약화",
        "武将が討たれる는 아군 무장이 살해된 사건을 뜻한다.",
        ("討たれ",),
    ),
    (2, 2092): Change(
        (("나오타카 부대에게 토벌되었다", "나오타카 부대에게 살해되었다"),),
        "사망 의미 약화",
        "討たれた는 나오타카 부대에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 2130): Change(
        (("오다 노부나가에게 토벌되었다", "오다 노부나가에게 살해되었다"),),
        "사망 의미 약화",
        "討たれた는 오다 노부나가에게 살해된 결말이다.",
        ("討たれ",),
    ),
    (2, 2206): Change(
        (("주군 모토나리에게 토벌당했다", "주군 모토나리에게 살해당했다"),),
        "사망 의미 약화",
        "主君元就に討たれた는 주군 모토나리에게 살해된 결말이다.",
        ("討たれ",),
    ),

    # 落城 is a castle's fall, not the Korean word 낙성 (completion of a
    # building).  Named forts are normalized to the Korean castle name form.
    (2, 31): Change(
        (("낙성 직전에", "성 함락 직전에"),),
        "성 함락 용어 오역",
        "落城은 성의 함락을 뜻한다.",
        ("落城",),
    ),
    (2, 84): Change(
        (("받아 낙성, 멸망했다.", "받아 성이 함락되어 멸망했다."),),
        "성 함락 용어 오역",
        "落城은 공격 뒤 성이 함락된 사건이다.",
        ("落城",),
    ),
    (2, 98): Change(
        (("공격받아 낙성하고 전사했다.", "공격받아 성이 함락되고 전사했다."),),
        "성 함락 용어 오역",
        "落城은 성이 함락된 뒤의 전사 서술이다.",
        ("落城",),
    ),
    (2, 104): Change(
        (("공격을 받아 낙성, 전사했다.", "공격을 받아 성이 함락되어 전사했다."),),
        "성 함락 용어 오역",
        "落城은 성이 함락된 뒤의 전사 서술이다.",
        ("落城",),
    ),
    (2, 219): Change(
        (("낙성과 함께 자결.", "성이 함락되자 자결했다."),),
        "성 함락 용어 오역",
        "落城と共に自刃은 성 함락에 맞춰 자결했다는 뜻이다.",
        ("落城",),
    ),
    (2, 327): Change(
        (("낙성 후", "성 함락 후"),),
        "성 함락 용어 오역",
        "落城後는 성 함락 후를 뜻한다.",
        ("落城",),
    ),
    (2, 483): Change(
        (("오사카 낙성 후", "오사카성 함락 후"),),
        "성 함락 용어 오역",
        "大坂落城後는 오사카성 함락 후를 뜻한다.",
        ("落城",),
    ),
    (2, 1219): Change(
        (("낙성을 면했다", "성 함락을 면했다"),),
        "성 함락 용어 오역",
        "落城を免れた는 성 함락을 면했다는 뜻이다.",
        ("落城",),
    ),
    (2, 1265): Change(
        (("낙성 후에는", "성 함락 후에는"),),
        "성 함락 용어 오역",
        "落城後には는 성 함락 후에는을 뜻한다.",
        ("落城",),
    ),
    (2, 1512): Change(
        (("낙성 때 자결했다는", "성 함락 때 자결했다는"),),
        "성 함락 용어 오역",
        "落城時는 성 함락 때를 뜻한다.",
        ("落城",),
    ),
    (2, 1554): Change(
        (("쇼즈이성 낙성 후", "쇼즈이성 함락 후"),),
        "성 함락 용어 오역",
        "勝瑞城落城後는 쇼즈이성 함락 후를 뜻한다.",
        ("落城",),
    ),
    (2, 1746): Change(
        (("오다와라 낙성 후", "오다와라성 함락 후"),),
        "성 함락 용어 오역",
        "小田原落城後는 오다와라성 함락 후를 뜻한다.",
        ("落城",),
    ),
    (2, 1821): Change(
        (("낙성을 면했다", "성 함락을 면했다"),),
        "성 함락 용어 오역",
        "落城を免れた는 성 함락을 면했다는 뜻이다.",
        ("落城",),
    ),
    (2, 2019): Change(
        (("낙성과 함께 자해했다.", "성 함락과 함께 자결했다."),),
        "성 함락·자결 용어 오역",
        "落城に伴い自害した는 성 함락과 함께 자결했다는 뜻이다.",
        ("落城", "自害"),
    ),
    (2, 2156): Change(
        (("오사카 낙성 후에는", "오사카성 함락 후에는"),),
        "성 함락 용어 오역",
        "大坂落城後には는 오사카성 함락 후에는을 뜻한다.",
        ("落城",),
    ),
    (3, 21): Change(
        (("오사카 낙성 후에는", "오사카성 함락 후에는"),),
        "성 함락 용어 오역",
        "大坂落城後には는 오사카성 함락 후에는을 뜻한다.",
        ("落城",),
    ),

    # 陪臣 is a retainer's retainer, not betrayal (배신).
    (2, 1672): Change(
        (("배신 신분이면서도", "가신의 가신 신분이면서도"),),
        "신분 용어 오역",
        "陪臣은 배신자가 아니라 가신의 가신을 뜻한다.",
        ("陪臣",),
    ),
    (2, 1784): Change(
        (("천하의 삼배신 중 한 명", "천하의 삼대 가신의 가신 중 한 명"),),
        "신분 용어 오역",
        "天下の三陪臣은 천하의 삼대 가신의 가신이라는 호칭이다.",
        ("陪臣",),
    ),

    # 自害 describes self-inflicted death in these biographies; Korean 자해
    # means self-harm and falsely leaves the person alive.
    (2, 28): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 70): Change((("자해", "자결"),), "자결 용어 오역", "自害させ는 자해가 아니라 자결하게 했다는 뜻이다.", ("自害",)),
    (2, 71): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 87): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 220): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 463): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 893): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 1146): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 1199): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 1200): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 1333): Change((("자해", "자결"),), "자결 용어 오역", "自害는 자해가 아니라 자결을 뜻한다.", ("自害",)),
    (2, 1341): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 1645): Change((("자해", "자결"),), "자결 용어 오역", "殉じて自害した는 순사해 자결했다는 뜻이다.", ("自害",)),
    (2, 1838): Change((("자해", "자결"),), "자결 용어 오역", "自害した는 자해가 아니라 자결했다는 뜻이다.", ("自害",)),
    (2, 1878): Change((("자해", "자결"),), "자결 용어 오역", "父の命により自害した는 아버지의 명으로 자결했다는 뜻이다.", ("自害",)),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_utf16le(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load(path: Path) -> dict[tuple[int, int], str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return coordinate_texts(parse_raw_strdata(raw))


def profile(text: str) -> dict[str, object]:
    return {
        "escape_tags": ESC_RE.findall(text),
        "runtime_tokens": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "newlines": re.findall(r"\r\n|\n|\r", text),
        "outer_ascii_whitespace": (
            text[: len(text) - len(text.lstrip(" \t"))],
            text[len(text.rstrip(" \t")) :],
        ),
        "private_use": PRIVATE_USE_RE.findall(text),
        "fullwidth_percent_count": text.count("％"),
        "question_marks": text.count("?"),
    }


def safe_under(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=False)
    allowed = root.resolve(strict=False)
    if resolved != allowed and allowed not in resolved.parents:
        raise ValueError(f"output must remain below {allowed}: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    jp = load(PRISTINE_JP)
    ko = load(LIVE_KO)
    if set(jp) != set(ko):
        raise ValueError("pristine JP and live KO strdata coordinates differ")
    rows: list[dict[str, object]] = []
    for coordinate, change in sorted(CHANGES.items()):
        if coordinate not in jp:
            raise ValueError(f"missing coordinate: {coordinate}")
        source = jp[coordinate]
        missing_markers = [marker for marker in change.source_markers if marker not in source]
        if missing_markers:
            raise ValueError(f"{coordinate}: source markers absent: {missing_markers}")
        current = ko[coordinate]
        proposed = current
        for before, after in change.replacements:
            occurrence_count = proposed.count(before)
            if occurrence_count != 1:
                raise ValueError(f"{coordinate}: expected one fragment {before!r}, found {occurrence_count}")
            proposed = proposed.replace(before, after, 1)
        if proposed == current:
            raise ValueError(f"{coordinate}: no textual change")
        current_profile = profile(current)
        proposed_profile = profile(proposed)
        if current_profile != proposed_profile:
            raise ValueError(f"{coordinate}: protected format profile changed")
        if not HANGUL_RE.search(proposed):
            raise ValueError(f"{coordinate}: proposal has no Hangul")
        if "\ufffd" in proposed or "??" in proposed:
            raise ValueError(f"{coordinate}: corrupted replacement glyph or repeated question mark")
        rows.append(
            {
                "block": coordinate[0],
                "id": coordinate[1],
                "ko": current,
                "proposed_ko": proposed,
                "issue_type": change.issue_type,
                "rationale": change.rationale,
                "current_hash": sha256_utf16le(current),
                "live_ko_file_sha256": sha256_file(LIVE_KO),
                "pristine_jp_file_sha256": sha256_file(PRISTINE_JP),
                "source_marker_validation": "match",
                "format_validation": {
                    "escape_tags": "match",
                    "runtime_tokens": "match",
                    "printf": "match",
                    "newlines": "match",
                    "outer_ascii_whitespace": "match",
                    "private_use": "match",
                    "fullwidth_percent_count": "match",
                    "question_marks": "unchanged",
                },
            }
        )
    keys = [(int(row["block"]), int(row["id"])) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate candidate coordinate")
    summary = {
        "row_count": len(rows),
        "unique_coordinate_count": len(set(keys)),
        "coordinate_count_audited": len(jp),
        "pristine_jp_pc_sha256": sha256_file(PRISTINE_JP),
        "live_steam_ko_sha256": sha256_file(LIVE_KO),
        "source_marker_validation": "all_match",
        "format_profiles": "all_match",
        "hangul_rows": sum(bool(HANGUL_RE.search(str(row["proposed_ko"]))) for row in rows),
        "double_question_or_replacement_glyph_rows": [
            [row["block"], row["id"]]
            for row in rows
            if "??" in str(row["proposed_ko"]) or "\ufffd" in str(row["proposed_ko"])
        ],
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rows, summary = build_rows()
    if args.validate:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    if args.write:
        output = safe_under(args.output, TMP_ROOT)
        payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
        atomic_write(output, payload)
        print(
            json.dumps(
                {**summary, "output": str(output), "output_bytes": output.stat().st_size},
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
