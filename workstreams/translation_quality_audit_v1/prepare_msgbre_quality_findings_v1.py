#!/usr/bin/env python3
"""Create source-gated addendum candidates for the msgbre term cross-check.

Inputs are limited to pristine PC Japanese msgbre and the current Steam PC
Korean msgbre.  The prior 98-row msgbre review file is read only to reject
duplicate IDs.  The optional output is ASCII JSONL below ``tmp``; no game
resource is rebuilt or written.
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
    / "MSG_PK"
    / "JP"
    / "msgbre.bin"
)
LIVE_KO = STEAM / "MSG_PK" / "JP" / "msgbre.bin"
TMP_ROOT = REPO / "tmp"
EXISTING = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgbre_findings.v1.jsonl"
DEFAULT_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgbre_quality_findings.v1.jsonl"

sys.path.insert(0, str(REPO / "tools"))
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
KANA_OR_HAN_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


@dataclass(frozen=True)
class Change:
    replacements: tuple[tuple[str, str], ...]
    issue: str
    rationale: str
    source_markers: tuple[str, ...]


# The 28 rows below are only the clearly wrong items from the one-time
# source-led cross-check.  本領→본령 was deliberately excluded: every matched
# occurrence meant an original holding/territory and needs no automatic edit.
CHANGES: dict[int, Change] = {
    # 討たれ: killed by the named actor/army, not generic subjugation.
    1075: Change((("우키타 나오이에에게 토벌되었다", "우키타 나오이에에게 살해되었다"),), "사망 의미 약화", "討たれた는 우키타 나오이에에게 살해된 결말이다.", ("討たれ",)),
    1130: Change((("다카하시 아키타네에게 토벌되었다", "다카하시 아키타네에게 살해되었다"),), "사망 의미 약화", "討たれた는 다카하시 아키타네에게 살해된 결말이다.", ("討たれ",)),
    1147: Change((("시바타 가쓰이에에게 토벌되어 수급", "시바타 가쓰이에에게 살해되어 수급"),), "사망 의미 약화", "討たれ首級は의 수급 문맥은 살해된 결말이다.", ("討たれ",)),
    1198: Change(
        (("쓰구나리를 토벌했으나", "쓰구나리를 죽였으나"), ("쓰구나리의 아들 미쓰나리에게 토벌당했다", "쓰구나리의 아들 미쓰나리에게 살해당했다")),
        "사망 의미 약화",
        "討った 뒤 討たれた의 교차 서술로, 두 인물의 사망 관계를 보존해야 한다.",
        ("討たれ",),
    ),
    1213: Change((("부친 도하루가 토벌되자", "부친 도하루가 살해되자"),), "사망 의미 약화", "父・道春が討たれる는 부친 도하루가 살해된 사건이다.", ("討たれ",)),
    1312: Change((("우에스기 겐신에게 토벌되었다", "우에스기 겐신에게 살해되었다"),), "사망 의미 약화", "討たれた는 우에스기 겐신에게 살해된 결말이다.", ("討たれ",)),
    1600: Change((("히사쓰나에게 토벌되었다", "히사쓰나에게 살해되었다"),), "사망 의미 약화", "討たれた는 히사쓰나에게 살해된 결말이다.", ("討たれ",)),
    1639: Change((("패해 토벌되었다", "패해 살해되었다"),), "사망 의미 약화", "敗れ討たれた는 패전 뒤 살해된 결말이다.", ("討たれ",)),
    1691: Change((("요시타카가 스에 하루카타에게 토벌된 뒤", "요시타카가 스에 하루카타에게 살해된 뒤"),), "사망 의미 약화", "義隆が討たれた後는 요시타카가 살해된 뒤를 뜻한다.", ("討たれ",)),
    1960: Change((("다다이에의 군세에 토벌되었다", "다다이에의 군세에 살해되었다"),), "사망 의미 약화", "討たれた는 다다이에의 군세에게 살해된 결말이다.", ("討たれ",)),
    2051: Change((("아군 무장이 토벌당하자", "아군 무장이 살해당하자"),), "사망 의미 약화", "武将が討たれる는 아군 무장이 살해된 사건을 뜻한다.", ("討たれ",)),
    2092: Change((("이이 나오타카 부대에게 토벌되었다", "이이 나오타카 부대에게 살해되었다"),), "사망 의미 약화", "討たれた는 이이 나오타카 부대에게 살해된 결말이다.", ("討たれ",)),
    2130: Change((("오다 노부나가에게 토벌되었다", "오다 노부나가에게 살해되었다"),), "사망 의미 약화", "討たれた는 오다 노부나가에게 살해된 결말이다.", ("討たれ",)),
    2206: Change((("주군 모토나리에게 토벌당했다", "주군 모토나리에게 살해당했다"),), "사망 의미 약화", "主君元就に討たれた는 주군 모토나리에게 살해된 결말이다.", ("討たれ",)),

    # 討ち取る: the named person was killed, often in a head-taking context.
    707: Change((("시마 사콘을 토벌하는", "시마 사콘을 베어 죽이는"),), "사망 의미 약화", "島左近を討ち取る는 시마 사콘을 베어 죽인 전공이다.", ("討ち取",)),
    1446: Change((("이케다 쓰네오키를 토벌하는", "이케다 쓰네오키를 베어 죽이는"),), "사망 의미 약화", "池田恒興を討ち取る는 이케다 쓰네오키를 베어 죽인 전공이다.", ("討ち取",)),
    1475: Change((("모토히로를 토벌하여 그 수급", "모토히로를 베어 죽여 그 수급"),), "사망 의미 약화", "討ち取り首級を持ち帰った는 모토히로를 베어 수급을 거둔 전공이다.", ("討ち取",)),
    1517: Change((("미야케 다카시게를 토벌하는", "미야케 다카시게를 베어 죽이는"),), "사망 의미 약화", "三宅高繁を討ち取る는 미야케 다카시게를 베어 죽인 전공이다.", ("討ち取",)),
    2097: Change((("모리 요시나리를 토벌하였으나", "모리 요시나리를 베어 죽였으나"),), "사망 의미 약화", "森可成を討ち取る는 모리 요시나리를 베어 죽인 전공이다.", ("討ち取",)),

    # 落城: a castle falling, not completion of a building (낙성).
    1219: Change((("낙성을 면했다", "성 함락을 면했다"),), "성 함락 용어 오역", "落城を免れた는 성 함락을 면했다는 뜻이다.", ("落城",)),
    1265: Change((("낙성 후에는", "성 함락 후에는"),), "성 함락 용어 오역", "落城後には는 성 함락 후에는을 뜻한다.", ("落城",)),
    1512: Change((("낙성 때 자결했다는", "성 함락 때 자결했다는"),), "성 함락 용어 오역", "落城時は 성 함락 때를 뜻한다.", ("落城",)),
    1554: Change((("쇼즈이성 낙성 후에는", "쇼즈이성 함락 후에는"),), "성 함락 용어 오역", "勝瑞城の落城後에는 쇼즈이성 함락 후에는을 뜻한다.", ("落城",)),
    1746: Change((("오다와라 낙성 후", "오다와라성 함락 후"),), "성 함락 용어 오역", "小田原落城後는 오다와라성 함락 후를 뜻한다.", ("落城",)),
    1821: Change((("낙성을 면했다", "성 함락을 면했다"),), "성 함락 용어 오역", "落城を免れた는 성 함락을 면했다는 뜻이다.", ("落城",)),
    2156: Change((("오사카 낙성 후에는", "오사카성 함락 후에는"),), "성 함락 용어 오역", "大坂落城後には는 오사카성 함락 후에는을 뜻한다.", ("落城",)),

    # 陪臣: a retainer's retainer, not betrayal.
    1672: Change((("배신 신분이면서도", "가신의 가신 신분이면서도"),), "신분 용어 오역", "陪臣은 배신자가 아니라 가신의 가신을 뜻한다.", ("陪臣",)),
    1784: Change((("천하의 삼배신 중 한 명", "천하의 삼대 가신의 가신 중 한 명"),), "신분 용어 오역", "天下の三陪臣은 천하의 삼대 가신의 가신이라는 호칭이다.", ("陪臣",)),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


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
        "private_use": [f"U+{ord(character):04X}" for character in text if 0xE000 <= ord(character) <= 0xF8FF],
        "fullwidth_percent_count": text.count("％"),
        "question_marks": text.count("?"),
    }


def existing_ids() -> set[int]:
    if not EXISTING.is_file():
        raise ValueError(f"existing msgbre findings are absent: {EXISTING}")
    identifiers: set[int] = set()
    for line_number, line in enumerate(EXISTING.read_text(encoding="ascii").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        identifier = row.get("id")
        if not isinstance(identifier, int) or identifier in identifiers:
            raise ValueError(f"invalid existing candidate ID at line {line_number}")
        identifiers.add(identifier)
    return identifiers


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
    if len(jp) != len(ko):
        raise ValueError("pristine JP and live KO msgbre tables differ")
    covered = existing_ids()
    duplicate_ids = sorted(set(CHANGES).intersection(covered))
    if duplicate_ids:
        raise ValueError(f"new candidates overlap existing 98 IDs: {duplicate_ids}")

    jp_file_sha = sha256_file(PRISTINE_JP)
    ko_file_sha = sha256_file(LIVE_KO)
    rows: list[dict[str, object]] = []
    for identifier, change in sorted(CHANGES.items()):
        if not 0 <= identifier < len(jp):
            raise ValueError(f"coordinate outside msgbre table: {identifier}")
        source = jp[identifier]
        missing_markers = [marker for marker in change.source_markers if marker not in source]
        if missing_markers:
            raise ValueError(f"{identifier}: source markers absent: {missing_markers}")
        current = ko[identifier]
        proposed = current
        for before, after in change.replacements:
            count = proposed.count(before)
            if count != 1:
                raise ValueError(f"{identifier}: expected one fragment {before!r}, found {count}")
            proposed = proposed.replace(before, after, 1)
        if proposed == current:
            raise ValueError(f"{identifier}: no effective correction")
        current_profile = profile(current)
        proposal_profile = profile(proposed)
        source_profile = profile(source)
        current_checks = {
            "escape_tags_match": current_profile["escape_tags"] == proposal_profile["escape_tags"],
            "runtime_tokens_match": current_profile["runtime_tokens"] == proposal_profile["runtime_tokens"],
            "printf_tokens_match": current_profile["printf"] == proposal_profile["printf"],
            "newlines_match": current_profile["newlines"] == proposal_profile["newlines"],
            "outer_ascii_whitespace_match": current_profile["outer_ascii_whitespace"] == proposal_profile["outer_ascii_whitespace"],
            "private_use_match": current_profile["private_use"] == proposal_profile["private_use"],
            "fullwidth_percent_count_match": current_profile["fullwidth_percent_count"] == proposal_profile["fullwidth_percent_count"],
            "question_marks_unchanged": current_profile["question_marks"] == proposal_profile["question_marks"],
        }
        source_token_checks = {
            "escape_tags_match": source_profile["escape_tags"] == proposal_profile["escape_tags"],
            "runtime_tokens_match": source_profile["runtime_tokens"] == proposal_profile["runtime_tokens"],
            "printf_tokens_match": source_profile["printf"] == proposal_profile["printf"],
            "newlines_match": source_profile["newlines"] == proposal_profile["newlines"],
            "private_use_match": source_profile["private_use"] == proposal_profile["private_use"],
            "fullwidth_percent_count_match": source_profile["fullwidth_percent_count"] == proposal_profile["fullwidth_percent_count"],
        }
        integrity_checks = {
            "hangul_present": bool(HANGUL_RE.search(proposed)),
            "no_japanese_or_cjk_residue": not bool(KANA_OR_HAN_RE.search(proposed)),
            "no_replacement_glyph": "\ufffd" not in proposed,
            "no_repeated_question_marks": "??" not in proposed,
        }
        if not all(current_checks.values()) or not all(source_token_checks.values()) or not all(integrity_checks.values()):
            raise ValueError(f"{identifier}: format or integrity validation failed")
        rows.append(
            {
                "id": identifier,
                "ko": current,
                "proposed_ko": proposed,
                "current_hash": text_hash(current),
                # Existing semantic builders use this name for the frozen
                # current-Korean file baseline; expose the JP source checksum
                # separately so both provenance chains are unambiguous.
                "source_file_sha256": ko_file_sha,
                "pristine_jp_file_sha256": jp_file_sha,
                "issue": change.issue,
                "rationale": change.rationale,
                "source_marker_validation": "match",
                "format_profile": {
                    "current": current_profile,
                    "proposed": proposal_profile,
                    "pristine_jp": source_profile,
                },
                "format_validation": {
                    "current_to_proposed": current_checks,
                    "pristine_jp_to_proposed_tokens": source_token_checks,
                    "integrity": integrity_checks,
                    "all_required_checks_pass": True,
                },
            }
        )
    keys = [row["id"] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate addendum candidate ID")
    summary = {
        "row_count": len(rows),
        "unique_id_count": len(set(keys)),
        "existing_candidate_id_count": len(covered),
        "overlap_with_existing_candidate_ids": [],
        "live_steam_ko_sha256": ko_file_sha,
        "pristine_jp_pc_sha256": jp_file_sha,
        "current_hashes": "utf16le_all_match",
        "format_profiles": "all_match",
        "source_marker_validation": "all_match",
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
        print(json.dumps({**summary, "output": str(output), "output_bytes": output.stat().st_size}, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
